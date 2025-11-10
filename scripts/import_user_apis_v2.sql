-- 用户管理模块 API v2 数据导入脚本
-- 执行前请先清理旧数据：DELETE FROM t_sys_api_endpoints WHERE api_path LIKE '/api/v2/users%';

-- 插入用户管理模块的19个API接口
INSERT INTO t_sys_api_endpoints (api_code, api_name, api_path, http_method, group_id, description, version, is_public, is_deprecated, status, permission_code) VALUES 
-- 基础CRUD操作
('users_list', '获取用户列表', '/api/v2/users/', 'GET', 2, '获取用户列表，支持分页、搜索、过滤', 'v2', false, false, 'active', 'api:v2:users:list'),
('users_detail', '获取用户详情', '/api/v2/users/{user_id}', 'GET', 2, '获取指定用户的详细信息', 'v2', false, false, 'active', 'api:v2:users:detail'),
('users_create', '创建用户', '/api/v2/users/', 'POST', 2, '创建新用户，支持角色和部门关联', 'v2', false, false, 'active', 'api:v2:users:create'),
('users_update', '更新用户', '/api/v2/users/{user_id}', 'PUT', 2, '完整更新用户信息', 'v2', false, false, 'active', 'api:v2:users:update'),
('users_patch', '部分更新用户', '/api/v2/users/{user_id}', 'PATCH', 2, '部分更新用户信息，支持选择性字段更新', 'v2', false, false, 'active', 'api:v2:users:patch'),
('users_delete', '删除用户', '/api/v2/users/{user_id}', 'DELETE', 2, '删除指定用户，包含安全检查', 'v2', false, false, 'active', 'api:v2:users:delete'),

-- 用户角色和权限管理
('users_roles_get', '获取用户角色', '/api/v2/users/{user_id}/roles', 'GET', 2, '获取指定用户的角色列表', 'v2', false, false, 'active', 'api:v2:users:roles:get'),
('users_roles_set', '设置用户角色', '/api/v2/users/{user_id}/roles', 'PUT', 2, '设置指定用户的角色', 'v2', false, false, 'active', 'api:v2:users:roles:set'),
('users_permissions_get', '获取用户权限', '/api/v2/users/{user_id}/permissions', 'GET', 2, '获取指定用户的权限列表', 'v2', false, false, 'active', 'api:v2:users:permissions:get'),

-- 用户状态管理
('users_status_update', '更新用户状态', '/api/v2/users/{user_id}/status', 'PATCH', 2, '更新指定用户的状态', 'v2', false, false, 'active', 'api:v2:users:status:update'),
('users_activate', '激活用户', '/api/v2/users/{user_id}/actions/activate', 'POST', 2, '激活指定用户账户', 'v2', false, false, 'active', 'api:v2:users:activate'),
('users_deactivate', '禁用用户', '/api/v2/users/{user_id}/actions/deactivate', 'POST', 2, '禁用指定用户账户', 'v2', false, false, 'active', 'api:v2:users:deactivate'),
('users_reset_password', '重置用户密码', '/api/v2/users/{user_id}/actions/reset-password', 'POST', 2, '重置指定用户的密码', 'v2', false, false, 'active', 'api:v2:users:reset_password'),

-- 批量操作
('users_batch_create', '批量创建用户', '/api/v2/users/_batch-create', 'POST', 2, '批量创建多个用户', 'v2', false, false, 'active', 'api:v2:users:batch_create'),
('users_batch_update', '批量更新用户', '/api/v2/users/_batch-update', 'PATCH', 2, '批量更新多个用户信息', 'v2', false, false, 'active', 'api:v2:users:batch_update'),
('users_batch_delete', '批量删除用户', '/api/v2/users/_batch-delete', 'POST', 2, '批量删除多个用户', 'v2', false, false, 'active', 'api:v2:users:batch_delete'),
('users_batch_activate', '批量激活用户', '/api/v2/users/_batch-activate', 'POST', 2, '批量激活多个用户账户', 'v2', false, false, 'active', 'api:v2:users:batch_activate'),
('users_batch_deactivate', '批量禁用用户', '/api/v2/users/_batch-deactivate', 'POST', 2, '批量禁用多个用户账户', 'v2', false, false, 'active', 'api:v2:users:batch_deactivate'),

-- 高级功能
('users_search', '复杂查询用户', '/api/v2/users/search', 'POST', 2, '支持多条件筛选和排序的复杂查询', 'v2', false, false, 'active', 'api:v2:users:search'),
('users_export', '导出用户数据', '/api/v2/users/export', 'GET', 2, '导出用户数据，支持CSV/JSON格式', 'v2', false, false, 'active', 'api:v2:users:export');

-- 验证插入结果
SELECT COUNT(*) as total_apis FROM t_sys_api_endpoints WHERE group_id = 2;
SELECT api_code, api_name, api_path, http_method FROM t_sys_api_endpoints WHERE group_id = 2 ORDER BY api_path, http_method;