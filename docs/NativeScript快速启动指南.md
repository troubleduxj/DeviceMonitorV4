# NativeScript 快速启动指南

> 🚀 10 分钟快速验证 NativeScript 开发环境

**目标**: 确认开发环境就绪，能够运行第一个 NativeScript-Vue 应用

---

## ⚡ 快速验证流程

### 1️⃣ 安装 NativeScript CLI (2 分钟)

```bash
# Windows/macOS/Linux 通用
npm install -g @nativescript/core

# 验证安装
ns --version
```

**预期输出**:
```
8.5.0
```

---

### 2️⃣ 环境检查 (3 分钟)

#### Android 环境

```bash
ns doctor android
```

**预期输出**:
```
✔ Getting environment information
✔ Your ANDROID_HOME environment variable is set
✔ The Android SDK is installed
✔ A compatible Android SDK for compilation is found
✔ Javac is installed and is configured properly
✔ The Java Development Kit (JDK) is installed
```

#### iOS 环境（仅 macOS）

```bash
ns doctor ios
```

**预期输出**:
```
✔ Xcode is installed
✔ Xcode Command Line Tools are installed
✔ CocoaPods is installed
```

---

### 3️⃣ 创建测试项目 (2 分钟)

```bash
# 在临时目录创建测试项目（不影响主项目）
cd Desktop  # 或任意临时目录

# 创建 NativeScript-Vue + TypeScript 项目
ns create hello-ns --vue --ts

# 进入项目
cd hello-ns
```

---

### 4️⃣ 运行应用 (3 分钟)

#### 方式 A: Android 模拟器

```bash
# 确保 Android 模拟器已启动或连接真机
ns run android
```

#### 方式 B: iOS 模拟器（macOS）

```bash
ns run ios
```

**预期结果**:
- ✅ 应用成功编译
- ✅ 自动打开模拟器/部署到真机
- ✅ 看到默认的 NativeScript-Vue 界面
- ✅ 界面显示 "Hello, NativeScript-Vue!"

---

## 🎯 验证成功标志

如果你看到以下内容，说明环境配置成功：

### Android
- 应用图标出现在模拟器/真机上
- 应用自动启动
- 界面显示正常
- 控制台输出构建成功信息

### iOS
- 应用图标出现在模拟器上
- 应用自动启动
- 界面显示正常
- Xcode 签名无错误

---

## 🔧 常见问题快速修复

### ❌ 问题 1: `ns: command not found`

**原因**: NativeScript CLI 未正确安装或未添加到 PATH

**解决**:
```bash
# 重新安装
npm install -g @nativescript/core

# 验证全局包路径
npm list -g --depth=0
```

---

### ❌ 问题 2: `ANDROID_HOME not set`

**原因**: Android SDK 环境变量未配置

**解决 (Windows)**:
```powershell
# 打开系统环境变量设置
# 新建环境变量
变量名: ANDROID_HOME
变量值: C:\Users\你的用户名\AppData\Local\Android\Sdk

# 添加到 Path
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\tools
```

**解决 (macOS/Linux)**:
```bash
# 编辑 ~/.bash_profile 或 ~/.zshrc
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools

# 生效
source ~/.bash_profile  # 或 source ~/.zshrc
```

---

### ❌ 问题 3: `No emulators found`

**原因**: 未创建 Android 模拟器

**解决**:
```bash
# 打开 Android Studio
# Tools -> AVD Manager -> Create Virtual Device
# 选择设备型号（推荐 Pixel 5）
# 选择系统镜像（推荐 API 30+）
# 完成创建

# 或使用命令行启动已有模拟器
emulator -list-avds
emulator -avd <模拟器名称>
```

---

### ❌ 问题 4: iOS 构建失败（macOS）

**原因**: Xcode Command Line Tools 未安装或 CocoaPods 缺失

**解决**:
```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 安装 CocoaPods
sudo gem install cocoapods

# 验证
pod --version
```

---

### ❌ 问题 5: Android 构建慢

**原因**: Gradle 首次下载依赖

**解决**:
- 首次构建需要 5-10 分钟（下载 Gradle、Android SDK、依赖包）
- 后续构建会快很多（1-2 分钟）
- 建议使用国内镜像加速（可选）

---

## 📱 设备连接

### Android 真机调试

1. **开启开发者模式**
   - 设置 -> 关于手机 -> 连续点击"版本号" 7 次

2. **开启 USB 调试**
   - 设置 -> 开发者选项 -> USB 调试（开启）

3. **连接电脑**
   ```bash
   # 验证设备连接
   adb devices
   
   # 预期输出
   List of devices attached
   XXXXXXXXXXXXXX  device
   ```

4. **运行应用**
   ```bash
   ns run android --device <设备ID>
   ```

---

### iOS 真机调试（macOS）

1. **Apple 开发者账号**
   - 需要 Apple ID（免费或付费开发者账号）

2. **Xcode 配置**
   - 打开 Xcode
   - Preferences -> Accounts -> 添加 Apple ID

3. **设备信任**
   - 连接 iPhone/iPad 到 Mac
   - 设备上弹出"信任此电脑"，点击信任

4. **运行应用**
   ```bash
   ns run ios --device <设备名称>
   ```

---

## ✅ 环境就绪检查清单

完成以下检查后，即可开始正式开发：

- [ ] `ns --version` 输出版本号
- [ ] `ns doctor android` 全部通过（Android）
- [ ] `ns doctor ios` 全部通过（iOS，macOS）
- [ ] 测试项目 `hello-ns` 成功运行
- [ ] Android 模拟器或真机可用
- [ ] iOS 模拟器或真机可用（macOS）
- [ ] 热重载工作正常（修改代码自动刷新）

---

## 🎉 下一步

环境验证通过后，请继续阅读：

1. **集成到主项目**: `NativeScript-Vue集成实施指南.md`
2. **技术栈详情**: `NativeScript技术栈版本.md`
3. **改造方案**: `NativeScript-Vue 多端化改造方案与任务清单.md`

---

## 📞 获取帮助

### 官方资源

- [NativeScript 官方文档](https://docs.nativescript.org/)
- [NativeScript-Vue 文档](https://nativescript-vue.org/)
- [NativeScript 社区论坛](https://discourse.nativescript.org/)

### 常见错误速查

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `ENOENT: no such file or directory` | 路径不存在 | 检查项目路径和文件名 |
| `Gradle build failed` | Android 构建失败 | 清理缓存 `ns clean` |
| `Pod install failed` | iOS 依赖安装失败 | `cd platforms/ios && pod install` |
| `Unable to apply changes on device` | 热重载失败 | 重启应用 `ns run android` |

---

**准备好了吗？让我们开始吧！** 🚀

