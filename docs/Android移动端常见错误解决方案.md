# Android 移动端常见错误解决方案

> **DeviceMonitor Mobile - 问题排查指南**  
> 记录移动端启动和运行过程中的常见错误及解决方案

---

## 🐛 错误 1：npm 代理连接失败

### 错误信息
```
npm error code ECONNREFUSED
npm error syscall connect
npm error errno ECONNREFUSED
npm error FetchError: request to https://registry.npmmirror.com/@nativescript%2fandroid failed, 
reason: connect ECONNREFUSED 127.0.0.1:7890
```

### 原因分析
- npm 配置了代理（通常是 Clash/V2Ray），但代理服务未运行
- 端口 `127.0.0.1:7890` 无法连接

### 解决方案

#### 方案 A：清除代理配置（推荐）
```powershell
# 1. 检查当前代理配置
npm config get proxy
npm config get https-proxy

# 2. 删除代理配置
npm config delete proxy
npm config delete https-proxy

# 3. 验证已清除
npm config get proxy  # 应该返回 null
```

#### 方案 B：启动代理服务
如果您需要使用代理：
```powershell
# 1. 启动 Clash/V2Ray 等代理工具
# 2. 确保运行在 7890 端口
# 3. 重新运行应用
pnpm android
```

#### 方案 C：临时禁用代理
```powershell
# 只在当前会话中禁用
$env:HTTP_PROXY=""
$env:HTTPS_PROXY=""
pnpm android
```

---

## 🐛 错误 2：Node.js 模块导出错误（entities）

### 错误信息
```
Error [ERR_PACKAGE_PATH_NOT_EXPORTED]: Package subpath './decode' is not defined by "exports" 
in D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\node_modules\.pnpm\node_modules\entities\package.json
```

### 原因分析
- Node.js v22 版本太新，与某些 webpack 依赖不兼容
- `entities` 包的导出配置与新版本 Node.js 冲突
- 推荐使用 Node.js 18 LTS 或 20 LTS

### 解决方案

#### 方案 A：配置依赖覆盖（推荐 - 已应用）✅

在**根目录** `package.json` 中添加：
```json
{
  "pnpm": {
    "overrides": {
      "entities": "^4.5.0"
    }
  }
}
```

然后重新安装：
```powershell
# 在项目根目录
pnpm install

# 运行应用
cd mobile
pnpm android
```

#### 方案 B：使用 nvm-windows 切换 Node.js 版本（推荐生产环境）

**安装 nvm-windows：**
1. 下载：https://github.com/coreybutler/nvm-windows/releases
2. 安装 `nvm-setup.exe`

**切换到 Node.js 20 LTS：**
```powershell
# 查看已安装的版本
nvm list

# 安装 Node.js 20 LTS
nvm install 20.18.1

# 切换到 Node.js 20
nvm use 20.18.1

# 验证版本
node --version
# 应该显示: v20.18.1

# 重新安装依赖
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2
Remove-Item -Recurse -Force mobile\node_modules
pnpm install

# 运行应用
cd mobile
pnpm android
```

#### 方案 C：使用 Node.js 18 LTS
```powershell
# 安装 Node.js 18
nvm install 18.20.5
nvm use 18.20.5

# 重新安装依赖
pnpm install
cd mobile
pnpm android
```

### 推荐的 Node.js 版本

| 版本 | 兼容性 | 推荐度 | 说明 |
|------|--------|--------|------|
| **Node.js 20 LTS** | ✅ 完全兼容 | ⭐⭐⭐⭐⭐ | 最新 LTS，推荐 |
| **Node.js 18 LTS** | ✅ 完全兼容 | ⭐⭐⭐⭐⭐ | 稳定可靠 |
| Node.js 22 | ⚠️ 部分兼容 | ⭐⭐ | 需要配置 overrides |
| Node.js 16 | ⚠️ 不推荐 | ⭐ | 即将停止维护 |

---

## 🐛 错误 3：NativeScript Android 平台未安装

### 错误信息
```
Command npm.cmd failed with exit code 1
× Component @nativescript/android is not installed.
```

### 原因分析
- 缺少 `@nativescript/android` 包
- 这是 Android 构建的核心依赖

### 解决方案

```powershell
# 切换到 mobile 目录
cd mobile

# 安装 Android 平台组件
pnpm add @nativescript/android

# 验证安装
npx ns doctor
# 应该显示: √ Component @nativescript/android is installed
```

### 同时安装 iOS 平台（仅 macOS）
```bash
# 如果在 macOS 上开发
pnpm add @nativescript/ios
```

---

## 🐛 错误 4：找不到设备

### 错误信息
```
Searching for devices...
Error: Cannot find connected devices.
```

### 原因分析
- 没有连接的 Android 设备或模拟器
- ADB 服务未启动

### 解决方案

#### 方案 A：启动 Android 模拟器
```powershell
# 1. 打开 Android Studio
# 2. 点击 Device Manager（右侧工具栏）
# 3. 点击 AVD 旁边的 ▶️ 播放按钮

# 4. 验证设备连接
adb devices
# 应该显示: emulator-5554    device
```

#### 方案 B：连接真机
```powershell
# 1. 启用开发者选项
#    设置 → 关于手机 → 连续点击版本号 7 次

# 2. 启用 USB 调试
#    设置 → 开发者选项 → USB 调试

# 3. 用 USB 线连接手机
# 4. 手机上允许 USB 调试授权

# 5. 验证连接
adb devices
```

#### 方案 C：重启 ADB 服务
```powershell
adb kill-server
adb start-server
adb devices
```

---

## 🐛 错误 5：ANDROID_HOME 未设置

### 错误信息
```
Your ANDROID_HOME environment variable is not set or not set properly.
```

### 原因分析
- 环境变量 `ANDROID_HOME` 未配置
- 或者路径配置错误

### 解决方案

#### 方案 A：图形界面设置（永久）

**步骤：**
1. 右键 "此电脑" → 属性
2. 高级系统设置 → 环境变量
3. 在"系统变量"中点击"新建"：
   ```
   变量名: ANDROID_HOME
   变量值: C:\Users\你的用户名\AppData\Local\Android\Sdk
   ```
4. 编辑 Path 变量，添加：
   ```
   %ANDROID_HOME%\platform-tools
   %ANDROID_HOME%\emulator
   %ANDROID_HOME%\tools
   %ANDROID_HOME%\tools\bin
   ```
5. 点击"确定"保存
6. **重启 PowerShell**

#### 方案 B：PowerShell 设置（临时）
```powershell
# 临时设置（仅当前会话）
$env:ANDROID_HOME = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
$env:Path += ";$env:ANDROID_HOME\platform-tools"
$env:Path += ";$env:ANDROID_HOME\emulator"

# 验证
Write-Host $env:ANDROID_HOME
adb --version
```

#### 方案 C：PowerShell 永久设置（管理员权限）
```powershell
# 以管理员身份运行 PowerShell

# 设置系统环境变量
$androidHome = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidHome, 'Machine')

# 获取当前 Path
$path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')

# 添加 Android 路径
$newPath = "$path;$androidHome\platform-tools;$androidHome\emulator;$androidHome\tools;$androidHome\tools\bin"
[System.Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine')

Write-Host "环境变量配置完成！请重启 PowerShell" -ForegroundColor Green
```

---

## 🐛 错误 6：Gradle 构建失败

### 错误信息
```
FAILURE: Build failed with an exception.
```

### 原因分析
- Gradle 缓存损坏
- 依赖下载失败
- 构建配置错误

### 解决方案

#### 方案 A：清理缓存
```powershell
cd mobile

# 清理 NativeScript 缓存
pnpm clean

# 删除平台文件夹
Remove-Item -Recurse -Force platforms -ErrorAction SilentlyContinue

# 重新运行
pnpm android
```

#### 方案 B：清理 Gradle 缓存
```powershell
# 清理 Gradle 缓存（Windows）
Remove-Item -Recurse -Force $env:USERPROFILE\.gradle\caches -ErrorAction SilentlyContinue

# 重新构建
cd mobile
pnpm android
```

#### 方案 C：更新依赖
```powershell
cd mobile

# 删除 node_modules
Remove-Item -Recurse -Force node_modules

# 重新安装
pnpm install

# 运行
pnpm android
```

---

## 🐛 错误 7：端口占用

### 错误信息
```
Port 8081 is already in use
```

### 原因分析
- Metro bundler 端口被占用
- 之前的进程未正常关闭

### 解决方案

```powershell
# 查找占用端口的进程
netstat -ano | findstr :8081

# 结束进程（替换 <PID> 为实际进程 ID）
taskkill /PID <PID> /F

# 或者一键结束 Node 进程
taskkill /IM node.exe /F

# 重新运行
pnpm android
```

---

## 🐛 错误 8：应用崩溃

### 错误信息
```
Application has stopped
```

### 原因分析
- 代码错误
- 原生模块问题
- 内存不足

### 解决方案

#### 查看崩溃日志
```powershell
# 实时日志
adb logcat

# 过滤应用日志
adb logcat | Select-String "DeviceMonitor"

# 查看崩溃日志
adb logcat -b crash

# 导出日志到文件
adb logcat -d > crash_log.txt
```

#### 清理重装
```powershell
cd mobile

# 卸载应用
adb uninstall org.nativescript.preview

# 清理缓存
pnpm clean

# 重新安装
pnpm android
```

---

## 🐛 错误 9：npm 警告信息

### 错误信息
```
npm warn Unknown env config "verify-deps-before-run"
npm warn Unknown env config "_jsr-registry"
```

### 原因分析
- npm 配置了不存在或废弃的配置项
- 通常不影响构建，但会显示警告

### 解决方案

```powershell
# 查看所有 npm 配置
npm config list

# 删除未知配置项
npm config delete verify-deps-before-run
npm config delete _jsr-registry

# 或者重置所有配置
npm config edit
# 删除不需要的配置项，保存并退出
```

---

## 🔍 完整诊断流程

遇到问题时，按以下顺序排查：

### 1️⃣ 环境检查
```powershell
# 运行诊断工具
cd mobile
npx ns doctor

# 应该全部显示 √
√ Your ANDROID_HOME environment variable is set
√ Your adb from the Android SDK is correctly installed
√ The Android SDK is installed
√ A compatible Android SDK for compilation is found
√ Javac is installed and is configured properly
√ The Java Development Kit (JDK) is installed
√ Component @nativescript/android is installed
```

### 2️⃣ 设备检查
```powershell
# 检查设备连接
adb devices

# 应该显示至少一个设备
# List of devices attached
# emulator-5554    device
```

### 3️⃣ 网络检查
```powershell
# 检查代理配置
npm config get proxy
npm config get https-proxy

# 如果有代理但不需要，删除
npm config delete proxy
npm config delete https-proxy
```

### 4️⃣ 清理重试
```powershell
cd mobile

# 清理缓存
pnpm clean

# 删除构建文件
Remove-Item -Recurse -Force platforms -ErrorAction SilentlyContinue

# 重新运行
pnpm android
```

---

## ❌ 错误 #10: `readable-stream/passthrough` 模块找不到

### 错误信息
```
Error: Cannot find module 'readable-stream/passthrough'
Require stack:
- lazystream\lib\lazystream.js
- archiver-utils\index.js
- archiver\lib\core.js
```

### 错误原因
- `readable-stream` 新版本（v4.x）改变了导出方式
- `lazystream` 和 `archiver-utils` 依赖旧的子路径导出
- 这与 `entities` 问题类似，是导出路径变更导致的

### 解决方案

#### 方法 1：添加 `readable-stream` 降级（推荐）
```powershell
# 编辑根目录的 package.json
```

**添加到 `pnpm.overrides`：**
```json
{
  "pnpm": {
    "overrides": {
      "readable-stream": "^3.6.2"
    }
  }
}
```

#### 方法 2：完整清理和重装
```powershell
# 清理所有依赖
Remove-Item -Recurse -Force node_modules
Remove-Item -Recurse -Force mobile\node_modules
Remove-Item -Force pnpm-lock.yaml

# 清理 pnpm 缓存
pnpm store prune

# 重新安装
pnpm install

# 验证
cd mobile
pnpm android
```

### 说明
- `readable-stream` 是 Node.js 核心 stream 模块的兼容性包
- 版本 3.6.2 支持传统的子路径导出（如 `/passthrough`）
- 版本 4.x 改用了新的 ES Module 导出方式

---

## 📊 快速问题定位表

| 错误特征 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `ECONNREFUSED` | 代理配置问题 | 删除 npm 代理配置 |
| `@nativescript/android is not installed` | 缺少平台包 | `pnpm add @nativescript/android` |
| `Cannot find module 'readable-stream/passthrough'` | 导出路径变更 | 添加 `pnpm.overrides` 降级 `readable-stream` |
| `Cannot find connected devices` | 无设备连接 | 启动模拟器或连接真机 |
| `ANDROID_HOME not set` | 环境变量未配置 | 设置 ANDROID_HOME 环境变量 |
| `Build failed` | 构建错误 | 清理缓存 + 重新构建 |
| `Port already in use` | 端口占用 | 结束占用端口的进程 |
| `Application crashed` | 应用崩溃 | 查看 logcat 日志 |

---

## 🆘 获取帮助

如果上述方案都无法解决问题：

1. **查看详细日志**
   ```powershell
   adb logcat > full_log.txt
   ```

2. **运行完整诊断**
   ```powershell
   npx ns doctor
   ```

3. **查看构建日志**
   - 检查终端输出的完整错误堆栈
   - 保存错误信息以便排查

4. **参考官方文档**
   - [NativeScript 文档](https://docs.nativescript.org/)
   - [Android 开发文档](https://developer.android.com/)

---

## ✅ 成功启动检查清单

应用成功启动后，应该看到：

- [ ] 终端显示：`Successfully synced application`
- [ ] 模拟器中应用自动打开
- [ ] 应用界面正常显示
- [ ] 控制台无错误日志
- [ ] 可以进行操作和交互

---

**最后更新**: 2025-10-25  
**适用版本**: NativeScript 8.9.x, Android SDK 33+

