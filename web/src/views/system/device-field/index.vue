<template>
  <CommonPage show-footer title="设备字段配置管理">
    <template #action>
      <n-button 
        v-permission="'POST /api/v2/device-fields'"
        type="primary" 
        @click="handleCreate" 
        :disabled="!selectedDeviceType"
      >
        <template #icon>
          <n-icon><AddOutline /></n-icon>
        </template>
        新增字段
      </n-button>
    </template>

    <CrudTable
      ref="$table"
      :columns="columns"
      :get-data="getFieldsData"
      :pagination="pagination"
      row-key="id"
      @onPageChange="handlePageChange"
      @onPageSizeChange="handlePageSizeChange"
    >
      <template #queryBar>
        <QueryBarItem label="设备类型" :label-width="80">
          <n-select
            v-model:value="selectedDeviceType"
            :options="deviceTypeOptions"
            placeholder="请选择设备类型"
            clearable
            @update:value="handleDeviceTypeChange"
            :loading="loadingDeviceTypes"
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <!-- 字段编辑对话框 -->
    <n-modal
      v-model:show="showDialog"
      preset="card"
      :title="dialogTitle"
      style="width: 600px"
      :mask-closable="false"
    >
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="120px"
      >
        <n-form-item label="选择字段" path="field_code" v-if="!isEdit">
          <n-space vertical style="width: 100%">
            <n-select
              v-model:value="formData.field_code"
              :options="tdengineFieldOptions"
              placeholder="从 TDengine 超级表选择字段"
              filterable
              :loading="loadingTDengineFields"
              @update:value="handleFieldSelect"
            >
              <template #empty>
                <n-empty description="未找到可用字段">
                  <template #extra>
                    <n-button size="small" @click="loadTDengineFields">
                      刷新字段列表
                    </n-button>
                  </template>
                </n-empty>
              </template>
            </n-select>
            <n-text depth="3" style="font-size: 12px">
              💡 提示：字段代码将自动从 TDengine 超级表中提取，确保完全匹配
            </n-text>
          </n-space>
        </n-form-item>

        <n-form-item label="字段代码" path="field_code" v-if="isEdit">
          <n-input
            v-model:value="formData.field_code"
            placeholder="字段代码"
            disabled
          />
        </n-form-item>

        <n-form-item label="字段名称" path="field_name">
          <n-input v-model:value="formData.field_name" placeholder="请输入字段名称（中文）" />
        </n-form-item>

        <n-form-item label="字段类型" path="field_type">
          <n-input
            v-model:value="formData.field_type"
            placeholder="字段类型"
            disabled
          >
            <template #suffix>
              <n-tag size="small" :type="getFieldTypeTagType(formData.field_type)">
                {{ formData.field_type }}
              </n-tag>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item label="单位" path="unit">
          <n-input v-model:value="formData.unit" placeholder="请输入单位（如：MPa、°C）" />
        </n-form-item>

        <n-form-item label="排序" path="sort_order">
          <n-input-number
            v-model:value="formData.sort_order"
            :min="1"
            :max="100"
            placeholder="数字越小越靠前"
            style="width: 100%"
          />
        </n-form-item>

        <n-form-item label="图标" path="display_config.icon">
          <n-input
            v-model:value="formData.display_config.icon"
            placeholder="请输入图标（emoji）"
            maxlength="2"
          >
            <template #suffix>
              <n-popover trigger="hover">
                <template #trigger>
                  <n-icon><HelpCircleOutline /></n-icon>
                </template>
                <div>
                  <p>常用图标：</p>
                  <p>📊 数值/图表 🌡️ 温度 💧 湿度</p>
                  <p>📳 振动 ⚡ 电流 🔥 功率</p>
                  <p>🌪️ 气压 ⚙️ 设备 📡 信号</p>
                </div>
              </n-popover>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item label="颜色" path="display_config.color">
          <n-color-picker v-model:value="formData.display_config.color" :show-alpha="false" />
        </n-form-item>

        <n-form-item label="字段分类" path="field_category">
          <n-select
            v-model:value="formData.field_category"
            :options="fieldCategoryOptions"
            :loading="loadingFieldCategories"
            placeholder="请选择字段分类"
          />
        </n-form-item>

        <n-divider title-placement="left">字段分组配置</n-divider>

        <n-form-item label="字段分组" path="field_group">
          <n-select
            v-model:value="formData.field_group"
            :options="fieldGroupOptions"
            :loading="loadingFieldGroups"
            placeholder="请选择字段分组"
          >
            <template #suffix>
              <n-popover trigger="hover">
                <template #trigger>
                  <n-icon><HelpCircleOutline /></n-icon>
                </template>
                <div style="max-width: 300px">
                  <p><strong>字段分组说明：</strong></p>
                  <p>• <strong>核心参数</strong>：最重要的参数，默认显示</p>
                  <p>• <strong>温度参数</strong>：温度相关参数</p>
                  <p>• <strong>功率参数</strong>：功率、电流相关参数</p>
                  <p>• <strong>速度参数</strong>：速度、转速相关参数</p>
                  <p>• <strong>尺寸参数</strong>：尺寸、宽度相关参数</p>
                  <p>• <strong>其他参数</strong>：未分类参数</p>
                </div>
              </n-popover>
            </template>
          </n-select>
        </n-form-item>

        <n-form-item label="默认显示" path="is_default_visible">
          <n-switch v-model:value="formData.is_default_visible">
            <template #checked>是</template>
            <template #unchecked>否</template>
          </n-switch>
          <n-text depth="3" style="margin-left: 12px; font-size: 12px">
            默认显示的字段会直接在设备卡片中展示，其他字段需要展开查看
          </n-text>
        </n-form-item>

        <n-form-item label="分组排序" path="group_order">
          <n-input-number
            v-model:value="formData.group_order"
            :min="0"
            :max="999"
            placeholder="数字越小越靠前"
            style="width: 100%"
          />
          <n-text depth="3" style="margin-left: 12px; font-size: 12px">
            控制分组在卡片中的显示顺序
          </n-text>
        </n-form-item>

        <n-divider title-placement="left">其他配置</n-divider>

        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="请输入字段描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="监测关键字段" path="is_monitoring_key">
          <n-switch v-model:value="formData.is_monitoring_key">
            <template #checked>是</template>
            <template #unchecked>否</template>
          </n-switch>
          <n-text depth="3" style="margin-left: 12px; font-size: 12px">
            只有监测关键字段才会在设备卡片中显示
          </n-text>
        </n-form-item>

        <n-form-item label="启用" path="is_active">
          <n-switch v-model:value="formData.is_active">
            <template #checked>是</template>
            <template #unchecked>否</template>
          </n-switch>
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showDialog = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            保存
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </CommonPage>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import {
  NSpace,
  NSelect,
  NButton,
  NDataTable,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NColorPicker,
  NSwitch,
  NIcon,
  NText,
  NPopover,
  NTag,
  NPopconfirm,
  NEmpty,
  NDivider,
  useMessage,
  type DataTableColumns
} from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/page/QueryBarItem.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import PermissionButton from '@/components/Permission/PermissionButton.vue'
import {
  AddOutline,
  RefreshOutline,
  CreateOutline,
  TrashOutline,
  HelpCircleOutline
} from '@vicons/ionicons5'
import deviceV2Api from '@/api/device-v2'
import systemV2Api from '@/api/system-v2'
import type { DeviceType, DeviceField } from '@/types/device'
import { usePermission } from '@/composables/usePermission'
import { renderIcon } from '@/utils'

defineOptions({ name: 'DeviceFieldConfig' })

const message = useMessage()
const { hasPermission } = usePermission()

// 表格引用
const $table = ref<any>(null)

// TDengine 字段相关状态
const tdengineFieldOptions = ref<Array<{ label: string; value: string; tdengine_type: string; field_type: string }>>([])
const loadingTDengineFields = ref(false)

// 状态
const selectedDeviceType = ref<string>('')
const deviceTypeOptions = ref<Array<{ label: string; value: string }>>([])
const loadingDeviceTypes = ref(false)
const showDialog = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const formRef = ref()

// 分页配置
const pagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  showQuickJumper: true,
  prefix: (info: any) => `共 ${info.itemCount} 条`
})
// 注意：不设置 itemCount，让 CrudTable 使用内部的 total 值

// 处理分页变化事件
function handlePageChange(page: number) {
  pagination.page = page
}

function handlePageSizeChange(pageSize: number) {
  pagination.pageSize = pageSize
  pagination.page = 1
}

// 表单数据
const formData = reactive({
  id: null as number | null,
  device_type_code: '',
  field_name: '',
  field_code: '',
  field_type: 'float',
  unit: '',
  sort_order: 1,
  display_config: {
    icon: '',
    color: '#1890ff'
  },
  field_category: 'data_collection',
  description: '',
  is_monitoring_key: true,
  is_active: true,
  // 字段分组相关
  field_group: 'default',
  is_default_visible: true,
  group_order: 0
})

// 字段类型选项
const fieldTypeOptions = [
  { label: '浮点数 (float)', value: 'float' },
  { label: '整数 (int)', value: 'int' },
  { label: '字符串 (string)', value: 'string' },
  { label: '布尔值 (boolean)', value: 'boolean' }
]

// 字段分组选项（从数据字典加载）
const fieldGroupOptions = ref<Array<{ label: string; value: string }>>([])
const loadingFieldGroups = ref(false)

// 加载字段分组选项
async function loadFieldGroupOptions() {
  try {
    loadingFieldGroups.value = true
    const response = await systemV2Api.getDictDataByType('device_field_group')
    if (response.success && response.data && response.data.data) {
      fieldGroupOptions.value = response.data.data
        .filter((item: any) => item.is_enabled)
        .sort((a: any, b: any) => a.sort_order - b.sort_order)
        .map((item: any) => ({
          label: item.data_label,
          value: item.data_value
        }))
      console.log('字段分组选项加载成功:', fieldGroupOptions.value.length)
    }
  } catch (error) {
    console.error('加载字段分组选项失败:', error)
    message.warning('加载字段分组选项失败，使用默认选项')
    // 后备选项
    fieldGroupOptions.value = [
      { label: '📊 核心参数', value: 'core' },
      { label: '🌡️ 温度参数', value: 'temperature' },
      { label: '⚡ 功率参数', value: 'power' },
      { label: '⚙️ 速度参数', value: 'speed' },
      { label: '📏 尺寸参数', value: 'dimension' },
      { label: '📋 其他参数', value: 'other' },
      { label: '默认分组', value: 'default' }
    ]
  } finally {
    loadingFieldGroups.value = false
  }
}

// 字段分类选项（从数据字典加载）
const fieldCategoryOptions = ref<Array<{ label: string; value: string }>>([])
const loadingFieldCategories = ref(false)

// 加载字段分类选项
async function loadFieldCategoryOptions() {
  try {
    loadingFieldCategories.value = true
    const response = await systemV2Api.getDictDataByType('device_field_category')
    if (response.success && response.data && response.data.data) {
      fieldCategoryOptions.value = response.data.data
        .filter((item: any) => item.is_enabled)
        .sort((a: any, b: any) => a.sort_order - b.sort_order)
        .map((item: any) => ({
          label: item.data_label,
          value: item.data_value
        }))
      console.log('字段分类选项加载成功:', fieldCategoryOptions.value.length)
    }
  } catch (error) {
    console.error('加载字段分类选项失败:', error)
    message.warning('加载字段分类选项失败，使用默认选项')
    // 后备选项
    fieldCategoryOptions.value = [
      { label: '数据采集', value: 'data_collection' },
      { label: '控制参数', value: 'control' },
      { label: '状态信息', value: 'status' },
      { label: '其他', value: 'other' }
    ]
  } finally {
    loadingFieldCategories.value = false
  }
}

// 表单验证规则
const formRules = {
  field_name: [
    { required: true, message: '请输入字段名称', trigger: 'blur' }
  ],
  field_code: [
    { required: true, message: '请输入字段代码', trigger: 'blur' },
    {
      pattern: /^[a-z_][a-z0-9_]*$/,
      message: '字段代码只能包含小写字母、数字和下划线，且必须以字母或下划线开头',
      trigger: 'blur'
    }
  ],
  field_type: [
    { required: true, message: '请选择字段类型', trigger: 'change' }
  ],
  sort_order: [
    { required: true, type: 'number', message: '请输入排序值', trigger: 'blur' }
  ]
}

// 对话框标题
const dialogTitle = computed(() => {
  return isEdit.value ? '编辑字段配置' : '新增字段配置'
})

// 字段分组显示映射（动态生成）
const groupMap = computed(() => {
  const map: Record<string, { label: string; icon: string }> = {}
  
  fieldGroupOptions.value.forEach(option => {
    // 提取emoji图标（如果有）
    const match = option.label.match(/^([\u{1F300}-\u{1F9FF}])\s*(.+)$/u)
    if (match) {
      map[option.value] = {
        label: match[2],  // 去掉emoji的标签
        icon: match[1]     // emoji图标
      }
    } else {
      map[option.value] = {
        label: option.label,
        icon: ''
      }
    }
  })
  
  return map
})

// 表格列定义
const columns: DataTableColumns<DeviceField> = [
  {
    title: '序号',
    key: 'sort_order',
    width: 80,
    align: 'center'
  },
  {
    title: '字段名称',
    key: 'field_name',
    width: 120,
    render: (row) => {
      const icon = row.display_config?.icon
      return h('span', {}, [
        icon ? h('span', { style: 'margin-right: 8px' }, icon) : null,
        row.field_name
      ])
    }
  },
  {
    title: '字段代码',
    key: 'field_code',
    width: 150
  },
  {
    title: '字段类型',
    key: 'field_type',
    width: 100,
    render: (row) => {
      const typeMap: Record<string, { label: string; type: string }> = {
        float: { label: 'float', type: 'info' },
        int: { label: 'int', type: 'success' },
        string: { label: 'string', type: 'warning' },
        boolean: { label: 'boolean', type: 'error' }
      }
      const config = typeMap[row.field_type] || { label: row.field_type, type: 'default' }
      return h(NTag, { type: config.type as any, size: 'small' }, { default: () => config.label })
    }
  },
  {
    title: '单位',
    key: 'unit',
    width: 80,
    render: (row) => row.unit || '-'
  },
  {
    title: '字段分组',
    key: 'field_group',
    width: 120,
    render: (row) => {
      const config = groupMap.value[row.field_group || 'default'] || { label: row.field_group || 'default', icon: '' }
      return h('span', {}, [
        config.icon ? h('span', { style: 'margin-right: 4px' }, config.icon) : null,
        config.label
      ])
    }
  },
  {
    title: '默认显示',
    key: 'is_default_visible',
    width: 100,
    align: 'center',
    render: (row) => {
      return h(
        NTag,
        { type: row.is_default_visible ? 'info' : 'default', size: 'small' },
        { default: () => (row.is_default_visible ? '是' : '否') }
      )
    }
  },
  {
    title: '监测关键',
    key: 'is_monitoring_key',
    width: 100,
    align: 'center',
    render: (row) => {
      return h(
        NTag,
        { type: row.is_monitoring_key ? 'success' : 'default', size: 'small' },
        { default: () => (row.is_monitoring_key ? '是' : '否') }
      )
    }
  },
  {
    title: '状态',
    key: 'is_active',
    width: 80,
    align: 'center',
    render: (row) => {
      return h(
        NTag,
        { type: row.is_active ? 'success' : 'error', size: 'small' },
        { default: () => (row.is_active ? '启用' : '禁用') }
      )
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    align: 'center',
    fixed: 'right',
    render: (row) => {
      const actions = []
      
      // 编辑按钮 - 使用 PermissionButton
      actions.push(
        h(PermissionButton, {
          permission: 'PUT /api/v2/device-fields/{field_id}',
          size: 'small',
          type: 'primary',
          style: 'margin-right: 8px;',
          onClick: () => handleEdit(row)
        }, {
          default: () => '编辑',
          icon: renderIcon('material-symbols:edit', { size: 16 })
        })
      )
      
      // 删除按钮 - 使用 PermissionButton 带确认
      actions.push(
        h(PermissionButton, {
          permission: 'DELETE /api/v2/device-fields/{field_id}',
          size: 'small',
          type: 'error',
          needConfirm: true,
          confirmTitle: '删除确认',
          confirmContent: `确定删除字段"${row.field_name}"吗？此操作不可恢复。`,
          onConfirm: () => handleDelete(row.id)
        }, {
          default: () => '删除',
          icon: renderIcon('material-symbols:delete-outline', { size: 16 })
        })
      )
      
      return h(NSpace, { justify: 'center' }, {
        default: () => actions
      })
    }
  }
]

// 加载设备类型列表
async function loadDeviceTypes() {
  try {
    loadingDeviceTypes.value = true
    const response = await deviceV2Api.deviceTypes.list({ include_counts: false })
    if (response.success && response.data) {
      deviceTypeOptions.value = response.data.map((type: DeviceType) => ({
        label: type.type_name,
        value: type.type_code
      }))
    }
  } catch (error) {
    console.error('加载设备类型失败:', error)
    message.error('加载设备类型失败')
  } finally {
    loadingDeviceTypes.value = false
  }
}

// 加载 TDengine 字段列表
async function loadTDengineFields() {
  if (!selectedDeviceType.value) {
    tdengineFieldOptions.value = []
    return
  }

  try {
    loadingTDengineFields.value = true
    const response = await deviceV2Api.deviceFields.getTDengineFields(selectedDeviceType.value)
    if (response.success && response.data && response.data.fields) {
      tdengineFieldOptions.value = response.data.fields.map((field: any) => ({
        label: `${field.field_code} (${field.tdengine_type})`,
        value: field.field_code,
        tdengine_type: field.tdengine_type,
        field_type: field.field_type
      }))
    }
  } catch (error) {
    console.error('加载 TDengine 字段失败:', error)
    message.error('加载 TDengine 字段失败')
  } finally {
    loadingTDengineFields.value = false
  }
}

// 处理字段选择
function handleFieldSelect(fieldCode: string) {
  const selectedField = tdengineFieldOptions.value.find(f => f.value === fieldCode)
  if (selectedField) {
    formData.field_code = fieldCode
    formData.field_type = selectedField.field_type
    // 自动填充字段名称（可以后续修改）
    if (!formData.field_name) {
      formData.field_name = fieldCode
    }
  }
}

// 获取字段类型标签颜色
function getFieldTypeTagType(fieldType: string) {
  const typeMap: Record<string, any> = {
    'float': 'info',
    'int': 'success',
    'string': 'warning',
    'boolean': 'error'
  }
  return typeMap[fieldType] || 'default'
}

// 适配 CrudTable 的数据加载函数（前端分页）
async function getFieldsData(params: any = {}) {
  if (!selectedDeviceType.value) {
    return {
      data: [],
      total: 0
    }
  }

  try {
    // 使用getByDeviceType获取所有字段，而不仅仅是监测字段
    const response = await deviceV2Api.deviceFields.getByDeviceType(selectedDeviceType.value)
    if (response.success && response.data) {
      const allData = response.data
      const total = allData.length
      
      // 前端分页处理
      const page = params.page || 1
      const pageSize = params.page_size || pagination.pageSize
      const startIndex = (page - 1) * pageSize
      const endIndex = startIndex + pageSize
      const paginatedData = allData.slice(startIndex, endIndex)
      
      return {
        data: paginatedData,
        total: total
      }
    }
    return {
      data: [],
      total: 0
    }
  } catch (error) {
    console.error('加载字段列表失败:', error)
    message.error('加载字段列表失败')
    return {
      data: [],
      total: 0
    }
  }
}

// 设备类型变化
function handleDeviceTypeChange() {
  $table.value?.handleSearch() // 触发 CrudTable 重新加载数据
  loadTDengineFields() // 同时加载 TDengine 字段
}

// 新增字段
function handleCreate() {
  isEdit.value = false
  resetForm()
  formData.device_type_code = selectedDeviceType.value
  showDialog.value = true
  // 加载 TDengine 字段供选择
  loadTDengineFields()
}

// 编辑字段
function handleEdit(row: DeviceField) {
  isEdit.value = true
  Object.assign(formData, {
    id: row.id,
    device_type_code: row.device_type_code,
    field_name: row.field_name,
    field_code: row.field_code,
    field_type: row.field_type,
    unit: row.unit || '',
    sort_order: row.sort_order,
    display_config: {
      icon: row.display_config?.icon || '',
      color: row.display_config?.color || '#1890ff'
    },
    field_category: row.field_category || 'data_collection',
    description: row.description || '',
    is_monitoring_key: row.is_monitoring_key,
    is_active: row.is_active
  })
  showDialog.value = true
}

// 删除字段
async function handleDelete(id: number) {
  try {
    const response = await deviceV2Api.deviceFields.delete(id)
    if (response.success) {
      message.success('删除成功')
      // 刷新表格数据
      $table.value?.handleSearch()
    } else {
      message.error(response.message || '删除失败')
    }
  } catch (error) {
    console.error('删除字段失败:', error)
    message.error('删除字段失败')
  }
}

// 提交表单
async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true

    const data = {
      device_type_code: formData.device_type_code,
      field_name: formData.field_name,
      field_code: formData.field_code,
      field_type: formData.field_type,
      unit: formData.unit || null,
      sort_order: formData.sort_order,
      display_config: formData.display_config.icon || formData.display_config.color !== '#1890ff'
        ? formData.display_config
        : null,
      field_category: formData.field_category,
      field_group: formData.field_group,  // ✅ 添加字段分组
      is_default_visible: formData.is_default_visible,  // ✅ 添加默认显示
      group_order: formData.group_order,  // ✅ 添加分组排序
      description: formData.description || null,
      is_monitoring_key: formData.is_monitoring_key,
      is_active: formData.is_active
    }

    let response
    if (isEdit.value && formData.id) {
      response = await deviceV2Api.deviceFields.update(formData.id, data)
    } else {
      response = await deviceV2Api.deviceFields.create(data)
    }

    if (response.success) {
      message.success(isEdit.value ? '更新成功' : '创建成功')
      showDialog.value = false
      // 刷新表格数据
      $table.value?.handleSearch()
    } else {
      message.error(response.message || (isEdit.value ? '更新失败' : '创建失败'))
    }
  } catch (error: any) {
    if (error?.errors) {
      // 表单验证错误
      return
    }
    console.error('提交失败:', error)
    message.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
function resetForm() {
  Object.assign(formData, {
    id: null,
    device_type_code: '',
    field_name: '',
    field_code: '',
    field_type: 'float',
    unit: '',
    sort_order: 1,
    display_config: {
      icon: '',
      color: '#1890ff'
    },
    field_category: 'data_collection',
    description: '',
    is_monitoring_key: true,
    is_active: true
  })
  formRef.value?.restoreValidation()
}

// 初始化
onMounted(() => {
  loadDeviceTypes()
  loadFieldGroupOptions()      // ✅ 加载字段分组选项
  loadFieldCategoryOptions()   // ✅ 加载字段分类选项
})
</script>

<style scoped lang="scss">
.device-field-config {
  padding: 16px;
}
</style>
