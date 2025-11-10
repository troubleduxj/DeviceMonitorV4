# Phase 4: AI集成与优化 - 实施指南

> **实施阶段**: Phase 4 (第10-12周)  
> **预计时间**: 2-3周  
> **当前状态**: ⏸️ 待开始  
> **前置条件**: ✅ Phase 1-3 已完成

---

## 📋 阶段概览

### 核心目标
实现AI特征提取服务，为机器学习模型提供标准化的特征数据，并对整个系统进行性能优化。

### 主要交付物
1. ✨ **AI特征提取服务** - 从时序数据提取标准化特征
2. 📊 **训练数据集生成** - 为模型训练准备数据
3. ⚡ **系统性能优化** - SQL、缓存、监控全面优化
4. 📈 **监控告警配置** - Prometheus + Grafana仪表盘

---

## 🎯 Week 10-11: AI特征提取服务开发

### 目标
开发完整的AI特征提取服务，支持多种特征工程方法

---

### Day 1-3: AIFeatureService 核心开发

#### 任务 4.1: 创建 AIFeatureService 类

**文件**: `app/services/ai_feature_service.py`  
**预计代码量**: 600-800行

**核心方法**:

```python
class AIFeatureService:
    """AI特征提取服务"""
    
    async def extract_features(
        self,
        model_code: str,
        device_code: str,
        start_time: datetime,
        end_time: datetime,
        **kwargs
    ) -> Dict[str, Any]:
        """
        提取特征矩阵
        
        参数:
            model_code: 数据模型代码
            device_code: 设备编码
            start_time: 开始时间
            end_time: 结束时间
            **kwargs: 其他参数（如window_size, normalize_method等）
        
        返回:
            {
                "features": [...],  # 特征矩阵
                "feature_names": [...],  # 特征名称
                "timestamps": [...],  # 时间戳
                "metadata": {...}  # 元数据
            }
        """
        pass
    
    def _handle_missing_values(
        self,
        data: pd.DataFrame,
        method: str = 'interpolate'
    ) -> pd.DataFrame:
        """
        处理缺失值
        
        方法:
            - 'drop': 删除包含缺失值的行
            - 'forward_fill': 前向填充
            - 'backward_fill': 后向填充
            - 'interpolate': 线性插值
            - 'mean': 均值填充
            - 'median': 中位数填充
        """
        pass
    
    def _handle_outliers(
        self,
        data: pd.DataFrame,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        处理异常值
        
        方法:
            - 'iqr': IQR方法（四分位距）
            - 'z_score': Z-Score方法
            - 'clip': 截断法
        """
        pass
    
    def _apply_sliding_window(
        self,
        data: pd.DataFrame,
        window_size: int,
        overlap: float = 0.5
    ) -> List[pd.DataFrame]:
        """
        应用滑动窗口
        
        参数:
            window_size: 窗口大小（数据点数量）
            overlap: 重叠比例（0-1之间）
        
        返回:
            窗口化的数据片段列表
        """
        pass
    
    def _min_max_normalize(
        self,
        data: pd.DataFrame,
        feature_range: Tuple[float, float] = (0, 1)
    ) -> pd.DataFrame:
        """
        Min-Max归一化
        
        公式: (x - min) / (max - min) * (max' - min') + min'
        """
        pass
    
    def _z_score_normalize(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Z-Score标准化
        
        公式: (x - mean) / std
        """
        pass
    
    async def generate_training_dataset(
        self,
        model_code: str,
        device_codes: List[str],
        start_time: datetime,
        end_time: datetime,
        label_column: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成训练数据集
        
        返回:
            {
                "X_train": [...],  # 训练特征
                "y_train": [...],  # 训练标签
                "X_val": [...],    # 验证特征
                "y_val": [...],    # 验证标签
                "feature_info": {...}  # 特征信息
            }
        """
        pass
```

**技术栈**:
- NumPy - 数值计算
- Pandas - 数据处理
- Scikit-learn - 特征工程
- TDengine - 时序数据查询

**依赖关系**:
```python
# requirements.txt 新增
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
```

**验收标准**:
- [x] 支持6种缺失值处理方法
- [x] 支持3种异常值处理方法
- [x] 支持滑动窗口（可配置窗口大小和重叠）
- [x] 支持2种归一化方法
- [x] 支持训练/验证集划分

---

### Day 4-5: AI特征API开发

#### 任务 4.2: 创建特征提取API

**文件**: `app/api/v2/ai/features.py`  
**预计代码量**: 350-400行

**API清单** (3个接口):

##### 1. POST /api/v2/ai/features/extract - 提取特征

**请求参数**:
```json
{
  "model_code": "welding_ai_model",
  "device_code": "WLD001",
  "start_time": "2025-11-01T00:00:00",
  "end_time": "2025-11-02T00:00:00",
  "window_size": 100,
  "overlap": 0.5,
  "normalize_method": "z_score",
  "missing_value_method": "interpolate",
  "outlier_method": "iqr"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "features": [[...], [...], ...],
    "feature_names": ["current_mean", "voltage_std", ...],
    "timestamps": ["2025-11-01T00:00:00", ...],
    "metadata": {
      "window_count": 48,
      "window_size": 100,
      "overlap": 0.5,
      "normalize_method": "z_score"
    }
  },
  "execution_time": 1250
}
```

---

##### 2. POST /api/v2/ai/features/dataset - 创建训练数据集

**请求参数**:
```json
{
  "model_code": "welding_ai_model",
  "device_codes": ["WLD001", "WLD002", "WLD003"],
  "start_time": "2025-10-01T00:00:00",
  "end_time": "2025-11-01T00:00:00",
  "label_column": "quality_label",
  "val_split": 0.2,
  "random_state": 42,
  "window_size": 100,
  "overlap": 0.5,
  "normalize_method": "min_max"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "dataset_id": "ds_20251103_001",
    "train_samples": 3840,
    "val_samples": 960,
    "feature_count": 25,
    "class_distribution": {
      "0": 2800,
      "1": 2000
    },
    "download_url": "/api/v2/ai/datasets/ds_20251103_001/download"
  }
}
```

---

##### 3. GET /api/v2/ai/features/stats - 特征统计

**请求参数**:
```
GET /api/v2/ai/features/stats?model_code=welding_ai_model&start_time=...&end_time=...
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "feature_statistics": [
      {
        "feature_name": "current_mean",
        "min": 120.5,
        "max": 180.3,
        "mean": 150.2,
        "std": 12.5,
        "missing_ratio": 0.02
      },
      ...
    ],
    "correlation_matrix": [[...], [...], ...],
    "sample_count": 10000
  }
}
```

---

#### 任务 4.3: API注册与测试

**修改文件**: `app/api/v2/__init__.py`

```python
# 添加 AI特征路由
from app.api.v2.ai.features import router as ai_features_router

v2_router.include_router(
    ai_features_router,
    prefix="/ai/features",
    tags=["AI特征提取 v2"]
)
```

**测试清单**:
- [ ] 单设备特征提取测试
- [ ] 多设备数据集生成测试
- [ ] 特征统计查询测试
- [ ] 错误处理测试（无效参数、数据不足等）
- [ ] 性能测试（> 1000条/秒）

**验收标准**:
- [ ] 所有API接口正常工作
- [ ] 响应格式符合API V2规范
- [ ] 错误处理完善
- [ ] Swagger文档完整
- [ ] 性能达标（特征提取 > 1000条/秒）

---

## ⚡ Week 12: 系统优化

### 目标
全面优化系统性能，建立监控告警体系

---

### Day 1-2: 性能优化

#### 任务 12.1: SQL查询优化

**优化项**:

1. **索引优化**
```sql
-- 分析慢查询
SELECT * FROM pg_stat_statements 
ORDER BY total_exec_time DESC 
LIMIT 10;

-- 添加复合索引
CREATE INDEX idx_device_field_type_code 
ON t_device_field (device_type_id, field_code);

CREATE INDEX idx_data_model_type_status 
ON t_device_data_model (model_type, is_active);

-- 添加部分索引
CREATE INDEX idx_active_models 
ON t_device_data_model (model_code) 
WHERE is_active = true;
```

2. **查询重写**
```python
# Before: N+1查询
models = await DeviceDataModel.all()
for model in models:
    mappings = await model.field_mappings.all()  # N次查询

# After: 预加载
models = await DeviceDataModel.all().prefetch_related('field_mappings')
for model in models:
    mappings = model.field_mappings  # 0次查询
```

3. **分页优化**
```python
# Before: COUNT(*)很慢
total = await DeviceDataModel.all().count()
models = await DeviceDataModel.all().offset(skip).limit(limit)

# After: 使用approximate count
total = await get_approximate_count('t_device_data_model')
models = await DeviceDataModel.all().offset(skip).limit(limit)
```

---

#### 任务 12.2: 缓存优化

**优化策略**:

1. **查询结果缓存**
```python
from functools import lru_cache
from app.core.cache import redis_client

# 模型配置缓存（24小时）
@lru_cache(maxsize=100)
async def get_cached_model_config(model_code: str):
    cache_key = f"model:config:{model_code}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    config = await get_model_config(model_code)
    await redis_client.set(cache_key, json.dumps(config), ex=86400)
    return config

# 字段映射缓存（6小时）
async def get_cached_field_mappings(device_type_id: int):
    cache_key = f"mappings:{device_type_id}"
    # ... 类似逻辑
```

2. **缓存预热**
```python
# app/core/init_app.py
async def warm_up_cache():
    """应用启动时预热缓存"""
    logger.info("开始缓存预热...")
    
    # 预热活跃模型配置
    active_models = await DeviceDataModel.filter(is_active=True).all()
    for model in active_models:
        await get_cached_model_config(model.model_code)
    
    # 预热字段映射
    device_types = await DeviceType.all()
    for dt in device_types:
        await get_cached_field_mappings(dt.id)
    
    logger.info(f"缓存预热完成，共预热 {len(active_models)} 个模型")
```

3. **缓存失效策略**
```python
# 模型更新时清除缓存
async def update_model(model_id: int, data: dict):
    model = await DeviceDataModel.get(id=model_id)
    
    # 更新模型
    await model.update_from_dict(data)
    await model.save()
    
    # 清除相关缓存
    cache_key = f"model:config:{model.model_code}"
    await redis_client.delete(cache_key)
    get_cached_model_config.cache_clear()  # 清除LRU缓存
    
    return model
```

**性能目标**:
- [ ] 缓存命中率 > 95%
- [ ] 缓存响应时间 < 10ms
- [ ] 查询性能提升 > 50%

---

### Day 3-4: 监控告警配置

#### 任务 12.3: Prometheus监控

**1. Prometheus配置**

**文件**: `prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'device-monitor-api'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/api/v2/metrics'
```

**2. FastAPI Metrics中间件**

**文件**: `app/core/middlewares.py`

```python
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# 定义指标
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_queries = Gauge(
    'active_queries',
    'Number of active database queries'
)

# 添加Metrics端点
@router.get("/metrics")
async def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

**3. 自定义业务指标**

```python
# app/services/metrics.py
from prometheus_client import Gauge, Counter

# 模型相关指标
model_query_count = Counter(
    'model_query_total',
    'Total model queries',
    ['model_code', 'model_type']
)

model_query_duration = Histogram(
    'model_query_duration_seconds',
    'Model query duration',
    ['model_code']
)

feature_extraction_count = Counter(
    'feature_extraction_total',
    'Total feature extractions',
    ['model_code']
)

# 在业务代码中使用
async def query_realtime_data(model_code: str, ...):
    start_time = time.time()
    
    try:
        result = await _do_query(...)
        model_query_count.labels(
            model_code=model_code,
            model_type='realtime'
        ).inc()
        
        return result
    finally:
        duration = time.time() - start_time
        model_query_duration.labels(model_code=model_code).observe(duration)
```

---

#### 任务 12.4: Grafana仪表盘

**Grafana配置**:

1. **API性能仪表盘**
   - HTTP请求量（QPS）
   - 响应时间（P50/P90/P99）
   - 错误率
   - 活跃连接数

2. **数据库性能仪表盘**
   - 查询TPS
   - 慢查询数量
   - 连接池使用率
   - 缓存命中率

3. **业务指标仪表盘**
   - 模型查询量（按模型类型）
   - 特征提取量
   - 数据处理耗时
   - 活跃设备数

**Grafana Dashboard JSON**:

```json
{
  "dashboard": {
    "title": "Device Monitor - 数据模型性能",
    "panels": [
      {
        "title": "API QPS",
        "targets": [
          {
            "expr": "rate(http_requests_total[1m])"
          }
        ]
      },
      {
        "title": "模型查询量 Top 10",
        "targets": [
          {
            "expr": "topk(10, sum by (model_code) (rate(model_query_total[5m])))"
          }
        ]
      }
    ]
  }
}
```

**告警规则**:

```yaml
groups:
  - name: device_monitor_alerts
    rules:
      - alert: HighAPILatency
        expr: http_request_duration_seconds{quantile="0.99"} > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API响应时间过长"
          description: "P99延迟超过2秒"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "API错误率过高"
          description: "5xx错误率超过5%"
      
      - alert: LowCacheHitRate
        expr: cache_hit_rate < 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "缓存命中率过低"
          description: "缓存命中率低于90%"
```

**验收标准**:
- [ ] Prometheus正确采集指标
- [ ] Grafana仪表盘正常显示
- [ ] 告警规则配置完成
- [ ] 告警通知正常（邮件/钉钉/企业微信）

---

### Day 5: 文档与测试

#### 任务 12.5: 性能测试

**测试工具**: Locust

**测试脚本**: `tests/performance/locustfile.py`

```python
from locust import HttpUser, task, between

class DataModelUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # 登录获取token
        response = self.client.post("/api/v2/auth/login", json={
            "username": "test_user",
            "password": "test_pass"
        })
        self.token = response.json()["data"]["access_token"]
    
    @task(3)
    def query_models(self):
        self.client.get(
            "/api/v2/metadata/models",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def query_data(self):
        self.client.post(
            "/api/v2/data/query/realtime",
            json={
                "model_code": "welding_realtime",
                "filters": {},
                "page": 1,
                "page_size": 50
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def extract_features(self):
        self.client.post(
            "/api/v2/ai/features/extract",
            json={
                "model_code": "welding_ai_model",
                "device_code": "WLD001",
                "start_time": "2025-11-01T00:00:00",
                "end_time": "2025-11-01T01:00:00"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

**执行测试**:
```bash
# 100并发，持续5分钟
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8001 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m
```

**性能指标**:
| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| QPS | > 100 | ? | ⏸️ 待测试 |
| P99延迟 | < 2s | ? | ⏸️ 待测试 |
| 错误率 | < 1% | ? | ⏸️ 待测试 |
| 缓存命中率 | > 95% | ? | ⏸️ 待测试 |

---

#### 任务 12.6: 文档更新

**需更新的文档**:

1. **API接口文档**
   - 添加3个AI特征API文档
   - 更新性能指标说明

2. **部署文档**
   - 添加Prometheus部署步骤
   - 添加Grafana配置说明

3. **性能调优指南**
   - SQL优化建议
   - 缓存配置建议
   - 监控告警配置

---

## 📊 Phase 4 交付成果

### 代码交付
- ✨ `AIFeatureService` 类（600-800行）
- ✨ 3个AI特征API接口（350-400行）
- ⚡ SQL优化脚本
- ⚡ 缓存配置代码
- 📈 Prometheus + Grafana配置

### 性能指标
| 指标 | 优化前 | 目标 | 验证 |
|------|--------|------|------|
| API QPS | ~50 | > 100 | ⏸️ |
| P99延迟 | ~3s | < 2s | ⏸️ |
| 缓存命中率 | ~70% | > 95% | ⏸️ |
| 特征提取性能 | - | > 1000条/秒 | ⏸️ |

### 文档交付
- 📄 Phase 4完成报告
- 📄 AI特征提取API文档
- 📄 性能调优指南
- 📄 监控配置手册

---

## 🎯 验收标准

### 功能验收
- [ ] AI特征提取服务正常工作
- [ ] 支持6种缺失值处理方法
- [ ] 支持3种异常值处理方法
- [ ] 支持2种归一化方法
- [ ] 训练数据集生成功能正常

### 性能验收
- [ ] 特征提取性能 > 1000条/秒
- [ ] API QPS > 100
- [ ] P99延迟 < 2秒
- [ ] 缓存命中率 > 95%
- [ ] 错误率 < 1%

### 监控验收
- [ ] Prometheus正确采集指标
- [ ] Grafana仪表盘正常显示
- [ ] 告警规则配置完成
- [ ] 告警通知正常

### 文档验收
- [ ] API文档完整
- [ ] 性能调优指南完整
- [ ] 监控配置手册完整
- [ ] Phase 4完成报告完整

---

## ⚠️ 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| AI算法复杂度高 | 中 | 高 | 先实现基础功能，高级功能迭代 |
| 性能目标难以达成 | 中 | 中 | 分阶段优化，持续改进 |
| Redis依赖问题 | 低 | 中 | 支持降级到内存缓存 |
| 监控配置复杂 | 中 | 低 | 提供配置模板和示例 |

---

## 📅 时间规划

### Week 10
- Day 1-3: AIFeatureService核心开发
- Day 4-5: AI特征API开发

### Week 11
- Day 1-2: 集成测试和调试
- Day 3-5: 文档和示例代码

### Week 12
- Day 1-2: 性能优化
- Day 3-4: 监控告警配置
- Day 5: 测试和文档

---

## 🎉 完成后

Phase 4完成后，系统将具备：
1. ✨ **完整的AI能力** - 特征提取、数据集生成
2. ⚡ **优秀的性能** - QPS翻倍，延迟减半
3. 📈 **完善的监控** - 实时掌握系统状态
4. 🛡️ **稳定的运行** - 告警及时，快速响应

**下一步**: Phase 5 - 全面测试与正式上线

---

**创建时间**: 2025-11-03  
**作者**: AI Assistant  
**状态**: ⏸️ 待开始


