# 前端启动指南 - 最终版

## 🎉 已完成修复

### 修改内容

1. **vite.config.js** - 修改监听地址
   ```javascript
   server: {
     host: '0.0.0.0',  // 监听所有网络接口
     port: VITE_PORT || 3001,
     strictPort: false,  // 自动尝试下一个端口
   }
   ```

2. **package.json** - 添加端口参数
   ```json
   "scripts": {
     "dev": "vite --port 3001 --host 0.0.0.0",
     "dev:3000": "vite --port 3000 --host 0.0.0.0",
     "dev:5173": "vite --port 5173 --host 0.0.0.0"
   }
   ```

---

## 🚀 现在请执行

### 在管理员PowerShell中运行：

```powershell
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\web
npm run dev
```

---

## 📝 预期结果

```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3001/
  ➜  Network: http://192.168.x.x:3001/
  ➜  press h to show help
```

---

## 🌐 访问地址

- **本地访问**: http://localhost:3001
- **网络访问**: http://0.0.0.0:3001
- **回环地址**: http://127.0.0.1:3001

---

## 🔧 如果还有问题

### 方案A: 尝试其他端口

```powershell
npm run dev:3000   # 使用3000端口
```

### 方案B: 临时禁用防火墙

Windows安全中心 → 防火墙和网络保护 → 专用网络 → 关闭（测试完记得开启）

### 方案C: 添加防火墙规则

```powershell
# 允许Node.js访问网络
New-NetFirewallRule -DisplayName "Vite Dev Server" -Direction Inbound -Protocol TCP -LocalPort 3001 -Action Allow
```

---

## ✅ 启动成功后

1. **访问**: http://localhost:3001
2. **登录**: 使用管理员账号
3. **检查**: 左侧菜单是否有"数据模型管理"

---

## 📞 下一步

如果前端成功启动，请执行：

```powershell
# 返回项目根目录
cd ..

# 执行数据库菜单脚本
python database/migrations/device-data-model/execute_menu_migration.py
```

---

**关键改动**: 使用 `0.0.0.0` 代替 `127.0.0.1`，避免Windows权限问题！

