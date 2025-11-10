# Mock数据展示验证指南

> **更新时间**: 2025-11-05 20:18  
> **目的**: 验证AI监测页面Mock数据正常展示  
> **适用页面**: 趋势预测、健康评分  

---

## ✅ 已完成的修复

### 1. TrendChart组件修复 ✅

**问题**: 组件使用硬编码数据，忽略传入的props.data

**修复**: 
```javascript
// 修改chartOption，使用传入的data
const chartData = props.data && props.data.length > 0 ? props.data : []
const healthyData = chartData.map(item => item.healthy || 0)
const warningData = chartData.map(item => item.warning || 0)
const errorData = chartData.map(item => item.error || 0)
```

**结果**: ✅ 组件现在会正确显示传入的数据

---

### 2. Mock规则数据格式 ✅

**已添加Mock规则**:
```
GET /api/v2/ai-monitor/health-trend
```

**返回数据格式**:
```json
{
  "success": true,
  "code": 200,
  "data": [
    {"time": "2024-01-01", "healthy": 85, "warning": 12, "error": 3},
    {"time": "2024-01-02", "healthy": 83, "warning": 14, "error": 3},
    ...
  ]
}
```

**结果**: ✅ 数据格式匹配组件期望

---

### 3. 页面数据加载 ✅

**修复refreshPrediction函数**:
```javascript
// 并行加载健康趋势数据
fetch('/api/v2/ai-monitor/health-trend').then(r => r.json())

// 处理响应
if (healthTrendResponse.status === 'fulfilled' && healthTrendResponse.value?.data) {
  healthTrendData.value = healthTrendResponse.value.data || []
}
```

**结果**: ✅ 页面会从API获取数据

---

## 🚀 验证步骤（5分钟）

### 步骤1: 启用Mock拦截器（必须）

打开浏览器，按F12打开控制台，输入：

```javascript
// 1. 启用Mock
window.__mockInterceptor.enable()

// 2. 重新加载Mock规则
await window.__mockInterceptor.reload()

// 3. 验证加载（应该看到6个AI相关规则）
window.__mockInterceptor.getStats()
// 输出示例：
// {
//   enabled: true,
//   rulesCount: 6,
//   rules: [...]
// }

// 4. 刷新页面使Mock生效
location.reload()
```

---

### 步骤2: 访问趋势预测页面

1. 登录系统（如果需要）
2. 进入：**AI监测** > **趋势预测**
3. 页面会自动加载数据（onMounted时调用refreshPrediction）

---

### 步骤3: 手动刷新数据

1. 点击页面右上角的 **刷新数据** 按钮
2. 打开浏览器开发者工具 (F12)
3. 切换到 **Console** 标签
4. 查看日志输出

**预期看到的日志**:
```
🔄 刷新趋势预测数据...
[Mock拦截器] 拦截请求: { method: 'GET', url: '/api/v2/ai-monitor/health-trend' }
[Mock拦截器] 命中规则: { id: 2, name: 'AI预测-健康趋势数据' }
✅ 健康趋势数据加载成功: 7
✅ 风险评估数据加载成功: 3
✅ 预测报告数据加载成功
✅ 所有数据加载完成
```

---

### 步骤4: 验证图表数据

切换到 **Network** 标签:

**查找请求**:
```
GET /api/v2/ai-monitor/health-trend
```

**检查响应**:
- Status: 200 OK
- Response Headers: `x-mock-match: true` ← Mock拦截标识
- Response Data: 包含7天健康趋势数据

**预期响应**:
```json
{
  "success": true,
  "code": 200,
  "message": "获取健康趋势成功",
  "data": [
    {"time": "2024-01-01", "healthy": 85, "warning": 12, "error": 3},
    {"time": "2024-01-02", "healthy": 83, "warning": 14, "error": 3},
    ...
  ]
}
```

---

### 步骤5: 查看图表展示

在页面上找到 **"设备健康趋势预测"** 卡片

**应该看到**:
- ✅ X轴：7个日期（2024-01-01 ~ 2024-01-07）
- ✅ Y轴：设备数量
- ✅ 3条折线：
  - 绿色线（健康）：85 → 75 (下降趋势)
  - 黄色线（预警）：12 → 19 (上升趋势)
  - 红色线（异常）：3 → 6 (上升趋势)
- ✅ 图表有数据，不是空白

---

## 🐛 如果图表仍为空

### 排查步骤

#### 1. 检查Mock是否启用

```javascript
// 控制台检查
window.__mockInterceptor.isEnabled()
// 应该返回: true
```

如果返回false，重新启用：
```javascript
window.__mockInterceptor.enable()
location.reload()
```

---

#### 2. 检查Mock规则是否加载

```javascript
window.__mockInterceptor.getStats()
```

**应该看到**:
```javascript
{
  enabled: true,
  rulesCount: 6,  // ← 至少6个规则
  rules: [
    { url_pattern: '/api/v2/ai-monitor/health-trend', ... },
    ...
  ]
}
```

如果rulesCount为0，重新加载：
```javascript
await window.__mockInterceptor.reload()
location.reload()
```

---

#### 3. 检查Network请求

F12 > Network标签:

**查找**:
```
GET /api/v2/ai-monitor/health-trend
```

**如果找不到请求**:
- 说明页面没有发送请求
- 检查refreshPrediction函数是否被调用
- 查看Console是否有错误

**如果找到请求但状态404**:
- 说明Mock未拦截
- 重新启用Mock并reload

**如果找到请求且状态200**:
- 查看响应头是否有 `x-mock-match: true`
- 查看响应数据是否正确
- 检查data数组是否有7个元素

---

#### 4. 检查数据赋值

Console中输入：
```javascript
// 查看healthTrendData的值
// （需要在Vue DevTools中查看，或在页面中添加调试）
```

或在refreshPrediction函数添加console.log后重新刷新。

---

#### 5. 检查TrendChart组件

如果数据已正确加载但图表不显示：

**可能原因**:
- 组件的data watcher可能需要触发
- 需要nextTick后图表才更新

**解决**:
```javascript
// 在refreshPrediction的最后确保有：
await nextTick()
updateCharts()  // 如果有这个函数
```

---

## 💡 调试技巧

### 临时添加调试日志

在`web/src/views/ai-monitor/trend-prediction/index.vue`的refreshPrediction函数中：

```javascript
// 在处理健康趋势数据后添加：
if (healthTrendResponse.status === 'fulfilled' && healthTrendResponse.value?.data) {
  healthTrendData.value = healthTrendResponse.value.data || []
  console.log('✅ 健康趋势数据加载成功:', healthTrendData.value.length)
  console.log('   数据内容:', JSON.stringify(healthTrendData.value, null, 2))  // ← 添加这行
}
```

刷新页面后查看完整的数据内容。

---

### 检查组件接收的数据

在TrendChart.vue组件中添加watch：

```javascript
import { watch } from 'vue'

watch(() => props.data, (newData) => {
  console.log('TrendChart收到新数据:', newData)
  console.log('数据长度:', newData?.length)
}, { immediate: true, deep: true })
```

---

## 🎯 预期最终效果

启用Mock后，访问趋势预测页面，应该看到：

### 设备健康趋势预测卡片

**图表展示**:
- ✅ X轴: 2024-01-01, 01-02, ..., 01-07 (7个日期)
- ✅ 绿色折线（健康）: 从85降至75
- ✅ 黄色折线（预警）: 从12升至19
- ✅ 红色折线（异常）: 从3升至6
- ✅ 图表平滑流畅
- ✅ Tooltip正常显示

**数据来源**:
- ✅ Mock管理系统（/api/v2/ai-monitor/health-trend规则）
- ✅ 响应头包含: x-mock-match: true
- ✅ 可在Mock管理页面编辑此规则的数据

---

## 📝 完整验证清单

### Mock模式测试

- [ ] 启用Mock拦截器
- [ ] 重新加载Mock规则
- [ ] 刷新页面
- [ ] 访问趋势预测页面
- [ ] 查看Network是否拦截请求
- [ ] 查看响应头x-mock-match
- [ ] 查看Console日志
- [ ] **查看图表是否显示7天数据** ← 重点
- [ ] 3条折线是否正常显示

### 真实API模式测试

- [ ] 禁用Mock拦截器
- [ ] 确保后端运行
- [ ] 刷新页面
- [ ] 点击刷新数据
- [ ] 查看是否调用真实API
- [ ] 查看响应是否来自后端

---

## 🔧 快速修复脚本

如果仍然有问题，运行此脚本：

```javascript
// 浏览器控制台

// 完整的Mock初始化流程
async function initMock() {
  console.log('=== 初始化Mock系统 ===')
  
  // 1. 清除旧状态
  localStorage.removeItem('mock_enabled')
  
  // 2. 启用Mock
  window.__mockInterceptor.enable()
  console.log('✓ Mock已启用')
  
  // 3. 加载规则
  await window.__mockInterceptor.reload()
  console.log('✓ Mock规则已加载')
  
  // 4. 验证
  const stats = window.__mockInterceptor.getStats()
  console.log('✓ Mock状态:', stats)
  
  if (stats.rulesCount < 6) {
    console.error('✗ Mock规则数量不足，预期6个，实际' + stats.rulesCount)
    return false
  }
  
  // 5. 刷新页面
  console.log('=== 准备刷新页面 ===')
  console.log('Mock规则数:', stats.rulesCount)
  console.log('3秒后自动刷新...')
  
  setTimeout(() => location.reload(), 3000)
  return true
}

// 执行初始化
await initMock()
```

---

## 🎊 完成状态

**修复内容**:
- ✅ TrendChart组件使用props.data
- ✅ Mock规则数据格式正确
- ✅ 页面正确调用API
- ✅ 数据处理逻辑完善

**Mock规则**:
- ✅ 6个AI相关规则已插入
- ✅ 健康趋势数据规则已就绪
- ✅ 返回7天完整数据

**下一步**:
- 按照上述步骤验证
- 如有问题，查看调试技巧
- 确认图表正常显示

---

**现在启用Mock并刷新页面，"设备健康趋势预测"卡片应该能正常展示7天的趋势数据了！** 🚀

