#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报警管理API v2
提供报警的查看、处理、确认和统计功能
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.base import APIResponse, PaginatedResponse
from app.core.response_formatter_v2 import create_formatter
from app.core.pagination import get_pagination_params, create_pagination_response
from app.log import logger


# 报警相关枚举和模型
class AlarmLevel(str, Enum):
    """报警级别枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlarmStatus(str, Enum):
    """报警状态枚举"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlarmType(str, Enum):
    """报警类型枚举"""
    SYSTEM = "system"
    DEVICE = "device"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"


# 请求和响应模型
class AlarmQuery(BaseModel):
    """报警查询参数"""
    level: Optional[str] = Field(None, description="报警级别过滤")
    status: Optional[str] = Field(None, description="报警状态过滤")
    alarm_type: Optional[str] = Field(None, description="报警类型过滤")
    source: Optional[str] = Field(None, description="报警源过滤")
    date_from: Optional[datetime] = Field(None, description="开始时间")
    date_to: Optional[datetime] = Field(None, description="结束时间")
    search: Optional[str] = Field(None, description="搜索关键词")


class AlarmResponse(BaseModel):
    """报警响应模型"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    id: int = Field(..., description="报警ID")
    title: str = Field(..., description="报警标题")
    description: str = Field(..., description="报警描述")
    level: AlarmLevel = Field(..., description="报警级别")
    status: AlarmStatus = Field(..., description="报警状态")
    alarm_type: AlarmType = Field(..., description="报警类型")
    source: str = Field(..., description="报警源")
    source_id: Optional[int] = Field(None, description="报警源ID")
    rule_id: Optional[int] = Field(None, description="报警规则ID")
    rule_name: Optional[str] = Field(None, description="报警规则名称")
    triggered_at: datetime = Field(..., description="触发时间")
    acknowledged_at: Optional[datetime] = Field(None, description="确认时间")
    acknowledged_by: Optional[int] = Field(None, description="确认人ID")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    resolved_by: Optional[int] = Field(None, description="解决人ID")
    closed_at: Optional[datetime] = Field(None, description="关闭时间")
    closed_by: Optional[int] = Field(None, description="关闭人ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="报警数据")
    tags: List[str] = Field(default_factory=list, description="报警标签")
    count: int = Field(1, description="报警次数")
    last_occurrence: datetime = Field(..., description="最后发生时间")
    resolution_notes: Optional[str] = Field(None, description="解决备注")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class AlarmHandleRequest(BaseModel):
    """报警处理请求"""
    action: str = Field(..., description="处理动作: acknowledge, resolve, close")
    notes: Optional[str] = Field(None, description="处理备注")


class BatchAlarmHandleRequest(BaseModel):
    """批量报警处理请求"""
    alarm_ids: List[int] = Field(..., description="报警ID列表")
    action: str = Field(..., description="处理动作: acknowledge, resolve, close")
    notes: Optional[str] = Field(None, description="处理备注")


class AlarmAcknowledgeRequest(BaseModel):
    """报警确认请求"""
    notes: Optional[str] = Field(None, description="确认备注")


class AlarmStatisticsResponse(BaseModel):
    """报警统计响应"""
    total_alarms: int = Field(..., description="总报警数")
    active_alarms: int = Field(..., description="活跃报警数")
    acknowledged_alarms: int = Field(..., description="已确认报警数")
    resolved_alarms: int = Field(..., description="已解决报警数")
    closed_alarms: int = Field(..., description="已关闭报警数")
    by_level: Dict[str, int] = Field(..., description="按级别统计")
    by_type: Dict[str, int] = Field(..., description="按类型统计")
    by_source: Dict[str, int] = Field(..., description="按来源统计")
    trend_data: List[Dict[str, Any]] = Field(..., description="趋势数据")


router = APIRouter(tags=["报警管理"])


@router.get("", response_model=APIResponse[PaginatedResponse[AlarmResponse]])
async def get_alarms(
    query: AlarmQuery = Depends(),
    pagination: dict = Depends(get_pagination_params),
    device_type: Optional[str] = Query(None, description="设备类型，当前支持：welding")
):
    """
    获取报警列表
    
    支持按级别、状态、类型、来源等条件过滤，支持关键词搜索
    从数据库查询真实的焊接报警历史数据
    """
    try:
        # 导入焊接报警历史模型
        from app.models.device import WeldingAlarmHistory
        
        # 构建查询条件
        db_query = WeldingAlarmHistory.all()
        
        # 处理搜索关键词（设备编号）
        if query.search:
            db_query = db_query.filter(prod_code__contains=query.search)
        
        # 处理时间范围过滤
        if query.date_from:
            # 支持多种时间格式
            parsed_start_time = query.date_from
            if isinstance(query.date_from, str):
                if 'T' in query.date_from:
                    # ISO格式：2025-07-31T16:00:00
                    parsed_start_time = datetime.fromisoformat(query.date_from.replace('Z', '+00:00'))
                else:
                    # 标准格式：2025-07-31 16:00:00
                    try:
                        parsed_start_time = datetime.strptime(query.date_from, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # 尝试只有日期的格式：2025-07-31
                        parsed_start_time = datetime.strptime(query.date_from, '%Y-%m-%d')
            db_query = db_query.filter(alarm_time__gte=parsed_start_time)
            logger.info(f"应用开始时间过滤: {parsed_start_time}")
            
        if query.date_to:
            # 支持多种时间格式
            parsed_end_time = query.date_to
            if isinstance(query.date_to, str):
                if 'T' in query.date_to:
                    # ISO格式：2025-07-31T16:00:00
                    parsed_end_time = datetime.fromisoformat(query.date_to.replace('Z', '+00:00'))
                else:
                    # 标准格式：2025-07-31 16:00:00
                    try:
                        parsed_end_time = datetime.strptime(query.date_to, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # 尝试只有日期的格式：2025-07-31
                        parsed_end_time = datetime.strptime(query.date_to, '%Y-%m-%d')
                        # 如果只有日期，设置为当天的最后一刻
                        parsed_end_time = parsed_end_time.replace(hour=23, minute=59, second=59)
            db_query = db_query.filter(alarm_time__lte=parsed_end_time)
            logger.info(f"应用结束时间过滤: {parsed_end_time}")
        
        # 获取总数
        total = await db_query.count()
        
        # 分页查询
        offset = pagination["offset"]
        limit = pagination["limit"]
        alarms = await db_query.offset(offset).limit(limit).order_by('-alarm_time')
        
        # 转换数据格式为前端期望的格式
        alarm_responses = []
        for alarm in alarms:
            item = {
                "id": alarm.id,
                "prod_code": alarm.prod_code,
                "alarm_time": alarm.alarm_time.isoformat() if alarm.alarm_time else None,
                "alarm_end_time": alarm.alarm_end_time.isoformat() if alarm.alarm_end_time else None,
                "alarm_duration_sec": alarm.alarm_duration_sec,
                "alarm_code": alarm.alarm_code,
                "alarm_message": alarm.alarm_message,
                "alarm_solution": alarm.alarm_solution,
                "created_at": alarm.alarm_time.isoformat() if alarm.alarm_time else None,
                "updated_at": alarm.alarm_time.isoformat() if alarm.alarm_time else None
            }
            alarm_responses.append(item)
        
        # 创建分页响应
        paginated_response = create_pagination_response(
            data=alarm_responses,
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
        
        formatter = create_formatter()
        logger.info(f"获取报警列表成功，共{total}条记录，当前页{pagination['page']}条记录")
        return formatter.success(
            data=paginated_response,
            message=f"获取报警列表成功，共{total}条记录"
        )
        
    except Exception as e:
        logger.error(f"获取报警列表失败: {str(e)}", exc_info=True)
        formatter = create_formatter()
        return formatter.error(
            message="获取报警列表失败"
        )


@router.get("/{alarm_id}", response_model=APIResponse[AlarmResponse])
async def get_alarm(alarm_id: int):
    """获取报警详情"""
    try:
        alarm_data = await simulate_get_alarm_detail(alarm_id)
        if not alarm_data:
            formatter = create_formatter()
            return formatter.error(
                message="报警不存在",
                code=404
            )
        
        alarm_response = AlarmResponse(**alarm_data)
        
        formatter = create_formatter()
        return formatter.success(
            data=alarm_response,
            message="获取报警详情成功"
        )
        
    except Exception as e:
        logger.error(f"获取报警详情失败: alarm_id={alarm_id}, 错误: {str(e)}")
        formatter = create_formatter()
        return formatter.error(
            message="获取报警详情失败"
        )


@router.put("/{alarm_id}/handle", response_model=APIResponse[AlarmResponse])
async def handle_alarm(
    alarm_id: int,
    handle_data: AlarmHandleRequest,
    current_user_id: int = 1  # TODO: 从认证中获取
):
    """处理报警"""
    try:
        # 验证处理动作
        valid_actions = ["acknowledge", "resolve", "close"]
        if handle_data.action not in valid_actions:
            formatter = create_formatter()
            return formatter.error(
                message=f"无效的处理动作: {handle_data.action}",
                code=400
            )
        
        # 模拟处理报警
        alarm_data = await simulate_handle_alarm(alarm_id, handle_data.action, handle_data.notes, current_user_id)
        if not alarm_data:
            formatter = create_formatter()
            return formatter.error(
                message="报警不存在",
                code=404
            )
        
        alarm_response = AlarmResponse(**alarm_data)
        
        formatter = create_formatter()
        return formatter.success(
            data=alarm_response,
            message=f"报警{handle_data.action}成功"
        )
        
    except Exception as e:
        logger.error(f"处理报警失败: alarm_id={alarm_id}, 错误: {str(e)}")
        formatter = create_formatter()
        return formatter.error(
            message="处理报警失败"
        )


@router.put("/batch-handle", response_model=APIResponse[dict])
async def batch_handle_alarms(
    batch_data: BatchAlarmHandleRequest,
    current_user_id: int = 1  # TODO: 从认证中获取
):
    """批量处理报警"""
    try:
        # 验证处理动作
        valid_actions = ["acknowledge", "resolve", "close"]
        if batch_data.action not in valid_actions:
            formatter = create_formatter()
            return formatter.error(
                message=f"无效的处理动作: {batch_data.action}",
                code=400
            )
        
        success_count = 0
        failed_count = 0
        failed_ids = []
        errors = []
        
        for alarm_id in batch_data.alarm_ids:
            try:
                result = await simulate_handle_alarm(alarm_id, batch_data.action, batch_data.notes, current_user_id)
                if result:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_ids.append(alarm_id)
                    errors.append(f"报警 {alarm_id} 不存在")
                    
            except Exception as e:
                failed_count += 1
                failed_ids.append(alarm_id)
                errors.append(f"处理报警 {alarm_id} 失败: {str(e)}")
        
        formatter = create_formatter()
        return formatter.success(
            data={
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_ids": failed_ids,
                "errors": errors
            },
            message=f"批量处理完成，成功 {success_count} 个，失败 {failed_count} 个"
        )
        
    except Exception as e:
        logger.error(f"批量处理报警失败: {str(e)}")
        formatter = create_formatter()
        return formatter.error(
            message="批量处理报警失败",
            details={"error": str(e)}
        )


@router.post("/{alarm_id}/acknowledge", response_model=APIResponse[AlarmResponse])
async def acknowledge_alarm(
    alarm_id: int,
    ack_data: AlarmAcknowledgeRequest,
    current_user_id: int = 1  # TODO: 从认证中获取
):
    """确认报警"""
    try:
        alarm_data = await simulate_handle_alarm(alarm_id, "acknowledge", ack_data.notes, current_user_id)
        if not alarm_data:
            formatter = create_formatter()
            return formatter.error(
                message="报警不存在",
                code=404
            )
        
        alarm_response = AlarmResponse(**alarm_data)
        
        formatter = create_formatter()
        return formatter.success(
            data=alarm_response,
            message="确认报警成功"
        )
        
    except Exception as e:
        logger.error(f"确认报警失败: alarm_id={alarm_id}, 错误: {str(e)}")
        formatter = create_formatter()
        return formatter.error(
            message="确认报警失败",
            details={"error": str(e)}
        )


@router.get("/statistics", response_model=APIResponse[AlarmStatisticsResponse])
async def get_alarm_statistics(
    date_from: Optional[datetime] = Query(None, description="统计开始时间"),
    date_to: Optional[datetime] = Query(None, description="统计结束时间"),
    alarm_type: Optional[str] = Query(None, description="报警类型过滤")
):
    """获取报警统计"""
    try:
        # 设置默认时间范围（最近30天）
        if not date_from:
            date_from = datetime.now() - timedelta(days=30)
        if not date_to:
            date_to = datetime.now()
        
        # 模拟统计数据
        statistics = await simulate_get_alarm_statistics(date_from, date_to, alarm_type)
        
        statistics_response = AlarmStatisticsResponse(**statistics)
        
        formatter = create_formatter()
        return formatter.success(
            data=statistics_response,
            message="获取报警统计成功"
        )
        
    except Exception as e:
        logger.error(f"获取报警统计失败: {str(e)}")
        formatter = create_formatter()
        return formatter.error(
            message="获取报警统计失败",
            details={"error": str(e)}
        )


# =====================================================
# 模拟数据和辅助函数
# =====================================================

async def simulate_get_alarms(query: AlarmQuery, pagination: dict) -> Dict[str, Any]:
    """模拟获取报警列表"""
    # 模拟报警数据
    base_alarms = [
        {
            "id": 1,
            "title": "设备温度过高",
            "description": "焊接设备001温度超过安全阈值",
            "level": "critical",
            "status": "active",
            "alarm_type": "device",
            "source": "device_monitor",
            "source_id": 1001,
            "rule_id": 101,
            "rule_name": "设备温度监控",
            "triggered_at": datetime.now() - timedelta(hours=2),
            "acknowledged_at": None,
            "acknowledged_by": None,
            "resolved_at": None,
            "resolved_by": None,
            "closed_at": None,
            "closed_by": None,
            "data": {
                "device_id": 1001,
                "temperature": 85.6,
                "threshold": 80.0,
                "sensor_id": "TEMP_001"
            },
            "tags": ["temperature", "critical", "device"],
            "count": 3,
            "last_occurrence": datetime.now() - timedelta(minutes=15),
            "resolution_notes": None,
            "created_at": datetime.now() - timedelta(hours=2),
            "updated_at": datetime.now() - timedelta(minutes=15)
        },
        {
            "id": 2,
            "title": "系统CPU使用率过高",
            "description": "监控服务器CPU使用率持续超过90%",
            "level": "high",
            "status": "acknowledged",
            "alarm_type": "system",
            "source": "system_monitor",
            "source_id": 2001,
            "rule_id": 102,
            "rule_name": "系统资源监控",
            "triggered_at": datetime.now() - timedelta(hours=1),
            "acknowledged_at": datetime.now() - timedelta(minutes=30),
            "acknowledged_by": 1,
            "resolved_at": None,
            "resolved_by": None,
            "closed_at": None,
            "closed_by": None,
            "data": {
                "cpu_usage": 92.3,
                "threshold": 90.0,
                "server_id": 2001,
                "process_count": 156
            },
            "tags": ["cpu", "performance", "system"],
            "count": 1,
            "last_occurrence": datetime.now() - timedelta(hours=1),
            "resolution_notes": None,
            "created_at": datetime.now() - timedelta(hours=1),
            "updated_at": datetime.now() - timedelta(minutes=30)
        },
        {
            "id": 3,
            "title": "网络连接异常",
            "description": "设备002网络连接中断",
            "level": "medium",
            "status": "resolved",
            "alarm_type": "device",
            "source": "network_monitor",
            "source_id": 1002,
            "rule_id": 103,
            "rule_name": "网络连接监控",
            "triggered_at": datetime.now() - timedelta(hours=3),
            "acknowledged_at": datetime.now() - timedelta(hours=2, minutes=30),
            "acknowledged_by": 2,
            "resolved_at": datetime.now() - timedelta(minutes=45),
            "resolved_by": 2,
            "closed_at": None,
            "closed_by": None,
            "data": {
                "device_id": 1002,
                "last_ping": (datetime.now() - timedelta(hours=3)).isoformat(),
                "network_status": "disconnected"
            },
            "tags": ["network", "connectivity", "device"],
            "count": 1,
            "last_occurrence": datetime.now() - timedelta(hours=3),
            "resolution_notes": "网络线路已修复",
            "created_at": datetime.now() - timedelta(hours=3),
            "updated_at": datetime.now() - timedelta(minutes=45)
        }
    ]
    
    # 应用过滤条件
    filtered_alarms = base_alarms.copy()
    
    if query.level:
        filtered_alarms = [a for a in filtered_alarms if a["level"] == query.level]
    
    if query.status:
        filtered_alarms = [a for a in filtered_alarms if a["status"] == query.status]
    
    if query.alarm_type:
        filtered_alarms = [a for a in filtered_alarms if a["alarm_type"] == query.alarm_type]
    
    if query.source:
        filtered_alarms = [a for a in filtered_alarms if a["source"] == query.source]
    
    if query.search:
        search_lower = query.search.lower()
        filtered_alarms = [
            a for a in filtered_alarms 
            if search_lower in a["title"].lower() or search_lower in a["description"].lower()
        ]
    
    # 分页
    total = len(filtered_alarms)
    start = pagination["offset"]
    end = start + pagination["limit"]
    items = filtered_alarms[start:end]
    
    return {
        "items": items,
        "total": total
    }


async def simulate_get_alarm_detail(alarm_id: int) -> Optional[Dict[str, Any]]:
    """模拟获取报警详情"""
    alarms_data = await simulate_get_alarms(AlarmQuery(), {"offset": 0, "limit": 100})
    
    for alarm in alarms_data["items"]:
        if alarm["id"] == alarm_id:
            return alarm
    
    return None


async def simulate_handle_alarm(alarm_id: int, action: str, notes: Optional[str], user_id: int) -> Optional[Dict[str, Any]]:
    """模拟处理报警"""
    alarm_data = await simulate_get_alarm_detail(alarm_id)
    if not alarm_data:
        return None
    
    now = datetime.now()
    
    if action == "acknowledge":
        alarm_data["status"] = "acknowledged"
        alarm_data["acknowledged_at"] = now
        alarm_data["acknowledged_by"] = user_id
    elif action == "resolve":
        alarm_data["status"] = "resolved"
        alarm_data["resolved_at"] = now
        alarm_data["resolved_by"] = user_id
        if notes:
            alarm_data["resolution_notes"] = notes
    elif action == "close":
        alarm_data["status"] = "closed"
        alarm_data["closed_at"] = now
        alarm_data["closed_by"] = user_id
    
    alarm_data["updated_at"] = now
    
    return alarm_data


async def simulate_get_alarm_statistics(date_from: datetime, date_to: datetime, alarm_type: Optional[str]) -> Dict[str, Any]:
    """模拟获取报警统计"""
    # 模拟统计数据
    statistics = {
        "total_alarms": 156,
        "active_alarms": 23,
        "acknowledged_alarms": 45,
        "resolved_alarms": 78,
        "closed_alarms": 10,
        "by_level": {
            "critical": 12,
            "high": 34,
            "medium": 67,
            "low": 32,
            "info": 11
        },
        "by_type": {
            "system": 45,
            "device": 78,
            "performance": 23,
            "security": 8,
            "business": 2
        },
        "by_source": {
            "device_monitor": 89,
            "system_monitor": 34,
            "network_monitor": 23,
            "security_monitor": 8,
            "business_monitor": 2
        },
        "trend_data": [
            {"date": "2024-01-01", "count": 12, "critical": 2, "high": 4, "medium": 5, "low": 1},
            {"date": "2024-01-02", "count": 15, "critical": 3, "high": 5, "medium": 6, "low": 1},
            {"date": "2024-01-03", "count": 8, "critical": 1, "high": 2, "medium": 4, "low": 1},
            {"date": "2024-01-04", "count": 18, "critical": 4, "high": 6, "medium": 7, "low": 1},
            {"date": "2024-01-05", "count": 11, "critical": 2, "high": 3, "medium": 5, "low": 1},
            {"date": "2024-01-06", "count": 14, "critical": 2, "high": 4, "medium": 6, "low": 2},
            {"date": "2024-01-07", "count": 9, "critical": 1, "high": 2, "medium": 5, "low": 1}
        ]
    }
    
    # 如果指定了报警类型，调整统计数据
    if alarm_type and alarm_type in statistics["by_type"]:
        type_count = statistics["by_type"][alarm_type]
        ratio = type_count / statistics["total_alarms"]
        
        # 按比例调整各项统计
        for key in ["total_alarms", "active_alarms", "acknowledged_alarms", "resolved_alarms", "closed_alarms"]:
            statistics[key] = int(statistics[key] * ratio)
    
    return statistics