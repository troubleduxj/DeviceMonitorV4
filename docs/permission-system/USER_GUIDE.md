# 权限系统使用指南

## 概述

本指南将帮助您快速了解和使用权限系统，包括基本概念、功能特性、使用方法和常见问题解决方案。

## 目录

- [基本概念](#基本概念)
- [快速开始](#快速开始)
- [用户管理](#用户管理)
- [角色管理](#角色管理)
- [权限配置](#权限配置)
- [前端集成](#前端集成)
- [常见问题](#常见问题)

## 基本概念

### 权限模型

本系统采用基于角色的访问控制（RBAC）模型：

```
用户 (User) ←→ 角色 (Role) ←→ 权限 (Permission)
```

- **用户 (User)**: 系统的使用者
- **角色 (Role)**: 权限的集合，用户通过角色获得权限
- **权限 (Permission)**: 对系统资源的访问控制

### 权限类型

1. **菜单权限**: 控制用户可以访问哪些页面和菜单
2. **API权限**: 控制用户可以调用哪些API接口
3. **按钮权限**: 控制页面上按钮的显示和功能
4. **数据权限**: 控制用户可以访问哪些数据范围

### 权限继承

- 用户可以拥有多个角色
- 用户的最终权限是所有角色权限的并集
- 超级用户拥有所有权限

## 快速开始

### 1. 系统登录

访问系统登录页面，输入用户名和密码：

```
URL: http://your-domain.com/login
默认管理员账号: admin
默认密码: admin123
```

### 2. 首次配置

登录后，建议按以下步骤进行初始配置：

1. **修改默认密码**
   - 进入个人中心 → 修改密码
   - 设置强密码（至少8位，包含字母、数字、特殊字符）

2. **创建角色**
   - 进入系统管理 → 角色管理
   - 创建适合您组织的角色（如：部门管理员、普通用户等）

3. **分配权限**
   - 为每个角色分配相应的菜单权限和API权限
   - 遵循最小权限原则

4. **创建用户**
   - 进入系统管理 → 用户管理
   - 为团队成员创建账号并分配角色

### 3. 权限验证

系统会自动验证用户权限：
- 页面访问权限：无权限的页面会跳转到403错误页
- API调用权限：无权限的API调用会返回403错误
- 按钮显示权限：无权限的按钮会自动隐藏

## 用户管理

### 创建用户

1. 进入 **系统管理 → 用户管理**
2. 点击 **新增用户** 按钮
3. 填写用户信息：
   - 用户名：唯一标识，不可重复
   - 邮箱：用于找回密码和通知
   - 昵称：显示名称
   - 密码：初始密码
   - 状态：启用/禁用
   - 角色：选择用户角色

### 编辑用户

1. 在用户列表中找到目标用户
2. 点击 **编辑** 按钮
3. 修改用户信息并保存

### 重置密码

管理员可以为用户重置密码：
1. 在用户列表中找到目标用户
2. 点击 **重置密码** 按钮
3. 输入新密码并确认

### 用户状态管理

- **启用**: 用户可以正常登录和使用系统
- **禁用**: 用户无法登录，现有会话会被终止

### 批量操作

支持批量操作用户：
- 批量启用/禁用
- 批量删除
- 批量分配角色

## 角色管理

### 创建角色

1. 进入 **系统管理 → 角色管理**
2. 点击 **新增角色** 按钮
3. 填写角色信息：
   - 角色名称：显示名称
   - 角色标识：唯一标识，用于代码中的权限判断
   - 描述：角色说明
   - 状态：启用/禁用

### 分配权限

#### 菜单权限分配
1. 编辑角色
2. 在 **菜单权限** 标签页中
3. 勾选角色可以访问的菜单项
4. 支持父子菜单的级联选择

#### API权限分配
1. 编辑角色
2. 在 **API权限** 标签页中
3. 按模块勾选API权限
4. 可以按权限类型筛选（查看、创建、更新、删除）

### 角色层级

建议按组织结构创建角色层级：

```
超级管理员 (admin)
├── 系统管理员 (system_admin)
├── 部门管理员 (dept_admin)
│   ├── 人事管理员 (hr_admin)
│   ├── 财务管理员 (finance_admin)
│   └── 技术管理员 (tech_admin)
└── 普通用户 (user)
    ├── 人事专员 (hr_user)
    ├── 财务专员 (finance_user)
    └── 技术专员 (tech_user)
```

### 权限模板

系统提供常用的权限模板：

1. **查看权限模板**
   - 只能查看数据，不能修改
   - 适用于只读用户

2. **操作权限模板**
   - 可以查看和修改数据
   - 适用于业务操作人员

3. **管理权限模板**
   - 拥有完整的CRUD权限
   - 适用于管理人员

## 权限配置

### 菜单权限配置

#### 菜单结构
```
系统管理 (system)
├── 用户管理 (system:user)
│   ├── 查看用户 (system:user:view)
│   ├── 创建用户 (system:user:create)
│   ├── 编辑用户 (system:user:update)
│   └── 删除用户 (system:user:delete)
├── 角色管理 (system:role)
└── 菜单管理 (system:menu)
```

#### 权限标识规范
- 格式：`模块:功能:操作`
- 示例：`system:user:view`（系统模块-用户功能-查看操作）
- 层级：支持多级权限继承

### API权限配置

#### 自动发现
系统可以自动发现API端点：
1. 进入 **系统管理 → API管理**
2. 点击 **同步API** 按钮
3. 系统会扫描所有API端点并自动注册

#### 手动配置
也可以手动添加API权限：
1. 点击 **新增API** 按钮
2. 填写API信息：
   - API标识：权限标识
   - 请求路径：API路径
   - 请求方法：GET/POST/PUT/DELETE
   - 描述：API说明

### 权限验证规则

#### 白名单路径
以下路径不需要权限验证：
- `/api/v2/auth/login` - 登录接口
- `/api/v2/auth/refresh` - 刷新令牌
- `/health` - 健康检查
- `/docs` - API文档

#### 超级用户
超级用户拥有所有权限，跳过权限检查。

#### 权限匹配规则
1. 精确匹配：完全匹配API路径和方法
2. 模糊匹配：支持路径参数匹配
3. 权限继承：拥有父权限自动拥有子权限

## 前端集成

### Vue.js 集成

#### 1. 安装权限组件
```javascript
// main.js
import { createApp } from 'vue'
import PermissionComponents from '@/components/Permission'

const app = createApp(App)
app.use(PermissionComponents)
```

#### 2. 使用权限按钮
```vue
<template>
  <!-- 基础用法 -->
  <PermissionButton permission="system:user:create">
    新增用户
  </PermissionButton>
  
  <!-- 多权限（任一满足） -->
  <PermissionButton :permissions="['system:user:update', 'system:user:delete']">
    编辑用户
  </PermissionButton>
  
  <!-- 多权限（全部满足） -->
  <PermissionButton 
    :permissions="['system:user:view', 'system:user:update']"
    require-all
  >
    高级编辑
  </PermissionButton>
</template>
```

#### 3. 使用权限指令
```vue
<template>
  <!-- 隐藏无权限元素 -->
  <div v-permission="'system:user:view'">
    用户信息
  </div>
  
  <!-- 禁用无权限元素 -->
  <button v-permission:disable="'system:user:delete'">
    删除用户
  </button>
  
  <!-- 多权限指令 -->
  <div v-permission:any="['system:user:view', 'system:user:update']">
    用户操作区域
  </div>
</template>
```

#### 4. 路由权限守卫
```javascript
// router/index.js
import { usePermissionStore } from '@/stores/permission'

router.beforeEach(async (to, from, next) => {
  const permissionStore = usePermissionStore()
  
  // 检查路由权限
  if (to.meta.requiresAuth) {
    if (!permissionStore.isAuthenticated) {
      next('/login')
      return
    }
    
    if (to.meta.permission && !permissionStore.hasPermission(to.meta.permission)) {
      next('/403')
      return
    }
  }
  
  next()
})
```

#### 5. 权限Store使用
```javascript
// 在组件中使用
import { usePermissionStore } from '@/stores/permission'

export default {
  setup() {
    const permissionStore = usePermissionStore()
    
    // 检查单个权限
    const canView = permissionStore.hasPermission('system:user:view')
    
    // 检查多个权限（任一满足）
    const canEdit = permissionStore.hasAnyPermission([
      'system:user:update',
      'system:user:delete'
    ])
    
    // 检查多个权限（全部满足）
    const canManage = permissionStore.hasAllPermissions([
      'system:user:view',
      'system:user:update'
    ])
    
    // 获取用户菜单
    const menus = permissionStore.userMenus
    
    return {
      canView,
      canEdit,
      canManage,
      menus
    }
  }
}
```

### React 集成

#### 1. 权限Hook
```javascript
// hooks/usePermission.js
import { useSelector } from 'react-redux'

export const usePermission = () => {
  const permissions = useSelector(state => state.auth.permissions)
  
  const hasPermission = (permission) => {
    return permissions.includes(permission)
  }
  
  const hasAnyPermission = (permissionList) => {
    return permissionList.some(permission => permissions.includes(permission))
  }
  
  const hasAllPermissions = (permissionList) => {
    return permissionList.every(permission => permissions.includes(permission))
  }
  
  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions
  }
}
```

#### 2. 权限组件
```javascript
// components/PermissionButton.jsx
import React from 'react'
import { usePermission } from '@/hooks/usePermission'

const PermissionButton = ({ 
  permission, 
  permissions, 
  requireAll = false, 
  children, 
  ...props 
}) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermission()
  
  let hasAccess = false
  
  if (permission) {
    hasAccess = hasPermission(permission)
  } else if (permissions) {
    hasAccess = requireAll 
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions)
  }
  
  if (!hasAccess) {
    return null
  }
  
  return <button {...props}>{children}</button>
}

export default PermissionButton
```

## 常见问题

### Q1: 用户无法登录怎么办？

**A**: 检查以下几点：
1. 确认用户名和密码正确
2. 检查用户状态是否为启用
3. 查看系统日志是否有错误信息
4. 确认JWT配置是否正确

### Q2: 用户登录后看不到菜单怎么办？

**A**: 可能的原因：
1. 用户没有分配角色
2. 角色没有分配菜单权限
3. 菜单状态为禁用
4. 前端菜单组件配置错误

### Q3: API调用返回403错误怎么办？

**A**: 检查步骤：
1. 确认用户已登录且令牌有效
2. 检查用户角色是否有对应API权限
3. 确认API权限配置是否正确
4. 查看权限中间件日志

### Q4: 如何批量导入用户？

**A**: 可以通过以下方式：
1. 使用API批量创建用户
2. 准备Excel模板文件
3. 通过管理界面的导入功能
4. 编写脚本调用API接口

### Q5: 如何备份和恢复权限配置？

**A**: 建议方案：
1. 定期备份数据库
2. 导出权限配置为JSON文件
3. 使用版本控制管理配置文件
4. 建立配置变更审批流程

### Q6: 权限系统性能优化建议？

**A**: 优化策略：
1. 启用Redis缓存
2. 合理设置缓存过期时间
3. 使用批量权限检查
4. 优化数据库查询
5. 监控系统性能指标

### Q7: 如何处理权限冲突？

**A**: 处理原则：
1. 权限采用并集模式（拥有任一角色权限即可）
2. 明确权限优先级
3. 避免权限重复分配
4. 定期审查权限配置

### Q8: 如何实现数据权限控制？

**A**: 实现方案：
1. 在数据模型中添加部门字段
2. 在查询时添加数据权限过滤
3. 使用中间件自动处理数据权限
4. 配置数据权限规则

## 最佳实践

### 1. 权限设计原则

- **最小权限原则**: 用户只获得完成工作所需的最小权限
- **职责分离**: 不同职责的操作分配给不同角色
- **权限审查**: 定期审查和清理不必要的权限
- **权限文档**: 维护清晰的权限文档和变更记录

### 2. 角色设计建议

- **按职能划分**: 根据实际工作职能设计角色
- **层级清晰**: 建立清晰的角色层级关系
- **权限聚合**: 将相关权限聚合到同一角色
- **灵活组合**: 支持用户拥有多个角色

### 3. 安全建议

- **强密码策略**: 要求用户使用强密码
- **定期更换**: 定期更换密码和密钥
- **会话管理**: 合理设置会话超时时间
- **审计日志**: 记录所有权限相关操作
- **异常监控**: 监控异常登录和权限访问

### 4. 运维建议

- **监控告警**: 设置权限系统监控告警
- **性能优化**: 定期优化权限查询性能
- **备份恢复**: 建立完善的备份恢复机制
- **版本管理**: 对权限配置进行版本管理

## 技术支持

如需技术支持，请联系：

- **邮箱**: support@example.com
- **文档**: https://docs.example.com
- **社区**: https://community.example.com
- **GitHub**: https://github.com/example/permission-system

---

**文档版本**: v2.0  
**最后更新**: 2025-10-10  
**适用版本**: 权限系统 v2.0+