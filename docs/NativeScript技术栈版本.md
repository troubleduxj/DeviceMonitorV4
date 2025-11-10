# NativeScript 技术栈版本清单

> 📦 DeviceMonitor Mobile 端技术栈与版本锁定

**更新日期**: 2025-10-25  
**NativeScript 版本**: 8.5.0  
**Vue 版本**: 3.x

---

## 🎯 核心框架

| 包名 | 版本 | 说明 |
|------|------|------|
| `@nativescript/core` | `~8.5.0` | NativeScript 核心框架 |
| `@nativescript/vue` | `^2.0.0` | Vue 3 集成（官方） |
| `vue` | `^3.3.0` | Vue 3 核心 |
| `typescript` | `~5.0.0` | TypeScript 支持 |
| `pinia` | `^2.1.0` | 状态管理（与 Web 统一） |

---

## 📱 原生功能插件

### 核心功能

| 插件 | 版本 | 用途 | 优先级 |
|------|------|------|--------|
| `@nativescript/secure-storage` | `latest` | Token 安全存储 | 🔴 高 |
| `@nativescript/local-notifications` | `latest` | 本地通知 | 🟡 中 |
| `@nativescript/geolocation` | `latest` | 地理位置 | 🟡 中 |

### 设备管理功能

| 插件 | 版本 | 用途 | 优先级 |
|------|------|------|--------|
| `nativescript-barcodescanner` | `latest` | 二维码扫描（设备巡检） | 🔴 高 |
| `@nativescript/camera` | `latest` | 相机拍照（维修记录） | 🟡 中 |
| `@nativescript/bluetooth` | `latest` | 蓝牙连接（可选） | 🟢 低 |

### 网络与通信

| 插件 | 版本 | 用途 | 优先级 |
|------|------|------|--------|
| 内置 `fetch` | - | HTTP 请求（Shared 层使用） | 🔴 高 |
| 内置 `WebSocket` | - | 实时告警推送 | 🟡 中 |

### UI 增强

| 插件 | 版本 | 用途 | 优先级 |
|------|------|------|--------|
| `@nativescript/datetimepicker` | `latest` | 日期时间选择器 | 🟡 中 |
| `nativescript-ui-charts` | `latest` | 图表展示（可选） | 🟢 低 |

---

## 🛠️ 开发工具

### 必需工具

| 工具 | 版本 | 说明 |
|------|------|------|
| Node.js | `18.x` | 推荐使用 LTS 版本 |
| pnpm | `8.x` | 包管理器（Monorepo） |
| @nativescript/cli | `latest` | NS 命令行工具 |

### 平台工具

#### Android 开发

| 工具 | 版本 | 说明 |
|------|------|------|
| Android Studio | `最新稳定版` | IDE + SDK 管理 |
| Android SDK | `30+` | 最低支持 Android 11 |
| Gradle | `7.x+` | 构建工具（AS 内置） |
| JDK | `11 或 17` | Java 开发工具包 |

#### iOS 开发（仅 macOS）

| 工具 | 版本 | 说明 |
|------|------|------|
| Xcode | `14+` | IDE + SDK 管理 |
| iOS SDK | `15+` | 最低支持 iOS 15 |
| CocoaPods | `1.11+` | iOS 依赖管理 |

---

## 📦 构建与打包

### Webpack 配置

| 包名 | 版本 | 说明 |
|------|------|------|
| `@nativescript/webpack` | `~5.0.0` | NS 专用 Webpack 配置 |
| `webpack` | `~5.x` | 打包工具 |

### TypeScript 配置

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "Node",
    "lib": ["ES2020"],
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "skipLibCheck": true
  }
}
```

---

## 🔗 与 Shared 层集成

### Shared 层依赖

| 包名 | 版本 | 说明 |
|------|------|------|
| `@device-monitor/shared` | `workspace:*` | 共享业务层 |
| `ofetch` 或内置 `fetch` | - | HTTP 客户端（跨端） |

### Path Alias 配置

```json
{
  "paths": {
    "@/*": ["app/*"],
    "@shared/*": ["../packages/shared/*"]
  }
}
```

---

## 🌐 环境配置

### API 地址

```typescript
// 开发环境
const DEV_API = {
  android: 'http://10.0.2.2:8000/api/v2',  // Android 模拟器访问宿主机
  ios: 'http://localhost:8000/api/v2',      // iOS 模拟器
};

// 生产环境
const PROD_API = 'https://your-domain.com/api/v2';
```

### 平台差异处理

```typescript
import { isAndroid, isIOS } from '@nativescript/core';

const BASE_URL = __DEV__
  ? (isAndroid ? 'http://10.0.2.2:8000' : 'http://localhost:8000')
  : 'https://your-domain.com';
```

---

## 📋 安装清单

### Step 1: 安装 NativeScript CLI

```bash
# 全局安装
npm install -g @nativescript/core

# 验证
ns --version
```

### Step 2: 检查环境

```bash
# Android 环境检查
ns doctor android

# iOS 环境检查（macOS）
ns doctor ios
```

**预期输出**:
```
✔ Getting environment information
✔ Your ANDROID_HOME environment variable is set and points to correct directory.
✔ The Android SDK is installed.
✔ A compatible Android SDK for compilation is found.
✔ Javac is installed and is configured properly.
✔ The Java Development Kit (JDK) is installed and is configured properly.
✔ Local builds for iOS can be executed only on a macOS system. (仅适用于 iOS)
```

### Step 3: 创建测试项目（验证）

```bash
# 在项目外创建测试项目
cd ..
ns create ns-test --vue --ts

# 进入并运行
cd ns-test
ns run android  # 或 ns run ios
```

---

## 🚨 已知问题与解决方案

### Android 模拟器网络访问

**问题**: 模拟器无法访问 `localhost`  
**解决**: 使用 `10.0.2.2` 代替 `localhost`

```typescript
const baseURL = isAndroid && __DEV__
  ? 'http://10.0.2.2:8000/api/v2'
  : 'http://localhost:8000/api/v2';
```

### iOS 模拟器 HTTPS 证书

**问题**: 自签名证书不受信任  
**解决**: 开发环境使用 HTTP，生产环境强制 HTTPS

### Webpack 构建慢

**问题**: 首次构建时间长  
**解决**: 使用 Webpack cache 和增量构建

```javascript
// webpack.config.js
module.exports = (env) => {
  return {
    cache: {
      type: 'filesystem',
    },
    // ...
  };
};
```

---

## 📚 参考文档

- [NativeScript 官方文档](https://docs.nativescript.org/)
- [NativeScript-Vue 文档](https://nativescript-vue.org/)
- [NativeScript 插件市场](https://market.nativescript.org/)
- [Android 开发环境配置](https://docs.nativescript.org/environment-setup.html#android)
- [iOS 开发环境配置](https://docs.nativescript.org/environment-setup.html#ios)

---

## ✅ 环境验证检查清单

在开始正式开发前，请确认以下项目：

- [ ] Node.js 18.x 已安装
- [ ] pnpm 8.x 已安装
- [ ] @nativescript/cli 已全局安装
- [ ] `ns doctor android` 通过（Android 开发）
- [ ] `ns doctor ios` 通过（iOS 开发，macOS）
- [ ] Android Studio 已安装并配置 SDK
- [ ] Xcode 已安装（macOS，iOS 开发）
- [ ] 测试项目 `ns-test` 可以成功运行
- [ ] Android 模拟器或真机可用
- [ ] iOS 模拟器或真机可用（macOS）

**全部通过后，即可开始正式集成！** 🎉

---

**下一步**: 阅读 `NativeScript-Vue集成实施指南.md` 开始 Phase 1

