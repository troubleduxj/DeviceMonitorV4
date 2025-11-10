# AI API前缀统一方案 - 执行计划

> **制定时间**: 2025-11-06 09:52  
> **用户需求**: 统一前缀，彻底解决问题  
> **执行时间**: 1-2小时  
> **目标**: 所有AI API统一使用 `/api/v2/ai/` 前缀  

---

## 🎯 统一方案

### 统一前缀规则

**所有AI相关API统一使用**：`/api/v2/ai/`

**通过模块名区分功能**：

```
/api/v2/ai/
├── predictions/              # 趋势预测（合并3个文件）
│   ├── /tasks/              # 任务管理（原predictions.py）
│   ├── /execute/            # 实时预测（原trend_prediction.py）
│   └── /analytics/          # 数据分析（原prediction_analytics.py）
│
├── health-scores/           # 健康评分（合并2个文件）
│   ├── /calculate/          # 评分计算（原health_scoring.py）
│   └── /records/            # 记录管理（原health_scores.py）
│
├── anomalies/              # 异常检测（保持）
├── features/               # 特征提取（保持）
├── analysis/               # 智能分析（保持）
├── annotations/            # 数据标注（保持）
└── models/                 # 模型管理（保持）
```

---

## 📋 执行清单

### 阶段1：后端API修改（30分钟）

#### 1. predictions.py
```python
# 改前
router = APIRouter(prefix="/predictions", tags=["AI预测-任务管理"])
# 注册: v2_router.include_router(predictions_router, prefix="/ai-monitor")
# 结果: /api/v2/ai-monitor/predictions/...

# 改后
router = APIRouter(prefix="/predictions/tasks", tags=["AI预测-任务管理"])
# 注册: v2_router.include_router(predictions_router, prefix="/ai")
# 结果: /api/v2/ai/predictions/tasks/...
```

#### 2. trend_prediction.py
```python
# 改前
router = APIRouter(prefix="/ai/trend-prediction", tags=["AI预测-趋势计算"])
# 结果: /api/v2/ai/trend-prediction/...

# 改后
router = APIRouter(prefix="/predictions/execute", tags=["AI预测-实时计算"])
# 注册: v2_router.include_router(trend_prediction_router, prefix="/ai")
# 结果: /api/v2/ai/predictions/execute/...
```

#### 3. prediction_analytics.py
```python
# 改前
router = APIRouter(prefix="/prediction-analytics", tags=["AI预测-数据分析"])
# 注册: v2_router.include_router(prediction_analytics_router, prefix="/ai-monitor")
# 结果: /api/v2/ai-monitor/prediction-analytics/...

# 改后
router = APIRouter(prefix="/predictions/analytics", tags=["AI预测-数据分析"])
# 注册: v2_router.include_router(prediction_analytics_router, prefix="/ai")
# 结果: /api/v2/ai/predictions/analytics/...
```

---

### 阶段2：路由注册修改（10分钟）

#### app/api/v2/__init__.py

```python
# 统一注册到 /ai 前缀下
if ai_settings.ai_module_enabled and ai_settings.ai_trend_prediction_enabled:
    try:
        from .ai.predictions import router as predictions_router
        from .ai.prediction_analytics import router as prediction_analytics_router
        from .ai.trend_prediction import router as trend_prediction_router
        
        # 全部使用 /ai 前缀
        v2_router.include_router(predictions_router, prefix="/ai")
        v2_router.include_router(prediction_analytics_router, prefix="/ai")
        v2_router.include_router(trend_prediction_router, prefix="/ai")
        
        logging.info("✅ AI预测模块路由已注册（统一前缀: /ai）")
    except ImportError as e:
        logging.warning(f"⚠️ 无法加载AI预测模块路由: {e}")
```

---

### 阶段3：前端调用修改（20分钟）

#### web/src/api/v2/ai-module.js

```javascript
// 修改所有调用路径
export const predictionManagementApi = {
  // 改前: '/ai-monitor/predictions/batch'
  // 改后: '/ai/predictions/tasks/batch'
  createBatch: (data) => requestV2.post('/ai/predictions/tasks/batch', data),
  
  // 改前: '/ai-monitor/predictions/history'  
  // 改后: '/ai/predictions/tasks/history'
  getHistory: (params) => requestV2.get('/ai/predictions/tasks/history', { params }),
  
  // 其他接口类似修改...
}
```

#### web/src/views/ai-monitor/trend-prediction/index.vue

```javascript
// 修改fetch调用
const [batchResponse, riskResponse, healthTrendResponse, reportResponse] = 
  await Promise.allSettled([
    predictionManagementApi.createBatch(...),
    // 改前: fetch('/api/v2/ai-monitor/prediction-analytics/risk-assessment')
    // 改后: fetch('/api/v2/ai/predictions/analytics/risk-assessment')
    fetch('/api/v2/ai/predictions/analytics/risk-assessment').then(r => r.json()),
    fetch('/api/v2/ai/predictions/analytics/health-trend').then(r => r.json()),
    fetch('/api/v2/ai/predictions/analytics/report').then(r => r.json())
  ])
```

---

### 阶段4：Mock规则更新（10分钟）

#### 更新Mock规则URL

```python
# scripts/update_mock_urls.py - 批量更新Mock规则路径

UPDATE t_sys_mock_data 
SET url_pattern = REPLACE(url_pattern, '/ai-monitor/predictions/', '/ai/predictions/tasks/')
WHERE url_pattern LIKE '/ai-monitor/predictions/%';

UPDATE t_sys_mock_data
SET url_pattern = REPLACE(url_pattern, '/ai-monitor/prediction-analytics/', '/ai/predictions/analytics/')
WHERE url_pattern LIKE '/ai-monitor/prediction-analytics/%';
```

---

## 🚀 开始执行

让我立即开始！

