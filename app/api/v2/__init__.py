"""
API v2 路由模块
提供新版本的API接口
"""
from fastapi import APIRouter

# 创建v2版本的路由器（不需要前缀，因为在主路由中已经添加了/v2前缀）
v2_router = APIRouter()

# 导入v2版本的子路由
from .base import router as base_router
from .auth import router as auth_router
from .users import router as users_router
from .roles import router as roles_router
from .menus import router as menus_router
from .departments import router as departments_router
from .devices import router as devices_router
from .device_maintenance import router as device_maintenance_router
from .device_repair_records import router as device_repair_records_router
from .device_process import router as device_process_router
from .device_field_config import router as device_field_config_router
from .health import router as health_router
from .docs import router as docs_router

# 导入新增的系统管理模块路由
from .apis import router as apis_router
from .api_groups import router as api_groups_router
from .api_classification import router as api_classification_router
from .audit_logs import router as audit_logs_router
# from .audit import router as audit_router  # 新的权限审计系统 - 暂时注释
# from .batch_operations import router as batch_operations_router  # 批量操作权限控制 - 暂时注释
from .dict_types import router as dict_types_router
from .dict_data import router as dict_data_router
from .system_params import router as system_params_router
from .avatar import router as avatar_router
from .alarms import router as alarms_router
from .init_button_permissions import router as init_button_permissions_router
from .mock_data import router as mock_data_router

# ⭐ 导入元数据管理模块路由（新增）
from .metadata import router as metadata_router
from .metadata_sync import router as metadata_sync_router  # 元数据同步路由
# ⭐ 导入动态模型模块路由（Phase 2 新增）
from .dynamic_models import router as dynamic_models_router
# ⭐ 导入数据查询模块路由（Phase 2 新增）
from .data_query import router as data_query_router
# ⭐ 导入系统健康检查路由（AI模块支持）
from .system_health import router as system_health_router

# ⭐ 条件导入AI模块路由（阶段1核心完善）
# 这些导入会被下面的条件注册使用

# 导入性能优化控制器
# from app.controllers.permission_performance_controller import router as performance_router  # 暂时注释
# from app.controllers.permission_performance_optimization_controller import router as performance_optimization_router  # 暂时注释

# 注册基础模块路由
v2_router.include_router(base_router, prefix="/base", tags=["基础功能 v2"])
v2_router.include_router(auth_router, prefix="/auth", tags=["认证管理 v2"])
v2_router.include_router(avatar_router, prefix="/avatar", tags=["头像生成 v2"])

# 注册系统管理模块路由
v2_router.include_router(users_router, prefix="/users", tags=["用户管理 v2"])
v2_router.include_router(roles_router, prefix="/roles", tags=["角色管理 v2"])
v2_router.include_router(menus_router, prefix="/menus", tags=["菜单管理 v2"])
v2_router.include_router(departments_router, prefix="/departments", tags=["部门管理 v2"])

# 注册新增的系统管理模块路由
v2_router.include_router(apis_router, prefix="/apis", tags=["API管理 v2"])
v2_router.include_router(api_groups_router, prefix="/api-groups", tags=["API分组管理 v2"])
v2_router.include_router(api_classification_router, prefix="/api-classification", tags=["API分类优化 v2"])
v2_router.include_router(audit_logs_router, prefix="/audit-logs", tags=["审计日志 v2"])
# v2_router.include_router(audit_router, prefix="/audit", tags=["权限审计系统 v2"])  # 新的权限审计系统 - 暂时注释
# v2_router.include_router(batch_operations_router, prefix="/batch", tags=["批量操作权限控制 v2"])  # 批量操作权限控制 - 暂时注释
# v2_router.include_router(performance_router, prefix="/performance", tags=["权限系统性能优化 v2"])  # 权限系统性能优化 - 暂时注释
# v2_router.include_router(performance_optimization_router, prefix="/performance-optimization", tags=["权限系统性能优化增强 v2"])  # 权限系统性能优化增强 - 暂时注释
v2_router.include_router(dict_types_router, prefix="/dict-types", tags=["字典类型管理 v2"])
v2_router.include_router(dict_data_router, prefix="/dict-data", tags=["字典数据管理 v2"])
v2_router.include_router(system_params_router, prefix="/system-params", tags=["系统参数管理 v2"])
v2_router.include_router(system_params_router, prefix="/system/config", tags=["系统配置管理 v2"])

# 注册设备管理模块路由
v2_router.include_router(devices_router, prefix="/devices", tags=["设备管理 v2"])
v2_router.include_router(device_maintenance_router, prefix="/device", tags=["设备维护管理 v2"])
v2_router.include_router(device_repair_records_router, prefix="/device/maintenance", tags=["设备维修记录管理 v2"])
v2_router.include_router(device_field_config_router, prefix="/device/config", tags=["设备字段配置管理 v2"])
v2_router.include_router(device_process_router, prefix="/devices", tags=["设备工艺管理 v2"])

# 注册报警管理模块路由
v2_router.include_router(alarms_router, prefix="/alarms", tags=["报警管理 v2"])

# ⭐ 注册元数据管理模块路由（新增）
v2_router.include_router(metadata_router, tags=["元数据管理 v2"])
v2_router.include_router(metadata_sync_router, tags=["元数据同步 v2"])

# ⭐ 注册动态模型模块路由（Phase 2 新增）
v2_router.include_router(dynamic_models_router, tags=["动态模型 v2"])

# ⭐ 注册数据查询模块路由（Phase 2 新增）
v2_router.include_router(data_query_router, tags=["数据查询 v2"])

# 注册其他模块路由
v2_router.include_router(health_router, prefix="/health", tags=["健康检查 v2"])
v2_router.include_router(system_health_router, tags=["系统健康 v2"])  # AI模块健康检查
v2_router.include_router(docs_router, prefix="/docs", tags=["API文档 v2"])
v2_router.include_router(init_button_permissions_router, tags=["系统初始化 v2"])
v2_router.include_router(mock_data_router, tags=["Mock数据管理 v2"])

# ⭐ 条件注册AI模块路由（统一前缀：/ai）
# 只在AI模块启用时注册路由，避免资源浪费
from app.settings.ai_settings import ai_settings

if ai_settings.ai_module_enabled and ai_settings.ai_trend_prediction_enabled:
    try:
        # 预测模块 - 统一使用 /ai 前缀
        from .ai.predictions import router as predictions_router
        from .ai.prediction_analytics import router as prediction_analytics_router
        from .ai.trend_prediction import router as trend_prediction_router
        
        # 全部注册到 /ai 前缀下
        v2_router.include_router(predictions_router, prefix="/ai")
        v2_router.include_router(prediction_analytics_router, prefix="/ai")
        v2_router.include_router(trend_prediction_router, prefix="/ai")
        
        import logging
        logging.info("✅ AI预测模块路由已注册（统一前缀: /api/v2/ai）")
        logging.info("   - /ai/predictions/tasks/...")
        logging.info("   - /ai/predictions/execute/...")
        logging.info("   - /ai/predictions/analytics/...")
    except ImportError as e:
        import logging
        logging.warning(f"⚠️ 无法加载AI预测模块路由: {e}")

__all__ = ["v2_router"]