-- Node-RED数据采集数据库初始化脚本
-- 为设备传感器数据创建必要的表结构

-- 创建设备传感器数据表
CREATE TABLE IF NOT EXISTS device_sensor_data (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    value DECIMAL(10,3) NOT NULL,
    unit VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建设备信息表
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    device_name VARCHAR(200),
    device_type VARCHAR(50),
    location VARCHAR(100),
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建传感器类型表
CREATE TABLE IF NOT EXISTS sensor_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    unit VARCHAR(20),
    min_value DECIMAL(10,3),
    max_value DECIMAL(10,3),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建数据聚合表（用于统计分析）
CREATE TABLE IF NOT EXISTS sensor_data_summary (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    avg_value DECIMAL(10,3),
    min_value DECIMAL(10,3),
    max_value DECIMAL(10,3),
    count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(device_id, sensor_type, date)
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_device_sensor_data_device_id ON device_sensor_data(device_id);
CREATE INDEX IF NOT EXISTS idx_device_sensor_data_sensor_type ON device_sensor_data(sensor_type);
CREATE INDEX IF NOT EXISTS idx_device_sensor_data_timestamp ON device_sensor_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_device_sensor_data_device_timestamp ON device_sensor_data(device_id, timestamp);

-- 创建触发器自动更新updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER IF NOT EXISTS update_device_sensor_data_updated_at 
    BEFORE UPDATE ON device_sensor_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_devices_updated_at 
    BEFORE UPDATE ON devices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入示例传感器类型
INSERT INTO sensor_types (type_name, unit, min_value, max_value, description) VALUES
    ('temperature', '°C', -40.0, 85.0, '温度传感器'),
    ('humidity', '%', 0.0, 100.0, '湿度传感器'),
    ('pressure', 'hPa', 300.0, 1100.0, '气压传感器'),
    ('light', 'lux', 0.0, 100000.0, '光照传感器'),
    ('motion', 'bool', 0.0, 1.0, '运动传感器'),
    ('battery', 'V', 0.0, 5.0, '电池电压')
ON CONFLICT (type_name) DO NOTHING;

-- 插入示例设备
INSERT INTO devices (device_id, device_name, device_type, location, description) VALUES
    ('device_001', '温湿度传感器1号', 'DHT22', '实验室A区', '温湿度监控'),
    ('device_002', '光照传感器1号', 'BH1750', '实验室A区', '光照强度监控'),
    ('device_003', '气压传感器1号', 'BMP180', '实验室A区', '大气压监控')
ON CONFLICT (device_id) DO NOTHING;

-- 创建数据清理存储过程（清理30天前的数据）
CREATE OR REPLACE FUNCTION cleanup_old_sensor_data(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM device_sensor_data 
    WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 创建视图用于实时监控
CREATE OR REPLACE VIEW latest_device_data AS
SELECT 
    d.device_id,
    d.device_name,
    d.location,
    s.type_name as sensor_type,
    s.unit,
    sd.value as latest_value,
    sd.timestamp as latest_timestamp,
    CASE 
        WHEN sd.timestamp > NOW() - INTERVAL '5 minutes' THEN 'online'
        ELSE 'offline'
    END as device_status
FROM devices d
CROSS JOIN sensor_types s
LEFT JOIN LATERAL (
    SELECT value, timestamp 
    FROM device_sensor_data 
    WHERE device_id = d.device_id AND sensor_type = s.type_name
    ORDER BY timestamp DESC 
    LIMIT 1
) sd ON true
WHERE sd.value IS NOT NULL;