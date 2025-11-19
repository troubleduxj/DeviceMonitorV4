# API分类预览报告

生成时间: 2025-11-19 16:24:33

## 总体统计

- 扫描到的路由总数: 537
- 数据库已存在: 118
- 需要新增: 419
- 分类数量: 34


## 设备管理
- 总数: 79
- 已存在: 28
- 需新增: 51
- 描述: 设备增删改查、类型管理、状态监控

### 需要新增的API (51个):
  - GET /list
  - GET /get
  - GET /get_by_code
  - POST /create
  - POST /update
  - DELETE /delete
  - GET /by_type
  - GET /by_location
  - GET /by_team
  - GET /locked
  ... 还有 41 个

## 用户管理
- 总数: 37
- 已存在: 20
- 需新增: 17
- 描述: 用户增删改查、角色分配、状态管理

### 需要新增的API (17个):
  - GET /usermenu
  - GET /userapi
  - GET /api/v2/users/
  - GET /api/v2/users/export
  - DELETE /api/v2/users/batch
  - POST /api/v2/users/
  - POST /api/v2/users/search
  - POST /api/v2/users/
  - GET /api/v2/users/
  - POST /api/v2/users/{user_id}/reset-password
  ... 还有 7 个

## 角色管理
- 总数: 34
- 已存在: 13
- 需新增: 21
- 描述: 角色增删改查、权限分配、层级管理

### 需要新增的API (21个):
  - GET /api/v2/roles/
  - POST /api/v2/roles/
  - DELETE /api/v2/roles/batch
  - POST /api/v2/roles/batch
  - PUT /api/v2/roles/batch
  - GET /api/v2/roles/{role_id}/users
  - POST /api/v2/roles/{role_id}/users
  - DELETE /api/v2/roles/{role_id}/users/{user_id}
  - GET /api/v2/roles/tree
  - POST /api/v2/roles/
  ... 还有 11 个

## 字典管理
- 总数: 31
- 已存在: 10
- 需新增: 21
- 描述: 字典类型、字典数据管理

### 需要新增的API (21个):
  - POST /predict
  - POST /api/v2/dict-data/batch
  - PUT /api/v2/dict-data/batch
  - DELETE /api/v2/dict-data/batch
  - GET /api/v2/dict-data/by-type/{type_code}
  - POST /api/v2/dict-types/batch
  - PUT /api/v2/dict-types/batch
  - DELETE /api/v2/dict-types/batch
  - PUT /{dict_type_id}
  - PATCH /{dict_type_id}
  ... 还有 11 个

## 菜单管理
- 总数: 27
- 已存在: 6
- 需新增: 21
- 描述: 菜单增删改查、权限配置、可见性控制

### 需要新增的API (21个):
  - GET /api/v2/menus/
  - POST /api/v2/menus/batch
  - PATCH /api/v2/menus/batch
  - DELETE /api/v2/menus/batch
  - GET /api/v2/menus/tree
  - POST /api/v2/menus/
  - PUT /api/v2/menus/{menu_id}
  - GET /api/v2/menus/{menu_id}/usage
  - GET /api/v2/menus/user-menus
  - GET /api/v2/menus/user-menus/{user_id}
  ... 还有 11 个

## 权限性能监控
- 总数: 26
- 已存在: 0
- 需新增: 26
- 描述: 权限检查性能监控、缓存优化

### 需要新增的API (26个):
  - GET /api/v2/permission/performance/metrics
  - POST /api/v2/permission/performance/batch-check
  - POST /api/v2/permission/performance/preload-users
  - POST /api/v2/permission/performance/warm-up-cache
  - POST /api/v2/permission/performance/optimize-patterns
  - POST /api/v2/permission/performance/async-check
  - GET /api/v2/permission/performance/async-result/{task_id}
  - GET /api/v2/permission/performance/monitor/summary
  - GET /api/v2/permission/performance/monitor/history/{metric}
  - GET /api/v2/permission/performance/monitor/alerts
  ... 还有 16 个

## 部门管理
- 总数: 25
- 已存在: 6
- 需新增: 19
- 描述: 部门增删改查、层级管理、权限范围

### 需要新增的API (19个):
  - GET /api/v2/departments/
  - POST /api/v2/departments/
  - POST /api/v2/departments/batch
  - DELETE /api/v2/departments/batch
  - GET /api/v2/departments/{dept_id}/users
  - PUT /api/v2/departments/{dept_id}/users/{user_id}
  - DELETE /api/v2/departments/{dept_id}/users/{user_id}
  - GET /api/v2/departments/accessible
  - POST /api/v2/departments/check-access
  - POST /api/v2/departments/check-cross-access
  ... 还有 9 个

## API管理
- 总数: 21
- 已存在: 9
- 需新增: 12
- 描述: API端点管理、分组管理、权限配置

### 需要新增的API (12个):
  - GET /
  - GET /
  - GET /charts
  - GET /audit
  - POST /reorganize
  - POST /auto-map
  - POST /sync-endpoints
  - GET /report
  - POST /optimize
  - POST /repair-codes/generate
  ... 还有 2 个

## 设备维护管理
- 总数: 21
- 已存在: 3
- 需新增: 18
- 描述: 设备维护记录、维修记录、计划管理

### 需要新增的API (18个):
  - GET /api/v2/device/maintenance/maintenance/records
  - GET /api/v2/device/maintenance/maintenance/records/{record_id}
  - POST /api/v2/device/maintenance/maintenance/records
  - PUT /api/v2/device/maintenance/maintenance/records/{record_id}
  - DELETE /api/v2/device/maintenance/maintenance/records/{record_id}
  - GET /api/v2/device/maintenance/maintenance/plans
  - POST /api/v2/device/maintenance/maintenance/plans
  - GET /api/v2/device/maintenance/maintenance/reminders
  - GET /api/v2/device/maintenance/maintenance/statistics
  - GET /repair-records/statistics
  ... 还有 8 个

## 元数据管理
- 总数: 21
- 已存在: 0
- 需新增: 21
- 描述: 字段管理、模型管理、映射配置

### 需要新增的API (21个):
  - POST /api/v2/metadata/fields
  - GET /api/v2/metadata/fields
  - GET /api/v2/metadata/fields/{field_id}
  - PUT /api/v2/metadata/fields/{field_id}
  - DELETE /api/v2/metadata/fields/{field_id}
  - POST /api/v2/metadata/models
  - GET /api/v2/metadata/models
  - GET /api/v2/metadata/models/{model_id}
  - GET /api/v2/metadata/models/code/{model_code}
  - PUT /api/v2/metadata/models/{model_id}
  ... 还有 11 个

## 权限配置
- 总数: 17
- 已存在: 0
- 需新增: 17
- 描述: 权限端点配置、规则管理、版本控制

### 需要新增的API (17个):
  - GET /api/v2/permission-config/endpoints
  - GET /api/v2/permission-config/endpoints/{api_code}
  - POST /api/v2/permission-config/endpoints
  - PUT /api/v2/permission-config/endpoints/{api_code}
  - DELETE /api/v2/permission-config/endpoints/{api_code}
  - GET /api/v2/permission-config/rules
  - GET /api/v2/permission-config/rules/{rule_id}
  - POST /api/v2/permission-config/rules
  - PUT /api/v2/permission-config/rules/{rule_id}
  - DELETE /api/v2/permission-config/rules/{rule_id}
  ... 还有 7 个

## 文档管理
- 总数: 16
- 已存在: 6
- 需新增: 10
- 描述: API文档、变更日志、版本管理

### 需要新增的API (10个):
  - GET /api/v2/docs/changelog/breaking
  - GET /api/v2/docs/swagger/generate
  - GET /api/v2/docs/swagger/download
  - GET /api/v2/docs/swagger/modules
  - POST /api/v2/docs/sync
  - GET /api/v2/docs/sync/status
  - GET /api/v2/docs/versions/{version}
  - GET /api/v2/docs/changes
  - GET /docs
  - GET /redoc

## TDengine管理
- 总数: 15
- 已存在: 0
- 需新增: 15
- 描述: TDengine服务器管理、数据库查询

### 需要新增的API (15个):
  - GET /api/tdengine/servers
  - GET /api/tdengine/servers/{server_name}
  - POST /api/tdengine/servers/{server_name}
  - DELETE /api/tdengine/servers/{server_name}
  - POST /api/tdengine/servers/{server_name}/set-default
  - GET /api/tdengine/health
  - GET /api/tdengine/health/{server_name}
  - POST /api/tdengine/test-connection/{server_name}
  - GET /api/tdengine/statistics
  - GET /api/tdengine/databases
  ... 还有 5 个

## 批量操作
- 总数: 15
- 已存在: 0
- 需新增: 15
- 描述: 批量操作、权限验证、模拟执行

### 需要新增的API (15个):
  - DELETE /api/v2/batch/users/batch
  - PUT /api/v2/batch/users/batch
  - POST /api/v2/batch/users/batch-deactivate
  - DELETE /api/v2/batch/roles/batch
  - DELETE /api/v2/batch/devices/batch
  - PUT /api/v2/batch/devices/batch
  - POST /api/v2/batch/manual-check-example
  - POST /api/v2/batch/check-permission
  - GET /api/v2/batch/limits/{resource_type}
  - GET /api/v2/batch/supported-resources
  ... 还有 5 个

## 认证管理
- 总数: 13
- 已存在: 4
- 需新增: 9
- 描述: 用户认证、登录登出、密码管理

### 需要新增的API (9个):
  - POST /access_token
  - GET /userinfo
  - POST /update_password
  - GET /api/v2/auth/user
  - GET /api/v2/auth/user/apis
  - GET /api/v2/auth/user-apis
  - GET /api/v2/auth/user/menus
  - POST /api/v2/auth/refresh
  - POST /api/v2/auth/logout-all

## 审计日志
- 总数: 12
- 已存在: 0
- 需新增: 12
- 描述: 审计日志、安全事件、操作记录

### 需要新增的API (12个):
  - GET /api/v2/audit/dashboard
  - GET /api/v2/audit/trends
  - GET /api/v2/audit/users/{user_id}/activity
  - GET /api/v2/audit/summary
  - GET /{log_id}
  - GET /api/v2/audit/logs
  - GET /api/v2/audit/security-events
  - GET /api/v2/audit/statistics
  - GET /api/v2/audit/action-types
  - GET /api/v2/audit/risk-levels
  ... 还有 2 个

## 系统监控
- 总数: 11
- 已存在: 0
- 需新增: 11
- 描述: 系统性能监控、健康检查、指标统计

### 需要新增的API (11个):
  - GET /api/monitoring/health
  - GET /api/monitoring/performance/stats
  - GET /api/monitoring/performance/functions
  - GET /api/monitoring/performance/metrics
  - GET /api/monitoring/system/metrics
  - GET /api/monitoring/alerts
  - POST /api/monitoring/export
  - DELETE /api/monitoring/metrics
  - GET /api/v2/system/health
  - GET /api/v2/system/modules/ai/config
  ... 还有 1 个

## AI预测
- 总数: 11
- 已存在: 0
- 需新增: 11
- 描述: AI预测、风险评估、报告生成

### 需要新增的API (11个):
  - GET /api/v2/ai/predictions/{prediction_id}
  - PUT /api/v2/ai/predictions/{prediction_id}
  - DELETE /api/v2/ai/predictions/{prediction_id}
  - GET /api/v2/ai/predictions/{prediction_id}/export
  - POST /api/v2/ai/predictions/{prediction_id}/share
  - POST /api/v2/ai/predictions/batch
  - GET /api/v2/ai/predictions/history
  - POST /api/v2/ai/predictions/batch-delete
  - GET /api/v2/ai/prediction-analytics/risk-assessment
  - GET /api/v2/ai/prediction-analytics/health-trend
  ... 还有 1 个

## 设备工艺管理
- 总数: 10
- 已存在: 0
- 需新增: 10
- 描述: 工艺管理、执行记录、模板管理

### 需要新增的API (10个):
  - GET /api/v2/device/processes
  - GET /api/v2/device/processes/{process_id}
  - POST /api/v2/device/processes
  - PUT /api/v2/device/processes/{process_id}
  - DELETE /api/v2/device/processes/{process_id}
  - GET /api/v2/device/processes/executions
  - POST /api/v2/device/processes/executions
  - GET /api/v2/device/processes/templates
  - POST /api/v2/device/processes/templates
  - GET /api/v2/device/processes/statistics

## 系统参数
- 总数: 10
- 已存在: 3
- 需新增: 7
- 描述: 系统参数配置

### 需要新增的API (7个):
  - DELETE /api/v2/system-params/batch
  - GET /api/v2/system-params/cached/{param_key}
  - GET /{param_id}
  - PUT /{param_id}
  - DELETE /{param_id}
  - DELETE /batch
  - GET /cached/{param_key}

## AI分析
- 总数: 9
- 已存在: 0
- 需新增: 9
- 描述: AI分析任务、结果查询

### 需要新增的API (9个):
  - POST /analysis
  - POST /analysis
  - POST /heavy-analysis
  - GET /api/v2/ai/analysis/{analysis_id}
  - PUT /api/v2/ai/analysis/{analysis_id}
  - DELETE /api/v2/ai/analysis/{analysis_id}
  - GET /api/v2/ai/analysis/{analysis_id}/results
  - POST /api/v2/ai/analysis/{analysis_id}/schedule
  - POST /api/v2/ai/analysis/batch-delete

## 安全管理
- 总数: 9
- 已存在: 0
- 需新增: 9
- 描述: 安全事件、威胁检测、IP统计

### 需要新增的API (9个):
  - GET /api/security/security/summary
  - GET /api/security/security/events
  - GET /api/security/security/threats
  - GET /api/security/security/ip/{ip_address}
  - GET /api/security/security/ip/{ip_address}/events
  - POST /api/security/security/cleanup
  - GET /api/security/security/config
  - GET /api/security/security/status
  - GET /api/security/security/enums

## API分组管理
- 总数: 9
- 已存在: 4
- 需新增: 5
- 描述: API分组的增删改查

### 需要新增的API (5个):
  - GET /api/v2/api-groups/all
  - DELETE /api/v2/api-groups/batch
  - GET /api/v2/api-groups/{group_id}/apis
  - POST /api/v2/api-groups/{group_id}/apis
  - DELETE /api/v2/api-groups/{group_id}/apis/{api_id}

## AI模型
- 总数: 8
- 已存在: 0
- 需新增: 8
- 描述: AI模型管理、训练、部署

### 需要新增的API (8个):
  - GET /api/v2/ai/models/{model_id}
  - POST /api/v2/ai/models/upload
  - PUT /api/v2/ai/models/{model_id}
  - DELETE /api/v2/ai/models/{model_id}
  - POST /api/v2/ai/models/{model_id}/train
  - GET /api/v2/ai/models/{model_id}/metrics
  - POST /api/v2/ai/models/{model_id}/deploy
  - POST /api/v2/ai/models/batch-delete

## 设备字段配置
- 总数: 7
- 已存在: 0
- 需新增: 7
- 描述: 设备字段配置、缓存管理

### 需要新增的API (7个):
  - GET /api/v2/device/device-fields/{device_type_code}
  - GET /api/v2/device/device-fields
  - POST /api/v2/device/device-fields
  - PUT /api/v2/device/device-fields/{field_id}
  - DELETE /api/v2/device/device-fields/{field_id}
  - POST /api/v2/device/device-fields/cache/clear
  - GET /api/v2/device/device-fields/cache/status

## Mock数据
- 总数: 7
- 已存在: 0
- 需新增: 7
- 描述: Mock数据规则管理

### 需要新增的API (7个):
  - GET /api/v2/mock/{mock_id}
  - PUT /api/v2/mock/{mock_id}
  - DELETE /api/v2/mock/{mock_id}
  - POST /api/v2/mock/batch-delete
  - POST /api/v2/mock/{mock_id}/toggle
  - GET /api/v2/mock/active/list
  - POST /api/v2/mock/{mock_id}/hit

## AI健康评分
- 总数: 7
- 已存在: 0
- 需新增: 7
- 描述: AI健康评分、趋势分析

### 需要新增的API (7个):
  - GET /api/v2/ai/health-scores/{score_id}
  - PUT /api/v2/ai/health-scores/{score_id}
  - DELETE /api/v2/ai/health-scores/{score_id}
  - GET /api/v2/ai/health-scores/export
  - PUT /api/v2/ai/health-scores/config
  - GET /api/v2/ai/health-scores/trends
  - POST /api/v2/ai/health-scores/batch-delete

## 基础服务
- 总数: 6
- 已存在: 3
- 需新增: 3
- 描述: 基础服务接口

### 需要新增的API (3个):
  - GET /api/v2/base/userinfo
  - POST /api/v2/base/logout
  - POST /api/v2/base/refresh

## AI标注
- 总数: 6
- 已存在: 0
- 需新增: 6
- 描述: AI标注数据管理

### 需要新增的API (6个):
  - GET /api/v2/ai/annotations/{project_id}
  - PUT /api/v2/ai/annotations/{project_id}
  - DELETE /api/v2/ai/annotations/{project_id}
  - POST /api/v2/ai/annotations/{project_id}/import
  - GET /api/v2/ai/annotations/{project_id}/export
  - POST /api/v2/ai/annotations/batch-delete

## 报警管理
- 总数: 5
- 已存在: 3
- 需新增: 2
- 描述: 报警记录、处理、统计

### 需要新增的API (2个):
  - PUT /api/v2/alarms/batch-handle
  - GET /api/v2/alarms/statistics

## 动态模型
- 总数: 5
- 已存在: 0
- 需新增: 5
- 描述: 动态模型生成、缓存管理

### 需要新增的API (5个):
  - POST /api/v2/dynamic-models/generate
  - GET /api/v2/dynamic-models/fields-info
  - DELETE /api/v2/dynamic-models/cache
  - GET /api/v2/dynamic-models/cache/stats
  - POST /api/v2/dynamic-models/validate

## 数据查询
- 总数: 4
- 已存在: 0
- 需新增: 4
- 描述: 实时数据查询、统计查询

### 需要新增的API (4个):
  - POST /api/v2/data/query/realtime
  - POST /api/v2/data/query/statistics
  - GET /api/v2/data/models/{model_code}/preview
  - GET /api/v2/data/models/list

## 头像管理
- 总数: 2
- 已存在: 0
- 需新增: 2
- 描述: 用户头像生成和管理

### 需要新增的API (2个):
  - GET /generate/{username}
  - GET /api/v2/avatar/generate/{username}

## 其他
- 总数: 1
- 已存在: 0
- 需新增: 1
- 描述: 

### 需要新增的API (1个):
  - GET /