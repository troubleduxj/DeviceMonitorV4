# Mock数据管理功能使用指南

## 📖 功能概述

Mock数据管理功能允许您在不依赖真实API的情况下，模拟各种数据场景，非常适合：

- 🎯 **系统演示**：展示系统功能而无需真实数据
- 🧪 **前端开发**：后端接口未就绪时进行前端开发
- 🔍 **功能测试**：测试各种数据场景和边界情况
- 🎓 **培训演示**：创建稳定可控的演示环境

---

## 🚀 快速开始

### 1. 安装数据库表

执行以下SQL脚本创建Mock数据表：

```bash
# 进入数据库
psql -U postgres -d device_monitor

# 执行迁移脚本
\i database/migrations/add_mock_data_table.sql
\i database/migrations/add_mock_management_menu.sql
```

或使用psql命令行：

```bash
psql -U postgres -d device_monitor -f database/migrations/add_mock_data_table.sql
psql -U postgres -d device_monitor -f database/migrations/add_mock_management_menu.sql
```

### 2. 初始化按钮权限

1. **重启后端服务**（使权限配置生效）：
```bash
cd d:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2
python run.py
```

2. **在浏览器控制台执行**（F12打开控制台）：
```javascript
const token = localStorage.getItem('access_token');
fetch('/api/v2/system/init-button-permissions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
})
.then(res => res.json())
.then(data => {
  console.log('初始化结果:', data);
  alert(`完成！创建 ${data.data.created} 个，跳过 ${data.data.skipped} 个`);
});
```

3. **刷新页面**（F5）

### 3. 访问Mock管理页面

- 进入系统后，在左侧菜单找到：**Mock数据管理**
- 或直接访问：`http://localhost:3000/advanced-settings/mock-data`

---

## 📋 功能说明

### 创建Mock规则

1. **点击"新建Mock规则"按钮**

2. **填写表单**：

   | 字段 | 说明 | 示例 |
   |------|------|------|
   | 规则名称 | Mock规则的名称 | `模拟设备列表` |
   | 规则描述 | 规则用途说明（可选） | `返回3个设备的模拟数据` |
   | HTTP方法 | API的HTTP方法 | `GET` / `POST` / `PUT` / `DELETE` |
   | URL匹配模式 | 要拦截的API路径 | `/api/v2/devices` |
   | 响应状态码 | HTTP状态码 | `200` |
   | 延迟时间(ms) | 模拟网络延迟 | `0` ~ `10000` |
   | 优先级 | 数字越大越优先匹配 | `0` (默认) |
   | 响应数据 | JSON格式的响应数据 | 见下方示例 |
   | 启用状态 | 是否立即启用 | 启用 / 禁用 |

3. **响应数据示例**：

```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "演示设备001",
        "type": "焊机",
        "status": "在线",
        "location": "车间A-01"
      },
      {
        "id": 2,
        "name": "演示设备002",
        "type": "压力机",
        "status": "离线",
        "location": "车间B-03"
      }
    ],
    "total": 2,
    "page": 1,
    "page_size": 20
  }
}
```

4. **点击"确定"保存**

---

### URL匹配模式

Mock系统支持通配符匹配：

| 模式 | 说明 | 示例 |
|------|------|------|
| `/api/v2/devices` | 精确匹配 | 只匹配该路径 |
| `/api/v2/devices/*` | 单层通配 | 匹配 `/api/v2/devices/123` |
| `/api/v2/devices/**` | 多层通配 | 匹配 `/api/v2/devices/123/details` |
| `/api/v2/*/details` | 中间通配 | 匹配 `/api/v2/users/details` |

**示例**：

```javascript
// 匹配所有设备相关API
url_pattern: '/api/v2/devices/**'

// 匹配特定ID的设备
url_pattern: '/api/v2/devices/123'

// 匹配所有用户API
url_pattern: '/api/v2/users/*'
```

---

### 启用/禁用Mock

有三种方式控制Mock：

#### 方式1：通过UI切换（推荐）

在Mock管理页面，直接点击每条规则的开关按钮。

#### 方式2：全局启用/禁用

在浏览器控制台（F12）执行：

```javascript
// 启用Mock
window.__mockInterceptor.enable()

// 禁用Mock
window.__mockInterceptor.disable()

// 切换Mock状态
window.__mockInterceptor.toggle()

// 查看Mock状态
window.__mockInterceptor.getStats()
```

#### 方式3：通过LocalStorage

```javascript
// 启用
localStorage.setItem('mock_enabled', 'true')

// 禁用
localStorage.setItem('mock_enabled', 'false')

// 刷新页面生效
location.reload()
```

---

### 优先级规则

当多个Mock规则都匹配同一个请求时，按以下顺序选择：

1. **优先级数字大的优先** (`priority` 字段)
2. **同优先级时，按创建时间降序** (新创建的优先)

**示例**：

```javascript
// 规则1：优先级 0
{
  url_pattern: '/api/v2/devices',
  priority: 0
}

// 规则2：优先级 10（会优先匹配）
{
  url_pattern: '/api/v2/devices',
  priority: 10
}
```

---

### 查看Mock统计

每条Mock规则会记录：

- **命中次数** (`hit_count`)：被使用的次数
- **最后命中时间** (`last_hit_time`)：最后一次被使用的时间

点击"详情"按钮可以查看完整统计信息。

---

## 🎯 使用场景示例

### 场景1：演示设备管理功能

**目标**：展示设备列表、详情、编辑功能，无需真实数据。

**步骤**：

1. **创建设备列表Mock**：
```json
{
  "name": "演示-设备列表",
  "method": "GET",
  "url_pattern": "/api/v2/devices",
  "response_data": {
    "code": 200,
    "data": {
      "items": [
        {"id": 1, "name": "焊机A01", "status": "在线"},
        {"id": 2, "name": "焊机A02", "status": "离线"},
        {"id": 3, "name": "压力机B01", "status": "在线"}
      ],
      "total": 3
    }
  }
}
```

2. **创建设备详情Mock**：
```json
{
  "name": "演示-设备详情",
  "method": "GET",
  "url_pattern": "/api/v2/devices/*",
  "response_data": {
    "code": 200,
    "data": {
      "id": 1,
      "name": "焊机A01",
      "type": "焊机",
      "status": "在线",
      "location": "车间A",
      "lastMaintenance": "2025-10-15"
    }
  }
}
```

3. **创建编辑成功Mock**：
```json
{
  "name": "演示-编辑设备成功",
  "method": "PUT",
  "url_pattern": "/api/v2/devices/*",
  "response_data": {
    "code": 200,
    "message": "更新成功"
  }
}
```

4. **启用所有规则**，进行演示！

---

### 场景2：测试错误处理

**目标**：测试系统在各种错误情况下的表现。

**步骤**：

1. **创建404错误Mock**：
```json
{
  "name": "测试-404错误",
  "method": "GET",
  "url_pattern": "/api/v2/test-404",
  "response_code": 404,
  "response_data": {
    "code": 404,
    "message": "资源不存在"
  }
}
```

2. **创建500错误Mock**：
```json
{
  "name": "测试-服务器错误",
  "method": "POST",
  "url_pattern": "/api/v2/test-500",
  "response_code": 500,
  "response_data": {
    "code": 500,
    "message": "服务器内部错误"
  }
}
```

3. **创建网络延迟Mock**：
```json
{
  "name": "测试-慢速网络",
  "method": "GET",
  "url_pattern": "/api/v2/test-slow",
  "delay": 5000,  // 5秒延迟
  "response_data": {
    "code": 200,
    "message": "慢速响应"
  }
}
```

---

### 场景3：前端开发联调

**目标**：后端接口未就绪，前端独立开发。

**步骤**：

1. **根据API文档创建Mock规则**
2. **启用Mock**
3. **进行前端开发和测试**
4. **后端就绪后，禁用Mock切换到真实API**

---

## 🔧 高级用法

### 动态数据生成

虽然当前版本不支持动态数据，但可以通过以下方式模拟：

1. **创建多个Mock规则**，每个返回不同数据
2. **通过优先级和启用/禁用**切换不同场景
3. **定期手动更新响应数据**

### Mock规则模板

常用的响应格式模板：

**成功响应**：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 实际数据
  }
}
```

**分页响应**：
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

**错误响应**：
```json
{
  "code": 400,
  "message": "参数错误",
  "data": null
}
```

---

## 🐛 调试技巧

### 查看Mock拦截日志

在浏览器控制台（F12）中：

```javascript
// 查看Mock统计
window.__mockInterceptor.getStats()
/* 输出：
{
  enabled: true,
  rulesCount: 5,
  rules: [...]
}
*/

// 重新加载Mock规则
window.__mockInterceptor.reload()

// 查看所有规则
window.__mockInterceptor.getRules()
```

### 检查请求是否被Mock

在Network标签中，被Mock的请求会有特殊标记：

- 响应头中包含：`x-mock-match: true`
- Console中会输出：`[Mock拦截器] 命中规则: ...`

### 常见问题排查

**Q1: Mock规则不生效？**

检查清单：
- [ ] 规则是否启用？（`enabled = true`）
- [ ] Mock全局是否启用？（`window.__mockInterceptor.isEnabled()`）
- [ ] URL匹配模式是否正确？
- [ ] 是否有更高优先级的规则覆盖？

**Q2: 响应数据格式错误？**

- 确保响应数据是有效的JSON格式
- 使用在线JSON验证工具检查
- 在Mock管理页面会自动验证JSON格式

**Q3: 如何临时禁用所有Mock？**

```javascript
window.__mockInterceptor.disable()
location.reload()  // 刷新页面
```

---

## 📊 最佳实践

### 1. 命名规范

使用清晰的命名规则：

```
[场景]-[功能]-[说明]

示例：
- 演示-设备列表-3条数据
- 测试-登录失败-密码错误
- 开发-用户详情-完整信息
```

### 2. 组织规则

- **按功能模块分组**：使用优先级或命名前缀
- **及时清理**：删除不再使用的规则
- **文档化**：在描述字段写清楚用途

### 3. 数据真实性

- **模拟真实数据结构**：严格按照API文档
- **数据合理性**：时间、数字、状态等要符合逻辑
- **边界情况**：准备空数据、大量数据等场景

### 4. 版本管理

建议：
1. **导出Mock配置**（手动复制规则数据）
2. **保存到代码仓库**（如 `docs/mock-data-templates.json`）
3. **团队共享**：统一演示数据

---

## 🔒 权限说明

Mock数据管理功能需要以下权限：

| 操作 | 权限标识 | 说明 |
|------|----------|------|
| 查看列表 | `GET /api/v2/mock-data` | 自动分配给所有用户 |
| 新建规则 | `POST /api/v2/mock-data` | 需要分配 |
| 编辑规则 | `PUT /api/v2/mock-data/{id}` | 需要分配 |
| 删除规则 | `DELETE /api/v2/mock-data/{id}` | 需要分配 |
| 批量删除 | `POST /api/v2/mock-data/batch-delete` | 需要分配 |
| 切换状态 | `POST /api/v2/mock-data/{id}/toggle` | 需要分配 |

在"角色管理"中给相应角色分配权限。

---

## 📚 API参考

### 获取启用的Mock规则

```http
GET /api/v2/mock-data/active/list
```

**响应**：
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "method": "GET",
      "url_pattern": "/api/v2/devices",
      "response_data": {...},
      "response_code": 200,
      "delay": 0
    }
  ]
}
```

### 记录Mock命中

```http
POST /api/v2/mock-data/{id}/hit
```

---

## 🎉 总结

Mock数据管理功能让您能够：

✅ **快速搭建演示环境** - 无需真实数据即可展示系统功能
✅ **前后端独立开发** - 不阻塞前端开发进度
✅ **全面测试场景** - 模拟各种数据和错误情况
✅ **灵活控制** - 随时启用/禁用，优先级控制
✅ **统计分析** - 追踪Mock使用情况

开始使用Mock功能，让您的系统演示更加专业和流畅！ 🚀

---

**相关文档**：
- [按钮权限工作流程](./BUTTON_PERMISSION_WORKFLOW.md)
- [系统权限控制文档](../权限控制系统文档.md)
- [API文档](./api-v2/)

**反馈与建议**：
如有问题或建议，请联系开发团队或提交Issue。

