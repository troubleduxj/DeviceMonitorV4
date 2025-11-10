# 移动端 PC 调试指南

> **DeviceMonitor Mobile - NativeScript Vue 3**  
> 在 PC 端查看、测试和调试移动端程序的完整指南

---

## 🎯 概述

NativeScript 是**原生移动应用**框架，需要在移动设备或模拟器上运行。但我们可以通过以下方式在 PC 上进行开发和调试：

---

## ✅ 方案一：Android 模拟器（推荐 - Windows/Mac/Linux 可用）

### 1. 安装 Android Studio

**下载地址**: https://developer.android.com/studio

**安装步骤**:
```powershell
# 1. 下载并安装 Android Studio
# 2. 运行 Android Studio
# 3. 打开 SDK Manager (Settings → Appearance & Behavior → System Settings → Android SDK)
# 4. 安装以下组件：
#    - Android SDK Platform (API 33 或更高)
#    - Android SDK Build-Tools
#    - Android SDK Platform-Tools
#    - Android Emulator
#    - Intel x86 Emulator Accelerator (HAXM installer) - Intel CPU
#    或 Android Emulator Hypervisor Driver - AMD CPU
```

### 2. 创建 Android 虚拟设备 (AVD)

**步骤**:
1. 打开 Android Studio
2. 点击 **Tools** → **AVD Manager**
3. 点击 **Create Virtual Device**
4. 选择设备型号（推荐 Pixel 5 或 Pixel 6）
5. 选择系统镜像（推荐 API 33 - Android 13）
6. 配置 AVD 设置：
   - RAM: 至少 2GB
   - 启用 Hardware - GLES 2.0
   - 启用 Multi-Core CPU
7. 点击 **Finish**

### 3. 配置环境变量

**Windows PowerShell**:
```powershell
# 添加到系统环境变量
$env:ANDROID_HOME = "C:\Users\你的用户名\AppData\Local\Android\Sdk"
$env:Path += ";$env:ANDROID_HOME\platform-tools"
$env:Path += ";$env:ANDROID_HOME\emulator"
$env:Path += ";$env:ANDROID_HOME\tools"
$env:Path += ";$env:ANDROID_HOME\tools\bin"

# 验证安装
adb --version
```

**永久设置**（系统环境变量）:
1. 右键 **此电脑** → **属性** → **高级系统设置**
2. 点击 **环境变量**
3. 在 **系统变量** 中添加：
   - 变量名: `ANDROID_HOME`
   - 变量值: `C:\Users\你的用户名\AppData\Local\Android\Sdk`
4. 编辑 `Path` 变量，添加：
   - `%ANDROID_HOME%\platform-tools`
   - `%ANDROID_HOME%\emulator`
   - `%ANDROID_HOME%\tools`

### 4. 运行移动端应用

**启动模拟器**:
```powershell
# 方法1：通过 Android Studio 启动
# AVD Manager → 点击绿色播放按钮

# 方法2：通过命令行启动
emulator -list-avds  # 查看可用的 AVD
emulator -avd Pixel_5_API_33  # 启动指定的 AVD
```

**运行应用**:
```powershell
# 在项目根目录
cd mobile

# 确保模拟器已启动
adb devices

# 运行应用（会自动检测模拟器）
pnpm android

# 或使用 NativeScript CLI
ns run android
```

### 5. 热重载开发

NativeScript 支持**热重载** (Hot Module Replacement)：

```powershell
# 开发模式（文件修改后自动刷新）
pnpm android

# 应用会自动监听文件变化
# 修改 .vue、.ts 文件后，应用会自动更新
```

---

## ✅ 方案二：真机调试（推荐用于性能测试）

### 1. 启用开发者选项

**Android 设备**:
1. 进入 **设置** → **关于手机**
2. 连续点击 **版本号** 7 次
3. 返回设置，找到 **开发者选项**
4. 启用 **USB 调试**
5. 启用 **USB 安装**（某些设备需要）

### 2. 连接设备

```powershell
# 用 USB 线连接手机和电脑
# 手机上会弹出 USB 调试授权提示，点击允许

# 验证连接
adb devices
# 输出示例：
# List of devices attached
# ABC123456789    device
```

### 3. 运行应用

```powershell
cd mobile
pnpm android

# 应用会自动安装到真机
```

---

## 🔧 方案三：Chrome DevTools 调试

### Android 应用调试

**启动调试**:
```powershell
# 1. 运行应用（模拟器或真机）
cd mobile
pnpm android

# 2. 打开 Chrome 浏览器
# 3. 访问: chrome://inspect
# 4. 找到你的应用并点击 "inspect"
```

**调试功能**:
- ✅ Console 日志查看
- ✅ 网络请求监控
- ✅ 性能分析
- ✅ 断点调试
- ✅ DOM 检查（有限支持）

### Vue DevTools

NativeScript 不支持传统的 Vue DevTools，但可以使用：

```typescript
// 在代码中添加日志
console.log('User data:', this.user);
console.table(this.items);
console.dir(this.complexObject);
```

---

## 🖥️ 方案四：NativeScript Preview（有限支持）

### NativeScript Preview App

**优点**: 无需配置 Android Studio  
**缺点**: 不支持自定义原生插件，功能受限

```powershell
# 1. 在手机上安装 NativeScript Preview
# Google Play: https://play.google.com/store/apps/details?id=org.nativescript.preview

# 2. 安装 NativeScript Preview CLI（全局）
npm install -g nativescript

# 3. 运行预览
cd mobile
ns preview

# 4. 扫描二维码在手机上预览
```

⚠️ **注意**: 此方案对我们的项目支持有限，因为我们使用了自定义配置。

---

## 🛠️ 方案五：VS Code 调试配置

### 配置 launch.json

创建 `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch on Android",
      "type": "nativescript",
      "request": "launch",
      "platform": "android",
      "appRoot": "${workspaceFolder}/mobile",
      "sourceMaps": true,
      "watch": true
    },
    {
      "name": "Attach on Android",
      "type": "nativescript",
      "request": "attach",
      "platform": "android",
      "appRoot": "${workspaceFolder}/mobile",
      "sourceMaps": true
    }
  ]
}
```

### 安装 VS Code 扩展

```
NativeScript Extension Pack
```

包含：
- NativeScript
- NativeScript XML Snippets
- Angular/TypeScript/JavaScript 支持

---

## 📊 各方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **Android 模拟器** | ✅ 完整功能<br>✅ 热重载<br>✅ 接近真实环境 | ⚠️ 需要配置<br>⚠️ 占用资源 | ⭐⭐⭐⭐⭐ |
| **真机调试** | ✅ 真实性能<br>✅ 传感器支持<br>✅ 快速响应 | ⚠️ 需要物理设备<br>⚠️ USB 线连接 | ⭐⭐⭐⭐⭐ |
| **Chrome DevTools** | ✅ 强大调试功能<br>✅ 网络监控<br>✅ 性能分析 | ℹ️ 需配合模拟器/真机 | ⭐⭐⭐⭐⭐ |
| **Preview App** | ✅ 快速预览<br>✅ 无需配置 | ❌ 功能受限<br>❌ 不支持插件 | ⭐⭐ |
| **VS Code 调试** | ✅ IDE 集成<br>✅ 断点调试 | ℹ️ 需配合模拟器/真机 | ⭐⭐⭐⭐ |

---

## 🚀 推荐开发流程

### 日常开发（推荐）

```powershell
# 1. 启动 Android 模拟器
# 通过 Android Studio AVD Manager 启动

# 2. 运行应用（热重载模式）
cd mobile
pnpm android

# 3. 编辑代码
# 在 VS Code 中修改 .vue、.ts 文件
# 应用会自动刷新

# 4. 查看日志
# 终端中会显示 console.log 输出
# 或使用 Chrome DevTools (chrome://inspect)
```

### 功能测试

```powershell
# 1. 在真机上测试性能和用户体验
adb devices
cd mobile
pnpm android

# 2. 测试不同屏幕尺寸
# 使用不同的 AVD（Pixel 5, Pixel 6, Tablet）
```

### 调试问题

```powershell
# 1. 查看详细日志
adb logcat

# 2. 清理缓存重新运行
cd mobile
pnpm clean
pnpm android

# 3. 使用 Chrome DevTools 断点调试
# chrome://inspect → inspect → Sources 面板
```

---

## ❌ 不能做的事情

### 不支持浏览器预览

NativeScript 应用**不能在浏览器中运行**，因为：
- ❌ 使用原生 API（不是 Web API）
- ❌ UI 组件是原生控件（不是 HTML/CSS）
- ❌ 需要原生运行时环境

### 与 Web 项目的区别

| 特性 | Web (浏览器) | Mobile (NativeScript) |
|------|-------------|----------------------|
| 预览方式 | `npm run dev` → 浏览器 | 模拟器 / 真机 |
| UI 组件 | HTML 元素 | 原生组件 (Label, Button) |
| 样式系统 | CSS | CSS 子集 + 原生样式 |
| API | Web API | 原生 API |
| 调试工具 | 浏览器 DevTools | Chrome DevTools + ADB |

---

## 🎯 快速开始步骤（Windows）

### 首次设置（约30-60分钟）

```powershell
# 1. 安装 Android Studio
# 下载: https://developer.android.com/studio

# 2. 安装 Android SDK 组件
# 打开 Android Studio → SDK Manager
# 安装 Android SDK Platform-Tools, Build-Tools, Emulator

# 3. 创建 AVD
# AVD Manager → Create Virtual Device → Pixel 5 → API 33

# 4. 配置环境变量
# ANDROID_HOME = C:\Users\你的用户名\AppData\Local\Android\Sdk
# Path += %ANDROID_HOME%\platform-tools

# 5. 验证配置
adb --version
```

### 运行应用（2分钟）

```powershell
# 1. 启动模拟器
# Android Studio → AVD Manager → 启动

# 2. 运行应用
cd mobile
pnpm install  # 首次运行
pnpm android  # 启动应用

# 3. 等待构建和安装（首次较慢，约2-5分钟）
# 后续热重载很快（1-3秒）
```

---

## 🆘 常见问题

### Q1: 模拟器启动失败

**解决方案**:
```powershell
# 检查 HAXM/Hypervisor 是否启用
# Intel CPU: 安装 HAXM
# AMD CPU: 启用 Windows Hypervisor Platform

# 检查 BIOS 虚拟化是否启用
# 重启电脑 → 进入 BIOS → 启用 VT-x/AMD-V
```

### Q2: adb devices 找不到设备

**解决方案**:
```powershell
# 重启 ADB 服务
adb kill-server
adb start-server
adb devices
```

### Q3: 构建失败

**解决方案**:
```powershell
# 清理缓存
cd mobile
pnpm clean
rm -rf platforms
rm -rf node_modules
pnpm install
pnpm android
```

### Q4: 应用崩溃

**解决方案**:
```powershell
# 查看崩溃日志
adb logcat | Select-String "DeviceMonitor"

# 或查看所有日志
adb logcat
```

---

## 📚 相关资源

### 官方文档
- [NativeScript 文档](https://docs.nativescript.org/)
- [Android Studio 文档](https://developer.android.com/studio/intro)
- [ADB 文档](https://developer.android.com/studio/command-line/adb)

### 视频教程
- [NativeScript 入门](https://www.youtube.com/results?search_query=nativescript+tutorial)
- [Android 模拟器设置](https://www.youtube.com/results?search_query=android+emulator+setup)

---

## ✅ 总结

**PC 端调试移动端应用的最佳实践**:

1. **开发阶段**: Android 模拟器 + 热重载
2. **功能测试**: 真机测试
3. **问题调试**: Chrome DevTools + ADB Logcat
4. **性能优化**: 真机性能分析

**关键点**:
- ✅ 需要 Android Studio 和 Android SDK
- ✅ 必须在模拟器或真机上运行（不能在浏览器）
- ✅ 支持热重载，开发体验良好
- ✅ 可以使用 Chrome DevTools 调试
- ✅ VS Code 提供完整的开发支持

**开始开发前的检查清单**:
- [ ] Android Studio 已安装
- [ ] Android SDK 已配置
- [ ] 环境变量已设置（ANDROID_HOME）
- [ ] AVD 已创建
- [ ] adb 命令可用
- [ ] 项目依赖已安装（pnpm install）

准备好后，就可以开始愉快的移动端开发了！🚀

