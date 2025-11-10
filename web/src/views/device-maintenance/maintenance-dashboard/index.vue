<template>
  <div class="maintenance-dashboard">
    <!-- 页面标题 -->
    <div class="dashboard-header">
      <n-page-header title="设备维护看板" subtitle="实时监控设备维护状态和统计信息">
        <template #extra>
          <n-space>
            <n-button type="primary" @click="refreshData">
              <template #icon>
                <n-icon><RefreshIcon /></n-icon>
              </template>
              刷新数据
            </n-button>
            <n-button @click="exportReport">
              <template #icon>
                <n-icon><DownloadIcon /></n-icon>
              </template>
              导出报告
            </n-button>
          </n-space>
        </template>
      </n-page-header>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <n-grid :cols="4" :x-gap="16" :y-gap="16">
        <n-grid-item>
          <n-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <n-icon size="32"><DeviceIcon /></n-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ totalDevices }}</div>
                <div class="stat-label">设备总数</div>
              </div>
            </div>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon normal">
                <n-icon size="32"><CheckCircleIcon /></n-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ normalDevices }}</div>
                <div class="stat-label">正常设备</div>
              </div>
            </div>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon warning">
                <n-icon size="32"><WarningIcon /></n-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ warningDevices }}</div>
                <div class="stat-label">预警设备</div>
              </div>
            </div>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon error">
                <n-icon size="32"><CloseCircleIcon /></n-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ errorDevices }}</div>
                <div class="stat-label">故障设备</div>
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>

    <!-- 图表和数据展示区域 -->
    <div class="charts-section">
      <n-grid :cols="2" :x-gap="16" :y-gap="16">
        <!-- 设备状态分布图 -->
        <n-grid-item>
          <n-card title="设备状态分布" class="chart-card">
            <div class="chart-container">
              <div class="pie-chart-placeholder">
                <div class="chart-legend">
                  <div class="legend-item">
                    <span class="legend-color normal"></span>
                    <span>正常 ({{ normalDevices }})</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color warning"></span>
                    <span>预警 ({{ warningDevices }})</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color error"></span>
                    <span>故障 ({{ errorDevices }})</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color maintenance"></span>
                    <span>维护中 ({{ maintenanceDevices }})</span>
                  </div>
                </div>
              </div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 维护趋势图 -->
        <n-grid-item>
          <n-card title="维护趋势" class="chart-card">
            <div class="chart-container">
              <div class="line-chart-placeholder">
                <div class="trend-data">
                  <div v-for="item in maintenanceTrend" :key="item.month" class="trend-item">
                    <div class="trend-bar" :style="{ height: item.height }"></div>
                    <div class="trend-label">{{ item.month }}</div>
                  </div>
                </div>
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>

    <!-- 维护记录和任务区域 -->
    <div class="records-section">
      <n-grid :cols="2" :x-gap="16" :y-gap="16">
        <!-- 最近维护记录 -->
        <n-grid-item>
          <n-card title="最近维护记录" class="records-card">
            <template #header-extra>
              <n-button text @click="viewAllRecords">查看全部</n-button>
            </template>
            <n-list>
              <n-list-item v-for="record in recentRecords" :key="record.id">
                <div class="record-item">
                  <div class="record-header">
                    <span class="device-name">{{ record.deviceName }}</span>
                    <n-tag :type="getRecordType(record.status)" size="small">
                      {{ record.status }}
                    </n-tag>
                  </div>
                  <div class="record-details">
                    <div class="record-info">
                      <span class="record-type">{{ record.type }}</span>
                      <span class="record-date">{{ record.date }}</span>
                    </div>
                    <div class="record-description">{{ record.description }}</div>
                  </div>
                </div>
              </n-list-item>
            </n-list>
          </n-card>
        </n-grid-item>

        <!-- 待处理任务 -->
        <n-grid-item>
          <n-card title="待处理任务" class="tasks-card">
            <template #header-extra>
              <n-button text @click="viewAllTasks">查看全部</n-button>
            </template>
            <n-list>
              <n-list-item v-for="task in pendingTasks" :key="task.id">
                <div class="task-item">
                  <div class="task-header">
                    <span class="task-title">{{ task.title }}</span>
                    <n-tag :type="getPriorityType(task.priority)" size="small">
                      {{ task.priority }}
                    </n-tag>
                  </div>
                  <div class="task-details">
                    <div class="task-info">
                      <span class="task-device">{{ task.deviceName }}</span>
                      <span class="task-deadline">截止: {{ task.deadline }}</span>
                    </div>
                    <div class="task-assignee">负责人: {{ task.assignee }}</div>
                  </div>
                </div>
              </n-list-item>
            </n-list>
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>

    <!-- 设备健康度排行 -->
    <div class="health-section">
      <n-card title="设备健康度排行" class="health-card">
        <n-grid :cols="3" :x-gap="16">
          <n-grid-item>
            <div class="health-category">
              <h4>健康度最高</h4>
              <div class="health-list">
                <div v-for="device in topHealthDevices" :key="device.id" class="health-item">
                  <div class="device-info">
                    <span class="device-name">{{ device.name }}</span>
                    <span class="device-location">{{ device.location }}</span>
                  </div>
                  <div class="good health-score">{{ device.health }}%</div>
                </div>
              </div>
            </div>
          </n-grid-item>

          <n-grid-item>
            <div class="health-category">
              <h4>需要关注</h4>
              <div class="health-list">
                <div v-for="device in attentionDevices" :key="device.id" class="health-item">
                  <div class="device-info">
                    <span class="device-name">{{ device.name }}</span>
                    <span class="device-location">{{ device.location }}</span>
                  </div>
                  <div class="health-score warning">{{ device.health }}%</div>
                </div>
              </div>
            </div>
          </n-grid-item>

          <n-grid-item>
            <div class="health-category">
              <h4>紧急处理</h4>
              <div class="health-list">
                <div v-for="device in urgentDevices" :key="device.id" class="health-item">
                  <div class="device-info">
                    <span class="device-name">{{ device.name }}</span>
                    <span class="device-location">{{ device.location }}</span>
                  </div>
                  <div class="health-score error">{{ device.health }}%</div>
                </div>
              </div>
            </div>
          </n-grid-item>
        </n-grid>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  NPageHeader,
  NCard,
  NGrid,
  NGridItem,
  NButton,
  NSpace,
  NIcon,
  NList,
  NListItem,
  NTag,
  useMessage,
} from 'naive-ui'
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Desktop as DeviceIcon,
  CheckmarkCircle as CheckCircleIcon,
  Warning as WarningIcon,
  CloseCircle as CloseCircleIcon,
} from '@vicons/ionicons5'

const message = useMessage()

// 静态数据
const totalDevices = ref(156)
const normalDevices = ref(128)
const warningDevices = ref(18)
const errorDevices = ref(7)
const maintenanceDevices = ref(3)

// 维护趋势数据
const maintenanceTrend = ref([
  { month: '1月', count: 12, height: '60%' },
  { month: '2月', count: 8, height: '40%' },
  { month: '3月', count: 15, height: '75%' },
  { month: '4月', count: 20, height: '100%' },
  { month: '5月', count: 18, height: '90%' },
  { month: '6月', count: 14, height: '70%' },
])

// 最近维护记录
const recentRecords = ref([
  {
    id: 1,
    deviceName: '生产线A-设备001',
    status: '已完成',
    type: '定期保养',
    date: '2024-01-15',
    description: '更换滤芯，检查传动系统',
  },
  {
    id: 2,
    deviceName: '包装机B-002',
    status: '进行中',
    type: '故障维修',
    date: '2024-01-14',
    description: '传感器故障，正在更换部件',
  },
  {
    id: 3,
    deviceName: '检测设备C-003',
    status: '已完成',
    type: '升级维护',
    date: '2024-01-13',
    description: '软件升级，校准精度',
  },
  {
    id: 4,
    deviceName: '输送带D-004',
    status: '待处理',
    type: '预防性维护',
    date: '2024-01-12',
    description: '润滑保养，检查磨损情况',
  },
])

// 待处理任务
const pendingTasks = ref([
  {
    id: 1,
    title: '生产线A设备年检',
    deviceName: '生产线A-设备001',
    priority: '高',
    deadline: '2024-01-20',
    assignee: '张工程师',
  },
  {
    id: 2,
    title: '包装机传感器更换',
    deviceName: '包装机B-002',
    priority: '紧急',
    deadline: '2024-01-16',
    assignee: '李技师',
  },
  {
    id: 3,
    title: '检测设备校准',
    deviceName: '检测设备C-003',
    priority: '中',
    deadline: '2024-01-25',
    assignee: '王师傅',
  },
  {
    id: 4,
    title: '输送带保养',
    deviceName: '输送带D-004',
    priority: '低',
    deadline: '2024-01-30',
    assignee: '赵技师',
  },
])

// 设备健康度数据
const topHealthDevices = ref([
  { id: 1, name: '生产线A-001', location: '车间1', health: 98 },
  { id: 2, name: '检测设备B-002', location: '车间2', health: 96 },
  { id: 3, name: '包装机C-003', location: '车间3', health: 94 },
])

const attentionDevices = ref([
  { id: 4, name: '输送带D-004', location: '车间1', health: 75 },
  { id: 5, name: '压缩机E-005', location: '车间2', health: 72 },
  { id: 6, name: '冷却系统F-006', location: '车间3', health: 68 },
])

const urgentDevices = ref([
  { id: 7, name: '焊接机G-007', location: '车间1', health: 45 },
  { id: 8, name: '切割机H-008', location: '车间2', health: 38 },
  { id: 9, name: '打磨机I-009', location: '车间3', health: 32 },
])

// 方法
const refreshData = () => {
  message.success('数据刷新成功')
}

const exportReport = () => {
  message.info('正在导出维护报告...')
}

const viewAllRecords = () => {
  message.info('跳转到维护记录页面')
}

const viewAllTasks = () => {
  message.info('跳转到任务管理页面')
}

const getRecordType = (status) => {
  const typeMap = {
    已完成: 'success',
    进行中: 'warning',
    待处理: 'info',
  }
  return typeMap[status] || 'default'
}

const getPriorityType = (priority) => {
  const typeMap = {
    紧急: 'error',
    高: 'warning',
    中: 'info',
    低: 'default',
  }
  return typeMap[priority] || 'default'
}
</script>

<style scoped>
.maintenance-dashboard {
  padding: 16px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.dashboard-header {
  margin-bottom: 24px;
  background: white;
  border-radius: 8px;
  padding: 16px;
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.normal {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.error {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  height: 300px;
}

.chart-container {
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-chart-placeholder {
  text-align: center;
}

.chart-legend {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-color.normal {
  background: #52c41a;
}

.legend-color.warning {
  background: #faad14;
}

.legend-color.error {
  background: #ff4d4f;
}

.legend-color.maintenance {
  background: #1890ff;
}

.line-chart-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trend-data {
  display: flex;
  align-items: end;
  gap: 20px;
  height: 150px;
}

.trend-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.trend-bar {
  width: 30px;
  background: linear-gradient(to top, #1890ff, #40a9ff);
  border-radius: 4px 4px 0 0;
  min-height: 20px;
}

.trend-label {
  font-size: 12px;
  color: #666;
}

.records-section {
  margin-bottom: 24px;
}

.records-card,
.tasks-card {
  height: 400px;
}

.record-item,
.task-item {
  width: 100%;
}

.record-header,
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.device-name,
.task-title {
  font-weight: 500;
  color: #333;
}

.record-details,
.task-details {
  color: #666;
  font-size: 14px;
}

.record-info,
.task-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.record-description,
.task-assignee {
  font-size: 13px;
  color: #999;
}

.health-section {
  margin-bottom: 24px;
}

.health-card {
  min-height: 300px;
}

.health-category h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.health-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.health-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  border-left: 4px solid #e0e0e0;
}

.device-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.device-name {
  font-weight: 500;
  color: #333;
}

.device-location {
  font-size: 12px;
  color: #999;
}

.health-score {
  font-weight: bold;
  font-size: 18px;
  padding: 4px 8px;
  border-radius: 4px;
}

.health-score.good {
  color: #52c41a;
  background: #f6ffed;
}

.health-score.warning {
  color: #faad14;
  background: #fffbe6;
}

.health-score.error {
  color: #ff4d4f;
  background: #fff2f0;
}
</style>
