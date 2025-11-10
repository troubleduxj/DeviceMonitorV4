# Web 端接入 Shared 层指南

> 本文档说明如何将现有 Web 端代码逐步迁移到使用跨端共享层（`packages/shared`）

## 📋 目录

1. [接入概述](#接入概述)
2. [API 层迁移](#api-层迁移)
3. [工具函数迁移](#工具函数迁移)
4. [类型定义迁移](#类型定义迁移)
5. [迁移检查清单](#迁移检查清单)

---

## 接入概述

### 为什么要接入 Shared 层？

- ✅ **代码复用**：Web 和移动端共享业务逻辑
- ✅ **类型安全**：统一的 TypeScript 类型定义
- ✅ **维护简化**：一处修改，多端生效
- ✅ **渐进式迁移**：不影响现有功能，逐步替换

### 已完成的工作

```
packages/shared/
├── types/         ✅ 完整的业务类型定义（User、Device、Alarm 等）
├── utils/         ✅ 跨端工具函数（validators、datetime、format、helpers、storage）
└── api/           ✅ 统一的 API 客户端（auth、device、alarm、repair）
```

### Web 端适配层

```
web/src/
├── api/shared.ts      ✅ Shared API 适配器
├── utils/shared.ts    ✅ Shared Utils 导出
├── types/shared.ts    ✅ Shared Types 导出
└── examples/SharedLayerExample.vue  ✅ 使用示例
```

---

## API 层迁移

### 步骤 1：导入 Shared API

**旧代码（web/src/api/device.js）**

```javascript
import api from './index';

export const getDevices = (params) => {
  return api.get('/devices', { params });
};

export const getDevice = (id) => {
  return api.get(`/devices/${id}`);
};
```

**新代码（使用 Shared API）**

```javascript
import sharedApi from '@/api/shared';

export const getDevices = (params) => {
  return sharedApi.device.getDevices(params);
};

export const getDevice = (id) => {
  return sharedApi.device.getDevice(id);
};
```

### 步骤 2：逐步替换现有 API 调用

**示例：设备列表页面**

```vue
<script setup>
// 旧方式
// import { getDevices } from '@/api/device';

// 新方式
import sharedApi from '@/api/shared';

async function loadDevices() {
  // 旧方式
  // const { data } = await getDevices({ page: 1, pageSize: 20 });
  
  // 新方式
  const result = await sharedApi.device.getDevices({
    page: 1,
    pageSize: 20,
  });
  
  console.log(result.data);
}
</script>
```

### API 迁移对照表

| 业务模块 | 旧 API 文件 | Shared API | 状态 |
|---------|------------|------------|------|
| 认证登录 | `api/auth.js` | `sharedApi.auth.*` | ⏳ 待迁移 |
| 设备管理 | `api/device-v2.js` | `sharedApi.device.*` | ⏳ 待迁移 |
| 告警管理 | `api/alarm.js` | `sharedApi.alarm.*` | ⏳ 待迁移 |
| 维修记录 | `api/repair.js` | `sharedApi.repair.*` | ⏳ 待迁移 |

---

## 工具函数迁移

### 步骤 1：导入 Shared Utils

**旧代码（web/src/utils/common/common.js）**

```javascript
import dayjs from 'dayjs';

export function formatDateTime(time, format = 'YYYY-MM-DD HH:mm:ss') {
  return dayjs(time).format(format);
}

export function debounce(fn, delay) {
  // ...
}
```

**新代码（使用 Shared Utils）**

```javascript
// 直接从 shared 导入
import { formatDateTime, debounce } from '@/utils/shared';

// 或者按需导入
export { formatDateTime, debounce } from '@/utils/shared';
```

### 步骤 2：更新组件中的引用

**示例：日期格式化**

```vue
<script setup>
// 旧方式
// import { formatDateTime } from '@/utils/common/common';

// 新方式
import { formatDateTime } from '@/utils/shared';

const formattedDate = formatDateTime(new Date());
</script>
```

### 工具函数迁移对照表

| 功能分类 | 旧工具文件 | Shared Utils | 状态 |
|---------|-----------|--------------|------|
| 类型检查 | `utils/common/is.js` | `isValidEmail, isEmpty, isObject` 等 | ⏳ 待迁移 |
| 日期处理 | `utils/common/common.js` | `formatDate, formatDateTime` 等 | ⏳ 待迁移 |
| 数据格式化 | `utils/format.js` | `formatFileSize, formatNumber` 等 | ⏳ 待迁移 |
| 防抖节流 | `utils/common/common.js` | `debounce, throttle` | ⏳ 待迁移 |
| 对象操作 | 无 | `deepClone, pick, omit` 等 | ✅ 新增 |

---

## 类型定义迁移

### 步骤 1：导入 Shared Types

**旧代码（组件中内联类型）**

```vue
<script setup lang="ts">
interface Device {
  id: number;
  device_name: string;
  device_code: string;
  status?: string;
}

const devices = ref<Device[]>([]);
</script>
```

**新代码（使用 Shared Types）**

```vue
<script setup lang="ts">
import type { Device } from '@/types/shared';

const devices = ref<Device[]>([]);
</script>
```

### 步骤 2：API 返回值类型

```typescript
import type { Paginated, Device } from '@/types/shared';
import sharedApi from '@/api/shared';

async function getDeviceList(): Promise<Paginated<Device>> {
  const result = await sharedApi.device.getDevices({ page: 1, pageSize: 20 });
  return result.data;
}
```

### 可用类型列表

```typescript
// 通用类型
Maybe<T>, Result<T, E>, HttpMethod, ApiResponse<T>, Paginated<T>

// 用户与权限
User, UserMinimal, Role, Department, Menu, LoginRequest, LoginResponse

// 设备管理
Device, DeviceType, DeviceCreateInput, DeviceUpdateInput, DeviceStatusStats

// 告警管理
Alarm, AlarmStats, AlarmCreateInput, AlarmAcknowledgeInput, AlarmResolveInput

// 维修管理
RepairRecord, RepairRecordCreateInput, RepairRecordUpdateInput

// 系统配置
SystemConfig, SystemConfigCreateInput, SystemConfigUpdateInput

// 统计数据
DashboardStats, ChartData, TimeSeriesData
```

---

## 迁移检查清单

### 阶段 1：基础接入 ✅

- [x] 创建 `web/src/api/shared.ts`
- [x] 创建 `web/src/utils/shared.ts`
- [x] 创建 `web/src/types/shared.ts`
- [x] 创建示例页面 `SharedLayerExample.vue`

### 阶段 2：核心模块迁移 ⏳

#### 认证模块
- [ ] 登录页面 (`views/login/index.vue`)
- [ ] 权限管理 (`composables/usePermission.js`)
- [ ] 用户信息 store (`store/modules/user.js`)

#### 设备模块
- [ ] 设备列表 (`views/device/baseinfo/index.vue`)
- [ ] 设备详情页面
- [ ] 设备类型管理

#### 告警模块
- [ ] 告警列表 (`views/alarm/*.vue`)
- [ ] 告警统计图表

#### 维修模块
- [ ] 维修记录列表
- [ ] 维修表单

### 阶段 3：工具函数迁移 ⏳

- [ ] 替换 `utils/common/is.js` 引用
- [ ] 替换 `utils/common/common.js` 引用
- [ ] 替换 `utils/format.js` 引用
- [ ] 移除冗余的旧工具文件

### 阶段 4：清理优化 ⏳

- [ ] 删除已迁移的旧 API 文件
- [ ] 删除已迁移的旧工具文件
- [ ] 更新文档和注释
- [ ] 运行完整测试

---

## 注意事项

### ⚠️ 兼容性

- Shared 层的 API 响应格式可能与旧 API 略有不同，需要适配
- 某些工具函数的参数顺序可能不同，需要检查

### ⚠️ 错误处理

- Shared API 默认不自动处理错误提示，需要在调用处添加 try-catch
- 可以在 `api/shared.ts` 中统一配置错误拦截器

### ⚠️ Token 管理

- 当前 Token 从 `localStorage` 获取
- 如需修改，在 `web/src/api/shared.ts` 中调整 `getToken` 函数

### ⚠️ TypeScript 支持

- 建议将组件逐步改为 `<script setup lang="ts">`
- 可以先在 `.js` 文件中使用 Shared API，再逐步迁移到 TypeScript

---

## 示例代码

完整示例请参考：`web/src/examples/SharedLayerExample.vue`

运行方式：在开发环境中访问 `/examples/shared-layer` 路由（需要在路由配置中添加）。

---

## 获取帮助

- 查看 Shared 层文档：`packages/shared/README.md`
- 查看 API 定义：`packages/shared/api/*.ts`
- 查看类型定义：`packages/shared/types/index.ts`
- 查看工具函数：`packages/shared/utils/*.ts`

