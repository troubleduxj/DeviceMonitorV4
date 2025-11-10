# Android 模拟器常见问题解决

> **DeviceMonitor Mobile - 模拟器故障排除指南**

---

## 🔴 问题 1: Bandicam Vulkan Hooks 冲突

### 错误信息

```
Suggestion(s) based on crash info:
It appears Bandicam Vulkan hooks are installed on your system, 
which can be causing the crash. Try uninstalling Bandicam / removing the hooks.
```

### 原因

Bandicam（或其他录屏软件）的 Vulkan hooks 与 Android 模拟器的硬件加速冲突。

### 解决方案

#### ✅ 方案 1: 修改图形渲染模式（推荐）

**步骤**:
1. Android Studio → Device Manager
2. 找到 AVD → 点击 ✏️ (编辑)
3. Show Advanced Settings
4. **Graphics**: `Hardware - GLES 2.0` → 改为 `Software - GLES 2.0`
5. Finish → 重新启动模拟器

**优点**: 
- 无需卸载软件
- 兼容性最好

**缺点**: 
- 性能稍降（但足够开发使用）

#### ⚡ 方案 2: 临时关闭 Bandicam

**步骤**:
```
Ctrl + Shift + Esc → 任务管理器
结束进程:
  - bdcam.exe
  - bdcam64.exe
  - BandiCamHook.exe
  
启动模拟器
```

**优点**: 
- 保持硬件加速性能

**缺点**: 
- 每次需要手动关闭

#### 🔧 方案 3: 禁用 Vulkan Hooks

**Bandicam 设置**:
```
1. 打开 Bandicam
2. Settings → Advanced
3. 禁用 "Vulkan Capture"
4. 重启电脑
```

#### 🗑️ 方案 4: 卸载冲突软件

如果不需要 Bandicam，直接卸载：
```
控制面板 → 程序和功能 → 卸载 Bandicam
```

---

## 🔴 问题 2: 模拟器启动慢

### 症状

- 模拟器启动超过 2 分钟
- 黑屏时间长

### 解决方案

#### 优化 AVD 配置

```
Device Manager → Edit AVD → Show Advanced Settings

推荐配置:
- RAM: 3072 MB (或更高)
- VM heap: 512 MB
- Graphics: Hardware - GLES 2.0 (如无冲突)
- Boot option: Quick Boot (启用快速启动)
- Multi-Core CPU: 4 核
```

#### 启用硬件加速

**Intel CPU**:
```
确保安装 HAXM:
SDK Manager → SDK Tools → Intel x86 Emulator Accelerator (HAXM)
```

**AMD CPU**:
```powershell
# 以管理员身份运行 PowerShell
Enable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform
```

#### 使用冷启动

```
Device Manager → AVD 右侧下拉菜单 → Cold Boot Now
```

---

## 🔴 问题 3: "HAXM installation failed"

### 错误信息

```
Intel HAXM installation failed
```

### 原因

CPU 虚拟化未启用（Intel VT-x 或 AMD-V）

### 解决方案

#### 启用 CPU 虚拟化

**步骤**:
1. 重启电脑
2. 进入 BIOS/UEFI:
   - 通常按 `F2`, `F10`, `Del`, 或 `F12` 键
   - 取决于主板品牌
3. 找到虚拟化选项:
   - Intel: "Intel Virtualization Technology" 或 "VT-x"
   - AMD: "SVM Mode" 或 "AMD-V"
4. 设置为 **Enabled**
5. 保存并退出 (F10)

#### AMD CPU 替代方案

如果是 AMD CPU，使用 Windows Hypervisor Platform：

```powershell
# 以管理员身份运行 PowerShell
Enable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform

# 重启电脑
```

---

## 🔴 问题 4: "Unable to locate adb"

### 错误信息

```
✖ WARNING: adb from the Android SDK is not installed
```

### 原因

环境变量未正确配置

### 解决方案

#### 验证环境变量

```powershell
# 检查 ANDROID_HOME
Write-Host $env:ANDROID_HOME
# 应该输出: C:\Users\xxx\AppData\Local\Android\Sdk

# 检查 Path
$env:Path -split ';' | Select-String "android"
# 应该包含 platform-tools
```

#### 设置环境变量

**图形界面**:
```
右键 "此电脑" → 属性 → 高级系统设置 → 环境变量

系统变量:
  ANDROID_HOME = C:\Users\你的用户名\AppData\Local\Android\Sdk
  
Path 添加:
  %ANDROID_HOME%\platform-tools
  %ANDROID_HOME%\emulator
```

**PowerShell** (管理员):
```powershell
$androidHome = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidHome, 'Machine')

$path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
$newPath = "$path;$androidHome\platform-tools;$androidHome\emulator"
[System.Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine')
```

⚠️ **重启 PowerShell 使配置生效**

---

## 🔴 问题 5: 模拟器黑屏/无响应

### 解决方案

#### 方法 1: 冷启动

```
Device Manager → AVD 右侧下拉菜单 → Cold Boot Now
```

#### 方法 2: 清除 AVD 数据

```
Device Manager → AVD 右侧下拉菜单 → Wipe Data
重新启动模拟器
```

#### 方法 3: 重新创建 AVD

```
Device Manager → 删除旧 AVD → Create Device → 重新配置
```

---

## 🔴 问题 6: "Execution failed for task ':app:mergeDebugResources'"

### 错误信息

```
Execution failed for task ':app:mergeDebugResources'
```

### 解决方案

```powershell
cd mobile

# 清理项目
pnpm clean

# 删除 platforms
Remove-Item -Recurse -Force platforms

# 清理 node_modules (可选)
Remove-Item -Recurse -Force node_modules
pnpm install

# 重新运行
pnpm android
```

---

## 🔴 问题 7: Gradle 下载慢/失败

### 症状

- 构建卡在下载 Gradle
- 下载速度很慢

### 解决方案

#### 使用本地 Gradle

下载 Gradle: https://gradle.org/releases/

解压到本地，配置 `gradle-wrapper.properties`:

```properties
distributionUrl=file:///C:/Gradle/gradle-7.5-all.zip
```

#### 使用镜像源

创建/编辑 `mobile/gradle.properties`:

```properties
org.gradle.jvmargs=-Xmx2048m
systemProp.http.proxyHost=mirrors.cloud.tencent.com
systemProp.http.proxyPort=80
systemProp.https.proxyHost=mirrors.cloud.tencent.com
systemProp.https.proxyPort=80
```

---

## 🔴 问题 8: "adb: device offline"

### 症状

```
adb devices
List of devices attached
emulator-5554    offline
```

### 解决方案

```powershell
# 重启 ADB 服务
adb kill-server
adb start-server

# 重启模拟器
# Device Manager → 关闭模拟器 → 重新启动
```

---

## 🆘 通用诊断步骤

### 1. 运行 NativeScript 诊断

```powershell
cd mobile
npx ns doctor
```

会检查:
- Java JDK
- Android SDK
- ADB
- 模拟器配置

### 2. 检查设备连接

```powershell
adb devices
```

应该显示:
```
List of devices attached
emulator-5554    device
```

### 3. 查看详细日志

```powershell
# Android 日志
adb logcat

# 过滤应用日志
adb logcat | Select-String "DeviceMonitor"

# NativeScript 详细日志
cd mobile
npx ns run android --log trace
```

### 4. 清理重建

```powershell
cd mobile
pnpm clean
Remove-Item -Recurse -Force platforms
pnpm android
```

---

## 📋 模拟器推荐配置

### 开发环境（平衡性能与兼容性）

```
硬件配置:
  Device: Pixel 5
  RAM: 3072 MB
  VM heap: 512 MB
  Internal Storage: 2048 MB

系统镜像:
  Release: Tiramisu (API 33)
  ABI: x86_64

图形设置:
  Graphics: Software - GLES 2.0 (兼容性好)
  或 Hardware - GLES 2.0 (性能好，但可能冲突)

启动选项:
  Boot option: Quick Boot
  Multi-Core CPU: 4
```

### 性能测试环境（高性能）

```
硬件配置:
  Device: Pixel 6
  RAM: 4096 MB
  VM heap: 768 MB

系统镜像:
  Release: Tiramisu (API 33)
  ABI: x86_64

图形设置:
  Graphics: Hardware - GLES 2.0

启动选项:
  Boot option: Quick Boot
  Multi-Core CPU: 6-8
```

---

## 🔍 常用检查命令

```powershell
# 检查环境变量
Write-Host "ANDROID_HOME: $env:ANDROID_HOME"

# 检查 ADB
adb --version

# 检查 Java
javac -version

# 检查设备
adb devices

# 运行诊断
npx ns doctor

# 查看模拟器列表
emulator -list-avds

# 通过命令行启动模拟器
emulator -avd Pixel_5_API_33
```

---

## 📞 还是无法解决？

### 收集信息

运行以下命令收集诊断信息:

```powershell
Write-Host "=== 环境信息 ===" 
Write-Host "ANDROID_HOME: $env:ANDROID_HOME"
Write-Host "`n=== ADB 版本 ==="
adb --version
Write-Host "`n=== Java 版本 ==="
javac -version
Write-Host "`n=== 连接的设备 ==="
adb devices
Write-Host "`n=== NativeScript 诊断 ==="
cd mobile
npx ns doctor
```

将输出提供给我，我会帮你进一步诊断。

---

## ✅ 配置检查清单

遇到问题时，逐项检查：

- [ ] ANDROID_HOME 环境变量已设置
- [ ] Path 包含 platform-tools
- [ ] `adb --version` 有输出
- [ ] `javac -version` 有输出
- [ ] CPU 虚拟化已启用
- [ ] HAXM 或 Hypervisor Platform 已安装
- [ ] AVD 已创建
- [ ] 模拟器可以启动
- [ ] `adb devices` 显示 device
- [ ] `npx ns doctor` 全部 ✔
- [ ] 没有冲突的软件（Bandicam 等）

---

**遇到问题不要慌，按照此文档逐步排查，90% 的问题都能解决！** 🚀


