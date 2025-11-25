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
import { ref, reactive, onMounted, onBeforeUnmount, nextTick, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, NCard, NInput, NDatePicker, NDataTable, NPagination, useMessage, NSelect } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/page/QueryBarItem.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import ViewToggle from '@/components/common/ViewToggle.vue'
import { formatDate, formatDateTime } from '@/utils'
import * as echarts from 'echarts'
import { compatibilityApi as deviceDataApi } from '@/api/device-v2'
import { deviceFieldApi } from '@/api/device-field'
import type { DeviceField } from '@/api/device-field'
import { useDeviceFieldStore } from '@/store/modules/device-field'

// 页面名称
defineOptions({ name: '历史数据查询' })

// 消息提示
const message = useMessage()

// 设备字段 Store
const deviceFieldStore = useDeviceFieldStore()

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
  device_type_code: route.query.device_type_code || '', // 设备类型代码
  start_time: route.query.start_time
    ? new Date(route.query.start_time).getTime()
    : new Date(Date.now() - 24 * 60 * 60 * 1000).getTime(), // 默认查询最近24小时
  end_time: route.query.end_time ? new Date(route.query.end_time).getTime() : new Date().getTime(),
})

// 选中的设备ID
const selectedDeviceId = ref('14324G0216')

// 加载状态
const loading = ref(false)

// 设备类型字段配置
const deviceFields = ref<DeviceField[]>([])

// 动态生成表格列
const historyColumns = computed(() => {
  const columns = [
    {
      title: '时间',
      key: 'ts',
      width: 180,
      fixed: 'left' as const,
      render: (row: any) => {
        return formatDateTime(row.ts, 'YYYY-MM-DD HH:mm:ss')
      },
    },
  ]

  // 根据设备字段配置动态添加列
  if (deviceFields.value && deviceFields.value.length > 0) {
    deviceFields.value.forEach((field) => {
      columns.push({
        title: field.field_name,
        key: field.field_code,
        width: 120,
        render: (row: any) => {
          const value = row[field.field_code]
          if (value === null || value === undefined) {
            return '-'
          }
          return field.unit ? `${value}${field.unit}` : value
        },
      })
    })
  } else {
    // 如果没有字段配置，使用默认列（兼容旧数据）
    columns.push(
      {
        title: '预设电流',
        key: 'preset_current',
        width: 100,
        render: (row: any) => {
          return row.preset_current ? `${row.preset_current}A` : '-'
        },
      },
      {
        title: '预设电压',
        key: 'preset_voltage',
        width: 100,
        render: (row: any) => {
          return row.preset_voltage ? `${row.preset_voltage}V` : '-'
        },
      },
      {
        title: '焊接电流',
        key: 'weld_current',
        width: 100,
        render: (row: any) => {
          return row.weld_current ? `${row.weld_current}A` : '-'
        },
      },
      {
        title: '焊接电压',
        key: 'weld_voltage',
        width: 100,
        render: (row: any) => {
          return row.weld_voltage ? `${row.weld_voltage}V` : '-'
        },
      }
    )
  }

  return columns
})

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

  // 根据设备字段配置动态生成图表
  const legendData: string[] = []
  const series: any[] = []
  const yAxisConfig: any[] = []

  if (deviceFields.value && deviceFields.value.length > 0) {
    // 按字段类型分组（用于多Y轴）
    const fieldsByUnit = new Map<string, DeviceField[]>()
    deviceFields.value.forEach((field) => {
      const unit = field.unit || '无单位'
      if (!fieldsByUnit.has(unit)) {
        fieldsByUnit.set(unit, [])
      }
      fieldsByUnit.get(unit)!.push(field)
    })

    // 为每个单位创建一个Y轴
    let yAxisIndex = 0
    const colors = ['#ff4d4f', '#1890ff', '#52c41a', '#faad14', '#722ed1', '#eb2f96']
    let colorIndex = 0

    fieldsByUnit.forEach((fields, unit) => {
      // 创建Y轴
      yAxisConfig.push({
        type: 'value',
        name: unit !== '无单位' ? unit : '',
        position: yAxisIndex % 2 === 0 ? 'left' : 'right',
        offset: Math.floor(yAxisIndex / 2) * 60,
        axisLabel: {
          formatter: unit !== '无单位' ? `{value}${unit}` : '{value}',
        },
      })

      // 为该单位的每个字段创建一条线
      fields.forEach((field) => {
        legendData.push(field.field_name)
        series.push({
          name: field.field_name,
          type: 'line',
          yAxisIndex: yAxisIndex,
          data: (historyData.value || []).map((item: any) => [item.ts, item[field.field_code]]),
          smooth: true,
          lineStyle: {
            color: colors[colorIndex % colors.length],
          },
        })
        colorIndex++
      })

      yAxisIndex++
    })
  } else {
    // 默认配置（兼容旧数据）
    legendData.push('预设电流', '预设电压', '焊接电流', '焊接电压')
    yAxisConfig.push(
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
      }
    )
    series.push(
      {
        name: '预设电流',
        type: 'line',
        yAxisIndex: 0,
        data: (historyData.value || []).map((item: any) => [item.ts, item.preset_current]),
        smooth: true,
        lineStyle: {
          color: '#ff4d4f',
        },
      },
      {
        name: '焊接电流',
        type: 'line',
        yAxisIndex: 0,
        data: (historyData.value || []).map((item: any) => [item.ts, item.weld_current]),
        smooth: true,
        lineStyle: {
          color: '#ff7a45',
        },
      },
      {
        name: '预设电压',
        type: 'line',
        yAxisIndex: 1,
        data: (historyData.value || []).map((item: any) => [item.ts, item.preset_voltage]),
        smooth: true,
        lineStyle: {
          color: '#1890ff',
        },
      },
      {
        name: '焊接电压',
        type: 'line',
        yAxisIndex: 1,
        data: (historyData.value || []).map((item: any) => [item.ts, item.weld_voltage]),
        smooth: true,
        lineStyle: {
          color: '#40a9ff',
        },
      }
    )
  }

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
      data: legendData,
      top: 30,
      type: 'scroll',
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
    yAxis: yAxisConfig,
    series: series,
  }

  chartInstance.setOption(option)
}

/**
 * 处理查询
 */
/**
 * 加载设备字段配置
 */
async function loadDeviceFields() {
  if (!queryForm.device_type_code) {
    console.warn('⚠️ 未指定设备类型代码，无法加载字段配置')
    return
  }

  try {
    console.log(`📋 加载设备类型字段配置: ${queryForm.device_type_code}`)
    const fields = await deviceFieldStore.getMonitoringFields(queryForm.device_type_code)
    
    // 只显示监测关键字段
    deviceFields.value = fields.filter((f) => f.is_monitoring_key && f.is_active)
    
    console.log(`✅ 加载到 ${deviceFields.value.length} 个监测字段`)
  } catch (error) {
    console.error('❌ 加载设备字段配置失败:', error)
    // 失败时使用空数组，会回退到默认列
    deviceFields.value = []
  }
}

// 查询历史数据
async function queryHistoryData() {
  loading.value = true
  try {
    // 先加载字段配置
    await loadDeviceFields()

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
      console.log('📊 图表模式 - API响应:', response)
      console.log('📊 图表模式 - 响应数据类型:', typeof response)
      console.log('📊 图表模式 - 响应数据结构:', Object.keys(response))
      
      // 处理响应数据 - 兼容不同的响应格式
      let dataArray = []
      if (Array.isArray(response)) {
        dataArray = response
      } else if (response.data && Array.isArray(response.data)) {
        dataArray = response.data
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        dataArray = response.data.data
      }
      
      console.log('📊 图表模式 - 提取的数据数组:', dataArray)
      console.log('📊 图表模式 - 数据数量:', dataArray.length)
      
      historyData.value = dataArray
      // 图表模式下不重置itemCount，保持表格模式的分页状态

      nextTick(() => {
        // 如果图表实例不存在才初始化，避免重复初始化
        if (!chartInstance) {
          initChart()
        }
        updateChart(dataArray)
      })
    } else {
      // 表格模式：使用正常分页
      queryParams.limit = pagination.pageSize
      queryParams.offset = (pagination.page - 1) * pagination.pageSize

      const response = await deviceDataApi.getDeviceHistoryData(queryParams)
      console.log('📋 表格模式 - API响应:', response)
      console.log('📋 表格模式 - 响应数据类型:', typeof response)
      console.log('📋 表格模式 - 响应数据结构:', Object.keys(response))
      
      // 处理响应数据 - 兼容不同的响应格式
      let dataArray = []
      let total = 0
      
      if (Array.isArray(response)) {
        dataArray = response
        total = response.length
      } else if (response.data && Array.isArray(response.data)) {
        dataArray = response.data
        total = response.total || response.data.length
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        dataArray = response.data.data
        total = response.data.total || response.data.data.length
      }
      
      console.log('📋 表格模式 - 提取的数据数组:', dataArray)
      console.log('📋 表格模式 - 数据数量:', dataArray.length)
      console.log('📋 表格模式 - 总数:', total)
      
      historyData.value = dataArray
      pagination.itemCount = total
    }
  } catch (error) {
    console.error('❌ 查询历史数据失败:', error)
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
function updateChart(data: any[]) {
  if (!chartInstance || !data || !Array.isArray(data)) return

  const series: any[] = []
  const colors = ['#ff4d4f', '#1890ff', '#52c41a', '#faad14', '#722ed1', '#eb2f96']
  let colorIndex = 0

  if (deviceFields.value && deviceFields.value.length > 0) {
    // 按字段类型分组（用于多Y轴）
    const fieldsByUnit = new Map<string, DeviceField[]>()
    deviceFields.value.forEach((field) => {
      const unit = field.unit || '无单位'
      if (!fieldsByUnit.has(unit)) {
        fieldsByUnit.set(unit, [])
      }
      fieldsByUnit.get(unit)!.push(field)
    })

    let yAxisIndex = 0
    fieldsByUnit.forEach((fields) => {
      fields.forEach((field) => {
        series.push({
          name: field.field_name,
          type: 'line',
          yAxisIndex: yAxisIndex,
          data: data.map((item) => [item.ts, item[field.field_code]]),
          smooth: true,
          lineStyle: {
            color: colors[colorIndex % colors.length],
          },
        })
        colorIndex++
      })
      yAxisIndex++
    })
  } else {
    // 默认配置（兼容旧数据）
    series.push(
      {
        name: '预设电流',
        type: 'line',
        yAxisIndex: 0,
        data: data.map((item) => [item.ts, item.preset_current]),
        smooth: true,
        lineStyle: {
          color: '#ff4d4f',
        },
      },
      {
        name: '焊接电流',
        type: 'line',
        yAxisIndex: 0,
        data: data.map((item) => [item.ts, item.weld_current]),
        smooth: true,
        lineStyle: {
          color: '#ff7a45',
        },
      },
      {
        name: '预设电压',
        type: 'line',
        yAxisIndex: 1,
        data: data.map((item) => [item.ts, item.preset_voltage]),
        smooth: true,
        lineStyle: {
          color: '#1890ff',
        },
      },
      {
        name: '焊接电压',
        type: 'line',
        yAxisIndex: 1,
        data: data.map((item) => [item.ts, item.weld_voltage]),
        smooth: true,
        lineStyle: {
          color: '#40a9ff',
        },
      }
    )
  }

  const option = {
    series: series,
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
