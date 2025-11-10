# Android Studio 安装步骤速查

> **快速参考 - 从下载到运行应用**

---

## ✅ 当前进度：已下载 Android Studio

---

## 📝 安装和配置步骤

### 步骤 1：安装 Android Studio（5-10分钟）

1. **双击运行安装程序**
   ```
   android-studio-2024.x.x.x-windows.exe
   ```

2. **安装向导**
   - Welcome 界面 → 点击 **Next**
   - Choose Components:
     - ✅ Android Studio
     - ✅ Android Virtual Device
     - 点击 **Next**
   
3. **选择安装位置**
   - 默认: `C:\Program Files\Android\Android Studio`
   - 建议保持默认
   - 点击 **Next**

4. **开始安装**
   - 点击 **Install**
   - 等待安装完成（约 2-5 分钟）
   - 点击 **Next** → **Finish**

5. **启动 Android Studio**
   - 勾选 "Start Android Studio"
   - 点击 **Finish**

---

### 步骤 2：首次启动配置（10-30分钟）

#### 2.1 导入设置

```
□ Do not import settings （首次安装选这个）
点击 OK
```

#### 2.2 数据共享（可选）

```
选择: Don't send (或 Send，随意)
点击下一步
```

#### 2.3 **重要！安装类型**

```
○ Standard （推荐）
  ✅ 自动安装所需的 SDK 组件
  ✅ 自动下载系统镜像
  ✅ 配置 AVD

点击 Next
```

#### 2.4 选择主题

```
○ Light （亮色）
○ Dark  （暗色）

随意选择，点击 Next
```

#### 2.5 **SDK 组件下载（关键步骤）**

会显示即将下载的组件清单：

```
✅ Android SDK Platform 33
✅ Android SDK Platform-Tools  
✅ Android SDK Build-Tools
✅ Android Emulator
✅ Intel x86 Emulator Accelerator (HAXM) - Intel CPU
   或
✅ Android Emulator Hypervisor Driver - AMD CPU
✅ SDK Patch Applier
```

- 大小: 约 1-3 GB
- 时间: 10-30 分钟（取决于网速）
- 点击 **Next**
- 点击 **Finish** 开始下载

⏱️ **等待下载完成** - 这是最耗时的步骤

#### 2.6 完成安装

```
下载完成后会显示 "Finish"
点击 Finish
```

---

### 步骤 3：安装额外的 SDK 组件（5分钟）

Android Studio 主界面出现后：

#### 3.1 打开 SDK Manager

```
方法 1: 点击右上角 ⚙️ 图标 → SDK Manager
方法 2: More Actions → SDK Manager
方法 3: Tools → SDK Manager
```

#### 3.2 安装 SDK Platforms

在 **SDK Platforms** 标签页：

```
✅ Android 13.0 (Tiramisu) - API Level 33  ⭐ 推荐
   - Android SDK Platform 33
   - Google APIs Intel x86_64 Atom System Image

可选（建议安装）:
□ Android 14.0 (UpsideDownCake) - API Level 34
□ Android 12.0 (S) - API Level 31
```

勾选后点击 **Apply** → **OK**

#### 3.3 安装 SDK Tools

切换到 **SDK Tools** 标签页：

```
✅ Android SDK Build-Tools 34.x.x
✅ Android SDK Build-Tools 33.x.x
✅ Android SDK Platform-Tools
✅ Android Emulator
✅ Intel x86 Emulator Accelerator (HAXM installer) - Intel CPU
   或
✅ Android Emulator Hypervisor Driver - AMD CPU
```

勾选后点击 **Apply** → **OK** → 等待安装

---

### 步骤 4：配置环境变量（5分钟）⭐ 重要

#### 4.1 找到 Android SDK 路径

在 SDK Manager 中查看 **Android SDK Location**:

```
默认路径:
C:\Users\你的用户名\AppData\Local\Android\Sdk
```

复制这个路径！

#### 4.2 设置环境变量

**方法 A: 图形界面（推荐）**

1. **打开环境变量设置**
   ```
   右键 "此电脑" → 属性 
   → 高级系统设置 
   → 环境变量
   ```

2. **新建 ANDROID_HOME**（在"系统变量"部分）
   ```
   变量名: ANDROID_HOME
   变量值: C:\Users\你的用户名\AppData\Local\Android\Sdk
   
   点击 "确定"
   ```

3. **编辑 Path 变量**（在"系统变量"部分）
   ```
   找到 "Path" → 点击 "编辑"
   点击 "新建"，添加以下 4 个路径：
   
   %ANDROID_HOME%\platform-tools
   %ANDROID_HOME%\emulator
   %ANDROID_HOME%\tools
  %ANDROID_HOME%\tools\bin
   
   点击 "确定"
   ```

4. **保存**
   ```
   点击所有对话框的 "确定"
   ```

**方法 B: PowerShell（管理员）**

```powershell
# 右键 PowerShell → 以管理员身份运行

# 替换为你的实际路径
$androidHome = "C:\Users\你的用户名\AppData\Local\Android\Sdk"

# 设置 ANDROID_HOME
[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidHome, 'Machine')

# 获取当前 Path
$path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')

# 添加 Android 相关路径
$newPath = "$path;$androidHome\platform-tools;$androidHome\emulator;$androidHome\tools;$androidHome\tools\bin"

# 更新 Path
[System.En vironment]::SetEnvironmentVariable('Path', $newPath, 'Machine')

Write-Host "环境变量配置完成！" -ForegroundColor Green
Write-Host "请重启 PowerShell" -ForegroundColor Yellow
```

---

### 步骤 5：创建 Android 虚拟设备（5分钟）

#### 5.1 打开 Device Manager

```
方法 1: 点击右侧工具栏 📱 Device Manager 图标
方法 2: More Actions → Virtual Device Manager
方法 3: Tools → Device Manager
```

#### 5.2 创建新设备

1. **点击 "Create Device"**

2. **选择硬件**
   ```
   Category: Phone
   设备: Pixel 5 或 Pixel 6 （推荐）
   
   点击 Next
   ```

3. **下载系统镜像**
   ```
   Release Name: Tiramisu (API 33)
   ABI: x86_64
   
   如果显示 "Download"，点击下载
   等待下载完成（约 800MB-1GB）
   
   点击 Next
   ```

4. **配置 AVD**
   ```
   AVD Name: Pixel_5_API_33 (默认即可)
   
   点击 "Show Advanced Settings" (可选优化):
   - RAM: 2048 MB (推荐 3072 MB)
   - VM heap: 256 MB
   - Graphics: Hardware - GLES 2.0
   
   点击 Finish
   ```

#### 5.3 启动模拟器测试

```
在 Device Manager 中找到你创建的设备
点击 ▶️ (播放按钮)

等待启动（首次约 30-60 秒）
看到 Android 桌面 = 成功！
```

---

### 步骤 6：验证配置（2分钟）⭐ 重要

⚠️ **必须先重启 PowerShell！**

```powershell
# 1. 重新打开 PowerShell

# 2. 检查环境变量
Write-Host $env:ANDROID_HOME
# 应该输出: C:\Users\xxx\AppData\Local\Android\Sdk

# 3. 检查 ADB
adb --version
# 应该输出: Android Debug Bridge version x.x.x

# 4. 检查连接的设备（确保模拟器运行中）
adb devices
# 应该输出:
# List of devices attached
# emulator-5554    device

# 5. 运行 NativeScript 诊断
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile
npx ns doctor
```

#### 期望的 `ns doctor` 输出:

```
✔ Javac is installed and is configured properly.
✔ The Java Development Kit (JDK) is installed and is configured properly.
✔ The Android SDK is installed and is configured properly.
✔ A compatible Android SDK for compilation is found.
✔ The `adb` command is found.
✔ The Android Emulator is installed and is configured properly.
```

如果全部 ✔，说明配置成功！

---

### 步骤 7：运行应用（首次 3-8 分钟）🎉

```powershell
# 确保在 mobile 目录
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile

# 确保模拟器已启动
adb devices

# 运行应用
pnpm android
```

#### 首次运行过程:

```
1. [0-30秒] 准备环境
2. [1-3分钟] 下载 Gradle 依赖
3. [1-3分钟] 编译原生代码
4. [10-20秒] 安装到模拟器
5. [5-10秒] 启动应用

总计: 3-8 分钟（首次）
后续: 热重载 1-3 秒 ⚡
```

---

## 🆘 常见问题快速解决

### Q1: "HAXM installation failed"

**Intel CPU**:
```
1. 重启电脑
2. 进入 BIOS (按 F2/F10/Del)
3. 启用 "Virtualization Technology" 或 "VT-x"
4. 保存并重启
```

**AMD CPU**:
```powershell
# 以管理员身份运行 PowerShell
Enable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform
```

### Q2: "Unable to locate adb"

```powershell
# 重启 PowerShell 后重试
# 或者临时设置:
$env:ANDROID_HOME = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
$env:Path = "$env:Path;$env:ANDROID_HOME\platform-tools"
```

### Q3: 模拟器启动慢

```
1. AVD Manager → Edit AVD
2. Show Advanced Settings
3. RAM: 增加到 3072 MB
4. Graphics: Hardware - GLES 2.0
5. Boot option: Quick Boot
```

### Q4: 下载速度慢

Android Studio 下载慢是正常的（国外服务器）

**加速方法**:
- 使用有线网络
- 换个时间段（凌晨较快）
- 使用移动热点（有时比宽带快）

---

## ✅ 配置完成检查清单

安装完成后，确保这些都打勾：

- [ ] Android Studio 已安装
- [ ] SDK Platform 33 已安装
- [ ] SDK Build-Tools 已安装
- [ ] 系统镜像 (API 33) 已下载
- [ ] ANDROID_HOME 环境变量已设置
- [ ] Path 已更新
- [ ] PowerShell 已重启
- [ ] `adb --version` 命令有效
- [ ] AVD 已创建
- [ ] 模拟器可以启动
- [ ] `adb devices` 显示模拟器
- [ ] `npx ns doctor` 全部通过 ✔

---

## 🎯 当前你的位置

```
✅ 步骤 1: 下载 Android Studio  <-- 你在这里
□ 步骤 2: 安装 Android Studio
□ 步骤 3: 首次启动配置
□ 步骤 4: 安装 SDK 组件
□ 步骤 5: 配置环境变量
□ 步骤 6: 创建虚拟设备
□ 步骤 7: 验证配置
□ 步骤 8: 运行应用
```

---

## 📞 需要帮助？

在任何步骤遇到问题，运行：

```powershell
cd mobile
npx ns doctor
```

会告诉你缺少什么组件。

---

**预计总时间**: 30-60 分钟（大部分是下载等待）

**准备好了？开始安装 Android Studio 吧！** 🚀

