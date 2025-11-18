-- =====================================================
-- TDengine压力传感器配置脚本
-- 数据库: TDengine (devicemonitor)
-- 用途: 创建时序数据表结构和测试数据
-- =====================================================

-- 切换到设备监控数据库
USE devicemonitor;

-- =====================================================
-- 1. 创建超级表
-- =====================================================
CREATE STABLE IF NOT EXISTS st_pressure_sensor (
    ts TIMESTAMP,                    -- 时间戳（主键）
    pressure FLOAT,                  -- 压力值 (MPa)
    temperature FLOAT,               -- 温度 (°C)
    vibration FLOAT,                 -- 振动值 (mm/s)
    status NCHAR(20),               -- 设备状态
    error_code NCHAR(50),           -- 错误代码
    error_message NCHAR(500)        -- 错误信息
) TAGS (
    device_code NCHAR(50),          -- 设备编号（TAG）
    device_name NCHAR(100),         -- 设备名称（TAG）
    install_location NCHAR(255)     -- 安装位置（TAG）
);

-- 验证超级表创建
DESCRIBE st_pressure_sensor;

-- =====================================================
-- 2. 创建子表（设备实例）
-- =====================================================
CREATE TABLE IF NOT EXISTS tb_ps001 USING st_pressure_sensor 
TAGS (
    'PS001',                        -- device_code
    '1号车间压力传感器',             -- device_name
    '1号车间-A区-管道1'              -- install_location
);

-- 验证子表创建
SHOW TABLES LIKE 'tb_ps001';

-- =====================================================
-- 3. 插入测试数据
-- =====================================================

-- 3.1 插入正常运行数据
INSERT INTO tb_ps001 VALUES 
    (NOW - 10m, 5.2, 45.3, 2.1, 'online', NULL, NULL),
    (NOW - 9m, 5.3, 45.5, 2.2, 'online', NULL, NULL),
    (NOW - 8m, 5.1, 45.4, 2.0, 'online', NULL, NULL),
    (NOW - 7m, 5.4, 45.6, 2.3, 'online', NULL, NULL),
    (NOW - 6m, 5.2, 45.5, 2.1, 'online', NULL, NULL),
    (NOW - 5m, 5.5, 45.7, 2.4, 'online', NULL, NULL);

-- 3.2 插入异常数据
INSERT INTO tb_ps001 VALUES 
    (NOW - 4m, 8.9, 68.2, 38.5, 'error', 'E001', '压力异常'),
    (NOW - 3m, 9.2, 70.1, 42.3, 'error', 'E001', '压力异常');

-- 3.3 插入恢复正常数据
INSERT INTO tb_ps001 VALUES 
    (NOW - 2m, 5.3, 46.0, 2.2, 'online', NULL, NULL),
    (NOW - 1m, 5.2, 45.8, 2.1, 'online', NULL, NULL),
    (NOW, 5.4, 45.9, 2.3, 'online', NULL, NULL);

-- =====================================================
-- 4. 数据验证查询
-- =====================================================

-- 4.1 查看最新数据
SELECT * FROM tb_ps001 ORDER BY ts DESC LIMIT 20;

-- 4.2 统计查询
SELECT 
    COUNT(*) as total_records,
    AVG(pressure) as avg_pressure,
    MAX(pressure) as max_pressure,
    MIN(pressure) as min_pressure,
    AVG(temperature) as avg_temperature,
    AVG(vibration) as avg_vibration
FROM tb_ps001;

-- 4.3 异常数据查询
SELECT * FROM tb_ps001 WHERE status = 'error' ORDER BY ts DESC;

-- 4.4 按时间段统计
SELECT 
    _wstart as time_window,
    AVG(pressure) as avg_pressure,
    MAX(pressure) as max_pressure,
    MIN(pressure) as min_pressure,
    COUNT(*) as data_count
FROM tb_ps001
WHERE ts >= NOW - 1h
INTERVAL(5m);

-- =====================================================
-- 5. 性能测试查询
-- =====================================================

-- 5.1 查询最近1小时数据
SELECT * FROM tb_ps001 WHERE ts >= NOW - 1h ORDER BY ts DESC;

-- 5.2 聚合查询
SELECT 
    _wstart,
    AVG(pressure) as avg_pressure,
    STDDEV(pressure) as std_pressure
FROM tb_ps001
WHERE ts >= NOW - 24h
INTERVAL(1h);

-- 5.3 多设备联合查询（如果有多个设备）
SELECT 
    tbname,
    COUNT(*) as record_count,
    AVG(pressure) as avg_pressure
FROM st_pressure_sensor
WHERE ts >= NOW - 1h
GROUP BY tbname;
