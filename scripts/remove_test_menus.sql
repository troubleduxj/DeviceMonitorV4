-- 删除或隐藏测试和系统页面菜单
-- PostgreSQL 版本

-- 方案1：隐藏这些菜单（推荐 - 可恢复）
UPDATE menu 
SET is_hidden = true, 
    updated_at = CURRENT_TIMESTAMP
WHERE name IN (
    '403',
    '404',
    '登录页',
    'Login',
    '权限调试',
    '简单测试',
    '权限测试',
    '权限组件测试',
    'PermissionDebug',
    'SimpleTest',
    'TestPermission',
    'TestComponents'
);

-- 查看更新结果
SELECT id, name, path, menu_type, is_hidden, created_at 
FROM menu 
WHERE name IN (
    '403',
    '404',
    '登录页',
    'Login',
    '权限调试',
    '简单测试',
    '权限测试',
    '权限组件测试',
    'PermissionDebug',
    'SimpleTest',
    'TestPermission',
    'TestComponents'
)
ORDER BY name;

-- 方案2：完全删除这些菜单（不可恢复 - 谨慎使用）
-- 取消下面的注释来执行删除
/*
DELETE FROM menu 
WHERE name IN (
    '403',
    '404',
    '登录页',
    'Login',
    '权限调试',
    '简单测试',
    '权限测试',
    '权限组件测试',
    'PermissionDebug',
    'SimpleTest',
    'TestPermission',
    'TestComponents'
);
*/

