<script setup lang="ts">
import { h, onMounted, ref, resolveDirective, withDirectives, watch } from 'vue'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NSwitch,
  NTag,
  NPopconfirm,
  NSpace,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NPagination,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/page/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import ViewToggle from '@/components/common/ViewToggle.vue'

import { formatDate, renderIcon } from '@/utils'
import { useCRUD } from '@/composables/useCRUD'

defineOptions({ name: '工作流管理' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')
const viewMode = ref('card') // 视图模式：'card' 或 'table'
const workflowList = ref([]) // 卡片视图的工作流列表
const cardPagination = ref({
  page: 1,
  pageSize: 12,
  total: 0,
})

// 视图切换选项
const viewOptions = [
  {
    value: 'card',
    label: '卡片视图',
    icon: 'material-symbols:grid-view',
  },
  {
    value: 'table',
    label: '表格视图',
    icon: 'material-symbols:table-rows',
  },
]

// 工作流状态选项
const statusOptions = [
  { label: '启用', value: true },
  { label: '禁用', value: false },
]

// 工作流类型选项
const typeOptions = [
  { label: '设备监控流程', value: 'device_monitor' },
  { label: '报警处理流程', value: 'alarm_process' },
  { label: '数据采集流程', value: 'data_collection' },
  { label: '维护保养流程', value: 'maintenance' },
  { label: '自定义流程', value: 'custom' },
]

// 优先级选项
const priorityOptions = [
  { label: '低', value: 'low' },
  { label: '中', value: 'medium' },
  { label: '高', value: 'high' },
  { label: '紧急', value: 'urgent' },
]

const {
  modalVisible,
  modalTitle,
  modalAction,
  modalLoading,
  handleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleDelete,
  handleAdd,
} = useCRUD({
  name: '工作流',
  initForm: {
    name: '',
    description: '',
    type: 'custom',
    priority: 'medium',
    is_active: true,
    config: '{}',
  },
  doCreate: async (data) => {
    // 模拟API调用
    console.log('创建工作流:', data)
    return { code: 200, message: '创建成功' }
  },
  doUpdate: async (data) => {
    // 模拟API调用
    console.log('更新工作流:', data)
    return { code: 200, message: '更新成功' }
  },
  doDelete: async (data) => {
    // 模拟API调用
    console.log('删除工作流:', data)
    return { code: 200, message: '删除成功' }
  },
  refresh: () => $table.value?.handleSearch(),
})

onMounted(() => {
  console.log('工作流管理页面已挂载')
  // 初始加载卡片数据
  if (viewMode.value === 'card') {
    loadWorkflowCards()
  }
})

// 监听视图模式变化
watch(viewMode, (newMode) => {
  if (newMode === 'card') {
    loadWorkflowCards()
  }
})

// 表格列配置
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 60,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '工作流名称',
    key: 'name',
    width: 150,
    align: 'center',
    ellipsis: { tooltip: true },
    render(row) {
      return h(
        'span',
        {
          style: {
            color: row.is_active ? 'var(--n-primary-color)' : 'var(--n-text-color-disabled)',
            fontWeight: '500',
            cursor: 'pointer',
            textDecoration: 'underline',
          },
          onClick: () => handleView(row),
        },
        row.name
      )
    },
  },
  {
    title: '描述',
    key: 'description',
    width: 200,
    align: 'center',
    ellipsis: { tooltip: true },
    render(row) {
      return h(
        'span',
        {
          style: {
            color: row.is_active ? 'var(--n-text-color-2)' : 'var(--n-text-color-disabled)',
          },
        },
        row.description || '暂无描述'
      )
    },
  },
  {
    title: '类型',
    key: 'type',
    width: 120,
    align: 'center',
    render(row) {
      const typeMap = {
        device_monitor: { label: '设备监控', color: 'info' },
        alarm_process: { label: '报警处理', color: 'warning' },
        data_collection: { label: '数据采集', color: 'success' },
        maintenance: { label: '维护保养', color: 'default' },
        custom: { label: '自定义', color: 'primary' },
      }
      const config = typeMap[row.type] || { label: row.type, color: 'default' }
      return h(NTag, { type: config.color, size: 'small' }, { default: () => config.label })
    },
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    align: 'center',
    render(row) {
      const priorityMap = {
        low: { label: '低', color: 'default' },
        medium: { label: '中', color: 'info' },
        high: { label: '高', color: 'warning' },
        urgent: { label: '紧急', color: 'error' },
      }
      const config = priorityMap[row.priority] || { label: row.priority, color: 'default' }
      return h(NTag, { type: config.color, size: 'small' }, { default: () => config.label })
    },
  },
  {
    title: '状态',
    key: 'is_active',
    width: 80,
    align: 'center',
    render(row) {
      return h(NSwitch, {
        size: 'small',
        value: row.is_active,
        checkedValue: true,
        uncheckedValue: false,
        onUpdateValue: () => handleUpdateStatus(row),
      })
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 150,
    align: 'center',
    ellipsis: { tooltip: true },
    render(row) {
      return h(
        'span',
        { style: { fontSize: '12px', color: 'var(--n-text-color-3)' } },
        formatDate(row.created_at)
      )
    },
  },
  {
    title: '更新时间',
    key: 'updated_at',
    width: 150,
    align: 'center',
    ellipsis: { tooltip: true },
    render(row) {
      return h(
        'span',
        { style: { fontSize: '12px', color: 'var(--n-text-color-3)' } },
        formatDate(row.updated_at)
      )
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            style: 'margin-right: 8px;',
            onClick: () => handleEdit(row),
          },
          {
            default: () => '编辑',
            icon: renderIcon('material-symbols:edit', { size: 16 }),
          }
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handleDelete({ id: row.id }, false),
            onNegativeClick: () => {},
          },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  type: 'error',
                },
                {
                  default: () => '删除',
                  icon: renderIcon('material-symbols:delete-outline', { size: 16 }),
                }
              ),
            default: () => h('div', {}, '确定删除该工作流吗？'),
          }
        ),
      ]
    },
  },
]

// 修改工作流状态
async function handleUpdateStatus(row) {
  try {
    row.is_active = !row.is_active
    // 模拟API调用
    console.log('更新工作流状态:', row)
    $message?.success(row.is_active ? '已启用该工作流' : '已禁用该工作流')
    $table.value?.handleSearch()
  } catch (err) {
    // 有异常恢复原来的状态
    row.is_active = !row.is_active
    $message?.error('状态更新失败')
  }
}

// 查看工作流详情
function handleView(row) {
  console.log('查看工作流详情:', row)
  $message.info('查看功能开发中...')
}

// 重置查询条件
function handleReset() {
  queryItems.value = {}
  if (viewMode.value === 'table') {
    $table.value?.handleSearch()
  } else {
    loadWorkflowCards()
  }
}

// 获取类型标签颜色
function getTypeColor(type) {
  const typeMap = {
    device_monitor: 'info',
    alarm_process: 'warning',
    data_collection: 'success',
    maintenance: 'default',
    custom: 'primary',
  }
  return typeMap[type] || 'default'
}

// 获取类型标签文本
function getTypeLabel(type) {
  const typeMap = {
    device_monitor: '设备监控',
    alarm_process: '报警处理',
    data_collection: '数据采集',
    maintenance: '维护保养',
    custom: '自定义',
  }
  return typeMap[type] || type
}

// 获取优先级标签颜色
function getPriorityColor(priority) {
  const priorityMap = {
    low: 'default',
    medium: 'info',
    high: 'warning',
    urgent: 'error',
  }
  return priorityMap[priority] || 'default'
}

// 获取优先级标签文本
function getPriorityLabel(priority) {
  const priorityMap = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急',
  }
  return priorityMap[priority] || priority
}

// 加载卡片视图数据
async function loadWorkflowCards() {
  try {
    const params = {
      page: cardPagination.value.page,
      page_size: cardPagination.value.pageSize,
      ...queryItems.value,
    }
    const result = await getWorkflowListData(params)
    workflowList.value = result.data
    cardPagination.value.total = result.total
  } catch (error) {
    console.error('加载工作流卡片失败:', error)
    workflowList.value = []
  }
}

// 卡片视图分页变化
function handleCardPageChange(page) {
  cardPagination.value.page = page
  loadWorkflowCards()
}

// 卡片视图页面大小变化
function handleCardPageSizeChange(pageSize) {
  cardPagination.value.pageSize = pageSize
  cardPagination.value.page = 1
  loadWorkflowCards()
}

// 获取工作流列表数据
const getWorkflowListData = async (params) => {
  try {
    console.log('获取工作流列表，参数:', params)

    // 模拟数据
    const mockData = [
      {
        id: 1,
        name: '设备状态监控流程',
        description: '实时监控设备运行状态，异常时自动触发报警',
        type: 'device_monitor',
        priority: 'high',
        is_active: true,
        config: JSON.stringify({
          trigger: 'device_status_change',
          actions: ['send_alert', 'log_event'],
          conditions: { status: 'error' },
        }),
        created_at: '2024-01-15 10:30:00',
        updated_at: '2024-01-20 14:20:00',
      },
      {
        id: 2,
        name: '报警处理流程',
        description: '自动处理设备报警，包括通知相关人员和记录处理过程',
        type: 'alarm_process',
        priority: 'urgent',
        is_active: true,
        config: JSON.stringify({
          trigger: 'alarm_received',
          actions: ['notify_admin', 'create_ticket'],
          escalation: { timeout: 300 },
        }),
        created_at: '2024-01-10 09:15:00',
        updated_at: '2024-01-18 16:45:00',
      },
      {
        id: 3,
        name: '数据采集流程',
        description: '定时采集设备数据并存储到数据库',
        type: 'data_collection',
        priority: 'medium',
        is_active: false,
        config: JSON.stringify({
          schedule: '*/5 * * * *',
          sources: ['sensor_1', 'sensor_2'],
          storage: 'database',
        }),
        created_at: '2024-01-05 08:00:00',
        updated_at: '2024-01-15 12:30:00',
      },
      {
        id: 4,
        name: '设备维护提醒流程',
        description: '根据设备使用时间和状态，自动生成维护提醒',
        type: 'maintenance',
        priority: 'low',
        is_active: true,
        config: JSON.stringify({
          schedule: '0 9 * * 1',
          criteria: { runtime_hours: 1000 },
          notification: 'email',
        }),
        created_at: '2024-01-01 00:00:00',
        updated_at: '2024-01-10 10:00:00',
      },
    ]

    // 模拟搜索过滤
    let filteredData = mockData
    if (params.name) {
      filteredData = filteredData.filter((item) =>
        item.name.toLowerCase().includes(params.name.toLowerCase())
      )
    }
    if (params.type) {
      filteredData = filteredData.filter((item) => item.type === params.type)
    }
    if (params.is_active !== undefined && params.is_active !== null) {
      filteredData = filteredData.filter((item) => item.is_active === params.is_active)
    }

    // 模拟分页
    const page = params.page || 1
    const pageSize = params.page_size || 10
    const start = (page - 1) * pageSize
    const end = start + pageSize
    const paginatedData = filteredData.slice(start, end)

    return {
      data: paginatedData,
      total: filteredData.length,
    }
  } catch (err) {
    console.error('获取工作流列表失败:', err)
    return { data: [], total: 0 }
  }
}

// 表单验证规则
const validateWorkflow = {
  name: [
    {
      required: true,
      message: '请输入工作流名称',
      trigger: ['input', 'blur'],
    },
  ],
  type: [
    {
      required: true,
      message: '请选择工作流类型',
      trigger: ['change', 'blur'],
    },
  ],
  priority: [
    {
      required: true,
      message: '请选择优先级',
      trigger: ['change', 'blur'],
    },
  ],
}
</script>

<template>
  <CommonPage show-footer title="工作流管理">
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
        <NButton type="primary" @click="handleAdd">
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建工作流
        </NButton>
      </div>
    </template>

    <!-- 查询条件 -->
    <div class="query-bar mb-4">
      <div class="flex flex-wrap items-center gap-4">
        <QueryBarItem label="名称" :label-width="50">
          <NInput
            v-model:value="queryItems.name"
            clearable
            type="text"
            placeholder="请输入工作流名称"
            style="width: 200px"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="类型" :label-width="50">
          <NSelect
            v-model:value="queryItems.type"
            :options="typeOptions"
            clearable
            placeholder="请选择类型"
            style="width: 180px"
          />
        </QueryBarItem>
        <QueryBarItem label="状态" :label-width="50">
          <NSelect
            v-model:value="queryItems.is_active"
            :options="statusOptions"
            clearable
            placeholder="请选择状态"
            style="width: 120px"
          />
        </QueryBarItem>
        <NButton type="primary" @click="$table?.handleSearch()">
          <TheIcon icon="material-symbols:search" :size="16" class="mr-1" />搜索
        </NButton>
        <NButton @click="handleReset">
          <TheIcon icon="material-symbols:refresh" :size="16" class="mr-1" />重置
        </NButton>
      </div>
    </div>

    <!-- 表格视图 -->
    <CrudTable
      v-if="viewMode === 'table'"
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="getWorkflowListData"
    />

    <!-- 卡片视图 -->
    <div v-else class="workflow-cards">
      <div class="workflow-grid">
        <div v-for="workflow in workflowList" :key="workflow.id" class="workflow-card-item">
          <NCard class="workflow-card" hoverable @click="handleView(workflow)">
            <!-- 状态指示器 -->
            <div
              class="status-indicator"
              :class="`status-indicator--${workflow.is_active ? 'active' : 'inactive'}`"
            ></div>

            <div class="workflow-card-header">
              <div class="workflow-icon-wrapper">
                <TheIcon icon="material-symbols:account-tree" :size="24" class="workflow-icon" />
              </div>
              <div class="workflow-info">
                <h3 class="workflow-title">{{ workflow.name }}</h3>
                <p class="workflow-description">{{ workflow.description || '暂无描述' }}</p>
              </div>
            </div>

            <!-- 工作流标签和状态 -->
            <div class="workflow-tags">
              <NTag :type="getTypeColor(workflow.type)" size="small" :bordered="false">
                {{ getTypeLabel(workflow.type) }}
              </NTag>
              <NTag :type="getPriorityColor(workflow.priority)" size="small" :bordered="false">
                {{ getPriorityLabel(workflow.priority) }}
              </NTag>
            </div>

            <!-- 工作流操作按钮 -->
            <div class="workflow-actions">
              <NButton size="small" type="primary" ghost @click.stop="handleEdit(workflow)">
                <TheIcon icon="material-symbols:edit" :size="14" class="mr-1" />
                编辑
              </NButton>
              <NSwitch
                :value="workflow.is_active"
                size="small"
                @update:value="() => handleUpdateStatus(workflow)"
                @click.stop
              />
            </div>
          </NCard>
        </div>
      </div>

      <!-- 卡片视图分页 -->
      <div class="workflow-pagination">
        <NPagination
          v-model:page="cardPagination.page"
          :page-size="cardPagination.pageSize"
          :item-count="cardPagination.total"
          :show-size-picker="true"
          :page-sizes="[12, 24, 48]"
          @update:page="handleCardPageChange"
          @update:page-size="handleCardPageSizeChange"
        />
      </div>
    </div>

    <!-- 新增/编辑 弹窗 -->
    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      width="600px"
      @save="handleSave"
    >
      <NForm
        ref="modalFormRef"
        label-placement="left"
        label-align="left"
        :label-width="100"
        :model="modalForm"
        :rules="validateWorkflow"
      >
        <NFormItem label="工作流名称" path="name">
          <NInput v-model:value="modalForm.name" clearable placeholder="请输入工作流名称" />
        </NFormItem>
        <NFormItem label="描述" path="description">
          <NInput
            v-model:value="modalForm.description"
            type="textarea"
            clearable
            placeholder="请输入工作流描述"
            :rows="3"
          />
        </NFormItem>
        <NFormItem label="类型" path="type">
          <NSelect
            v-model:value="modalForm.type"
            :options="typeOptions"
            placeholder="请选择工作流类型"
          />
        </NFormItem>
        <NFormItem label="优先级" path="priority">
          <NSelect
            v-model:value="modalForm.priority"
            :options="priorityOptions"
            placeholder="请选择优先级"
          />
        </NFormItem>
        <NFormItem label="状态" path="is_active">
          <NSwitch
            v-model:value="modalForm.is_active"
            :checked-value="true"
            :unchecked-value="false"
          >
            <template #checked>启用</template>
            <template #unchecked>禁用</template>
          </NSwitch>
        </NFormItem>
        <NFormItem label="配置" path="config">
          <NInput
            v-model:value="modalForm.config"
            type="textarea"
            clearable
            placeholder="请输入JSON格式的配置信息"
            :rows="6"
          />
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>

<style scoped>
/* 查询条件样式 */
.query-bar {
  background: var(--n-card-color);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--n-border-color);
}

/* 卡片网格布局 */
.workflow-cards {
  margin-top: 16px;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.workflow-card-item {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.workflow-card-item:hover {
  transform: translateY(-2px);
}

/* 工作流卡片样式 - 现代化设计 */
.workflow-card {
  position: relative;
  border: 1px solid var(--n-border-color);
  border-radius: 12px;
  background: var(--n-card-color);
  transition: all 0.3s ease;
  overflow: hidden;
  border-left: 4px solid #e0e0e0;
}

.workflow-card:hover {
  border-color: var(--n-primary-color);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 状态指示器 */
.status-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  z-index: 10;
}

.status-indicator--active {
  background-color: #18a058;
  animation: pulse-green 2s infinite;
}

.status-indicator--inactive {
  background-color: #909399;
  animation: none;
}

/* 绿色闪烁动画 */
@keyframes pulse-green {
  0% {
    box-shadow: 0 0 0 0 rgba(24, 160, 88, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(24, 160, 88, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(24, 160, 88, 0);
  }
}

/* 卡片头部 */
.workflow-card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.workflow-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  flex-shrink: 0;
}

.workflow-icon {
  color: white;
}

.workflow-info {
  flex: 1;
  min-width: 0;
}

.workflow-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--n-text-color-1);
  margin: 0 0 6px 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.workflow-description {
  font-size: 13px;
  color: var(--n-text-color-2);
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 工作流标签 */
.workflow-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

/* 工作流操作 */
.workflow-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--n-divider-color);
}

/* 分页样式 */
.workflow-pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding: 24px 0;
  border-top: 1px solid var(--n-divider-color);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .workflow-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .workflow-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .workflow-card-header {
    gap: 10px;
  }

  .workflow-icon-wrapper {
    width: 36px;
    height: 36px;
  }

  .workflow-title {
    font-size: 15px;
  }

  .workflow-description {
    font-size: 12px;
  }

  .workflow-actions {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }

  .workflow-pagination {
    margin-top: 24px;
    padding: 16px 0;
  }

  .query-bar .flex {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .query-bar .flex > * {
    width: 100%;
  }
}

/* 暗色主题适配 */
.dark .workflow-card {
  background: var(--n-card-color);
  border-color: var(--n-border-color);
}

.dark .workflow-card:hover {
  border-color: var(--n-primary-color);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.1);
}

/* 加载状态 */
.workflow-cards.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* 空状态 */
.workflow-empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--n-text-color-3);
}

.workflow-empty .empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.workflow-empty .empty-text {
  font-size: 16px;
  margin-bottom: 8px;
}

.workflow-empty .empty-description {
  font-size: 14px;
  opacity: 0.7;
}
</style>
