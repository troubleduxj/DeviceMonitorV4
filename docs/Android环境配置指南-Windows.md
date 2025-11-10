# Android 环境配置指南 (Windows)

> **DeviceMonitor Mobile - Android 开发环境配置**  
> 解决 "ANDROID_HOME is not set" 错误

---

## 🎯 目标

配置 Android 开发环境，使 NativeScript 能够构建和运行 Android 应用。

---

## 📋 步骤清单

- [ ] 安装 Android Studio
- [ ] 安装 Android SDK
- [ ] 配置环境变量
- [ ] 创建虚拟设备
- [ ] 验证配置

---

## 1️⃣ 安装 Android Studio

### 下载

**官方网站**: https://developer.android.com/studio

**直接下载链接**:
- Windows: https://redirector.gvt1.com/edgedl/android/studio/install/2024.1.1.12/android-studio-2024.1.1.12-windows.exe

### 安装步骤

1. **运行安装程序**
   - 双击下载的 `.exe` 文件
   
2. **选择组件**
   - ✅ Android Studio
   - ✅ Android SDK
   - ✅ Android Virtual Device

3. **选择安装位置**
   - 默认: `C:\Program Files\Android\Android Studio`
   - 建议使用默认位置

4. **完成安装**
   - 点击 Next → Install → Finish

---

## 2️⃣ 首次启动 Android Studio

### 初始配置向导

1. **启动 Android Studio**

2. **选择设置导入**
   - 选择 "Do not import settings"
   - 点击 OK

3. **数据共享**
   - 选择 "Don't send"（可选）

4. **安装类型**
   - 选择 **"Standard"** (推荐)
   - 点击 Next

5. **选择主题**
   - Light 或 Dark（随意选择）
   - 点击 Next

6. **SDK 组件**
   - 会显示将要下载的组件清单
   - ✅ Android SDK
   - ✅ Android SDK Platform
   - ✅ Performance (Intel ® HAXM)
   - ✅ Android Virtual Device
   - 点击 Next

7. **下载组件**
   - 等待下载完成（约 1-3 GB，需要 10-30 分钟）
   - 点击 Finish

---

## 3️⃣ 安装必需的 SDK 组件

### 打开 SDK Manager

1. 启动 Android Studio
2. 点击 **More Actions** → **SDK Manager**
   或者：**Tools** → **SDK Manager**

### 安装 SDK Platforms

在 **SDK Platforms** 标签页：

```
✅ Android 13.0 (API 33) - Tiramisu
   - Android SDK Platform 33
   - Sources for Android 33
   - Google APIs Intel x86_64 Atom System Image
```

**推荐额外安装**:
```
✅ Android 14.0 (API 34)
✅ Android 12.0 (API 31)
```

### 安装 SDK Tools

在 **SDK Tools** 标签页：

```
✅ Android SDK Build-Tools 33.x.x
✅ Android SDK Build-Tools 34.x.x
✅ Android SDK Platform-Tools
✅ Android SDK Tools (Obsolete) - 如果可见
✅ Android Emulator
✅ Intel x86 Emulator Accelerator (HAXM installer) - Intel CPU
   或
   Android Emulator Hypervisor Driver - AMD CPU
✅ Google Play services
```

**点击 Apply** → **OK** → 等待下载和安装

---

## 4️⃣ 配置环境变量

### 找到 Android SDK 路径

默认路径：
```
C:\Users\你的用户名\AppData\Local\Android\Sdk
```

验证路径：
1. 打开 Android Studio
2. **File** → **Settings** → **Appearance & Behavior** → **System Settings** → **Android SDK**
3. 查看 **Android SDK Location**

### 设置环境变量（图形界面）

#### 方法 1：通过系统设置

1. **打开系统属性**
   - 右键 **此电脑** → **属性**
   - 点击 **高级系统设置**
   - 点击 **环境变量**

2. **新建系统变量**（在"系统变量"部分）
   - 变量名: `ANDROID_HOME`
   - 变量值: `C:\Users\你的用户名\AppData\Local\Android\Sdk`
   - 点击 **确定**

3. **编辑 Path 变量**（在"系统变量"部分）
   - 找到 `Path` 变量
   - 点击 **编辑**
   - 点击 **新建**，添加以下路径：
     ```
     %ANDROID_HOME%\platform-tools
     %ANDROID_HOME%\emulator
     %ANDROID_HOME%\tools
     %ANDROID_HOME%\tools\bin
     ```
   - 点击 **确定**

4. **保存并重启**
   - 点击所有对话框的 **确定**
   - **重启 PowerShell** 或重启电脑

#### 方法 2：通过 PowerShell（临时）

```powershell
# 设置环境变量（当前会话有效）
$env:ANDROID_HOME = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
$env:Path += ";$env:ANDROID_HOME\platform-tools"
$env:Path += ";$env:ANDROID_HOME\emulator"
$env:Path += ";$env:ANDROID_HOME\tools"
$env:Path += ";$env:ANDROID_HOME\tools\bin"
```

⚠️ **注意**: 方法 2 只是临时的，关闭 PowerShell 后失效。建议使用方法 1。

### 设置环境变量（PowerShell 脚本）- 永久设置

```powershell
# 以管理员身份运行 PowerShell
# 右键 PowerShell → 以管理员身份运行

# 设置 ANDROID_HOME
$androidHome = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidHome, 'Machine')

# 添加到 Path
$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
$newPaths = @(
    "$androidHome\platform-tools",
    "$androidHome\emulator",
    "$androidHome\tools",
    "$androidHome\tools\bin"
)

foreach ($path in $newPaths) {
    if ($currentPath -notlike "*$path*") {
        $currentPath += ";$path"
    }
}

[System.Environment]::SetEnvironmentVariable('Path', $currentPath, 'Machine')

Write-Host "✓ 环境变量配置完成" -ForegroundColor Green
Write-Host "⚠️ 请重启 PowerShell 或电脑使配置生效" -ForegroundColor Yellow
```

---

## 5️⃣ 验证配置

### 重启 PowerShell

**重要**: 配置环境变量后必须重启 PowerShell

### 验证命令

```powershell
# 1. 检查 ANDROID_HOME
Write-Host "ANDROID_HOME: $env:ANDROID_HOME"
# 应该输出: C:\Users\你的用户名\AppData\Local\Android\Sdk

# 2. 检查 ADB
adb --version
# 应该输出: Android Debug Bridge version ...

# 3. 检查 Java
javac -version
# 应该输出: javac 17.x.x 或更高

# 4. 运行 NativeScript 诊断
cd mobile
npx ns doctor
```

### 期望输出

```
✔ Javac is installed and is configured properly.
✔ The Java Development Kit (JDK) is installed and is configured properly.
✔ The Android SDK is installed and is configured properly.
✔ A compatible Android SDK for compilation is found.
✔ The `adb` command is found.
✔ The Android Emulator is installed and is configured properly.
```

---

## 6️⃣ 创建 Android 虚拟设备 (AVD)

### 打开 AVD Manager

1. 启动 Android Studio
2. 点击 **More Actions** → **Virtual Device Manager**
   或者：**Tools** → **Device Manager**

### 创建新设备

1. **点击 "Create Device"**

2. **选择硬件**
   - Category: Phone
   - 推荐: **Pixel 5** 或 **Pixel 6**
   - 点击 **Next**

3. **选择系统镜像**
   - Release Name: **Tiramisu** (API 33)
   - ABI: **x86_64** (Intel) 或 **arm64-v8a** (ARM)
   - 如果未下载，点击 **Download** 旁边的链接
   - 点击 **Next**

4. **配置 AVD**
   - AVD Name: `Pixel_5_API_33` (默认)
   - Startup orientation: Portrait
   - **Show Advanced Settings**:
     - RAM: 2048 MB (最少)
     - VM heap: 256 MB
     - Graphics: **Hardware - GLES 2.0** (推荐)
     - Boot option: Quick Boot
   - 点击 **Finish**

### 启动模拟器

1. 在 Device Manager 中找到你的 AVD
2. 点击 **播放按钮** (▶️)
3. 等待模拟器启动（首次较慢，约 30-60 秒）

---

## 7️⃣ 运行应用

### 确保模拟器运行

```powershell
# 检查连接的设备
adb devices

# 应该看到:
# List of devices attached
# emulator-5554    device
```

### 运行应用

```powershell
# 进入 mobile 目录
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile

# 运行应用
pnpm android
```

**首次运行**:
- ⏱️ 需要 3-8 分钟
- 📦 下载 Gradle、依赖包
- 🔨 编译原生代码
- 📲 安装到模拟器

**后续运行**:
- ⚡ 热重载 1-3 秒

---

## 🆘 常见问题

### Q1: "HAXM installation failed"

**原因**: Intel 虚拟化未启用

**解决方案**:
1. 重启电脑
2. 进入 BIOS (通常按 F2, F10, Del 键)
3. 找到 "Virtualization Technology" 或 "VT-x"
4. 设置为 **Enabled**
5. 保存并退出

**AMD CPU**: 使用 Windows Hypervisor Platform
```powershell
# 以管理员身份运行
Enable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform
```

### Q2: "Unable to locate adb"

**解决方案**:
```powershell
# 验证环境变量
$env:ANDROID_HOME
$env:Path -split ';' | Select-String "android"

# 重启 PowerShell
# 重新运行 adb --version
```

### Q3: 模拟器启动失败

**解决方案 1**: 使用 x86_64 镜像（更快）
- AVD Manager → Edit → 更换 System Image

**解决方案 2**: 增加 RAM
- AVD Manager → Edit → Show Advanced Settings → RAM: 3072 MB

**解决方案 3**: 冷启动
- AVD Manager → 下拉菜单 → Cold Boot Now

### Q4: Gradle 下载慢

**解决方案**: 使用国内镜像

创建 `mobile/gradle.properties`:
```properties
org.gradle.jvmargs=-Xmx2048m -XX:MaxPermSize=512m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8
systemProp.http.proxyHost=mirrors.cloud.tencent.com
systemProp.http.proxyPort=80
systemProp.https.proxyHost=mirrors.cloud.tencent.com
systemProp.https.proxyPort=80
```

### Q5: "Execution failed for task ':app:mergeDebugResources'"

**解决方案**:
```powershell
cd mobile
pnpm clean
rm -r platforms
pnpm android
```

---

## 🎯 配置检查清单

完成后，确保以下都打勾：

- [ ] Android Studio 已安装
- [ ] Android SDK Platform 33 已安装
- [ ] Android SDK Build-Tools 已安装
- [ ] ANDROID_HOME 环境变量已设置
- [ ] Path 包含 platform-tools
- [ ] `adb --version` 命令有效
- [ ] `javac -version` 命令有效
- [ ] AVD 已创建
- [ ] 模拟器可以启动
- [ ] `adb devices` 显示设备
- [ ] `npx ns doctor` 全部通过

---

## 📚 相关资源

### 官方文档
- [NativeScript Windows 设置](https://docs.nativescript.org/setup/windows)
- [Android Studio 下载](https://developer.android.com/studio)
- [Android 系统要求](https://developer.android.com/studio/install)

### 视频教程
- [Android Studio 安装教程](https://www.youtube.com/results?search_query=android+studio+installation)
- [配置 Android 环境变量](https://www.youtube.com/results?search_query=android+environment+variables)

---

## ✅ 完成后

配置完成后，运行：

```powershell
# 1. 验证环境
cd mobile
npx ns doctor

# 2. 启动模拟器
# 通过 Android Studio AVD Manager

# 3. 运行应用
pnpm android
```

🎉 **恭喜！你已准备好开发 Android 应用了！**

---

## ⏱️ 预估时间

| 步骤 | 时间 |
|------|------|
| 下载 Android Studio | 5-15 分钟 |
| 安装 Android Studio | 5-10 分钟 |
| 下载 SDK 组件 | 10-30 分钟 |
| 配置环境变量 | 5 分钟 |
| 创建 AVD | 5 分钟 |
| **总计** | **30-65 分钟** |

**首次运行应用**: 3-8 分钟  
**后续开发**: 热重载 1-3 秒

---

**需要帮助？** 查看 [移动端PC调试指南.md](./移动端PC调试指南.md)

