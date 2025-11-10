<script setup lang="ts">
import { h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import { NButton, NForm, NFormItem, NInput, NPopconfirm, NSelect, NSwitch, NTag } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/page/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import PermissionButton from '@/components/Permission/PermissionButton.vue'

import { formatDate, formatDateTime, renderIcon } from '@/utils'
import { useCRUD } from '@/composables/useCRUD'
import api from '@/api'
// ✅ Shared API 迁移 (2025-10-25)
import { deviceTypeApi } from '@/api/device-shared'
import TheIcon from '@/components/icon/TheIcon.vue'
import { useRouter } from 'vue-router'

defineOptions({ name: '设备类型管理' })

const router = useRouter()

const $table = ref(null)
const queryItems = ref({
  type_name: '',
  type_code: '',
  is_active: undefined,
})
const vPermission = resolveDirective('permission')

const {
  modalVisible,
  modalAction,
  modalTitle,
  modalLoading,
  handleAdd,
  handleDelete,
  handleEdit,
  handleSave,
  modalForm,
  modalFormRef,
} = useCRUD({
  name: '设备类型',
  initForm: {
    type_name: '',
    type_code: '',
    tdengine_stable_name: '',
    description: '',
    is_active: true,
  },
  // ✅ Shared API 迁移
  doCreate: deviceTypeApi.create,
  doDelete: deviceTypeApi.delete,
  doUpdate: deviceTypeApi.update,
  refresh: () => $table.value?.handleSearch(),
})

onMounted(() => {
  $table.value?.handleSearch()
})

const columns = [
  {
    title: '类型名称',
    key: 'type_name',
    width: 150,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '类型编码',
    key: 'type_code',
    width: 120,
    align: 'center',
    ellipsis: { tooltip: true },
    render(row) {
      return h(NTag, { type: 'info' }, { default: () => row.type_code })
    },
  },
  {
    title: 'stable对照',
    key: 'tdengine_stable_name',
    width: 180,
    align: 'center',
    ellipsis: { tooltip: true },
    render(row) {
      return h(NTag, { type: 'warning' }, { default: () => row.tdengine_stable_name })
    },
  },
  {
    title: '状态',
    key: 'is_active',
    width: 80,
    align: 'center',
    render(row) {
      return h(
        NTag,
        { type: row.is_active ? 'success' : 'error' },
        { default: () => (row.is_active ? '激活' : '禁用') }
      )
    },
  },
  {
    title: '描述',
    key: 'description',
    width: 200,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    align: 'center',
    render(row) {
      return h('span', formatDateTime(row.created_at))
    },
  },
  {
    title: '更新时间',
    key: 'updated_at',
    width: 180,
    align: 'center',
    render(row) {
      return h('span', formatDateTime(row.updated_at))
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 280,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        h(
          PermissionButton,
          {
            permission: 'PUT /api/v2/devices/types/{id}',
            size: 'small',
            type: 'primary',
            style: 'margin-right: 8px;',
            onClick: () => {
              handleEdit(row)
            },
          },
          {
            default: () => '编辑',
            icon: renderIcon('material-symbols:edit-outline', { size: 16 }),
          }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'info',
            style: 'margin-right: 8px;',
            onClick: () => {
              // 跳转到数据模型配置页面，并预填充设备类型
              router.push({
                path: '/data-model/config',
                query: {
                  device_type: row.type_code,
                  type_name: row.type_name,
                },
              })
            },
          },
          {
            default: () => '配置数据模型',
            icon: renderIcon('mdi:database-cog', { size: 16 }),
          }
        ),
        h(
          PermissionButton,
          {
            permission: 'DELETE /api/v2/devices/types/{id}',
            size: 'small',
            type: 'error',
            needConfirm: true,
            confirmTitle: '删除确认',
            confirmContent: '确定删除该设备类型吗？此操作不可恢复。',
            onConfirm: () => handleDelete(row.type_code, false),
          },
          {
            default: () => '删除',
            icon: renderIcon('material-symbols:delete-outline', { size: 16 }),
          }
        ),
      ]
    },
  },
]
</script>

<template>
  <CommonPage show-footer title="设备类型列表">
    <template #action>
      <PermissionButton permission="POST /api/v2/devices/types" type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建设备类型
      </PermissionButton>
    </template>

    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="deviceTypeApi.list"
    >
      <template #queryBar>
        <QueryBarItem label="类型名称" :label-width="70">
          <NInput
            v-model:value="queryItems.type_name"
            clearable
            type="text"
            placeholder="请输入类型名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="类型编码" :label-width="70">
          <NInput
            v-model:value="queryItems.type_code"
            clearable
            type="text"
            placeholder="请输入类型编码"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="激活状态" :label-width="70">
          <NSelect
            v-model:value="queryItems.is_active"
            clearable
            placeholder="请选择状态"
            :options="[
              { label: '激活', value: true },
              { label: '禁用', value: false },
            ]"
            @update:value="$table?.handleSearch()"
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSave"
    >
      <NForm
        ref="modalFormRef"
        label-placement="left"
        label-align="left"
        :label-width="80"
        :model="modalForm"
        :disabled="modalAction === 'view'"
      >
        <NFormItem
          label="类型编码"
          path="type_code"
          :rule="{
            required: true,
            message: '请输入类型编码',
            trigger: ['input', 'blur'],
          }"
        >
          <NInput v-model:value="modalForm.type_code" placeholder="请输入类型编码" />
        </NFormItem>
        <NFormItem
          label="类型名称"
          path="type_name"
          :rule="{
            required: true,
            message: '请输入类型名称',
            trigger: ['input', 'blur'],
          }"
        >
          <NInput v-model:value="modalForm.type_name" placeholder="请输入类型名称" />
        </NFormItem>
        <NFormItem
          label="TDengine超级表名"
          path="tdengine_stable_name"
          :rule="{
            required: true,
            message: '请输入TDengine超级表名',
            trigger: ['input', 'blur'],
          }"
        >
          <NInput
            v-model:value="modalForm.tdengine_stable_name"
            placeholder="请输入TDengine超级表名"
          />
        </NFormItem>
        <NFormItem label="状态" path="is_active">
          <NSwitch v-model:value="modalForm.is_active">
            <template #checked>激活</template>
            <template #unchecked>禁用</template>
          </NSwitch>
        </NFormItem>
        <NFormItem label="描述" path="description">
          <NInput
            v-model:value="modalForm.description"
            type="textarea"
            placeholder="请输入描述"
            :autosize="{
              minRows: 3,
              maxRows: 5,
            }"
          />
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>
