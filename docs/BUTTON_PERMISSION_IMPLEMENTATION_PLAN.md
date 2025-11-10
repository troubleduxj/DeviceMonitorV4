# 按钮权限控制实施计划

## 📊 当前状态

- **已完成**：25个页面 (48%)
- **待实施**：重点关注10个高价值页面
- **预计工作量**：2-3小时

## 🎯 第一阶段实施清单（高优先级）

### 1. 统计报表模块（3个页面）

#### 1.1 焊接记录 (`statistics/weld-record`)
**当前状态**：使用 NButton  
**需要改造**：
- ✅ 已有导出按钮
- 🔧 需要替换为 PermissionButton

**操作**：
```vue
<!-- 第9-12行 -->
<!-- 替换前 -->
<NButton type="primary" @click="handleExport">
  <TheIcon icon="material-symbols:download" :size="16" class="mr-5" />
  导出记录
</NButton>

<!-- 替换后 -->
<PermissionButton 
  permission="GET /api/v2/statistics/weld-records/export"
  type="primary" 
  @click="handleExport"
>
  <TheIcon icon="material-symbols:download" :size="16" class="mr-5" />
  导出记录
</PermissionButton>
```

**需要添加的按钮权限**：
```javascript
{
  parentId: [焊接记录菜单ID],
  name: '导出焊接记录',
  perms: 'GET /api/v2/statistics/weld-records/export',
  icon: 'material-symbols:download',
  order: 1
}
```

#### 1.2 在线率统计 (`statistics/online-rate`)
**当前状态**：只有查询按钮  
**建议**：如果未来需要导出功能，可以预留权限

#### 1.3 焊接时长 (`statistics/weld-time`)
**当前状态**：待检查  
**操作**：类似焊接记录

---

### 2. 系统管理模块（4个页面）

#### 2.1 审计日志 (`system/auditlog`)
**需求分析**：
- 查看日志（已有权限控制在页面级别）
- 导出日志（需要添加按钮权限）

#### 2.2 API分组管理 (`system/api/groups`)
**需求分析**：
- 新建分组
- 编辑分组
- 删除分组

#### 2.3 主题管理 (`system/theme`)
**需求分析**：
- 切换主题（可能不需要权限控制）
- 自定义主题（可能需要）

#### 2.4 组件管理 (`system/components`)
**需求分析**：
- 启用/禁用组件
- 配置组件

---

### 3. 工作流管理模块（2个页面）

#### 3.1 工作流管理 (`flow-settings/workflow-manage`)
**需求分析**：
- 新建工作流
- 编辑工作流
- 删除工作流
- 发布工作流

#### 3.2 工作流设计 (`flow-settings/workflow-design`)
**需求分析**：
- 保存设计
- 发布工作流
- 导出工作流

---

### 4. 其他模块（3个页面）

#### 4.1 历史数据查询 (`device-monitor/history`)
**需求分析**：
- 导出数据

#### 4.2 报警分析 (`alarm/alarm-analysis`)
**需求分析**：
- 导出分析报告

#### 4.3 异常检测 (`ai-monitor/anomaly-detection`)
**需求分析**：
- 处理异常
- 导出异常记录

---

## 🚀 实施步骤

### 步骤1：快速实施统计报表模块（30分钟）

**焊接记录页面**：

1. 修改导入语句
```vue
<script setup>
// 添加导入
import PermissionButton from '@/components/Permission/PermissionButton.vue'
</script>
```

2. 替换导出按钮（见上方代码）

3. 创建按钮权限（执行脚本）
```javascript
// 在浏览器控制台执行
const token = localStorage.getItem('access_token');

// 查找焊接记录菜单ID
fetch('/api/v2/auth/user/menus', {
  headers: {'Authorization': 'Bearer ' + token}
}).then(r=>r.json()).then(data => {
  // 查找菜单
  function findMenu(items, name) {
    for(let item of items) {
      if(item.name === name) return item;
      if(item.children) {
        const found = findMenu(item.children, name);
        if(found) return found;
      }
    }
  }
  const menu = findMenu(data.data, '焊接记录');
  if(menu) {
    console.log('焊接记录菜单ID:', menu.id);
    
    // 创建按钮权限
    fetch('/api/v2/menus', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: '导出焊接记录',
        path: '',
        component: '',
        menu_type: 'button',
        icon: 'material-symbols:download',
        order_num: 1,
        parent_id: menu.id,
        perms: 'GET /api/v2/statistics/weld-records/export',
        visible: true,
        status: true,
        is_frame: false,
        is_cache: false
      })
    }).then(r=>r.json()).then(d => {
      console.log('创建结果:', d);
      alert('完成！请刷新页面查看');
    });
  }
});
```

### 步骤2：实施系统管理模块（1小时）

依次改造：
1. API分组管理
2. 审计日志
3. 主题管理（如需要）
4. 组件管理（如需要）

### 步骤3：实施其他模块（1小时）

依次改造：
1. 工作流管理
2. 历史数据查询
3. 报警分析
4. 异常检测

---

## ✅ 验证清单

每个页面改造完成后：

- [ ] 代码已修改（NButton → PermissionButton）
- [ ] 按钮权限已创建到数据库
- [ ] 在角色管理中可以看到按钮权限
- [ ] 分配权限后，按钮显示/隐藏正常
- [ ] 无权限时，按钮被禁用
- [ ] 控制台无错误

---

## 📝 建议的执行顺序

### 今天立即完成（30分钟）
1. ✅ 焊接记录页面改造
2. ✅ 验证效果

### 本周完成（2-3小时）
3. 系统管理模块改造
4. 工作流管理模块改造
5. 其他高优先级页面

### 可选（根据需求）
6. 中优先级页面
7. 低优先级页面

---

## 🎯 预期成果

完成第一阶段后：
- **权限控制覆盖率**：70%+ （35/52个页面）
- **核心业务页面**：100%覆盖
- **权限粒度**：细化到按钮级别
- **安全性**：显著提升

---

**下一步行动**：

请确认是否立即开始第一个页面（焊接记录）的改造？我可以帮您：
1. 自动修改代码
2. 生成创建权限的脚本
3. 指导测试验证

请回复 "开始" 或 "查看[具体页面名称]" 来继续！

