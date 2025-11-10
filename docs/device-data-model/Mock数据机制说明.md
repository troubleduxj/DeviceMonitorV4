# Mock数据机制说明 - AI监测模块

> **更新时间**: 2025-11-05 19:10  
> **状态**: ✅ 12个AI预测Mock规则已添加  

---

## ✅ 问题回答

### AI监测模块的Mock数据来源？

**答案：是的！** AI监测模块下的所有页面的Mock数据都来自**Mock数据管理页面**新增的规则。

---

## 🔧 Mock机制工作原理

### 1. Mock规则存储

**数据库表**: `t_sys_mock_data`

**规则内容**:
```sql
SELECT id, name, method, url_pattern, enabled, priority
FROM t_sys_mock_data
WHERE url_pattern LIKE '%ai%prediction%';
```

**刚刚添加的12条规则**:
- `POST /api/v2/ai-monitor/predictions/batch` - 批量创建预测
- `GET /api/v2/ai-monitor/predictions/history` - 查询历史
- `GET /api/v2/ai-monitor/predictions` - 获取列表
- ... 共12条

---

### 2. 前端加载Mock规则

**加载流程**:

```javascript
// 1. 前端启动时初始化Mock拦截器
// web/src/main.js 或 app启动时
import { initMockInterceptor } from '@/utils/mock-interceptor'

await initMockInterceptor()  // 从服务器加载Mock规则
```

**加载接口**: `GET /api/v2/mock-data/active/list`

**返回数据**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "method": "POST",
      "url_pattern": "/api/v2/ai-monitor/predictions/batch",
      "response_data": {...},
      "response_code": 201,
      "delay": 500
    },
    // ... 更多规则
  ]
}
```

---

### 3. 请求拦截匹配

**拦截流程**:

```javascript
// web/src/utils/http/v2-interceptors.js

// 1. 请求发起
axios.post('/api/v2/ai-monitor/predictions/batch', data)

// 2. 请求拦截器检查
mockRequestInterceptor(config) {
  if (mockEnabled) {
    // 3. 查找匹配的Mock规则
    const rule = findMatchingRule('POST', '/api/v2/ai-monitor/predictions/batch')
    
    if (rule) {
      // 4. 标记为Mock请求
      config._isMockRequest = true
      config._mockRule = rule
    }
  }
}

// 5. 如果是Mock请求，返回Mock数据
// 否则，发送真实API请求
```

---

### 4. 规则匹配逻辑

**支持的URL模式**:

1. **精确匹配**:
   ```
   /api/v2/ai-monitor/predictions/batch
   ```

2. **通配符匹配**:
   ```
   /api/v2/ai-monitor/predictions/*  ← 匹配任意ID
   /api/v2/ai-monitor/**  ← 匹配所有子路径
   ```

3. **正则表达式**:
   ```
   /api/v2/devices/100[1-5]$  ← 匹配1001-1005
   ```

---

## 📝 如何使用Mock功能

### 方式1：在系统中管理（推荐）⭐

#### 步骤1: 访问Mock数据管理页面

1. 登录系统：http://localhost:3000
2. 进入：**系统管理** > **Mock数据管理**（或 **高级设置** > **Mock数据管理**）

#### 步骤2: 查看AI预测Mock规则

- 搜索框输入："AI预测" 或 "趋势预测"
- 应该看到**12条Mock规则**
- 状态栏显示：[ON]（已启用）

#### 步骤3: 启用Mock功能

**方式A - 在浏览器控制台**:
```javascript
// 打开浏览器开发者工具 (F12)
// 在Console中输入：

// 启用Mock
window.__mockInterceptor.enable()

// 重新加载Mock规则
await window.__mockInterceptor.reload()

// 查看状态
window.__mockInterceptor.getStats()
```

**方式B - 在系统设置页面**（如果有Mock开关）

#### 步骤4: 测试Mock数据

1. 进入：**AI监测** > **趋势预测**
2. 点击：**刷新数据** 按钮
3. 打开：浏览器开发者工具 (F12) > Network标签
4. 查看：请求被Mock拦截，响应头包含 `x-mock-match: true`

---

### 方式2：浏览器控制台快速启用

**打开任意页面，按F12打开控制台，输入**:

```javascript
// 1. 启用Mock
window.__mockInterceptor.enable()

// 2. 加载规则
await window.__mockInterceptor.reload()

// 3. 查看规则
window.__mockInterceptor.getStats()
// 输出: { enabled: true, rulesCount: 12, rules: [...] }

// 4. 刷新页面或重新发起请求
location.reload()
```

---

## 🎯 Mock数据展示效果

### 启用Mock后的表现

#### AI趋势预测页面

**点击"刷新数据"按钮**:

```javascript
// 请求被拦截
POST /api/v2/ai-monitor/predictions/batch

// 返回Mock数据
{
  "success": true,
  "code": 201,
  "message": "批量预测任务创建完成，成功 3 个",
  "data": {
    "predictions": [
      {
        "id": 1,
        "prediction_name": "WLD-001-temperature-预测-24h",
        "device_code": "WLD-001",
        "status": "pending",
        ...
      }
    ]
  }
}

// 页面展示：
// ✓ 预测精度: 92.5%
// ✓ 预测设备: 3
// ✓ 图表数据更新
```

---

### Mock vs 真实API对比

| 特性 | Mock模式 | 真实API模式 |
|------|---------|------------|
| **数据来源** | Mock数据管理页面 | 后端数据库 |
| **响应速度** | 配置的延迟（200-1500ms）| 实际处理时间 |
| **数据内容** | 预配置的Mock数据 | 真实的数据库数据 |
| **后端依赖** | 不需要后端运行 | 需要后端运行 |
| **适用场景** | 演示、前端开发、测试 | 生产环境、真实业务 |

---

## 📋 已添加的Mock规则详情

### 预测任务管理Mock（6个）

**1. 批量创建预测任务**
```
接口: POST /api/v2/ai-monitor/predictions/batch
延迟: 500ms
响应: 201 Created
数据: 包含3个预测任务
```

**2. 查询设备预测历史**
```
接口: GET /api/v2/ai-monitor/predictions/history
延迟: 300ms
响应: 200 OK
数据: 包含5条历史记录
```

**3. 获取预测列表**
```
接口: GET /api/v2/ai-monitor/predictions
延迟: 200ms
响应: 200 OK
数据: 包含15条预测记录（分页）
```

**4. 获取预测详情**
```
接口: GET /api/v2/ai-monitor/predictions/*
延迟: 200ms
响应: 200 OK
数据: 包含完整预测结果（24个预测点）
```

**5-6**: 创建单个任务、删除任务等

---

### 趋势预测执行Mock（4个）

**7. 执行趋势预测**
```
接口: POST /api/v2/ai/trend-prediction/predict
延迟: 800ms
响应: 200 OK
数据: 包含5步预测结果 + 趋势分析
```

**8. 批量趋势预测**
```
接口: POST /api/v2/ai/trend-prediction/predict/batch
延迟: 1200ms
响应: 200 OK
数据: 包含3个设备的预测结果
```

**9. 预测方法对比**
```
接口: POST /api/v2/ai/trend-prediction/compare
延迟: 1500ms
响应: 200 OK
数据: ARIMA、MA、EMA方法对比结果
```

**10. 获取预测方法**
```
接口: GET /api/v2/ai/trend-prediction/methods
延迟: 100ms
响应: 200 OK
数据: 4种预测方法说明
```

---

### 其他功能Mock（2个）

**11. 导出预测报告**
```
接口: GET /api/v2/ai-monitor/predictions/*/export
延迟: 1000ms
响应: 200 OK
数据: 文件下载信息
```

**12. 批量删除预测**
```
接口: POST /api/v2/ai-monitor/predictions/batch-delete
延迟: 400ms
响应: 200 OK
数据: 删除操作结果
```

---

## 🎨 Mock数据特点

### 真实感设计

**预测数据**:
- ✅ 24小时预测点（每小时一个）
- ✅ 合理的数值范围（75-95）
- ✅ 置信区间（±3.5）
- ✅ 置信度（0.85-0.95）

**趋势分析**:
- ✅ 上升/下降/平稳趋势
- ✅ MAE、RMSE、MAPE评估指标
- ✅ 不同方法性能对比

**元数据**:
- ✅ 设备代码和名称
- ✅ 指标名称
- ✅ 预测方法
- ✅ 数据周期

---

## 🔄 Mock功能切换

### 启用Mock（演示模式）

**适用场景**:
- 📺 系统演示
- 💻 前端开发
- 🧪 UI测试
- ⚡ 性能测试

**操作**:
```javascript
// 浏览器控制台
window.__mockInterceptor.enable()
await window.__mockInterceptor.reload()
location.reload()
```

**效果**:
- ✅ 所有AI预测API请求被拦截
- ✅ 返回预配置的Mock数据
- ✅ 不依赖后端服务
- ✅ 固定的响应延迟

---

### 禁用Mock（真实数据模式）

**适用场景**:
- 🎯 真实业务使用
- 🔍 功能测试
- 📊 数据验证
- 🚀 生产环境

**操作**:
```javascript
// 浏览器控制台
window.__mockInterceptor.disable()
location.reload()
```

**效果**:
- ✅ 请求发送到真实后端API
- ✅ 返回数据库中的真实数据
- ✅ 支持完整的CRUD操作
- ✅ 真实的业务逻辑

---

## 📊 验证Mock功能

### 快速验证步骤

#### 1. 查看Mock规则（1分钟）

访问：**系统管理** > **Mock数据管理**

**应该看到**:
- ✅ 12条AI预测相关Mock规则
- ✅ 状态：已启用
- ✅ 优先级：100
- ✅ 响应数据：完整的JSON结构

---

#### 2. 启用Mock拦截（30秒）

打开浏览器控制台 (F12)：

```javascript
// 启用Mock
window.__mockInterceptor.enable()

// 加载规则
await window.__mockInterceptor.reload()

// 查看状态（应该显示12条规则）
window.__mockInterceptor.getStats()
```

**预期输出**:
```javascript
{
  enabled: true,
  rulesCount: 12,  // ← 12条AI预测规则
  rules: [
    { id: 1, method: "POST", url_pattern: "/api/v2/ai-monitor/predictions/batch", ... },
    { id: 2, method: "GET", url_pattern: "/api/v2/ai-monitor/predictions/history", ... },
    // ... 更多规则
  ]
}
```

---

#### 3. 测试Mock拦截（2分钟）

访问：**AI监测** > **趋势预测**

**操作**:
1. 打开Network标签 (F12)
2. 点击页面上的 **刷新数据** 按钮
3. 查看Network请求

**预期看到**:
```
POST /api/v2/ai-monitor/predictions/batch
Status: 201 (from disk cache 或 304)
Response Headers:
  x-mock-match: true  ← 说明被Mock拦截了！
  
Response Data:
{
  "success": true,
  "code": 201,
  "message": "批量预测任务创建完成，成功 3 个",
  "data": { ... }  ← Mock数据
}
```

**Console输出**:
```
[Mock拦截器] URL匹配成功: { url: '/api/v2/ai-monitor/predictions/batch', ... }
[Mock拦截器] 拦截请求: { method: 'POST', url: '/api/v2/ai-monitor/predictions/batch' }
[Mock拦截器] 命中规则: { id: 1, method: 'POST', ... }
```

---

## 🎯 Mock vs 真实数据对比

### 当前系统状态

**数据库中的真实数据**: ✅ 有（8条预测记录）
**Mock规则**: ✅ 有（12条规则）

### 两种模式的数据来源

#### Mock模式启用时 🎭

```
前端请求 → Mock拦截器 → 匹配规则 → 返回Mock数据
             ↑
             来自 t_sys_mock_data 表
```

**数据特点**:
- ✅ 预配置的示例数据
- ✅ 固定的响应延迟
- ✅ 不调用后端API
- ✅ 适合演示和开发

---

#### Mock模式禁用时 💼

```
前端请求 → 真实API → 数据库查询 → 返回真实数据
                        ↑
                        t_ai_predictions 表
```

**数据特点**:
- ✅ 实时的数据库数据
- ✅ 真实的业务逻辑
- ✅ 支持CRUD操作
- ✅ 适合生产使用

---

## 🔍 如何区分当前使用的是Mock还是真实数据

### 方法1：查看响应头

**Mock数据**:
```
响应头包含: x-mock-match: true
```

**真实数据**:
```
响应头不包含 x-mock-match
```

---

### 方法2：查看Console日志

**Mock模式**:
```
[Mock拦截器] 拦截请求: ...
[Mock拦截器] 命中规则: ...
```

**真实模式**:
```
[API v2 Request] POST /api/v2/ai-monitor/predictions/batch
[API v2 Response] POST /api/v2/ai-monitor/predictions/batch - 201
```

---

### 方法3：查看数据特征

**Mock数据特征**:
- 固定的设备ID（WLD-001, WLD-002, WLD-003）
- 固定的数值范围
- 完全一致的响应延迟

**真实数据特征**:
- 实际创建的设备ID
- 动态生成的预测值
- 变化的响应时间

---

## 💡 最佳实践

### 什么时候用Mock模式？

**✅ 推荐使用Mock**:
1. 📺 **系统演示** - 给客户展示功能
2. 💻 **前端开发** - 后端未完成时独立开发
3. 🎨 **UI调整** - 快速迭代界面设计
4. ⚡ **性能测试** - 模拟不同延迟
5. 🐛 **错误测试** - 模拟各种错误场景

**❌ 不推荐使用Mock**:
1. 🎯 **真实业务** - 实际使用系统
2. 🧪 **功能测试** - 验证业务逻辑
3. 📊 **数据分析** - 需要真实数据
4. 🚀 **生产环境** - 必须使用真实API

---

### 如何管理Mock规则？

#### 在Mock数据管理页面

**查看规则**:
- 列表显示所有规则
- 支持搜索和筛选
- 显示命中次数统计

**编辑规则**:
- 修改响应数据
- 调整延迟时间
- 更改优先级
- 启用/禁用规则

**创建新规则**:
- 点击"新建"按钮
- 填写接口信息
- 配置响应数据
- 保存即生效

---

## 🎊 总结

### AI监测模块Mock数据机制

**回答你的问题**：

✅ **是的！** AI监测模块下的各页面（趋势预测、异常检测、健康评分等）的Mock数据**完全来自Mock数据管理页面新增的规则**。

**工作流程**：

1. ✅ Mock规则存储在 `t_sys_mock_data` 表
2. ✅ 前端启动时从 `/api/v2/mock-data/active/list` 加载规则
3. ✅ 请求拦截器匹配URL和Method
4. ✅ 匹配成功则返回Mock数据，否则发送真实请求
5. ✅ 可以在Mock数据管理页面实时管理规则

**当前状态**：

- ✅ 已添加12条AI预测Mock规则
- ✅ 默认全部启用（enabled=true）
- ✅ 高优先级（priority=100）
- ✅ 包含完整的响应数据结构
- ✅ 立即可用！

**使用方式**：

```javascript
// 在浏览器控制台启用Mock
window.__mockInterceptor.enable()
await window.__mockInterceptor.reload()

// 刷新页面，Mock数据即刻生效！
location.reload()
```

---

**现在访问Mock数据管理页面，搜索"AI预测"，你就能看到这12条新增的Mock规则了！** 🚀


