# NativeScript-Vue 集成实施指南

> 📱 将 DeviceMonitorV2 扩展到移动端（iOS/Android）的完整执行手册

**开始日期**: 2025-10-25  
**当前状态**: Phase 0 - 准备与验证  
**预计完成**: 2-3 周

---

## 📋 前置条件检查

### ✅ 已完成的工作

- ✅ **Shared 层已建立** - `packages/shared/` 包含跨端代码
- ✅ **Web 端已迁移** - 5 个核心组件使用 Shared API
- ✅ **类型定义完善** - TypeScript 类型覆盖核心业务
- ✅ **API 客户端就绪** - 支持跨平台的 HTTP 客户端

### 📦 系统要求

#### 开发环境

```bash
# 必需
Node.js: >= 16.x (推荐 18.x)
npm: >= 8.x
pnpm: >= 8.x

# 平台工具
Android: Android Studio + SDK 30+
iOS: Xcode 14+ (仅 macOS)
```

#### NativeScript 版本

```json
{
  "@nativescript/core": "^8.5.0",
  "@nativescript/vue": "^2.x",
  "nativescript-vue": "^2.x"
}
```

---

## 🚀 Phase 0: 准备与验证（当前阶段）

### 步骤 1: 安装 NativeScript CLI

```bash
# 全局安装 NativeScript CLI
npm install -g @nativescript/core

# 验证安装
ns --version

# 检查环境（会检查 Android/iOS 开发环境）
ns doctor android
ns doctor ios  # 仅 macOS
```

### 步骤 2: 创建测试项目（验证环境）

```bash
# 在项目外创建临时测试项目
cd ..
ns create ns-test-app --vue --ts

# 进入测试项目
cd ns-test-app

# 运行（Android）
ns run android

# 运行（iOS，仅 macOS）
ns run ios
```

**验证点**:
- ✅ 应用成功在模拟器/真机上运行
- ✅ 可以看到默认的 NativeScript-Vue 界面
- ✅ 热重载工作正常

### 步骤 3: 技术栈确认

创建 `docs/NativeScript技术栈版本.md`:

```markdown
# NativeScript 技术栈版本清单

## 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| @nativescript/core | 8.5.0 | NS 核心框架 |
| @nativescript/vue | 2.x | Vue 3 集成 |
| typescript | 5.x | TypeScript 支持 |
| pinia | 2.x | 状态管理 |

## 原生功能

| 插件 | 版本 | 用途 |
|------|------|------|
| @nativescript/secure-storage | latest | Token 安全存储 |
| @nativescript/local-notifications | latest | 本地通知 |
| nativescript-barcodescanner | latest | 二维码扫描 |
| @nativescript/camera | latest | 相机功能 |

## 开发工具

| 工具 | 版本 | 用途 |
|------|------|------|
| Node.js | 18.x | 运行环境 |
| pnpm | 8.x | 包管理 |
| Android Studio | 最新 | Android 开发 |
| Xcode | 14+ | iOS 开发（macOS） |
```

---

## 🏗️ Phase 1: Mobile 项目初始化

### 步骤 1: 在主仓库创建 mobile 目录

```bash
# 回到主项目
cd DeviceMonitorV2

# 创建 mobile 项目
ns create mobile --vue --ts

# 进入 mobile 目录
cd mobile
```

### 步骤 2: 配置 pnpm Workspace

修改根目录 `pnpm-workspace.yaml`:

```yaml
packages:
  - 'web'
  - 'mobile'
  - 'packages/*'
```

### 步骤 3: 配置 mobile/package.json

```json
{
  "name": "@device-monitor/mobile",
  "version": "1.0.0",
  "description": "DeviceMonitor Mobile App",
  "main": "app/app.ts",
  "scripts": {
    "android": "ns run android",
    "ios": "ns run ios",
    "clean": "ns clean",
    "build:android": "ns build android --release",
    "build:ios": "ns build ios --release"
  },
  "dependencies": {
    "@nativescript/core": "~8.5.0",
    "@nativescript/vue": "^2.0.0",
    "pinia": "^2.1.0",
    "@device-monitor/shared": "workspace:*"
  },
  "devDependencies": {
    "@nativescript/types": "~8.5.0",
    "@nativescript/webpack": "~5.0.0",
    "typescript": "~5.0.0"
  }
}
```

### 步骤 4: 配置 TypeScript

`mobile/tsconfig.json`:

```json
{
  "extends": "../tsconfig.base.json",
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "Node",
    "lib": ["ES2020"],
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "skipLibCheck": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["app/*"],
      "@shared/*": ["../packages/shared/*"]
    }
  },
  "include": ["app/**/*"],
  "exclude": ["node_modules", "platforms"]
}
```

### 步骤 5: 创建基础目录结构

```bash
cd mobile/app

# 创建目录
mkdir -p pages components stores services navigation plugins

# 创建基础文件
touch pages/LoginPage.vue
touch pages/HomePage.vue
touch stores/authStore.ts
touch services/apiService.ts
touch navigation/index.ts
```

---

## 🔌 Phase 2: 连接 Shared 层

### 步骤 1: 验证 Shared 层引用

`mobile/app/services/apiService.ts`:

```typescript
/**
 * Mobile 端 API 服务
 * 使用 Shared 层的 API 客户端
 */
import { createApiServices } from '@shared/api';
import { getString, setString, remove } from '@nativescript/core/application-settings';

// Token 管理（使用 ApplicationSettings）
const TOKEN_KEY = 'access_token';

const getToken = (): string => {
  return getString(TOKEN_KEY, '');
};

const setToken = (token: string): void => {
  setString(TOKEN_KEY, token);
};

const removeToken = (): void => {
  remove(TOKEN_KEY);
};

// 创建 API 服务实例
const baseURL = __DEV__ 
  ? 'http://10.0.2.2:8000/api/v2'  // Android 模拟器访问本机
  : 'https://your-production-api.com/api/v2';

export const api = createApiServices({
  baseURL,
  getToken,
});

export { setToken, removeToken };
```

### 步骤 2: 创建认证 Store

`mobile/app/stores/authStore.ts`:

```typescript
/**
 * 认证状态管理
 * 复用 Shared 层逻辑
 */
import { defineStore } from 'pinia';
import { api, setToken as saveToken, removeToken } from '../services/apiService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as any,
    isLoggedIn: false,
  }),

  actions: {
    async login(username: string, password: string) {
      try {
        const result = await api.auth.login({ username, password });
        
        // 保存 Token
        saveToken(result.data.token);
        
        // 更新状态
        this.user = result.data.user;
        this.isLoggedIn = true;
        
        return true;
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },

    async logout() {
      try {
        await api.auth.logout();
      } catch (error) {
        console.error('Logout failed:', error);
      } finally {
        // 清除本地数据
        removeToken();
        this.user = null;
        this.isLoggedIn = false;
      }
    },

    async checkAuth() {
      try {
        const result = await api.auth.getUserInfo();
        this.user = result.data;
        this.isLoggedIn = true;
        return true;
      } catch (error) {
        this.isLoggedIn = false;
        return false;
      }
    },
  },
});
```

### 步骤 3: 创建登录页面

`mobile/app/pages/LoginPage.vue`:

```vue
<template>
  <Page>
    <ActionBar title="设备监控系统" />
    
    <StackLayout class="login-container">
      <Label text="欢迎登录" class="title" />
      
      <TextField
        v-model="username"
        hint="用户名"
        class="input"
      />
      
      <TextField
        v-model="password"
        hint="密码"
        secure="true"
        class="input"
      />
      
      <Button
        text="登录"
        @tap="handleLogin"
        :isEnabled="!loading"
        class="btn-primary"
      />
      
      <ActivityIndicator
        v-if="loading"
        :busy="loading"
        class="loading"
      />
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
const loading = ref(false);

async function handleLogin() {
  if (!username.value || !password.value) {
    alert('请输入用户名和密码');
    return;
  }

  try {
    loading.value = true;
    await authStore.login(username.value, password.value);
    
    // 登录成功，跳转到首页
    navigateTo(HomePage, { clearHistory: true });
  } catch (error: any) {
    alert({
      title: '登录失败',
      message: error.message || '请检查用户名和密码',
      okButtonText: '确定'
    });
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-container {
  padding: 20;
  background-color: #f5f5f5;
}

.title {
  font-size: 24;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30;
  color: #333;
}

.input {
  font-size: 16;
  padding: 15;
  margin-bottom: 15;
  background-color: white;
  border-radius: 5;
}

.btn-primary {
  font-size: 18;
  font-weight: bold;
  color: white;
  background-color: #1890ff;
  padding: 15;
  border-radius: 5;
  margin-top: 10;
}

.loading {
  margin-top: 20;
}
</style>
```

### 步骤 4: 创建首页

`mobile/app/pages/HomePage.vue`:

```vue
<template>
  <Page>
    <ActionBar title="首页">
      <ActionItem
        text="退出"
        @tap="handleLogout"
        ios.position="right"
        android.position="actionBar"
      />
    </ActionBar>
    
    <StackLayout>
      <Label text="欢迎回来！" class="title" />
      <Label :text="`用户: ${user?.username}`" class="info" />
      
      <Button
        text="设备列表"
        @tap="() => navigateTo(DeviceListPage)"
        class="menu-item"
      />
      
      <Button
        text="告警列表"
        @tap="() => navigateTo(AlarmListPage)"
        class="menu-item"
      />
    </StackLayout>
  </Page>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '../stores/authStore';
import { navigateTo } from '@nativescript/vue';
import LoginPage from './LoginPage.vue';
// import DeviceListPage from './DeviceListPage.vue';
// import AlarmListPage from './AlarmListPage.vue';

const authStore = useAuthStore();
const user = computed(() => authStore.user);

async function handleLogout() {
  const result = await confirm({
    title: '确认退出',
    message: '确定要退出登录吗？',
    okButtonText: '确定',
    cancelButtonText: '取消'
  });

  if (result) {
    await authStore.logout();
    navigateTo(LoginPage, { clearHistory: true });
  }
}
</script>

<style scoped>
.title {
  font-size: 24;
  font-weight: bold;
  text-align: center;
  margin: 30 0;
}

.info {
  font-size: 16;
  text-align: center;
  margin-bottom: 20;
  color: #666;
}

.menu-item {
  font-size: 16;
  margin: 10 20;
  padding: 15;
  background-color: #1890ff;
  color: white;
  border-radius: 5;
}
</style>
```

### 步骤 5: 配置主应用入口

`mobile/app/app.ts`:

```typescript
import { createApp } from '@nativescript/vue';
import { createPinia } from 'pinia';
import LoginPage from './pages/LoginPage.vue';

const pinia = createPinia();

const app = createApp(LoginPage);
app.use(pinia);

app.start();
```

---

## 🧪 Phase 3: 测试运行

### Android 测试

```bash
# 在 mobile 目录下
cd mobile

# 安装依赖
pnpm install

# 运行 Android
pnpm android
```

**验证点**:
- ✅ 应用成功编译
- ✅ 登录页面正常显示
- ✅ 可以输入用户名密码
- ✅ 点击登录按钮能调用后端 API
- ✅ 登录成功后跳转到首页

### iOS 测试（macOS）

```bash
# 运行 iOS
pnpm ios
```

---

## 📝 Phase 4: 开发规范

### 文件命名规范

```
Pages: PascalCase + Page 后缀（LoginPage.vue）
Components: PascalCase（UserCard.vue）
Stores: camelCase + Store 后缀（authStore.ts）
Services: camelCase + Service 后缀（apiService.ts）
```

### 代码组织规范

```
mobile/app/
├── pages/           # 页面组件
├── components/      # 可复用组件
├── stores/          # Pinia stores
├── services/        # 业务服务层
├── navigation/      # 导航配置
├── plugins/         # 原生插件封装
├── assets/          # 静态资源
└── styles/          # 全局样式
```

### Git 提交规范

```bash
feat(mobile): 添加登录页面
fix(mobile): 修复 Android 返回键问题
docs(mobile): 更新集成指南
```

---

## 🔒 安全配置

### Token 存储

使用 `@nativescript/secure-storage` 替代 ApplicationSettings:

```typescript
import { SecureStorage } from '@nativescript/secure-storage';

const secureStorage = new SecureStorage();

export const setToken = (token: string): Promise<boolean> => {
  return secureStorage.set({
    key: 'access_token',
    value: token
  });
};

export const getToken = (): Promise<string> => {
  return secureStorage.get({ key: 'access_token' });
};
```

### HTTPS 配置

生产环境强制 HTTPS，配置证书验证。

---

## 📊 里程碑

| 阶段 | 目标 | 预计时间 | 状态 |
|------|------|---------|------|
| Phase 0 | 环境准备 | 1天 | ⏳ 进行中 |
| Phase 1 | 项目初始化 | 1天 | 🔲 待开始 |
| Phase 2 | Shared 连接 | 1天 | 🔲 待开始 |
| Phase 3 | 登录功能 | 1天 | 🔲 待开始 |
| Phase 4 | MVP 页面 | 3-5天 | 🔲 待开始 |
| Phase 5 | 功能完善 | 1周+ | 🔲 待开始 |

---

## 🎯 下一步行动

### 立即执行

1. **安装 NativeScript CLI**
   ```bash
   npm install -g @nativescript/core
   ns doctor android
   ```

2. **验证环境**
   ```bash
   ns create test-app --vue --ts
   cd test-app
   ns run android
   ```

3. **确认成功后**，返回主项目开始正式集成

---

**准备好开始了吗？** 🚀

