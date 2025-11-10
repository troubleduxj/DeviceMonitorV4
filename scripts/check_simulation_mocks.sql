-- 检查模拟设备Mock规则是否成功插入

-- 1. 查询所有包含"模拟设备"的Mock规则
SELECT 
    id,
    name,
    method,
    url_pattern,
    enabled,
    priority,
    description,
    created_at
FROM t_sys_mock_data
WHERE description LIKE '%模拟设备%'
ORDER BY id DESC;

-- 2. 统计Mock规则数量
SELECT 
    '总Mock规则数' as "类型",
    COUNT(*) as "数量"
FROM t_sys_mock_data
UNION ALL
SELECT 
    '模拟设备Mock规则数' as "类型",
    COUNT(*) as "数量"
FROM t_sys_mock_data
WHERE description LIKE '%模拟设备%';

-- 3. 查看最近插入的5条记录
SELECT 
    id,
    name,
    method,
    enabled,
    created_at
FROM t_sys_mock_data
ORDER BY id DESC
LIMIT 5;

-- 4. 检查是否有未启用的规则
SELECT 
    enabled,
    COUNT(*) as count
FROM t_sys_mock_data
GROUP BY enabled;

