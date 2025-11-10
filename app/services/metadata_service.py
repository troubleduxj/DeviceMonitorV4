"""
元数据管理服务
提供设备字段定义、数据模型、字段映射的业务逻辑
"""

from typing import List, Optional, Dict, Any, Tuple
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from app.models.device import DeviceField, DeviceDataModel, DeviceFieldMapping, ModelExecutionLog
from app.schemas.metadata import (
    DeviceFieldCreate, DeviceFieldUpdate,
    DeviceDataModelCreate, DeviceDataModelUpdate,
    DeviceFieldMappingCreate, DeviceFieldMappingUpdate,
    ModelExecutionLogCreate
)
from app.core.exceptions import APIException
import logging

logger = logging.getLogger(__name__)


class MetadataService:
    """元数据管理服务"""
    
    # =====================================================
    # 设备字段定义管理
    # =====================================================
    
    @staticmethod
    async def create_field(field_data: DeviceFieldCreate) -> DeviceField:
        """创建设备字段定义"""
        try:
            field = await DeviceField.create(**field_data.model_dump())
            logger.info(f"创建设备字段成功: {field.field_name} ({field.field_code})")
            return field
        except Exception as e:
            logger.error(f"创建设备字段失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_field_by_id(field_id: int) -> Optional[DeviceField]:
        """根据ID获取字段定义"""
        try:
            return await DeviceField.get(id=field_id)
        except DoesNotExist:
            return None
    
    @staticmethod
    async def get_fields(
        device_type_code: Optional[str] = None,
        field_category: Optional[str] = None,
        is_monitoring_key: Optional[bool] = None,
        is_ai_feature: Optional[bool] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[DeviceField], int]:
        """获取字段定义列表（分页）"""
        query = DeviceField.all()
        
        # 构建查询条件
        if device_type_code:
            query = query.filter(device_type_code=device_type_code)
        if field_category:
            query = query.filter(field_category=field_category)
        if is_monitoring_key is not None:
            query = query.filter(is_monitoring_key=is_monitoring_key)
        if is_ai_feature is not None:
            query = query.filter(is_ai_feature=is_ai_feature)
        if is_active is not None:
            query = query.filter(is_active=is_active)
        if search:
            query = query.filter(
                Q(field_name__icontains=search) | 
                Q(field_code__icontains=search) |
                Q(description__icontains=search)
            )
        
        # 统计总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        fields = await query.order_by('device_type_code', 'sort_order').offset(offset).limit(page_size)
        
        return fields, total
    
    @staticmethod
    async def update_field(field_id: int, field_data: DeviceFieldUpdate) -> Optional[DeviceField]:
        """更新字段定义"""
        try:
            field = await DeviceField.get(id=field_id)
            update_data = field_data.model_dump(exclude_unset=True)
            await field.update_from_dict(update_data).save()
            logger.info(f"更新设备字段成功: {field.field_name}")
            return field
        except DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"更新设备字段失败: {str(e)}")
            raise
    
    @staticmethod
    async def delete_field(field_id: int) -> bool:
        """删除字段定义（软删除）"""
        try:
            field = await DeviceField.get(id=field_id)
            field.is_active = False
            await field.save()
            logger.info(f"删除设备字段成功: {field.field_name}")
            return True
        except DoesNotExist:
            return False
    
    # =====================================================
    # 数据模型管理
    # =====================================================
    
    @staticmethod
    async def create_model(model_data: DeviceDataModelCreate) -> DeviceDataModel:
        """创建数据模型"""
        try:
            # 转换 Pydantic 模型为字典
            model_dict = model_data.model_dump()
            
            # 处理嵌套的 Pydantic 模型
            model_dict['selected_fields'] = [f.model_dump() for f in model_data.selected_fields]
            if model_data.aggregation_config:
                model_dict['aggregation_config'] = model_data.aggregation_config.model_dump()
            if model_data.ai_config:
                model_dict['ai_config'] = model_data.ai_config.model_dump()
            
            model = await DeviceDataModel.create(**model_dict)
            logger.info(f"创建数据模型成功: {model.model_name} ({model.model_code})")
            return model
        except Exception as e:
            logger.error(f"创建数据模型失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_model_by_id(model_id: int) -> Optional[DeviceDataModel]:
        """根据ID获取数据模型"""
        try:
            return await DeviceDataModel.get(id=model_id)
        except DoesNotExist:
            return None
    
    @staticmethod
    async def get_model_by_code(model_code: str, version: Optional[str] = None) -> Optional[DeviceDataModel]:
        """根据编码获取数据模型"""
        try:
            query = DeviceDataModel.filter(model_code=model_code)
            if version:
                query = query.filter(version=version)
            else:
                # 获取最新版本
                query = query.filter(is_active=True)
            return await query.first()
        except Exception:
            return None
    
    @staticmethod
    async def get_models(
        device_type_code: Optional[str] = None,
        model_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[DeviceDataModel], int]:
        """获取数据模型列表（分页）"""
        query = DeviceDataModel.all()
        
        # 构建查询条件
        if device_type_code:
            query = query.filter(device_type_code=device_type_code)
        if model_type:
            query = query.filter(model_type=model_type)
        if is_active is not None:
            query = query.filter(is_active=is_active)
        if search:
            query = query.filter(
                Q(model_name__icontains=search) | 
                Q(model_code__icontains=search)
            )
        
        # 统计总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        models = await query.order_by('-created_at').offset(offset).limit(page_size)
        
        return models, total
    
    @staticmethod
    async def update_model(model_id: int, model_data: DeviceDataModelUpdate) -> Optional[DeviceDataModel]:
        """更新数据模型"""
        try:
            model = await DeviceDataModel.get(id=model_id)
            update_dict = model_data.model_dump(exclude_unset=True)
            
            # 处理嵌套的 Pydantic 模型
            if 'selected_fields' in update_dict and update_dict['selected_fields']:
                update_dict['selected_fields'] = [f.model_dump() if hasattr(f, 'model_dump') else f for f in update_dict['selected_fields']]
            if 'aggregation_config' in update_dict and update_dict['aggregation_config']:
                if hasattr(update_dict['aggregation_config'], 'model_dump'):
                    update_dict['aggregation_config'] = update_dict['aggregation_config'].model_dump()
            if 'ai_config' in update_dict and update_dict['ai_config']:
                if hasattr(update_dict['ai_config'], 'model_dump'):
                    update_dict['ai_config'] = update_dict['ai_config'].model_dump()
            
            await model.update_from_dict(update_dict).save()
            logger.info(f"更新数据模型成功: {model.model_name}")
            return model
        except DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"更新数据模型失败: {str(e)}")
            raise
    
    @staticmethod
    async def delete_model(model_id: int) -> bool:
        """删除数据模型（软删除）"""
        try:
            model = await DeviceDataModel.get(id=model_id)
            model.is_active = False
            await model.save()
            logger.info(f"删除数据模型成功: {model.model_name}")
            return True
        except DoesNotExist:
            return False
    
    @staticmethod
    async def activate_model(model_id: int) -> Optional[DeviceDataModel]:
        """激活数据模型（同时停用同类型的其他模型）"""
        try:
            model = await DeviceDataModel.get(id=model_id)
            
            # 停用同设备类型、同模型类型的其他激活模型
            await DeviceDataModel.filter(
                device_type_code=model.device_type_code,
                model_type=model.model_type,
                is_active=True
            ).exclude(id=model_id).update(is_active=False)
            
            # 激活当前模型
            model.is_active = True
            await model.save()
            
            logger.info(f"激活数据模型成功: {model.model_name}")
            return model
        except DoesNotExist:
            return None
    
    # =====================================================
    # 字段映射管理
    # =====================================================
    
    @staticmethod
    async def create_mapping(mapping_data: DeviceFieldMappingCreate) -> DeviceFieldMapping:
        """创建字段映射"""
        try:
            mapping_dict = mapping_data.model_dump()
            if mapping_data.transform_rule:
                mapping_dict['transform_rule'] = mapping_data.transform_rule.model_dump()
            
            mapping = await DeviceFieldMapping.create(**mapping_dict)
            logger.info(f"创建字段映射成功: {mapping.tdengine_stable}.{mapping.tdengine_column}")
            return mapping
        except Exception as e:
            logger.error(f"创建字段映射失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_mapping_by_id(mapping_id: int) -> Optional[DeviceFieldMapping]:
        """根据ID获取字段映射"""
        try:
            return await DeviceFieldMapping.get(id=mapping_id).prefetch_related('device_field')
        except DoesNotExist:
            return None
    
    @staticmethod
    async def get_mappings(
        device_type_code: Optional[str] = None,
        tdengine_stable: Optional[str] = None,
        is_tag: Optional[bool] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[DeviceFieldMapping], int]:
        """获取字段映射列表（分页）"""
        query = DeviceFieldMapping.all().prefetch_related('device_field')
        
        # 构建查询条件
        if device_type_code:
            query = query.filter(device_type_code=device_type_code)
        if tdengine_stable:
            query = query.filter(tdengine_stable=tdengine_stable)
        if is_tag is not None:
            query = query.filter(is_tag=is_tag)
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        # 统计总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        mappings = await query.order_by('device_type_code', 'tdengine_stable', 'tdengine_column').offset(offset).limit(page_size)
        
        return mappings, total
    
    @staticmethod
    async def update_mapping(mapping_id: int, mapping_data: DeviceFieldMappingUpdate) -> Optional[DeviceFieldMapping]:
        """更新字段映射"""
        try:
            mapping = await DeviceFieldMapping.get(id=mapping_id)
            update_dict = mapping_data.model_dump(exclude_unset=True)
            
            if 'transform_rule' in update_dict and update_dict['transform_rule']:
                if hasattr(update_dict['transform_rule'], 'model_dump'):
                    update_dict['transform_rule'] = update_dict['transform_rule'].model_dump()
            
            await mapping.update_from_dict(update_dict).save()
            logger.info(f"更新字段映射成功: {mapping.tdengine_stable}.{mapping.tdengine_column}")
            return mapping
        except DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"更新字段映射失败: {str(e)}")
            raise
    
    @staticmethod
    async def delete_mapping(mapping_id: int) -> bool:
        """删除字段映射"""
        try:
            mapping = await DeviceFieldMapping.get(id=mapping_id)
            await mapping.delete()
            logger.info(f"删除字段映射成功: {mapping.tdengine_stable}.{mapping.tdengine_column}")
            return True
        except DoesNotExist:
            return False
    
    # =====================================================
    # 模型执行日志
    # =====================================================
    
    @staticmethod
    async def create_execution_log(log_data: ModelExecutionLogCreate) -> ModelExecutionLog:
        """创建执行日志"""
        try:
            log = await ModelExecutionLog.create(**log_data.model_dump())
            return log
        except Exception as e:
            logger.error(f"创建执行日志失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_execution_logs(
        model_id: Optional[int] = None,
        execution_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[ModelExecutionLog], int]:
        """获取执行日志列表（分页）"""
        query = ModelExecutionLog.all().prefetch_related('model')
        
        # 构建查询条件
        if model_id:
            query = query.filter(model_id=model_id)
        if execution_type:
            query = query.filter(execution_type=execution_type)
        if status:
            query = query.filter(status=status)
        
        # 统计总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        logs = await query.order_by('-executed_at').offset(offset).limit(page_size)
        
        return logs, total
    
    # =====================================================
    # 统计功能
    # =====================================================
    
    @staticmethod
    async def get_model_statistics() -> Dict[str, Any]:
        """获取模型统计信息"""
        total_models = await DeviceDataModel.all().count()
        active_models = await DeviceDataModel.filter(is_active=True).count()
        realtime_models = await DeviceDataModel.filter(model_type='realtime').count()
        statistics_models = await DeviceDataModel.filter(model_type='statistics').count()
        ai_models = await DeviceDataModel.filter(model_type='ai_analysis').count()
        
        total_executions = await ModelExecutionLog.all().count()
        success_executions = await ModelExecutionLog.filter(status='success').count()
        success_rate = (success_executions / total_executions * 100) if total_executions > 0 else 0
        
        # 计算平均执行时间
        avg_time_result = await ModelExecutionLog.filter(
            status='success',
            execution_time_ms__isnull=False
        ).values_list('execution_time_ms')
        
        avg_execution_time_ms = 0
        if avg_time_result:
            times = [t[0] for t in avg_time_result if t[0] is not None]
            avg_execution_time_ms = sum(times) / len(times) if times else 0
        
        return {
            'total_models': total_models,
            'active_models': active_models,
            'realtime_models': realtime_models,
            'statistics_models': statistics_models,
            'ai_models': ai_models,
            'total_executions': total_executions,
            'success_rate': round(success_rate, 2),
            'avg_execution_time_ms': round(avg_execution_time_ms, 2)
        }

