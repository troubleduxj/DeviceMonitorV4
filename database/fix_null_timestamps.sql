-- 修复空的时间戳字段
-- 为所有表的created_at和updated_at字段设置默认值

-- 修复t_sys_api_groups表
UPDATE t_sys_api_groups 
SET created_at = CURRENT_TIMESTAMP 
WHERE created_at IS NULL;

UPDATE t_sys_api_groups 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;

-- 修复t_sys_api_endpoints表
UPDATE t_sys_api_endpoints 
SET created_at = CURRENT_TIMESTAMP 
WHERE created_at IS NULL;

UPDATE t_sys_api_endpoints 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;

-- 修复其他可能有问题的表
UPDATE t_sys_menu 
SET created_at = CURRENT_TIMESTAMP 
WHERE created_at IS NULL;

UPDATE t_sys_menu 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;

UPDATE t_sys_user 
SET created_at = CURRENT_TIMESTAMP 
WHERE created_at IS NULL;

UPDATE t_sys_user 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;

UPDATE t_sys_role 
SET created_at = CURRENT_TIMESTAMP 
WHERE created_at IS NULL;

UPDATE t_sys_role 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;

UPDATE t_sys_dept 
SET created_at = CURRENT_TIMESTAMP 
WHERE created_at IS NULL;

UPDATE t_sys_dept 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;

-- 设置默认值约束
ALTER TABLE t_sys_api_groups 
ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE t_sys_api_endpoints 
ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

SELECT 'Timestamp fields fixed successfully!' as result;