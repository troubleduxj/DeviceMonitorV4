-- 删除Mock数据管理菜单项
-- 由于组件文件被删除，需要从数据库中移除对应的菜单项

-- 删除Mock数据管理菜单（包括其子按钮权限）
DELETE FROM t_sys_menu 
WHERE name = 'Mock数据管理' 
   OR parent_id IN (SELECT id FROM t_sys_menu WHERE name = 'Mock数据管理');

-- 查询确认
SELECT id, name, path, parent_id 
FROM t_sys_menu 
WHERE name LIKE '%Mock%'
ORDER BY id;

-- 如果上面的查询返回空，说明删除成功

