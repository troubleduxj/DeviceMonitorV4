# Java 版本升级指南 - Windows

## 🔍 当前问题

```
> Dependency requires at least JVM runtime version 11. This build uses a Java 8 JVM.
```

**原因**：Android Gradle Plugin 需要 Java 11+，但系统使用的是 Java 8。

---

## 📥 下载 Java 17 LTS（推荐）

### 方法 1：Oracle JDK（官方，推荐）

**下载地址**：
- 官网：https://www.oracle.com/java/technologies/downloads/#java17
- 直链（Windows x64）：https://download.oracle.com/java/17/latest/jdk-17_windows-x64_bin.exe

**步骤**：
1. 下载 `jdk-17_windows-x64_bin.exe`
2. 运行安装程序
3. 默认安装路径：`C:\Program Files\Java\jdk-17`
4. 按提示完成安装

### 方法 2：Adoptium（OpenJDK，免费）

**下载地址**：
- 官网：https://adoptium.net/
- 直链：https://github.com/adoptium/temurin17-binaries/releases

**步骤**：
1. 下载 `OpenJDK17U-jdk_x64_windows_hotspot_*.msi`
2. 运行安装程序
3. **勾选**"Set JAVA_HOME variable"（自动设置环境变量）
4. **勾选**"Add to PATH"（添加到系统路径）
5. 完成安装

### 方法 3：使用包管理器（高级用户）

```powershell
# 使用 Chocolatey
choco install openjdk17

# 或使用 Scoop
scoop install openjdk17
```

---

## ⚙️ 配置环境变量

### 自动配置（推荐）

在 PowerShell 中运行以下命令：

```powershell
# 查找已安装的 Java 17
$javaPath = "C:\Program Files\Java\jdk-17"

# 如果是 Adoptium
if (-not (Test-Path $javaPath)) {
    $javaPath = "C:\Program Files\Eclipse Adoptium\jdk-17*"
    $javaPath = (Get-Item $javaPath -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
}

# 如果是 OpenJDK
if (-not (Test-Path $javaPath)) {
    $javaPath = "C:\Program Files\OpenJDK\jdk-17*"
    $javaPath = (Get-Item $javaPath -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
}

if (Test-Path $javaPath) {
    Write-Host "找到 Java: $javaPath" -ForegroundColor Green
    
    # 设置系统环境变量（需要管理员权限）
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $javaPath, "Machine")
    
    # 设置当前会话
    $env:JAVA_HOME = $javaPath
    $env:PATH = "$javaPath\bin;$env:PATH"
    
    Write-Host "✓ JAVA_HOME 已设置" -ForegroundColor Green
    Write-Host ""
    Write-Host "验证安装："
    & "$javaPath\bin\java.exe" -version
} else {
    Write-Host "未找到 Java 17，请手动设置" -ForegroundColor Red
}
```

### 手动配置

1. **打开系统环境变量**：
   - 按 `Win + X`，选择"系统"
   - 点击"高级系统设置"
   - 点击"环境变量"

2. **设置 JAVA_HOME**（系统变量）：
   - 点击"新建"
   - 变量名：`JAVA_HOME`
   - 变量值：`C:\Program Files\Java\jdk-17`（或您的实际安装路径）
   - 点击"确定"

3. **更新 PATH**（系统变量）：
   - 找到 `Path` 变量，点击"编辑"
   - 点击"新建"
   - 添加：`%JAVA_HOME%\bin`
   - 将此项**移到顶部**（确保优先使用）
   - 点击"确定"

4. **应用更改**：
   - 关闭所有 PowerShell 和命令提示符窗口
   - 重新打开一个新的 PowerShell 窗口

---

## ✅ 验证安装

在**新的** PowerShell 窗口中运行：

```powershell
# 检查 Java 版本
java -version

# 检查 JAVA_HOME
echo $env:JAVA_HOME

# 检查 javac
javac -version
```

**预期输出**：
```
openjdk version "17.0.x" ...
OpenJDK Runtime Environment ...
OpenJDK 64-Bit Server VM ...

C:\Program Files\Java\jdk-17

javac 17.0.x
```

---

## 🚀 继续构建

验证 Java 17 安装成功后，重新运行构建：

```powershell
# 进入项目目录
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile

# 清理旧的构建
Remove-Item -Path "platforms/android/.gradle" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "platforms/tempPlugin" -Recurse -Force -ErrorAction SilentlyContinue

# 重新构建
npm run android
```

---

## 🔧 故障排除

### 问题 1：命令提示符不识别 java

**原因**：环境变量未生效

**解决**：
1. 确认已关闭所有旧的终端窗口
2. 重新打开一个**新的** PowerShell 窗口
3. 如果还是不行，**重启电脑**

### 问题 2：仍然使用 Java 8

**原因**：PATH 中 Java 8 的优先级更高

**解决**：
1. 打开环境变量设置
2. 在 PATH 中找到 Java 8 的路径（如 `C:\Program Files\Java\jdk1.8*\bin`）
3. 将其**移到 Java 17 路径下方**，或**删除**
4. 重启终端

### 问题 3：多个 Java 版本冲突

**解决**：
```powershell
# 查找所有 Java 安装
Get-ChildItem "C:\Program Files\Java" -ErrorAction SilentlyContinue
Get-ChildItem "C:\Program Files\Eclipse Adoptium" -ErrorAction SilentlyContinue
Get-ChildItem "C:\Program Files\OpenJDK" -ErrorAction SilentlyContinue

# 手动指定使用 Java 17
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
```

---

## 📊 系统需求对照表

| 组件 | 最低要求 | 推荐版本 | 您的版本 |
|------|----------|----------|----------|
| Node.js | 18.x | 20.x LTS | ✅ 20.18.1 |
| Java | 11+ | **17 LTS** | ❌ 8 |
| Android SDK | 21+ | 34 | 待检查 |

---

## 💡 为什么选择 Java 17？

1. **LTS 版本**：长期支持（至 2029 年）
2. **兼容性好**：支持所有现代 Android 开发工具
3. **性能优化**：比 Java 8 快 20-30%
4. **稳定可靠**：被 Android Studio 默认使用

---

## ⏭️ 下一步

安装 Java 17 后：
1. ✅ 验证版本（`java -version` 显示 17）
2. ✅ 清理构建缓存
3. 🚀 重新运行 `npm run android`
4. ⏱️ 等待构建完成（约 5-10 分钟）

---

## 📞 需要帮助？

如果遇到问题，请提供：
1. `java -version` 的输出
2. `echo $env:JAVA_HOME` 的输出
3. `echo $env:PATH` 的输出（可能很长）
4. 安装时的错误信息（如有）

