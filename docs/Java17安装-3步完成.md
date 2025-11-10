# Java 17 安装 - 3 步完成

## 🎯 快速安装（3 分钟）

---

### ✅ **步骤 1：下载安装程序**

我已经为您启动了下载脚本！

**或者，手动下载：**

打开浏览器，访问以下**任意一个**链接：

1. **Microsoft OpenJDK**（推荐）
   ```
   https://www.microsoft.com/openjdk
   ```
   - 选择：**Java 17 LTS**
   - 下载：**Windows x64 MSI** 安装包

2. **Adoptium（备选）**
   ```
   https://adoptium.net/temurin/releases/?version=17
   ```
   - 选择：**Windows x64 .msi**

---

### ✅ **步骤 2：安装 Java 17**

双击下载的 `.msi` 安装文件，按照向导操作：

1. ☑️ **接受**许可协议
2. ☑️ 使用**默认**安装路径（`C:\Program Files\...`）
3. ☑️ 点击 **Install**（安装）
4. ☑️ 等待安装完成（约 1-2 分钟）
5. ☑️ 点击 **Finish**（完成）

**安装路径**（记住这个，待会要用）：
```
C:\Program Files\Microsoft\jdk-17.0.13.11-hotspot
```
或类似路径。

---

### ✅ **步骤 3：配置并构建**

安装完成后，在 PowerShell 中运行：

```powershell
# 进入项目目录
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2

# 配置 Java 17
.\scripts\configure-java17.ps1
```

脚本会：
1. 自动找到 Java 17 安装
2. 配置环境变量
3. 验证安装
4. 询问是否立即构建

选择 **Y** 即可开始构建！

---

## 🚀 **预期结果**

配置完成后，运行 `java -version` 应显示：

```
openjdk version "17.0.13" ...
OpenJDK Runtime Environment ...
OpenJDK 64-Bit Server VM ...
```

然后构建将自动开始，预计 **5-10 分钟**完成。

---

## ❓ **遇到问题？**

### 问题 1：下载速度慢

**解决**：
- 使用国内镜像：https://mirrors.tuna.tsinghua.edu.cn/Adoptium/
- 或找同事/朋友要安装包

### 问题 2：找不到 Java 17

**解决**：
运行配置脚本时，会提示手动输入路径：
```
C:\Program Files\Microsoft\jdk-17.0.13.11-hotspot
```

### 问题 3：仍然使用 Java 8

**解决**：
关闭所有 PowerShell 窗口，重新打开一个新的，然后：
```powershell
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2
.\scripts\configure-java17.ps1
```

---

## 📝 **手动配置（高级）**

如果脚本不工作，手动配置环境变量：

1. 按 `Win + X`，选择"系统"
2. "高级系统设置" → "环境变量"
3. 在"系统变量"中：
   - 新建：`JAVA_HOME` = `C:\Program Files\Microsoft\jdk-17.0.13.11-hotspot`
   - 编辑 `Path`，添加：`%JAVA_HOME%\bin`（移到最上面）
4. 确定，关闭所有终端，重新打开

验证：
```powershell
java -version
echo $env:JAVA_HOME
```

---

## ⏭️ **完成后**

Java 17 配置成功后：

```powershell
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile
npm run android
```

构建成功后，查看：
- [移动端快速启动指南](./移动端快速启动指南.md)
- [移动端PC调试指南](./移动端PC调试指南.md)

---

## 📞 需要帮助

如遇问题，请告诉我：
1. 安装到哪一步了
2. 错误信息（如有）
3. `java -version` 的输出

