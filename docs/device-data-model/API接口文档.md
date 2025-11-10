# 元数据管理 API 接口文档

> **API 版本**: v2  
> **基础路径**: `/api/v2/metadata`  
> **认证方式**: JWT Bearer Token

---

## 📋 接口概览

| 模块 | 接口数量 | 描述 |
|------|---------|------|
| **设备字段定义** | 5个 | 管理设备字段的CRUD操作 |
| **数据模型** | 7个 | 管理数据模型的CRUD及激活操作 |
| **字段映射** | 5个 | 管理PostgreSQL与TDengine的字段映射 |
| **执行日志** | 1个 | 查询模型执行日志 |
| **统计信息** | 1个 | 获取模型统计数据 |
| **合计** | **19个** | |

---

## 🔐 认证说明

所有接口都需要在请求头中携带JWT Token：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 1. 设备字段定义 API

### 1.1 创建设备字段

**接口**: `POST /api/v2/metadata/fields`

**请求体**:
```json
{
  "device_type_code": "welding",
  "field_name": "焊接电流",
  "field_code": "avg_current",
  "field_type": "float",
  "field_category": "data_collection",
  "unit": "A",
  "description": "平均焊接电流值",
  "is_required": true,
  "sort_order": 1,
  "is_active": true,
  "is_monitoring_key": true,
  "is_ai_feature": true,
  "aggregation_method": "avg",
  "data_range": {
    "min": 0,
    "max": 500
  },
  "alarm_threshold": {
    "warning": 400,
    "critical": 450
  },
  "display_config": {
    "chart_type": "line",
    "color": "#1890ff",
    "unit_position": "suffix",
    "decimals": 1
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "创建设备字段成功",
  "data": {
    "id": 1,
    "field_name": "焊接电流",
    "field_code": "avg_current",
    ...
  },
  "request_id": "req_xxx",
  "timestamp": "2025-11-03T10:00:00Z"
}
```

### 1.2 获取设备字段列表

**接口**: `GET /api/v2/metadata/fields`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_type_code` | string | 否 | 设备类型代码 |
| `field_category` | string | 否 | 字段分类 |
| `is_monitoring_key` | boolean | 否 | 是否为监控关键字段 |
| `is_ai_feature` | boolean | 否 | 是否为AI特征 |
| `is_active` | boolean | 否 | 是否激活 |
| `search` | string | 否 | 搜索关键词 |
| `page` | integer | 否 | 页码（默认1） |
| `page_size` | integer | 否 | 每页数量（默认10，最大100） |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取设备字段列表成功",
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total": 50,
    "total_pages": 5
  },
  "request_id": "req_xxx",
  "timestamp": "2025-11-03T10:00:00Z"
}
```

### 1.3 获取设备字段详情

**接口**: `GET /api/v2/metadata/fields/{field_id}`

### 1.4 更新设备字段

**接口**: `PUT /api/v2/metadata/fields/{field_id}`

**请求体**: 同创建接口，所有字段可选

### 1.5 删除设备字段

**接口**: `DELETE /api/v2/metadata/fields/{field_id}`

**说明**: 软删除，将`is_active`设置为`false`

---

## 2. 数据模型 API

### 2.1 创建数据模型

**接口**: `POST /api/v2/metadata/models`

**请求体示例（实时监控模型）**:
```json
{
  "model_name": "焊接设备实时监控模型",
  "model_code": "welding_realtime_v1",
  "device_type_code": "welding",
  "model_type": "realtime",
  "selected_fields": [
    {
      "field_code": "avg_current",
      "alias": "平均电流",
      "weight": 1.5,
      "is_required": true,
      "transform": null
    },
    {
      "field_code": "avg_voltage",
      "alias": "平均电压",
      "weight": 1.5,
      "is_required": true,
      "transform": null
    }
  ],
  "version": "1.0",
  "is_active": true,
  "is_default": true,
  "description": "用于实时监控焊接设备关键参数"
}
```

**请求体示例（统计分析模型）**:
```json
{
  "model_name": "焊接设备每日统计模型",
  "model_code": "welding_statistics_daily_v1",
  "device_type_code": "welding",
  "model_type": "statistics",
  "selected_fields": [...],
  "aggregation_config": {
    "time_window": "1d",
    "interval": "1h",
    "methods": ["avg", "max", "min", "sum"],
    "group_by": ["device_code", "team_name"],
    "custom_expressions": {
      "total_power": "AVG(avg_current * avg_voltage)"
    }
  },
  "version": "1.0",
  "is_active": true,
  "description": "用于每日焊接设备统计分析"
}
```

**请求体示例（AI分析模型）**:
```json
{
  "model_name": "焊接设备异常检测AI模型",
  "model_code": "welding_ai_anomaly_v1",
  "device_type_code": "welding",
  "model_type": "ai_analysis",
  "selected_fields": [...],
  "ai_config": {
    "algorithm": "isolation_forest",
    "purpose": "anomaly_detection",
    "features": ["avg_current", "avg_voltage", "spec_match_rate"],
    "normalization": "min-max",
    "window_size": 100,
    "missing_value_strategy": "interpolate",
    "outlier_threshold": 3.0,
    "training_params": {
      "contamination": 0.05,
      "n_estimators": 100
    }
  },
  "version": "1.0",
  "is_active": true,
  "description": "用于焊接设备异常检测"
}
```

### 2.2 获取数据模型列表

**接口**: `GET /api/v2/metadata/models`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_type_code` | string | 否 | 设备类型代码 |
| `model_type` | string | 否 | 模型类型：realtime/statistics/ai_analysis |
| `is_active` | boolean | 否 | 是否激活 |
| `search` | string | 否 | 搜索关键词 |
| `page` | integer | 否 | 页码 |
| `page_size` | integer | 否 | 每页数量 |

### 2.3 获取数据模型详情

**接口**: `GET /api/v2/metadata/models/{model_id}`

### 2.4 根据编码获取数据模型

**接口**: `GET /api/v2/metadata/models/code/{model_code}`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | string | 否 | 模型版本（不传则返回激活版本） |

### 2.5 更新数据模型

**接口**: `PUT /api/v2/metadata/models/{model_id}`

### 2.6 删除数据模型

**接口**: `DELETE /api/v2/metadata/models/{model_id}`

### 2.7 激活数据模型

**接口**: `POST /api/v2/metadata/models/{model_id}/activate`

**说明**: 激活后，同设备类型、同模型类型的其他模型将自动停用

---

## 3. 字段映射 API

### 3.1 创建字段映射

**接口**: `POST /api/v2/metadata/mappings`

**请求体**:
```json
{
  "device_type_code": "welding",
  "tdengine_database": "hlzg_db",
  "tdengine_stable": "welding_record_his",
  "tdengine_column": "avg_current",
  "device_field_id": 1,
  "transform_rule": {
    "type": "composite",
    "rules": [
      {
        "type": "range_limit",
        "min": 0,
        "max": 500
      },
      {
        "type": "round",
        "decimals": 1
      }
    ]
  },
  "is_tag": false,
  "is_active": true
}
```

### 3.2 获取字段映射列表

**接口**: `GET /api/v2/metadata/mappings`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_type_code` | string | 否 | 设备类型代码 |
| `tdengine_stable` | string | 否 | TDengine超级表名 |
| `is_tag` | boolean | 否 | 是否为TAG列 |
| `is_active` | boolean | 否 | 是否激活 |
| `page` | integer | 否 | 页码 |
| `page_size` | integer | 否 | 每页数量 |

### 3.3 获取字段映射详情

**接口**: `GET /api/v2/metadata/mappings/{mapping_id}`

### 3.4 更新字段映射

**接口**: `PUT /api/v2/metadata/mappings/{mapping_id}`

### 3.5 删除字段映射

**接口**: `DELETE /api/v2/metadata/mappings/{mapping_id}`

---

## 4. 执行日志 API

### 4.1 获取执行日志列表

**接口**: `GET /api/v2/metadata/execution-logs`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model_id` | integer | 否 | 模型ID |
| `execution_type` | string | 否 | 执行类型：query/feature_extract/training/validation |
| `status` | string | 否 | 执行状态：success/failed/timeout/cancelled |
| `page` | integer | 否 | 页码 |
| `page_size` | integer | 否 | 每页数量 |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取执行日志列表成功",
  "data": [
    {
      "id": 1,
      "model_id": 1,
      "execution_type": "query",
      "status": "success",
      "execution_time_ms": 235,
      "data_volume": 1523,
      "executed_at": "2025-11-03T10:00:00Z",
      ...
    }
  ],
  "pagination": {...}
}
```

---

## 5. 统计信息 API

### 5.1 获取模型统计信息

**接口**: `GET /api/v2/metadata/statistics`

**响应示例**:
```json
{
  "code": 200,
  "message": "获取统计信息成功",
  "data": {
    "total_models": 10,
    "active_models": 8,
    "realtime_models": 3,
    "statistics_models": 4,
    "ai_models": 3,
    "total_executions": 12345,
    "success_rate": 98.5,
    "avg_execution_time_ms": 245.67
  }
}
```

---

## 🚨 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token无效或过期） |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

**错误响应示例**:
```json
{
  "code": 404,
  "message": "数据模型不存在",
  "error_type": "NotFoundError",
  "request_id": "req_xxx",
  "timestamp": "2025-11-03T10:00:00Z"
}
```

---

## 📝 使用示例

### Python示例

```python
import requests

# 1. 获取Token（登录）
login_response = requests.post("http://localhost:8000/api/v2/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = login_response.json()["data"]["token"]

# 2. 创建数据模型
headers = {"Authorization": f"Bearer {token}"}
model_data = {
    "model_name": "测试模型",
    "model_code": "test_model_v1",
    "device_type_code": "welding",
    "model_type": "realtime",
    "selected_fields": [
        {"field_code": "avg_current", "alias": "电流", "weight": 1.0, "is_required": True}
    ],
    "version": "1.0"
}
response = requests.post(
    "http://localhost:8000/api/v2/metadata/models",
    json=model_data,
    headers=headers
)
print(response.json())

# 3. 查询数据模型列表
response = requests.get(
    "http://localhost:8000/api/v2/metadata/models",
    params={"device_type_code": "welding", "page": 1, "page_size": 10},
    headers=headers
)
print(response.json())
```

### JavaScript示例

```javascript
// 1. 获取Token
const loginResponse = await fetch('http://localhost:8000/api/v2/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin123'})
});
const {data: {token}} = await loginResponse.json();

// 2. 创建数据模型
const modelResponse = await fetch('http://localhost:8000/api/v2/metadata/models', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    model_name: '测试模型',
    model_code: 'test_model_v1',
    device_type_code: 'welding',
    model_type: 'realtime',
    selected_fields: [
      {field_code: 'avg_current', alias: '电流', weight: 1.0, is_required: true}
    ],
    version: '1.0'
  })
});
const modelData = await modelResponse.json();
console.log(modelData);
```

---

## 🔍 API测试

### 使用 Swagger UI

访问: `http://localhost:8000/docs`

在Swagger UI中可以：
- 查看所有API接口
- 在线测试API
- 查看请求/响应示例

### 使用 Postman

导入 Postman Collection:
1. 打开Postman
2. Import → Link → `http://localhost:8000/openapi.json`
3. 设置环境变量 `base_url` 和 `token`
4. 开始测试

---

## 📞 技术支持

如有问题，请联系：
- **技术负责人**: [待填写]
- **API文档**: `http://localhost:8000/docs`
- **项目文档**: `docs/device-data-model/`

