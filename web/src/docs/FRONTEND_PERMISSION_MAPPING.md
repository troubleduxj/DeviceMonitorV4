# 前端按钮权限配置指南

## 权限配置流程

### 1. 在角色管理界面配置权限

1. 进入 **系统管理 → 角色管理**
2. 点击要配置的角色的 **"编辑"** 按钮
3. 切换到 **"权限设置"** 标签页
4. 使用权限树选择器选择对应的API权限

### 2. 前端按钮权限映射关系

以下是各个页面按钮与后端API权限的对应关系：

## 系统管理页面

### 角色管理页面 (`/system/roles`)

| 按钮名称 | 权限配置 | 对应API权限 |
|---------|---------|------------|
| 新增角色 | `resource="role", action="create"` | `POST /api/v1/roles` |
| 刷新 | `resource="role", action="read"` | `GET /api/v1/roles` |
| 保存 | `resource="role", action="update"` | `PUT /api/v1/roles` |

**配置方法：**
1. 在权限树中找到 **"角色管理"** 模块
2. 选择对应的操作：
   - 勾选 `POST /api/v1/roles` → 显示"新增角色"按钮
   - 勾选 `GET /api/v1/roles` → 显示"刷新"按钮  
   - 勾选 `PUT /api/v1/roles` → 显示"保存"按钮

## AI监控页面

### 趋势预测页面 (`/ai-monitor/trend-prediction`)

| 按钮名称 | 权限配置 | 对应API权限 |
|---------|---------|------------|
| 开始预测 | `resource="ai-monitor", action="predict"` | `POST /api/v1/ai-monitor/predict` |
| 刷新数据 | `resource="ai-monitor", action="read"` | `GET /api/v1/ai-monitor` |
| 导出报告 | `resource="ai-monitor", action="export"` | `GET /api/v1/ai-monitor/export` |
| 安排维护 | `resource="device", action="update"` | `PUT /api/v1/devices` |

**配置方法：**
1. 在权限树中找到 **"AI监控"** 模块
2. 选择对应的操作：
   - 勾选 `POST /api/v1/ai-monitor/predict` → 显示"开始预测"按钮
   - 勾选 `GET /api/v1/ai-monitor` → 显示"刷新数据"按钮
   - 勾选 `GET /api/v1/ai-monitor/export` → 显示"导出报告"按钮

### 数据标注页面 (`/ai-monitor/data-annotation`)

| 按钮名称 | 权限配置 | 对应API权限 |
|---------|---------|------------|
| 新建项目 | `resource="ai-monitor", action="create"` | `POST /api/v1/ai-monitor` |
| 导入数据 | `resource="ai-monitor", action="import"` | `POST /api/v1/ai-monitor/import` |
| 刷新 | `resource="ai-monitor", action="read"` | `GET /api/v1/ai-monitor` |
| 保存 | `resource="ai-monitor", action="update"` | `PUT /api/v1/ai-monitor` |

### 模型管理页面 (`/ai-monitor/model-management`)

| 按钮名称 | 权限配置 | 对应API权限 |
|---------|---------|------------|
| 上传模型 | `resource="ai-monitor", action="import"` | `POST /api/v1/ai-monitor/models` |
| 刷新 | `resource="ai-monitor", action="read"` | `GET /api/v1/ai-monitor/models` |

### 健康评分页面 (`/ai-monitor/health-scoring`)

| 按钮名称 | 权限配置 | 对应API权限 |
|---------|---------|------------|
| 刷新数据 | `resource="ai-monitor", action="read"` | `GET /api/v1/ai-monitor/health` |
| 导出报告 | `resource="ai-monitor", action="export"` | `GET /api/v1/ai-monitor/health/export` |
| 评分配置 | `resource="ai-monitor", action="config"` | `PUT /api/v1/ai-monitor/health/config` |

### 智能分析页面 (`/ai-monitor/smart-analysis`)

| 按钮名称 | 权限配置 | 对应API权限 |
|---------|---------|------------|
| 新建分析 | `resource="ai-monitor", action="create"` | `POST /api/v1/ai-monitor/analysis` |
| 刷新 | `resource="ai-monitor", action="read"` | `GET /api/v1/ai-monitor/analysis` |

## 设备监控页面

### 设备监控页面 (`/device-monitor`)

| 按钮名称 | 权限配置 | 对应API权限 |
|---------|---------|------------|
| 刷新数据 | `resource="device", action="read"` | `GET /api/v1/devices` |

**配置方法：**
1. 在权限树中找到 **"设备管理"** 模块
2. 勾选 `GET /api/v1/devices` → 显示"刷新数据"按钮

## 报警管理页面

### 报警信息页面 (`/alarm/alarm-info`)

| 按钮名称 | 权限配置 | 对应API权限 |
|---------|---------|------------|
| 查询 | `resource="alarm", action="read"` | `GET /api/v1/alarms` |
| 重置 | `resource="alarm", action="read"` | `GET /api/v1/alarms` |

**配置方法：**
1. 在权限树中找到 **"报警管理"** 模块
2. 勾选 `GET /api/v1/alarms` → 显示查询和重置按钮

## 仪表板页面

### 焊接仪表板 (`/dashboard/dashboard-weld`)

| 按钮名称 | 权限配置 | 对应API权限 |
|---------|---------|------------|
| 更多报警 | `resource="alarm", action="read"` | `GET /api/v1/alarms` |

## 权限配置最佳实践

### 1. 角色权限配置建议

**超级管理员 (super_admin)**
- 勾选所有权限
- 可以访问所有功能

**系统管理员 (system_admin)**
- 勾选系统管理相关权限：
  - `GET /api/v1/roles`
  - `POST /api/v1/roles`
  - `PUT /api/v1/roles`
  - `DELETE /api/v1/roles`
  - `GET /api/v1/users`
  - `POST /api/v1/users`
  - `PUT /api/v1/users`

**设备管理员 (device_manager)**
- 勾选设备和报警相关权限：
  - `GET /api/v1/devices`
  - `PUT /api/v1/devices`
  - `GET /api/v1/alarms`
  - `PUT /api/v1/alarms`

**AI分析师 (ai_analyst)**
- 勾选AI监控相关权限：
  - `GET /api/v1/ai-monitor`
  - `POST /api/v1/ai-monitor`
  - `PUT /api/v1/ai-monitor`
  - `GET /api/v1/ai-monitor/export`
  - `POST /api/v1/ai-monitor/predict`

**普通用户 (regular_user)**
- 只勾选查看权限：
  - `GET /api/v1/devices`
  - `GET /api/v1/alarms`
  - `GET /api/v1/ai-monitor`

### 2. 权限配置验证

配置完权限后，可以通过以下方式验证：

1. **登录对应角色的用户**
2. **访问相关页面**
3. **检查按钮是否按预期显示/隐藏**
4. **测试按钮点击是否有权限**

### 3. 批量配置技巧

在权限树界面中，你可以使用：

1. **按模块批量选择** - 点击模块名称快速选择整个模块的权限
2. **按操作类型批量选择** - 点击"GET操作"、"POST操作"等快速选择同类操作
3. **搜索功能** - 输入关键词快速找到特定权限
4. **全选/清空** - 快速选择或清空所有权限

### 4. 权限生效

权限配置保存后：
- **立即生效** - 用户下次刷新页面或重新登录后生效
- **动态更新** - 如果实现了权限动态更新，可以实时生效

## 常见问题

### Q: 为什么配置了权限但按钮还是不显示？
A: 检查以下几点：
1. 权限是否正确保存
2. 用户是否重新登录
3. API权限名称是否与前端配置一致
4. 是否有缓存问题

### Q: 如何添加新的按钮权限？
A: 
1. 在后端添加对应的API权限
2. 在前端使用PermissionButton组件
3. 在角色管理界面配置对应权限

### Q: 权限配置后多久生效？
A: 
- 默认情况下需要用户重新登录
- 如果实现了权限动态更新，可以实时生效