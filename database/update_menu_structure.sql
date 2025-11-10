-- 更新菜单结构：将主题管理移动到高级设置下面，并添加组件管理

-- 1. 将主题管理菜单移动到高级设置下面
UPDATE t_sys_menu 
SET parent_id = 25, "order" = 10
WHERE id = 66;

-- 2. 显示高级设置菜单（如果被隐藏）
UPDATE t_sys_menu 
SET is_hidden = false
WHERE id = 25;

-- 3. 添加组件管理菜单到高级设置下面
INSERT INTO t_sys_menu (
    name, 
    remark, 
    menu_type, 
    icon, 
    path, 
    "order", 
    parent_id, 
    is_hidden, 
    component, 
    keepalive, 
    redirect,
    created_at,
    updated_at
) VALUES (
    '组件管理',
    '{"description": "系统组件管理和监控", "features": ["组件列表", "健康检查", "性能监控", "依赖分析"]}',
    'menu',
    'material-symbols:widgets',
    'components',
    20,
    25,
    false,
    '/system/components/index',
    true,
    null,
    NOW(),
    NOW()
);

-- 4. 验证更新结果
SELECT id, name, path, parent_id, "order", is_hidden 
FROM t_sys_menu 
WHERE parent_id = 25 OR id = 25
ORDER BY parent_id, "order";