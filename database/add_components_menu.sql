-- 添加组件管理菜单到系统管理下面

-- 查看当前系统管理菜单结构
SELECT id, name, path, parent_id, "order", is_hidden 
FROM t_sys_menu 
WHERE parent_id = 1 OR id = 1
ORDER BY parent_id, "order";

-- 添加组件管理菜单
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
    90,
    1,
    false,
    '/system/components/index',
    true,
    null,
    NOW(),
    NOW()
);

-- 验证添加结果
SELECT id, name, path, parent_id, "order", is_hidden, component 
FROM t_sys_menu 
WHERE parent_id = 1 OR id = 1
ORDER BY parent_id, "order";