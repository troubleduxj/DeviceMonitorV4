# 模拟设备Mock数据 - 手动安装指南

## 🎯 由于数据库连接问题，请使用以下手动方式

---

## 📝 方法1：使用pgAdmin执行（推荐）⭐

### 步骤详解：

#### 1️⃣ 打开pgAdmin
- 启动pgAdmin应用程序
- 输入主密码（如果需要）

#### 2️⃣ 连接到数据库
- 在左侧树形菜单中找到：
  ```
  Servers
    └─ PostgreSQL
        └─ Databases
            └─ device_monitor
  ```
- 点击 `device_monitor` 展开

#### 3️⃣ 打开查询工具
- 右键点击 `device_monitor`
- 选择 **"Query Tool"** (查询工具)
- 或使用快捷键：`Alt + Shift + Q`

#### 4️⃣ 打开SQL文件
- 在查询工具窗口中，点击 **"Open File"** (打开文件) 图标 📁
- 或使用快捷键：`Ctrl + O`
- 导航到文件：
  ```
  D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\database\migrations\insert_simulation_device_mocks.sql
  ```
- 点击"打开"

#### 5️⃣ 执行SQL
- 检查SQL内容已正确加载
- 点击 **"Execute/Refresh"** (执行/刷新) 按钮 ▶️
- 或使用快捷键：`F5`

#### 6️⃣ 验证结果
- 查看底部的"Messages"（消息）面板
- 应该看到成功提示：
  ```
  ✅ 模拟设备Mock规则插入完成！
  已插入的Mock规则:
    1. 模拟设备分类-设备列表 (5台设备)
    2. 模拟设备-详情信息
    3. 模拟设备-实时数据
    4. 模拟设备-历史数据 (2025-10-29全天24小时)
    5. 模拟设备-统计数据
  ```

---

## 📝 方法2：直接复制SQL到pgAdmin

如果打开文件失败，可以手动复制SQL：

### 步骤：

#### 1️⃣ 打开SQL文件
- 使用记事本或VSCode打开：
  ```
  D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\database\migrations\insert_simulation_device_mocks.sql
  ```

#### 2️⃣ 全选复制
- 按 `Ctrl + A` 全选
- 按 `Ctrl + C` 复制

#### 3️⃣ 粘贴到pgAdmin
- 在pgAdmin的查询工具中
- 按 `Ctrl + V` 粘贴SQL代码

#### 4️⃣ 执行
- 按 `F5` 执行

---

## 📝 方法3：使用psql命令行（高级用户）

如果PostgreSQL的bin目录在PATH中：

```bash
# 打开命令提示符（CMD，不是PowerShell）
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2

# 执行SQL文件
psql -h localhost -p 5432 -U postgres -d device_monitor -f database\migrations\insert_simulation_device_mocks.sql
```

输入密码：`Hanatech@123`

---

## ✅ 插入后的验证

### 在pgAdmin中验证：

执行以下查询查看插入的规则：

```sql
-- 查看所有模拟设备Mock规则
SELECT 
    id,
    name,
    url_pattern,
    method,
    response_status,
    enabled,
    priority,
    description
FROM t_sys_mock_data
WHERE description LIKE '%模拟设备%'
ORDER BY priority DESC, id;
```

**预期结果：** 应该返回5行记录

### 在前端验证：

1. **刷新浏览器** (Ctrl + Shift + R)
2. **访问Mock管理页面**：
   - 导航到：高级设置 → Mock数据管理
3. **查看规则列表**：
   - 应该看到5条新的Mock规则
   - 规则名称包含"模拟设备"字样

---

## 📋 插入的Mock规则列表

插入成功后，你将看到以下5条规则：

| # | 规则名称 | URL模式 | 方法 | 说明 |
|---|---------|---------|------|------|
| 1 | 模拟设备分类-设备列表 | `/api/v2/devices.*device_type=simulation` | GET | 5台模拟设备 |
| 2 | 模拟设备-详情信息 | `/api/v2/devices/100[1-5]$` | GET | 设备详细信息 |
| 3 | 模拟设备-实时数据 | `/api/v2/devices/100[1-5]/realtime` | GET | 实时监测数据 |
| 4 | 模拟设备-历史数据 | `/api/v2/devices/100[1-5]/history` | GET | 10-29历史数据 |
| 5 | 模拟设备-统计数据 | `/api/v2/devices/statistics.*device_type=simulation` | GET | 统计汇总 |

---

## 🚀 下一步操作

### 1️⃣ 启用Mock规则

在Mock管理页面中：
- [ ] 找到"模拟设备分类-设备列表"→ 点击"启用"
- [ ] 找到"模拟设备-详情信息"→ 点击"启用"
- [ ] 找到"模拟设备-实时数据"→ 点击"启用"
- [ ] 找到"模拟设备-历史数据"→ 点击"启用"
- [ ] 找到"模拟设备-统计数据"→ 点击"启用"

### 2️⃣ 启用全局Mock开关

- [ ] 在Mock管理页面右上角
- [ ] 点击"启用Mock"按钮
- [ ] 确认按钮显示为"已启用"状态

### 3️⃣ 查看模拟设备

- [ ] 导航到：设备管理 → 设备信息管理
- [ ] 设备类型选择：**模拟设备**
- [ ] 点击"查询"按钮
- [ ] 应该显示5台模拟设备 🎉

---

## 🎨 模拟设备数据预览

### 设备列表（5台）

```
┌────────────────┬──────────────────┬─────────┬──────┐
│ 设备编号       │ 设备名称         │ 位置    │ 状态 │
├────────────────┼──────────────────┼─────────┼──────┤
│ SIM-DEV-001    │ 模拟温控设备A    │ A区     │ 运行 │
│ SIM-DEV-002    │ 模拟压力监测设备B│ B区     │ 运行 │
│ SIM-DEV-003    │ 模拟流量计设备C  │ C区     │ 运行 │
│ SIM-DEV-004    │ 模拟能耗监控设备D│ D区     │ 维护 │
│ SIM-DEV-005    │ 模拟振动传感设备E│ E区     │ 运行 │
└────────────────┴──────────────────┴─────────┴──────┘
```

### 实时数据示例（任意设备）

```
📊 监测指标：
  🌡️ 温度：45.8°C     [正常]
  💨 压力：2.3 MPa    [正常]
  💧 流量：125.6 L/min [正常]
  ⚡ 功耗：2.15 kW    [正常]
  📳 振动：0.8 mm/s   [正常]
  📈 效率：92.5%      [优秀]
```

### 历史数据（2025-10-29）

```
24小时完整数据点
每小时1个数据点
包含温度、压力、流量、功耗、振动、效率
```

---

## 🔍 故障排除

### 问题1：SQL执行报错

**错误示例：**
```
ERROR:  duplicate key value violates unique constraint
```

**原因：** 规则已存在

**解决：**
- 这是正常的，表示规则已经插入过了
- 直接进行下一步：启用Mock规则

---

### 问题2：看不到插入的规则

**检查步骤：**

1. 在pgAdmin中执行：
```sql
SELECT COUNT(*) FROM t_sys_mock_data WHERE description LIKE '%模拟设备%';
```

2. 如果返回0，说明插入失败，重新执行SQL
3. 如果返回5，说明插入成功，刷新浏览器

---

### 问题3：启用后看不到模拟设备

**检查清单：**

- [ ] Mock规则是否已启用（5条）
- [ ] 全局Mock开关是否已开启
- [ ] 设备类型筛选是否选择"模拟设备"
- [ ] 浏览器是否已刷新（Ctrl + Shift + R）

**控制台检查：**
```javascript
// 在浏览器控制台执行
window.__mockInterceptor.getStats()

// 应该显示：
// {
//   enabled: true,
//   rulesCount: 5,
//   hitCount: 0
// }
```

---

## 📞 需要帮助？

如果以上方法都失败，请：

1. **检查PostgreSQL服务**
   - 打开"服务"（services.msc）
   - 查找"postgresql-x64-xx"
   - 确认状态为"正在运行"

2. **检查数据库密码**
   - 确认密码是否为：`Hanatech@123`
   - 尝试在pgAdmin中重新连接

3. **查看详细文档**
   - [模拟设备Mock完整指南](./SIMULATION_DEVICE_MOCK_GUIDE.md)
   - [Mock功能使用指南](./MOCK_USAGE_GUIDE.md)

---

## ✨ 快速开始文档

安装完成后，查看快速开始：
→ [docs/SIMULATION_DEVICE_QUICK_START.md](./SIMULATION_DEVICE_QUICK_START.md)

---

**最后更新：** 2025-10-30  
**版本：** 1.0.0  
**适用场景：** 数据库连接失败时的手动安装

