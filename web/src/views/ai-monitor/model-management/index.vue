<template>
  <div class="model-management">
    <!-- 页面头部 -->
    <div v-permission="{ action: 'read', resource: 'model_management' }" class="page-header">
      <n-space justify="space-between" align="center">
        <div>
          <h2>模型管理</h2>
          <p class="page-description">管理AI模型的上传、部署、版本控制和性能监控</p>
        </div>
        <n-space>
          <PermissionButton
            permission="POST /api/v2/ai-monitor/models"
            type="primary"
            @click="showUploadModal = true"
          >
            <template #icon>
              <n-icon><cloud-upload-outline /></n-icon>
            </template>
            上传模型
          </PermissionButton>
          <PermissionButton permission="GET /api/v2/ai-monitor/models" @click="refreshData">
            <template #icon>
              <n-icon><refresh-outline /></n-icon>
            </template>
            刷新
          </PermissionButton>
        </n-space>
      </n-space>
    </div>

    <!-- 统计卡片 -->
    <n-grid :cols="4" :x-gap="16" :y-gap="16" class="stats-grid">
      <n-grid-item>
        <n-card>
          <n-statistic label="总模型数" :value="stats.totalModels">
            <template #prefix>
              <n-icon color="#18a058">
                <cube-outline />
              </n-icon>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="运行中" :value="stats.runningModels">
            <template #prefix>
              <n-icon color="#2080f0">
                <play-circle-outline />
              </n-icon>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="训练中" :value="stats.trainingModels">
            <template #prefix>
              <n-icon color="#f0a020">
                <time-outline />
              </n-icon>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="平均准确率" :value="stats.avgAccuracy" suffix="%">
            <template #prefix>
              <n-icon color="#18a058">
                <analytics-outline />
              </n-icon>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 筛选和搜索 -->
    <n-card class="filter-card">
      <n-space>
        <n-input
          v-model:value="searchKeyword"
          placeholder="搜索模型名称或描述"
          clearable
          style="width: 300px"
        >
          <template #prefix>
            <n-icon><search-outline /></n-icon>
          </template>
        </n-input>
        <n-select
          v-model:value="filterStatus"
          placeholder="状态筛选"
          clearable
          style="width: 150px"
          :options="statusOptions"
        />
        <n-select
          v-model:value="filterType"
          placeholder="模型类型"
          clearable
          style="width: 150px"
          :options="typeOptions"
        />
        <n-date-picker
          v-model:value="dateRange"
          type="daterange"
          clearable
          placeholder="创建时间范围"
        />
      </n-space>
    </n-card>

    <!-- 模型列表 -->
    <ModelList
      :models="filteredModels"
      :loading="loading"
      @deploy="handleDeploy"
      @stop="handleStop"
      @delete="handleDelete"
      @view-detail="handleViewDetail"
      @download="handleDownload"
    />

    <!-- 上传模型弹窗 -->
    <ModelUpload v-model:show="showUploadModal" @success="handleUploadSuccess" />

    <!-- 模型详情弹窗 -->
    <ModelDetail v-model:show="showDetailModal" :model="selectedModel" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  NSpace,
  NButton,
  NIcon,
  NCard,
  NGrid,
  NGridItem,
  NStatistic,
  NInput,
  NSelect,
  NDatePicker,
  useMessage,
  useDialog,
} from 'naive-ui'
import {
  CloudUploadOutline,
  RefreshOutline,
  CubeOutline,
  PlayCircleOutline,
  TimeOutline,
  AnalyticsOutline,
  SearchOutline,
} from '@vicons/ionicons5'
import PermissionButton from '@/components/common/PermissionButton.vue'
import ModelList from './components/ModelList.vue'
import ModelUpload from './components/ModelUpload.vue'
import ModelDetail from './components/ModelDetail.vue'

// 响应式数据
const loading = ref(false)
const showUploadModal = ref(false)
const showDetailModal = ref(false)
const selectedModel = ref(null)
const searchKeyword = ref('')
const filterStatus = ref(null)
const filterType = ref(null)
const dateRange = ref(null)

// 统计数据
const stats = ref({
  totalModels: 0,
  runningModels: 0,
  trainingModels: 0,
  avgAccuracy: 0,
})

// 模型列表
const models = ref([])

// 筛选选项
const statusOptions = [
  { label: '运行中', value: 'running' },
  { label: '已停止', value: 'stopped' },
  { label: '训练中', value: 'training' },
  { label: '部署中', value: 'deploying' },
  { label: '错误', value: 'error' },
]

const typeOptions = [
  { label: '异常检测', value: 'anomaly_detection' },
  { label: '趋势预测', value: 'trend_prediction' },
  { label: '健康评分', value: 'health_scoring' },
  { label: '分类模型', value: 'classification' },
  { label: '回归模型', value: 'regression' },
]

// 计算属性 - 过滤后的模型列表
const filteredModels = computed(() => {
  let result = models.value

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(
      (model) =>
        model.name.toLowerCase().includes(keyword) ||
        model.description.toLowerCase().includes(keyword)
    )
  }

  // 状态筛选
  if (filterStatus.value) {
    result = result.filter((model) => model.status === filterStatus.value)
  }

  // 类型筛选
  if (filterType.value) {
    result = result.filter((model) => model.type === filterType.value)
  }

  // 日期范围筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const [startDate, endDate] = dateRange.value
    result = result.filter((model) => {
      const modelDate = new Date(model.createdAt)
      return modelDate >= startDate && modelDate <= endDate
    })
  }

  return result
})

// 消息和对话框
const message = useMessage()
const dialog = useDialog()

// 生成模拟数据
const generateMockData = () => {
  const mockModels = []
  const statuses = ['running', 'stopped', 'training', 'deploying']
  const types = ['anomaly_detection', 'trend_prediction', 'health_scoring', 'classification']
  const names = [
    '设备异常检测模型',
    '生产趋势预测模型',
    '设备健康评分模型',
    '质量分类模型',
    '故障预警模型',
  ]

  for (let i = 1; i <= 15; i++) {
    mockModels.push({
      id: i,
      name: `${names[i % names.length]}_v${Math.floor(i / 3) + 1}.${i % 3}`,
      description: `这是一个用于${names[i % names.length]}的AI模型，具有高精度和稳定性`,
      type: types[i % types.length],
      status: statuses[i % statuses.length],
      version: `v${Math.floor(i / 3) + 1}.${i % 3}`,
      accuracy: (85 + Math.random() * 10).toFixed(2),
      size: `${(Math.random() * 500 + 50).toFixed(1)}MB`,
      createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      author: `用户${(i % 5) + 1}`,
      deployedAt:
        Math.random() > 0.5
          ? new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
          : null,
      metrics: {
        precision: (80 + Math.random() * 15).toFixed(2),
        recall: (75 + Math.random() * 20).toFixed(2),
        f1Score: (78 + Math.random() * 17).toFixed(2),
      },
    })
  }

  return mockModels
}

// 计算统计数据
const calculateStats = () => {
  const totalModels = models.value.length
  const runningModels = models.value.filter((m) => m.status === 'running').length
  const trainingModels = models.value.filter((m) => m.status === 'training').length
  const avgAccuracy = models.value.reduce((sum, m) => sum + parseFloat(m.accuracy), 0) / totalModels

  stats.value = {
    totalModels,
    runningModels,
    trainingModels,
    avgAccuracy: avgAccuracy.toFixed(1),
  }
}

// 刷新数据
const refreshData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise((resolve) => setTimeout(resolve, 1000))
    models.value = generateMockData()
    calculateStats()
    message.success('数据刷新成功')
  } catch (error) {
    message.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

// 处理模型部署
const handleDeploy = async (model) => {
  try {
    // 模拟部署过程
    message.loading('正在部署模型...', { duration: 2000 })
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // 更新模型状态
    const index = models.value.findIndex((m) => m.id === model.id)
    if (index !== -1) {
      models.value[index].status = 'running'
      models.value[index].deployedAt = new Date().toISOString()
    }

    calculateStats()
    message.success('模型部署成功')
  } catch (error) {
    message.error('模型部署失败')
  }
}

// 处理模型停止
const handleStop = async (model) => {
  try {
    const index = models.value.findIndex((m) => m.id === model.id)
    if (index !== -1) {
      models.value[index].status = 'stopped'
    }
    calculateStats()
    message.success('模型已停止')
  } catch (error) {
    message.error('停止模型失败')
  }
}

// 处理模型删除
const handleDelete = (model) => {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除模型 "${model.name}" 吗？此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const index = models.value.findIndex((m) => m.id === model.id)
        if (index !== -1) {
          models.value.splice(index, 1)
        }
        calculateStats()
        message.success('模型删除成功')
      } catch (error) {
        message.error('删除模型失败')
      }
    },
  })
}

// 查看模型详情
const handleViewDetail = (model) => {
  selectedModel.value = model
  showDetailModal.value = true
}

// 下载模型
const handleDownload = (model) => {
  message.info(`开始下载模型: ${model.name}`)
  // 这里可以实现实际的下载逻辑
}

// 上传成功回调
const handleUploadSuccess = (newModel) => {
  models.value.unshift(newModel)
  calculateStats()
  message.success('模型上传成功')
}

// 组件挂载时初始化数据
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.model-management {
  padding: 16px;
}

.page-header {
  margin-bottom: 16px;
}

.page-description {
  color: #666;
  margin: 4px 0 0 0;
  font-size: 14px;
}

.stats-grid {
  margin-bottom: 16px;
}

.filter-card {
  margin-bottom: 16px;
}
</style>
