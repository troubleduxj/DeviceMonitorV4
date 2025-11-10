-- 添加API分组数据
-- 基于老API表的分组信息完善分组表

INSERT INTO t_sys_api_groups (group_code, group_name, parent_id, description, sort_order, status, created_at, updated_at) VALUES 
('user_module', '用户模块', 0, '用户相关API接口', 1, 'active', NOW(), NOW()),
('role_module', '角色模块', 0, '角色相关API接口', 2, 'active', NOW(), NOW()),
('menu_module', '菜单模块', 0, '菜单相关API接口', 3, 'active', NOW(), NOW()),
('dept_module', '部门模块', 0, '部门相关API接口', 4, 'active', NOW(), NOW()),
('api_module', 'API模块', 0, 'API管理相关接口', 5, 'active', NOW(), NOW()),
('device_module', '设备模块', 0, '设备相关API接口', 6, 'active', NOW(), NOW()),
('device_data', '设备数据', 0, '设备数据相关API接口', 7, 'active', NOW(), NOW()),
('device_type', '设备类型管理', 0, '设备类型管理相关API接口', 8, 'active', NOW(), NOW()),
('device_alarm', '设备报警', 0, '设备报警相关API接口', 9, 'active', NOW(), NOW()),
('basic_module', '基础模块', 0, '基础功能相关API接口', 10, 'active', NOW(), NOW()),
('dashboard_module', '仪表板模块', 0, '仪表板相关API接口', 11, 'active', NOW(), NOW()),
('audit_module', '审计日志模块', 0, '审计日志相关API接口', 12, 'active', NOW(), NOW());

-- 更新API端点的分组分配
-- 用户模块相关API
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'user_module') 
WHERE api_path LIKE '%user%' OR api_code LIKE '%user%';

-- 角色模块相关API
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'role_module') 
WHERE api_path LIKE '%role%' OR api_code LIKE '%role%';

-- 菜单模块相关API
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'menu_module') 
WHERE api_path LIKE '%menu%' OR api_code LIKE '%menu%';

-- 部门模块相关API
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'dept_module') 
WHERE api_path LIKE '%dept%' OR api_code LIKE '%dept%';

-- API模块相关API
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'api_module') 
WHERE api_path LIKE '%api%' OR api_code LIKE '%api%';

-- 设备模块相关API
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'device_module') 
WHERE api_path LIKE '%device%' OR api_code LIKE '%device%';

-- 设备数据相关API
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'device_data') 
WHERE api_path LIKE '%data%' OR api_code LIKE '%data%';

-- 设备报警相关API
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'device_alarm') 
WHERE api_path LIKE '%alarm%' OR api_code LIKE '%alarm%';

-- 分析相关API分配到基础模块
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'basic_module') 
WHERE api_path LIKE '%analysis%' OR api_code LIKE '%analysis%';

-- 配置相关API分配到基础模块
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'basic_module') 
WHERE api_path LIKE '%config%' OR api_code LIKE '%config%';

-- 版本信息API分配到基础模块
UPDATE t_sys_api_endpoints SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'basic_module') 
WHERE api_path LIKE '%version%' OR api_code LIKE '%version%';