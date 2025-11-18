# 新增设备类型与AI检测实现指南

## 📋 文档概述

**文档版本**: v1.0  
**创建日期**: 2025-11-10  
**适用系统**: DeviceMonitorV2  
**目标**: 指导开发人员完成新设备类型的添加和AI检测功能的集成测试

---

## 🎯 实施目标

本指南将帮助你完成以下任务：

1. ✅ 在系统中新增一个自定义设备类型（以"智能压力传感器"为例）
2. ✅ 配置设备类型的字段定义和元数据
3. ✅ 创建TDengine时序数据库表结构
4. ✅ 实现设备数据采集和存储
5. ✅ 集成AI异常检测功能
6. ✅ 配置健康评分系统
7. ✅ 完成端到端功能测试

---

## 📊 系统架构概览

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Vue3 + TS)                      │
│  - 设备管理界面                                           │
│  - AI检测可视化                                           │
│  - 健康评分展示                                           │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────┐
│                 后端 (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  设备管理API  │  │  AI检测API   │  │  数据查询API  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────┬───────────────────┬────────────────────────┘
             │                   │
    ┌────────▼────────┐  ┌──────▼──────────┐
    │   PostgreSQL    │  │    TDengine     │
    │  (业务数据)      │  │   (时序数据)     │
    └─────────────────┘  └─────────────────┘
```


### 数据流向

```
设备数据采集 → PostgreSQL(设备信息) → TDengine(时序数据) → AI分析引擎 → 结果展示
```

---

## 🚀 实施步骤

## 第一阶段：数据库准备

### 步骤 1.1：创建设备类型

**目标**: 在PostgreSQL中注册新的设备类型

**操作方式**: 通过API或数据库直接插入

#### 方式A：使用API（推荐）

```bash
# 请求地址
POST http://localhost:8001/api/v2/device-types

# 请求体
{
  "type_name": "智能压力传感器",
  "type_code": "PRESSURE_SENSOR_V1",
  "tdengine_stable_name": "st_pressure_sensor",
  "description": "用于监测管道压力的智能传感器，支持实时数据采集和异常检测",
  "is_active": true
}
```

#### 方式B：直接SQL插入

```sql
-- 连接到PostgreSQL数据库
-- 数据库: devicemonitor
-- 用户: postgres

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
```

**验证结果**:
```sql
SELECT * FROM t_device_type WHERE type_code = 'PRESSURE_SENSOR_V1';
```


### 步骤 1.2：定义设备字段

**目标**: 配置设备的数据采集字段和AI分析特征

**字段配置示例**:

```sql
-- 1. 压力值字段（主要监控指标）
INSERT INTO t_device_field (
    device_type_code,
    field_name,
    field_code,
    field_type,
    field_category,
    unit,
    description,
    is_required,
    sort_order,
    is_active,
    is_monitoring_key,
    is_ai_feature,
    aggregation_method,
    data_range,
    alarm_threshold,
    display_config,
    created_at,
    updated_at
) VALUES (
    'PRESSURE_SENSOR_V1',
    '压力值',
    'pressure',
    'float',
    'data_collection',
    'MPa',
    '当前压力读数',
    true,
    1,
    true,
    true,  -- 实时监控关键字段
    true,  -- AI分析特征字段
    'avg',
    '{"min": 0, "max": 10}',
    '{"warning": 8, "critical": 9.5}',
    '{"chart_type": "line", "color": "#1890ff"}',
    NOW(),
    NOW()
);

-- 2. 温度字段
INSERT INTO t_device_field (
    device_type_code, field_name, field_code, field_type, field_category,
    unit, description, is_required, sort_order, is_active,
    is_monitoring_key, is_ai_feature, aggregation_method,
    data_range, alarm_threshold, display_config, created_at, updated_at
) VALUES (
    'PRESSURE_SENSOR_V1', '温度', 'temperature', 'float', 'data_collection',
    '°C', '传感器温度', true, 2, true,
    true, true, 'avg',
    '{"min": -20, "max": 80}',
    '{"warning": 70, "critical": 75}',
    '{"chart_type": "line", "color": "#ff4d4f"}',
    NOW(), NOW()
);

-- 3. 振动值字段
INSERT INTO t_device_field (
    device_type_code, field_name, field_code, field_type, field_category,
    unit, description, is_required, sort_order, is_active,
    is_monitoring_key, is_ai_feature, aggregation_method,
    data_range, alarm_threshold, created_at, updated_at
) VALUES (
    'PRESSURE_SENSOR_V1', '振动值', 'vibration', 'float', 'data_collection',
    'mm/s', '设备振动强度', false, 3, true,
    true, true, 'max',
    '{"min": 0, "max": 50}',
    '{"warning": 40, "critical": 45}',
    NOW(), NOW()
);

-- 4. 设备状态字段
INSERT INTO t_device_field (
    device_type_code, field_name, field_code, field_type, field_category,
    unit, description, is_required, sort_order, is_active,
    is_monitoring_key, created_at, updated_at
) VALUES (
    'PRESSURE_SENSOR_V1', '设备状态', 'status', 'string', 'data_collection',
    NULL, '设备运行状态：online/offline/error/maintenance', true, 4, true,
    true, NOW(), NOW()
);
```

**验证结果**:
```sql
SELECT field_name, field_code, is_monitoring_key, is_ai_feature 
FROM t_device_field 
WHERE device_type_code = 'PRESSURE_SENSOR_V1'
ORDER BY sort_order;
```


### 步骤 1.3：创建TDengine超级表

**目标**: 在TDengine中创建时序数据存储表

**连接TDengine**:
```bash
# 连接信息
地址: 127.0.0.1:6041
数据库: devicemonitor
用户名: root
密码: taosdata
```

**创建超级表SQL**:
```sql
-- 切换到设备监控数据库
USE devicemonitor;

-- 创建压力传感器超级表
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

-- 查看超级表信息
SHOW STABLES LIKE 'st_pressure_sensor';
```

**预期输出**:
```
name                | type      | length | note
--------------------|-----------|--------|------
ts                  | TIMESTAMP | 8      |
pressure            | FLOAT     | 4      |
temperature         | FLOAT     | 4      |
vibration           | FLOAT     | 4      |
status              | NCHAR     | 20     |
error_code          | NCHAR     | 50     |
error_message       | NCHAR     | 500    |
device_code         | NCHAR     | 50     | TAG
device_name         | NCHAR     | 100    | TAG
install_location    | NCHAR     | 255    | TAG
```


### 步骤 1.4：配置字段映射

**目标**: 建立PostgreSQL字段与TDengine列的映射关系

```sql
-- 获取字段ID（用于外键关联）
-- 先查询字段ID
SELECT id, field_code FROM t_device_field 
WHERE device_type_code = 'PRESSURE_SENSOR_V1';

-- 假设查询结果：
-- id=1, field_code='pressure'
-- id=2, field_code='temperature'
-- id=3, field_code='vibration'
-- id=4, field_code='status'

-- 创建字段映射
INSERT INTO t_device_field_mapping (
    device_type_code,
    tdengine_database,
    tdengine_stable,
    tdengine_column,
    device_field_id,
    is_tag,
    is_active,
    created_at,
    updated_at
) VALUES
    ('PRESSURE_SENSOR_V1', 'devicemonitor', 'st_pressure_sensor', 'pressure', 1, false, true, NOW(), NOW()),
    ('PRESSURE_SENSOR_V1', 'devicemonitor', 'st_pressure_sensor', 'temperature', 2, false, true, NOW(), NOW()),
    ('PRESSURE_SENSOR_V1', 'devicemonitor', 'st_pressure_sensor', 'vibration', 3, false, true, NOW(), NOW()),
    ('PRESSURE_SENSOR_V1', 'devicemonitor', 'st_pressure_sensor', 'status', 4, false, true, NOW(), NOW());

-- 验证映射
SELECT 
    dfm.device_type_code,
    df.field_code,
    dfm.tdengine_column,
    dfm.is_tag
FROM t_device_field_mapping dfm
JOIN t_device_field df ON dfm.device_field_id = df.id
WHERE dfm.device_type_code = 'PRESSURE_SENSOR_V1';
```

---

## 第二阶段：设备实例创建

### 步骤 2.1：创建测试设备

**通过API创建**:

```bash
POST http://localhost:8001/api/v2/devices

# 请求体
{
  "device_code": "PS001",
  "device_name": "1号车间压力传感器",
  "device_model": "PS-3000",
  "device_type": "PRESSURE_SENSOR_V1",
  "manufacturer": "华为技术有限公司",
  "production_date": "2024-01-15",
  "install_date": "2024-02-01",
  "install_location": "1号车间-A区-管道1",
  "online_address": "192.168.1.101",
  "team_name": "设备维护一组",
  "description": "用于监测1号车间主管道压力"
}
```

**或使用SQL**:
```sql
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
```

**验证**:
```sql
SELECT * FROM t_device_info WHERE device_code = 'PS001';
```


### 步骤 2.2：创建TDengine子表

**目标**: 为具体设备创建时序数据表

```sql
-- 连接TDengine
USE devicemonitor;

-- 创建设备子表（使用超级表）
CREATE TABLE IF NOT EXISTS tb_ps001 USING st_pressure_sensor 
TAGS (
    'PS001',                      -- device_code
    '1号车间压力传感器',           -- device_name
    '1号车间-A区-管道1'            -- install_location
);

-- 验证子表创建
SHOW TABLES LIKE 'tb_ps001';

-- 查看子表结构
DESCRIBE tb_ps001;
```

---

## 第三阶段：数据采集与存储

### 步骤 3.1：模拟数据写入

**方式A：通过TDengine直接插入测试数据**

```sql
-- 插入模拟数据（正常运行状态）
INSERT INTO tb_ps001 VALUES 
    (NOW - 10m, 5.2, 45.3, 2.1, 'online', NULL, NULL),
    (NOW - 9m, 5.3, 45.5, 2.2, 'online', NULL, NULL),
    (NOW - 8m, 5.1, 45.4, 2.0, 'online', NULL, NULL),
    (NOW - 7m, 5.4, 45.6, 2.3, 'online', NULL, NULL),
    (NOW - 6m, 5.2, 45.5, 2.1, 'online', NULL, NULL),
    (NOW - 5m, 5.5, 45.7, 2.4, 'online', NULL, NULL),
    (NOW - 4m, 8.9, 68.2, 38.5, 'error', 'E001', '压力异常'),  -- 异常数据
    (NOW - 3m, 9.2, 70.1, 42.3, 'error', 'E001', '压力异常'),  -- 异常数据
    (NOW - 2m, 5.3, 46.0, 2.2, 'online', NULL, NULL),
    (NOW - 1m, 5.2, 45.8, 2.1, 'online', NULL, NULL),
    (NOW, 5.4, 45.9, 2.3, 'online', NULL, NULL);

-- 验证数据
SELECT * FROM tb_ps001 ORDER BY ts DESC LIMIT 20;

-- 统计数据
SELECT 
    COUNT(*) as total_records,
    AVG(pressure) as avg_pressure,
    MAX(pressure) as max_pressure,
    MIN(pressure) as min_pressure
FROM tb_ps001;
```

**方式B：通过Python脚本批量生成数据**

创建文件 `scripts/generate_pressure_sensor_data.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力传感器测试数据生成脚本
"""

import taos
import random
from datetime import datetime, timedelta

# TDengine连接配置
TDENGINE_HOST = "127.0.0.1"
TDENGINE_PORT = 6041
TDENGINE_USER = "root"
TDENGINE_PASSWORD = "taosdata"
TDENGINE_DATABASE = "devicemonitor"

def generate_test_data():
    """生成测试数据"""
    # 连接TDengine
    conn = taos.connect(
        host=TDENGINE_HOST,
        port=TDENGINE_PORT,
        user=TDENGINE_USER,
        password=TDENGINE_PASSWORD,
        database=TDENGINE_DATABASE
    )
    cursor = conn.cursor()
    
    # 生成24小时的数据，每分钟一条
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(1440):  # 24小时 * 60分钟
        timestamp = base_time + timedelta(minutes=i)
        
        # 正常数据范围
        pressure = round(random.uniform(4.8, 5.8), 2)
        temperature = round(random.uniform(43.0, 48.0), 2)
        vibration = round(random.uniform(1.5, 3.0), 2)
        status = 'online'
        error_code = 'NULL'
        error_message = 'NULL'
        
        # 随机插入异常数据（5%概率）
        if random.random() < 0.05:
            pressure = round(random.uniform(8.5, 9.5), 2)
            temperature = round(random.uniform(65.0, 75.0), 2)
            vibration = round(random.uniform(35.0, 45.0), 2)
            status = 'error'
            error_code = "'E001'"
            error_message = "'压力异常'"
        
        # 插入数据
        sql = f"""
        INSERT INTO tb_ps001 VALUES (
            '{timestamp.strftime('%Y-%m-%d %H:%M:%S')}',
            {pressure}, {temperature}, {vibration},
            '{status}', {error_code}, {error_message}
        )
        """
        cursor.execute(sql)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ 成功生成1440条测试数据")

if __name__ == "__main__":
    generate_test_data()
```

**运行脚本**:
```bash
cd scripts
python generate_pressure_sensor_data.py
```


---

## 第四阶段：AI异常检测集成

### 步骤 4.1：测试异常检测API

**目标**: 验证AI异常检测功能是否正常工作

**测试用例1：统计方法检测**

```bash
POST http://localhost:8001/api/v2/ai/anomalies/detect

# 请求头
Authorization: Bearer <your_token>
Content-Type: application/json

# 请求体
{
  "data": [5.2, 5.3, 5.1, 5.4, 8.9, 9.2, 5.3, 5.2, 5.4],
  "device_code": "PS001",
  "device_name": "1号车间压力传感器",
  "method": "statistical",
  "threshold": 3.0,
  "save_to_db": true
}
```

**预期响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "is_anomaly": true,
    "anomaly_count": 2,
    "anomaly_rate": 22.22,
    "anomalies": [
      {
        "index": 4,
        "value": 8.9,
        "score": 0.85,
        "severity": "高",
        "method": "statistical"
      },
      {
        "index": 5,
        "value": 9.2,
        "score": 0.92,
        "severity": "极高",
        "method": "statistical"
      }
    ],
    "data_points": 9,
    "method_used": "statistical"
  }
}
```

**测试用例2：组合方法检测**

```bash
POST http://localhost:8001/api/v2/ai/anomalies/detect

{
  "data": [5.2, 5.3, 5.1, 5.4, 5.2, 5.5, 8.9, 9.2, 5.3, 5.2, 5.4],
  "device_code": "PS001",
  "method": "combined",
  "threshold": 2.5,
  "save_to_db": true
}
```

**测试用例3：从TDengine查询数据并检测**

创建测试脚本 `scripts/test_ai_detection.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI异常检测测试脚本
"""

import requests
import taos
from datetime import datetime, timedelta

# API配置
API_BASE_URL = "http://localhost:8001/api/v2"
API_TOKEN = "your_jwt_token_here"  # 需要先登录获取

# TDengine配置
TDENGINE_HOST = "127.0.0.1"
TDENGINE_PORT = 6041
TDENGINE_USER = "root"
TDENGINE_PASSWORD = "taosdata"
TDENGINE_DATABASE = "devicemonitor"

def get_device_data(device_code, hours=1):
    """从TDengine获取设备数据"""
    conn = taos.connect(
        host=TDENGINE_HOST,
        port=TDENGINE_PORT,
        user=TDENGINE_USER,
        password=TDENGINE_PASSWORD,
        database=TDENGINE_DATABASE
    )
    cursor = conn.cursor()
    
    # 查询最近N小时的压力数据
    sql = f"""
    SELECT pressure FROM tb_{device_code.lower()}
    WHERE ts >= NOW - {hours}h
    ORDER BY ts ASC
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # 提取压力值
    pressure_data = [row[0] for row in results]
    return pressure_data

def test_anomaly_detection(device_code, data, method="combined"):
    """测试异常检测"""
    url = f"{API_BASE_URL}/ai/anomalies/detect"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "data": data,
        "device_code": device_code,
        "method": method,
        "threshold": 3.0,
        "save_to_db": True
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 异常检测成功")
        print(f"   检测到异常: {result['data']['is_anomaly']}")
        print(f"   异常点数量: {result['data']['anomaly_count']}")
        print(f"   异常率: {result['data']['anomaly_rate']}%")
        
        if result['data']['anomalies']:
            print(f"\n   异常详情:")
            for anomaly in result['data']['anomalies']:
                print(f"   - 索引{anomaly['index']}: 值={anomaly['value']}, "
                      f"分数={anomaly['score']}, 严重程度={anomaly['severity']}")
    else:
        print(f"❌ 异常检测失败: {response.text}")

if __name__ == "__main__":
    # 获取设备数据
    print("📊 正在获取设备数据...")
    pressure_data = get_device_data("PS001", hours=1)
    print(f"   获取到 {len(pressure_data)} 条数据")
    
    # 执行异常检测
    print("\n🔍 开始异常检测...")
    test_anomaly_detection("PS001", pressure_data, method="combined")
```

**运行测试**:
```bash
python scripts/test_ai_detection.py
```


### 步骤 4.2：配置AI数据模型

**目标**: 创建用于AI分析的数据模型配置

```sql
-- 创建实时监控数据模型
INSERT INTO t_device_data_model (
    model_name,
    model_code,
    device_type_code,
    model_type,
    selected_fields,
    version,
    is_active,
    is_default,
    description,
    created_at,
    updated_at
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

-- 创建AI分析数据模型
INSERT INTO t_device_data_model (
    model_name,
    model_code,
    device_type_code,
    model_type,
    selected_fields,
    ai_config,
    version,
    is_active,
    description,
    created_at,
    updated_at
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

-- 验证模型创建
SELECT model_name, model_code, model_type, is_active 
FROM t_device_data_model 
WHERE device_type_code = 'PRESSURE_SENSOR_V1';
```


---

## 第五阶段：健康评分系统

### 步骤 5.1：创建健康评分配置

**通过API创建健康评分**:

```bash
POST http://localhost:8001/api/v2/ai/health-scores/records

# 请求头
Authorization: Bearer <your_token>
Content-Type: application/json

# 请求体
{
  "score_name": "PS001设备健康评分",
  "description": "基于压力、温度、振动等多维度指标的综合健康评分",
  "target_type": "device",
  "target_id": 1,  # 设备ID，需要从t_device_info查询
  "scoring_algorithm": "weighted_average",
  "weight_config": {
    "pressure_stability": 0.4,
    "temperature_normal": 0.3,
    "vibration_level": 0.2,
    "error_frequency": 0.1
  },
  "threshold_config": {
    "excellent": 90,
    "good": 75,
    "fair": 60,
    "poor": 40,
    "critical": 0
  }
}
```

### 步骤 5.2：计算健康评分

**创建健康评分计算脚本** `scripts/calculate_health_score.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备健康评分计算脚本
"""

import taos
import numpy as np
from datetime import datetime, timedelta

def calculate_pressure_stability(data, normal_range=(4.5, 6.0)):
    """计算压力稳定性得分"""
    in_range = sum(1 for x in data if normal_range[0] <= x <= normal_range[1])
    stability_score = (in_range / len(data)) * 100
    return stability_score

def calculate_temperature_normal(data, normal_range=(40, 50)):
    """计算温度正常性得分"""
    in_range = sum(1 for x in data if normal_range[0] <= x <= normal_range[1])
    normal_score = (in_range / len(data)) * 100
    return normal_score

def calculate_vibration_level(data, threshold=30):
    """计算振动水平得分"""
    low_vibration = sum(1 for x in data if x < threshold)
    vibration_score = (low_vibration / len(data)) * 100
    return vibration_score

def calculate_error_frequency(error_count, total_count):
    """计算错误频率得分"""
    error_rate = error_count / total_count
    error_score = max(0, (1 - error_rate) * 100)
    return error_score

def get_device_metrics(device_code, hours=24):
    """获取设备指标数据"""
    conn = taos.connect(
        host="127.0.0.1",
        port=6041,
        user="root",
        password="taosdata",
        database="devicemonitor"
    )
    cursor = conn.cursor()
    
    # 查询数据
    sql = f"""
    SELECT pressure, temperature, vibration, status
    FROM tb_{device_code.lower()}
    WHERE ts >= NOW - {hours}h
    ORDER BY ts ASC
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # 解析数据
    pressure_data = [row[0] for row in results if row[0] is not None]
    temperature_data = [row[1] for row in results if row[1] is not None]
    vibration_data = [row[2] for row in results if row[2] is not None]
    error_count = sum(1 for row in results if row[3] == 'error')
    
    return {
        'pressure': pressure_data,
        'temperature': temperature_data,
        'vibration': vibration_data,
        'error_count': error_count,
        'total_count': len(results)
    }

def calculate_health_score(device_code):
    """计算设备健康评分"""
    print(f"📊 正在计算设备 {device_code} 的健康评分...")
    
    # 获取设备数据
    metrics = get_device_metrics(device_code, hours=24)
    
    if metrics['total_count'] == 0:
        print("❌ 没有找到设备数据")
        return None
    
    # 计算各维度得分
    pressure_score = calculate_pressure_stability(metrics['pressure'])
    temperature_score = calculate_temperature_normal(metrics['temperature'])
    vibration_score = calculate_vibration_level(metrics['vibration'])
    error_score = calculate_error_frequency(
        metrics['error_count'], 
        metrics['total_count']
    )
    
    # 权重配置
    weights = {
        'pressure': 0.4,
        'temperature': 0.3,
        'vibration': 0.2,
        'error': 0.1
    }
    
    # 计算总分
    overall_score = (
        pressure_score * weights['pressure'] +
        temperature_score * weights['temperature'] +
        vibration_score * weights['vibration'] +
        error_score * weights['error']
    )
    
    # 确定风险等级
    if overall_score >= 90:
        risk_level = "优秀"
    elif overall_score >= 75:
        risk_level = "良好"
    elif overall_score >= 60:
        risk_level = "一般"
    elif overall_score >= 40:
        risk_level = "较差"
    else:
        risk_level = "危险"
    
    # 输出结果
    print(f"\n✅ 健康评分计算完成:")
    print(f"   总体评分: {overall_score:.2f}")
    print(f"   风险等级: {risk_level}")
    print(f"\n   维度得分:")
    print(f"   - 压力稳定性: {pressure_score:.2f} (权重: {weights['pressure']})")
    print(f"   - 温度正常性: {temperature_score:.2f} (权重: {weights['temperature']})")
    print(f"   - 振动水平: {vibration_score:.2f} (权重: {weights['vibration']})")
    print(f"   - 错误频率: {error_score:.2f} (权重: {weights['error']})")
    print(f"\n   数据统计:")
    print(f"   - 总数据点: {metrics['total_count']}")
    print(f"   - 错误次数: {metrics['error_count']}")
    
    return {
        'overall_score': overall_score,
        'risk_level': risk_level,
        'dimension_scores': {
            'pressure_stability': pressure_score,
            'temperature_normal': temperature_score,
            'vibration_level': vibration_score,
            'error_frequency': error_score
        }
    }

if __name__ == "__main__":
    calculate_health_score("PS001")
```

**运行评分计算**:
```bash
python scripts/calculate_health_score.py
```


---

## 第六阶段：趋势预测

### 步骤 6.1：创建预测任务

**通过API创建预测**:

```bash
POST http://localhost:8001/api/v2/ai/predictions

# 请求头
Authorization: Bearer <your_token>
Content-Type: application/json

# 请求体
{
  "prediction_name": "PS001压力趋势预测",
  "description": "预测未来24小时的压力变化趋势",
  "target_variable": "pressure",
  "prediction_horizon": 24,
  "model_type": "ARIMA",
  "parameters": {
    "p": 2,
    "d": 1,
    "q": 2,
    "seasonal": false
  },
  "data_source": "tb_ps001",
  "data_filters": {
    "time_range": "7d",
    "min_data_points": 100
  }
}
```

### 步骤 6.2：查询预测结果

```bash
GET http://localhost:8001/api/v2/ai/predictions/{prediction_id}

# 响应示例
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "prediction_name": "PS001压力趋势预测",
    "status": "completed",
    "progress": 100,
    "result_data": {
      "predictions": [
        {"timestamp": "2025-11-11 00:00:00", "value": 5.3, "confidence_lower": 4.8, "confidence_upper": 5.8},
        {"timestamp": "2025-11-11 01:00:00", "value": 5.4, "confidence_lower": 4.9, "confidence_upper": 5.9}
      ],
      "trend": "stable",
      "anomaly_probability": 0.05
    },
    "accuracy_score": 0.92,
    "completed_at": "2025-11-10 12:00:00"
  }
}
```

---

## 第七阶段：前端集成测试

### 步骤 7.1：访问设备管理页面

1. 启动前端服务
```bash
cd web
pnpm dev
```

2. 访问 http://localhost:3000

3. 登录系统（默认账号：admin / admin123）

4. 导航到 **设备管理** → **设备列表**

5. 查找设备 "PS001" 或 "1号车间压力传感器"

**💡 提示**: 如需了解如何通过前端页面操作新增设备分类和设备，请参考 [前端页面操作指南](./前端页面操作指南.md)

### 步骤 7.2：查看实时监控

1. 点击设备详情

2. 查看实时数据面板：
   - 压力值曲线图
   - 温度值曲线图
   - 振动值曲线图
   - 设备状态指示器

3. 验证数据更新（如果配置了WebSocket）

### 步骤 7.3：查看AI分析结果

1. 导航到 **AI监控** → **异常检测**

2. 选择设备 "PS001"

3. 查看异常检测结果：
   - 异常点标记
   - 异常严重程度
   - 时间分布图

4. 导航到 **AI监控** → **健康评分**

5. 查看健康评分卡片：
   - 总体评分
   - 风险等级
   - 维度得分雷达图
   - 趋势变化曲线

### 步骤 7.4：查看趋势预测

1. 导航到 **AI监控** → **趋势预测**

2. 选择设备和预测指标

3. 查看预测结果：
   - 历史数据曲线
   - 预测数据曲线
   - 置信区间
   - 趋势分析

---

## 第八阶段：前端页面维护

### 步骤 8.1：前端项目结构说明

**前端技术栈**:
- Vue 3 (Composition API)
- TypeScript
- Naive UI (组件库)
- Pinia (状态管理)
- Vue Router (路由管理)

**项目结构**:
```
web/
├── src/
│   ├── views/              # 页面组件
│   │   ├── device/         # 设备管理模块
│   │   │   ├── baseinfo/   # 设备信息管理
│   │   │   ├── type/       # 设备类型管理
│   │   │   ├── index.vue   # 设备管理首页
│   │   │   └── route.ts    # 路由配置
│   │   │
│   │   └── ai-monitor/     # AI监控模块
│   │       ├── dashboard/           # AI监控总览
│   │       ├── anomaly-detection/   # 异常检测
│   │       ├── trend-prediction/    # 趋势预测
│   │       ├── health-scoring/      # 健康评分
│   │       ├── model-management/    # 模型管理
│   │       ├── smart-analysis/      # 智能分析
│   │       ├── data-annotation/     # 数据标注
│   │       ├── index.vue            # AI监控首页
│   │       └── route.ts             # 路由配置
│   │
│   ├── router/             # 路由配置
│   ├── store/              # Pinia状态管理
│   ├── api/                # API接口
│   ├── components/         # 公共组件
│   └── utils/              # 工具函数
│
└── package.json
```

### 步骤 8.2：添加新设备类型的页面支持

#### 方式A：修改现有设备管理页面（推荐）

**文件位置**: `web/src/views/device/baseinfo/index.vue`

**修改内容**:

1. **添加设备类型筛选**

在设备列表的查询表单中，添加设备类型下拉选择：

```vue
<!-- 在查询表单中添加 -->
<n-form-item label="设备类型" path="device_type">
  <n-select
    v-model:value="queryParams.device_type"
    :options="deviceTypeOptions"
    placeholder="请选择设备类型"
    clearable
  />
</n-form-item>
```

2. **添加设备类型选项数据**

```typescript
// 在 setup() 中添加
const deviceTypeOptions = ref([
  { label: '全部', value: '' },
  { label: '智能压力传感器', value: 'PRESSURE_SENSOR_V1' },
  // 其他设备类型...
])

// 或者从API动态获取
const loadDeviceTypes = async () => {
  const response = await deviceTypeApi.getList()
  deviceTypeOptions.value = response.data.items.map(item => ({
    label: item.type_name,
    value: item.type_code
  }))
}
```

3. **添加设备类型特定字段显示**

在设备详情或编辑表单中，根据设备类型动态显示字段：

```vue
<template>
  <!-- 基础字段 -->
  <n-form-item label="设备编号" path="device_code">
    <n-input v-model:value="formData.device_code" />
  </n-form-item>
  
  <!-- 压力传感器特定字段 -->
  <template v-if="formData.device_type === 'PRESSURE_SENSOR_V1'">
    <n-form-item label="压力范围" path="pressure_range">
      <n-input v-model:value="formData.pressure_range" placeholder="例如: 0-10 MPa" />
    </n-form-item>
    
    <n-form-item label="温度范围" path="temperature_range">
      <n-input v-model:value="formData.temperature_range" placeholder="例如: -20-80 °C" />
    </n-form-item>
  </template>
</template>
```

#### 方式B：创建专用设备类型页面

**步骤1**: 创建新页面文件

```bash
# 创建压力传感器专用页面
mkdir -p web/src/views/device/pressure-sensor
touch web/src/views/device/pressure-sensor/index.vue
```

**步骤2**: 编写页面组件

创建文件 `web/src/views/device/pressure-sensor/index.vue`:

```vue
<template>
  <div class="pressure-sensor-page">
    <n-card title="压力传感器管理">
      <!-- 查询表单 -->
      <n-form inline :model="queryParams" label-placement="left">
        <n-form-item label="设备编号">
          <n-input v-model:value="queryParams.device_code" placeholder="请输入设备编号" />
        </n-form-item>
        
        <n-form-item label="安装位置">
          <n-input v-model:value="queryParams.install_location" placeholder="请输入安装位置" />
        </n-form-item>
        
        <n-form-item>
          <n-button type="primary" @click="handleQuery">
            <template #icon>
              <n-icon><SearchOutline /></n-icon>
            </template>
            查询
          </n-button>
          <n-button @click="handleReset" style="margin-left: 8px">重置</n-button>
        </n-form-item>
      </n-form>
      
      <!-- 操作按钮 -->
      <n-space style="margin-bottom: 16px">
        <n-button type="primary" @click="handleAdd">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          新增传感器
        </n-button>
      </n-space>
      
      <!-- 数据表格 -->
      <n-data-table
        :columns="columns"
        :data="tableData"
        :loading="loading"
        :pagination="pagination"
        @update:page="handlePageChange"
      />
    </n-card>
    
    <!-- 编辑对话框 -->
    <n-modal v-model:show="showModal" preset="card" title="压力传感器信息" style="width: 800px">
      <n-form ref="formRef" :model="formData" :rules="rules" label-placement="left" label-width="120px">
        <n-form-item label="设备编号" path="device_code">
          <n-input v-model:value="formData.device_code" placeholder="例如: PS001" />
        </n-form-item>
        
        <n-form-item label="设备名称" path="device_name">
          <n-input v-model:value="formData.device_name" placeholder="例如: 1号车间压力传感器" />
        </n-form-item>
        
        <n-form-item label="设备型号" path="device_model">
          <n-input v-model:value="formData.device_model" placeholder="例如: PS-3000" />
        </n-form-item>
        
        <n-form-item label="压力范围" path="pressure_range">
          <n-input v-model:value="formData.pressure_range" placeholder="例如: 0-10 MPa" />
        </n-form-item>
        
        <n-form-item label="温度范围" path="temperature_range">
          <n-input v-model:value="formData.temperature_range" placeholder="例如: -20-80 °C" />
        </n-form-item>
        
        <n-form-item label="安装位置" path="install_location">
          <n-input v-model:value="formData.install_location" placeholder="例如: 1号车间-A区-管道1" />
        </n-form-item>
      </n-form>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { NButton, NIcon, useMessage } from 'naive-ui'
import { SearchOutline, AddOutline } from '@vicons/ionicons5'
import { deviceApi } from '@/api/device'

const message = useMessage()
const loading = ref(false)
const showModal = ref(false)
const tableData = ref([])

// 查询参数
const queryParams = reactive({
  device_code: '',
  install_location: '',
  device_type: 'PRESSURE_SENSOR_V1' // 固定为压力传感器
})

// 表单数据
const formData = reactive({
  device_code: '',
  device_name: '',
  device_model: '',
  device_type: 'PRESSURE_SENSOR_V1',
  pressure_range: '',
  temperature_range: '',
  install_location: ''
})

// 表格列定义
const columns = [
  { title: '设备编号', key: 'device_code' },
  { title: '设备名称', key: 'device_name' },
  { title: '设备型号', key: 'device_model' },
  { title: '安装位置', key: 'install_location' },
  { title: '在线地址', key: 'online_address' },
  {
    title: '操作',
    key: 'actions',
    render(row) {
      return h('div', [
        h(NButton, { size: 'small', onClick: () => handleEdit(row) }, { default: () => '编辑' }),
        h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row), style: 'margin-left: 8px' }, { default: () => '删除' })
      ])
    }
  }
]

// 分页配置
const pagination = reactive({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100]
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await deviceApi.getList({
      page: pagination.page,
      page_size: pagination.pageSize,
      ...queryParams
    })
    tableData.value = response.data.items
    pagination.itemCount = response.data.total
  } catch (error) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 查询
const handleQuery = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  Object.assign(queryParams, {
    device_code: '',
    install_location: '',
    device_type: 'PRESSURE_SENSOR_V1'
  })
  handleQuery()
}

// 新增
const handleAdd = () => {
  Object.assign(formData, {
    device_code: '',
    device_name: '',
    device_model: '',
    device_type: 'PRESSURE_SENSOR_V1',
    pressure_range: '',
    temperature_range: '',
    install_location: ''
  })
  showModal.value = true
}

// 编辑
const handleEdit = (row) => {
  Object.assign(formData, row)
  showModal.value = true
}

// 删除
const handleDelete = async (row) => {
  // 实现删除逻辑
}

// 提交
const handleSubmit = async () => {
  // 实现提交逻辑
}

// 页码变化
const handlePageChange = (page) => {
  pagination.page = page
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.pressure-sensor-page {
  padding: 16px;
}
</style>
```

**步骤3**: 添加路由配置

修改 `web/src/views/device/route.ts`:

```typescript
import type { RouteRecordRaw } from 'vue-router'

const Layout = () => import('@/layout/index.vue')

const route: RouteRecordRaw = {
  path: '/device',
  name: 'Device',
  component: Layout,
  meta: {
    title: '设备管理',
    icon: 'mdi-air-humidifier',
    requiresAuth: true,
  },
  children: [
    // ... 其他路由
    {
      path: 'pressure-sensor',
      name: 'PressureSensor',
      component: () => import('./pressure-sensor/index.vue'),
      meta: {
        title: '压力传感器',
        icon: 'mdi:gauge',
        requiresAuth: true,
        keepAlive: true,
      },
    },
  ],
}

export default route
```

### 步骤 8.3：添加AI监控页面支持

#### 修改异常检测页面

**文件位置**: `web/src/views/ai-monitor/anomaly-detection/index.vue`

**添加设备类型筛选**:

```vue
<template>
  <div class="anomaly-detection-page">
    <n-card title="异常检测">
      <!-- 查询表单 -->
      <n-form inline :model="queryParams">
        <n-form-item label="设备类型">
          <n-select
            v-model:value="queryParams.device_type"
            :options="deviceTypeOptions"
            placeholder="请选择设备类型"
            @update:value="handleDeviceTypeChange"
          />
        </n-form-item>
        
        <n-form-item label="设备">
          <n-select
            v-model:value="queryParams.device_code"
            :options="deviceOptions"
            placeholder="请选择设备"
            filterable
          />
        </n-form-item>
        
        <n-form-item label="检测方法">
          <n-select
            v-model:value="queryParams.method"
            :options="methodOptions"
            placeholder="请选择检测方法"
          />
        </n-form-item>
        
        <n-form-item>
          <n-button type="primary" @click="handleDetect">开始检测</n-button>
        </n-form-item>
      </n-form>
      
      <!-- 检测结果展示 -->
      <n-card v-if="detectionResult" title="检测结果" style="margin-top: 16px">
        <n-descriptions :column="3">
          <n-descriptions-item label="是否异常">
            <n-tag :type="detectionResult.is_anomaly ? 'error' : 'success'">
              {{ detectionResult.is_anomaly ? '是' : '否' }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="异常点数量">
            {{ detectionResult.anomaly_count }}
          </n-descriptions-item>
          <n-descriptions-item label="异常率">
            {{ detectionResult.anomaly_rate }}%
          </n-descriptions-item>
        </n-descriptions>
        
        <!-- 异常点详情 -->
        <n-data-table
          v-if="detectionResult.anomalies.length > 0"
          :columns="anomalyColumns"
          :data="detectionResult.anomalies"
          style="margin-top: 16px"
        />
        
        <!-- 数据可视化图表 -->
        <div ref="chartRef" style="width: 100%; height: 400px; margin-top: 16px"></div>
      </n-card>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { aiApi } from '@/api/ai'
import { deviceApi } from '@/api/device'
import * as echarts from 'echarts'

const message = useMessage()
const chartRef = ref(null)
const detectionResult = ref(null)

// 设备类型选项
const deviceTypeOptions = ref([
  { label: '智能压力传感器', value: 'PRESSURE_SENSOR_V1' },
  // 其他设备类型...
])

// 设备选项
const deviceOptions = ref([])

// 检测方法选项
const methodOptions = [
  { label: '统计方法', value: 'statistical' },
  { label: '孤立森林', value: 'isolation_forest' },
  { label: '组合方法', value: 'combined' }
]

// 查询参数
const queryParams = reactive({
  device_type: 'PRESSURE_SENSOR_V1',
  device_code: '',
  method: 'combined'
})

// 异常点表格列
const anomalyColumns = [
  { title: '索引', key: 'index' },
  { title: '异常值', key: 'value' },
  { title: '异常分数', key: 'score' },
  {
    title: '严重程度',
    key: 'severity',
    render(row) {
      const typeMap = {
        '极低': 'default',
        '低': 'info',
        '中等': 'warning',
        '高': 'error',
        '极高': 'error'
      }
      return h(NTag, { type: typeMap[row.severity] }, { default: () => row.severity })
    }
  }
]

// 设备类型变化
const handleDeviceTypeChange = async (value) => {
  // 加载该类型下的设备列表
  const response = await deviceApi.getList({ device_type: value })
  deviceOptions.value = response.data.items.map(item => ({
    label: `${item.device_name} (${item.device_code})`,
    value: item.device_code
  }))
  queryParams.device_code = ''
}

// 开始检测
const handleDetect = async () => {
  if (!queryParams.device_code) {
    message.warning('请选择设备')
    return
  }
  
  try {
    // 调用异常检测API
    const response = await aiApi.detectAnomaly({
      device_code: queryParams.device_code,
      method: queryParams.method
    })
    
    detectionResult.value = response.data
    
    // 绘制图表
    renderChart()
    
    message.success('检测完成')
  } catch (error) {
    message.error('检测失败')
  }
}

// 绘制图表
const renderChart = () => {
  if (!chartRef.value) return
  
  const chart = echarts.init(chartRef.value)
  
  // 图表配置
  const option = {
    title: { text: '异常检测结果' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: detectionResult.value.data.map((_, i) => i) },
    yAxis: { type: 'value' },
    series: [
      {
        name: '数据值',
        type: 'line',
        data: detectionResult.value.data,
        markPoint: {
          data: detectionResult.value.anomalies.map(a => ({
            coord: [a.index, a.value],
            value: a.value,
            itemStyle: { color: 'red' }
          }))
        }
      }
    ]
  }
  
  chart.setOption(option)
}

onMounted(() => {
  handleDeviceTypeChange(queryParams.device_type)
})
</script>
```

### 步骤 8.4：添加菜单配置

如果需要在系统菜单中显示新页面，需要在数据库中添加菜单配置：

```sql
-- 添加压力传感器菜单
INSERT INTO t_menu (
    menu_name, parent_id, menu_type, path, component,
    icon, order_num, visible, status, perms,
    created_at, updated_at
) VALUES (
    '压力传感器', 
    (SELECT id FROM t_menu WHERE path = '/device'),  -- 父菜单ID
    'C',  -- 菜单类型：C=菜单，M=目录，F=按钮
    'pressure-sensor',
    'device/pressure-sensor/index',
    'mdi:gauge',
    3,
    true,
    true,
    'device:pressure:list',
    NOW(),
    NOW()
);
```

### 步骤 8.5：API接口封装

创建设备类型专用的API接口文件：

**文件位置**: `web/src/api/pressure-sensor.ts`

```typescript
import { http } from '@/utils/http'

export interface PressureSensorData {
  device_code: string
  device_name: string
  device_model: string
  pressure_range: string
  temperature_range: string
  install_location: string
}

export const pressureSensorApi = {
  // 获取压力传感器列表
  getList(params: any) {
    return http.get('/api/v2/devices', {
      params: {
        ...params,
        device_type: 'PRESSURE_SENSOR_V1'
      }
    })
  },
  
  // 获取压力传感器详情
  getDetail(id: number) {
    return http.get(`/api/v2/devices/${id}`)
  },
  
  // 创建压力传感器
  create(data: PressureSensorData) {
    return http.post('/api/v2/devices', {
      ...data,
      device_type: 'PRESSURE_SENSOR_V1'
    })
  },
  
  // 更新压力传感器
  update(id: number, data: PressureSensorData) {
    return http.put(`/api/v2/devices/${id}`, data)
  },
  
  // 删除压力传感器
  delete(id: number) {
    return http.delete(`/api/v2/devices/${id}`)
  },
  
  // 获取实时数据
  getRealTimeData(deviceCode: string) {
    return http.get('/api/v2/data/realtime', {
      params: { device_code: deviceCode }
    })
  },
  
  // 获取历史数据
  getHistoryData(deviceCode: string, params: any) {
    return http.get('/api/v2/data/history', {
      params: {
        device_code: deviceCode,
        ...params
      }
    })
  }
}
```

### 步骤 8.6：状态管理（可选）

如果需要全局状态管理，可以创建Pinia Store：

**文件位置**: `web/src/store/modules/pressure-sensor.ts`

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { pressureSensorApi } from '@/api/pressure-sensor'

export const usePressureSensorStore = defineStore('pressureSensor', () => {
  const sensorList = ref([])
  const currentSensor = ref(null)
  const loading = ref(false)
  
  // 加载传感器列表
  const loadSensorList = async (params: any) => {
    loading.value = true
    try {
      const response = await pressureSensorApi.getList(params)
      sensorList.value = response.data.items
      return response.data
    } finally {
      loading.value = false
    }
  }
  
  // 获取传感器详情
  const getSensorDetail = async (id: number) => {
    const response = await pressureSensorApi.getDetail(id)
    currentSensor.value = response.data
    return response.data
  }
  
  return {
    sensorList,
    currentSensor,
    loading,
    loadSensorList,
    getSensorDetail
  }
})
```

### 步骤 8.7：页面维护总结

**前端页面维护的关键步骤**:

1. ✅ **创建或修改页面组件** (`web/src/views/`)
2. ✅ **配置路由** (`route.ts`)
3. ✅ **封装API接口** (`web/src/api/`)
4. ✅ **添加菜单配置** (数据库或配置文件)
5. ✅ **创建状态管理** (可选，`web/src/store/`)
6. ✅ **测试页面功能**

**页面开发规范**:

- 使用 TypeScript 编写代码
- 遵循 Vue 3 Composition API 规范
- 使用 Naive UI 组件库
- 统一的错误处理和消息提示
- 响应式设计，适配不同屏幕尺寸
- 代码注释清晰，便于维护


---

## 🧪 完整测试清单

### 数据库层测试

- [ ] PostgreSQL设备类型创建成功
- [ ] 设备字段定义完整且正确
- [ ] TDengine超级表创建成功
- [ ] 字段映射关系正确
- [ ] 设备实例创建成功
- [ ] TDengine子表创建成功

### 数据采集测试

- [ ] 能够成功写入测试数据
- [ ] 数据格式符合表结构
- [ ] 时间戳正确
- [ ] TAG字段正确关联

### API功能测试

- [ ] 设备列表查询正常
- [ ] 设备详情查询正常
- [ ] 实时数据查询正常
- [ ] 历史数据查询正常
- [ ] 异常检测API响应正常
- [ ] 健康评分API响应正常
- [ ] 趋势预测API响应正常

### AI功能测试

- [ ] 统计方法异常检测准确
- [ ] 孤立森林方法异常检测准确
- [ ] 组合方法异常检测准确
- [ ] 异常严重程度划分合理
- [ ] 健康评分计算正确
- [ ] 维度得分合理
- [ ] 风险等级判断准确
- [ ] 趋势预测结果合理

### 前端集成测试

- [ ] 设备列表显示正常
- [ ] 设备详情页面正常
- [ ] 实时数据图表显示正常
- [ ] 异常检测结果展示正常
- [ ] 健康评分卡片显示正常
- [ ] 趋势预测图表显示正常
- [ ] 数据刷新功能正常

---

## 📝 测试报告模板

### 测试环境

- **测试日期**: 2025-11-10
- **测试人员**: [姓名]
- **系统版本**: DeviceMonitorV2 v1.0
- **数据库版本**: PostgreSQL 12+, TDengine 3.0+

### 测试结果

#### 1. 设备类型创建

| 测试项 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|------|
| 设备类型创建 | 成功创建PRESSURE_SENSOR_V1 | ✅ 成功 | 通过 |
| 字段定义 | 创建4个字段 | ✅ 成功 | 通过 |
| TDengine表 | 创建st_pressure_sensor | ✅ 成功 | 通过 |

#### 2. 数据采集

| 测试项 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|------|
| 数据写入 | 成功写入1440条 | ✅ 成功 | 通过 |
| 数据查询 | 能够查询到数据 | ✅ 成功 | 通过 |

#### 3. AI功能

| 测试项 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|------|
| 异常检测 | 检测到2个异常点 | ✅ 成功 | 通过 |
| 健康评分 | 评分75-85分 | ✅ 82分 | 通过 |
| 趋势预测 | 生成24小时预测 | ✅ 成功 | 通过 |

### 问题记录

| 问题ID | 问题描述 | 严重程度 | 状态 | 备注 |
|--------|----------|----------|------|------|
| - | - | - | - | - |

### 测试结论

- **总体评价**: [通过/不通过]
- **主要问题**: [描述]
- **改进建议**: [建议]

---

## 🔧 常见问题排查

### 问题1：TDengine连接失败

**症状**: 无法连接到TDengine数据库

**排查步骤**:
```bash
# 1. 检查TDengine服务状态
systemctl status taosd  # Linux
# 或查看进程
ps aux | grep taosd

# 2. 检查端口是否开放
netstat -an | grep 6041

# 3. 测试连接
taos -h 127.0.0.1 -P 6041 -u root -p taosdata
```

**解决方案**:
- 启动TDengine服务
- 检查防火墙配置
- 验证用户名密码

### 问题2：异常检测无结果

**症状**: API返回成功但没有检测到异常

**排查步骤**:
```python
# 检查数据分布
import numpy as np
data = [5.2, 5.3, 5.1, 5.4, 5.2]
print(f"均值: {np.mean(data)}")
print(f"标准差: {np.std(data)}")
print(f"最大值: {np.max(data)}")
print(f"最小值: {np.min(data)}")
```

**解决方案**:
- 调整threshold参数（降低阈值）
- 确保数据中包含明显异常值
- 尝试不同的检测方法

### 问题3：健康评分为0

**症状**: 计算的健康评分为0或异常低

**排查步骤**:
```sql
-- 检查数据完整性
SELECT 
    COUNT(*) as total,
    COUNT(pressure) as pressure_count,
    COUNT(temperature) as temp_count,
    AVG(pressure) as avg_pressure
FROM tb_ps001
WHERE ts >= NOW - 24h;
```

**解决方案**:
- 确保有足够的历史数据
- 检查数据范围配置
- 验证权重配置

### 问题4：前端无法显示数据

**症状**: 前端页面空白或无数据

**排查步骤**:
```bash
# 1. 检查后端API
curl http://localhost:8001/api/v2/devices

# 2. 检查浏览器控制台
# 打开F12查看Network和Console

# 3. 检查前端代理配置
# 查看 web/vite.config.js
```

**解决方案**:
- 检查CORS配置
- 验证API路径
- 检查认证token


---

## 📚 附录

### 附录A：完整SQL脚本

创建文件 `docs/device_test/setup_pressure_sensor.sql`:

```sql
-- =====================================================
-- 压力传感器设备类型完整配置脚本
-- =====================================================

-- 1. 创建设备类型
INSERT INTO t_device_type (
    type_name, type_code, tdengine_stable_name, description, 
    is_active, device_count, created_at, updated_at
) VALUES (
    '智能压力传感器', 'PRESSURE_SENSOR_V1', 'st_pressure_sensor',
    '用于监测管道压力的智能传感器，支持实时数据采集和异常检测',
    true, 0, NOW(), NOW()
);

-- 2. 创建设备字段
INSERT INTO t_device_field (
    device_type_code, field_name, field_code, field_type, field_category,
    unit, description, is_required, sort_order, is_active,
    is_monitoring_key, is_ai_feature, aggregation_method,
    data_range, alarm_threshold, display_config, created_at, updated_at
) VALUES
    ('PRESSURE_SENSOR_V1', '压力值', 'pressure', 'float', 'data_collection',
     'MPa', '当前压力读数', true, 1, true, true, true, 'avg',
     '{"min": 0, "max": 10}', '{"warning": 8, "critical": 9.5}',
     '{"chart_type": "line", "color": "#1890ff"}', NOW(), NOW()),
    
    ('PRESSURE_SENSOR_V1', '温度', 'temperature', 'float', 'data_collection',
     '°C', '传感器温度', true, 2, true, true, true, 'avg',
     '{"min": -20, "max": 80}', '{"warning": 70, "critical": 75}',
     '{"chart_type": "line", "color": "#ff4d4f"}', NOW(), NOW()),
    
    ('PRESSURE_SENSOR_V1', '振动值', 'vibration', 'float', 'data_collection',
     'mm/s', '设备振动强度', false, 3, true, true, true, 'max',
     '{"min": 0, "max": 50}', '{"warning": 40, "critical": 45}', NOW(), NOW()),
    
    ('PRESSURE_SENSOR_V1', '设备状态', 'status', 'string', 'data_collection',
     NULL, '设备运行状态：online/offline/error/maintenance', true, 4, true,
     true, NOW(), NOW());

-- 3. 创建字段映射（需要先获取field_id）
-- 注意：实际使用时需要替换field_id
INSERT INTO t_device_field_mapping (
    device_type_code, tdengine_database, tdengine_stable, tdengine_column,
    device_field_id, is_tag, is_active, created_at, updated_at
) 
SELECT 
    'PRESSURE_SENSOR_V1', 'devicemonitor', 'st_pressure_sensor', field_code,
    id, false, true, NOW(), NOW()
FROM t_device_field
WHERE device_type_code = 'PRESSURE_SENSOR_V1';

-- 4. 创建测试设备
INSERT INTO t_device_info (
    device_code, device_name, device_model, device_type,
    manufacturer, production_date, install_date, install_location,
    online_address, team_name, is_locked, description,
    created_at, updated_at
) VALUES (
    'PS001', '1号车间压力传感器', 'PS-3000', 'PRESSURE_SENSOR_V1',
    '华为技术有限公司', '2024-01-15', '2024-02-01', '1号车间-A区-管道1',
    '192.168.1.101', '设备维护一组', false, '用于监测1号车间主管道压力',
    NOW(), NOW()
);

-- 5. 创建数据模型
INSERT INTO t_device_data_model (
    model_name, model_code, device_type_code, model_type,
    selected_fields, version, is_active, is_default, description,
    created_at, updated_at
) VALUES
    ('压力传感器实时监控模型', 'PRESSURE_REALTIME_V1', 'PRESSURE_SENSOR_V1', 'realtime',
     '[{"field_code": "pressure", "alias": "压力", "weight": 1.0, "is_required": true},
       {"field_code": "temperature", "alias": "温度", "weight": 0.8, "is_required": true},
       {"field_code": "vibration", "alias": "振动", "weight": 0.6, "is_required": false}]',
     '1.0', true, true, '用于实时监控压力传感器的关键指标', NOW(), NOW()),
    
    ('压力传感器AI异常检测模型', 'PRESSURE_AI_ANOMALY_V1', 'PRESSURE_SENSOR_V1', 'ai_analysis',
     '[{"field_code": "pressure", "alias": "压力", "weight": 1.0, "is_required": true},
       {"field_code": "temperature", "alias": "温度", "weight": 0.7, "is_required": true},
       {"field_code": "vibration", "alias": "振动", "weight": 0.5, "is_required": true}]',
     '1.0', true, false, '基于孤立森林算法的多维异常检测模型', NOW(), NOW());

-- 验证查询
SELECT '=== 设备类型 ===' as info;
SELECT * FROM t_device_type WHERE type_code = 'PRESSURE_SENSOR_V1';

SELECT '=== 设备字段 ===' as info;
SELECT field_name, field_code, is_monitoring_key, is_ai_feature 
FROM t_device_field WHERE device_type_code = 'PRESSURE_SENSOR_V1';

SELECT '=== 设备实例 ===' as info;
SELECT * FROM t_device_info WHERE device_code = 'PS001';

SELECT '=== 数据模型 ===' as info;
SELECT model_name, model_code, model_type 
FROM t_device_data_model WHERE device_type_code = 'PRESSURE_SENSOR_V1';
```

### 附录B：TDengine完整脚本

创建文件 `docs/device_test/setup_tdengine.sql`:

```sql
-- =====================================================
-- TDengine压力传感器配置脚本
-- =====================================================

-- 切换数据库
USE devicemonitor;

-- 创建超级表
CREATE STABLE IF NOT EXISTS st_pressure_sensor (
    ts TIMESTAMP,
    pressure FLOAT,
    temperature FLOAT,
    vibration FLOAT,
    status NCHAR(20),
    error_code NCHAR(50),
    error_message NCHAR(500)
) TAGS (
    device_code NCHAR(50),
    device_name NCHAR(100),
    install_location NCHAR(255)
);

-- 创建子表
CREATE TABLE IF NOT EXISTS tb_ps001 USING st_pressure_sensor 
TAGS ('PS001', '1号车间压力传感器', '1号车间-A区-管道1');

-- 插入测试数据
INSERT INTO tb_ps001 VALUES 
    (NOW - 10m, 5.2, 45.3, 2.1, 'online', NULL, NULL),
    (NOW - 9m, 5.3, 45.5, 2.2, 'online', NULL, NULL),
    (NOW - 8m, 5.1, 45.4, 2.0, 'online', NULL, NULL),
    (NOW - 7m, 5.4, 45.6, 2.3, 'online', NULL, NULL),
    (NOW - 6m, 5.2, 45.5, 2.1, 'online', NULL, NULL),
    (NOW - 5m, 5.5, 45.7, 2.4, 'online', NULL, NULL),
    (NOW - 4m, 8.9, 68.2, 38.5, 'error', 'E001', '压力异常'),
    (NOW - 3m, 9.2, 70.1, 42.3, 'error', 'E001', '压力异常'),
    (NOW - 2m, 5.3, 46.0, 2.2, 'online', NULL, NULL),
    (NOW - 1m, 5.2, 45.8, 2.1, 'online', NULL, NULL),
    (NOW, 5.4, 45.9, 2.3, 'online', NULL, NULL);

-- 验证数据
SELECT * FROM tb_ps001 ORDER BY ts DESC LIMIT 20;

-- 统计查询
SELECT 
    COUNT(*) as total_records,
    AVG(pressure) as avg_pressure,
    MAX(pressure) as max_pressure,
    MIN(pressure) as min_pressure,
    AVG(temperature) as avg_temperature,
    AVG(vibration) as avg_vibration
FROM tb_ps001;

-- 异常数据查询
SELECT * FROM tb_ps001 WHERE status = 'error' ORDER BY ts DESC;
```


### 附录C：Python测试脚本集合

创建文件 `docs/device_test/test_scripts.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力传感器完整测试脚本集合
"""

import requests
import taos
import numpy as np
from datetime import datetime, timedelta
import json

# =====================================================
# 配置部分
# =====================================================

# API配置
API_BASE_URL = "http://localhost:8001/api/v2"
API_USERNAME = "admin"
API_PASSWORD = "admin123"
API_TOKEN = None  # 将在登录后自动填充

# TDengine配置
TDENGINE_CONFIG = {
    "host": "127.0.0.1",
    "port": 6041,
    "user": "root",
    "password": "taosdata",
    "database": "devicemonitor"
}

# 设备配置
DEVICE_CODE = "PS001"
DEVICE_TYPE = "PRESSURE_SENSOR_V1"

# =====================================================
# 工具函数
# =====================================================

def login():
    """登录并获取token"""
    global API_TOKEN
    url = f"{API_BASE_URL}/auth/login"
    response = requests.post(url, json={
        "username": API_USERNAME,
        "password": API_PASSWORD
    })
    
    if response.status_code == 200:
        result = response.json()
        API_TOKEN = result['data']['access_token']
        print(f"✅ 登录成功，Token: {API_TOKEN[:20]}...")
        return True
    else:
        print(f"❌ 登录失败: {response.text}")
        return False

def get_headers():
    """获取请求头"""
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

# =====================================================
# 测试1：设备类型验证
# =====================================================

def test_device_type():
    """测试设备类型是否存在"""
    print("\n" + "="*50)
    print("测试1：设备类型验证")
    print("="*50)
    
    url = f"{API_BASE_URL}/device-types"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code == 200:
        result = response.json()
        device_types = result['data']['items']
        
        found = False
        for dt in device_types:
            if dt['type_code'] == DEVICE_TYPE:
                found = True
                print(f"✅ 找到设备类型: {dt['type_name']}")
                print(f"   类型代码: {dt['type_code']}")
                print(f"   TDengine表: {dt['tdengine_stable_name']}")
                print(f"   激活状态: {dt['is_active']}")
                break
        
        if not found:
            print(f"❌ 未找到设备类型: {DEVICE_TYPE}")
            return False
    else:
        print(f"❌ 查询失败: {response.text}")
        return False
    
    return True

# =====================================================
# 测试2：设备实例验证
# =====================================================

def test_device_instance():
    """测试设备实例是否存在"""
    print("\n" + "="*50)
    print("测试2：设备实例验证")
    print("="*50)
    
    url = f"{API_BASE_URL}/devices"
    params = {"device_code": DEVICE_CODE}
    response = requests.get(url, params=params, headers=get_headers())
    
    if response.status_code == 200:
        result = response.json()
        devices = result['data']['items']
        
        if len(devices) > 0:
            device = devices[0]
            print(f"✅ 找到设备: {device['device_name']}")
            print(f"   设备编号: {device['device_code']}")
            print(f"   设备类型: {device['device_type']}")
            print(f"   安装位置: {device['install_location']}")
            return device['id']
        else:
            print(f"❌ 未找到设备: {DEVICE_CODE}")
            return None
    else:
        print(f"❌ 查询失败: {response.text}")
        return None

# =====================================================
# 测试3：TDengine数据验证
# =====================================================

def test_tdengine_data():
    """测试TDengine数据"""
    print("\n" + "="*50)
    print("测试3：TDengine数据验证")
    print("="*50)
    
    try:
        conn = taos.connect(**TDENGINE_CONFIG)
        cursor = conn.cursor()
        
        # 查询数据
        table_name = f"tb_{DEVICE_CODE.lower()}"
        sql = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(sql)
        count = cursor.fetchone()[0]
        
        print(f"✅ 数据表存在: {table_name}")
        print(f"   数据条数: {count}")
        
        if count > 0:
            # 查询最新数据
            sql = f"SELECT * FROM {table_name} ORDER BY ts DESC LIMIT 5"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            print(f"\n   最新5条数据:")
            for row in results:
                print(f"   - 时间: {row[0]}, 压力: {row[1]}, 温度: {row[2]}, 状态: {row[4]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ TDengine查询失败: {e}")
        return False

# =====================================================
# 测试4：AI异常检测
# =====================================================

def test_anomaly_detection():
    """测试AI异常检测"""
    print("\n" + "="*50)
    print("测试4：AI异常检测")
    print("="*50)
    
    # 获取设备数据
    try:
        conn = taos.connect(**TDENGINE_CONFIG)
        cursor = conn.cursor()
        
        table_name = f"tb_{DEVICE_CODE.lower()}"
        sql = f"SELECT pressure FROM {table_name} ORDER BY ts DESC LIMIT 50"
        cursor.execute(sql)
        results = cursor.fetchall()
        
        pressure_data = [row[0] for row in results if row[0] is not None]
        
        cursor.close()
        conn.close()
        
        if len(pressure_data) < 3:
            print(f"❌ 数据不足，需要至少3条数据")
            return False
        
        print(f"   获取到 {len(pressure_data)} 条压力数据")
        
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        return False
    
    # 调用异常检测API
    url = f"{API_BASE_URL}/ai/anomalies/detect"
    payload = {
        "data": pressure_data,
        "device_code": DEVICE_CODE,
        "method": "combined",
        "threshold": 3.0,
        "save_to_db": True
    }
    
    response = requests.post(url, json=payload, headers=get_headers())
    
    if response.status_code == 200:
        result = response.json()
        data = result['data']
        
        print(f"✅ 异常检测完成")
        print(f"   检测到异常: {data['is_anomaly']}")
        print(f"   异常点数量: {data['anomaly_count']}")
        print(f"   异常率: {data['anomaly_rate']:.2f}%")
        
        if data['anomalies']:
            print(f"\n   异常详情:")
            for anomaly in data['anomalies'][:5]:  # 只显示前5个
                print(f"   - 索引{anomaly['index']}: 值={anomaly['value']}, "
                      f"分数={anomaly['score']:.2f}, 严重程度={anomaly['severity']}")
        
        return True
    else:
        print(f"❌ 异常检测失败: {response.text}")
        return False

# =====================================================
# 测试5：健康评分
# =====================================================

def test_health_score(device_id):
    """测试健康评分"""
    print("\n" + "="*50)
    print("测试5：健康评分")
    print("="*50)
    
    # 创建健康评分
    url = f"{API_BASE_URL}/ai/health-scores/records"
    payload = {
        "score_name": f"{DEVICE_CODE}设备健康评分测试",
        "description": "自动化测试创建的健康评分",
        "target_type": "device",
        "target_id": device_id,
        "scoring_algorithm": "weighted_average",
        "weight_config": {
            "pressure_stability": 0.4,
            "temperature_normal": 0.3,
            "vibration_level": 0.2,
            "error_frequency": 0.1
        },
        "threshold_config": {
            "excellent": 90,
            "good": 75,
            "fair": 60,
            "poor": 40,
            "critical": 0
        }
    }
    
    response = requests.post(url, json=payload, headers=get_headers())
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 健康评分创建成功")
        print(f"   评分ID: {result['data']['id']}")
        return True
    else:
        print(f"❌ 健康评分创建失败: {response.text}")
        return False

# =====================================================
# 主测试流程
# =====================================================

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("压力传感器设备类型与AI检测完整测试")
    print("="*70)
    
    # 登录
    if not login():
        print("\n❌ 测试终止：登录失败")
        return
    
    # 测试1：设备类型
    test1_result = test_device_type()
    
    # 测试2：设备实例
    device_id = test_device_instance()
    test2_result = device_id is not None
    
    # 测试3：TDengine数据
    test3_result = test_tdengine_data()
    
    # 测试4：AI异常检测
    test4_result = test_anomaly_detection()
    
    # 测试5：健康评分
    test5_result = False
    if device_id:
        test5_result = test_health_score(device_id)
    
    # 测试总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    tests = [
        ("设备类型验证", test1_result),
        ("设备实例验证", test2_result),
        ("TDengine数据验证", test3_result),
        ("AI异常检测", test4_result),
        ("健康评分", test5_result)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for name, result in tests:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统功能正常。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查相关配置。")

if __name__ == "__main__":
    run_all_tests()
```

**运行完整测试**:
```bash
python docs/device_test/test_scripts.py
```


### 附录D：API接口清单

#### 设备管理API

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取设备列表 | GET | /api/v2/devices | 支持分页和多条件查询 |
| 获取设备详情 | GET | /api/v2/devices/{id} | 获取单个设备详细信息 |
| 创建设备 | POST | /api/v2/devices | 创建新设备 |
| 更新设备 | PUT | /api/v2/devices/{id} | 更新设备信息 |
| 删除设备 | DELETE | /api/v2/devices/{id} | 删除设备 |
| 获取设备类型列表 | GET | /api/v2/device-types | 获取所有设备类型 |
| 创建设备类型 | POST | /api/v2/device-types | 创建新设备类型 |

#### AI检测API

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 异常检测 | POST | /api/v2/ai/anomalies/detect | 检测数据异常 |
| 批量异常检测 | POST | /api/v2/ai/anomalies/batch-detect | 批量检测多个设备 |
| 获取异常记录 | GET | /api/v2/ai/anomalies/records | 查询历史异常记录 |
| 创建健康评分 | POST | /api/v2/ai/health-scores/records | 创建健康评分任务 |
| 获取健康评分 | GET | /api/v2/ai/health-scores/records | 查询健康评分列表 |
| 创建趋势预测 | POST | /api/v2/ai/predictions | 创建预测任务 |
| 获取预测结果 | GET | /api/v2/ai/predictions/{id} | 获取预测结果 |

#### 数据查询API

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 查询实时数据 | GET | /api/v2/data/realtime | 查询设备实时数据 |
| 查询历史数据 | GET | /api/v2/data/history | 查询设备历史数据 |
| 数据统计 | GET | /api/v2/data/statistics | 数据统计分析 |

### 附录E：数据模型关系图

```
┌─────────────────────────────────────────────────────────────┐
│                     设备类型 (DeviceType)                     │
│  - type_code: PRESSURE_SENSOR_V1                            │
│  - tdengine_stable_name: st_pressure_sensor                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ 1:N
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   设备字段 (DeviceField)                      │
│  - field_code: pressure, temperature, vibration             │
│  - is_monitoring_key: true                                  │
│  - is_ai_feature: true                                      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ 1:N
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              字段映射 (DeviceFieldMapping)                    │
│  - tdengine_column: pressure                                │
│  - tdengine_stable: st_pressure_sensor                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   设备实例 (DeviceInfo)                       │
│  - device_code: PS001                                       │
│  - device_type: PRESSURE_SENSOR_V1                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ 1:N
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              TDengine子表 (tb_ps001)                         │
│  - 继承自: st_pressure_sensor                                │
│  - TAGs: device_code, device_name, install_location         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                数据模型 (DeviceDataModel)                     │
│  - model_code: PRESSURE_AI_ANOMALY_V1                       │
│  - model_type: ai_analysis                                  │
│  - selected_fields: [pressure, temperature, vibration]      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ 使用
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  AI分析结果                                   │
│  - 异常检测记录 (AIAnomalyRecord)                            │
│  - 健康评分 (AIHealthScore)                                  │
│  - 趋势预测 (AIPrediction)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 最佳实践建议

### 1. 设备类型设计

- ✅ 使用有意义的类型代码（如：PRESSURE_SENSOR_V1）
- ✅ 包含版本号，便于后续升级
- ✅ TDengine表名使用统一前缀（如：st_）
- ✅ 详细的描述信息，便于维护

### 2. 字段定义

- ✅ 合理设置is_monitoring_key和is_ai_feature标志
- ✅ 配置合理的数据范围和告警阈值
- ✅ 使用标准单位（国际单位制）
- ✅ 字段排序要符合业务逻辑

### 3. 数据采集

- ✅ 保持数据采集频率稳定
- ✅ 及时处理异常数据
- ✅ 定期清理历史数据
- ✅ 监控数据质量

### 4. AI模型配置

- ✅ 根据实际业务调整算法参数
- ✅ 定期评估模型准确性
- ✅ 保留足够的历史数据用于训练
- ✅ 记录模型版本和变更

### 5. 性能优化

- ✅ 合理使用TDengine的TAG功能
- ✅ 创建必要的索引
- ✅ 控制单次查询的数据量
- ✅ 使用缓存减少数据库压力

---

## 📞 技术支持

### 遇到问题？

1. **查看日志**
   - 后端日志：`app/logs/`
   - TDengine日志：`/var/log/taos/`
   - PostgreSQL日志：根据配置位置

2. **检查配置**
   - 数据库连接配置
   - API端口配置
   - 环境变量配置

3. **联系支持**
   - 提交Issue到项目仓库
   - 查看项目文档
   - 联系开发团队

---

## 📝 更新日志

### v1.0 (2025-11-10)
- ✅ 初始版本发布
- ✅ 完整的设备类型新增流程
- ✅ AI检测功能集成指南
- ✅ 测试脚本和工具

---

## 📄 许可证

本文档遵循项目主许可证（MIT License）

---

**文档结束**

如有疑问或建议，请联系项目维护团队。

