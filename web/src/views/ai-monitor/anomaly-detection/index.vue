<template>
  <CommonPage title="异常检测看板">
    <template #action>
      <n-space>
        <n-button type="primary" size="small" @click="refreshData">
          <template #icon><n-icon><RefreshOutline /></n-icon></template>
          刷新数据
        </n-button>
        <n-button size="small">导出报表</n-button>
      </n-space>
    </template>

    <!-- 1. 顶部操作与筛选 -->
    <n-card :bordered="false" class="mb-4 shadow-sm" size="small">
      <div class="flex items-center gap-4">
        <n-form-item label="设备分类" label-placement="left" :show-feedback="false">
          <n-tree-select
            v-model:value="selectedDeviceTypes"
            multiple
            filterable
            placeholder="选择设备分类"
            :options="deviceTypeOptions"
            style="width: 300px"
            size="small"
            @update:value="handleDeviceFilterChange"
          />
        </n-form-item>
        <n-form-item label="时间范围" label-placement="left" :show-feedback="false">
          <n-radio-group v-model:value="timeRange" size="small">
            <n-radio-button value="1h">1小时</n-radio-button>
            <n-radio-button value="24h">24小时</n-radio-button>
            <n-radio-button value="7d">7天</n-radio-button>
          </n-radio-group>
        </n-form-item>
      </div>
    </n-card>

    <!-- 2. 核心指标卡片 -->
    <n-grid :x-gap="16" :cols="4" class="mb-4">
      <n-grid-item>
        <n-card size="small" :bordered="false" class="shadow-sm stats-card">
          <n-statistic label="监控设备总数" :value="deviceOptions.length">
            <template #prefix>
              <n-icon color="#2080f0" class="p-1 bg-blue-50 rounded"><ServerOutline /></n-icon>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card size="small" :bordered="false" class="shadow-sm stats-card">
          <n-statistic label="今日异常总数" :value="stats.total">
            <template #prefix>
              <n-icon color="#d03050" class="p-1 bg-red-50 rounded"><AlertCircleOutline /></n-icon>
            </template>
            <template #suffix>
              <span class="text-xs text-red-500 flex items-center ml-2">
                <n-icon><ArrowUpOutline /></n-icon> {{ stats.trend }}%
              </span>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card size="small" :bordered="false" class="shadow-sm stats-card">
          <n-statistic label="高风险设备" :value="stats.riskDevices">
            <template #prefix>
              <n-icon color="#f0a020" class="p-1 bg-yellow-50 rounded"><WarningOutline /></n-icon>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card size="small" :bordered="false" class="shadow-sm stats-card">
          <n-statistic label="平均健康度" :value="98.5" :precision="1">
             <template #prefix>
              <n-icon color="#18a058" class="p-1 bg-green-50 rounded"><PulseOutline /></n-icon>
            </template>
             <template #suffix><span class="text-xs text-gray-400">分</span></template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 3. 图表分析区 -->
    <n-grid :x-gap="20" :y-gap="20" cols="1 s:2" responsive="screen" class="mb-4 mt-4">
      <n-grid-item>
        <n-card title="全局异常趋势分析" :bordered="false" class="shadow-sm rounded-xl" hoverable>
          <template #header-extra>
             <n-tag type="info" size="small" round>近24小时</n-tag>
          </template>
          <div ref="trendChartRef" style="height: 400px"></div>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="设备风险排行 Top 5" :bordered="false" class="shadow-sm rounded-xl" hoverable>
           <div ref="rankChartRef" style="height: 400px"></div>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 4. 实时监控设备列表 -->
    <n-card title="实时监控设备列表" :bordered="false" size="small" class="shadow-sm">
      <template #header-extra>
        <n-space>
          <n-button type="primary" size="small" @click="handleAddDevice">
            <template #icon><n-icon><AddOutline /></n-icon></template>
            新增检测设备
          </n-button>
          <n-input-group size="small">
             <n-input placeholder="搜索设备名称/编号" v-model:value="searchKeyword" @keyup.enter="refreshData" />
             <n-button type="primary" ghost @click="refreshData">搜索</n-button>
          </n-input-group>
        </n-space>
      </template>
      <n-data-table
        :columns="deviceColumns"
        :data="deviceTableData"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
        size="small"
        :row-key="row => row.device_code"
      />
    </n-card>

    <!-- 抽屉：单设备详情 -->
    <n-drawer v-model:show="showDetail" width="90%" placement="right">
      <n-drawer-content :title="`设备详情: ${currentDeviceName}`" closable :body-content-style="{ padding: '0' }">
        <AnomalyDetail :device-code="currentDeviceCode" v-if="showDetail" />
      </n-drawer-content>
    </n-drawer>

    <!-- 弹窗：新增检测设备配置 -->
    <n-modal v-model:show="showConfigModal" preset="card" title="新增检测设备配置" style="width: 800px">
      <DetectionConfig 
        :config="{}" 
        @update="handleConfigUpdate"
        @reset="handleConfigReset"
      />
    </n-modal>

  </CommonPage>
</template>

<script setup>
import { ref, onMounted, onUnmounted, h, computed } from 'vue'
import { 
  RefreshOutline, 
  AlertCircleOutline, 
  WarningOutline, 
  ArrowUpOutline, 
  ServerOutline, 
  PulseOutline,
  AddOutline,
} from '@vicons/ionicons5'
import { NTag, NButton, useMessage, NProgress, NModal } from 'naive-ui'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import CommonPage from '@/components/page/CommonPage.vue'
import AnomalyDetail from './components/AnomalyDetail.vue'
import DetectionConfig from './components/DetectionConfig.vue'
import { deviceApi, deviceTypeApi } from '@/api/device-v2'
import { useRouter } from 'vue-router'

const router = useRouter()
import { anomalyDetectionApi } from '@/api/v2/ai-module'

// --- State ---
const selectedDeviceTypes = ref([])
const timeRange = ref('24h')
const showDetail = ref(false)
const showConfigModal = ref(false)
const currentDeviceCode = ref('')
const currentDeviceName = ref('')
const searchKeyword = ref('')
const message = useMessage()
const loading = ref(false)

const deviceTypeOptions = ref([])
const deviceTableData = ref([]) // Stores the list of devices with their status
const allRecords = ref([]) // Stores the raw anomaly records for calculation

const stats = ref({
  total: 0,
  riskDevices: 0,
  rate: 0,
  trend: 0
})

// --- Columns for Device List ---
const deviceColumns = [
  { 
    title: '设备编号', 
    key: 'device_code', 
    width: 120,
    fixed: 'left',
    render(row) {
      return h('span', { class: 'font-mono' }, row.device_code)
    }
  },
  { 
    title: '设备名称', 
    key: 'device_name', 
    width: 150 
  },
  { 
    title: '监控状态', 
    key: 'status',
    width: 100,
    render(row) {
      // Determine status based on recent anomalies
      if (row.severity === 'high') {
        return h(NTag, { type: 'error', size: 'small', round: true }, { default: () => '高风险' })
      } else if (row.severity === 'medium') {
        return h(NTag, { type: 'warning', size: 'small', round: true }, { default: () => '警告' })
      } else {
        return h(NTag, { type: 'success', size: 'small', round: true }, { default: () => '正常' })
      }
    }
  },
  {
    title: '异常置信度',
    key: 'anomaly_score',
    width: 150,
    render(row) {
      const score = row.anomaly_score || 0
      let status = 'success'
      if (score > 80) status = 'error'
      else if (score > 50) status = 'warning'
      
      return h(NProgress, {
        type: 'line',
        percentage: score > 100 ? 100 : score,
        indicatorPlacement: 'inside',
        status: status,
        height: 18
      })
    }
  },
  { 
    title: '最近检测时间', 
    key: 'last_check_time', 
    width: 160,
    render(row) {
      return row.last_check_time ? dayjs(row.last_check_time).format('YYYY-MM-DD HH:mm:ss') : '-'
    }
  },
  { 
    title: '异常统计(24h)', 
    key: 'anomaly_count', 
    width: 120,
    align: 'center',
    render(row) {
      return h('span', { class: row.anomaly_count > 0 ? 'text-red-500 font-bold' : 'text-gray-400' }, row.anomaly_count)
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    fixed: 'right',
    render(row) {
      return h(
        NButton,
        {
          size: 'tiny',
          type: 'primary',
          secondary: true,
          onClick: () => openDetail(row)
        },
        { default: () => '详情分析' }
      )
    }
  }
]

// --- API Methods ---

/**
 * 获取设备列表并整合异常状态
 */
const fetchDevicesAndStatus = async () => {
  loading.value = true
  try {
    // 1. 获取设备分类 (用于筛选)
    if (deviceTypeOptions.value.length === 0) {
      const typeRes = await deviceTypeApi.list()
      const items = typeRes.data?.items || (Array.isArray(typeRes.data) ? typeRes.data : [])
      deviceTypeOptions.value = items.map(t => ({
        label: t.type_name || t.type_code,
        key: t.type_code
      }))
    }

    // 2. 获取所有设备
    const deviceParams = { page_size: 1000 }
    if (searchKeyword.value) {
      deviceParams.search = searchKeyword.value
    }
    const deviceRes = await deviceApi.list(deviceParams) // Fetch enough devices
    let devices = deviceRes.data?.items || (Array.isArray(deviceRes.data) ? deviceRes.data : [])
    
    // Client-side filtering removed as backend handles search
    // if (searchKeyword.value) {
    //   const k = searchKeyword.value.toLowerCase()
    //   devices = devices.filter(d => 
    //     (d.device_name && d.device_name.toLowerCase().includes(k)) || 
    //     (d.device_code && d.device_code.toLowerCase().includes(k))
    //   )
    // }
    
    // Filter by Device Type if selected
    if (selectedDeviceTypes.value.length > 0) {
      devices = devices.filter(d => selectedDeviceTypes.value.includes(d.device_type))
    }

    // 3. 获取近期异常记录用于计算状态
    // Use a wider time range to capture recent status
    const recordRes = await anomalyDetectionApi.getRecords({
      page: 1,
      page_size: 100, 
      // time_range: timeRange.value // API support needed, assuming backend handles or we filter
    })
    
    const records = recordRes.data?.records || []
    allRecords.value = records // Save for charts

    // 3. Merge Status
    // Map: device_code -> { severity, score, last_time, count }
    const statusMap = {}
    
    records.forEach(r => {
      const code = r.device_code
      if (!statusMap[code]) {
        statusMap[code] = {
          count: 0,
          maxSeverity: 'low',
          maxScore: 0,
          lastTime: null
        }
      }
      
      statusMap[code].count++
      
      // Update Max Score
      if (r.anomaly_score > statusMap[code].maxScore) {
        statusMap[code].maxScore = r.anomaly_score
      }
      
      // Update Severity (high > medium > low)
      const currentSev = statusMap[code].maxSeverity
      if (r.severity === 'high') statusMap[code].maxSeverity = 'high'
      else if (r.severity === 'medium' && currentSev !== 'high') statusMap[code].maxSeverity = 'medium'
      
      // Update Last Time
      const rTime = dayjs(r.detection_time)
      if (!statusMap[code].lastTime || rTime.isAfter(dayjs(statusMap[code].lastTime))) {
        statusMap[code].lastTime = r.detection_time
      }
    })

    // 4. Build Table Data
    deviceTableData.value = devices.map(d => {
      const stat = statusMap[d.device_code] || {}
      return {
        ...d,
        severity: stat.maxSeverity || 'low',
        anomaly_score: stat.maxScore || 0, // In reality this should be the *latest* score, using max for now to highlight risk
        last_check_time: stat.lastTime || null, // Or d.updated_at
        anomaly_count: stat.count || 0
      }
    })
    
    // Sort by Risk (High severity first, then score)
    deviceTableData.value.sort((a, b) => {
       const severityWeight = { high: 3, medium: 2, low: 1 }
       const sa = severityWeight[a.severity] || 0
       const sb = severityWeight[b.severity] || 0
       if (sa !== sb) return sb - sa
       return b.anomaly_score - a.anomaly_score
    })

    // 5. Update Stats
    updateStats(records, deviceTableData.value)
    updateCharts(records)

  } catch (error) {
    console.error('获取数据失败', error)
    message.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

const updateStats = (records, devices) => {
  stats.value.total = records.length
  stats.value.riskDevices = devices.filter(d => d.severity === 'high').length
  // Simple trend mock
  stats.value.trend = 12.5 
}

// --- Charts ---
const trendChartRef = ref(null)
const rankChartRef = ref(null)
let trendChart = null
let rankChart = null

/**
 * 更新图表数据
 */
const updateCharts = (records) => {
  if (!trendChartRef.value || !rankChartRef.value) return
  
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)
  if (!rankChart) rankChart = echarts.init(rankChartRef.value)
  
  // 1. Rank Chart (Top Risk Devices)
  const deviceCount = {}
  records.forEach(r => {
    const name = r.device_name || r.device_code
    deviceCount[name] = (deviceCount[name] || 0) + 1
  })
  
  const sortedDevices = Object.entries(deviceCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    
  rankChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 10, right: 20, bottom: 20, left: 10, containLabel: true },
    xAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed' } } },
    yAxis: { type: 'category', data: sortedDevices.map(d => d[0]).reverse() },
    series: [{
      name: '异常次数',
      type: 'bar',
      barWidth: 20,
      data: sortedDevices.map(d => d[1]).reverse(),
      itemStyle: { 
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#188df0' }
        ])
      },
      label: { show: true, position: 'right' }
    }]
  })
  
  // 2. Trend Chart
  // Group by hour
  const timeMap = {}
  records.forEach(r => {
     const hour = dayjs(r.detection_time).format('HH:00')
     timeMap[hour] = (timeMap[hour] || 0) + 1
  })
  
  // Fill last 24h
  const hours = []
  const data = []
  for(let i=23; i>=0; i--) {
    const h = dayjs().subtract(i, 'hour').format('HH:00')
    hours.push(h)
    data.push(timeMap[h] || 0)
  }

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, right: 20, bottom: 20, left: 40, containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: hours },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed' } } },
    series: [{
      name: '异常数量',
      type: 'line',
      smooth: true,
      symbol: 'none',
      data: data,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(208, 48, 80, 0.5)' },
          { offset: 1, color: 'rgba(208, 48, 80, 0.05)' }
        ])
      },
      itemStyle: { color: '#d03050' }
    }]
  })
}

// --- Actions ---
const openDetail = (row) => {
  currentDeviceCode.value = row.device_code
  currentDeviceName.value = row.device_name || row.device_code
  showDetail.value = true
}

const handleDeviceFilterChange = () => {
  fetchDevicesAndStatus()
}

const handleAddDevice = () => {
  showConfigModal.value = true
}

const handleConfigUpdate = () => {
  // Config updated, maybe refresh list or just log
  // message.success('配置已更新')
}

const handleConfigReset = () => {
  // message.info('配置已重置')
}

const refreshData = () => {
  fetchDevicesAndStatus()
  message.success('数据已刷新')
}

// --- Lifecycle ---
onMounted(() => {
  fetchDevicesAndStatus()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (trendChart) trendChart.dispose()
  if (rankChart) rankChart.dispose()
})

const handleResize = () => {
  if (trendChart) trendChart.resize()
  if (rankChart) rankChart.resize()
}
</script>

<style scoped>
.anomaly-dashboard {
  background-color: #f5f7f9;
  min-height: 100vh;
  padding: 16px;
}

.stats-card {
  transition: all 0.3s;
}
.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

:deep(.n-card__content) {
  padding: 16px;
}
</style>
