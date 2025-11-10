# Week 2-3: AI功能开发详细计划

**计划周期**: 2-3周  
**开始日期**: 2025-11-04  
**状态**: 待开始  
**前置条件**: Week 1模块化实施已完成 ✅

---

## 📋 总体目标

在Week 1建立的模块化架构基础上，实现以下核心AI功能：
1. **特征提取服务** - 从设备数据中提取有价值的特征
2. **异常检测算法** - 实时检测设备运行异常
3. **趋势预测模型** - 预测设备状态趋势
4. **健康评分系统** - 综合评估设备健康状况

---

## 🗓️ 实施时间表

### Week 2: 核心算法实现（7天）

#### Day 1-2: 特征提取服务
- [ ] 统计特征提取
- [ ] 时间序列特征
- [ ] 频域特征
- [ ] 特征缓存机制

#### Day 3-4: 异常检测算法
- [ ] 基于统计的异常检测（3-sigma规则）
- [ ] 基于孤立森林的异常检测
- [ ] 异常等级划分
- [ ] 异常记录存储

#### Day 5-6: 趋势预测模型
- [ ] ARIMA时间序列预测
- [ ] 简单移动平均预测
- [ ] 预测结果缓存
- [ ] 预测准确度评估

#### Day 7: 健康评分系统
- [ ] 多维度指标定义
- [ ] 综合评分算法
- [ ] 健康等级划分
- [ ] 评分历史记录

### Week 3: 集成与优化（7-10天）

#### Day 1-2: API接口实现
- [ ] 特征提取API
- [ ] 异常检测API
- [ ] 趋势预测API
- [ ] 健康评分API

#### Day 3-4: 前端集成
- [ ] AI仪表盘页面
- [ ] 异常检测页面
- [ ] 趋势预测页面
- [ ] 健康评分页面

#### Day 5-6: 性能优化
- [ ] 算法性能优化
- [ ] 缓存策略优化
- [ ] 异步任务处理
- [ ] 资源使用优化

#### Day 7: 测试与文档
- [ ] 单元测试
- [ ] 集成测试
- [ ] API文档
- [ ] 用户文档

---

## 🎯 详细任务分解

### 1. 特征提取服务

#### 1.1 统计特征
**文件**: `app/services/ai/feature_extraction.py`

**功能**:
- 均值、方差、标准差
- 最大值、最小值、范围
- 分位数（25%, 50%, 75%）
- 峰度、偏度

**实现思路**:
```python
class StatisticalFeatureExtractor:
    def extract(self, data: List[float]) -> Dict[str, float]:
        return {
            'mean': np.mean(data),
            'std': np.std(data),
            'max': np.max(data),
            'min': np.min(data),
            'q25': np.percentile(data, 25),
            'q50': np.percentile(data, 50),
            'q75': np.percentile(data, 75),
        }
```

#### 1.2 时间序列特征
**功能**:
- 趋势（上升/下降/平稳）
- 周期性检测
- 自相关系数
- 变化率

**实现思路**:
```python
class TimeSeriesFeatureExtractor:
    def extract_trend(self, data: List[float]) -> str:
        """提取趋势：上升、下降、平稳"""
        coefficients = np.polyfit(range(len(data)), data, 1)
        slope = coefficients[0]
        if slope > 0.1:
            return "上升"
        elif slope < -0.1:
            return "下降"
        else:
            return "平稳"
```

#### 1.3 频域特征
**功能**:
- FFT频谱分析
- 主频率识别
- 频率能量分布

**实现思路**:
```python
class FrequencyFeatureExtractor:
    def extract(self, data: List[float]) -> Dict:
        fft_result = np.fft.fft(data)
        frequencies = np.fft.fftfreq(len(data))
        # 提取主频率、能量等
```

---

### 2. 异常检测算法

#### 2.1 基于统计的异常检测
**文件**: `app/services/ai/anomaly_detection.py`

**方法**: 3-sigma规则
```python
class StatisticalAnomalyDetector:
    def detect(self, data: List[float]) -> List[Dict]:
        mean = np.mean(data)
        std = np.std(data)
        threshold = 3 * std
        
        anomalies = []
        for i, value in enumerate(data):
            if abs(value - mean) > threshold:
                anomalies.append({
                    'index': i,
                    'value': value,
                    'severity': self._calculate_severity(value, mean, std)
                })
        return anomalies
```

**异常等级**:
- 轻微: 3σ < |x - μ| < 4σ
- 中等: 4σ < |x - μ| < 5σ
- 严重: |x - μ| > 5σ

#### 2.2 基于孤立森林的异常检测
**方法**: Isolation Forest
```python
from sklearn.ensemble import IsolationForest

class MLAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1)
    
    def fit_predict(self, data: np.ndarray) -> np.ndarray:
        predictions = self.model.fit_predict(data)
        # -1表示异常，1表示正常
        return predictions
```

#### 2.3 异常记录存储
**数据库表**: `t_ai_anomaly_record`
```sql
CREATE TABLE t_ai_anomaly_record (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50),
    metric_name VARCHAR(100),
    anomaly_value FLOAT,
    expected_value FLOAT,
    severity VARCHAR(20),
    detection_method VARCHAR(50),
    detected_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);
```

---

### 3. 趋势预测模型

#### 3.1 ARIMA预测
**文件**: `app/services/ai/prediction.py`

```python
from statsmodels.tsa.arima.model import ARIMA

class ARIMAPredictor:
    def predict(self, history: List[float], steps: int = 10) -> List[float]:
        """
        使用ARIMA模型预测未来值
        
        Args:
            history: 历史数据
            steps: 预测步数
        
        Returns:
            预测值列表
        """
        model = ARIMA(history, order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        return forecast.tolist()
```

#### 3.2 简单移动平均预测
```python
class MovingAveragePredictor:
    def predict(self, history: List[float], window: int = 5) -> float:
        """简单移动平均预测下一个值"""
        if len(history) < window:
            return np.mean(history)
        return np.mean(history[-window:])
```

#### 3.3 预测准确度评估
**指标**:
- MAE (平均绝对误差)
- RMSE (均方根误差)
- MAPE (平均绝对百分比误差)

```python
class PredictionEvaluator:
    @staticmethod
    def calculate_mae(actual: List[float], predicted: List[float]) -> float:
        return np.mean(np.abs(np.array(actual) - np.array(predicted)))
    
    @staticmethod
    def calculate_rmse(actual: List[float], predicted: List[float]) -> float:
        return np.sqrt(np.mean((np.array(actual) - np.array(predicted)) ** 2))
```

---

### 4. 健康评分系统

#### 4.1 评分维度
**文件**: `app/services/ai/health_scoring.py`

**维度定义**:
1. **性能指标** (30%): 基于关键性能参数
2. **异常频率** (25%): 最近异常发生频率
3. **趋势健康** (25%): 趋势是否健康
4. **运行时长** (20%): 连续运行稳定性

```python
class HealthScoreCalculator:
    WEIGHTS = {
        'performance': 0.30,
        'anomaly_frequency': 0.25,
        'trend': 0.25,
        'uptime': 0.20
    }
    
    def calculate(self, metrics: Dict) -> Dict:
        """计算综合健康评分"""
        scores = {
            'performance': self._score_performance(metrics),
            'anomaly_frequency': self._score_anomaly(metrics),
            'trend': self._score_trend(metrics),
            'uptime': self._score_uptime(metrics)
        }
        
        # 加权平均
        total_score = sum(
            scores[key] * self.WEIGHTS[key] 
            for key in scores
        )
        
        return {
            'total_score': total_score,
            'grade': self._get_grade(total_score),
            'details': scores
        }
    
    def _get_grade(self, score: float) -> str:
        """评分等级"""
        if score >= 90: return 'A-优秀'
        elif score >= 80: return 'B-良好'
        elif score >= 70: return 'C-一般'
        elif score >= 60: return 'D-较差'
        else: return 'F-危险'
```

#### 4.2 评分历史记录
**数据库表**: `t_ai_health_score`
```sql
CREATE TABLE t_ai_health_score (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50),
    total_score FLOAT,
    grade VARCHAR(20),
    performance_score FLOAT,
    anomaly_score FLOAT,
    trend_score FLOAT,
    uptime_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔌 API接口设计

### 特征提取API
```python
@router.post("/ai/features/extract")
@require_ai_feature("feature_extraction")
async def extract_features(
    device_id: str,
    metric_name: str,
    time_range: Optional[str] = "1h"
):
    """提取设备指标特征"""
    pass
```

### 异常检测API
```python
@router.post("/ai/anomaly/detect")
@require_ai_feature("anomaly_detection")
async def detect_anomalies(
    device_id: str,
    metric_name: str,
    method: str = "statistical"  # or "ml"
):
    """检测异常"""
    pass

@router.get("/ai/anomaly/list")
@require_ai_feature("anomaly_detection")
async def list_anomalies(
    device_id: Optional[str] = None,
    severity: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """查询异常记录"""
    pass
```

### 趋势预测API
```python
@router.post("/ai/prediction/forecast")
@require_ai_feature("trend_prediction")
async def forecast_trend(
    device_id: str,
    metric_name: str,
    steps: int = 10,
    model: str = "arima"  # or "ma"
):
    """趋势预测"""
    pass
```

### 健康评分API
```python
@router.get("/ai/health/score/{device_id}")
@require_ai_feature("health_scoring")
async def get_health_score(device_id: str):
    """获取设备健康评分"""
    pass

@router.get("/ai/health/history/{device_id}")
@require_ai_feature("health_scoring")
async def get_health_history(
    device_id: str,
    days: int = 7
):
    """获取健康评分历史"""
    pass
```

---

## 📦 依赖包

### 新增Python包
```txt
# 数据分析
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0

# 机器学习
scikit-learn>=1.0.0

# 时间序列
statsmodels>=0.13.0

# 性能优化
numba>=0.54.0  # 可选，用于加速
```

### 安装命令
```bash
pip install numpy pandas scipy scikit-learn statsmodels
```

---

## ✅ 验收标准

### 功能验收
- [ ] 所有核心算法实现并通过单元测试
- [ ] API接口完整且文档清晰
- [ ] 前端页面可用且数据展示正确
- [ ] 性能满足要求（响应时间<2s）

### 质量验收
- [ ] 代码测试覆盖率 ≥ 80%
- [ ] 无严重性能问题
- [ ] 无严重bug
- [ ] 文档完整

### 性能指标
- 特征提取: <500ms (1000条数据)
- 异常检测: <1s (1000条数据)
- 趋势预测: <2s (100条历史数据，预测10步)
- 健康评分: <300ms

---

## 📝 测试计划

### 单元测试
- 特征提取器测试
- 异常检测器测试
- 预测模型测试
- 健康评分测试

### 集成测试
- API端到端测试
- 前后端集成测试
- 性能压力测试

### 测试数据
- 使用模拟设备数据
- 覆盖正常、异常、边界情况
- 不同数据量测试（10条、100条、1000条）

---

## 🚀 部署计划

### 开发环境
1. 安装依赖包
2. 配置AI功能开关
3. 运行测试验证

### 生产环境
1. 性能测试通过后
2. 分阶段启用功能
3. 监控资源使用
4. 收集用户反馈

---

## 📊 风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 算法性能不足 | 高 | 中 | 提前性能测试，优化算法 |
| 依赖包兼容性 | 中 | 低 | 锁定版本，充分测试 |
| 数据质量问题 | 高 | 中 | 数据预处理，异常处理 |
| 资源占用过高 | 中 | 中 | 资源监控，限流控制 |

---

## 📚 参考资料

### 算法文档
- ARIMA: https://otexts.com/fpp2/arima.html
- Isolation Forest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
- 时间序列分析: https://www.statsmodels.org/stable/tsa.html

### 最佳实践
- 特征工程: https://www.featuretools.com/
- 异常检测: https://scikit-learn.org/stable/modules/outlier_detection.html

---

## 🎯 下一步行动

**立即开始**: Day 1-2 特征提取服务实现

**关键里程碑**:
- Week 2 Day 7: 核心算法完成
- Week 3 Day 4: 前端集成完成
- Week 3 Day 7: 全部完成并交付

---

**计划制定日期**: 2025-11-04  
**计划制定者**: AI Assistant  
**审核状态**: 待确认

