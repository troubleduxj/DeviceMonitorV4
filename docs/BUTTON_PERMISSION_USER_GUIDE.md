# 按钮权限初始化 - 用户操作指南

## 🎯 快速开始

### 步骤1：初始化按钮权限

打开浏览器控制台（F12），粘贴并执行以下代码：

```javascript
console.log('🚀 开始初始化按钮权限...\n');

const token = localStorage.getItem('access_token');

if (!token) {
  console.error('❌ 未找到 access_token，请先登录！');
} else {
  fetch('/api/v2/system/init-button-permissions', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    }
  })
  .then(res => res.json())
  .then(data => {
    console.log('='.repeat(60));
    console.log('📊 初始化结果');
    console.log('='.repeat(60));
    
    if (data.code === 200) {
      console.log(`✅ 成功创建: ${data.data.created} 个按钮权限`);
      console.log(`⏭️ 已跳过: ${data.data.skipped} 个（已存在）`);
      console.log(`📋 当前总数: ${data.data.total_buttons} 个按钮权限`);
      console.log('\n详细信息:');
      console.table(data.data.details);
      
      alert(
        '✅ 初始化成功！\n\n' +
        `新创建: ${data.data.created} 个\n` +
        `已跳过: ${data.data.skipped} 个\n` +
        `总按钮数: ${data.data.total_buttons} 个\n\n` +
        '📌 下一步操作：\n' +
        '1. 刷新页面（F5）\n' +
        '2. 进入: 系统管理 → 角色管理\n' +
        '3. 点击"分配权限" → "菜单权限"\n' +
        '4. 展开菜单查看按钮权限'
      );
    } else {
      console.error('❌ 初始化失败:', data.message);
      alert('❌ 初始化失败: ' + data.message);
    }
    
    console.log('='.repeat(60));
  })
  .catch(err => {
    console.error('❌ 请求错误:', err);
    alert('❌ 请求失败: ' + err.message);
  });
}
```

### 步骤2：刷新页面

按 `F5` 刷新浏览器页面。

### 步骤3：配置角色权限

1. 导航到：**系统管理 → 角色管理**
2. 找到要配置的角色，点击 **"分配权限"** 按钮
3. 切换到 **"菜单权限"** 标签页
4. 展开菜单节点，例如：
   ```
   📁 系统管理
     📁 用户管理
       🔘 新建用户 [POST]
       🔘 编辑用户 [PUT]
       🔘 删除用户 [DELETE]
       🔘 重置密码 [POST]
       🔘 批量删除用户 [DELETE]
       🔘 导出用户 [GET]
   ```
5. 勾选需要分配的按钮权限
6. 点击 **"保存"** 按钮

### 步骤4：验证权限

1. 使用不同权限的用户登录系统
2. 查看对应页面的按钮是否正确显示/隐藏
3. 测试按钮操作是否被正确控制

---

## 📋 新增的按钮权限清单

### 统计报表模块

#### 焊接记录
- 🔘 **导出焊接记录** - `GET /api/v2/statistics/weld-records/export`

#### 焊接时长
- 🔘 **导出焊接时长** - `GET /api/v2/statistics/weld-time/export`

#### 在线率统计
- 🔘 **导出在线率** - `GET /api/v2/statistics/online-rate/export`

### 系统管理模块

#### 审计日志
- 🔘 **导出日志** - `GET /api/v2/audit-logs/export`

#### API分组管理
- 🔘 **新建API分组** - `POST /api/v2/api-groups`
- 🔘 **编辑API分组** - `PUT /api/v2/api-groups/{id}`
- 🔘 **删除API分组** - `DELETE /api/v2/api-groups/{id}`

### 工作流管理模块

#### 工作流管理
- 🔘 **新建工作流** - `POST /api/v2/workflows`
- 🔘 **编辑工作流** - `PUT /api/v2/workflows/{id}`
- 🔘 **删除工作流** - `DELETE /api/v2/workflows/{id}`
- 🔘 **发布工作流** - `POST /api/v2/workflows/{id}/publish`

#### 工作流设计
- 🔘 **保存工作流** - `POST /api/v2/workflows/save`
- 🔘 **发布工作流** - `POST /api/v2/workflows/publish`
- 🔘 **导出工作流** - `GET /api/v2/workflows/export`

### 设备监测模块

#### 历史数据查询
- 🔘 **导出历史数据** - `GET /api/v2/device-monitor/history/export`

### 报警管理模块

#### 报警分析
- 🔘 **导出报警分析** - `GET /api/v2/alarms/analysis/export`

### AI监控模块

#### 异常检测
- 🔘 **处理异常** - `POST /api/v2/ai-monitor/anomalies/{id}/handle`
- 🔘 **导出异常记录** - `GET /api/v2/ai-monitor/anomalies/export`

---

## ❓ 常见问题

### Q1: 执行脚本提示 "未找到 access_token"？
**A:** 请先登录系统，然后再执行脚本。

### Q2: 初始化后在角色管理中看不到按钮权限？
**A:** 
1. 检查是否刷新了页面（F5）
2. 检查控制台是否显示创建成功
3. 检查菜单名称是否匹配（见完成报告）

### Q3: 某些菜单下没有按钮权限？
**A:** 可能的原因：
- 该页面暂时没有需要权限控制的按钮
- 菜单名称在数据库中与配置不匹配
- 父菜单不存在

### Q4: 如何为新页面添加按钮权限？
**A:** 
1. 在 `app/api/v2/init_button_permissions.py` 中添加配置
2. 重新执行初始化脚本
3. 在页面代码中使用 `PermissionButton` 组件

### Q5: 超级管理员看不到按钮？
**A:** 
1. 检查用户是否确实是超级管理员（`is_superuser = true`）
2. 清除浏览器缓存
3. 重新登录

---

## 🔍 验证清单

在角色管理的"菜单权限"中，您应该能看到以下菜单展开后的按钮：

- ✅ **用户管理** - 6个按钮
- ✅ **角色管理** - 4个按钮
- ✅ **菜单管理** - 3个按钮
- ✅ **部门管理** - 3个按钮
- ✅ **设备信息管理** - 4个按钮
- ✅ **设备分类管理** - 3个按钮
- ✅ **维修记录** - 4个按钮
- ✅ **字典类型** - 3个按钮
- ✅ **字典数据** - 3个按钮
- ✅ **焊接记录** - 1个按钮
- ✅ **焊接时长** - 1个按钮（预留）
- ✅ **在线率统计** - 1个按钮（预留）
- ✅ **审计日志** - 1个按钮（预留）
- ✅ **API分组** - 3个按钮（预留）
- ✅ **工作流管理** - 4个按钮（预留）
- ✅ **工作流设计** - 3个按钮（预留）
- ✅ **历史数据** - 1个按钮（预留）
- ✅ **报警分析** - 1个按钮（预留）
- ✅ **异常检测** - 2个按钮（预留）

**注**：标记为"预留"的按钮权限已配置到后端，但前端页面可能暂未实现对应功能。

---

## 📞 技术支持

如遇到问题，请查看：
- 📄 完整报告：`docs/BUTTON_PERMISSION_COMPLETION_REPORT.md`
- 📄 审计报告：`docs/BUTTON_PERMISSION_PAGE_AUDIT.md`
- 📄 实施计划：`docs/BUTTON_PERMISSION_IMPLEMENTATION_PLAN.md`

或联系系统管理员。

---

**最后更新**：2025-10-30

