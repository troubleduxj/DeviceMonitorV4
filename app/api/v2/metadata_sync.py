"""
元数据同步 API V2 接口
提供从TDengine同步字段定义到PostgreSQL的功能
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request, Query, Body
from pydantic import BaseModel, Field

from app.core.response_formatter_v2 import create_formatter
from app.core.dependency import DependAuth
from app.models.admin import User
from app.services.tdengine_service import tdengine_service_manager
from app.services.metadata_service import MetadataService
from app.schemas.metadata import DeviceFieldCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metadata-sync", tags=["元数据同步"])


class TDengineFieldSyncRequest(BaseModel):
    """TDengine字段同步请求"""
    device_type_code: str = Field(..., description="设备类型代码，如 'welding'")
    tdengine_database: str = Field(..., description="TDengine数据库名")
    tdengine_stable: str = Field(..., description="TDengine超级表名")
    server_name: Optional[str] = Field(None, description="TDengine服务器名称")
    field_category: str = Field(default="data_collection", description="字段分类")
    overwrite_existing: bool = Field(default=False, description="是否覆盖已存在的字段")
    selected_fields: Optional[List[str]] = Field(None, description="选择同步的字段代码列表，为空则同步所有")


class FieldTypeMapping:
    """TDengine类型到PostgreSQL类型的映射"""
    
    TDENGINE_TO_PG_TYPE = {
        "TIMESTAMP": "timestamp",
        "INT": "int",
        "BIGINT": "bigint",
        "FLOAT": "float",
        "DOUBLE": "double",
        "BINARY": "string",
        "NCHAR": "string",
        "BOOL": "boolean",
        "TINYINT": "int",
        "SMALLINT": "int",
        "VARCHAR": "string",
    }
    
    @classmethod
    def convert_type(cls, tdengine_type: str) -> str:
        """
        转换TDengine类型到系统字段类型
        
        Args:
            tdengine_type: TDengine类型，如 "INT", "FLOAT"
            
        Returns:
            系统字段类型
        """
        # 提取基础类型（去除长度等修饰符）
        base_type = tdengine_type.upper().split('(')[0].strip()
        return cls.TDENGINE_TO_PG_TYPE.get(base_type, "string")


@router.post("/sync-from-tdengine", summary="从TDengine同步字段定义", response_model=None)
async def sync_fields_from_tdengine(
    request: Request,
    sync_request: TDengineFieldSyncRequest = Body(...),
    current_user: User = DependAuth
):
    """
    从TDengine超级表读取字段结构并同步到 t_device_field 表
    
    工作流程：
    1. 连接TDengine并读取超级表结构
    2. 解析字段信息（字段名、类型、长度）
    3. 检查PostgreSQL中是否已存在该字段
    4. 创建或更新字段定义
    5. 返回同步结果统计
    
    参数说明：
    - device_type_code: 设备类型代码（必填）
    - tdengine_database: TDengine数据库名（必填）
    - tdengine_stable: TDengine超级表名（必填）
    - server_name: TDengine服务器名称（可选，默认使用默认服务器）
    - field_category: 字段分类（可选，默认为 'data_collection'）
    - overwrite_existing: 是否覆盖已存在的字段（可选，默认为 False）
    """
    formatter = create_formatter(request)
    
    try:
        # 1. 获取TDengine服务并读取表结构
        logger.info(f"开始从TDengine同步字段: {sync_request.tdengine_database}.{sync_request.tdengine_stable}")
        
        tdengine_service = tdengine_service_manager.get_service(sync_request.server_name)
        schema_result = await tdengine_service.get_table_schema(
            sync_request.tdengine_database,
            sync_request.tdengine_stable
        )
        
        if not schema_result or not schema_result.get("columns"):
            return formatter.error(
                message=f"无法获取TDengine表结构或表为空: {sync_request.tdengine_stable}",
                code=404
            )
        
        all_columns = schema_result["columns"]
        logger.info(f"从TDengine读取到 {len(all_columns)} 个字段")
        
        # 过滤选中的字段
        if sync_request.selected_fields:
            # 转换为小写以便匹配
            selected_set = {f.lower() for f in sync_request.selected_fields}
            columns = [col for col in all_columns if col["name"].lower() in selected_set]
            logger.info(f"用户选择了 {len(columns)} 个字段进行同步")
        else:
            columns = all_columns
        
        # 2. 检查现有字段
        existing_fields, _ = await MetadataService.get_fields(
            device_type_code=sync_request.device_type_code,
            page=1,
            page_size=1000  # 获取所有字段
        )
        
        # 建立字段代码映射（小写）和字段名称映射（检查名称冲突）
        existing_fields_map = {field.field_code.lower(): field for field in existing_fields if field.field_code}
        existing_names_map = {field.field_name: field for field in existing_fields if field.field_name}
        
        # 3. 处理每个字段
        sync_results = {
            "created": [],
            "skipped": [],
            "errors": [],
            "total": len(columns)
        }
        
        for col in columns:
            field_name_en = col["name"]
            field_type_td = col["type"]
            field_length = col.get("length", 0)
            note = col.get("note", "")
            
            # 跳过时间戳字段（通常是主键）
            if field_name_en.lower() in ["ts", "timestamp", "_ts"]:
                sync_results["skipped"].append({
                    "field_code": field_name_en,
                    "reason": "系统时间戳字段"
                })
                continue
            
            # 检查是否已存在
            field_code = field_name_en.lower()
            existing_field = existing_fields_map.get(field_code)
            
            if existing_field:
                if existing_field.is_active:
                    if not sync_request.overwrite_existing:
                        sync_results["skipped"].append({
                            "field_code": field_code,
                            "reason": "字段已存在"
                        })
                        continue
                    else:
                        # TODO: 实现更新逻辑
                        sync_results["skipped"].append({
                            "field_code": field_code,
                            "reason": "暂不支持覆盖已存在字段"
                        })
                        continue
                else:
                    # 已存在但未激活（软删除），恢复它
                    try:
                        existing_field.is_active = True
                        await existing_field.save()
                        sync_results["created"].append({
                            "field_code": field_code,
                            "field_name": existing_field.field_name,
                            "field_type": existing_field.field_type
                        })
                        continue
                    except Exception as e:
                        sync_results["errors"].append({
                            "field_code": field_code,
                            "error": f"恢复字段失败: {str(e)}"
                        })
                        continue
            
            # 转换字段类型
            field_type = FieldTypeMapping.convert_type(field_type_td)
            
            # 生成字段中文名（默认与英文名相同，可后续手动修改）
            field_name_cn = note if note else field_name_en
            
            # 检查中文名是否冲突，如果冲突则添加后缀
            if field_name_cn in existing_names_map:
                field_name_cn = f"{field_name_cn}_{field_code}"
            
            # 判断是否为TAG（note中包含TAG标记）
            is_tag = "TAG" in note.upper() if note else False
            
            # 创建字段
            try:
                field_data = DeviceFieldCreate(
                    device_type_code=sync_request.device_type_code,
                    field_name=field_name_cn,
                    field_code=field_code,
                    field_type=field_type,
                    field_category=sync_request.field_category,
                    unit=None,  # 需要后续手动设置
                    description=f"从TDengine同步: {sync_request.tdengine_database}.{sync_request.tdengine_stable}.{field_name_en}",
                    is_required=False,
                    default_value=None,
                    validation_rule=None,
                    sort_order=0,
                    is_active=True,
                    is_monitoring_key=False,  # 需要后续手动设置
                    is_ai_feature=field_type in ["int", "float", "double"],  # 数值类型默认可用于AI
                    aggregation_method=None,
                    data_range=None,
                    alarm_threshold=None,
                    display_config=None
                )
                
                created_field = await MetadataService.create_field(field_data)
                
                sync_results["created"].append({
                    "field_code": field_code,
                    "field_name": field_name_cn,
                    "field_type": field_type,
                    "tdengine_type": field_type_td,
                    "id": created_field.id
                })
                
            except Exception as e:
                logger.error(f"创建字段失败: {field_code}, 错误: {str(e)}")
                sync_results["errors"].append({
                    "field_code": field_code,
                    "error": str(e)
                })
        
        # 4. 返回同步结果
        message = f"同步完成！成功创建 {len(sync_results['created'])} 个字段，跳过 {len(sync_results['skipped'])} 个字段"
        if sync_results["errors"]:
            message += f"，失败 {len(sync_results['errors'])} 个字段"
        
        return formatter.success(
            data=sync_results,
            message=message
        )
        
    except Exception as e:
        logger.error(f"从TDengine同步字段失败: {str(e)}", exc_info=True)
        return formatter.internal_error(f"从TDengine同步字段失败: {str(e)}")


@router.get("/preview-tdengine-fields", summary="预览TDengine表字段（不创建）", response_model=None)
async def preview_tdengine_fields(
    request: Request,
    device_type_code: str = Query(..., description="设备类型代码"),
    tdengine_database: str = Query(..., description="TDengine数据库名"),
    tdengine_stable: str = Query(..., description="TDengine超级表名"),
    server_name: Optional[str] = Query(None, description="TDengine服务器名称"),
    current_user: User = DependAuth
):
    """
    预览TDengine表字段结构（不实际创建字段）
    
    用于在同步前查看将要创建哪些字段
    """
    formatter = create_formatter(request)
    
    try:
        # 1. 获取TDengine表结构
        tdengine_service = tdengine_service_manager.get_service(server_name)
        schema_result = await tdengine_service.get_table_schema(
            tdengine_database,
            tdengine_stable
        )
        
        if not schema_result or not schema_result.get("columns"):
            return formatter.error(
                message=f"无法获取TDengine表结构: {tdengine_stable}",
                code=404
            )
        
        # 2. 检查现有字段
        existing_fields, _ = await MetadataService.get_fields(
            device_type_code=device_type_code,
            page=1,
            page_size=1000
        )
        
        existing_fields_map = {field.field_code: field for field in existing_fields}
        
        # 3. 构建预览数据
        preview_fields = []
        for col in schema_result["columns"]:
            field_name_en = col["name"]
            field_code = field_name_en.lower()
            existing_field = existing_fields_map.get(field_code)

            field_type_td = col["type"]
            field_type = FieldTypeMapping.convert_type(field_type_td)
            note = col.get("note", "")
            
            # 判断状态
            if field_name_en.lower() in ["ts", "timestamp", "_ts"]:
                status = "skip_system"
                status_text = "系统字段（跳过）"
            elif existing_field and existing_field.is_active:
                status = "exists"
                status_text = "已存在"
            else:
                status = "new"
                status_text = "将创建"
            
            preview_fields.append({
                "field_code": field_code,
                "field_name": note if note else field_name_en,
                "tdengine_type": field_type_td,
                "field_type": field_type,
                "note": note,
                "status": status,
                "status_text": status_text,
                "is_tag": "TAG" in note.upper() if note else False
            })
        
        return formatter.success(
            data={
                "database": tdengine_database,
                "stable": tdengine_stable,
                "total_fields": len(preview_fields),
                "new_fields": sum(1 for f in preview_fields if f["status"] == "new"),
                "existing_fields": sum(1 for f in preview_fields if f["status"] == "exists"),
                "skip_fields": sum(1 for f in preview_fields if f["status"] == "skip_system"),
                "fields": preview_fields
            },
            message="预览成功"
        )
        
    except Exception as e:
        logger.error(f"预览TDengine字段失败: {str(e)}", exc_info=True)
        return formatter.internal_error(f"预览TDengine字段失败: {str(e)}")

