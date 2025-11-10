<template>
  <div class="field-management">
    <!-- 查询条件 -->
    <n-card :bordered="false" class="mb-4">
      <n-space>
        <n-select
          v-model:value="queryParams.device_type_code"
          placeholder="选择设备类型"
          clearable
          style="width: 200px"
          :options="deviceTypeOptions"
        />
        
        <n-select
          v-model:value="queryParams.field_category"
          placeholder="选择字段分类"
          clearable
          style="width: 180px"
          :options="fieldCategoryOptions"
        />
        
        <n-input
          v-model:value="queryParams.search"
          placeholder="搜索字段名称或代码"
          clearable
          style="width: 250px"
        >
          <template #prefix>
            <n-icon :component="SearchOutline" />
          </template>
        </n-input>
        
        <n-button type="primary" @click="handleQuery">
          <template #icon>
            <n-icon :component="SearchOutline" />
          </template>
          查询
        </n-button>
        
        <n-button @click="handleReset">
          <template #icon>
            <n-icon :component="RefreshOutline" />
          </template>
          重置
        </n-button>
        
        <n-button type="success" @click="handleCreate">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          新建字段
        </n-button>
        
        <n-button type="info" @click="handleSyncFromTDengine">
          <template #icon>
            <n-icon :component="CloudDownloadOutline" />
          </template>
          从TDengine同步
        </n-button>
      </n-space>
    </n-card>

    <!-- 字段列表 -->
    <n-card :bordered="false">
      <n-data-table
        :columns="columns"
        :data="fieldList"
        :loading="loading"
        :pagination="pagination"
        :row-key="row => row.id"
      />
    </n-card>

    <!-- 新建/编辑字段对话框 -->
    <n-modal
      v-model:show="showFieldModal"
      :title="fieldModalTitle"
      preset="card"
      style="width: 800px"
    >
      <n-form
        ref="fieldFormRef"
        :model="fieldFormData"
        :rules="fieldFormRules"
        label-placement="left"
        label-width="120px"
      >
        <n-form-item label="设备类型" path="device_type_code">
          <n-select
            v-model:value="fieldFormData.device_type_code"
            placeholder="选择设备类型"
            :options="deviceTypeOptions"
          />
        </n-form-item>
        
        <n-form-item label="字段名称" path="field_name">
          <n-input v-model:value="fieldFormData.field_name" placeholder="请输入字段中文名称" />
        </n-form-item>
        
        <n-form-item label="字段代码" path="field_code">
          <n-input v-model:value="fieldFormData.field_code" placeholder="请输入字段代码（英文）" />
        </n-form-item>
        
        <n-form-item label="字段类型" path="field_type">
          <n-select
            v-model:value="fieldFormData.field_type"
            placeholder="选择字段类型"
            :options="fieldTypeOptions"
          />
        </n-form-item>
        
        <n-form-item label="字段分类" path="field_category">
          <n-select
            v-model:value="fieldFormData.field_category"
            placeholder="选择字段分类"
            :options="fieldCategoryOptions"
          />
        </n-form-item>
        
        <n-form-item label="单位">
          <n-input v-model:value="fieldFormData.unit" placeholder="如：A、V、℃" />
        </n-form-item>
        
        <n-form-item label="字段描述">
          <n-input
            v-model:value="fieldFormData.description"
            type="textarea"
            placeholder="请输入字段描述"
            :rows="3"
          />
        </n-form-item>
        
        <n-form-item label="监控关键字段">
          <n-switch v-model:value="fieldFormData.is_monitoring_key" />
        </n-form-item>
        
        <n-form-item label="AI特征字段">
          <n-switch v-model:value="fieldFormData.is_ai_feature" />
        </n-form-item>
      </n-form>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="showFieldModal = false">取消</n-button>
          <n-button type="primary" @click="handleSaveField" :loading="saving">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- TDengine同步对话框 -->
    <n-modal
      v-model:show="showSyncModal"
      title="从TDengine同步字段"
      preset="card"
      style="width: 900px"
    >
      <n-steps :current="syncStep" :status="syncStatus">
        <n-step title="配置参数" />
        <n-step title="预览字段" />
        <n-step title="执行同步" />
      </n-steps>
      
      <!-- 步骤1: 配置参数 -->
      <div v-show="syncStep === 1" class="mt-4">
        <n-form
          ref="syncFormRef"
          :model="syncFormData"
          :rules="syncFormRules"
          label-placement="left"
          label-width="140px"
        >
          <n-form-item label="设备类型" path="device_type_code">
            <n-select
              v-model:value="syncFormData.device_type_code"
              placeholder="选择设备类型"
              :options="deviceTypeOptions"
            />
          </n-form-item>
          
          <n-form-item label="TDengine数据库" path="tdengine_database">
            <n-input
              v-model:value="syncFormData.tdengine_database"
              placeholder="如：device_monitor"
            />
          </n-form-item>
          
          <n-form-item label="TDengine超级表" path="tdengine_stable">
            <n-input
              v-model:value="syncFormData.tdengine_stable"
              placeholder="如：weld_data"
            />
          </n-form-item>
          
          <n-form-item label="字段分类">
            <n-select
              v-model:value="syncFormData.field_category"
              placeholder="选择字段分类"
              :options="fieldCategoryOptions"
            />
          </n-form-item>
        </n-form>
      </div>
      
      <!-- 步骤2: 预览字段 -->
      <div v-show="syncStep === 2" class="mt-4">
        <n-alert type="info" class="mb-4">
          <template #header>
            预览结果
          </template>
          将创建 <strong>{{ previewResult.new_fields }}</strong> 个新字段，
          跳过 <strong>{{ previewResult.existing_fields }}</strong> 个已存在字段，
          忽略 <strong>{{ previewResult.skip_fields }}</strong> 个系统字段
        </n-alert>
        
        <n-data-table
          :columns="previewColumns"
          :data="previewResult.fields"
          :max-height="400"
          :pagination="false"
        />
      </div>
      
      <!-- 步骤3: 同步结果 -->
      <div v-show="syncStep === 3" class="mt-4">
        <n-result
          :status="syncStatus === 'error' ? 'error' : 'success'"
          :title="syncResultTitle"
          :description="syncResultDescription"
        >
          <template #footer>
            <n-collapse>
              <n-collapse-item title="查看详情">
                <n-tabs type="line">
                  <n-tab-pane name="created" :tab="`已创建 (${syncResult.created?.length || 0})`">
                    <n-list>
                      <n-list-item v-for="field in syncResult.created" :key="field.field_code">
                        <n-thing :title="field.field_code" :description="field.field_name">
                          <template #description>
                            {{ field.field_name }} | 类型: {{ field.field_type }}
                          </template>
                        </n-thing>
                      </n-list-item>
                    </n-list>
                  </n-tab-pane>
                  
                  <n-tab-pane name="skipped" :tab="`已跳过 (${syncResult.skipped?.length || 0})`">
                    <n-list>
                      <n-list-item v-for="field in syncResult.skipped" :key="field.field_code">
                        <n-thing :title="field.field_code">
                          <template #description>
                            原因: {{ field.reason }}
                          </template>
                        </n-thing>
                      </n-list-item>
                    </n-list>
                  </n-tab-pane>
                  
                  <n-tab-pane v-if="syncResult.errors?.length" name="errors" :tab="`失败 (${syncResult.errors?.length || 0})`">
                    <n-list>
                      <n-list-item v-for="field in syncResult.errors" :key="field.field_code">
                        <n-thing :title="field.field_code">
                          <template #description>
                            <n-text type="error">{{ field.error }}</n-text>
                          </template>
                        </n-thing>
                      </n-list-item>
                    </n-list>
                  </n-tab-pane>
                </n-tabs>
              </n-collapse-item>
            </n-collapse>
          </template>
        </n-result>
      </div>
      
      <template #footer>
        <n-space justify="end">
          <n-button v-if="syncStep > 1 && syncStep < 3" @click="syncStep--">上一步</n-button>
          <n-button @click="handleCloseSyncModal">{{ syncStep === 3 ? '完成' : '取消' }}</n-button>
          <n-button v-if="syncStep === 1" type="primary" @click="handlePreviewSync" :loading="previewing">
            下一步：预览
          </n-button>
          <n-button v-if="syncStep === 2" type="primary" @click="handleExecuteSync" :loading="syncing">
            执行同步
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, h } from 'vue'
import { NButton, NTag, NSpace, NSwitch, useMessage } from 'naive-ui'
import { 
  SearchOutline, 
  RefreshOutline, 
  AddOutline, 
  CreateOutline, 
  TrashOutline,
  CloudDownloadOutline
} from '@vicons/ionicons5'
import { dataModelApi } from '@/api/v2/data-model'
import axios from 'axios'

const message = useMessage()

// 查询参数
const queryParams = reactive({
  device_type_code: null,
  field_category: null,
  search: '',
  is_active: true
})

// 数据
const fieldList = ref([])
const loading = ref(false)
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (page) => {
    pagination.page = page
    fetchFieldList()
  },
  onUpdatePageSize: (pageSize) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    fetchFieldList()
  }
})

// 选项
const deviceTypeOptions = ref([
  { label: '焊接设备', value: 'welding' },
  { label: '切割设备', value: 'cutting' },
  { label: '装配设备', value: 'assembly' }
])

const fieldCategoryOptions = [
  { label: '数据采集', value: 'data_collection' },
  { label: '维护记录', value: 'maintenance_record' },
  { label: 'AI分析', value: 'ai_analysis' }
]

const fieldTypeOptions = [
  { label: '整数', value: 'int' },
  { label: '大整数', value: 'bigint' },
  { label: '浮点数', value: 'float' },
  { label: '双精度浮点数', value: 'double' },
  { label: '字符串', value: 'string' },
  { label: '布尔值', value: 'boolean' },
  { label: '时间戳', value: 'timestamp' },
  { label: 'JSON', value: 'json' }
]

// 表格列定义
const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '字段代码', key: 'field_code', width: 180 },
  { title: '字段名称', key: 'field_name', width: 150 },
  { title: '设备类型', key: 'device_type_code', width: 120 },
  { 
    title: '字段类型', 
    key: 'field_type', 
    width: 100,
    render(row) {
      const typeMap = {
        int: 'info',
        float: 'success',
        double: 'success',
        string: 'default',
        boolean: 'warning'
      }
      return h(NTag, { type: typeMap[row.field_type] || 'default' }, { default: () => row.field_type })
    }
  },
  { title: '单位', key: 'unit', width: 80 },
  {
    title: '监控字段',
    key: 'is_monitoring_key',
    width: 100,
    render(row) {
      return row.is_monitoring_key ? h(NTag, { type: 'success', size: 'small' }, { default: () => '是' }) : '-'
    }
  },
  {
    title: 'AI特征',
    key: 'is_ai_feature',
    width: 100,
    render(row) {
      return row.is_ai_feature ? h(NTag, { type: 'warning', size: 'small' }, { default: () => '是' }) : '-'
    }
  },
  {
    title: '状态',
    key: 'is_active',
    width: 80,
    render(row) {
      return h(NSwitch, {
        value: row.is_active,
        onUpdateValue: (value) => handleToggleActive(row.id, value)
      })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right',
    render(row) {
      return h(NSpace, null, {
        default: () => [
          h(NButton, {
            size: 'small',
            type: 'info',
            text: true,
            onClick: () => handleEdit(row.id)
          }, { default: () => '编辑' }),
          h(NButton, {
            size: 'small',
            type: 'error',
            text: true,
            onClick: () => handleDelete(row.id)
          }, { default: () => '删除' })
        ]
      })
    }
  }
]

// 字段表单相关
const showFieldModal = ref(false)
const fieldModalTitle = computed(() => fieldFormData.id ? '编辑字段' : '新建字段')
const fieldFormRef = ref(null)
const saving = ref(false)

const fieldFormData = reactive({
  id: null,
  device_type_code: null,
  field_name: '',
  field_code: '',
  field_type: null,
  field_category: 'data_collection',
  unit: '',
  description: '',
  is_monitoring_key: false,
  is_ai_feature: false
})

const fieldFormRules = {
  device_type_code: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
  field_name: [{ required: true, message: '请输入字段名称', trigger: 'blur' }],
  field_code: [
    { required: true, message: '请输入字段代码', trigger: 'blur' },
    { pattern: /^[a-z][a-z0-9_]*$/, message: '字段代码只能包含小写字母、数字和下划线，且必须以字母开头', trigger: 'blur' }
  ],
  field_type: [{ required: true, message: '请选择字段类型', trigger: 'change' }],
  field_category: [{ required: true, message: '请选择字段分类', trigger: 'change' }]
}

// TDengine同步相关
const showSyncModal = ref(false)
const syncStep = ref(1)
const syncStatus = ref('process')
const previewing = ref(false)
const syncing = ref(false)
const syncFormRef = ref(null)

const syncFormData = reactive({
  device_type_code: null,
  tdengine_database: 'device_monitor',
  tdengine_stable: '',
  field_category: 'data_collection'
})

const syncFormRules = {
  device_type_code: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
  tdengine_database: [{ required: true, message: '请输入TDengine数据库名', trigger: 'blur' }],
  tdengine_stable: [{ required: true, message: '请输入TDengine超级表名', trigger: 'blur' }]
}

const previewResult = reactive({
  total_fields: 0,
  new_fields: 0,
  existing_fields: 0,
  skip_fields: 0,
  fields: []
})

const previewColumns = [
  { 
    title: '状态', 
    key: 'status_text', 
    width: 120,
    render(row) {
      const statusMap = {
        new: { type: 'success', text: '✓ 将创建' },
        exists: { type: 'default', text: '- 已存在' },
        skip_system: { type: 'warning', text: '⊗ 跳过' }
      }
      const config = statusMap[row.status] || { type: 'default', text: row.status_text }
      return h(NTag, { type: config.type }, { default: () => config.text })
    }
  },
  { title: '字段代码', key: 'field_code', width: 180 },
  { title: '字段名称', key: 'field_name', width: 150 },
  { title: 'TDengine类型', key: 'tdengine_type', width: 120 },
  { title: '系统类型', key: 'field_type', width: 100 },
  { 
    title: 'TAG', 
    key: 'is_tag', 
    width: 80,
    render(row) {
      return row.is_tag ? h(NTag, { type: 'info', size: 'small' }, { default: () => 'TAG' }) : '-'
    }
  }
]

const syncResult = reactive({
  created: [],
  skipped: [],
  errors: []
})

const syncResultTitle = computed(() => {
  if (syncStatus.value === 'error') return '同步失败'
  const total = syncResult.created.length + syncResult.skipped.length + syncResult.errors.length
  return `同步完成！共处理 ${total} 个字段`
})

const syncResultDescription = computed(() => {
  return `成功创建 ${syncResult.created.length} 个，跳过 ${syncResult.skipped.length} 个，失败 ${syncResult.errors.length} 个`
})

// 方法
const fetchFieldList = async () => {
  loading.value = true
  try {
    const response = await dataModelApi.getFields({
      ...queryParams,
      page: pagination.page,
      page_size: pagination.pageSize
    })
    
    if (response.success) {
      fieldList.value = response.data || []
      pagination.itemCount = response.total || 0
    } else {
      message.error(response.message || '查询失败')
    }
  } catch (error) {
    message.error('查询失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  pagination.page = 1
  fetchFieldList()
}

const handleReset = () => {
  queryParams.device_type_code = null
  queryParams.field_category = null
  queryParams.search = ''
  handleQuery()
}

const handleCreate = () => {
  Object.assign(fieldFormData, {
    id: null,
    device_type_code: null,
    field_name: '',
    field_code: '',
    field_type: null,
    field_category: 'data_collection',
    unit: '',
    description: '',
    is_monitoring_key: false,
    is_ai_feature: false
  })
  showFieldModal.value = true
}

const handleEdit = async (id) => {
  try {
    const response = await dataModelApi.getField(id)
    if (response.success) {
      Object.assign(fieldFormData, response.data)
      showFieldModal.value = true
    } else {
      message.error(response.message || '获取字段详情失败')
    }
  } catch (error) {
    message.error('获取字段详情失败：' + (error.message || '未知错误'))
  }
}

const handleSaveField = async () => {
  try {
    await fieldFormRef.value?.validate()
    
    saving.value = true
    
    const response = fieldFormData.id
      ? await dataModelApi.updateField(fieldFormData.id, fieldFormData)
      : await dataModelApi.createField(fieldFormData)
    
    if (response.success) {
      message.success(fieldFormData.id ? '更新成功' : '创建成功')
      showFieldModal.value = false
      fetchFieldList()
    } else {
      message.error(response.message || '保存失败')
    }
  } catch (error) {
    if (!error.errors) {
      message.error('保存失败：' + (error.message || '未知错误'))
    }
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id) => {
  try {
    const response = await dataModelApi.deleteField(id)
    if (response.success) {
      message.success('删除成功')
      fetchFieldList()
    } else {
      message.error(response.message || '删除失败')
    }
  } catch (error) {
    message.error('删除失败：' + (error.message || '未知错误'))
  }
}

const handleToggleActive = async (id, value) => {
  try {
    const response = await dataModelApi.updateField(id, { is_active: value })
    if (response.success) {
      message.success(value ? '已激活' : '已停用')
      fetchFieldList()
    } else {
      message.error(response.message || '操作失败')
      fetchFieldList()
    }
  } catch (error) {
    message.error('操作失败：' + (error.message || '未知错误'))
    fetchFieldList()
  }
}

// TDengine同步相关方法
const handleSyncFromTDengine = () => {
  // 重置表单
  Object.assign(syncFormData, {
    device_type_code: queryParams.device_type_code || null,
    tdengine_database: 'device_monitor',
    tdengine_stable: '',
    field_category: 'data_collection'
  })
  
  // 重置状态
  syncStep.value = 1
  syncStatus.value = 'process'
  Object.assign(previewResult, {
    total_fields: 0,
    new_fields: 0,
    existing_fields: 0,
    skip_fields: 0,
    fields: []
  })
  Object.assign(syncResult, {
    created: [],
    skipped: [],
    errors: []
  })
  
  showSyncModal.value = true
}

const handlePreviewSync = async () => {
  try {
    await syncFormRef.value?.validate()
    
    previewing.value = true
    
    const response = await axios.get('/api/v2/metadata-sync/preview-tdengine-fields', {
      params: syncFormData
    })
    
    if (response.data.success) {
      Object.assign(previewResult, response.data.data)
      syncStep.value = 2
      message.success('预览成功')
    } else {
      message.error(response.data.message || '预览失败')
    }
  } catch (error) {
    if (!error.errors) {
      message.error('预览失败：' + (error.response?.data?.message || error.message || '未知错误'))
    }
  } finally {
    previewing.value = false
  }
}

const handleExecuteSync = async () => {
  syncing.value = true
  syncStatus.value = 'process'
  
  try {
    const response = await axios.post('/api/v2/metadata-sync/sync-from-tdengine', syncFormData)
    
    if (response.data.success) {
      Object.assign(syncResult, response.data.data)
      syncStep.value = 3
      syncStatus.value = 'finish'
      message.success(response.data.message || '同步成功')
      
      // 刷新字段列表
      fetchFieldList()
    } else {
      syncStatus.value = 'error'
      message.error(response.data.message || '同步失败')
    }
  } catch (error) {
    syncStep.value = 3
    syncStatus.value = 'error'
    message.error('同步失败：' + (error.response?.data?.message || error.message || '未知错误'))
  } finally {
    syncing.value = false
  }
}

const handleCloseSyncModal = () => {
  showSyncModal.value = false
  if (syncStep.value === 3 && syncStatus.value === 'finish') {
    // 同步成功后刷新列表
    fetchFieldList()
  }
}

// 生命周期
onMounted(() => {
  fetchFieldList()
})
</script>

<style scoped>
.field-management {
  padding: 16px;
}

.mb-4 {
  margin-bottom: 16px;
}

.mt-4 {
  margin-top: 16px;
}
</style>

