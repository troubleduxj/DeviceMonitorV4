# Week 3 Day 3-4: 前端集成 - 实施计划

> **计划日期**: 2025-11-04  
> **任务周期**: Day 3-4 (前端集成)  
> **前置条件**: Day 1-2 API接口实现 ✅ 已完成

---

## 📋 任务概述

将Week 3 Day 1-2完成的4个AI核心API集成到前端AI监测模块，实现数据可视化和交互功能。

**核心目标**:
1. 创建统一的前端API客户端
2. 集成AI仪表盘实时数据
3. 集成异常检测功能
4. 集成趋势预测功能
5. 集成健康评分功能
6. 优化Echarts图表展示

---

## 🎯 详细任务分解

### Task 1: ✅ 创建前端API客户端 (已完成)

**文件**: `web/src/api/v2/ai-module.js`

**完成内容**:
- ✅ `aiModuleApi` - AI模块系统API
- ✅ `featureExtractionApi` - 特征提取API（3个方法）
- ✅ `anomalyDetectionApi` - 异常检测API（4个方法）
- ✅ `trendPredictionApi` - 趋势预测API（4个方法）
- ✅ `healthScoringApi` - 健康评分API（5个方法）
- ✅ `aiFeaturesApi` - 旧版兼容API

**总计**: 21个API方法 ✅

---

### Task 2: ⏳ 集成AI仪表盘页面 (进行中)

**文件**: `web/src/views/ai-monitor/dashboard/index.vue`

**集成内容**:
- [ ] 获取实时设备健康评分数据
- [ ] 显示异常检测统计
- [ ] 展示趋势预测图表
- [ ] 集成健康评分卡片
- [ ] 实时数据刷新功能

**数据来源**:
```javascript
// 健康评分数据
healthScoringApi.score({
  device_code: 'WD001',
  performance_data: { cpu: 75.5, memory: 60.2 },
  anomaly_count: 3,
  uptime_days: 45
})

// 异常检测数据
anomalyDetectionApi.getRecords({
  page: 1,
  page_size: 10,
  is_handled: false
})

// 趋势预测（用于图表）
trendPredictionApi.predict({
  data: historicalData,
  steps: 10,
  method: 'auto'
})
```

**图表组件**:
- `AnomalyChart.vue` - 异常趋势图表
- `TrendChart.vue` - 健康趋势图表
- `HealthOverview.vue` - 健康状态总览

---

### Task 3: ⏸️ 集成异常检测页面 (待实施)

**文件**: `web/src/views/ai-monitor/anomaly-detection/index.vue`

**功能需求**:
1. **数据输入区域**
   - 设备选择器
   - 数据时间范围选择
   - 检测方法选择（统计/孤立森林/组合）
   - 阈值配置

2. **检测执行区域**
   - 执行检测按钮
   - 实时检测进度
   - 检测结果展示

3. **异常记录列表**
   - 异常记录表格
   - 严重程度筛选
   - 处理状态筛选
   - 处理操作

4. **可视化展示**
   - 异常点标记图表
   - 异常分布图
   - 严重程度分布饼图

**API调用**:
```javascript
// 执行异常检测
anomalyDetectionApi.detect({
  data: deviceData,
  device_code: selectedDevice,
  method: 'combined',
  threshold: 3.0,
  save_to_db: true
})

// 获取异常记录
anomalyDetectionApi.getRecords({
  device_code: selectedDevice,
  severity: selectedSeverity,
  is_handled: false,
  page: currentPage,
  page_size: 20
})

// 处理异常
anomalyDetectionApi.handleRecord(recordId, '已检查，设备正常')
```

---

### Task 4: ⏸️ 集成趋势预测页面 (待实施)

**文件**: `web/src/views/ai-monitor/trend-prediction/index.vue`

**功能需求**:
1. **预测配置区域**
   - 设备选择器
   - 历史数据范围
   - 预测步数输入
   - 预测方法选择（ARIMA/MA/EMA/LR/Auto）
   - 置信水平设置

2. **预测执行区域**
   - 执行预测按钮
   - 方法对比按钮
   - 预测进度显示

3. **预测结果展示**
   - 预测值表格
   - 置信区间
   - 趋势方向标识
   - 评估指标（MAE/RMSE/MAPE）

4. **可视化展示**
   - 历史数据+预测曲线图
   - 置信区间阴影
   - 多方法对比图
   - 趋势方向指示器

**API调用**:
```javascript
// 执行单一预测
trendPredictionApi.predict({
  data: historicalData,
  steps: 10,
  method: 'arima',
  confidence_level: 0.95
})

// 方法对比
trendPredictionApi.compare({
  data: historicalData,
  steps: 10,
  methods: ['arima', 'ma', 'ema', 'lr']
})

// 获取预测方法说明
trendPredictionApi.getMethods()
```

---

### Task 5: ⏸️ 集成健康评分页面 (待实施)

**文件**: `web/src/views/ai-monitor/health-scoring/index.vue`

**功能需求**:
1. **评分配置区域**
   - 设备选择器
   - 性能数据输入（CPU、内存、响应时间等）
   - 异常次数输入
   - 运行时长输入
   - 权重配置（可选）

2. **评分执行区域**
   - 执行评分按钮
   - 批量评分按钮
   - 评分进度显示

3. **评分结果展示**
   - 总分（0-100）
   - 健康等级（A/B/C/D/F）
   - 各维度评分
   - 改进建议列表
   - 风险等级

4. **健康趋势分析**
   - 历史评分曲线
   - 趋势方向（改善/恶化/稳定）
   - 平均分统计
   - 等级分布

5. **批量评分视图**
   - 设备列表
   - 批量评分结果
   - 等级分布图
   - 健康排名

**API调用**:
```javascript
// 单设备评分
healthScoringApi.score({
  device_code: 'WD001',
  device_name: '焊机001',
  performance_data: {
    cpu_usage: 75.5,
    memory_usage: 60.2,
    response_time: 120.0
  },
  anomaly_count: 3,
  uptime_days: 45.5,
  save_to_db: true
})

// 批量评分
healthScoringApi.scoreBatch({
  devices: {
    'WD001': { performance_data: {...}, anomaly_count: 3 },
    'WD002': { performance_data: {...}, anomaly_count: 1 }
  }
})

// 获取健康趋势
healthScoringApi.getTrend('WD001', 30)

// 获取评分历史
healthScoringApi.getHistory({
  device_code: 'WD001',
  page: 1,
  page_size: 20
})
```

---

### Task 6: ⏸️ 优化Echarts图表展示 (待实施)

**目标**: 统一所有AI监测页面的图表样式和交互

**优化内容**:
1. **图表主题统一**
   - 使用统一的颜色方案
   - 一致的字体和大小
   - 统一的图例样式

2. **交互优化**
   - 添加数据缩放（dataZoom）
   - 添加工具箱（toolbox）
   - 添加数据标注
   - 添加数据导出功能

3. **性能优化**
   - 大数据量使用虚拟滚动
   - 按需加载图表数据
   - 图表resize优化

4. **响应式设计**
   - 移动端适配
   - 不同屏幕尺寸优化

**图表类型**:
- 折线图（趋势预测、健康评分历史）
- 柱状图（异常统计、性能对比）
- 饼图（等级分布、异常类型分布）
- 散点图（异常点标记）
- 仪表盘（健康评分、CPU使用率）

---

## 📊 实施时间表

| 任务 | 预计时间 | 状态 |
|------|---------|------|
| Task 1: 前端API客户端 | 1小时 | ✅ 已完成 |
| Task 2: AI仪表盘集成 | 3小时 | ⏳ 进行中 |
| Task 3: 异常检测页面 | 4小时 | ⏸️ 待实施 |
| Task 4: 趋势预测页面 | 4小时 | ⏸️ 待实施 |
| Task 5: 健康评分页面 | 4小时 | ⏸️ 待实施 |
| Task 6: 图表优化 | 2小时 | ⏸️ 待实施 |
| **总计** | **18小时** | **~2天** |

---

## ✅ 验收标准

### 功能验收
- [ ] 所有API调用正常，无404或500错误
- [ ] 数据可视化图表正确展示
- [ ] 交互功能完整（刷新、筛选、分页等）
- [ ] 错误处理完善（加载失败、数据为空等）
- [ ] 响应式设计正常

### 性能验收
- [ ] 页面加载时间 < 2秒
- [ ] 图表渲染流畅，无卡顿
- [ ] 大数据量处理正常（1000+数据点）

### 代码质量
- [ ] Linter 0错误
- [ ] TypeScript类型检查通过
- [ ] 代码风格符合规范
- [ ] 组件复用性良好

---

## 🎨 UI/UX设计原则

1. **一致性**: 所有页面使用统一的布局和交互模式
2. **可读性**: 图表和数据清晰易读
3. **响应性**: 快速反馈用户操作
4. **引导性**: 提供操作提示和帮助信息
5. **容错性**: 友好的错误提示和降级处理

---

## 📚 参考资源

- **Naive UI**: https://www.naiveui.com/
- **Echarts**: https://echarts.apache.org/
- **Vue 3**: https://vuejs.org/
- **Vueuse**: https://vueuse.org/

---

## 🚀 后续优化（可选）

- [ ] 添加数据缓存，减少API调用
- [ ] 添加WebSocket实时更新
- [ ] 添加数据导出功能（Excel/CSV/PDF）
- [ ] 添加自定义仪表盘配置
- [ ] 添加AI模型配置界面
- [ ] 添加批量操作功能

---

**计划制定时间**: 2025-11-04  
**状态**: 🚀 开始实施

