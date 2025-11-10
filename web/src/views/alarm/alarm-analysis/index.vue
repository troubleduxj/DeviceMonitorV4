<template>
  <CommonPage show-footer>
    <!-- 时间范围选择 -->
    <NCard class="mb-15" rounded-10>
      <div class="flex flex-wrap items-center gap-15">
        <QueryBarItem label="时间范围" :label-width="70">
          <NDatePicker
            v-model:value="dateRange"
            type="datetimerange"
            clearable
            format="yyyy-MM-dd HH:mm:ss"
            value-format="timestamp"
            placeholder="请选择时间范围"
            style="width: 300px"
          />
        </QueryBarItem>
        <QueryBarItem label="设备类型" :label-width="70">
          <NSelect
            v-model:value="deviceType"
            :options="deviceTypeOptions"
            placeholder="请选择设备类型"
            clearable
            style="width: 150px"
          />
        </QueryBarItem>
        <div class="ml-20 flex items-center gap-10">
          <NButton type="primary" @click="handleQuery">
            <TheIcon icon="material-symbols:search" :size="16" class="mr-5" />查询
          </NButton>
          <NButton @click="handleReset">
            <TheIcon icon="material-symbols:refresh" :size="16" class="mr-5" />重置
          </NButton>
        </div>
      </div>
    </NCard>

    <!-- 统计卡片 -->
    <NCard class="mb-15" rounded-10>
      <template #header>
        <span>报警统计概览</span>
      </template>
      <div class="grid grid-cols-4 gap-4">
        <div class="stat-card">
          <div class="stat-icon">
            <TheIcon icon="material-symbols:analytics" :size="32" />
          </div>
          <div class="stat-content">
            <div class="stat-value">156</div>
            <div class="stat-label">今日报警</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <TheIcon icon="material-symbols:trending-up" :size="32" />
          </div>
          <div class="stat-content">
            <div class="stat-value">23%</div>
            <div class="stat-label">环比增长</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <TheIcon icon="material-symbols:device-hub" :size="32" />
          </div>
          <div class="stat-content">
            <div class="stat-value">12</div>
            <div class="stat-label">异常设备</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <TheIcon icon="material-symbols:schedule" :size="32" />
          </div>
          <div class="stat-content">
            <div class="stat-value">8.5min</div>
            <div class="stat-label">平均响应时间</div>
          </div>
        </div>
      </div>
    </NCard>

    <!-- 图表分析区域 -->
    <NCard class="mb-15" rounded-10>
      <template #header>
        <span>报警趋势分析</span>
      </template>
      <div class="chart-placeholder">
        <TheIcon icon="material-symbols:bar-chart" :size="64" />
        <p>图表分析功能开发中...</p>
      </div>
    </NCard>
  </CommonPage>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { NCard, NDatePicker, NSelect, NButton } from 'naive-ui'
import TheIcon from '@/components/icon/TheIcon.vue'
import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/page/QueryBarItem.vue'

// 查询参数
const dateRange = ref(null)
const deviceType = ref(null)

// 设备类型选项
const deviceTypeOptions = [
  { label: '全部', value: null },
  { label: '传感器', value: 'sensor' },
  { label: '控制器', value: 'controller' },
  { label: '执行器', value: 'actuator' },
]

// 查询处理
const handleQuery = () => {
  console.log('查询参数:', { dateRange: dateRange.value, deviceType: deviceType.value })
}

// 重置处理
const handleReset = () => {
  dateRange.value = null
  deviceType.value = null
}
</script>

<style scoped>
/* 统计卡片样式 */
.stat-card {
  @apply p-20 bg-white rounded-8 border border-gray-200 hover:shadow-md transition-all duration-300;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  @apply w-48 h-48 rounded-8 flex items-center justify-center text-white;
  background: linear-gradient(135deg, #18a058 0%, #36ad6a 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  @apply text-24 font-600 text-gray-800 mb-4;
}

.stat-label {
  @apply text-14 text-gray-600;
}

/* 图表占位符样式 */
.chart-placeholder {
  @apply h-300 flex items-center justify-center bg-gray-50 rounded-8 text-gray-500;
  flex-direction: column;
  gap: 12px;
}

.chart-placeholder p {
  @apply text-16 m-0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .grid-cols-4 {
    @apply grid-cols-2;
  }
}

@media (max-width: 640px) {
  .grid-cols-4 {
    @apply grid-cols-1;
  }

  .flex-wrap {
    @apply flex-col items-start;
  }

  .ml-20 {
    @apply ml-0 mt-15;
  }
}
</style>
