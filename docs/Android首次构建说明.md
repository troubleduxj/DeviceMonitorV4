# Android 首次构建说明

## 📊 当前构建状态

### ✅ 已完成
1. ✅ npm 依赖安装完成（1192包，34秒）
2. ✅ Webpack 编译成功（0 errors, 19 warnings, 3秒）
3. ✅ Gradle 8.14.3 下载完成（腾讯云镜像）
4. ⏳ **正在构建 Android APK**（首次构建通常需要 5-15 分钟）

### 🔄 构建阶段
```
npm install         ✅ 完成（34秒）
├─ Webpack 编译     ✅ 完成（3秒）
├─ Gradle 下载      ✅ 完成
└─ Android 构建     ⏳ 进行中（当前阶段）
   ├─ 下载依赖      ⏳ 可能还在下载
   ├─ 编译代码      ⏳ 等待中
   ├─ 打包 APK      ⏳ 等待中
   └─ 安装到设备    ⏳ 等待中
```

---

## ⏱️ 预计时间

| 阶段 | 首次 | 后续 |
|------|------|------|
| npm install | 30-60秒 | 10-20秒 |
| Webpack | 3-10秒 | 1-3秒 |
| Gradle 下载 | 1-3分钟 | 跳过 |
| **Android 构建** | **5-15分钟** | **2-5分钟** |
| **总计** | **6-20分钟** | **2-5分钟** |

---

## 🚀 加速构建的方法

### 1. 增加 Gradle 内存
已自动创建 `mobile/platforms/android/gradle.properties`：
```properties
org.gradle.jvmargs=-Xmx4096m
org.gradle.parallel=true
org.gradle.daemon=true
org.gradle.caching=true
```

### 2. 使用国内镜像（已配置）
- ✅ Gradle：腾讯云镜像
- ✅ Maven：阿里云镜像（如需配置见下方）

### 3. 配置 Maven 镜像（可选）
在 `mobile/platforms/android/build.gradle` 中添加：
```gradle
allprojects {
    repositories {
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/public' }
        maven { url 'https://maven.aliyun.com/repository/jcenter' }
        google()
        mavenCentral()
    }
}
```

---

## 🔍 查看构建进度

### 方法 1：查看终端输出
终端中的 `.` 表示 Gradle 正在工作：
```
Webpack compilation complete. Watching for file changes.
..................................................
```

### 方法 2：查看任务管理器
1. 打开任务管理器（Ctrl+Shift+Esc）
2. 查找 `java.exe` 进程
3. 如果 CPU 使用率 >30%，说明正在构建

### 方法 3：查看文件生成
检查是否生成了构建产物：
```powershell
Get-ChildItem "D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile\platforms\android\app\build\outputs" -Recurse
```

---

## ❌ 如果构建卡住

### 1. 检查网络
- 确保可以访问 GitHub、Maven Central
- 考虑使用 VPN 或镜像

### 2. 清理并重建
```bash
cd mobile
npx ns clean
npm run android
```

### 3. 手动清理 Gradle 缓存
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.gradle\caches"
```

### 4. 增加构建超时
在 `mobile/platforms/android/gradle.properties` 添加：
```properties
systemProp.http.socketTimeout=600000
systemProp.http.connectionTimeout=600000
```

---

## 📱 构建成功后

会看到以下输出：
```
BUILD SUCCESSFUL in 8m 32s
Installing on emulator-5554...
Successfully installed on device with identifier 'emulator-5554'.
```

然后自动启动应用！🎉

---

## 💡 提示

1. **首次构建很慢是正常的**，需要下载大量依赖
2. **不要中断构建**，即使看起来卡住了
3. **后续构建会快很多**（2-5分钟）
4. **保持网络连接稳定**

---

## 🔗 相关文档

- [Android环境配置指南](./Android环境配置指南-Windows.md)
- [Android Studio安装步骤](./Android-Studio-安装步骤速查.md)
- [移动端快速启动指南](./移动端快速启动指南.md)

