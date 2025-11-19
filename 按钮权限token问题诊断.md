# 按钮权限Token问题诊断

## 问题现象

用户hlzg_admin登录后，按钮显示但处于不可用状态。

## 日志分析

关键日志信息：

```
📊 accessApis数据状态: {isArray: true, length: 0, type: 'object'}
📋 所有API权限 (前10个): []
👤 用户信息: {username: 'hlzg_admin', isSuperUser: false, token: false, isLoggingOut: false}
```

**问题根源**：
1. `accessApis` 是空数组（length: 0）
2. `token: false` - Token不存在！

## 问题分析

### Token获取流程

```
用户登录
    ↓
后端返回token
    ↓
前端调用 setToken(token) 保存到 localStorage
    ↓
userStore.token getter 调用 getToken()
    ↓
从 localStorage 读取 'access_token'
    ↓
permissionStore.getAccessApis() 检查token
    ↓
如果token存在，调用 authApi.getUserApis()
    ↓
获取用户的API权限列表
```

### 问题定位

从代码中看到：

```typescript
// web/src/store/modules/permission/enhanced-permission-store.ts
const getAccessApis = async (forceRefresh: boolean = false) => {
  // 检查token
  if (!userStore.token) {
    console.log('无token，跳过API权限获取')  // ← 这里被触发了！
    return
  }
  // ...
}
```

**结论**：Token不存在，导致API权限获取被跳过。

## 可能的原因

### 1. 登录后Token没有保存

登录成功后，前端没有调用 `setToken()` 保存token到 `localStorage`。

### 2. Token的Key不匹配

- 代码中使用的key：`'access_token'`
- 实际保存的key可能不同

### 3. Token被清除

- 登录后token被某个逻辑清除
- 页面刷新时token丢失

### 4. 登录流程有问题

- 登录API返回的数据格式不正确
- Token字段名不匹配

## 诊断步骤

### 1. 检查localStorage中的Token

在浏览器控制台执行：

```javascript
// 查看所有localStorage数据
console.log('所有localStorage数据:', {...localStorage})

// 查看access_token
console.log('access_token:', localStorage.getItem('access_token'))

// 查看其他可能的token key
console.log('token:', localStorage.getItem('token'))
console.log('accessToken:', localStorage.getItem('accessToken'))
console.log('Authorization:', localStorage.getItem('Authorization'))
```

### 2. 检查登录响应

登录时，在浏览器Network标签中查看登录API的响应：

```
POST /api/v2/auth/login

Response:
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {...}
  }
}
```

确认：
- 响应中是否包含token
- Token字段名是什么（`access_token`, `token`, `accessToken`等）

### 3. 检查setToken调用

在登录页面组件中，查找登录成功后的处理逻辑：

```javascript
// 应该有类似这样的代码
const res = await authApi.login(loginForm)
if (res.data.access_token) {
  setToken(res.data.access_token)  // ← 检查这行是否存在
}
```

### 4. 检查Token是否被清除

在浏览器控制台执行：

```javascript
// 监听localStorage变化
window.addEventListener('storage', (e) => {
  if (e.key === 'access_token') {
    console.log('access_token变化:', {
      oldValue: e.oldValue,
      newValue: e.newValue,
      url: e.url
    })
  }
})
```

## 临时解决方案

### 方案1：手动设置Token

1. 使用admin账号登录
2. 在浏览器控制台执行：

```javascript
// 获取admin的token
console.log('admin token:', localStorage.getItem('access_token'))
```

3. 复制token
4. 使用hlzg_admin登录
5. 在浏览器控制台执行：

```javascript
// 手动设置token（使用hlzg_admin的实际token）
localStorage.setItem('access_token', 'YOUR_TOKEN_HERE')

// 刷新页面
location.reload()
```

### 方案2：使用admin账号

临时使用admin超级管理员账号，它不受此问题影响。

### 方案3：修改权限检查逻辑

临时禁用token检查（仅用于调试）：

```typescript
// web/src/store/modules/permission/enhanced-permission-store.ts
const getAccessApis = async (forceRefresh: boolean = false) => {
  // 临时注释掉token检查
  // if (!userStore.token) {
  //   console.log('无token，跳过API权限获取')
  //   return
  // }
  
  // 继续执行...
}
```

## 永久解决方案

### 1. 检查登录页面代码

找到登录页面组件（通常是 `web/src/views/login/index.vue`），确保登录成功后调用 `setToken()`：

```javascript
import { setToken } from '@/utils'

// 登录处理
const handleLogin = async () => {
  try {
    const res = await authApi.login(loginForm)
    
    // 保存token
    if (res.data.access_token) {
      setToken(res.data.access_token)
    }
    
    // 获取用户信息
    await userStore.getUserInfo()
    
    // 跳转
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
  }
}
```

### 2. 统一Token字段名

确保前后端使用相同的token字段名：

**后端**（`app/api/v2/auth.py`）：
```python
return {
    "access_token": token,
    "token_type": "bearer"
}
```

**前端**（`web/src/utils/auth/token.js`）：
```javascript
const TOKEN_CODE = 'access_token'  // 与后端一致
```

### 3. 添加Token持久化

确保token在页面刷新后仍然存在：

```javascript
// web/src/utils/auth/token.js
export function setToken(token) {
  if (!token) {
    console.warn('尝试设置空token')
    return
  }
  
  console.log('存储token到localStorage:', token.substring(0, 20) + '...')
  localStorage.setItem(TOKEN_CODE, token)
  
  // 验证保存成功
  const saved = localStorage.getItem(TOKEN_CODE)
  if (saved !== token) {
    console.error('Token保存失败！')
  } else {
    console.log('Token保存成功')
  }
}
```

## 验证步骤

### 1. 确认Token已保存

登录后，在浏览器控制台执行：

```javascript
console.log('Token:', localStorage.getItem('access_token'))
```

应该看到一个JWT token字符串。

### 2. 确认API权限已获取

在浏览器控制台执行：

```javascript
const store = useEnhancedPermissionStore()
console.log('API权限数量:', store.accessApis.length)
console.log('前10个权限:', store.accessApis.slice(0, 10))
```

应该看到127个权限。

### 3. 确认按钮可用

刷新页面，检查按钮是否可以点击。

## 相关文件

- Token管理：`web/src/utils/auth/token.js`
- 用户Store：`web/src/store/modules/user/index.ts`
- 权限Store：`web/src/store/modules/permission/enhanced-permission-store.ts`
- 登录页面：`web/src/views/login/index.vue`（需要查找）

## 修复日期

2025-11-19

## 修复状态

🔍 **诊断中** - 需要检查登录流程和token保存逻辑
