from typing import List, Optional, Dict, Any
from datetime import datetime
from tortoise.expressions import Q
from tortoise.queryset import QuerySet
from fastapi import HTTPException

from app.core.crud import CRUDBase
from app.models.device import WeldingAlarmHistory
from app.schemas.devices import WeldingAlarmHistoryQuery
from app.log import logger


class AlarmController:
    """报警控制器
    
    提供报警历史数据的查询和业务逻辑处理
    """
    
    def __init__(self):
        self.model = WeldingAlarmHistory
    
    async def get_welding_alarm_history(
        self,
        device_type: Optional[str] = None,
        device_code: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取焊接报警历史数据
        
        Args:
            device_type: 设备类型
            device_code: 设备编号
            start_time: 开始时间
            end_time: 结束时间
            page: 页码
            page_size: 每页数量
            
        Returns:
            包含报警历史数据和分页信息的字典
            
        Raises:
            HTTPException: 当查询参数无效时
        """
        try:
            # 验证设备类型参数
            if not device_type:
                logger.warning("设备类型参数为空")
                raise HTTPException(status_code=400, detail="请选择设备类型")
            
            # 设备类型过滤 - 当前只支持welding类型
            if device_type != "welding":
                logger.warning(f"不支持的设备类型: {device_type}")
                raise HTTPException(status_code=400, detail="您选择的设备类型暂时无法查询")
            
            # 构建查询条件
            query = self.model.all()
            
            # 设备编号过滤
            if device_code:
                query = query.filter(prod_code=device_code)
            
            # 时间范围过滤
            if start_time:
                query = query.filter(alarm_time__gte=start_time)
            
            if end_time:
                query = query.filter(alarm_time__lte=end_time)
            
            # 获取总数
            total = await query.count()
            
            # 分页查询
            offset = (page - 1) * page_size
            items = await query.offset(offset).limit(page_size).order_by("-alarm_time").values(
                "id", "prod_code", "alarm_time", "alarm_end_time", 
                "alarm_duration_sec", "alarm_code", "alarm_message", "alarm_solution"
            )
            
            # 为每个项目添加默认的时间戳字段
            for item in items:
                item["created_at"] = item["alarm_time"]  # 使用alarm_time作为created_at
                item["updated_at"] = item["alarm_time"]  # 使用alarm_time作为updated_at
            
            # 计算总页数
            total_pages = (total + page_size - 1) // page_size
            
            logger.info(f"查询焊接报警历史数据成功，共{total}条记录")
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"查询焊接报警历史数据失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="查询报警历史数据失败")
    
    async def get_alarm_statistics(
        self,
        device_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取报警统计信息
        
        Args:
            device_type: 设备类型
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            报警统计信息字典
        """
        try:
            # 构建查询条件
            query = self.model.all()
            
            # 设备类型过滤
            if device_type and device_type != "welding":
                return {
                    "total_alarms": 0,
                    "active_alarms": 0,
                    "resolved_alarms": 0,
                    "avg_duration": 0
                }
            
            # 时间范围过滤
            if start_time:
                query = query.filter(alarm_time__gte=start_time)
            
            if end_time:
                query = query.filter(alarm_time__lte=end_time)
            
            # 获取统计数据
            total_alarms = await query.count()
            active_alarms = await query.filter(alarm_end_time__isnull=True).count()
            resolved_alarms = await query.filter(alarm_end_time__isnull=False).count()
            
            # 计算平均持续时间（只计算已结束的报警）
            resolved_items = await query.filter(
                alarm_end_time__isnull=False,
                alarm_duration_sec__isnull=False
            ).values_list("alarm_duration_sec", flat=True)
            
            avg_duration = 0
            if resolved_items:
                avg_duration = sum(resolved_items) / len(resolved_items)
            
            logger.info(f"获取报警统计信息成功，总报警数: {total_alarms}")
            
            return {
                "total_alarms": total_alarms,
                "active_alarms": active_alarms,
                "resolved_alarms": resolved_alarms,
                "avg_duration": round(avg_duration, 2)
            }
            
        except Exception as e:
            logger.error(f"获取报警统计信息失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="获取报警统计信息失败")


# 创建全局实例
alarm_controller = AlarmController()