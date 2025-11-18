-- =====================================================
-- 压力传感器设备类型完整配置脚本
-- 数据库: PostgreSQL (devicemonitor)
-- 用途: 创建压力传感器设备类型及相关配置
-- =====================================================

-- 1. 创建设备类型
INSERT INTO t_device_type (
    type_name, 
    type_code, 
    tdengine_stable_name, 
    description, 
    is_active, 
    device_count, 
    created_at, 
    updated_at
) VALUES (
    '智能压力传感器',
    'PRESSURE_SENSOR_V1',
    'st_pressure_sensor',
    '用于监测管道压力的智能传感器，支持实时数据采集和异常检测',
    true,
    0,
    NOW(),
    NOW()
);

-- 2. 创建设备字段
-- 2.1 压力值字段（主要监控指标）
INSERT INTO t_device_field (
    device_type_code, field_name, field_code, field_type, field_category,
    unit, description, is_required, sort_order, is_active,
    is_monitoring_key, is_ai_feature, aggregation_method,
    data_range, alarm_threshold, display_config, created_at, updated_at
) VALUES (
    'PRESSURE_SENSOR_V1', '压力值', 'pressure', 'float', 'data_collection',
    'MPa', '当前压力读数', true, 1, true, true, true, 'avg',
    '{"min": 0, "max": 10}', '{"warning": 8, "critical": 9.5}',
    '{"chart_type": "line", "color": "#1890ff"}', NOW(), NOW()
);

-- 2.2 温度字段
INSERT INTO t_device_field (
    device_type_code, field_name, field_code, field_type, field_category,
    unit, description, is_required, sort_order, is_active,
    is_monitoring_key, is_ai_feature, aggregation_method,
    data_range, alarm_threshold, display_config, created_at, updated_at
) VALUES (
    'PRESSURE_SENSOR_V1', '温度', 'temperature', 'float', 'data_collection',
    '°C', '传感器温度', true, 2, true, true, true, 'avg',
    '{"min": -20, "max": 80}', '{"warning": 70, "critical": 75}',
    '{"chart_type": "line", "color": "#ff4d4f"}', NOW(), NOW()
);

-- 2.3 振动值字段
INSERT INTO t_device_field (
    device_type_code, field_name, field_code, field_type, field_category,
    unit, description, is_required, sort_order, is_active,
    is_monitoring_key, is_ai_feature, aggregation_method,
    data_range, alarm_threshold, created_at, updated_at
) VALUES (
    'PRESSURE_SENSOR_V1', '振动值', 'vibration', 'float', 'data_collection',
    'mm/s', '设备振动强度', false, 3, true, true, true, 'max',
    '{"min": 0, "max": 50}', '{"warning": 40, "critical": 45}', NOW(), NOW()
);

-- 2.4 设备状态字段
INSERT INTO t_device_field (
    device_type_code, field_name, field_code, field_type, field_category,
    unit, description, is_required, sort_order, is_active,
    is_monitoring_key, created_at, updated_at
) VALUES (
    'PRESSURE_SENSOR_V1', '设备状态', 'status', 'string', 'data_collection',
    NULL, '设备运行状态：online/offline/error/maintenance', 
    true, 4, true, true, NOW(), NOW()
);

-- 3. 创建字段映射（PostgreSQL ↔ TDengine）
INSERT INTO t_device_field_mapping (
    device_type_code, tdengine_database, tdengine_stable, tdengine_column,
    device_field_id, is_tag, is_active, created_at, updated_at
) 
SELECT 
    'PRESSURE_SENSOR_V1', 
    'devicemonitor', 
    'st_pressure_sensor', 
    field_code,
    id, 
    false, 
    true, 
    NOW(), 
    NOW()
FROM t_device_field
WHERE device_type_code = 'PRESSURE_SENSOR_V1';

-- 4. 创建测试设备
INSERT INTO t_device_info (
    device_code, device_name, device_model, device_type,
    manufacturer, production_date, install_date, install_location,
    online_address, team_name, is_locked, description,
    created_at, updated_at
) VALUES (
    'PS001',
    '1号车间压力传感器',
    'PS-3000',
    'PRESSURE_SENSOR_V1',
    '华为技术有限公司',
    '2024-01-15',
    '2024-02-01',
    '1号车间-A区-管道1',
    '192.168.1.101',
    '设备维护一组',
    false,
    '用于监测1号车间主管道压力',
    NOW(),
    NOW()
);

-- 5. 创建数据模型
-- 5.1 实时监控模型
INSERT INTO t_device_data_model (
    model_name, model_code, device_type_code, model_type,
    selected_fields, version, is_active, is_default, description,
    created_at, updated_at
) VALUES (
    '压力传感器实时监控模型',
    'PRESSURE_REALTIME_V1',
    'PRESSURE_SENSOR_V1',
    'realtime',
    '[
        {"field_code": "pressure", "alias": "压力", "weight": 1.0, "is_required": true},
        {"field_code": "temperature", "alias": "温度", "weight": 0.8, "is_required": true},
        {"field_code": "vibration", "alias": "振动", "weight": 0.6, "is_required": false}
    ]',
    '1.0',
    true,
    true,
    '用于实时监控压力传感器的关键指标',
    NOW(),
    NOW()
);

-- 5.2 AI异常检测模型
INSERT INTO t_device_data_model (
    model_name, model_code, device_type_code, model_type,
    selected_fields, ai_config, version, is_active, description,
    created_at, updated_at
) VALUES (
    '压力传感器AI异常检测模型',
    'PRESSURE_AI_ANOMALY_V1',
    'PRESSURE_SENSOR_V1',
    'ai_analysis',
    '[
        {"field_code": "pressure", "alias": "压力", "weight": 1.0, "is_required": true},
        {"field_code": "temperature", "alias": "温度", "weight": 0.7, "is_required": true},
        {"field_code": "vibration", "alias": "振动", "weight": 0.5, "is_required": true}
    ]',
    '{
        "algorithm": "isolation_forest",
        "features": ["pressure", "temperature", "vibration"],
        "normalization": "min-max",
        "window_size": 100,
        "contamination": 0.05
    }',
    '1.0',
    true,
    '基于孤立森林算法的多维异常检测模型',
    NOW(),
    NOW()
);

-- =====================================================
-- 验证查询
-- =====================================================

-- 验证设备类型
SELECT '=== 设备类型 ===' as info;
SELECT * FROM t_device_type WHERE type_code = 'PRESSURE_SENSOR_V1';

-- 验证设备字段
SELECT '=== 设备字段 ===' as info;
SELECT field_name, field_code, is_monitoring_key, is_ai_feature 
FROM t_device_field 
WHERE device_type_code = 'PRESSURE_SENSOR_V1'
ORDER BY sort_order;

-- 验证字段映射
SELECT '=== 字段映射 ===' as info;
SELECT 
    dfm.device_type_code,
    df.field_code,
    dfm.tdengine_column,
    dfm.is_tag
FROM t_device_field_mapping dfm
JOIN t_device_field df ON dfm.device_field_id = df.id
WHERE dfm.device_type_code = 'PRESSURE_SENSOR_V1';

-- 验证设备实例
SELECT '=== 设备实例 ===' as info;
SELECT * FROM t_device_info WHERE device_code = 'PS001';

-- 验证数据模型
SELECT '=== 数据模型 ===' as info;
SELECT model_name, model_code, model_type, is_active
FROM t_device_data_model 
WHERE device_type_code = 'PRESSURE_SENSOR_V1';
