-- 菜单数据表迁移SQL脚本
-- 将menu表数据迁移到t_sys_menu表

-- 1. 创建t_sys_menu表
CREATE TABLE IF NOT EXISTS t_sys_menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL COMMENT '菜单名称',
    remark JSON COMMENT '保留字段',
    menu_type VARCHAR(20) COMMENT '菜单类型',
    icon VARCHAR(100) COMMENT '菜单图标',
    path VARCHAR(100) NOT NULL COMMENT '菜单路径',
    `order` INT DEFAULT 0 COMMENT '排序',
    parent_id INT DEFAULT 0 COMMENT '父菜单ID',
    is_hidden BOOLEAN DEFAULT FALSE COMMENT '是否隐藏',
    component VARCHAR(100) COMMENT '组件',
    keepalive BOOLEAN DEFAULT TRUE COMMENT '存活',
    redirect VARCHAR(100) COMMENT '重定向',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_path (path),
    INDEX idx_order (`order`),
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统菜单表v2';

-- 2. 检查menu表数据量
SELECT COUNT(*) as menu_count FROM menu;

-- 3. 清空t_sys_menu表（如果存在数据）
DELETE FROM t_sys_menu;

-- 4. 迁移数据从menu表到t_sys_menu表
INSERT INTO t_sys_menu (
    id, name, remark, menu_type, icon, path, `order`, 
    parent_id, is_hidden, component, keepalive, redirect, 
    created_at, updated_at
)
SELECT 
    id, name, remark, menu_type, icon, path, `order`, 
    parent_id, is_hidden, component, keepalive, redirect, 
    created_at, updated_at
FROM menu
ORDER BY id;

-- 5. 验证迁移结果
SELECT COUNT(*) as t_sys_menu_count FROM t_sys_menu;

-- 6. 检查数据完整性
SELECT 
    'menu' as table_name, COUNT(*) as count FROM menu
UNION ALL
SELECT 
    't_sys_menu' as table_name, COUNT(*) as count FROM t_sys_menu;

-- 7. 显示迁移后的菜单数据样本
SELECT id, name, menu_type, path, parent_id, is_hidden 
FROM t_sys_menu 
ORDER BY parent_id, `order` 
LIMIT 10;