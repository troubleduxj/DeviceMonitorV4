-- 添加批量删除权限到系统
-- 为系统添加批量删除相关的API端点和权限配置

-- 需求映射：
-- 需求6.1: 前端权限控制
-- 需求6.2: 后端权限验证
-- 需求6.3: 细粒度权限检查

-- 1. 添加批量删除API端点到t_sys_api_endpoints表
INSERT INTO t_sys_api_endpoints (api_code, api_name, api_path, http_method, description, version, is_public, is_deprecated, status, permission_code, group_id, created_at, updated_at)
VALUES 
-- API管理批量删除
('api_batch_delete', 'API批量删除', '/api/v2/apis/batch', 'DELETE', '批量删除API端点', 'v2', false, false, 'active', 'api:batch_delete', 1, NOW(), NOW()),

-- 字典类型批量删除
('dict_type_batch_delete', '字典类型批量删除', '/api/v2/dict-types/batch', 'DELETE', '批量删除字典类型', 'v2', false, false, 'active', 'dict_type:batch_delete', 1, NOW(), NOW()),

-- 字典数据批量删除
('dict_data_batch_delete', '字典数据批量删除', '/api/v2/dict-data/batch', 'DELETE', '批量删除字典数据', 'v2', false, false, 'active', 'dict_data:batch_delete', 1, NOW(), NOW()),

-- 系统参数批量删除
('system_param_batch_delete', '系统参数批量删除', '/api/v2/system-params/batch', 'DELETE', '批量删除系统参数', 'v2', false, false, 'active', 'system_param:batch_delete', 1, NOW(), NOW()),

-- 部门批量删除
('dept_batch_delete', '部门批量删除', '/api/v2/departments/batch', 'DELETE', '批量删除部门', 'v2', false, false, 'active', 'dept:batch_delete', 1, NOW(), NOW()),

-- 用户批量删除
('user_batch_delete', '用户批量删除', '/api/v2/users/batch', 'DELETE', '批量删除用户', 'v2', false, false, 'active', 'user:batch_delete', 1, NOW(), NOW()),

-- 角色批量删除
('role_batch_delete', '角色批量删除', '/api/v2/roles/batch', 'DELETE', '批量删除角色', 'v2', false, false, 'active', 'role:batch_delete', 1, NOW(), NOW()),

-- 菜单批量删除
('menu_batch_delete', '菜单批量删除', '/api/v2/menus/batch', 'DELETE', '批量删除菜单', 'v2', false, false, 'active', 'menu:batch_delete', 1, NOW(), NOW())

ON CONFLICT (api_code) DO UPDATE SET
    api_name = EXCLUDED.api_name,
    api_path = EXCLUDED.api_path,
    http_method = EXCLUDED.http_method,
    description = EXCLUDED.description,
    version = EXCLUDED.version,
    permission_code = EXCLUDED.permission_code,
    updated_at = NOW();

-- 2. 为管理员角色分配批量删除权限
-- 假设管理员角色ID为1，如果不存在则需要先创建

-- 获取刚插入的API端点ID并分配给管理员角色
INSERT INTO t_sys_role_api (role_id, api_id)
SELECT 1, id FROM t_sys_api_endpoints 
WHERE api_code IN (
    'api_batch_delete',
    'dict_type_batch_delete', 
    'dict_data_batch_delete',
    'system_param_batch_delete',
    'dept_batch_delete',
    'user_batch_delete',
    'role_batch_delete',
    'menu_batch_delete'
)
ON CONFLICT (role_id, api_id) DO NOTHING;

-- 3. 创建批量删除权限分组（如果不存在）
INSERT INTO t_sys_api_groups (group_code, group_name, parent_id, description, sort_order, status, created_at, updated_at)
VALUES ('batch_delete', '批量删除权限', NULL, '系统批量删除操作相关权限', 100, 'active', NOW(), NOW())
ON CONFLICT (group_code) DO UPDATE SET
    group_name = EXCLUDED.group_name,
    description = EXCLUDED.description,
    updated_at = NOW();

-- 4. 将批量删除API端点分配到批量删除权限分组
UPDATE t_sys_api_endpoints 
SET group_id = (SELECT id FROM t_sys_api_groups WHERE group_code = 'batch_delete')
WHERE api_code IN (
    'api_batch_delete',
    'dict_type_batch_delete', 
    'dict_data_batch_delete',
    'system_param_batch_delete',
    'dept_batch_delete',
    'user_batch_delete',
    'role_batch_delete',
    'menu_batch_delete'
);

-- 5. 添加权限说明注释
COMMENT ON TABLE t_sys_api_endpoints IS '系统API端点表，包含批量删除权限配置';

-- 6. 创建权限检查视图（可选）
CREATE OR REPLACE VIEW v_batch_delete_permissions AS
SELECT 
    r.id as role_id,
    r.role_name,
    ae.api_code,
    ae.api_name,
    ae.api_path,
    ae.permission_code,
    ae.description
FROM t_sys_role r
JOIN t_sys_role_api ra ON r.id = ra.role_id
JOIN t_sys_api_endpoints ae ON ra.api_id = ae.id
WHERE ae.api_code LIKE '%_batch_delete'
AND ae.status = 'active'
ORDER BY r.role_name, ae.api_name;

-- 7. 添加权限检查函数
CREATE OR REPLACE FUNCTION check_batch_delete_permission(
    p_user_id INTEGER,
    p_resource_type VARCHAR(50)
) RETURNS BOOLEAN AS $$
DECLARE
    permission_count INTEGER;
    api_code_pattern VARCHAR(100);
BEGIN
    -- 构建API代码模式
    api_code_pattern := p_resource_type || '_batch_delete';
    
    -- 检查用户是否有对应的批量删除权限
    SELECT COUNT(*)
    INTO permission_count
    FROM t_sys_user u
    JOIN t_sys_user_role ur ON u.id = ur.user_id
    JOIN t_sys_role_api ra ON ur.role_id = ra.role_id
    JOIN t_sys_api_endpoints ae ON ra.api_id = ae.id
    WHERE u.id = p_user_id
    AND ae.api_code = api_code_pattern
    AND ae.status = 'active'
    AND u.status = '0'  -- 用户状态正常
    AND EXISTS (
        SELECT 1 FROM t_sys_role r 
        WHERE r.id = ur.role_id 
        AND r.status = '0'  -- 角色状态正常
    );
    
    -- 如果是超级管理员，直接返回true
    IF EXISTS (
        SELECT 1 FROM t_sys_user 
        WHERE id = p_user_id 
        AND user_type = '01'  -- 超级管理员
        AND status = '0'
    ) THEN
        RETURN TRUE;
    END IF;
    
    RETURN permission_count > 0;
END;
$$ LANGUAGE plpgsql;

-- 8. 添加权限缓存表（可选，用于性能优化）
CREATE TABLE IF NOT EXISTS t_sys_permission_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    permission_key VARCHAR(100) NOT NULL,
    has_permission BOOLEAN NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, permission_key)
);

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_permission_cache_user_key ON t_sys_permission_cache(user_id, permission_key);
CREATE INDEX IF NOT EXISTS idx_permission_cache_expires ON t_sys_permission_cache(expires_at);

-- 9. 添加权限缓存清理函数
CREATE OR REPLACE FUNCTION clean_expired_permission_cache() RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM t_sys_permission_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 10. 验证权限配置
DO $$
DECLARE
    api_count INTEGER;
    role_api_count INTEGER;
BEGIN
    -- 检查API端点是否正确创建
    SELECT COUNT(*) INTO api_count 
    FROM t_sys_api_endpoints 
    WHERE api_code LIKE '%_batch_delete';
    
    -- 检查角色权限是否正确分配
    SELECT COUNT(*) INTO role_api_count
    FROM t_sys_role_api ra
    JOIN t_sys_api_endpoints ae ON ra.api_id = ae.id
    WHERE ae.api_code LIKE '%_batch_delete'
    AND ra.role_id = 1;
    
    RAISE NOTICE '批量删除权限配置完成：';
    RAISE NOTICE '- 创建API端点数量: %', api_count;
    RAISE NOTICE '- 管理员角色权限数量: %', role_api_count;
    
    IF api_count < 8 THEN
        RAISE WARNING 'API端点创建不完整，期望8个，实际%个', api_count;
    END IF;
    
    IF role_api_count < 8 THEN
        RAISE WARNING '管理员角色权限分配不完整，期望8个，实际%个', role_api_count;
    END IF;
END $$;