<template>
  <CommonPage show-footer>
    <!-- 页面标题和操作区 -->
    <template #action>
      <div class="flex items-center gap-3">
        <ViewToggle
          v-model="viewMode"
          :options="viewOptions"
          size="small"
          :show-label="false"
          :icon-size="16"
          align="right"
        />
      </div>
    </template>

    <!-- 查询条件 -->
    <NCard class="mb-15" rounded-10>
      <div class="query-form">
        <div class="form-row flex items-center gap-15">
          <QueryBarItem label="设备编号" :label-width="70">
            <NInput
              v-model:value="queryForm.device_code"
              style="width: 180px"
              placeholder="请输入设备编号"
              clearable
            />
          </QueryBarItem>
          <QueryBarItem label="设备名称" :label-width="70">
            <NInput
              v-model:value="queryForm.device_name"
              style="width: 180px"
              placeholder="请输入设备名称"
              clearable
            />
          </QueryBarItem>
          <QueryBarItem label="开始时间" :label-width="70">
            <NDatePicker
              v-model:value="queryForm.start_time"
              type="datetime"
              style="width: 180px"
              placeholder="请选择开始时间"
              clearable
            />
          </QueryBarItem>
          <QueryBarItem label="结束时间" :label-width="70">
            <NDatePicker
              v-model:value="queryForm.end_time"
              type="datetime"
              style="width: 180px"
              placeholder="请选择结束时间"
              clearable
            />
          </QueryBarItem>
          <NButton type="primary" @click="handleQuery">
            <TheIcon icon="material-symbols:search" :size="16" class="mr-5" />查询
          </NButton>
          <NButton class="ml-10" @click="handleReset">
            <TheIcon icon="material-symbols:refresh" :size="16" class="mr-5" />重置
          </NButton>
        </div>
      </div>
    </NCard>

    <!-- 设备历史参数 -->
    <NCard class="mb-15" rounded-10>
      <template #header>
        <span>{{ queryForm.device_name }}（{{ queryForm.device_code }}）</span>
      </template>

      <!-- 图表展示 -->
      <div v-if="viewMode === 'chart'" class="chart-container">
        <div ref="chartRef" style="width: 100%; height: 400px"></div>
      </div>

      <!-- 表格展示 -->
      <div v-else>
        <NDataTable :columns="historyColumns" :data="historyData" :loading="loading" striped />

        <!-- 独立分页组件 -->
        <div v-if="historyData.length > 0" class="mt-6 flex justify-center">
          <NPagination
            v-model:page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :item-count="pagination.itemCount"
            :page-sizes="pagination.pageSizes"
            :show-size-picker="pagination.showSizePicker"
            :show-quick-jumper="pagination.showQuickJumper"
            :prefix="pagination.prefix"
            :suffix="pagination.suffix"
            @update:page="handlePageChange"
            @update:page-size="handlePageSizeChange"
          />
        </div>
      </div>
    </NCard>
  </CommonPage>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, NCard, NInput, NDatePicker, NDataTable, NPagination, useMessage } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/page/QueryBarItem.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import ViewToggle from '@/components/common/ViewToggle.vue'
import { formatDate, formatDateTime } from '@/utils'
import * as echarts from 'echarts'
import { compatibilityApi as deviceDataApi } from '@/api/device-v2'

// 页面名称
defineOptions({ name: '历史数据查询' })

// 消息提示
const message = useMessage()

// 视图模式
const viewMode = ref('chart')
const chartRef = ref(null)
let chartInstance = null

// 视图切换选项
const viewOptions = [
  {
    value: 'chart',
    label: '图表视图',
    icon: 'material-symbols:bar-chart',
  },
  {
    value: 'table',
    label: '表格视图',
    icon: 'material-symbols:table-rows',
  },
]

// 路由
const route = useRoute()

// 查询表单
const queryForm = reactive({
  device_code: route.query.device_code || '14323A0041',
  device_name: route.query.device_name || '',
  start_time: route.query.start_time
    ? new Date(route.query.start_time).getTime()
    : new Date(Date.now() - 30 * 60 * 1000).getTime(),
  end_time: route.query.end_time ? new Date(route.query.end_time).getTime() : new Date().getTime(),
})

// 选中的设备ID
const selectedDeviceId = ref('14324G0216')

// 加载状态
const loading = ref(false)

// 历史数据表格列定义
const historyColumns = [
  {
    title: '时间',
    key: 'ts',
    width: 180,
    render: (row) => {
      return formatDateTime(row.ts, 'YYYY-MM-DD HH:mm:ss')
    },
  },
  {
    title: '预设电流',
    key: 'preset_current',
    width: 100,
    render: (row) => {
      return `${row.preset_current}A`
    },
  },
  {
    title: '预设电压',
    key: 'preset_voltage',
    width: 100,
    render: (row) => {
      return `${row.preset_voltage}V`
    },
  },
  {
    title: '焊接电流',
    key: 'weld_current',
    width: 100,
    render: (row) => {
      return `${row.weld_current}A`
    },
  },
  {
    title: '焊接电压',
    key: 'weld_voltage',
    width: 100,
    render: (row) => {
      return `${row.weld_voltage}V`
    },
  },
]

// 模拟历史数据
const historyData = ref([])

// 分页状态
const pagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  showQuickJumper: true,
  itemCount: 0,
  prefix: ({ itemCount }) => `共 ${itemCount} 条`,
  suffix: ({ startIndex, endIndex }) => `显示 ${startIndex}-${endIndex} 条`,
})

// 分页事件处理函数
function handlePageChange(page) {
  isViewModeChanging.value = true
  pagination.page = page
  queryHistoryData().finally(() => {
    isViewModeChanging.value = false
  })
}

function handlePageSizeChange(pageSize) {
  isViewModeChanging.value = true
  pagination.pageSize = pageSize
  pagination.page = 1
  queryHistoryData().finally(() => {
    isViewModeChanging.value = false
  })
}

/**
 * 初始化图表
 */
function initChart() {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const option = {
    title: {
      text: '设备历史参数',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      data: ['预设电流', '预设电压', '焊接电流', '焊接电压'],
      top: 30,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
    },
    yAxis: [
      {
        type: 'value',
        name: '电流(A)',
        position: 'left',
        axisLabel: {
          formatter: '{value}A',
        },
      },
      {
        type: 'value',
        name: '电压(V)',
        position: 'right',
        axisLabel: {
          formatter: '{value}V',
        },
      },
    ],
    series: [
      {
        name: '预设电流',
        type: 'line',
        yAxisIndex: 0,
        data: (historyData.value || []).map((item) => [item.ts, item.preset_current]),
        smooth: true,
        lineStyle: {
          color: '#ff4d4f', // 红色
        },
      },
      {
        name: '焊接电流',
        type: 'line',
        yAxisIndex: 0,
        data: (historyData.value || []).map((item) => [item.ts, item.weld_current]),
        smooth: true,
        lineStyle: {
          color: '#ff7a45', // 橘红色
        },
      },
      {
        name: '预设电压',
        type: 'line',
        yAxisIndex: 1,
        data: (historyData.value || []).map((item) => [item.ts, item.preset_voltage]),
        smooth: true,
        lineStyle: {
          color: '#1890ff', // 蓝色
        },
      },
      {
        name: '焊接电压',
        type: 'line',
        yAxisIndex: 1,
        data: (historyData.value || []).map((item) => [item.ts, item.weld_voltage]),
        smooth: true,
        lineStyle: {
          color: '#40a9ff', // 浅蓝色
        },
      },
    ],
  }

  chartInstance.setOption(option)
}

/**
 * 处理查询
 */
// 查询历史数据
async function queryHistoryData() {
  loading.value = true
  try {
    // 根据视图模式决定查询参数
    const queryParams = {
      device_code: queryForm.device_code,
      start_time: queryForm.start_time,
      end_time: queryForm.end_time,
    }

    if (viewMode.value === 'chart') {
      // 图表模式：使用大的page_size获取所有数据点
      queryParams.limit = 10000
      queryParams.offset = 0

      const response = await deviceDataApi.getDeviceHistoryData(queryParams)
      historyData.value = response.data || []
      // 图表模式下不重置itemCount，保持表格模式的分页状态

      nextTick(() => {
        // 如果图表实例不存在才初始化，避免重复初始化
        if (!chartInstance) {
          initChart()
        }
        updateChart(response.data)
      })
    } else {
      // 表格模式：使用正常分页
      queryParams.limit = pagination.pageSize
      queryParams.offset = (pagination.page - 1) * pagination.pageSize

      const response = await deviceDataApi.getDeviceHistoryData(queryParams)
      // 后端返回SuccessExtra格式: { data, total, page, page_size }
      historyData.value = response.data || []
      pagination.itemCount = response.total || 0
    }
  } catch (error) {
    message.error(`查询失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 处理查询
function handleQuery() {
  pagination.page = 1
  queryHistoryData()
}

// 处理重置
function handleReset() {
  queryForm.device_code = '14324G0216'
  queryForm.device_name = ''
  queryForm.start_time = new Date(Date.now() - 30 * 60 * 1000).getTime()
  queryForm.end_time = new Date().getTime()
  pagination.page = 1
  queryHistoryData()
}

// 标记是否正在切换视图模式，避免重复查询
const isViewModeChanging = ref(false)

// 监听分页变化
watch(
  () => pagination.page,
  () => {
    if (!isViewModeChanging.value) {
      queryHistoryData()
    }
  }
)

// 监听每页显示数量变化
watch(
  () => pagination.pageSize,
  () => {
    if (!isViewModeChanging.value) {
      pagination.page = 1
      queryHistoryData()
    }
  }
)

// 监听视图模式变化
watch(
  () => viewMode.value,
  (newVal) => {
    isViewModeChanging.value = true

    if (newVal === 'chart') {
      // 切换到图表模式时重新查询数据以获取所有数据点
      queryHistoryData().finally(() => {
        isViewModeChanging.value = false
      })
    } else {
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
      // 切换到表格模式时，如果itemCount为0，先重置分页再查询
      if (pagination.itemCount === 0) {
        pagination.page = 1
      }
      queryHistoryData().finally(() => {
        isViewModeChanging.value = false
      })
    }
  }
)

// 初始化数据
onMounted(() => {
  queryHistoryData()
})

// 销毁图表实例
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// 更新图表数据
function updateChart(data) {
  if (!chartInstance || !data || !Array.isArray(data)) return

  // 使用时间戳格式的数据，与初始化时的时间轴保持一致
  const presetCurrentData = data.map((item) => [item.ts, item.preset_current])
  const presetVoltageData = data.map((item) => [item.ts, item.preset_voltage])
  const weldCurrentData = data.map((item) => [item.ts, item.weld_current])
  const weldVoltageData = data.map((item) => [item.ts, item.weld_voltage])

  const option = {
    series: [
      {
        name: '预设电流',
        type: 'line',
        yAxisIndex: 0,
        data: presetCurrentData,
        smooth: true,
        lineStyle: {
          color: '#ff4d4f', // 红色
        },
      },
      {
        name: '焊接电流',
        type: 'line',
        yAxisIndex: 0,
        data: weldCurrentData,
        smooth: true,
        lineStyle: {
          color: '#ff7a45', // 橘红色
        },
      },
      {
        name: '预设电压',
        type: 'line',
        yAxisIndex: 1,
        data: presetVoltageData,
        smooth: true,
        lineStyle: {
          color: '#1890ff', // 蓝色
        },
      },
      {
        name: '焊接电压',
        type: 'line',
        yAxisIndex: 1,
        data: weldVoltageData,
        smooth: true,
        lineStyle: {
          color: '#40a9ff', // 浅蓝色
        },
      },
    ],
  }
  chartInstance.setOption(option)
}

// 导出
// export default {
//   name: '历史数据查询',
// }
</script>

<style scoped>
.query-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.chart-container {
  width: 100%;
  height: 400px;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
