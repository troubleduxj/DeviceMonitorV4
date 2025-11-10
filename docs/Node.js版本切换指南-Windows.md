# Node.js 版本切换指南 (Windows)

> **解决 NativeScript 与 Node.js v22 的兼容性问题**  
> **推荐版本**: Node.js 20 LTS 或 18 LTS

---

## ⚠️ 为什么需要切换版本？

### 当前问题
```
Error [ERR_PACKAGE_PATH_NOT_EXPORTED]: Package subpath './decode' is not defined by "exports"
```

### 原因
- **Node.js v22.17.0** 是最新版本，引入了更严格的模块导出规则
- `@nativescript/webpack ~5.0.0` 依赖的某些包（如 `entities`）不兼容
- NativeScript 官方推荐使用 **Node.js 18 LTS** 或 **Node.js 20 LTS**

---

## 🚀 方案 A：使用 nvm-windows（推荐）⭐

nvm-windows 可以让您在同一台电脑上安装和切换多个 Node.js 版本。

### 步骤 1：下载 nvm-windows

**下载链接：**
https://github.com/coreybutler/nvm-windows/releases

**选择文件：**
- `nvm-setup.exe` （推荐，安装版）
- 最新版本：v1.1.12 或更高

**直接下载链接：**
https://github.com/coreybutler/nvm-windows/releases/download/1.1.12/nvm-setup.exe

### 步骤 2：安装 nvm-windows

1. **运行 `nvm-setup.exe`**
2. **接受许可协议**
3. **选择安装位置**（建议默认）：
   ```
   C:\Users\你的用户名\AppData\Roaming\nvm
   ```
4. **选择 Node.js 符号链接位置**（建议默认）：
   ```
   C:\Program Files\nodejs
   ```
5. **点击 Install** 完成安装

### 步骤 3：验证安装

打开**新的 PowerShell 窗口**（必须新开窗口）：

```powershell
# 检查 nvm 版本
nvm version
# 应该显示：1.1.12 或更高

# 查看当前 Node.js 版本
nvm list
# 会显示已安装的版本
```

### 步骤 4：安装 Node.js 20 LTS

```powershell
# 安装 Node.js 20 LTS（推荐）
nvm install 20.18.1

# 或者安装 Node.js 18 LTS
nvm install 18.20.5

# 查看安装进度
# 下载大约 20-30 MB，需要 1-3 分钟
```

### 步骤 5：切换到 Node.js 20

```powershell
# 切换到 Node.js 20
nvm use 20.18.1

# 验证版本
node --version
# 应该显示：v20.18.1

npm --version
# 应该显示：10.x.x
```

### 步骤 6：重新安装项目依赖

```powershell
# 切换到项目目录
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2

# 删除旧的 node_modules 和 lock 文件
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force mobile\node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force mobile\platforms -ErrorAction SilentlyContinue
Remove-Item pnpm-lock.yaml -ErrorAction SilentlyContinue

# 重新安装依赖
pnpm install

# 运行应用
cd mobile
pnpm android
```

---

## 🔧 方案 B：直接安装 Node.js 20 LTS（替换当前版本）

如果不需要多版本管理，可以直接安装 Node.js 20。

### 步骤 1：卸载当前 Node.js

1. 打开 **设置** → **应用**
2. 搜索 **Node.js**
3. 点击 **卸载**
4. 删除残留文件（可选）：
   ```powershell
   Remove-Item -Recurse -Force $env:APPDATA\npm -ErrorAction SilentlyContinue
   Remove-Item -Recurse -Force $env:APPDATA\npm-cache -ErrorAction SilentlyContinue
   ```

### 步骤 2：下载 Node.js 20 LTS

**官方下载页面：**
https://nodejs.org/en/download/

**Windows 64-bit 安装包：**
https://nodejs.org/dist/v20.18.1/node-v20.18.1-x64.msi

**文件大小：** 约 28 MB

### 步骤 3：安装 Node.js 20

1. **运行 `.msi` 安装文件**
2. **接受许可协议**
3. **选择安装位置**（建议默认）
4. **勾选所有组件**：
   - Node.js runtime
   - npm package manager
   - Online documentation shortcuts
   - **Add to PATH**（重要！）
5. **点击 Install**
6. **完成后重启 PowerShell**

### 步骤 4：验证安装

```powershell
# 新开 PowerShell 窗口

# 检查 Node.js 版本
node --version
# 应该显示：v20.18.1

# 检查 npm 版本
npm --version
# 应该显示：10.x.x

# 检查 pnpm 版本（如果没有需要重新安装）
pnpm --version
```

### 步骤 5：安装 pnpm（如果需要）

```powershell
# 安装 pnpm
npm install -g pnpm

# 验证
pnpm --version
```

### 步骤 6：重新安装项目依赖

```powershell
# 切换到项目目录
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2

# 删除旧的依赖
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force mobile\node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force mobile\platforms -ErrorAction SilentlyContinue
Remove-Item pnpm-lock.yaml -ErrorAction SilentlyContinue

# 重新安装
pnpm install

# 运行移动端
cd mobile
pnpm android
```

---

## 📊 Node.js 版本对比

| 版本 | 发布日期 | LTS 结束 | NativeScript兼容性 | 推荐度 |
|------|---------|---------|-------------------|--------|
| **Node.js 20.18.1 LTS** | 2024-10 | 2026-04 | ✅ 完全兼容 | ⭐⭐⭐⭐⭐ |
| **Node.js 18.20.5 LTS** | 2024-09 | 2025-04 | ✅ 完全兼容 | ⭐⭐⭐⭐ |
| Node.js 22.17.0 | 2025-10 | - | ⚠️ 部分兼容 | ⭐⭐ |
| Node.js 16.x | 2021-10 | 已过期 | ⚠️ 不推荐 | ⭐ |

---

## 🎯 nvm-windows 常用命令

### 版本管理
```powershell
# 查看已安装的版本
nvm list

# 查看可用的 Node.js 版本
nvm list available

# 安装指定版本
nvm install 20.18.1

# 卸载指定版本
nvm uninstall 22.17.0

# 切换版本
nvm use 20.18.1

# 查看当前版本
nvm current
```

### 别名管理
```powershell
# 为版本创建别名
nvm alias dev 20.18.1
nvm alias prod 18.20.5

# 使用别名切换
nvm use dev
```

---

## ✅ 切换完成后的验证

### 1. 检查版本
```powershell
node --version
# 应该显示：v20.18.1 或 v18.20.5

pnpm --version
# 应该显示：10.x.x
```

### 2. 检查环境
```powershell
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile

# 运行 NativeScript 诊断
npx ns doctor

# 应该全部显示 ✔
✔ Your ANDROID_HOME environment variable is set
✔ Your adb from the Android SDK is correctly installed
✔ The Android SDK is installed
✔ A compatible Android SDK for compilation is found
✔ Javac is installed and is configured properly
✔ Component @nativescript/android is installed
```

### 3. 测试应用
```powershell
# 确保模拟器运行中
adb devices

# 运行应用
cd mobile
pnpm android

# 应该不再出现 ERR_PACKAGE_PATH_NOT_EXPORTED 错误
```

---

## 🆘 常见问题

### Q1: nvm 安装后命令无效

**解决方案：**
```powershell
# 1. 关闭所有 PowerShell 窗口
# 2. 重新打开 PowerShell
# 3. 验证环境变量

$env:NVM_HOME
$env:NVM_SYMLINK

# 如果为空，手动添加到系统环境变量：
# NVM_HOME = C:\Users\你的用户名\AppData\Roaming\nvm
# NVM_SYMLINK = C:\Program Files\nodejs
# Path += %NVM_HOME%;%NVM_SYMLINK%
```

### Q2: "Access Denied" 错误

**解决方案：**
```powershell
# 以管理员身份运行 PowerShell
# 右键 PowerShell → 以管理员身份运行

nvm use 20.18.1
```

### Q3: 切换版本后 pnpm 不可用

**解决方案：**
```powershell
# 重新全局安装 pnpm
npm install -g pnpm

# 验证
pnpm --version
```

### Q4: 多个 Node.js 安装冲突

**解决方案：**
```powershell
# 查找 Node.js 安装位置
Get-Command node | Select-Object -ExpandProperty Source
Get-Command npm | Select-Object -ExpandProperty Source

# 如果有多个，卸载所有 Node.js，只保留 nvm 管理的版本
```

---

## 💡 最佳实践

### 1. 项目级版本管理

创建 `.nvmrc` 文件（在项目根目录）：
```
20.18.1
```

然后在项目目录运行：
```powershell
nvm use
# 自动切换到 .nvmrc 指定的版本
```

### 2. 不同项目使用不同版本

```powershell
# Web 项目（可以用最新版）
cd D:\Projects\web-project
nvm use 22.17.0

# Mobile 项目（使用 LTS）
cd D:\Projects\DeviceMonitorV2\mobile
nvm use 20.18.1
```

### 3. 设置默认版本

```powershell
# 设置系统默认版本
nvm alias default 20.18.1

# 重启后自动使用这个版本
```

---

## 📚 参考链接

### 官方文档
- [Node.js 官网](https://nodejs.org/)
- [nvm-windows GitHub](https://github.com/coreybutler/nvm-windows)
- [NativeScript 环境要求](https://docs.nativescript.org/environment-setup.html)

### 下载链接
- [Node.js 20 LTS](https://nodejs.org/dist/v20.18.1/)
- [Node.js 18 LTS](https://nodejs.org/dist/v18.20.5/)
- [nvm-windows Releases](https://github.com/coreybutler/nvm-windows/releases)

---

## ✅ 完成检查清单

切换 Node.js 版本后，请确认：

- [ ] Node.js 版本为 20.18.1 或 18.20.5
- [ ] pnpm 可用（`pnpm --version`）
- [ ] 旧的 node_modules 已删除
- [ ] 依赖重新安装（`pnpm install`）
- [ ] `npx ns doctor` 全部通过
- [ ] `pnpm android` 可以正常运行
- [ ] 不再出现 `ERR_PACKAGE_PATH_NOT_EXPORTED` 错误

---

## 🎉 成功后的状态

切换完成后，您应该看到：

```powershell
PS D:\...\DeviceMonitorV2\mobile> pnpm android

> @device-monitor/mobile@1.0.0 android
> npx ns run android

Searching for devices...
Copying template files...
Platform android successfully added. v8.9.2
Preparing project...
Building application...
Installing on emulator-5554...
Successfully synced application
```

**不再有错误！** ✨

---

**建议操作顺序：**
1. ✅ 安装 nvm-windows（方案 A，推荐）
2. ✅ 安装 Node.js 20 LTS
3. ✅ 切换到 Node.js 20
4. ✅ 删除旧依赖
5. ✅ 重新安装依赖
6. ✅ 运行应用

**预计总时间：** 10-15 分钟

---

**最后更新：** 2025-10-25  
**适用于：** Windows 10/11, Node.js 18-22, NativeScript 8.9+

