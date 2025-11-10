# API变更日志

本文档记录了系统管理API v2的所有变更历史。

## 版本 2.0.15

**发布时间**: 2025-11-06T12:54:56.878747

**端点数量**: 282

### 新增

- `POST /api/v2/metadata-sync/sync-from-tdengine` - 新增端点: POST /api/v2/metadata-sync/sync-from-tdengine
- `GET /api/v2/metadata-sync/preview-tdengine-fields` - 新增端点: GET /api/v2/metadata-sync/preview-tdengine-fields

### 修改

- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

---

## 版本 2.0.14

**发布时间**: 2025-11-06T10:18:58.851828

**端点数量**: 280

### 修改

- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

### 删除

- `GET /api/v2/ai-monitor/predictions` - 删除端点: GET /api/v2/ai-monitor/predictions
- `GET /api/v2/ai-monitor/predictions/{prediction_id}` - 删除端点: GET /api/v2/ai-monitor/predictions/{prediction_id}
- `POST /api/v2/ai-monitor/predictions` - 删除端点: POST /api/v2/ai-monitor/predictions
- `PUT /api/v2/ai-monitor/predictions/{prediction_id}` - 删除端点: PUT /api/v2/ai-monitor/predictions/{prediction_id}
- `DELETE /api/v2/ai-monitor/predictions/{prediction_id}` - 删除端点: DELETE /api/v2/ai-monitor/predictions/{prediction_id}
- `GET /api/v2/ai-monitor/predictions/{prediction_id}/export` - 删除端点: GET /api/v2/ai-monitor/predictions/{prediction_id}/export
- `POST /api/v2/ai-monitor/predictions/{prediction_id}/share` - 删除端点: POST /api/v2/ai-monitor/predictions/{prediction_id}/share
- `POST /api/v2/ai-monitor/predictions/batch` - 删除端点: POST /api/v2/ai-monitor/predictions/batch
- `GET /api/v2/ai-monitor/predictions/history` - 删除端点: GET /api/v2/ai-monitor/predictions/history
- `POST /api/v2/ai-monitor/predictions/batch-delete` - 删除端点: POST /api/v2/ai-monitor/predictions/batch-delete
- `GET /api/v2/ai-monitor/prediction-analytics/risk-assessment` - 删除端点: GET /api/v2/ai-monitor/prediction-analytics/risk-assessment
- `GET /api/v2/ai-monitor/prediction-analytics/health-trend` - 删除端点: GET /api/v2/ai-monitor/prediction-analytics/health-trend
- `GET /api/v2/ai-monitor/prediction-analytics/prediction-report` - 删除端点: GET /api/v2/ai-monitor/prediction-analytics/prediction-report
- `POST /api/v2/ai/trend-prediction/predict` - 删除端点: POST /api/v2/ai/trend-prediction/predict
- `POST /api/v2/ai/trend-prediction/predict/batch` - 删除端点: POST /api/v2/ai/trend-prediction/predict/batch
- `POST /api/v2/ai/trend-prediction/compare` - 删除端点: POST /api/v2/ai/trend-prediction/compare
- `GET /api/v2/ai/trend-prediction/methods` - 删除端点: GET /api/v2/ai/trend-prediction/methods

---

## 版本 2.0.13

**发布时间**: 2025-11-05T21:15:46.362321

**端点数量**: 297

### 新增

- `GET /api/v2/ai-monitor/prediction-analytics/risk-assessment` - 新增端点: GET /api/v2/ai-monitor/prediction-analytics/risk-assessment
- `GET /api/v2/ai-monitor/prediction-analytics/health-trend` - 新增端点: GET /api/v2/ai-monitor/prediction-analytics/health-trend
- `GET /api/v2/ai-monitor/prediction-analytics/prediction-report` - 新增端点: GET /api/v2/ai-monitor/prediction-analytics/prediction-report

### 修改

- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

### 删除

- `GET /api/v2/ai-monitor/predictions/risk-assessment` - 删除端点: GET /api/v2/ai-monitor/predictions/risk-assessment
- `GET /api/v2/ai-monitor/predictions/health-trend` - 删除端点: GET /api/v2/ai-monitor/predictions/health-trend
- `GET /api/v2/ai-monitor/predictions/prediction-report` - 删除端点: GET /api/v2/ai-monitor/predictions/prediction-report

---

## 版本 2.0.12

**发布时间**: 2025-11-05T21:10:24.640905

**端点数量**: 297

### 新增

- `GET /api/v2/ai-monitor/predictions/risk-assessment` - 新增端点: GET /api/v2/ai-monitor/predictions/risk-assessment
- `GET /api/v2/ai-monitor/predictions/health-trend` - 新增端点: GET /api/v2/ai-monitor/predictions/health-trend
- `GET /api/v2/ai-monitor/predictions/prediction-report` - 新增端点: GET /api/v2/ai-monitor/predictions/prediction-report

### 修改

- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

---

## 版本 2.0.11

**发布时间**: 2025-11-05T16:38:59.102374

**端点数量**: 294

### 新增

- `GET /api/v2/ai-monitor/predictions` - 新增端点: GET /api/v2/ai-monitor/predictions
- `GET /api/v2/ai-monitor/predictions/{prediction_id}` - 新增端点: GET /api/v2/ai-monitor/predictions/{prediction_id}
- `POST /api/v2/ai-monitor/predictions` - 新增端点: POST /api/v2/ai-monitor/predictions
- `PUT /api/v2/ai-monitor/predictions/{prediction_id}` - 新增端点: PUT /api/v2/ai-monitor/predictions/{prediction_id}
- `DELETE /api/v2/ai-monitor/predictions/{prediction_id}` - 新增端点: DELETE /api/v2/ai-monitor/predictions/{prediction_id}
- `GET /api/v2/ai-monitor/predictions/{prediction_id}/export` - 新增端点: GET /api/v2/ai-monitor/predictions/{prediction_id}/export
- `POST /api/v2/ai-monitor/predictions/{prediction_id}/share` - 新增端点: POST /api/v2/ai-monitor/predictions/{prediction_id}/share
- `POST /api/v2/ai-monitor/predictions/batch` - 新增端点: POST /api/v2/ai-monitor/predictions/batch
- `GET /api/v2/ai-monitor/predictions/history` - 新增端点: GET /api/v2/ai-monitor/predictions/history
- `POST /api/v2/ai-monitor/predictions/batch-delete` - 新增端点: POST /api/v2/ai-monitor/predictions/batch-delete
- `POST /api/v2/ai/trend-prediction/predict` - 新增端点: POST /api/v2/ai/trend-prediction/predict
- `POST /api/v2/ai/trend-prediction/predict/batch` - 新增端点: POST /api/v2/ai/trend-prediction/predict/batch
- `POST /api/v2/ai/trend-prediction/compare` - 新增端点: POST /api/v2/ai/trend-prediction/compare
- `GET /api/v2/ai/trend-prediction/methods` - 新增端点: GET /api/v2/ai/trend-prediction/methods

### 修改

- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

---

## 版本 2.0.10

**发布时间**: 2025-11-05T15:47:15.404770

**端点数量**: 280

### 新增

- `GET /api/v2/system/modules/ai/resources` - 新增端点: GET /api/v2/system/modules/ai/resources

### 修改

- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

---

## 版本 2.0.9

**发布时间**: 2025-11-04T11:03:39.281085

**端点数量**: 279

### 新增

- `GET /api/v2/system/health` - 新增端点: GET /api/v2/system/health
- `GET /api/v2/system/modules/ai/config` - 新增端点: GET /api/v2/system/modules/ai/config

### 修改

- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

---

## 版本 2.0.8

**发布时间**: 2025-11-03T18:53:32.143662

**端点数量**: 277

### 新增

- `POST /api/v2/metadata/fields` - 新增端点: POST /api/v2/metadata/fields
- `GET /api/v2/metadata/fields` - 新增端点: GET /api/v2/metadata/fields
- `GET /api/v2/metadata/fields/{field_id}` - 新增端点: GET /api/v2/metadata/fields/{field_id}
- `PUT /api/v2/metadata/fields/{field_id}` - 新增端点: PUT /api/v2/metadata/fields/{field_id}
- `DELETE /api/v2/metadata/fields/{field_id}` - 新增端点: DELETE /api/v2/metadata/fields/{field_id}
- `POST /api/v2/metadata/models` - 新增端点: POST /api/v2/metadata/models
- `GET /api/v2/metadata/models` - 新增端点: GET /api/v2/metadata/models
- `GET /api/v2/metadata/models/{model_id}` - 新增端点: GET /api/v2/metadata/models/{model_id}
- `GET /api/v2/metadata/models/code/{model_code}` - 新增端点: GET /api/v2/metadata/models/code/{model_code}
- `PUT /api/v2/metadata/models/{model_id}` - 新增端点: PUT /api/v2/metadata/models/{model_id}
- `DELETE /api/v2/metadata/models/{model_id}` - 新增端点: DELETE /api/v2/metadata/models/{model_id}
- `POST /api/v2/metadata/models/{model_id}/activate` - 新增端点: POST /api/v2/metadata/models/{model_id}/activate
- `POST /api/v2/metadata/mappings` - 新增端点: POST /api/v2/metadata/mappings
- `GET /api/v2/metadata/mappings` - 新增端点: GET /api/v2/metadata/mappings
- `GET /api/v2/metadata/mappings/{mapping_id}` - 新增端点: GET /api/v2/metadata/mappings/{mapping_id}
- `PUT /api/v2/metadata/mappings/{mapping_id}` - 新增端点: PUT /api/v2/metadata/mappings/{mapping_id}
- `DELETE /api/v2/metadata/mappings/{mapping_id}` - 新增端点: DELETE /api/v2/metadata/mappings/{mapping_id}
- `GET /api/v2/metadata/execution-logs` - 新增端点: GET /api/v2/metadata/execution-logs
- `GET /api/v2/metadata/statistics` - 新增端点: GET /api/v2/metadata/statistics
- `POST /api/v2/dynamic-models/generate` - 新增端点: POST /api/v2/dynamic-models/generate
- `GET /api/v2/dynamic-models/fields-info` - 新增端点: GET /api/v2/dynamic-models/fields-info
- `DELETE /api/v2/dynamic-models/cache` - 新增端点: DELETE /api/v2/dynamic-models/cache
- `GET /api/v2/dynamic-models/cache/stats` - 新增端点: GET /api/v2/dynamic-models/cache/stats
- `POST /api/v2/dynamic-models/validate` - 新增端点: POST /api/v2/dynamic-models/validate
- `POST /api/v2/data/query/realtime` - 新增端点: POST /api/v2/data/query/realtime
- `POST /api/v2/data/query/statistics` - 新增端点: POST /api/v2/data/query/statistics
- `GET /api/v2/data/models/{model_code}/preview` - 新增端点: GET /api/v2/data/models/{model_code}/preview
- `GET /api/v2/data/models/list` - 新增端点: GET /api/v2/data/models/list

### 修改

- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

---

## 版本 2.0.7

**发布时间**: 2025-11-02T15:35:50.567761

**端点数量**: 249

### 修改

- `GET /api/v2/alarms` - 修改端点: GET /api/v2/alarms
- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

---

## 版本 2.0.6

**发布时间**: 2025-10-30T10:24:23.777225

**端点数量**: 249

### 新增

- `GET /api/v2/mock-data` - 新增端点: GET /api/v2/mock-data
- `GET /api/v2/mock-data/{mock_id}` - 新增端点: GET /api/v2/mock-data/{mock_id}
- `POST /api/v2/mock-data` - 新增端点: POST /api/v2/mock-data
- `PUT /api/v2/mock-data/{mock_id}` - 新增端点: PUT /api/v2/mock-data/{mock_id}
- `DELETE /api/v2/mock-data/{mock_id}` - 新增端点: DELETE /api/v2/mock-data/{mock_id}
- `POST /api/v2/mock-data/batch-delete` - 新增端点: POST /api/v2/mock-data/batch-delete
- `POST /api/v2/mock-data/{mock_id}/toggle` - 新增端点: POST /api/v2/mock-data/{mock_id}/toggle
- `GET /api/v2/mock-data/active/list` - 新增端点: GET /api/v2/mock-data/active/list
- `POST /api/v2/mock-data/{mock_id}/hit` - 新增端点: POST /api/v2/mock-data/{mock_id}/hit

### 修改

- `GET /api/v2/docs/versions` - 修改端点: GET /api/v2/docs/versions
- `GET /api/v2/docs/changelog` - 修改端点: GET /api/v2/docs/changelog

---

