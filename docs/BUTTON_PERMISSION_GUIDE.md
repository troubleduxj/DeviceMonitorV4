# 按钮级权限控制功能说明

## 📋 功能概述

按钮级权限控制功能允许您在**角色管理的菜单权限配置**中，不仅可以勾选菜单，还能展开每个菜单，显示该页面下的具体按钮权限（如编辑、删除、导出等），实现**细粒度的权限控制**。

## 🎯 功能特点

1. **层级化权限管理** - 菜单 → 按钮的清晰层级结构
2. **可视化配置** - 在菜单权限树中直接勾选/取消勾选按钮权限
3. **统一权限体系** - 按钮权限作为菜单的一部分统一管理
4. **细粒度控制** - 可以精确控制每个按钮的显示和使用权限

## 📁 权限层级结构

```
📁 系统管理 (catalog - 目录)
  ├─ 📄 用户管理 (menu - 菜单)
  │   ├─ 🔘 新建用户 (button - 按钮)
  │   ├─ 🔘 编辑用户 (button - 按钮)
  │   ├─ 🔘 删除用户 (button - 按钮)
  │   ├─ 🔘 重置密码 (button - 按钮)
  │   ├─ 🔘 批量删除用户 (button - 按钮)
  │   └─ 🔘 导出用户 (button - 按钮)
  ├─ 📄 角色管理 (menu - 菜单)
  │   ├─ 🔘 新建角色 (button - 按钮)
  │   ├─ 🔘 编辑角色 (button - 按钮)
  │   ├─ 🔘 删除角色 (button - 按钮)
  │   └─ 🔘 分配权限 (button - 按钮)
  └─ 📄 菜单管理 (menu - 菜单)
      ├─ 🔘 新建菜单 (button - 按钮)
      ├─ 🔘 编辑菜单 (button - 按钮)
      └─ 🔘 删除菜单 (button - 按钮)
```

## 🚀 使用步骤

### 1. 初始化按钮权限数据

首先运行初始化脚本，为系统创建按钮权限记录：

```bash
# 进入项目目录
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2

# 运行初始化脚本
python scripts/init_button_permissions.py
```

**输出示例：**
```
============================================================
开始初始化按钮权限
============================================================

处理菜单: 用户管理 (ID: 10)
  ✅ 创建按钮权限: 新建用户 (POST /api/v2/users)
  ✅ 创建按钮权限: 编辑用户 (PUT /api/v2/users/{id})
  ✅ 创建按钮权限: 删除用户 (DELETE /api/v2/users/{id})
  ✅ 创建按钮权限: 重置密码 (POST /api/v2/users/{id}/actions/reset-password)
  ✅ 创建按钮权限: 批量删除用户 (DELETE /api/v2/users/batch)
  ✅ 创建按钮权限: 导出用户 (GET /api/v2/users/export)

处理菜单: 角色管理 (ID: 11)
  ✅ 创建按钮权限: 新建角色 (POST /api/v2/roles)
  ...

============================================================
按钮权限初始化完成！
  新创建: 32 个
  已跳过: 0 个
============================================================
```

### 2. 在角色管理中配置按钮权限

1. **打开角色管理页面**
   - 导航至：系统管理 → 角色管理

2. **选择角色并分配权限**
   - 点击角色列表中的"分配权限"按钮
   - 切换到"菜单权限"标签页

3. **展开菜单查看按钮权限**
   - 点击菜单项前的展开图标
   - 查看该菜单下的所有按钮权限
   - 每个按钮权限会显示：
     - 🔘 图标（按钮类型）
     - 按钮名称
     - HTTP方法标签（GET/POST/PUT/DELETE）
     - "按钮"类型标签

4. **勾选/取消勾选按钮权限**
   - 勾选整个菜单 → 自动勾选该菜单下的所有按钮
   - 单独勾选按钮 → 只授予该按钮的权限
   - 取消勾选按钮 → 移除该按钮的权限

5. **保存配置**
   - 点击"确定"保存权限配置

### 3. 验证权限配置

1. **使用配置的角色登录**
   - 退出当前用户
   - 使用已配置权限的角色账号登录

2. **检查按钮显示**
   - 访问相应的页面
   - 有权限的按钮：正常显示且可点击
   - 无权限的按钮：被禁用或隐藏

## 🎨 按钮权限的视觉效果

### 菜单权限树中的显示

- **目录节点**：📁 蓝色图标 + "目录"标签
- **菜单节点**：📄 绿色图标 + "菜单"标签  
- **按钮节点**：🔘 橙色图标 + HTTP方法标签 + "按钮"标签
  - GET: 绿色标签
  - POST: 蓝色标签
  - PUT: 橙色标签
  - DELETE: 红色标签

### 按钮节点的特殊样式

- 浅黄色背景（#fffbf0）
- 左侧橙色边框
- 较小的字体（13px）
- 鼠标悬停时背景变为更深的黄色（#fff7e6）

## 💡 权限检查逻辑

### 前端权限检查流程

```
用户点击按钮
    ↓
1. 检查是否有 token?
    ↓ 否 → ❌ 禁用按钮
    ↓ 是
2. 检查是否为超级管理员?
    ↓ 是 → ✅ 直接允许
    ↓ 否
3. 检查菜单权限列表（包含按钮权限）
    ↓
在 menuPermissions 中查找
    ↓ 找到 → ✅ 允许
    ↓ 找不到
4. 检查 API 权限列表
    ↓
在 accessApis 中查找
    ↓ 找到 → ✅ 允许
    ↓ 找不到 → ❌ 禁用按钮
```

### 按钮权限标识格式

```
HTTP方法 + 空格 + API路径

示例：
- POST /api/v2/users
- PUT /api/v2/users/{id}
- DELETE /api/v2/users/{id}
- GET /api/v2/users/export
```

## 📊 已配置的按钮权限

### 用户管理
- 🔘 新建用户 - `POST /api/v2/users`
- 🔘 编辑用户 - `PUT /api/v2/users/{id}`
- 🔘 删除用户 - `DELETE /api/v2/users/{id}`
- 🔘 重置密码 - `POST /api/v2/users/{id}/actions/reset-password`
- 🔘 批量删除用户 - `DELETE /api/v2/users/batch`
- 🔘 导出用户 - `GET /api/v2/users/export`

### 角色管理
- 🔘 新建角色 - `POST /api/v2/roles`
- 🔘 编辑角色 - `PUT /api/v2/roles/{id}`
- 🔘 删除角色 - `DELETE /api/v2/roles/{id}`
- 🔘 分配权限 - `POST /api/v2/roles/{id}/permissions`

### 菜单管理
- 🔘 新建菜单 - `POST /api/v2/menus`
- 🔘 编辑菜单 - `PUT /api/v2/menus/{id}`
- 🔘 删除菜单 - `DELETE /api/v2/menus/{id}`

### 部门管理
- 🔘 新建部门 - `POST /api/v2/departments`
- 🔘 编辑部门 - `PUT /api/v2/departments/{id}`
- 🔘 删除部门 - `DELETE /api/v2/departments/{id}`

### 设备管理
- 🔘 新建设备 - `POST /api/v2/devices`
- 🔘 编辑设备 - `PUT /api/v2/devices/{id}`
- 🔘 删除设备 - `DELETE /api/v2/devices/{id}`
- 🔘 导出设备 - `GET /api/v2/devices/export`

### 维修记录
- 🔘 新建维修记录 - `POST /api/v2/device/maintenance/repair-records`
- 🔘 编辑维修记录 - `PUT /api/v2/device/maintenance/repair-records/{id}`
- 🔘 删除维修记录 - `DELETE /api/v2/device/maintenance/repair-records/{id}`
- 🔘 导出维修记录 - `GET /api/v2/device/maintenance/repair-records/export`

### 字典管理
- 🔘 新建字典类型 - `POST /api/v2/dict-types`
- 🔘 编辑字典类型 - `PUT /api/v2/dict-types/{id}`
- 🔘 删除字典类型 - `DELETE /api/v2/dict-types/{id}`
- 🔘 新建字典数据 - `POST /api/v2/dict-data`
- 🔘 编辑字典数据 - `PUT /api/v2/dict-data/{id}`
- 🔘 删除字典数据 - `DELETE /api/v2/dict-data/{id}`

## 🔧 添加新的按钮权限

### 方法1：通过初始化脚本添加（推荐）

1. 编辑 `scripts/init_button_permissions.py`
2. 在 `BUTTON_PERMISSIONS` 列表中添加新配置：

```python
{
    "parent_menu_name": "您的菜单名称",
    "buttons": [
        {
            "name": "按钮名称",
            "perms": "HTTP方法 /api/路径",
            "icon": "material-symbols:icon-name",
            "order": 1
        }
    ]
}
```

3. 运行脚本：`python scripts/init_button_permissions.py`

### 方法2：直接在数据库中添加

```sql
INSERT INTO t_sys_menu (
    name, path, component, menu_type, icon, 
    order_num, parent_id, perms, visible, status,
    is_frame, is_cache
) VALUES (
    '按钮名称',           -- name
    '',                  -- path (按钮不需要路径)
    '',                  -- component (按钮不需要组件)
    'button',            -- menu_type
    'material-symbols:icon-name',  -- icon
    1,                   -- order_num
    [父菜单ID],          -- parent_id
    'POST /api/v2/xxx',  -- perms (权限标识)
    true,                -- visible
    true,                -- status
    false,               -- is_frame
    false                -- is_cache
);
```

## 🎯 最佳实践

### 1. 权限粒度设计

- **粗粒度**：只控制菜单访问 → 用户要么能访问整个页面，要么不能
- **细粒度**：控制到按钮级别 → 用户可以查看页面但不能编辑/删除

### 2. 权限命名规范

```
[HTTP方法] /api/v2/[资源]/[操作]

示例：
- POST /api/v2/users              (创建)
- GET /api/v2/users               (列表)
- GET /api/v2/users/{id}          (详情)
- PUT /api/v2/users/{id}          (更新)
- DELETE /api/v2/users/{id}       (删除)
- DELETE /api/v2/users/batch      (批量删除)
- GET /api/v2/users/export        (导出)
```

### 3. 角色设计建议

- **超级管理员**：拥有所有权限（自动通过所有权限检查）
- **管理员**：拥有大部分管理权限（可以新建、编辑、删除）
- **操作员**：拥有基本操作权限（可以新建、编辑）
- **查看者**：只有查看权限（只能查看列表和详情）

## 🐛 常见问题

### Q1: 初始化脚本运行后按钮权限没有显示？

**A:** 检查以下几点：
1. 确认脚本成功执行且没有报错
2. 清除浏览器缓存并重新登录
3. 检查父菜单名称是否正确（区分大小写）
4. 查看数据库中是否真的创建了按钮权限记录

### Q2: 勾选了按钮权限但按钮仍然不可用？

**A:** 可能的原因：
1. 没有保存权限配置
2. 需要重新登录才能生效
3. 按钮的权限标识与配置的不匹配
4. 检查 PermissionButton 组件的 permission 属性是否正确

### Q3: 按钮权限在菜单树中显示异常？

**A:** 检查：
1. 菜单数据的 type 或 menuType 字段是否为 'button'
2. 父菜单的 ID 是否正确
3. 浏览器控制台是否有错误信息

### Q4: 如何批量为多个角色分配相同的按钮权限？

**A:** 可以通过SQL批量插入：
```sql
-- 假设要为角色 ID 2, 3, 4 分配按钮权限 ID 100, 101, 102
INSERT INTO t_sys_role_menu (role_id, menu_id)
SELECT role_id, menu_id FROM (
  SELECT 2 as role_id, 100 as menu_id UNION ALL
  SELECT 2, 101 UNION ALL
  SELECT 2, 102 UNION ALL
  SELECT 3, 100 UNION ALL
  SELECT 3, 101 UNION ALL
  SELECT 3, 102 UNION ALL
  SELECT 4, 100 UNION ALL
  SELECT 4, 101 UNION ALL
  SELECT 4, 102
) AS temp;
```

## 📚 相关文件

### 后端文件
- `app/schemas/menus.py` - MenuType 枚举定义
- `app/api/v2/auth.py` - 菜单权限接口
- `app/models/admin.py` - Menu 模型
- `scripts/init_button_permissions.py` - 按钮权限初始化脚本

### 前端文件
- `web/src/components/system/MenuPermissionTree.vue` - 菜单权限树组件
- `web/src/store/modules/permission/enhanced-permission-store.ts` - 权限 Store
- `web/src/components/Permission/PermissionButton.vue` - 权限按钮组件
- `web/src/directives/permission.js` - 权限指令

## 📝 更新日志

### v1.0.0 (2025-10-29)
- ✅ 添加 BUTTON 类型到 MenuType 枚举
- ✅ 修改 MenuPermissionTree 组件支持按钮权限显示
- ✅ 更新后端菜单接口返回按钮权限数据
- ✅ 创建按钮权限初始化脚本
- ✅ 更新前端权限检查逻辑
- ✅ 为8个主要页面创建按钮权限配置

---

**最后更新时间：** 2025-10-29  
**版本：** v1.0.0  
**作者：** DeviceMonitor Team

