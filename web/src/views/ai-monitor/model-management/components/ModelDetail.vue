<template>
  <n-modal
    v-model:show="showModal"
    preset="card"
    title="模型详情"
    :style="{ width: '800px', maxHeight: '80vh' }"
    :mask-closable="true"
    :closable="true"
  >
    <div v-if="model" class="model-detail">
      <!-- 基本信息 -->
      <n-card title="基本信息" class="detail-section">
        <n-descriptions :column="2" label-placement="left">
          <n-descriptions-item label="模型名称">
            {{ model.name }}
          </n-descriptions-item>
          <n-descriptions-item label="版本">
            <n-tag type="info">{{ model.version }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="类型">
            <n-tag type="primary">{{ getTypeText(model.type) }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag :type="getStatusType(model.status)">
              {{ getStatusText(model.status) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="文件大小">
            {{ model.size }}
          </n-descriptions-item>
          <n-descriptions-item label="作者">
            {{ model.author }}
          </n-descriptions-item>
          <n-descriptions-item label="创建时间">
            {{ formatDate(model.createdAt) }}
          </n-descriptions-item>
          <n-descriptions-item label="更新时间">
            {{ formatDate(model.updatedAt) }}
          </n-descriptions-item>
          <n-descriptions-item label="部署时间">
            {{ model.deployedAt ? formatDate(model.deployedAt) : '未部署' }}
          </n-descriptions-item>
        </n-descriptions>

        <n-descriptions-item label="描述" :span="2">
          <n-text>{{ model.description || '暂无描述' }}</n-text>
        </n-descriptions-item>
      </n-card>

      <!-- 性能指标 -->
      <n-card title="性能指标" class="detail-section">
        <n-grid :cols="4" :x-gap="16">
          <n-grid-item>
            <n-statistic label="准确率" :value="model.accuracy" suffix="%">
              <template #prefix>
                <n-icon color="#18a058">
                  <checkmark-circle-outline />
                </n-icon>
              </template>
            </n-statistic>
          </n-grid-item>
          <n-grid-item>
            <n-statistic label="精确率" :value="model.metrics?.precision || 0" suffix="%">
              <template #prefix>
                <n-icon color="#2080f0">
                  <locate-outline />
                </n-icon>
              </template>
            </n-statistic>
          </n-grid-item>
          <n-grid-item>
            <n-statistic label="召回率" :value="model.metrics?.recall || 0" suffix="%">
              <template #prefix>
                <n-icon color="#f0a020">
                  <search-outline />
                </n-icon>
              </template>
            </n-statistic>
          </n-grid-item>
          <n-grid-item>
            <n-statistic label="F1分数" :value="model.metrics?.f1Score || 0" suffix="%">
              <template #prefix>
                <n-icon color="#d03050">
                  <analytics-outline />
                </n-icon>
              </template>
            </n-statistic>
          </n-grid-item>
        </n-grid>

        <!-- 性能图表 -->
        <div class="performance-chart" style="margin-top: 16px; height: 200px">
          <n-empty description="性能趋势图表" size="small" />
        </div>
      </n-card>

      <!-- 标签 -->
      <n-card v-if="model.tags && model.tags.length > 0" title="标签" class="detail-section">
        <n-space>
          <n-tag v-for="tag in model.tags" :key="tag" type="info" size="small">
            {{ tag }}
          </n-tag>
        </n-space>
      </n-card>

      <!-- 配置参数 -->
      <n-card
        v-if="model.parameters && model.parameters.length > 0"
        title="配置参数"
        class="detail-section"
      >
        <n-table size="small">
          <thead>
            <tr>
              <th>参数名</th>
              <th>参数值</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="param in model.parameters" :key="param.key">
              <td>{{ param.key }}</td>
              <td>
                <n-tag size="small">{{ param.value }}</n-tag>
              </td>
            </tr>
          </tbody>
        </n-table>
      </n-card>

      <!-- 部署历史 -->
      <n-card title="部署历史" class="detail-section">
        <n-timeline>
          <n-timeline-item
            type="success"
            title="模型创建"
            :time="formatDate(model.createdAt)"
            content="模型文件上传完成"
          />
          <n-timeline-item
            v-if="model.deployedAt"
            type="info"
            title="首次部署"
            :time="formatDate(model.deployedAt)"
            content="模型成功部署到生产环境"
          />
          <n-timeline-item
            v-if="model.status === 'running'"
            type="success"
            title="当前状态"
            time="现在"
            content="模型正在运行中"
          />
        </n-timeline>
      </n-card>

      <!-- 训练日志 -->
      <n-card title="训练日志" class="detail-section">
        <n-log
          :log="trainingLogs"
          :loading="loadingLogs"
          :rows="15"
          trim
          style="background-color: #1e1e1e; padding: 10px; border-radius: 4px; font-family: monospace;"
        />
        <n-space justify="end" style="margin-top: 8px">
          <n-button size="small" @click="fetchLogs">刷新日志</n-button>
        </n-space>
      </n-card>

      <!-- 操作日志 -->
      <n-card title="操作日志" class="detail-section">
        <n-table size="small">
          <thead>
            <tr>
              <th>时间</th>
              <th>操作</th>
              <th>操作者</th>
              <th>结果</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in mockLogs" :key="log.id">
              <td>{{ formatDate(log.time) }}</td>
              <td>{{ log.action }}</td>
              <td>{{ log.operator }}</td>
              <td>
                <n-tag :type="log.success ? 'success' : 'error'" size="small">
                  {{ log.success ? '成功' : '失败' }}
                </n-tag>
              </td>
            </tr>
          </tbody>
        </n-table>
      </n-card>
    </div>

    <template #action>
      <n-space justify="end">
        <n-button @click="showModal = false">关闭</n-button>
        <n-button type="primary" @click="handleDownload">
          <template #icon>
            <n-icon><download-outline /></n-icon>
          </template>
          下载模型
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch } from 'vue'
import {
  NModal,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NTag,
  NText,
  NGrid,
  NGridItem,
  NStatistic,
  NIcon,
  NSpace,
  NTable,
  NTimeline,
  NTimelineItem,
  NButton,
  NEmpty,
  useMessage,
  NLog,
} from 'naive-ui'
import {
  CheckmarkCircleOutline,
  SearchOutline,
  AnalyticsOutline,
  DownloadOutline,
  LocateOutline,
} from '@vicons/ionicons5'
import { modelManagementApi } from '@/api/v2/ai-module'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  model: {
    type: Object,
    default: null,
  },
})

// Emits
const emit = defineEmits(['update:show'])

// 计算属性
const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value),
})

// 消息提示
const message = useMessage()

// 训练日志
const trainingLogs = ref('')
const loadingLogs = ref(false)
let logPollingTimer = null

// 获取日志
const fetchLogs = async (isPolling = false) => {
  if (!props.model?.id) return
  
  if (!isPolling) loadingLogs.value = true
  try {
    const res = await modelManagementApi.getLogs(props.model.id)
    trainingLogs.value = res.data.logs || '暂无日志'
  } catch (error) {
    console.error('获取日志失败:', error)
    if (!isPolling) trainingLogs.value = '获取日志失败'
  } finally {
    if (!isPolling) loadingLogs.value = false
  }
}

// 轮询控制
const startLogPolling = () => {
  stopLogPolling()
  // 如果是训练中，开启轮询
  if (props.model?.status === 'training') {
    logPollingTimer = setInterval(() => {
      fetchLogs(true)
    }, 2000) // 2秒轮询一次
  }
}

const stopLogPolling = () => {
  if (logPollingTimer) {
    clearInterval(logPollingTimer)
    logPollingTimer = null
  }
}

// 监听弹窗打开，自动获取日志
watch(
  () => props.show,
  (val) => {
    if (val && props.model?.id) {
      fetchLogs()
      startLogPolling()
    } else {
      stopLogPolling()
    }
  }
)

// 监听状态变化
watch(
  () => props.model?.status,
  (newStatus) => {
    if (props.show) {
      if (newStatus === 'training') {
        startLogPolling()
      } else {
        stopLogPolling()
        // 状态变为非训练时，最后拉取一次日志
        fetchLogs()
      }
    }
  }
)

onUnmounted(() => {
  stopLogPolling()
})

// 模拟操作日志
const mockLogs = ref([
  {
    id: 1,
    time: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    action: '模型上传',
    operator: '用户1',
    success: true,
  },
  {
    id: 2,
    time: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    action: '模型部署',
    operator: '用户1',
    success: true,
  },
  {
    id: 3,
    time: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
    action: '模型停止',
    operator: '用户2',
    success: true,
  },
  {
    id: 4,
    time: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    action: '模型重启',
    operator: '用户1',
    success: true,
  },
])

// 获取状态标签类型
const getStatusType = (status) => {
  const statusMap = {
    running: 'success',
    stopped: 'default',
    training: 'warning',
    deploying: 'info',
    error: 'error',
  }
  return statusMap[status] || 'default'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    running: '运行中',
    stopped: '已停止',
    training: '训练中',
    deploying: '部署中',
    error: '错误',
  }
  return statusMap[status] || status
}

// 获取模型类型文本
const getTypeText = (type) => {
  const typeMap = {
    anomaly_detection: '异常检测',
    trend_prediction: '趋势预测',
    health_scoring: '健康评分',
    classification: '分类模型',
    regression: '回归模型',
  }
  return typeMap[type] || type
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 下载模型
const handleDownload = () => {
  if (props.model) {
    message.info(`开始下载模型: ${props.model.name}`)
    // 这里可以实现实际的下载逻辑
  }
}
</script>

<style scoped>
.model-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.performance-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  background-color: #fafafa;
}
</style>
