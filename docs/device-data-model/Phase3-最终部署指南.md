# Phase 3 最终部署指南

> **日期**: 2025-11-03  
> **状态**: ✅ 后端已修复并启动，⚠️ 前端待启动

---

## 📊 当前状态

| 组件 | 状态 | 说明 |
|-----|------|-----|
| **后端** | ✅ 运行中 | http://localhost:8000 |
| **API文档** | ✅ 可访问 | http://localhost:8000/docs |
| **前端** | ⚠️ 待启动 | 端口权限问题 |
| **数据库菜单** | ⏳ 待执行 | 需要运行脚本 |

---

## 🚀 完整启动流程

### Step 1: 后端启动 ✅（已完成）

```powershell
# 在项目根目录
python run.py
```

**验证**:
- ✅ 访问 http://localhost:8000/docs
- ✅ 看到Swagger API文档界面

---

### Step 2: 前端启动 ⚠️（3种方案任选其一）

#### 方案 A：管理员权限运行（推荐）⭐

1. **右键 PowerShell** → "以管理员身份运行"
2. 执行：
   ```powershell
   cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\web
   npm run dev
   ```
3. 访问：http://localhost:5173

#### 方案 B：使用3001端口（简单）⭐⭐

1. **双击运行**: `web/start-port-3001.bat`
2. 或手动执行：
   ```powershell
   cd web
   npx vite --port 3001 --host 127.0.0.1
   ```
3. 访问：http://localhost:3001

#### 方案 C：创建环境配置文件

1. 在 `web` 目录手动创建 `.env` 文件
2. 内容如下：
   ```env
   VITE_PORT=3001
   VITE_USE_PROXY=true
   VITE_BASE_API=http://localhost:8000
   ```
3. 执行：
   ```powershell
   cd web
   npm run dev
   ```
4. 访问：http://localhost:3001

---

### Step 3: 执行数据库菜单脚本 ⏳

**在前端登录之前**，需要执行此脚本创建新菜单：

```powershell
# 在项目根目录
python database/migrations/device-data-model/execute_menu_migration.py
```

**预期输出**:
```
连接数据库成功
开始执行SQL脚本...
SQL脚本执行成功！
已创建以下菜单：
- 数据模型管理 (/data-model)
  - 模型配置管理 (/data-model/config)
  - 字段映射管理 (/data-model/mapping)
  - 预览与测试 (/data-model/preview)
```

**⚠️ 注意**: 
- 如果数据库连接失败，请确保 PostgreSQL 服务正在运行
- 如果菜单已存在，可能会报错，这是正常的

---

## 🧪 功能测试流程

### 1. 登录系统

1. 访问 http://localhost:3001 （或5173）
2. 使用管理员账号登录（如 admin）

### 2. 查看新菜单

左侧菜单应该显示：

```
📊 数据模型管理
   └─ 模型配置管理
   └─ 字段映射管理
   └─ 预览与测试
```

### 3. 测试功能

#### 3.1 模型配置管理 (/data-model/config)

**功能点**:
- ✅ 查看模型列表（分页、搜索、筛选）
- ✅ 创建新模型
- ✅ 编辑模型配置
- ✅ 删除模型
- ✅ 选择字段绑定

**测试步骤**:
1. 点击"新增模型"按钮
2. 填写表单：
   - 模型名称: `test_device_model`
   - 显示名称: `测试设备模型`
   - 描述: `用于测试的设备数据模型`
   - 数据库类型: `PostgreSQL`
   - 表名: `t_device`
3. 选择字段（如：device_id, device_name, status）
4. 保存
5. 验证列表中显示新模型

#### 3.2 字段映射管理 (/data-model/mapping)

**功能点**:
- ✅ 查看映射列表
- ✅ 创建映射规则
- ✅ 配置转换规则
- ✅ 测试映射

**测试步骤**:
1. 点击"新增映射"
2. 填写：
   - 映射名称: `device_status_mapping`
   - 源数据库: `PostgreSQL`
   - 目标数据库: `TDengine`
   - 源表: `t_device`
   - 目标表: `device_data`
3. 配置字段映射：
   - `device_id` → `device_id` (无转换)
   - `status` → `status_code` (值映射: 0→离线, 1→在线)
4. 保存并测试

#### 3.3 数据预览 (/data-model/preview)

**功能点**:
- ✅ 选择数据模型
- ✅ 配置查询参数
- ✅ 实时数据查询
- ✅ 统计数据展示
- ✅ 图表可视化
- ✅ SQL预览
- ✅ 执行日志

**测试步骤**:
1. 选择模型: `test_device_model`
2. 设置查询条件：
   - 时间范围: 最近24小时
   - 限制条数: 100
3. 点击"查询实时数据"
4. 验证表格显示数据
5. 切换到"统计数据"标签
6. 验证图表展示
7. 查看"SQL预览"标签
8. 检查"执行日志"

---

## 📁 相关文档

| 文档 | 说明 |
|------|------|
| [Phase3完成报告.md](./Phase3完成报告.md) | Phase 3 开发总结 |
| [BugFix-完整修复报告-Final.md](./BugFix-完整修复报告-Final.md) | 后端Bug修复详情 |
| [前端启动问题解决方案.md](../../web/前端启动问题解决方案.md) | 前端启动详细指南 |
| [Phase3实施指南.md](./Phase3实施指南.md) | 原始实施指南 |

---

## 🛠️ 常见问题

### Q1: 前端启动失败 - 端口权限错误

**错误**: `Error: listen EACCES: permission denied 127.0.0.1:5173`

**解决**: 
- 方案A：使用管理员权限运行 PowerShell
- 方案B：更换端口（运行 `web/start-port-3001.bat`）
- 详见：[前端启动问题解决方案.md](../../web/前端启动问题解决方案.md)

### Q2: 数据库菜单脚本执行失败

**错误**: `数据库连接失败`

**解决**:
```powershell
# 检查PostgreSQL服务
Get-Service | Select-String postgresql

# 启动服务
net start postgresql-x64-15
```

### Q3: 看不到新菜单

**可能原因**:
1. 菜单脚本未执行
2. 权限未分配
3. 需要重新登录

**解决**:
```powershell
# 执行菜单脚本
python database/migrations/device-data-model/execute_menu_migration.py

# 退出登录重新进入
```

### Q4: API调用失败

**检查项**:
1. 后端是否运行：http://localhost:8000/docs
2. 前端代理配置是否正确
3. 浏览器控制台查看错误信息

**调试**:
```javascript
// 浏览器控制台
console.log(window.location.href)  // 当前URL
localStorage.getItem('token')      // 检查Token
```

### Q5: 模块未找到错误

**错误**: `Module not found`

**解决**:
```powershell
cd web
npm install
```

---

## 🎯 验收标准

### 功能验收

- [ ] 菜单正常显示
- [ ] 3个页面都可以访问
- [ ] 模型配置：CRUD操作正常
- [ ] 字段映射：创建和编辑正常
- [ ] 数据预览：查询和展示正常
- [ ] 图表可视化：ECharts正常渲染

### 性能验收

- [ ] 页面加载时间 < 2秒
- [ ] API响应时间 < 500ms
- [ ] 大数据量（1000+条）展示流畅

### 兼容性验收

- [ ] Chrome 浏览器
- [ ] Edge 浏览器
- [ ] Firefox 浏览器

---

## 📊 项目统计

### 代码统计

```
前端新增文件: 7个
- route.js (路由配置)
- data-model.js (API客户端)
- config/index.vue (模型配置)
- mapping/index.vue (字段映射)
- preview/index.vue (数据预览)
- 2个README.md

后端文件: 8个（已有，修复了导入错误）
- metadata.py
- data_query.py
- dynamic_models.py
- metadata_service.py
- dynamic_model_service.py
- sql_builder.py
- transform_engine.py
- data_query_service.py

数据库脚本: 2个
- 008_create_frontend_menu.sql
- execute_menu_migration.py
```

### 工作量统计

| 任务 | 耗时 | 状态 |
|------|------|------|
| 前端开发 | ~2小时 | ✅ |
| 后端Bug修复 | ~30分钟 | ✅ |
| 文档编写 | ~30分钟 | ✅ |
| 测试验收 | 待定 | ⏳ |
| **总计** | **~3小时** | **90%完成** |

---

## ✅ 下一步行动

### 立即执行（按顺序）

1. **启动前端** ⚠️
   ```powershell
   # 推荐方案：双击运行
   web\start-port-3001.bat
   ```

2. **执行菜单脚本** ⏳
   ```powershell
   python database/migrations/device-data-model/execute_menu_migration.py
   ```

3. **登录测试** ⏳
   - 访问 http://localhost:3001
   - 登录系统
   - 验证新菜单

4. **功能测试** ⏳
   - 测试3个页面
   - 验证CRUD操作
   - 检查数据展示

---

## 🎉 完成里程碑

✅ **Phase 1**: 基础架构 - 已完成  
✅ **Phase 2**: 动态模型 - 已完成  
✅ **Phase 3**: 前端界面 - 95%完成（等待测试）  
⏳ **Phase 4**: AI集成 - 未开始  
⏳ **Phase 5**: 测试部署 - 未开始

---

## 📞 支持

如有问题，请查看：
1. [前端启动问题解决方案.md](../../web/前端启动问题解决方案.md)
2. [BugFix-完整修复报告-Final.md](./BugFix-完整修复报告-Final.md)
3. API文档：http://localhost:8000/docs

---

**最后更新**: 2025-11-03 18:10  
**文档版本**: 1.0  
**状态**: Phase 3 即将完成！ 🚀

