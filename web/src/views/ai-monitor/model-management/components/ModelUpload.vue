<template>
  <n-modal
    v-model:show="showModal"
    preset="dialog"
    title="上传模型"
    :style="{ width: '600px' }"
    :mask-closable="false"
  >
    <n-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-placement="left"
      label-width="100px"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="模型名称" path="name">
        <n-input v-model:value="formData.name" placeholder="请输入模型名称" clearable />
      </n-form-item>

      <n-form-item label="模型描述" path="description">
        <n-input
          v-model:value="formData.description"
          type="textarea"
          placeholder="请输入模型描述"
          :rows="3"
          clearable
        />
      </n-form-item>

      <n-form-item label="模型类型" path="type">
        <n-select
          v-model:value="formData.type"
          placeholder="请选择模型类型"
          :options="typeOptions"
        />
      </n-form-item>

      <n-form-item label="版本号" path="version">
        <n-input v-model:value="formData.version" placeholder="例如: v1.0.0" clearable />
      </n-form-item>

      <n-form-item label="模型文件" path="file">
        <n-upload
          ref="uploadRef"
          :file-list="fileList"
          :max="1"
          :on-before-upload="handleBeforeUpload"
          :on-remove="handleRemove"
          :on-finish="handleFinish"
          :on-error="handleError"
          accept=".pkl,.h5,.onnx,.pt,.pth,.joblib,.model"
          :show-file-list="true"
          :custom-request="customRequest"
        >
          <n-upload-dragger>
            <div style="margin-bottom: 12px">
              <n-icon size="48" :depth="3">
                <cloud-upload-outline />
              </n-icon>
            </div>
            <n-text style="font-size: 16px"> 点击或者拖动文件到该区域来上传 </n-text>
            <n-p depth="3" style="margin: 8px 0 0 0">
              支持 .pkl, .h5, .onnx, .pt, .pth, .joblib, .model 格式
            </n-p>
          </n-upload-dragger>
        </n-upload>
      </n-form-item>

      <n-form-item label="标签" path="tags">
        <n-dynamic-tags v-model:value="formData.tags" placeholder="添加标签" />
      </n-form-item>

      <n-form-item label="配置参数">
        <n-card size="small" style="width: 100%">
          <template #header>
            <n-space justify="space-between">
              <span>模型参数</span>
              <n-button size="small" @click="addParameter"> 添加参数 </n-button>
            </n-space>
          </template>

          <n-space vertical>
            <div
              v-for="(param, index) in formData.parameters"
              :key="index"
              style="display: flex; gap: 8px; align-items: center"
            >
              <n-input v-model:value="param.key" placeholder="参数名" style="flex: 1" />
              <n-input v-model:value="param.value" placeholder="参数值" style="flex: 1" />
              <n-button size="small" quaternary type="error" @click="removeParameter(index)">
                <template #icon>
                  <n-icon><trash-outline /></n-icon>
                </template>
              </n-button>
            </div>

            <n-empty v-if="formData.parameters.length === 0" description="暂无参数" size="small" />
          </n-space>
        </n-card>
      </n-form-item>
    </n-form>

    <template #action>
      <n-space>
        <n-button @click="handleCancel">取消</n-button>
        <n-button type="primary" :loading="uploading" @click="handleSubmit">
          {{ uploading ? '上传中...' : '确认上传' }}
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  NModal,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NUpload,
  NUploadDragger,
  NIcon,
  NText,
  NP,
  NDynamicTags,
  NCard,
  NSpace,
  NButton,
  NEmpty,
  useMessage,
} from 'naive-ui'
import { CloudUploadOutline, TrashOutline } from '@vicons/ionicons5'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
})

// Emits
const emit = defineEmits(['update:show', 'success'])

// 响应式数据
const formRef = ref(null)
const uploadRef = ref(null)
const uploading = ref(false)
const fileList = ref([])

// 表单数据
const formData = ref({
  name: '',
  description: '',
  type: null,
  version: '',
  file: null,
  tags: [],
  parameters: [],
})

// 模型类型选项
const typeOptions = [
  { label: '异常检测', value: 'anomaly_detection' },
  { label: '趋势预测', value: 'trend_prediction' },
  { label: '健康评分', value: 'health_scoring' },
  { label: '分类模型', value: 'classification' },
  { label: '回归模型', value: 'regression' },
]

// 表单验证规则
const rules = {
  name: {
    required: true,
    message: '请输入模型名称',
    trigger: ['input', 'blur'],
  },
  description: {
    required: true,
    message: '请输入模型描述',
    trigger: ['input', 'blur'],
  },
  type: {
    required: true,
    message: '请选择模型类型',
    trigger: ['change', 'blur'],
  },
  version: {
    required: true,
    message: '请输入版本号',
    trigger: ['input', 'blur'],
  },
  file: {
    required: true,
    message: '请上传模型文件',
    trigger: ['change'],
  },
}

// 计算属性
const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value),
})

// 消息提示
const message = useMessage()

// 文件上传前的处理
const handleBeforeUpload = (data) => {
  const { file } = data
  const maxSize = 500 * 1024 * 1024 // 500MB

  if (file.size > maxSize) {
    message.error('文件大小不能超过 500MB')
    return false
  }

  formData.value.file = file
  return true
}

// 自定义上传请求
const customRequest = ({ file, onFinish, onError, onProgress }) => {
  // 这里可以实现实际的文件上传逻辑
  // 模拟上传进度
  let progress = 0
  const timer = setInterval(() => {
    progress += Math.random() * 30
    if (progress >= 100) {
      progress = 100
      clearInterval(timer)
      onFinish()
    }
    onProgress({ percent: Math.floor(progress) })
  }, 200)

  return {
    abort: () => {
      clearInterval(timer)
    },
  }
}

// 文件移除处理
const handleRemove = () => {
  formData.value.file = null
  return true
}

// 上传完成处理
const handleFinish = ({ file, event }) => {
  message.success('文件上传成功')
}

// 上传错误处理
const handleError = ({ file, event }) => {
  message.error('文件上传失败')
}

// 添加参数
const addParameter = () => {
  formData.value.parameters.push({
    key: '',
    value: '',
  })
}

// 移除参数
const removeParameter = (index) => {
  formData.value.parameters.splice(index, 1)
}

// 重置表单
const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    type: null,
    version: '',
    file: null,
    tags: [],
    parameters: [],
  }
  fileList.value = []
  if (formRef.value) {
    formRef.value.restoreValidation()
  }
}

// 取消操作
const handleCancel = () => {
  resetForm()
  showModal.value = false
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    if (!formData.value.file) {
      message.error('请上传模型文件')
      return
    }

    uploading.value = true

    // 模拟上传过程
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // 创建新模型对象
    const newModel = {
      id: Date.now(),
      name: formData.value.name,
      description: formData.value.description,
      type: formData.value.type,
      version: formData.value.version,
      status: 'stopped',
      accuracy: (85 + Math.random() * 10).toFixed(2),
      size: `${(formData.value.file.size / 1024 / 1024).toFixed(1)}MB`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      author: '当前用户',
      deployedAt: null,
      tags: formData.value.tags,
      parameters: formData.value.parameters.filter((p) => p.key && p.value),
      metrics: {
        precision: (80 + Math.random() * 15).toFixed(2),
        recall: (75 + Math.random() * 20).toFixed(2),
        f1Score: (78 + Math.random() * 17).toFixed(2),
      },
    }

    emit('success', newModel)
    message.success('模型上传成功')
    resetForm()
    showModal.value = false
  } catch (error) {
    message.error('表单验证失败，请检查输入')
  } finally {
    uploading.value = false
  }
}

// 监听弹窗显示状态
watch(
  () => props.show,
  (newVal) => {
    if (!newVal) {
      resetForm()
    }
  }
)
</script>

<style scoped>
/* 可以添加自定义样式 */
</style>
