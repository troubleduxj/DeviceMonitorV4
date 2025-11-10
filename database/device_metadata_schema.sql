-- =====================================================
-- 设备实时数据接口优化方案 - 数据库设计
-- 第一阶段：PostgreSQL元数据表设计
-- 创建日期：2024年
-- 描述：支持多设备类型的元数据管理系统
-- =====================================================

-- 1. 设备类型表 (t_device_type)
-- 存储不同类型设备的基本信息和对应的TDengine超级表
CREATE TABLE IF NOT EXISTS t_device_type (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL UNIQUE,
    type_code VARCHAR(50) NOT NULL UNIQUE,
    tdengine_stable_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 设备信息表 (t_device_info)
-- 存储具体设备实例的信息
CREATE TABLE IF NOT EXISTS t_device_info (
    id SERIAL PRIMARY KEY,
    device_code VARCHAR(50) UNIQUE NOT NULL,     -- 子表名，如 t_14412T0006
    device_name VARCHAR(100) NOT NULL,
    device_model VARCHAR(50),
    device_type VARCHAR(50) NOT NULL,            -- 对应 t_device_type.code
    manufacturer VARCHAR(100),
    production_date DATE,
    install_date DATE,
    install_location VARCHAR(255),
    online_address VARCHAR(255),
    team_name VARCHAR(100),
    is_locked BOOLEAN DEFAULT false,
    description TEXT,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (device_type) REFERENCES t_device_type(type_code)
);

-- 3. 设备字段定义表 (t_device_field)
-- 存储每种设备类型的字段定义，支持动态查询构建
CREATE TABLE IF NOT EXISTS t_device_field (
    id SERIAL PRIMARY KEY,
    device_type_code VARCHAR(50) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    field_description VARCHAR(200),
    is_required BOOLEAN DEFAULT false,
    is_tag BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_type_code) REFERENCES t_device_type(type_code) ON DELETE CASCADE,
    UNIQUE(device_type_code, field_name)
);

-- 创建索引优化查询性能
CREATE INDEX idx_device_type_code ON t_device_type(type_code);
CREATE INDEX idx_device_type_active ON t_device_type(is_active);
CREATE INDEX idx_device_info_device_code ON t_device_info(device_code);
CREATE INDEX idx_device_info_device_type ON t_device_info(device_type);
CREATE INDEX idx_device_info_locked ON t_device_info(is_locked);
CREATE INDEX idx_device_field_type_code ON t_device_field(device_type_code);
CREATE INDEX idx_device_field_sort ON t_device_field(device_type_code, sort_order);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_device_type_updated_at BEFORE UPDATE ON t_device_type
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_device_info_updated_at BEFORE UPDATE ON t_device_info
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 初始数据插入
-- =====================================================

-- 插入焊接设备类型（对应现有的welding_real_data超级表）
INSERT INTO t_device_type (type_name, type_code, tdengine_stable_name, description) 
VALUES 
('焊接设备', 'welding', 'welding_real_data', '焊接设备实时数据监控')
ON CONFLICT (type_code) DO NOTHING;

-- 插入焊接设备字段定义（基于welding_real_data超级表结构）
INSERT INTO t_device_field (device_type_code, field_name, field_type, field_description, is_tag, sort_order) 
VALUES 
-- 时间序列字段
('welding', 'ts', 'timestamp', '时间戳', false, 1),
-- 数据字段
('welding', 'team_name', 'string', '团队名称', false, 2),
('welding', 'device_status', 'string', '设备状态', false, 3),
('welding', 'lock_status', 'boolean', '锁定状态', false, 4),
('welding', 'preset_current', 'float', '预设电流', false, 5),
('welding', 'preset_voltage', 'float', '预设电压', false, 6),
('welding', 'weld_current', 'float', '焊接电流', false, 7),
('welding', 'weld_voltage', 'float', '焊接电压', false, 8),
('welding', 'material', 'string', '材料', false, 9),
('welding', 'wire_diameter', 'float', '焊丝直径', false, 10),
('welding', 'gas_type', 'string', '气体类型', false, 11),
('welding', 'weld_method', 'string', '焊接方法', false, 12),
('welding', 'weld_control', 'string', '焊接控制', false, 13),
('welding', 'staff_id', 'string', '员工ID', false, 14),
('welding', 'workpiece_id', 'string', '工件ID', false, 15),
('welding', 'ip_quality', 'int', 'IP质量', false, 16),
-- 标签字段
('welding', 'device_code', 'string', '设备代码', true, 17),
('welding', 'name', 'string', '设备名称', true, 18)
ON CONFLICT (device_type_code, field_name) DO NOTHING;

-- =====================================================
-- 查询视图定义
-- =====================================================

-- 创建设备类型详情视图
CREATE OR REPLACE VIEW v_device_type_detail AS
SELECT 
    dt.id,
    dt.type_name,
    dt.type_code,
    dt.tdengine_stable_name,
    dt.description,
    dt.is_active,
    COUNT(di.id) as device_count,
    COUNT(df.id) as field_count,
    dt.created_at,
    dt.updated_at
FROM t_device_type dt
LEFT JOIN t_device_info di ON dt.type_code = di.device_type AND di.is_locked = false
LEFT JOIN t_device_field df ON dt.type_code = df.device_type_code
GROUP BY dt.id, dt.type_name, dt.type_code, dt.tdengine_stable_name, 
         dt.description, dt.is_active, dt.created_at, dt.updated_at;

-- 创建设备完整信息视图
CREATE OR REPLACE VIEW v_device_full_info AS
SELECT 
    di.id,
    di.device_code,
    di.device_name,
    di.device_model,
    di.install_location,
    di.online_address,
    di.team_name,
    di.is_locked,
    di.description,
    dt.type_name,
    dt.type_code,
    dt.tdengine_stable_name,
    dt.description as type_description,
    di.created_at,
    di.updated_at
FROM t_device_info di
JOIN t_device_type dt ON di.device_type = dt.type_code;

-- =====================================================
-- 存储过程定义
-- =====================================================

-- 获取设备类型的字段定义（用于动态构建TDengine查询）
CREATE OR REPLACE FUNCTION get_device_type_fields(p_type_code VARCHAR)
RETURNS TABLE(
    field_name VARCHAR,
    field_type VARCHAR,
    field_description VARCHAR,
    is_tag BOOLEAN,
    sort_order INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        df.field_name,
        df.field_type,
        df.field_description,
        df.is_tag,
        df.sort_order
    FROM t_device_field df
    JOIN t_device_type dt ON df.device_type_code = dt.type_code
    WHERE dt.type_code = p_type_code
      AND dt.is_active = true
    ORDER BY df.sort_order, df.field_name;
END;
$$ LANGUAGE plpgsql;

-- 获取设备类型的TDengine超级表名
CREATE OR REPLACE FUNCTION get_tdengine_stable_name(p_type_code VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    stable_name VARCHAR;
BEGIN
    SELECT tdengine_stable_name INTO stable_name
    FROM t_device_type
    WHERE type_code = p_type_code AND is_active = true;
    
    RETURN stable_name;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 数据库设计完成
-- =====================================================

-- 验证表创建
SELECT 'Database schema created successfully' as status;

-- 显示表结构信息
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name IN ('t_device_type', 't_device_info', 't_device_field')
ORDER BY table_name, ordinal_position;