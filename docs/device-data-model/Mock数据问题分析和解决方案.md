# 清理AI监测页面硬编码Mock数据 - 修复方案

## 需要修改的文件

### 1. 趋势预测页面
**文件**: `web/src/views/ai-monitor/trend-prediction/index.vue`

**需要修改的硬编码数据**:
- Line 301-309: healthTrendData
- Line 312-364: riskData  
- Line 380-394: reportData

**修改方案**:
```javascript
// ❌ 删除硬编码
// const riskData = ref([{...}, {...}])

// ✅ 改为初始为空，从API获取
const riskData = ref([])

// ✅ 在refreshPrediction中从API获取真实数据
const refreshPrediction = async () => {
  try {
    // 调用查询历史API
    const response = await predictionManagementApi.getHistory({
      device_code: 'WLD-001',
      page: 1,
      page_size: 10
    })
    
    if (response.code === 200 && response.data) {
      // 将API数据转换为页面需要的格式
      riskData.value = transformPredictionsToRiskData(response.data.items)
    }
  } catch (error) {
    message.error('加载预测数据失败')
  }
}
```

### 2. 健康评分页面
**文件**: `web/src/views/ai-monitor/health-scoring/index.vue`

**需要修改**:
- Line 259-298+: deviceList（硬编码的设备健康数据）
- Line 243-249: scoreDistributionData
- Line 219-224: overviewStats

### 3. 异常检测页面
**文件**: `web/src/views/ai-monitor/anomaly-detection/index.vue`

**需要检查并修改**硬编码的异常数据

### 4. Dashboard页面
**文件**: `web/src/views/ai-monitor/dashboard/index.vue`

**需要检查并修改**硬编码的概览数据

---

## 是否立即执行修复？

如果需要，我可以立即：
1. 清理所有硬编码Mock数据
2. 改为从API获取数据
3. 支持Mock管理系统和真实API两种模式
4. 添加加载状态和错误处理

预计时间：30-60分钟

