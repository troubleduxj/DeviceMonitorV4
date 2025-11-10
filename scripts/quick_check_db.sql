-- 快速检查数据库中的Mock规则

-- 1. 总数统计
SELECT '=== 数据库统计 ===' as info;
SELECT 
    COUNT(*) as "总Mock规则数",
    COUNT(*) FILTER (WHERE enabled = true) as "已启用",
    COUNT(*) FILTER (WHERE enabled = false) as "未启用"
FROM t_sys_mock_data;

-- 2. 检查是否有模拟设备规则
SELECT '=== 模拟设备规则检查 ===' as info;
SELECT 
    COUNT(*) as "模拟设备规则数"
FROM t_sys_mock_data
WHERE name LIKE '%模拟设备%' OR description LIKE '%模拟设备%';

-- 3. 列出所有模拟设备规则
SELECT '=== 模拟设备规则详情 ===' as info;
SELECT 
    id,
    name,
    method,
    url_pattern,
    enabled,
    priority,
    created_at
FROM t_sys_mock_data
WHERE name LIKE '%模拟设备%' OR description LIKE '%模拟设备%'
ORDER BY id;

-- 4. 最近创建的10条规则
SELECT '=== 最近创建的规则 ===' as info;
SELECT 
    id,
    name,
    enabled,
    created_at
FROM t_sys_mock_data
ORDER BY created_at DESC
LIMIT 10;

-- 5. 检查表结构
SELECT '=== 表结构信息 ===' as info;
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 't_sys_mock_data'
ORDER BY ordinal_position;

