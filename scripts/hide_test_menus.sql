-- 隐藏测试和错误页面菜单
-- PostgreSQL 版本

-- 隐藏这些菜单项（设置 is_hidden = true）
UPDATE menu 
SET is_hidden = true, 
    updated_at = CURRENT_TIMESTAMP
WHERE name IN (
    '403',
    '404', 
    '登录页',
    '权限调试',
    '简单测试',
    '权限测试',
    '权限组件测试'
);

-- 查看隐藏的菜单
SELECT id, name, path, menu_type, is_hidden 
FROM menu 
WHERE name IN (
    '403',
    '404', 
    '登录页',
    '权限调试',
    '简单测试',
    '权限测试',
    '权限组件测试'
)
ORDER BY name;

