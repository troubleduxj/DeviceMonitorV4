# Shared 层 API 快速参考

> Web 端 Shared 层 API 适配器快速使用指南

## 📦 导入方式

### 方式 1：统一导入（推荐）
```javascript
import api from '@/api/index-shared';

// 使用
await api.auth.login({ username, password });
await api.device.list({ page: 1 });
await api.alarm.getStats();
await api.repair.list({ repair_status: 'pending' });
```

### 方式 2：按需导入
```javascript
import { authApi, deviceApi, alarmApi, repairApi } from '@/api/index-shared';

// 使用
await authApi.login({ username, password });
await deviceApi.list({ page: 1 });
```

### 方式 3：直接使用 Shared（最灵活）
```javascript
import sharedApi from '@/api/shared';

// 使用
await sharedApi.auth.login({ username, password });
await sharedApi.device.getDevices({ page: 1 });
```

---

## 🔐 认证 API (auth-shared.js)

### 登录
```javascript
import { authApi } from '@/api/index-shared';

const result = await authApi.login({
  username: 'admin',
  password: '123456',
  remember: true,
});

// 返回: { data: { access_token, refresh_token, user, permissions, menus } }
```

### 登出
```javascript
await authApi.logout();
// 自动清除 localStorage 中的所有认证数据
```

### 刷新 Token
```javascript
// 自动使用 localStorage 中的 refreshToken
await authApi.refreshToken();

// 或手动传入
await authApi.refreshToken('your-refresh-token');
```

### 获取当前用户
```javascript
const result = await authApi.getCurrentUser();
// 返回: { data: User }
```

### 修改密码
```javascript
await authApi.changePassword('old-password', 'new-password');
```

### 权限检查
```javascript
import { hasPermission, isSuperAdmin } from '@/api/index-shared';

// 检查单个权限
if (hasPermission('device:create')) {
  // 有权限
}

// 检查多个权限（任一）
if (hasAnyPermission(['device:create', 'device:update'])) {
  // 有任一权限
}

// 检查多个权限（全部）
if (hasAllPermissions(['device:create', 'device:update'])) {
  // 有所有权限
}

// 检查是否为超级管理员
if (isSuperAdmin()) {
  // 是超级管理员
}
```

### 本地数据获取
```javascript
// 获取本地用户信息
const user = authApi.getLocalUser();

// 获取本地权限列表
const permissions = authApi.getLocalPermissions();

// 获取本地菜单列表
const menus = authApi.getLocalMenus();

// 检查是否已登录
const isAuth = authApi.isAuthenticated();
```

### Token 管理
```javascript
import { getToken, setToken, isTokenExpiringSoon, autoRefreshToken } from '@/api/index-shared';

// 获取 Token
const token = getToken();

// 设置 Token
setToken('new-token');

// 检查 Token 是否即将过期（提前 5 分钟）
if (isTokenExpiringSoon()) {
  await autoRefreshToken();
}

// 自动刷新 Token（推荐在定时器中使用）
setInterval(autoRefreshToken, 60000); // 每分钟检查一次
```

---

## 📱 设备 API (device-shared.js)

### 设备列表
```javascript
import { deviceApi } from '@/api/index-shared';

const result = await deviceApi.list({
  page: 1,
  pageSize: 20,
  device_type: 'welding',
  status: 'online',
});

// 返回: { data: { items, total, page, pageSize } }
```

### 设备详情
```javascript
// 通过 ID
const result = await deviceApi.get(1);

// 通过设备编码
const result = await deviceApi.getByCode('WM-001');
```

### 创建设备
```javascript
await deviceApi.create({
  device_name: '焊机-001',
  device_code: 'WM-001',
  device_type: 'welding',
  device_model: 'MODEL-X',
  manufacturer: '厂商A',
  online_address: '192.168.1.100',
});
```

### 更新设备
```javascript
await deviceApi.update(1, {
  device_name: '焊机-001（更新）',
  status: 'maintenance',
});
```

### 删除设备
```javascript
// 单个删除
await deviceApi.delete(1);

// 批量删除
await deviceApi.batchDelete([1, 2, 3]);
```

### 设备统计
```javascript
const result = await deviceApi.getStats();
// 返回: { data: { total, online, offline, maintenance, alarm } }
```

### 设备类型 API
```javascript
import { deviceTypeApi } from '@/api/index-shared';

// 获取设备类型列表
const result = await deviceTypeApi.list({ page: 1 });

// 创建设备类型
await deviceTypeApi.create({
  type_code: 'welding',
  type_name: '焊机',
  description: '焊接设备',
});
```

---

## 🚨 告警 API (alarm-shared.js)

### 告警列表
```javascript
import { alarmApi, AlarmLevel, AlarmStatus } from '@/api/index-shared';

const result = await alarmApi.list({
  page: 1,
  pageSize: 20,
  level: AlarmLevel.WARNING,
  status: AlarmStatus.PENDING,
  device_id: 1,
});
```

### 告警详情
```javascript
const result = await alarmApi.get(1);
```

### 创建告警
```javascript
await alarmApi.create({
  title: '温度过高',
  level: AlarmLevel.WARNING,
  device_id: 1,
  description: '设备温度超过阈值',
  occurred_at: new Date().toISOString(),
});
```

### 确认告警
```javascript
await alarmApi.acknowledge(1, '已确认，正在处理');
```

### 解决告警
```javascript
await alarmApi.resolve(1, '问题已解决');
```

### 关闭告警
```javascript
await alarmApi.close(1, '已关闭');
```

### 批量操作
```javascript
// 批量确认
await alarmApi.batchAcknowledge([1, 2, 3], '批量确认');

// 批量解决
await alarmApi.batchResolve([1, 2, 3], '批量解决');
```

### 告警统计
```javascript
const result = await alarmApi.getStats({
  start_date: '2025-10-01',
  end_date: '2025-10-25',
});

// 返回: { 
//   data: { 
//     total, 
//     pending, 
//     acknowledged, 
//     resolved,
//     by_level: { info, warning, error, critical }
//   }
// }
```

### 实时告警
```javascript
const result = await alarmApi.getRealtime(10); // 获取最新 10 条
```

### 告警常量
```javascript
import {
  AlarmLevel,
  AlarmLevelText,
  AlarmLevelColor,
  AlarmStatus,
  AlarmStatusText,
  AlarmStatusColor,
} from '@/api/index-shared';

// 级别
console.log(AlarmLevel.WARNING); // 'warning'
console.log(AlarmLevelText[AlarmLevel.WARNING]); // '警告'
console.log(AlarmLevelColor[AlarmLevel.WARNING]); // 'warning'

// 状态
console.log(AlarmStatus.PENDING); // 'pending'
console.log(AlarmStatusText[AlarmStatus.PENDING]); // '待处理'
console.log(AlarmStatusColor[AlarmStatus.PENDING]); // 'warning'
```

---

## 🔧 维修 API (repair-shared.js)

### 维修记录列表
```javascript
import { repairApi, RepairStatus } from '@/api/index-shared';

const result = await repairApi.list({
  page: 1,
  pageSize: 20,
  device_id: 1,
  repair_status: RepairStatus.PENDING,
  start_date: '2025-10-01',
  end_date: '2025-10-25',
});
```

### 维修记录详情
```javascript
const result = await repairApi.get(1);
```

### 创建维修记录
```javascript
await repairApi.create({
  device_id: 1,
  fault_description: '设备故障描述',
  reported_at: new Date().toISOString(),
});
```

### 更新维修记录
```javascript
await repairApi.update(1, {
  repair_description: '维修过程描述',
  repair_result: '维修结果',
});
```

### 维修流程操作
```javascript
// 分配维修任务
await repairApi.assign(1, 123); // 123 为维修人员 ID

// 开始维修
await repairApi.start(1);

// 完成维修
await repairApi.complete(1, '维修过程描述', '维修结果说明');

// 取消维修
await repairApi.cancel(1, '取消原因');
```

### 删除维修记录
```javascript
// 单个删除
await repairApi.delete(1);

// 批量删除
await repairApi.batchDelete([1, 2, 3]);
```

### 设备维修历史
```javascript
const result = await repairApi.getDeviceHistory(1, { page: 1 });
```

### 维修常量与工具
```javascript
import {
  RepairStatus,
  RepairStatusText,
  RepairStatusColor,
  calculateRepairDuration,
  formatRepairDuration,
  isRepairOverdue,
} from '@/api/index-shared';

// 状态常量
console.log(RepairStatus.IN_PROGRESS); // 'in_progress'
console.log(RepairStatusText[RepairStatus.IN_PROGRESS]); // '进行中'

// 计算维修耗时（分钟）
const duration = calculateRepairDuration('2025-10-25 10:00:00', '2025-10-25 12:30:00');
console.log(duration); // 150

// 格式化维修耗时
console.log(formatRepairDuration(125)); // "2小时5分钟"
console.log(formatRepairDuration(1500)); // "1天1小时"

// 判断是否超时
const overdue = isRepairOverdue('2025-10-24 10:00:00', RepairStatus.PENDING, 24);
console.log(overdue); // true/false
```

---

## 🎨 在 Vue 组件中使用

### 基础示例
```vue
<script setup>
import { ref, onMounted } from 'vue';
import { deviceApi } from '@/api/index-shared';

const devices = ref([]);
const loading = ref(false);

async function loadDevices() {
  loading.value = true;
  try {
    const result = await deviceApi.list({ page: 1, pageSize: 20 });
    devices.value = result.data.items;
  } catch (error) {
    console.error('加载失败:', error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadDevices();
});
</script>
```

### 带权限检查
```vue
<script setup>
import { deviceApi } from '@/api/index-shared';
import { hasPermission } from '@/api/index-shared';

const canCreate = hasPermission('device:create');
const canEdit = hasPermission('device:update');
const canDelete = hasPermission('device:delete');

async function handleCreate() {
  if (!canCreate) {
    return window.$message?.warning('无权限');
  }
  
  await deviceApi.create({
    device_name: '新设备',
    device_code: 'NEW-001',
    device_type: 'welding',
  });
}
</script>

<template>
  <n-button v-if="canCreate" @click="handleCreate">创建设备</n-button>
</template>
```

### 使用常量
```vue
<script setup>
import { ref } from 'vue';
import { alarmApi, AlarmLevel, AlarmStatus } from '@/api/index-shared';

const alarms = ref([]);

async function loadAlarms() {
  const result = await alarmApi.list({
    page: 1,
    level: AlarmLevel.WARNING,
    status: AlarmStatus.PENDING,
  });
  alarms.value = result.data.items;
}
</script>

<template>
  <n-select
    v-model:value="selectedLevel"
    :options="[
      { label: '信息', value: AlarmLevel.INFO },
      { label: '警告', value: AlarmLevel.WARNING },
      { label: '错误', value: AlarmLevel.ERROR },
      { label: '严重', value: AlarmLevel.CRITICAL },
    ]"
  />
</template>
```

---

## 🚀 最佳实践

### 1. 统一错误处理
```javascript
import api from '@/api/index-shared';

async function loadData() {
  try {
    const result = await api.device.list({ page: 1 });
    return result.data;
  } catch (error) {
    window.$message?.error(`加载失败: ${error.message}`);
    return null;
  }
}
```

### 2. 使用 composables
```javascript
// composables/useDevices.js
import { ref } from 'vue';
import { deviceApi } from '@/api/index-shared';

export function useDevices() {
  const devices = ref([]);
  const loading = ref(false);
  
  async function loadDevices(params) {
    loading.value = true;
    try {
      const result = await deviceApi.list(params);
      devices.value = result.data.items;
      return result.data;
    } finally {
      loading.value = false;
    }
  }
  
  return { devices, loading, loadDevices };
}
```

### 3. 自动刷新 Token
```javascript
// main.js
import { autoRefreshToken } from '@/api/index-shared';

// 每分钟检查一次 Token 是否需要刷新
setInterval(autoRefreshToken, 60000);
```

### 4. 权限路由守卫
```javascript
// router/guard/permission.js
import { authApi, hasPermission } from '@/api/index-shared';

router.beforeEach(async (to, from, next) => {
  if (!authApi.isAuthenticated()) {
    return next('/login');
  }
  
  if (to.meta.permission && !hasPermission(to.meta.permission)) {
    return next('/403');
  }
  
  next();
});
```

---

## 📚 相关文档

- [Shared 层完整文档](../packages/shared/README.md)
- [Web 端接入指南](./Web端接入Shared层指南.md)
- [迁移进度追踪](./Web端Shared层迁移进度.md)
- [NativeScript 改造方案](./NativeScript-Vue 多端化改造方案与任务清单.md)

