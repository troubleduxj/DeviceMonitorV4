#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报警检测引擎服务
负责检测设备数据是否触发报警规则
"""

import asyncio
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from decimal import Decimal

from app.models.alarm import AlarmRule, AlarmRecord
from app.log import logger


class AlarmDetectionEngine:
    """报警检测引擎"""
    
    def __init__(self):
        self._rules_cache: Dict[str, List[AlarmRule]] = {}  # {device_type_code: [rules]}
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = 300  # 缓存5分钟
        self._trigger_counts: Dict[str, Dict[str, int]] = {}  # {device_code: {rule_code: count}}
        self._last_alarm_time: Dict[str, Dict[str, datetime]] = {}  # 静默期控制
    
    async def load_rules(self, force: bool = False) -> None:
        """加载报警规则到缓存"""
        now = datetime.now()
        
        # 检查缓存是否有效
        if not force and self._cache_time:
            elapsed = (now - self._cache_time).total_seconds()
            if elapsed < self._cache_ttl:
                return
        
        try:
            rules = await AlarmRule.filter(is_enabled=True).all()
            
            # 按设备类型分组
            self._rules_cache = {}
            for rule in rules:
                type_code = rule.device_type_code
                if type_code not in self._rules_cache:
                    self._rules_cache[type_code] = []
                self._rules_cache[type_code].append(rule)
            
            self._cache_time = now
            logger.info(f"报警规则缓存已更新，共 {len(rules)} 条规则")
            
        except Exception as e:
            logger.error(f"加载报警规则失败: {str(e)}")
    
    async def check_device_data(
        self, 
        device_code: str,
        device_name: Optional[str],
        device_type_code: str,
        data: Dict[str, Any]
    ) -> List[Dict]:
        """
        检测设备数据是否触发报警
        
        Args:
            device_code: 设备编码
            device_name: 设备名称
            device_type_code: 设备类型代码
            data: 设备数据字典 {field_code: value}
            
        Returns:
            触发的报警列表
        """
        await self.load_rules()
        
        rules = self._rules_cache.get(device_type_code, [])
        if not rules:
            return []
        
        triggered_alarms = []
        
        for rule in rules:
            field_code = rule.field_code
            
            # 检查数据中是否有该字段
            if field_code not in data:
                continue
            
            value = data[field_code]
            if value is None:
                continue
            
            # 转换为数值
            try:
                if isinstance(value, (int, float, Decimal)):
                    numeric_value = float(value)
                else:
                    numeric_value = float(str(value))
            except (ValueError, TypeError):
                continue
            
            # 检测阈值
            result = self._check_threshold(rule.threshold_config, numeric_value)
            
            if result["triggered"]:
                # 检查触发条件（连续次数）
                if self._check_trigger_condition(device_code, rule, result["triggered"]):
                    # 检查静默期
                    if self._check_silent_period(device_code, rule):
                        # 创建报警记录
                        alarm = await self._create_alarm_record(
                            rule=rule,
                            device_code=device_code,
                            device_name=device_name,
                            device_type_code=device_type_code,
                            field_code=field_code,
                            trigger_value=numeric_value,
                            level=result["level"],
                            message=result["message"]
                        )
                        if alarm:
                            triggered_alarms.append(alarm)
            else:
                # 重置触发计数
                self._reset_trigger_count(device_code, rule.rule_code)
        
        return triggered_alarms
    
    def _check_threshold(self, config: Dict, value: float) -> Dict:
        """检测阈值"""
        threshold_type = config.get("type", "range")
        
        # 按严重程度从高到低检查
        for level in ["emergency", "critical", "warning"]:
            if level not in config:
                continue
            
            threshold = config[level]
            triggered = False
            message = ""
            
            if threshold_type == "range":
                min_val = threshold.get("min")
                max_val = threshold.get("max")
                if min_val is not None and value < min_val:
                    triggered = True
                    message = f"低于下限 {min_val}，当前值 {value}"
                elif max_val is not None and value > max_val:
                    triggered = True
                    message = f"超过上限 {max_val}，当前值 {value}"
                    
            elif threshold_type == "upper":
                max_val = threshold.get("max")
                if max_val is not None and value > max_val:
                    triggered = True
                    message = f"超过上限 {max_val}，当前值 {value}"
                    
            elif threshold_type == "lower":
                min_val = threshold.get("min")
                if min_val is not None and value < min_val:
                    triggered = True
                    message = f"低于下限 {min_val}，当前值 {value}"
            
            if triggered:
                return {"triggered": True, "level": level, "message": message}
        
        return {"triggered": False, "level": None, "message": "正常"}
    
    def _check_trigger_condition(self, device_code: str, rule: AlarmRule, triggered: bool) -> bool:
        """检查触发条件（连续次数）"""
        rule_code = rule.rule_code
        condition = rule.trigger_condition or {}
        consecutive_count = condition.get("consecutive_count", 1)
        
        if device_code not in self._trigger_counts:
            self._trigger_counts[device_code] = {}
        
        if triggered:
            current_count = self._trigger_counts[device_code].get(rule_code, 0) + 1
            self._trigger_counts[device_code][rule_code] = current_count
            
            if current_count >= consecutive_count:
                return True
        else:
            self._trigger_counts[device_code][rule_code] = 0
        
        return False
    
    def _reset_trigger_count(self, device_code: str, rule_code: str) -> None:
        """重置触发计数"""
        if device_code in self._trigger_counts:
            self._trigger_counts[device_code][rule_code] = 0
    
    def _check_silent_period(self, device_code: str, rule: AlarmRule) -> bool:
        """检查静默期（避免重复报警）"""
        rule_code = rule.rule_code
        notification_config = rule.notification_config or {}
        silent_period = notification_config.get("silent_period", 300)  # 默认5分钟
        
        if device_code not in self._last_alarm_time:
            self._last_alarm_time[device_code] = {}
        
        last_time = self._last_alarm_time[device_code].get(rule_code)
        now = datetime.now()
        
        if last_time:
            elapsed = (now - last_time).total_seconds()
            if elapsed < silent_period:
                return False
        
        # 更新最后报警时间
        self._last_alarm_time[device_code][rule_code] = now
        return True
    
    async def _create_alarm_record(
        self,
        rule: AlarmRule,
        device_code: str,
        device_name: Optional[str],
        device_type_code: str,
        field_code: str,
        trigger_value: float,
        level: str,
        message: str
    ) -> Optional[Dict]:
        """创建报警记录"""
        try:
            # 生成报警代码
            alarm_code = f"{rule.rule_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            record = await AlarmRecord.create(
                rule_id=rule.id,
                device_code=device_code,
                device_name=device_name,
                device_type_code=device_type_code,
                alarm_code=alarm_code,
                alarm_level=level,
                alarm_title=f"{rule.rule_name} - {device_code}",
                alarm_content=message,
                field_code=field_code,
                field_name=rule.field_name,
                trigger_value=Decimal(str(trigger_value)),
                threshold_value=rule.threshold_config,
                triggered_at=datetime.now(),
                status="active",
            )
            
            logger.warning(f"报警触发: {rule.rule_name}, 设备: {device_code}, 级别: {level}, {message}")
            
            alarm_data = {
                "id": record.id,
                "rule_id": rule.id,
                "rule_name": rule.rule_name,
                "device_code": device_code,
                "device_name": device_name,
                "alarm_level": level,
                "alarm_title": record.alarm_title,
                "alarm_content": message,
                "field_code": field_code,
                "field_name": rule.field_name,
                "trigger_value": trigger_value,
                "triggered_at": record.triggered_at.isoformat(),
            }
            
            # 创建报警通知
            try:
                from app.services.notification_service import create_alarm_notification
                await create_alarm_notification(alarm_data)
            except Exception as notify_error:
                logger.error(f"创建报警通知失败: {str(notify_error)}")
            
            return alarm_data
            
        except Exception as e:
            logger.error(f"创建报警记录失败: {str(e)}")
            return None
    
    async def refresh_rules(self) -> None:
        """强制刷新规则缓存"""
        await self.load_rules(force=True)
    
    def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        total_rules = sum(len(rules) for rules in self._rules_cache.values())
        return {
            "total_rules": total_rules,
            "device_types": list(self._rules_cache.keys()),
            "cache_time": self._cache_time.isoformat() if self._cache_time else None,
            "trigger_counts": len(self._trigger_counts),
        }


# 全局单例
alarm_engine = AlarmDetectionEngine()


async def check_and_trigger_alarms(
    device_code: str,
    device_name: Optional[str],
    device_type_code: str,
    data: Dict[str, Any]
) -> List[Dict]:
    """
    检测设备数据并触发报警（供其他模块调用）
    
    Args:
        device_code: 设备编码
        device_name: 设备名称
        device_type_code: 设备类型代码
        data: 设备数据字典
        
    Returns:
        触发的报警列表
    """
    return await alarm_engine.check_device_data(
        device_code=device_code,
        device_name=device_name,
        device_type_code=device_type_code,
        data=data
    )
