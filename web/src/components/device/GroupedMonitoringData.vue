<template>
  <div class="grouped-monitoring-data">
    <!-- 加载状态 -->
    <template v-if="loading">
      <div class="loading-skeleton">
        <NSkeleton text :repeat="3" style="margin-bottom: 8px" />
      </div>
    </template>

    <!-- 轮播图显示 -->
    <template v-else-if="carouselItems.length > 0">
      <!-- 分组标题和导航 -->
      <div class="carousel-header">
        <div class="group-navigation">
          <NButton
            text
            size="small"
            :disabled="currentIndex === 0"
            @click="prevGroup"
            class="nav-btn"
          >
            <template #icon>
              <TheIcon icon="material-symbols:chevron-left" />
            </template>
          </NButton>
          
          <div class="group-info">
            <span class="group-icon">{{ currentGroup?.icon }}</span>
            <span class="group-title">{{ currentGroup?.title }}</span>
            <span class="group-count">({{ currentIndex + 1 }}/{{ carouselItems.length }})</span>
          </div>
          
          <NButton
            text
            size="small"
            :disabled="currentIndex === carouselItems.length - 1"
            @click="nextGroup"
            class="nav-btn"
          >
            <template #icon>
              <TheIcon icon="material-symbols:chevron-right" />
            </template>
          </NButton>
        </div>
      </div>

      <!-- 轮播容器 -->
      <div class="carousel-container">
        <NCarousel
          ref="carouselRef"
          v-model:current-index="currentIndex"
          :show-dots="true"
          :show-arrow="false"
          :slides-per-view="1"
          :space-between="0"
          :autoplay="false"
          :touchable="true"
          dot-type="dot"
          dot-placement="bottom"
          class="monitoring-carousel"
        >
          <div
            v-for="item in carouselItems"
            :key="item.name"
            class="carousel-item"
          >
            <div class="field-list">
              <div v-for="field in item.fields" :key="field.field_code" class="data-row">
                <span class="data-label">
                  <span v-if="getFieldIcon(field)" class="field-icon">{{ getFieldIcon(field) }}</span>
                  {{ field.field_name }}:
                </span>
                <span class="data-value" :style="{ color: getFieldColor(field) }">
                  {{ formatValue(realtimeData[field.field_code], field) }}
                </span>
              </div>
            </div>
          </div>
        </NCarousel>
      </div>
    </template>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <TheIcon icon="material-symbols:database-off-outline" :size="32" class="empty-icon" />
      <span class="empty-text">暂无监测数据</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { NSkeleton, NButton, NCarousel } from 'naive-ui'
import TheIcon from '@/components/icon/TheIcon.vue'

/**
 * 设备字段接口定义
 */
interface DeviceField {
  id: number
  device_type_code: string
  field_name: string
  field_code: string
  field_type: 'float' | 'int' | 'string' | 'boolean'
  unit?: string
  sort_order: number
  display_config?: {
    icon?: string
    color?: string
    chart_type?: string
  }
  field_category?: string
  description?: string
  field_group?: string
  is_default_visible?: boolean
  group_order?: number
}

/**
 * 组件 Props
 */
interface Props {
  monitoringFields: DeviceField[]
  realtimeData: Record<string, any>
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// 轮播相关
const carouselRef = ref()
const currentIndex = ref(0)

/**
 * 所有字段（按 sort_order 排序）
 */
const allFields = computed(() => {
  return [...props.monitoringFields].sort((a, b) => a.sort_order - b.sort_order)
})

/**
 * 核心字段（默认显示）
 */
const coreFields = computed(() => {
  return allFields.value
    .filter(f => f.is_default_visible !== false)
    .sort((a, b) => a.sort_order - b.sort_order)
})

/**
 * 其他分组字段
 */
const otherGroups = computed(() => {
  const groups = new Map<string, { name: string; title: string; icon: string; fields: DeviceField[]; order: number }>()
  
  allFields.value
    .filter(f => f.is_default_visible === false)
    .forEach(field => {
      const groupName = field.field_group || 'other'
      if (!groups.has(groupName)) {
        groups.set(groupName, {
          name: groupName,
          title: getGroupTitle(groupName),
          icon: getGroupIcon(groupName),
          fields: [],
          order: field.group_order || 999
        })
      }
      groups.get(groupName)!.fields.push(field)
    })
  
  // 按 group_order 排序
  return Array.from(groups.values())
    .sort((a, b) => a.order - b.order)
    .map(group => ({
      ...group,
      fields: group.fields.sort((a, b) => a.sort_order - b.sort_order)
    }))
})

/**
 * 轮播项目（包括核心参数和其他分组）
 */
const carouselItems = computed(() => {
  const items = []
  
  // 添加核心参数
  if (coreFields.value.length > 0) {
    items.push({
      name: 'core',
      title: '核心参数',
      icon: '📊',
      fields: coreFields.value
    })
  }
  
  // 添加其他分组
  items.push(...otherGroups.value)
  
  return items
})

/**
 * 当前分组
 */
const currentGroup = computed(() => {
  return carouselItems.value[currentIndex.value]
})

/**
 * 上一个分组
 */
function prevGroup() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

/**
 * 下一个分组
 */
function nextGroup() {
  if (currentIndex.value < carouselItems.value.length - 1) {
    currentIndex.value++
  }
}

/**
 * 监听字段变化，重置到第一页
 */
watch(() => props.monitoringFields, () => {
  currentIndex.value = 0
}, { deep: true })

/**
 * 获取分组标题
 */
function getGroupTitle(groupName: string): string {
  const titles: Record<string, string> = {
    core: '核心参数',
    temperature: '温度参数',
    power: '功率参数',
    speed: '速度参数',
    dimension: '尺寸参数',
    other: '其他参数'
  }
  return titles[groupName] || groupName
}

/**
 * 获取分组图标
 */
function getGroupIcon(groupName: string): string {
  const icons: Record<string, string> = {
    core: '📊',
    temperature: '🌡️',
    power: '⚡',
    speed: '⚙️',
    dimension: '📏',
    other: '📋'
  }
  return icons[groupName] || '📁'
}

/**
 * 格式化数值显示
 */
function formatValue(value: any, field: DeviceField): string {
  if (value === null || value === undefined || value === '') {
    return '--'
  }

  let formattedValue: string | number = value

  if (field.field_type === 'float') {
    const numValue = Number(value)
    if (!isNaN(numValue)) {
      formattedValue = numValue.toFixed(2)
    }
  } else if (field.field_type === 'int') {
    const numValue = Number(value)
    if (!isNaN(numValue)) {
      formattedValue = Math.round(numValue)
    }
  } else if (field.field_type === 'boolean') {
    formattedValue = value ? '是' : '否'
  } else {
    formattedValue = String(value)
  }

  if (field.unit) {
    return `${formattedValue} ${field.unit}`
  }

  return String(formattedValue)
}

/**
 * 获取字段图标
 */
function getFieldIcon(field: DeviceField): string {
  return field.display_config?.icon || ''
}

/**
 * 获取字段颜色
 */
function getFieldColor(field: DeviceField): string {
  return field.display_config?.color || '#333'
}
</script>

<style scoped lang="scss">
.grouped-monitoring-data {
  padding: 8px 0;
}

.loading-skeleton {
  padding: 12px;
}

// 轮播头部
.carousel-header {
  margin-bottom: 12px;
}

.group-navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.08) 0%, rgba(24, 144, 255, 0.03) 100%);
  border: 1px solid rgba(24, 144, 255, 0.15);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.nav-btn {
  padding: 4px;
  min-width: 32px;
  transition: all 0.2s;
  
  &:not(:disabled):hover {
    transform: scale(1.1);
  }
  
  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
}

.group-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  flex: 1;
  justify-content: center;

  .group-icon {
    font-size: 18px;
    animation: pulse 2s ease-in-out infinite;
  }

  .group-title {
    font-weight: 600;
  }

  .group-count {
    font-size: 12px;
    color: #666;
    font-weight: 400;
    background: rgba(0, 0, 0, 0.05);
    padding: 2px 8px;
    border-radius: 12px;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

// 轮播容器
.carousel-container {
  position: relative;
  padding-bottom: 32px;
}

.monitoring-carousel {
  :deep(.n-carousel__dots) {
    bottom: 0;
    gap: 8px;
  }
  
  :deep(.n-carousel__dot) {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.15);
    transition: all 0.3s;
  }
  
  :deep(.n-carousel__dot--active) {
    background: #1890ff;
    width: 24px;
    border-radius: 4px;
  }

  :deep(.n-carousel__slides) {
    min-height: 140px;
  }
}

.carousel-item {
  padding: 16px;
  background: rgba(0, 0, 0, 0.01);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 8px;
  min-height: 120px;
  transition: all 0.3s;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border-color: rgba(24, 144, 255, 0.2);
  }
}

.field-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.data-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  line-height: 1.6;
  padding: 6px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: rgba(24, 144, 255, 0.04);
    transform: translateX(2px);
  }
}

.data-label {
  color: #666;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;

  .field-icon {
    font-size: 16px;
    line-height: 1;
  }
}

.data-value {
  font-weight: 600;
  font-size: 14px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  transition: all 0.3s;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 16px;
  color: #999;
  text-align: center;

  .empty-icon {
    margin-bottom: 12px;
    opacity: 0.4;
  }

  .empty-text {
    font-size: 13px;
    opacity: 0.6;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .carousel-item {
    padding: 12px;
  }

  .data-row {
    font-size: 12px;
    padding: 5px 6px;
  }

  .data-value {
    font-size: 13px;
  }
  
  .group-navigation {
    padding: 8px 10px;
  }
  
  .group-info {
    font-size: 13px;
    gap: 6px;
    
    .group-icon {
      font-size: 16px;
    }
  }
}

// 深色模式适配
:deep(.dark) {
  .group-navigation {
    background: linear-gradient(135deg, rgba(24, 144, 255, 0.12) 0%, rgba(24, 144, 255, 0.05) 100%);
    border-color: rgba(24, 144, 255, 0.25);
  }
  
  .group-info {
    color: #fff;
    
    .group-count {
      background: rgba(255, 255, 255, 0.1);
      color: #ccc;
    }
  }
  
  .carousel-item {
    background: rgba(255, 255, 255, 0.02);
    border-color: rgba(255, 255, 255, 0.1);
    
    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      border-color: rgba(24, 144, 255, 0.4);
    }
  }

  .data-row {
    border-bottom-color: rgba(255, 255, 255, 0.05);
    
    &:hover {
      background: rgba(24, 144, 255, 0.08);
    }
  }

  .data-label {
    color: #aaa;
  }

  .data-value {
    color: #fff;
  }

  .empty-state {
    color: #666;
  }
  
  .monitoring-carousel {
    :deep(.n-carousel__dot) {
      background: rgba(255, 255, 255, 0.2);
    }
    
    :deep(.n-carousel__dot--active) {
      background: #1890ff;
    }
  }
}

// 动画效果
.carousel-item {
  animation: fadeInUp 0.4s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 数据值过渡动画
.data-value {
  transition: all 0.3s ease;
}
</style>
