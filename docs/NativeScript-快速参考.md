# NativeScript 快速参考卡片

> 🎯 关键命令和代码片段速查

---

## ⚡ 常用命令

### CLI 基础

```bash
# 安装 CLI
npm install -g @nativescript/core

# 环境检查
ns doctor android
ns doctor ios

# 创建项目
ns create <项目名> --vue --ts

# 运行
ns run android
ns run ios
ns run android --device <设备ID>

# 清理
ns clean

# 构建发布版
ns build android --release
ns build ios --release
```

---

## 📁 项目结构

```
mobile/
├── app/
│   ├── App.vue                 # 根组件
│   ├── main.ts                 # 入口文件
│   ├── pages/                  # 页面
│   │   ├── LoginPage.vue
│   │   ├── HomePage.vue
│   │   └── DeviceListPage.vue
│   ├── components/             # 组件
│   ├── stores/                 # Pinia stores
│   ├── services/               # 服务层
│   │   └── apiService.ts
│   ├── navigation/             # 导航配置
│   └── plugins/                # 原生插件封装
├── nativescript.config.ts      # NS 配置
├── package.json
└── tsconfig.json
```

---

## 🔧 核心代码模板

### 1. API Service（连接 Shared 层）

```typescript
// mobile/app/services/apiService.ts
import { createApiServices } from '@shared/api';
import { getString, setString, remove } from '@nativescript/core/application-settings';

const TOKEN_KEY = 'access_token';

const getToken = (): string => getString(TOKEN_KEY, '');
const setToken = (token: string): void => setString(TOKEN_KEY, token);
const removeToken = (): void => remove(TOKEN_KEY);

const baseURL = __DEV__ 
  ? 'http://10.0.2.2:8000/api/v2'
  : 'https://your-api.com/api/v2';

export const api = createApiServices({ baseURL, getToken });
export { setToken, removeToken };
```

---

### 2. 认证 Store

```typescript
// mobile/app/stores/authStore.ts
import { defineStore } from 'pinia';
import { api, setToken, removeToken } from '../services/apiService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isLoggedIn: false,
  }),
  
  actions: {
    async login(username: string, password: string) {
      const result = await api.auth.login({ username, password });
      setToken(result.data.token);
      this.user = result.data.user;
      this.isLoggedIn = true;
    },
    
    async logout() {
      await api.auth.logout();
      removeToken();
      this.user = null;
      this.isLoggedIn = false;
    },
  },
});
```

---

### 3. 页面模板

```vue
<!-- mobile/app/pages/LoginPage.vue -->
<template>
  <Page>
    <ActionBar title="登录" />
    
    <StackLayout padding="20">
      <TextField v-model="username" hint="用户名" />
      <TextField v-model="password" hint="密码" secure="true" />
      <Button text="登录" @tap="handleLogin" />
    </StackLayout>
  </Page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/authStore';
import { navigateTo } from '@nativescript/vue';
import HomePage from './HomePage.vue';

const authStore = useAuthStore();
const username = ref('');
const password = ref('');

async function handleLogin() {
  await authStore.login(username.value, password.value);
  navigateTo(HomePage, { clearHistory: true });
}
</script>
```

---

### 4. 列表页模板

```vue
<!-- mobile/app/pages/DeviceListPage.vue -->
<template>
  <Page>
    <ActionBar title="设备列表" />
    
    <ListView :items="devices" @itemTap="onItemTap">
      <template #default="{ item }">
        <StackLayout padding="10">
          <Label :text="item.name" fontSize="16" fontWeight="bold" />
          <Label :text="item.type" fontSize="14" color="#666" />
        </StackLayout>
      </template>
    </ListView>
  </Page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from '../services/apiService';

const devices = ref([]);

onMounted(async () => {
  const result = await api.device.getDevices({ page: 1, page_size: 20 });
  devices.value = result.data.records;
});

function onItemTap(args) {
  const device = devices.value[args.index];
  // 导航到详情页
}
</script>
```

---

## 🎨 常用组件

### 布局组件

```xml
<StackLayout>      <!-- 垂直堆叠 -->
<GridLayout>       <!-- 网格布局 -->
<FlexboxLayout>    <!-- Flexbox -->
<AbsoluteLayout>   <!-- 绝对定位 -->
<WrapLayout>       <!-- 自动换行 -->
```

### UI 组件

```xml
<Label text="文本" />
<Button text="按钮" @tap="handleTap" />
<TextField v-model="text" hint="提示" />
<TextView v-model="text" />  <!-- 多行 -->
<Switch v-model="checked" />
<Slider v-model="value" />
<DatePicker v-model="date" />
<TimePicker v-model="time" />
<ListView :items="list" />
<ScrollView>...</ScrollView>
<Image src="~/assets/img.png" />
```

---

## 🔌 常用插件

### 安装

```bash
# Secure Storage（Token 存储）
ns plugin add @nativescript/secure-storage

# 相机
ns plugin add @nativescript/camera

# 二维码扫描
ns plugin add nativescript-barcodescanner

# 地理位置
ns plugin add @nativescript/geolocation

# 本地通知
ns plugin add @nativescript/local-notifications
```

### 使用示例

```typescript
// Secure Storage
import { SecureStorage } from '@nativescript/secure-storage';
const storage = new SecureStorage();
await storage.set({ key: 'token', value: 'xxx' });
const token = await storage.get({ key: 'token' });

// 相机
import { Camera } from '@nativescript/camera';
const imageAsset = await Camera.takePicture();

// 二维码扫描
import { BarcodeScanner } from 'nativescript-barcodescanner';
const result = await BarcodeScanner.scan();
console.log(result.text);

// 地理位置
import { getCurrentLocation } from '@nativescript/geolocation';
const location = await getCurrentLocation({ desiredAccuracy: 3 });
console.log(location.latitude, location.longitude);
```

---

## 🌐 环境配置

### API 地址

```typescript
// 开发环境
const DEV_URL = isAndroid 
  ? 'http://10.0.2.2:8000/api/v2'   // Android 模拟器
  : 'http://localhost:8000/api/v2'; // iOS 模拟器

// 生产环境
const PROD_URL = 'https://your-api.com/api/v2';

const baseURL = __DEV__ ? DEV_URL : PROD_URL;
```

### 平台检测

```typescript
import { isAndroid, isIOS } from '@nativescript/core';

if (isAndroid) {
  // Android 特定代码
}

if (isIOS) {
  // iOS 特定代码
}
```

---

## 🎯 导航

```typescript
import { navigateTo, goBack } from '@nativescript/vue';

// 前进
navigateTo(HomePage);

// 前进并清除历史
navigateTo(HomePage, { clearHistory: true });

// 后退
goBack();

// 携带参数
navigateTo(DetailPage, {
  props: { deviceId: 123 }
});

// 在页面中接收参数
const props = defineProps<{ deviceId: number }>();
```

---

## 🎨 样式

```xml
<!-- 内联样式 -->
<Label text="Hello" color="red" fontSize="20" fontWeight="bold" />

<!-- CSS 类 -->
<Label text="Hello" class="title" />

<style scoped>
.title {
  color: #333;
  font-size: 20;
  font-weight: bold;
  margin: 10;
}
</style>

<!-- 全局样式 -->
<!-- app.css -->
```

### 单位

```
数字 = 设备独立像素（DIP）
fontSize="16"   // 16 DIP
width="100"     // 100 DIP
margin="10"     // 10 DIP
```

---

## 🐛 调试

### 日志

```typescript
console.log('普通日志');
console.error('错误日志');
console.warn('警告日志');

// 查看日志
ns run android --log trace
```

### Chrome DevTools

```bash
# 运行后，Chrome 访问：
chrome://inspect
```

---

## 📱 设备连接

### Android

```bash
# 查看设备
adb devices

# 指定设备运行
ns run android --device <设备ID>

# 端口转发（访问电脑服务）
adb reverse tcp:8000 tcp:8000
```

### iOS

```bash
# 查看设备
xcrun xctrace list devices

# 指定设备运行
ns run ios --device <设备名称>
```

---

## ⚠️ 常见问题

### 1. Android 无法访问本机 API

```typescript
// ❌ 错误
const baseURL = 'http://localhost:8000';

// ✅ 正确
const baseURL = 'http://10.0.2.2:8000';  // Android 模拟器
```

### 2. 热重载不工作

```bash
# 重启应用
ns run android --no-hmr
```

### 3. 构建失败

```bash
# 清理缓存
ns clean
rm -rf platforms node_modules
npm install
```

---

## 📚 参考资源

- [NativeScript 文档](https://docs.nativescript.org/)
- [NativeScript-Vue 文档](https://nativescript-vue.org/)
- [插件市场](https://market.nativescript.org/)
- [官方示例](https://github.com/NativeScript/nativescript-vue-samples)

---

**保存此文件以便快速查阅！** 🚀

