# Shared 层 API 问题修复记录

> 记录迁移过程中发现的问题及解决方案

---

## 🐛 问题 1: 设备类型 API 404 错误

### 错误现象

```
Failed to load resource: the server responded with a status of 404 (Not Found)
:3000/api/v2/device-types:1
```

### 错误原因

**错误的 API 路径映射**:
- Shared 层使用: `/device-types`
- 完整路径: `/api/v2/device-types`
- 实际后端路径: `/api/v2/devices/types`

### 解决方案

**修改文件**: `packages/shared/api/device.ts`

```diff
  async getDeviceTypes(params?: PaginationParams) {
-   return this.client.get<Paginated<DeviceType>>('/device-types', params);
+   return this.client.get<Paginated<DeviceType>>('/devices/types', params);
  }

  async getDeviceType(typeCode: string) {
-   return this.client.get<DeviceType>(`/device-types/${typeCode}`);
+   return this.client.get<DeviceType>(`/devices/types/${typeCode}`);
  }

  async createDeviceType(data: Omit<DeviceType, 'id'>) {
-   return this.client.post<DeviceType>('/device-types', data);
+   return this.client.post<DeviceType>('/devices/types', data);
  }

  async updateDeviceType(typeCode: string, data: Partial<DeviceType>) {
-   return this.client.put<DeviceType>(`/device-types/${typeCode}`, data);
+   return this.client.put<DeviceType>(`/devices/types/${typeCode}`, data);
  }

  async deleteDeviceType(typeCode: string) {
-   return this.client.delete(`/device-types/${typeCode}`);
+   return this.client.delete(`/devices/types/${typeCode}`);
  }
```

### 验证方法

```javascript
// 打开浏览器控制台，检查网络请求
// 应该看到: GET /api/v2/devices/types?page=1&page_size=20
// 状态码: 200 OK
```

---

## 🐛 问题 2: 未知的响应数据格式

### 错误现象

```
未知的响应数据格式: Object
```

控制台显示响应对象，但页面无法正确解析。

### 错误原因

**丢失分页元数据**:

原始后端响应格式：
```json
{
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "page_size": 20
  },
  "links": {...}
}
```

Shared 适配器错误地只返回了 `data` 部分：
```javascript
// ❌ 错误做法
list: async (params = {}) => {
  const result = await sharedApi.alarm.getAlarms(params);
  return { data: result.data };  // 丢失了 meta 和 links
},
```

前端代码依赖 `meta` 字段获取分页信息：
```javascript
pagination.itemCount = response.meta?.total || response.data.length
```

### 解决方案

**修改所有列表 API 适配器，保持完整响应**:

#### 1. `web/src/api/alarm-shared.js`

```diff
  list: async (params = {}) => {
    const result = await sharedApi.alarm.getAlarms(params);
-   return { data: result.data };
+   // 保持完整的分页响应格式（包含 data, meta, links）
+   return result;
  },
```

#### 2. `web/src/api/device-shared.js`

```diff
  // deviceTypeApi
  list: async (params = {}) => {
    const result = await sharedApi.device.getDeviceTypes(params);
-   return { data: result.data };
+   // 保持完整的分页响应格式（包含 data, meta, links）
+   return result;
  },

  // deviceApi
  list: async (params = {}) => {
    const result = await sharedApi.device.getDevices(params);
-   return { data: result.data };
+   // 保持完整的分页响应格式（包含 data, meta, links）
+   return result;
  },
```

#### 3. `web/src/api/repair-shared.js`

```diff
  list: async (params = {}) => {
    const result = await sharedApi.repair.getRepairRecords(params);
-   return { data: result.data };
+   // 保持完整的分页响应格式（包含 data, meta, links）
+   return result;
  },
```

### 验证方法

```javascript
// 打开浏览器控制台
// 应该看到完整的响应对象
console.log('✅ Shared API - 告警列表响应:', response);
// {
//   data: [...],
//   meta: { total: 100, page: 1, page_size: 20 },
//   links: {...}
// }

// 分页信息应该正确显示
console.log('分页信息:', {
  items: alarmData.value.length,
  total: pagination.itemCount,
  page: pagination.page,
  pageSize: pagination.pageSize,
});
```

---

## 🐛 问题 3: 维修记录 API 404 错误

### 错误现象

```
GET http://localhost:3000/api/v2/repair-records 404 (Not Found)
```

### 错误原因

**错误的 API 路径映射**:
- Shared 层使用: `/repair-records`
- 完整路径: `/api/v2/repair-records`
- 实际后端路径: `/api/v2/device/maintenance/repair-records`

### 解决方案

**修改文件**: `packages/shared/api/repair.ts`

```diff
  async getRepairRecords(params?: PaginationParams & {...}) {
-   return this.client.get<Paginated<RepairRecord>>('/repair-records', params);
+   return this.client.get<Paginated<RepairRecord>>('/device/maintenance/repair-records', params);
  }

  async getRepairRecord(id: number) {
-   return this.client.get<RepairRecord>(`/repair-records/${id}`);
+   return this.client.get<RepairRecord>(`/device/maintenance/repair-records/${id}`);
  }

  async createRepairRecord(data: RepairRecordCreateInput) {
-   return this.client.post<RepairRecord>('/repair-records', data);
+   return this.client.post<RepairRecord>('/device/maintenance/repair-records', data);
  }

  // ... 其他方法类似修改
```

---

## 🐛 问题 4: GET 请求无法传递查询参数

### 错误现象

```
401 Unauthorized - {"message":"缺少访问令牌"}
```

尽管 localStorage 中有 token，但请求时没有携带。

### 错误原因

**GET 方法缺少参数支持**:

`packages/shared/api/client.ts` 中的 `get` 方法没有接收 `params` 参数，导致：
1. 查询参数无法传递给后端
2. 某些依赖查询参数的认证逻辑失效

```typescript
// ❌ 错误实现
get<T = unknown>(path: string): Promise<T> {
  return this.request<T>(path, { method: "GET" });
}

// 调用时
await client.get('/devices/types', { page: 1 });  // params 被忽略！
```

### 解决方案

**修改文件**: `packages/shared/api/client.ts`

```diff
- get<T = unknown>(path: string): Promise<T> {
-   return this.request<T>(path, { method: "GET" });
- }
+ get<T = unknown>(path: string, params?: Record<string, any>): Promise<T> {
+   let url = path;
+   if (params) {
+     const query = new URLSearchParams();
+     Object.entries(params).forEach(([key, value]) => {
+       if (value !== null && value !== undefined) {
+         query.append(key, String(value));
+       }
+     });
+     const queryString = query.toString();
+     if (queryString) url = `${path}?${queryString}`;
+   }
+   return this.request<T>(url, { method: "GET" });
+ }
```

**效果**:
```typescript
// ✅ 正确使用
await client.get('/devices/types', { page: 1, page_size: 20 });
// 实际请求: GET /api/v2/devices/types?page=1&page_size=20
```

### 验证方法

```javascript
// 打开浏览器控制台，检查网络请求
// 应该看到完整的查询参数
GET /api/v2/devices/types?page=1&page_size=20
Headers:
  Authorization: Bearer eyJhbGci...
Status: 200 OK
```

---

## 📚 经验总结

### 1. API 路径映射原则

**规则**: Shared 层 API 路径应该与后端实际路径完全一致（去掉 baseURL 部分）

```javascript
// ✅ 正确
baseURL = '/api/v2'
path = '/devices/types'
完整路径 = '/api/v2/devices/types'

// ❌ 错误
baseURL = '/api/v2'
path = '/device-types'
完整路径 = '/api/v2/device-types'  // 后端不存在此路径
```

**验证方法**:
1. 查看后端路由定义（`app/api/v2/__init__.py`）
2. 使用 Postman/curl 测试实际 API 路径
3. 确保 Shared 层路径与后端一致

### 2. 响应格式保持原则

**规则**: 适配器应该保持后端原始响应格式，不要做不必要的转换

```javascript
// ✅ 正确：保持完整响应
list: async (params = {}) => {
  const result = await sharedApi.xxx.list(params);
  return result;  // { data, meta, links }
},

// ❌ 错误：丢失元数据
list: async (params = {}) => {
  const result = await sharedApi.xxx.list(params);
  return { data: result.data };  // 只有 data，丢失 meta 和 links
},

// ✅ 正确：只在必要时转换
get: async (id) => {
  const result = await sharedApi.xxx.get(id);
  return { data: result.data };  // 单个对象，不需要 meta
},
```

**适用场景**:
- ✅ 列表 API: 保持完整响应（需要 `meta` 用于分页）
- ✅ 详情 API: 可以只返回 `data`（不需要分页）
- ✅ 创建/更新 API: 可以只返回 `data`

### 3. 调试技巧

#### A. 网络请求调试

```javascript
// 1. 在浏览器开发者工具 Network 面板检查
// 2. 查看请求 URL 是否正确
// 3. 查看响应状态码和数据

// 示例：
GET /api/v2/devices/types?page=1&page_size=20
Status: 200 OK
Response: {
  "data": [...],
  "meta": { "total": 10 },
  "links": {...}
}
```

#### B. 响应数据调试

```javascript
// 在 API 调用后添加详细日志
const response = await alarmApi.list(params);
console.log('✅ Shared API 响应:', response);
console.log('数据类型:', typeof response);
console.log('data 字段:', response.data);
console.log('meta 字段:', response.meta);
console.log('links 字段:', response.links);
```

#### C. 类型检查

```javascript
// 使用类型守卫检查响应格式
if (response && response.data && Array.isArray(response.data)) {
  console.log('✅ 标准数组响应');
  if (response.meta) {
    console.log('✅ 包含分页元数据');
  } else {
    console.warn('⚠️ 缺少分页元数据');
  }
}
```

---

## ✅ 修复检查清单

### 代码修复

- [x] 修复 `packages/shared/api/device.ts` 路径
- [x] 修复 `packages/shared/api/repair.ts` 路径
- [x] 修复 `packages/shared/api/client.ts` GET 参数传递
- [x] 修复 `web/src/api/device-shared.js` 响应格式
- [x] 修复 `web/src/api/alarm-shared.js` 响应格式
- [x] 修复 `web/src/api/repair-shared.js` 响应格式

### 功能验证

- [ ] 设备类型列表加载正常
- [ ] 告警列表加载正常
- [ ] 维修记录列表加载正常
- [ ] 分页信息显示正确
- [ ] 搜索/筛选功能正常
- [ ] 无 404 错误
- [ ] 无 "未知的响应数据格式" 错误

### 文档更新

- [x] 创建问题修复记录文档
- [x] 提交代码到 Git
- [x] 推送到 GitHub

---

## 🔄 后续优化建议

### 1. 统一响应包装

创建一个通用的响应包装函数：

```typescript
// packages/shared/api/response-wrapper.ts
export function wrapListResponse<T>(result: any) {
  // 保持完整的分页响应
  return result;
}

export function wrapDetailResponse<T>(result: any) {
  // 详情接口可以只返回 data
  return { data: result.data };
}
```

### 2. 类型安全

为所有 API 响应添加 TypeScript 类型：

```typescript
interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    page_size: number;
  };
  links: {
    self: string;
    first?: string;
    last?: string;
    prev?: string;
    next?: string;
  };
}

export const alarmApi = {
  list: async (params = {}): Promise<PaginatedResponse<Alarm>> => {
    return await sharedApi.alarm.getAlarms(params);
  },
};
```

### 3. 自动化测试

添加 API 响应格式测试：

```javascript
// tests/api/alarm-shared.test.js
describe('Alarm API', () => {
  it('should return paginated response', async () => {
    const response = await alarmApi.list();
    
    expect(response).toHaveProperty('data');
    expect(response).toHaveProperty('meta');
    expect(response.meta).toHaveProperty('total');
    expect(Array.isArray(response.data)).toBe(true);
  });
});
```

---

## 📖 相关文档

- [Shared 层 API 快速参考](./Shared层API快速参考.md)
- [批量组件迁移指南](./批量组件迁移指南.md)
- [Web 端 Shared 层迁移进度](./Web端Shared层迁移进度.md)

---

**修复完成时间**: 2025-10-25  
**修复人**: AI Assistant  
**Commit**: `a497c9d`

