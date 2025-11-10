# Phase 3 实施指南 - 前端界面开发

> **项目**: 设备数据模型 - 元数据驱动架构  
> **阶段**: Phase 3 - 前端界面开发  
> **创建日期**: 2025-11-03  
> **预计完成**: Week 7-9 (3周)

---

## 📋 概述

Phase 3 的目标是开发完整的元数据管理和模型配置的可视化界面，为用户提供友好的数据模型管理体验。

### 总体进度

- ✅ Phase 1: 基础架构搭建 (100%)
- ✅ Phase 2: 动态模型实现 (100%)
- ⏳ Phase 3: 前端界面开发 (10%)
  - ✅ 菜单SQL脚本完成
  - ✅ 第一个页面骨架完成
  - ⏸️ 其他页面待开发

---

## 🎯 Phase 3 总体目标

### 功能目标
1. **菜单规划**: 新增"数据模型管理"一级菜单
2. **模型配置管理**: 可视化创建和编辑数据模型
3. **字段映射管理**: 管理PostgreSQL到TDengine的字段映射
4. **数据预览与测试**: 测试模型并预览数据

### 技术目标
- ✅ 复用现有 Naive UI 组件库
- ✅ 基于现有 RBAC 权限体系
- ✅ 不修改现有菜单和路由
- ✅ 保持与现有页面一致的视觉风格

---

## ✅ 已完成部分

### 1. 数据库菜单脚本 ✅

**文件**: `database/migrations/device-data-model/008_create_frontend_menu.sql`

**功能**:
- 创建一级菜单："数据模型管理"
- 创建3个子菜单：模型配置管理、字段映射管理、预览与测试
- 为 admin 角色分配菜单权限

**执行方法**:
```bash
# 方法1: 使用 psql
cd database/migrations/device-data-model
psql -h 127.0.0.1 -U postgres -d devicemonitor -f 008_create_frontend_menu.sql

# 方法2: 使用 Python 脚本（需要修改 execute_migration.py 添加此文件）
python execute_migration.py
```

**验证**:
```sql
-- 查看创建的菜单
SELECT * FROM t_menu WHERE path LIKE '/data-model%';

-- 查看 admin 角色权限
SELECT m.* 
FROM t_role_menu rm
JOIN t_menu m ON rm.menu_id = m.id
WHERE m.path LIKE '/data-model%';
```

### 2. 第一个前端页面 ✅

**文件**: `web/src/views/data-model/config/index.vue`

**功能**:
- 数据模型列表查询（分页、筛选）
- 新建/编辑数据模型
- 删除数据模型
- 激活/停用模型
- 字段选择（Transfer组件）

**特点**:
- 使用 Naive UI 组件
- 完整的表单验证
- 错误处理
- 响应式设计

---

## 📝 待开发部分

### Week 7 Part 2: 字段管理界面 (Day 3-5)

#### 任务 7.1: 字段映射管理页面

**文件**: `web/src/views/data-model/mapping/index.vue`

**功能需求**:
1. **字段映射列表**
   - 显示所有字段映射
   - 支持按设备类型、TDengine表筛选
   - 支持搜索（字段名、列名）
   - 分页显示

2. **新增/编辑映射**
   - 选择设备类型
   - 选择字段定义（DeviceField）
   - 配置TDengine数据库/表/列
   - 配置转换规则（6种类型）
   - 标记是否为TAG列

3. **转换规则配置器**
   - 表达式转换：输入框 + 语法提示
   - 映射转换：键值对编辑器
   - 范围限制：min/max 输入
   - 单位转换：from/to + factor
   - 四舍五入：decimals 输入
   - 组合转换：多个规则组合

**UI布局**:
```vue
<template>
  <div class="field-mapping">
    <!-- 查询条件 -->
    <n-card>
      <n-space>
        <n-input placeholder="搜索字段或列名" />
        <n-select placeholder="设备类型" />
        <n-select placeholder="TDengine表" />
        <n-button type="primary">查询</n-button>
        <n-button>重置</n-button>
        <n-button type="success">新增映射</n-button>
      </n-space>
    </n-card>

    <!-- 映射列表 -->
    <n-card>
      <n-data-table :columns="columns" :data="mappings" />
    </n-card>

    <!-- 新增/编辑对话框 -->
    <n-modal v-model:show="showModal">
      <n-form>
        <n-form-item label="设备类型">
          <n-select />
        </n-form-item>
        <n-form-item label="字段定义">
          <n-select />
        </n-form-item>
        <n-form-item label="TDengine数据库">
          <n-input />
        </n-form-item>
        <n-form-item label="TDengine表">
          <n-input />
        </n-form-item>
        <n-form-item label="TDengine列">
          <n-input />
        </n-form-item>
        <n-form-item label="是否TAG列">
          <n-switch />
        </n-form-item>
        <n-form-item label="转换规则">
          <transform-rule-editor v-model="transformRule" />
        </n-form-item>
      </n-form>
    </n-modal>
  </div>
</template>
```

**API调用**:
- `GET /api/v2/metadata/mappings` - 查询映射列表
- `POST /api/v2/metadata/mappings` - 创建映射
- `PUT /api/v2/metadata/mappings/{id}` - 更新映射
- `DELETE /api/v2/metadata/mappings/{id}` - 删除映射

---

### Week 8: 模型配置界面 (Day 1-5)

#### 任务 8.1: 模型配置向导

**文件**: `web/src/views/data-model/config/wizard.vue`

**功能需求**:
1. **步骤1: 基本信息**
   - 模型名称
   - 模型代码
   - 设备类型
   - 模型类型（realtime/statistics/ai_analysis）
   - 版本号
   - 说明

2. **步骤2: 字段选择**
   - 左侧：可用字段列表（按分类分组）
   - 右侧：已选字段列表（可拖拽排序）
   - 字段详情预览
   - 批量操作

3. **步骤3: 聚合配置**（仅 statistics 类型）
   - 时间窗口（interval）
   - 聚合方法（AVG, SUM, MAX, MIN等）
   - 分组字段（group_by）

4. **步骤4: AI配置**（仅 ai_analysis 类型）
   - 算法选择
   - 特征字段
   - 归一化方法
   - 窗口大小

5. **步骤5: SQL预览**
   - 显示生成的SQL
   - 支持复制
   - 支持测试执行

6. **步骤6: 测试运行**
   - 输入测试参数
   - 执行查询
   - 显示结果
   - 性能指标

**UI布局**:
```vue
<template>
  <div class="model-wizard">
    <n-steps :current="currentStep" :status="stepStatus">
      <n-step title="基本信息" />
      <n-step title="字段选择" />
      <n-step title="配置选项" />
      <n-step title="SQL预览" />
      <n-step title="测试运行" />
      <n-step title="完成" />
    </n-steps>

    <!-- 步骤内容 -->
    <n-card class="step-content">
      <component :is="currentStepComponent" v-model="modelData" />
    </n-card>

    <!-- 操作按钮 -->
    <n-space justify="end">
      <n-button @click="handlePrev" v-if="currentStep > 0">上一步</n-button>
      <n-button type="primary" @click="handleNext">
        {{ currentStep < 5 ? '下一步' : '完成' }}
      </n-button>
    </n-space>
  </div>
</template>
```

#### 任务 8.2: 字段选择器组件

**文件**: `web/src/components/data-model/FieldSelector.vue`

**功能**:
- 拖拽排序
- 字段详情预览
- 字段配置（权重、别名、必填项）
- 批量操作

---

### Week 9: 数据预览与测试 (Day 1-5)

#### 任务 9.1: 数据预览页面

**文件**: `web/src/views/data-model/preview/index.vue`

**功能需求**:
1. **模型选择**
   - 下拉选择数据模型
   - 显示模型信息（名称、类型、字段数）

2. **查询参数配置**
   - 设备编码（可选）
   - 时间范围（日期选择器）
   - 额外筛选条件（动态表单）
   - 分页参数（页码、每页记录数）

3. **实时数据预览**
   - 表格显示查询结果
   - 支持列排序
   - 支持导出（Excel/CSV）
   - 显示执行时间

4. **统计数据预览**
   - 配置时间间隔（interval）
   - 配置分组字段（group_by）
   - 图表展示（ECharts）
   - 表格展示

5. **SQL查看**
   - 显示生成的SQL
   - 支持复制
   - 语法高亮

6. **执行日志**
   - 显示最近的执行记录
   - 查看执行参数
   - 查看执行结果
   - 查看错误信息

**UI布局**:
```vue
<template>
  <div class="data-preview">
    <!-- 左侧：模型选择和参数配置 -->
    <n-layout-sider width="350px" bordered>
      <n-card title="模型选择">
        <n-select v-model:value="selectedModel" :options="modelOptions" />
      </n-card>

      <n-card title="查询参数">
        <n-form>
          <n-form-item label="设备编码">
            <n-input v-model:value="queryParams.device_code" />
          </n-form-item>
          <n-form-item label="时间范围">
            <n-date-picker v-model:value="queryParams.timeRange" type="datetimerange" />
          </n-form-item>
          <!-- 更多参数... -->
        </n-form>

        <n-button type="primary" block @click="handleQuery">
          执行查询
        </n-button>
      </n-card>

      <n-card title="SQL预览">
        <n-code :code="generatedSQL" language="sql" />
        <n-button text @click="handleCopySQL">复制</n-button>
      </n-card>
    </n-layout-sider>

    <!-- 右侧：查询结果 -->
    <n-layout-content>
      <n-tabs type="line">
        <n-tab-pane name="table" tab="表格视图">
          <n-data-table :columns="resultColumns" :data="resultData" />
        </n-tab-pane>
        
        <n-tab-pane name="chart" tab="图表视图" v-if="isStatistics">
          <div ref="chartRef" style="height: 500px"></div>
        </n-tab-pane>
        
        <n-tab-pane name="logs" tab="执行日志">
          <execution-log-list :model-id="selectedModelId" />
        </n-tab-pane>
      </n-tabs>
    </n-layout-content>
  </div>
</template>
```

**API调用**:
- `POST /api/v2/data/query/realtime` - 实时数据查询
- `POST /api/v2/data/query/statistics` - 统计数据查询
- `GET /api/v2/data/models/{model_code}/preview` - 快速预览
- `GET /api/v2/metadata/execution-logs` - 执行日志

#### 任务 9.2: 执行日志组件

**文件**: `web/src/components/data-model/ExecutionLogList.vue`

**功能**:
- 显示执行历史
- 筛选（状态、时间范围）
- 查看详情（参数、结果、SQL）
- 性能分析

---

## 🔧 通用组件开发

### 1. 转换规则编辑器

**文件**: `web/src/components/data-model/TransformRuleEditor.vue`

**功能**:
- 选择转换类型（6种）
- 根据类型显示不同的配置表单
- 实时预览转换效果
- 语法验证

**使用示例**:
```vue
<transform-rule-editor
  v-model="transformRule"
  :test-value="100"
  @update:modelValue="handleRuleChange"
/>
```

### 2. 字段详情预览

**文件**: `web/src/components/data-model/FieldDetail.vue`

**功能**:
- 显示字段基本信息
- 显示字段类型和单位
- 显示数据范围
- 显示报警阈值
- 显示显示配置

### 3. SQL 语法高亮

**文件**: `web/src/components/data-model/SQLHighlight.vue`

**功能**:
- SQL语法高亮显示
- 支持复制
- 支持格式化
- 支持执行（可选）

---

## 🎨 UI设计规范

### 颜色主题
- 主色调：#18a058（绿色）- Naive UI 默认
- 信息色：#2080f0（蓝色）
- 警告色：#f0a020（橙色）
- 错误色：#d03050（红色）
- 成功色：#18a058（绿色）

### 间距
- 页面padding: 16px
- 卡片margin: 16px
- 表单项margin: 16px
- 按钮间距: 8px

### 字体
- 标题：font-size: 16px, font-weight: 600
- 正文：font-size: 14px, font-weight: 400
- 小字：font-size: 12px, font-weight: 400

### 响应式设计
- 表格：自适应宽度，超出滚动
- 表单：最小宽度 600px
- 卡片：最大宽度 1400px

---

## 📡 API 集成

### API Client 配置

**文件**: `web/src/api/v2/data-model.js`

```javascript
import { apiV2Client } from '@/utils/http'

export const dataModelApi = {
  // 模型管理
  getModels(params) {
    return apiV2Client.get('/metadata/models', { params })
  },
  
  getModel(id) {
    return apiV2Client.get(`/metadata/models/${id}`)
  },
  
  createModel(data) {
    return apiV2Client.post('/metadata/models', data)
  },
  
  updateModel(id, data) {
    return apiV2Client.put(`/metadata/models/${id}`, data)
  },
  
  deleteModel(id) {
    return apiV2Client.delete(`/metadata/models/${id}`)
  },
  
  activateModel(id) {
    return apiV2Client.post(`/metadata/models/${id}/activate`)
  },
  
  // 字段管理
  getFields(params) {
    return apiV2Client.get('/metadata/fields', { params })
  },
  
  getField(id) {
    return apiV2Client.get(`/metadata/fields/${id}`)
  },
  
  createField(data) {
    return apiV2Client.post('/metadata/fields', data)
  },
  
  updateField(id, data) {
    return apiV2Client.put(`/metadata/fields/${id}`, data)
  },
  
  deleteField(id) {
    return apiV2Client.delete(`/metadata/fields/${id}`)
  },
  
  // 字段映射
  getMappings(params) {
    return apiV2Client.get('/metadata/mappings', { params })
  },
  
  getMapping(id) {
    return apiV2Client.get(`/metadata/mappings/${id}`)
  },
  
  createMapping(data) {
    return apiV2Client.post('/metadata/mappings', data)
  },
  
  updateMapping(id, data) {
    return apiV2Client.put(`/metadata/mappings/${id}`, data)
  },
  
  deleteMapping(id) {
    return apiV2Client.delete(`/metadata/mappings/${id}`)
  },
  
  // 数据查询
  queryRealtimeData(data) {
    return apiV2Client.post('/data/query/realtime', data)
  },
  
  queryStatisticsData(data) {
    return apiV2Client.post('/data/query/statistics', data)
  },
  
  previewModel(modelCode, params) {
    return apiV2Client.get(`/data/models/${modelCode}/preview`, { params })
  },
  
  // 动态模型
  generateModel(params) {
    return apiV2Client.post('/dynamic-models/generate', null, { params })
  },
  
  getFieldsInfo(params) {
    return apiV2Client.get('/dynamic-models/fields-info', { params })
  },
  
  validateData(modelCode, data) {
    return apiV2Client.post('/dynamic-models/validate', data, {
      params: { model_code: modelCode }
    })
  },
  
  // 执行日志
  getExecutionLogs(params) {
    return apiV2Client.get('/metadata/execution-logs', { params })
  },
  
  getExecutionLog(id) {
    return apiV2Client.get(`/metadata/execution-logs/${id}`)
  }
}
```

---

## ✅ 验收标准

### Week 7 验收
- [x] 数据库菜单创建成功
- [ ] admin 用户可见新菜单
- [ ] 模型配置管理页面基本功能完成
- [ ] 字段映射管理页面完成

### Week 8 验收
- [ ] 模型配置向导完成（6个步骤）
- [ ] 字段选择器支持拖拽排序
- [ ] SQL预览功能完成
- [ ] 模型测试功能完成

### Week 9 验收
- [ ] 数据预览页面完成
- [ ] 支持实时和统计查询
- [ ] 图表展示完成
- [ ] 执行日志查看完成
- [ ] 导出功能完成

---

## 🚀 快速开始

### 1. 执行数据库脚本

```bash
cd database/migrations/device-data-model
psql -h 127.0.0.1 -U postgres -d devicemonitor -f 008_create_frontend_menu.sql
```

### 2. 创建API文件

```bash
# 创建API目录
mkdir -p web/src/api/v2

# 创建data-model.js
touch web/src/api/v2/data-model.js
```

### 3. 完善第一个页面

**参考文件**: `web/src/views/data-model/config/index.vue`

需要补充的功能：
- [ ] 添加导出功能
- [ ] 添加批量操作
- [ ] 优化转换规则编辑器
- [ ] 添加模型复制功能

### 4. 开发其他页面

按照本文档的任务列表，逐个完成字段映射管理、数据预览等页面。

---

## 📚 参考资料

### 内部文档
- [00-设计方案总览](./00-设计方案总览.md)
- [02-架构设计](./02-架构设计.md)
- [06-实施计划](./06-实施计划.md)
- [08-前端菜单规划建议](./08-前端菜单规划建议.md)
- [API接口文档](./API接口文档.md)
- [Phase1完成报告](./Phase1完成报告.md)
- [Phase2完成报告](./Phase2完成报告.md)

### 技术文档
- [Vue 3 文档](https://cn.vuejs.org/)
- [Naive UI 文档](https://www.naiveui.com/)
- [ECharts 文档](https://echarts.apache.org/zh/index.html)
- [VueUse 文档](https://vueuse.org/)

### 现有代码参考
- 设备管理页面：`web/src/views/device/manage/index.vue`
- 报警信息页面：`web/src/views/alarm/alarm-info/index.vue`
- 统计分析页面：`web/src/views/statistics/weld-record/index.vue`

---

## 🔍 故障排查

### 问题 1: 菜单不显示

**原因**:
- 数据库菜单未创建
- 用户角色没有权限
- 前端缓存未清除

**解决方法**:
```sql
-- 检查菜单是否存在
SELECT * FROM t_menu WHERE path LIKE '/data-model%';

-- 检查用户权限
SELECT m.* 
FROM t_role_menu rm
JOIN t_menu m ON rm.menu_id = m.id
JOIN t_role r ON rm.role_id = r.id
WHERE r.role_code = 'admin' AND m.path LIKE '/data-model%';
```

清除浏览器缓存，重新登录。

### 问题 2: API 调用失败

**原因**:
- 后端服务未启动
- API 路由未注册
- 跨域配置问题

**解决方法**:
```bash
# 检查后端服务
curl http://localhost:8000/api/v2/metadata/models

# 查看API文档
# 访问 http://localhost:8000/docs
```

### 问题 3: 页面路由404

**原因**:
- 路由未注册
- 菜单path配置错误
- 组件文件路径错误

**解决方法**:
检查菜单path和组件文件是否匹配：
- 菜单: `/data-model/config`
- 文件: `web/src/views/data-model/config/index.vue`

---

## 📝 开发检查清单

### 开发前
- [ ] 阅读完整设计文档
- [ ] 了解现有页面结构
- [ ] 熟悉 Naive UI 组件
- [ ] 配置开发环境

### 开发中
- [ ] 遵循代码规范
- [ ] 使用TypeScript类型注解
- [ ] 添加错误处理
- [ ] 优化用户体验

### 开发后
- [ ] 单元测试
- [ ] 集成测试
- [ ] 浏览器兼容性测试
- [ ] 性能优化
- [ ] 文档更新

---

## ✅ 结论

Phase 3 的前端开发工作量较大，建议：

1. **分阶段开发**: 按照 Week 7 → Week 8 → Week 9 的顺序逐步完成
2. **优先级**: 先完成核心功能（模型配置、数据预览），再完善辅助功能
3. **复用组件**: 尽量复用现有组件和样式，保持界面一致性
4. **及时测试**: 每完成一个页面就进行测试，确保功能正常

**预计工作量**: 15-20个工作日（1名前端工程师）

---

**文档版本**: 1.0  
**最后更新**: 2025-11-03  
**状态**: ⏳ Phase 3 进行中 (10%)

