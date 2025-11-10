# Android 构建代理配置指南

## 📊 当前配置状态

### ✅ 已配置的镜像加速

1. **Gradle 镜像** - 腾讯云
   - 文件：`mobile/platforms/android/gradle/wrapper/gradle-wrapper.properties`
   - URL：`https://mirrors.cloud.tencent.com/gradle/`

2. **Maven 镜像** - 阿里云
   - 文件：`mobile/platforms/android/build.gradle`
   - 包含：
     - `maven.aliyun.com/repository/google`
     - `maven.aliyun.com/repository/public`
     - `maven.aliyun.com/repository/jcenter`
     - `maven.aliyun.com/repository/gradle-plugin`

---

## 🌐 是否需要开启代理？

### 判断标准

| 场景 | 是否需要代理 | 说明 |
|------|--------------|------|
| 使用了镜像 | ❌ **不需要** | 已配置阿里云/腾讯云镜像 |
| 下载速度 >500KB/s | ❌ **不需要** | 镜像已足够快 |
| 下载速度 <100KB/s | ✅ **建议使用** | 网络不佳或镜像被限速 |
| 频繁超时 | ✅ **建议使用** | 网络连接不稳定 |
| 需要访问 GitHub | ✅ **可能需要** | 某些插件从 GitHub 下载 |

### 快速测试

在 PowerShell 中运行：
```powershell
# 测试阿里云镜像连接速度
Measure-Command { Invoke-WebRequest -Uri "https://maven.aliyun.com/repository/public/" -UseBasicParsing | Out-Null }
```

如果耗时 **<2秒**：不需要代理  
如果耗时 **>5秒**：建议使用代理

---

## 📦 手动下载Gradle（备用方案）

如果自动下载失败或速度太慢，可以手动下载并放置：

### 步骤

1. **下载 Gradle**
   - 腾讯云镜像：`https://mirrors.cloud.tencent.com/gradle/gradle-8.14.3-bin.zip`
   - 阿里云镜像：`https://mirrors.aliyun.com/macports/distfiles/gradle/gradle-8.14.3-bin.zip`
   - 官方源：`https://services.gradle.org/distributions/gradle-8.14.3-bin.zip`

2. **放置到缓存目录**
   ```
   %USERPROFILE%\.gradle\wrapper\dists\gradle-8.14.3-bin\<hash>\
   ```
   
   或者直接放到：
   ```
   %USERPROFILE%\.gradle\wrapper\dists\gradle-8.14.3-bin\
   ```
   
   并创建一个随机命名的子目录。

3. **重新运行构建**
   ```powershell
   cd mobile
   npm run android
   ```

---

## 🔧 配置代理（可选）

### 方法 1：临时环境变量（推荐）

在启动构建前设置：

```powershell
# 设置 HTTP/HTTPS 代理
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"

# 设置不走代理的地址（国内镜像）
$env:NO_PROXY="localhost,127.0.0.1,*.aliyun.com,*.tencent.com"

# 然后运行构建
cd mobile
npm run android
```

### 方法 2：Gradle 全局配置

编辑 `%USERPROFILE%\.gradle\gradle.properties`：

```properties
# HTTP 代理
systemProp.http.proxyHost=127.0.0.1
systemProp.http.proxyPort=7890
systemProp.http.nonProxyHosts=*.aliyun.com|*.tencent.com|localhost

# HTTPS 代理
systemProp.https.proxyHost=127.0.0.1
systemProp.https.proxyPort=7890
systemProp.https.nonProxyHosts=*.aliyun.com|*.tencent.com|localhost
```

### 方法 3：npm 配置代理

```powershell
npm config set proxy http://127.0.0.1:7890
npm config set https-proxy http://127.0.0.1:7890

# 查看配置
npm config list
```

---

## 🚀 推荐方案（无需代理）

### 使用国内镜像 + 优化配置

**已经自动配置好了**：
- ✅ Gradle：腾讯云镜像
- ✅ Maven：阿里云镜像  
- ✅ Gradle 内存：4GB
- ✅ 并行构建：开启
- ✅ 守护进程：开启

这套配置在**国内网络环境下**已经足够快，**通常不需要代理**。

---

## 🔍 监控下载速度

### 实时查看构建日志

```powershell
# 在新的 PowerShell 窗口运行
Get-Content "D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile\build-log.txt" -Wait -Tail 20
```

### 查看 Gradle 下载详情

编辑 `mobile/platforms/android/gradle.properties`，添加：
```properties
# 显示详细下载信息
org.gradle.console=verbose
org.gradle.logging.level=info
```

---

## 📊 下载进度说明

### Gradle 下载的点点表示什么？

```
Downloading...
.....................................................
```

每个 `.` 表示：
- 一次心跳/进度更新
- 通常每 1-2 秒一个点
- **正常现象**，不是卡住了

### 典型下载时间

| 组件 | 首次 | 后续 |
|------|------|------|
| Gradle 8.14.3 | 1-3分钟 | 跳过 |
| Android SDK | 2-5分钟 | 跳过 |
| Maven 依赖 | 3-8分钟 | 1-2分钟 |
| **总计** | **6-15分钟** | **1-3分钟** |

---

## 🎯 何时必须使用代理

1. **公司网络**：有防火墙限制
2. **访问 GitHub**：需要下载 GitHub 上的资源
3. **镜像失效**：阿里云/腾讯云镜像不可用
4. **特殊插件**：某些 NativeScript 插件可能从国外下载

---

## 💡 建议

### 首次构建（当前）

1. ⏳ **先等待 5-10 分钟**
   - 镜像已配置，应该能正常下载
   - 观察终端的点点进度

2. 如果 10 分钟后还是很慢：
   ```powershell
   # 按 Ctrl+C 停止
   # 设置代理
   $env:HTTP_PROXY="http://127.0.0.1:7890"
   $env:HTTPS_PROXY="http://127.0.0.1:7890"
   # 重新启动
   npm run android
   ```

3. 查看是否有进度：
   ```powershell
   Get-Content mobile\build-log.txt -Tail 30
   ```

---

## 🔧 常用代理工具

| 工具 | 默认端口 | 设置方法 |
|------|----------|----------|
| Clash | 7890 | `http://127.0.0.1:7890` |
| V2rayN | 10809 | `http://127.0.0.1:10809` |
| SSR | 1080 | `socks5://127.0.0.1:1080` |
| Shadowsocks | 1080 | `socks5://127.0.0.1:1080` |

---

## ✅ 验证代理是否生效

```powershell
# 测试代理连接
curl -x http://127.0.0.1:7890 https://www.google.com -I

# 如果返回 200 OK，说明代理正常
```

---

## 📝 总结

**当前状态**：
- ✅ 已配置国内镜像（腾讯云 + 阿里云）
- ✅ 已优化 Gradle 性能
- ⏳ 首次构建正在进行中

**建议**：
1. **暂时不要开启代理**，先让镜像试试
2. **等待 5-10 分钟**观察进度
3. 如果确实很慢或超时，再开启代理
4. 使用临时环境变量方式，不要全局配置

**下次构建**：
- 有了缓存，构建会快很多（2-3分钟）
- 通常不再需要代理

