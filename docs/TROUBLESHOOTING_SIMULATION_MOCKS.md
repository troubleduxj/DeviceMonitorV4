# 模拟设备Mock规则故障排查指南

## 🔍 问题：前端Mock管理页面看不到新增的模拟设备规则

---

## 📋 排查步骤

### 步骤1：验证数据库中是否成功插入

#### 在pgAdmin中执行以下查询：

```sql
-- 查询所有模拟设备Mock规则
SELECT 
    id,
    name,
    method,
    url_pattern,
    enabled,
    priority,
    description,
    created_at
FROM t_sys_mock_data
WHERE description LIKE '%模拟设备%'
ORDER BY id DESC;
```

**预期结果：**
- 应该返回 **5行** 记录
- 规则名称包含："模拟设备分类-设备列表"、"模拟设备-详情信息"等

**如果返回0行：**
- ❌ 数据未插入成功
- 解决：重新在pgAdmin中执行SQL文件

**如果返回5行：**
- ✅ 数据插入成功，继续下一步

---

### 步骤2：检查后端API是否返回数据

#### 在浏览器控制台执行：

```javascript
// 检查API响应
fetch('/api/v2/mock-data', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'token': localStorage.getItem('access_token')
  }
})
.then(r => r.json())
.then(data => {
  console.log('Total mock rules:', data.data?.length || 0);
  console.log('Mock rules:', data.data);
  
  // 筛选模拟设备规则
  const simRules = data.data?.filter(r => r.description?.includes('模拟设备')) || [];
  console.log('Simulation device rules:', simRules.length);
  simRules.forEach(r => console.log(`  - ${r.name}`));
});
```

**预期结果：**
```
Total mock rules: 20
Simulation device rules: 5
  - 模拟设备分类-设备列表
  - 模拟设备-详情信息
  - 模拟设备-实时数据
  - 模拟设备-历史数据
  - 模拟设备-统计数据
```

**如果看不到模拟设备规则：**
- 问题在后端API
- 继续步骤3

**如果能看到：**
- 问题在前端显示
- 继续步骤4

---

### 步骤3：检查后端代码

#### 查看Mock Data API：

```bash
# 检查后端API文件
app/api/v2/mock_data.py
```

#### 检查后端日志：

查看后端控制台，看是否有错误信息。

---

### 步骤4：检查前端页面

#### 1. 刷新浏览器（硬刷新）

按 `Ctrl + Shift + R` 清除缓存并刷新

#### 2. 检查前端过滤条件

打开Mock管理页面，检查：
- [ ] 搜索框是否为空？
- [ ] 是否有启用状态筛选？
- [ ] 页码是否在第1页？

#### 3. 清除浏览器本地存储

在控制台执行：
```javascript
// 清除可能的缓存
sessionStorage.clear();
// 然后刷新页面
location.reload();
```

---

### 步骤5：查看前端Mock管理页面代码

检查文件：`web/src/views/advanced-settings/mock-data/index.vue`

#### 查看loadMockRules方法：

```javascript
const loadMockRules = async () => {
  loading.value = true
  try {
    const response = await requestV2.get('/mock-data')
    console.log('Mock规则响应:', response)
    
    if (response && response.data) {
      mockRules.value = Array.isArray(response.data) 
        ? response.data 
        : response.data.items || []
      
      console.log('加载的Mock规则数量:', mockRules.value.length)
      console.log('Mock规则列表:', mockRules.value)
    }
  } catch (error) {
    console.error('加载Mock规则失败:', error)
  } finally {
    loading.value = false
  }
}
```

---

## 🛠️ 常见问题及解决方案

### 问题1：数据库中有数据，但API返回空

**可能原因：**
- 后端查询条件过滤掉了数据
- 数据库连接问题

**解决方案：**
1. 检查后端API的查询条件
2. 检查数据库连接
3. 重启后端服务

---

### 问题2：API返回数据，但前端不显示

**可能原因：**
- 前端数据绑定问题
- 组件渲染问题
- 浏览器缓存

**解决方案：**

#### A. 在Mock管理页面控制台检查：

```javascript
// 检查Vue组件的数据
const vueApp = document.querySelector('#app').__vue__;
console.log('Mock rules in Vue:', vueApp.$refs?.mockDataPage?.mockRules);
```

#### B. 修改前端代码添加调试：

在 `web/src/views/advanced-settings/mock-data/index.vue` 中：

```javascript
watch(
  () => mockRules.value,
  (newVal) => {
    console.log('🔍 mockRules changed:', newVal.length, newVal);
  },
  { immediate: true, deep: true }
);
```

---

### 问题3：SQL执行报错

**错误示例：**
```
ERROR: duplicate key value violates unique constraint
```

**原因：** Mock规则已存在

**解决方案：**

#### 删除已存在的规则后重新插入：

```sql
-- 删除所有模拟设备Mock规则
DELETE FROM t_sys_mock_data 
WHERE description LIKE '%模拟设备%';

-- 然后重新执行插入SQL
```

---

## 🔧 快速修复脚本

### 脚本1：重新插入数据（强制覆盖）

创建文件：`database/migrations/reset_simulation_mocks.sql`

```sql
-- 删除现有的模拟设备Mock规则
DELETE FROM t_sys_mock_data 
WHERE description LIKE '%模拟设备%';

-- 重新执行插入
\i database/migrations/insert_simulation_device_mocks.sql
```

在pgAdmin中执行此文件。

---

### 脚本2：检查完整性

在pgAdmin中执行 `scripts/check_simulation_mocks.sql`：

```sql
-- 这个文件已经创建，包含完整的检查查询
```

---

## 📊 调试信息收集

如果问题仍未解决，请收集以下信息：

### 1. 数据库查询结果

```sql
SELECT COUNT(*) FROM t_sys_mock_data WHERE description LIKE '%模拟设备%';
```

输出：____

---

### 2. API响应

在浏览器控制台执行：
```javascript
fetch('/api/v2/mock-data', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'token': localStorage.getItem('access_token')
  }
})
.then(r => r.json())
.then(data => console.log('API Response:', JSON.stringify(data, null, 2)));
```

复制输出：____

---

### 3. 前端日志

查看文件：`logs/frontend-log.md` 最后50行

---

### 4. 浏览器控制台错误

按 F12 打开开发者工具，复制控制台中的所有错误信息。

---

## ✅ 验证成功的标志

完成修复后，应该看到：

### 在Mock管理页面：
- ✅ 显示5条新的Mock规则
- ✅ 规则名称包含"模拟设备"字样
- ✅ 所有规则状态为"未启用"（灰色开关）

### 规则列表：
```
1. 模拟设备分类-设备列表
2. 模拟设备-详情信息
3. 模拟设备-实时数据
4. 模拟设备-历史数据
5. 模拟设备-统计数据
```

---

## 📞 仍需帮助？

如果以上步骤都完成了但问题仍存在，请提供：

1. ✅ 数据库查询结果（步骤1的截图）
2. ✅ API响应内容（步骤2的控制台输出）
3. ✅ 前端控制台错误信息
4. ✅ Mock管理页面的截图

---

**最后更新：** 2025-10-30  
**版本：** 1.0.0

