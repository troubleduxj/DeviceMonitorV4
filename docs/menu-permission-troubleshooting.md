# 菜单权限问题排查指南

## 问题描述
用户反馈：不管怎么配置demo用户的角色，其菜单没有变化，比如维修记录功能对应菜单一直不显示。

## 问题分析

### 可能的原因

1. **数据库中缺少菜单数据**
   - 维修记录相关菜单没有在数据库中创建
   - 菜单状态被禁用

2. **角色权限配置问题**
   - 角色没有分配相应的菜单权限
   - 用户没有正确分配角色

3. **权限缓存问题**
   - 权限数据被缓存，修改后没有及时更新
   - 前端权限Store缓存没有刷新

4. **菜单权限标识不匹配**
   - 菜单的权限标识(perms)与角色权限不匹配
   - 权限检查逻辑有问题

## 排查步骤

### 1. 检查数据库菜单数据

```sql
-- 查看所有菜单
SELECT id, name, path, perms, status, parent_id FROM t_sys_menu ORDER BY order_num;

-- 查找维修相关菜单
SELECT id, name, path, perms, status FROM t_sys_menu WHERE name LIKE '%维修%' OR path LIKE '%repair%';

-- 检查菜单状态
SELECT id, name, status FROM t_sys_menu WHERE status = '1'; -- 禁用的菜单
```

### 2. 检查用户角色分配

```sql
-- 查看用户角色
SELECT u.username, r.role_name, r.status 
FROM t_sys_user u 
JOIN t_sys_user_role ur ON u.id = ur.user_id 
JOIN t_sys_role r ON ur.role_id = r.id 
WHERE u.username = 'demo';

-- 查看角色菜单权限
SELECT r.role_name, m.name as menu_name, m.path, m.perms 
FROM t_sys_role r 
JOIN t_sys_role_menu rm ON r.id = rm.role_id 
JOIN t_sys_menu m ON rm.menu_id = m.id 
WHERE r.role_name = '目标角色名';
```

### 3. 使用前端调试工具

在浏览器控制台执行：

```javascript
// 调试用户权限
permissionDebugger.debugUserPermissions()

// 调试菜单生成
permissionDebugger.debugMenuGeneration()

// 生成权限报告
permissionDebugger.generatePermissionReport()

// 检查特定权限
permissionDebugger.checkPermission('device:maintenance:repair:list')
```

### 4. 检查API响应

在浏览器Network面板查看：

```
GET /api/v2/auth/user/menu
```

检查返回的菜单数据是否包含维修记录相关菜单。

## 解决方案

### 方案1：创建缺失的菜单数据

如果数据库中缺少维修记录菜单，需要手动创建：

```sql
-- 创建设备维护父菜单
INSERT INTO t_sys_menu (name, path, component, menu_type, icon, order_num, parent_id, perms, visible, status, is_frame, is_cache, created_at, updated_at) 
VALUES ('设备维护', '/device-maintenance', 'Layout', 'M', 'material-symbols:build', 4, NULL, 'device:maintenance', true, true, false, true, NOW(), NOW());

-- 获取父菜单ID（假设为100）
-- 创建维修记录子菜单
INSERT INTO t_sys_menu (name, path, component, menu_type, icon, order_num, parent_id, perms, visible, status, is_frame, is_cache, created_at, updated_at) 
VALUES ('维修记录', 'repair-records', 'device-maintenance/repair-records/index', 'C', 'material-symbols:build-circle', 1, 100, 'device:maintenance:repair:list', true, true, false, true, NOW(), NOW());
```

### 方案2：配置角色菜单权限

```sql
-- 为角色分配菜单权限（假设角色ID为2，菜单ID为101）
INSERT INTO t_sys_role_menu (role_id, menu_id) VALUES (2, 100); -- 设备维护
INSERT INTO t_sys_role_menu (role_id, menu_id) VALUES (2, 101); -- 维修记录
```

### 方案3：清除权限缓存

在前端执行：

```javascript
// 清除权限缓存并重新加载
const permissionStore = useEnhancedPermissionStore()
await permissionStore.refreshPermissions()

// 或者重新登录
const userStore = useUserStore()
await userStore.logout()
// 然后重新登录
```

### 方案4：修复权限检查逻辑

如果权限检查逻辑有问题，检查以下文件：

1. `web/src/store/modules/permission/enhanced-permission-store.js` - 权限Store
2. `web/src/router/guard/permission-guard.js` - 路由守卫
3. `web/src/composables/usePermission.js` - 权限检查组合式函数

## 预防措施

### 1. 数据初始化脚本

创建菜单数据初始化脚本，确保所有必要的菜单都存在：

```python
# scripts/init_menus.py
async def init_device_maintenance_menus():
    # 创建设备维护相关菜单
    pass
```

### 2. 权限配置验证

添加权限配置验证功能：

```python
# app/services/permission_validation_service.py
class PermissionValidationService:
    async def validate_user_permissions(self, user_id):
        # 验证用户权限配置的完整性
        pass
```

### 3. 前端权限调试工具

已创建权限调试工具 `web/src/utils/permission-debug.js`，可以：

- 调试用户权限状态
- 检查菜单生成过程
- 生成权限报告
- 检查特定权限

### 4. 权限变更通知

实现权限变更的实时通知机制：

```javascript
// 监听权限变更
const permissionStore = useEnhancedPermissionStore()
watch(() => permissionStore.allPermissions, (newPermissions) => {
  console.log('权限已更新:', newPermissions)
  // 可以显示通知或刷新页面
})
```

## 测试验证

### 1. 手动测试流程

1. 登录demo用户
2. 访问 `/test/permission` 页面
3. 点击"调试菜单生成"按钮
4. 查看控制台输出的菜单信息
5. 检查是否包含维修记录菜单

### 2. 自动化测试

```javascript
// 测试菜单权限
describe('菜单权限测试', () => {
  it('应该显示有权限的菜单', async () => {
    // 模拟用户登录
    // 检查菜单是否正确显示
  })
})
```

## 常见问题FAQ

### Q: 为什么修改角色权限后菜单没有变化？
A: 可能是权限缓存问题，尝试清除缓存或重新登录。

### Q: 如何确认菜单数据是否正确？
A: 使用前端调试工具或直接查询数据库。

### Q: 权限检查失败怎么办？
A: 检查权限标识是否匹配，确认用户是否有相应角色。

### Q: 如何添加新的菜单权限？
A: 1. 在数据库中创建菜单记录 2. 为角色分配菜单权限 3. 清除缓存

## 相关文件

- `web/src/store/modules/permission/enhanced-permission-store.js` - 权限Store
- `web/src/utils/permission-debug.js` - 权限调试工具
- `web/src/components/Permission/` - 权限组件
- `app/services/menu_permission_service.py` - 后端菜单权限服务
- `app/controllers/menu_permission_controller.py` - 菜单权限控制器