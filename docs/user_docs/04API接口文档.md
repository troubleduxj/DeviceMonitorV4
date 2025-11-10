
## 概述
 
本文档描述了设备监控系统的所有API接口，基于FastAPI框架构建，提供RESTful风格的API服务。
 
### 基础信息
  
- **API版本**: v1

- **基础URL**: `/api/v1`

- **认证方式**: JWT Token

- **数据格式**: JSON
  
### 通用响应格式

#### 成功响应

```json
{
  "code": 200,
  "msg": "OK",
  "data": {}
}
```
#### 分页响应

```json
{
  "code": 200,
  "msg": "OK",
  "data": [],
  "total": 100,
  "page": 1,
  "page_size": 10
}
```
 
#### 错误响应

```json
{
  "code": 400,
  "msg": "错误信息",
  "data": null
}
```
## 认证相关接口
### 1. 获取访问令牌
 
**接口地址**: `POST /api/v1/base/access_token`
  
**接口描述**: 用户登录获取JWT访问令牌
  
**请求参数**:

```json
{
  "username": "用户名",
  "password": "密码"
}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
  }
}
```
  
### 2. 获取用户信息
  
**接口地址**: `GET /api/v1/base/userinfo`
  
**接口描述**: 获取当前登录用户的基本信息
  
**请求头**:

```
Authorization: Bearer {access_token}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "username": "admin",
    "nickname": "管理员",
    "email": "admin@example.com",
    "is_superuser": true
  }
}
```

### 3. 获取用户菜单
  
**接口地址**: `GET /api/v1/base/usermenu`
  
**接口描述**: 获取当前用户可访问的菜单列表
  
**请求头**:

```
Authorization: Bearer {access_token}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "id": 1,
      "title": "系统管理",
      "path": "/system",
      "icon": "system",
      "children": [
        {
          "id": 2,
          "title": "用户管理",
          "path": "/system/users",
          "icon": "user"
        }
      ]
    }
  ]
}
```
 
### 4. 获取用户API权限
  
**接口地址**: `GET /api/v1/base/userapi`
 
**接口描述**: 获取当前用户可访问的API列表
  
**请求头**:

```
Authorization: Bearer {access_token}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    "get/api/v1/users/list",
    "post/api/v1/users/create"
  ]
}
```
 
### 5. 修改密码
  
**接口地址**: `POST /api/v1/base/update_password`
  
**接口描述**: 修改当前用户密码
  
**请求头**:

```
Authorization: Bearer {access_token}
```
  
**请求参数**:

```json
{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "修改成功",
  "data": null
}
```
 
## 设备信息管理接口

### 1. 设备列表

**接口地址**: `GET /api/v1/devices/list`

**接口描述**: 获取设备列表，支持分页和搜索

**请求参数**:
- `page` (int, 可选): 页码，默认1
- `page_size` (int, 可选): 每页数量，默认10
- `device_code` (str, 可选): 设备编号搜索
- `device_name` (str, 可选): 设备名称搜索
- `device_type` (str, 可选): 设备类型搜索
- `manufacturer` (str, 可选): 制造商搜索
- `status` (str, 可选): 设备状态搜索
- `install_location` (str, 可选): 安装位置搜索

**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "id": 1,
      "device_code": "DEV001",
      "device_name": "温度传感器01",
      "device_model": "TMP36",
      "device_type": "传感器",
      "manufacturer": "德州仪器",
      "purchase_date": "2024-01-15",
      "warranty_period": 24,
      "install_date": "2024-01-20",
      "install_location": "车间A-01",
      "responsible_person": "张三",
      "contact_info": "13800138000",
      "status": "正常",
      "remarks": "定期维护",
      "created_at": "2024-01-15T10:00:00",
      "updated_at": "2024-01-20T15:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

### 2. 查看设备

**接口地址**: `GET /api/v1/devices/get`

**接口描述**: 根据ID获取设备详细信息

**请求参数**:
- `device_id` (int, 必需): 设备ID

**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "device_code": "DEV001",
    "device_name": "温度传感器01",
    "device_model": "TMP36",
    "device_type": "传感器",
    "manufacturer": "德州仪器",
    "purchase_date": "2024-01-15",
    "warranty_period": 24,
    "install_date": "2024-01-20",
    "install_location": "车间A-01",
    "responsible_person": "张三",
    "contact_info": "13800138000",
    "status": "正常",
    "remarks": "定期维护",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-20T15:30:00"
  }
}
```

### 3. 创建设备

**接口地址**: `POST /api/v1/devices/create`

**接口描述**: 创建新设备信息

**请求参数**:

```json
{
  "device_code": "DEV002",
  "device_name": "压力传感器01",
  "device_model": "MPX5700",
  "device_type": "传感器",
  "manufacturer": "飞思卡尔",
  "purchase_date": "2024-02-01",
  "warranty_period": 36,
  "install_date": "2024-02-05",
  "install_location": "车间B-02",
  "responsible_person": "李四",
  "contact_info": "13900139000",
  "status": "正常",
  "remarks": "新安装设备"
}
```

**响应示例**:

```json
{
  "code": 200,
  "msg": "Created Successfully",
  "data": null
}
```

### 4. 更新设备

**接口地址**: `POST /api/v1/devices/update`

**接口描述**: 更新设备信息

**请求参数**:

```json
{
  "id": 1,
  "device_code": "DEV001",
  "device_name": "温度传感器01-更新",
  "device_model": "TMP36",
  "device_type": "传感器",
  "manufacturer": "德州仪器",
  "purchase_date": "2024-01-15",
  "warranty_period": 24,
  "install_date": "2024-01-20",
  "install_location": "车间A-01",
  "responsible_person": "张三",
  "contact_info": "13800138000",
  "status": "维护中",
  "remarks": "设备维护更新"
}
```

**响应示例**:

```json
{
  "code": 200,
  "msg": "Updated Successfully",
  "data": null
}
```

### 5. 删除设备

**接口地址**: `DELETE /api/v1/devices/delete`

**接口描述**: 删除设备信息

**请求参数**:
- `device_id` (int, 必需): 设备ID

**响应示例**:

```json
{
  "code": 200,
  "msg": "Deleted Successfully",
  "data": null
}
```

### 6. 设备状态统计

**接口地址**: `GET /api/v1/devices/statistics`

**接口描述**: 获取设备状态统计信息

**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "total_devices": 100,
    "normal_devices": 85,
    "maintenance_devices": 10,
    "fault_devices": 3,
    "offline_devices": 2,
    "device_types": {
      "传感器": 60,
      "控制器": 25,
      "执行器": 15
    },
    "manufacturers": {
      "德州仪器": 30,
      "飞思卡尔": 25,
      "西门子": 20,
      "其他": 25
    }
  }
}
```

### 7. 批量导入设备

**接口地址**: `POST /api/v1/devices/batch_import`

**接口描述**: 批量导入设备信息

**请求参数**:

```json
{
  "devices": [
    {
      "device_code": "DEV003",
      "device_name": "流量传感器01",
      "device_model": "FLS100",
      "device_type": "传感器",
      "manufacturer": "艾默生",
      "install_location": "车间C-01"
    },
    {
      "device_code": "DEV004",
      "device_name": "流量传感器02",
      "device_model": "FLS100",
      "device_type": "传感器",
      "manufacturer": "艾默生",
      "install_location": "车间C-02"
    }
  ]
}
```

**响应示例**:

```json
{
  "code": 200,
  "msg": "Batch Import Successfully",
  "data": {
    "success_count": 2,
    "failed_count": 0,
    "failed_items": []
  }
}
```

### 8. 导出设备信息

**接口地址**: `GET /api/v1/devices/export`

**接口描述**: 导出设备信息为Excel文件

**请求参数**:
- `device_type` (str, 可选): 设备类型过滤
- `status` (str, 可选): 设备状态过滤
- `format` (str, 可选): 导出格式，默认excel

**响应**: 返回Excel文件流

## 用户管理接口
 
### 1. 用户列表
  
**接口地址**: `GET /api/v1/users/list`
  
**接口描述**: 获取用户列表，支持分页和搜索
  
**请求参数**:
- `page` (int, 可选): 页码，默认1
- `page_size` (int, 可选): 每页数量，默认10
- `username` (str, 可选): 用户名搜索
- `nickname` (str, 可选): 昵称搜索
- `email` (str, 可选): 邮箱搜索

**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "id": 1,
      "username": "admin",
      "nickname": "管理员",
      "email": "admin@example.com",
      "is_active": true,
      "is_superuser": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```
 
### 2. 查看用户
  
**接口地址**: `GET /api/v1/users/get`
  
**接口描述**: 根据ID获取用户详细信息
  
**请求参数**:
- `user_id` (int, 必需): 用户ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "username": "admin",
    "nickname": "管理员",
    "email": "admin@example.com",
    "is_active": true,
    "is_superuser": true,
    "roles": [1, 2],
    "dept_id": 1
  }
}
```
 
### 3. 创建用户
  
**接口地址**: `POST /api/v1/users/create`
  
**接口描述**: 创建新用户
  
**请求参数**:

```json
{
  "username": "newuser",
  "nickname": "新用户",
  "email": "newuser@example.com",
  "password": "password123",
  "is_active": true,
  "is_superuser": false,
  "roles": [1],
  "dept_id": 1
}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Created Successfully",
  "data": null
}
```

### 4. 更新用户
  
**接口地址**: `POST /api/v1/users/update`
  
**接口描述**: 更新用户信息
  
**请求参数**:

```json
{
  "id": 1,
  "username": "admin",
  "nickname": "超级管理员",
  "email": "admin@example.com",
  "is_active": true,
  "is_superuser": true,
  "roles": [1, 2],
  "dept_id": 1
}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Updated Successfully",
  "data": null
}
```
 
### 5. 删除用户
  
**接口地址**: `DELETE /api/v1/users/delete`
  
**接口描述**: 删除用户
  
**请求参数**:
- `user_id` (int, 必需): 用户ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Deleted Successfully",
  "data": null
}
```
 
### 6. 重置密码
  
**接口地址**: `POST /api/v1/users/reset_password`
  
**接口描述**: 重置用户密码
  
**请求参数**:

```json
{
  "user_id": 1,
  "new_password": "newpassword123"
}
```

**响应示例**:

```json
{
  "code": 200,
  "msg": "Password Reset Successfully",
  "data": null
}
```

## 角色管理接口

### 1. 角色列表
  
**接口地址**: `GET /api/v1/roles/list`
  
**接口描述**: 获取角色列表，支持分页和搜索
  
**请求参数**:
- `page` (int, 可选): 页码，默认1
- `page_size` (int, 可选): 每页数量，默认10
- `name` (str, 可选): 角色名称搜索
- `desc` (str, 可选): 角色描述搜索
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "id": 1,
      "name": "超级管理员",
      "desc": "系统超级管理员角色",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```
  
### 2. 查看角色
  
**接口地址**: `GET /api/v1/roles/get`
  
**接口描述**: 根据ID获取角色详细信息
  
**请求参数**:
- `role_id` (int, 必需): 角色ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "name": "超级管理员",
    "desc": "系统超级管理员角色",
    "is_active": true,
    "menus": [1, 2, 3],
    "apis": [1, 2, 3]
  }
}
```

### 3. 创建角色
  
**接口地址**: `POST /api/v1/roles/create`
  
**接口描述**: 创建新角色
  
**请求参数**:

```json
{
  "name": "普通用户",
  "desc": "普通用户角色",
  "is_active": true
}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Created Successfully",
  "data": null
}
```

### 4. 更新角色
  
**接口地址**: `POST /api/v1/roles/update`
  
**接口描述**: 更新角色信息
  
**请求参数**:

```json
{
  "id": 1,
  "name": "超级管理员",
  "desc": "系统超级管理员角色",
  "is_active": true
}
```

**响应示例**:

```json
{
  "code": 200,
  "msg": "Updated Successfully",
  "data": null
}
```
 
### 5. 删除角色
  
**接口地址**: `DELETE /api/v1/roles/delete`
  
**接口描述**: 删除角色
  
**请求参数**:
- `role_id` (int, 必需): 角色ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Deleted Successfully",
  "data": null
}
```
  
### 6. 查看角色权限
 
**接口地址**: `GET /api/v1/roles/access`
  
**接口描述**: 获取角色的菜单和API权限
  
**请求参数**:
- `role_id` (int, 必需): 角色ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "menus": [1, 2, 3],
    "apis": [1, 2, 3]
  }
}
```
 
### 7. 更新角色权限
  
**接口地址**: `POST /api/v1/roles/access`
  
**接口描述**: 更新角色的菜单和API权限
  
**请求参数**:

```json
{
  "role_id": 1,
  "menus": [1, 2, 3],
  "apis": [1, 2, 3]
}
```
 
**响应示例**:

```json
{
  "code": 200,
  "msg": "Updated Successfully",
  "data": null
}
```
  
## 菜单管理接口
 
### 1. 菜单列表
  
**接口地址**: `GET /api/v1/menus/list`
  
**接口描述**: 获取菜单树形结构列表
  
**请求参数**:
- `page` (int, 可选): 页码，默认1
- `page_size` (int, 可选): 每页数量，默认10
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "id": 1,
      "title": "系统管理",
      "path": "/system",
      "icon": "system",
      "parent_id": 0,
      "order": 1,
      "children": [
        {
          "id": 2,
          "title": "用户管理",
          "path": "/system/users",
          "icon": "user",
          "parent_id": 1,
          "order": 1,
          "children": []
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```
 
### 2. 查看菜单
  
**接口地址**: `GET /api/v1/menus/get`
  
**接口描述**: 根据ID获取菜单详细信息
  
**请求参数**:
- `menu_id` (int, 必需): 菜单ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "title": "系统管理",
    "path": "/system",
    "icon": "system",
    "parent_id": 0,
    "order": 1,
    "is_active": true
  }
}
```
 
### 3. 创建菜单
  
**接口地址**: `POST /api/v1/menus/create`
  
**接口描述**: 创建新菜单
  
**请求参数**:

```json
{
  "title": "设备管理",
  "path": "/device",
  "icon": "device",
  "parent_id": 0,
  "order": 2,
  "is_active": true
}
```
 
**响应示例**:

```json
{
  "code": 200,
  "msg": "Created Success",
  "data": null
}
```
  
### 4. 更新菜单
  
**接口地址**: `POST /api/v1/menus/update`
  
**接口描述**: 更新菜单信息
  
**请求参数**:

```json
{
  "id": 1,
  "title": "系统管理",
  "path": "/system",
  "icon": "system",
  "parent_id": 0,
  "order": 1,
  "is_active": true
}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Updated Success",
  "data": null
}
```
  
### 5. 删除菜单
  
**接口地址**: `DELETE /api/v1/menus/delete`
  
**接口描述**: 删除菜单（不能删除有子菜单的菜单）
  
**请求参数**:
- `id` (int, 必需): 菜单ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Deleted Success",
  "data": null
}
```
 
## 部门管理接口

### 1. 部门列表
  
**接口地址**: `GET /api/v1/depts/list`
  
**接口描述**: 获取部门树形结构列表
  
**请求参数**:
- `name` (str, 可选): 部门名称搜索
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "id": 1,
      "name": "总公司",
      "parent_id": 0,
      "order": 1,
      "children": [
        {
          "id": 2,
          "name": "技术部",
          "parent_id": 1,
          "order": 1,
          "children": []
        }
      ]
    }
  ]
}
```
### 2. 查看部门
  
**接口地址**: `GET /api/v1/depts/get`
  
**接口描述**: 根据ID获取部门详细信息
  
**请求参数**:
- `id` (int, 必需): 部门ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "name": "总公司",
    "parent_id": 0,
    "order": 1,
    "is_active": true
  }
}
```
 
### 3. 创建部门
  
**接口地址**: `POST /api/v1/depts/create`
  
**接口描述**: 创建新部门
  
**请求参数**:

```json
{
  "name": "市场部",
  "parent_id": 1,
  "order": 2,
  "is_active": true
}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Created Successfully",
  "data": null
}
```
  
### 4. 更新部门
  
**接口地址**: `POST /api/v1/depts/update`
  
**接口描述**: 更新部门信息
  
**请求参数**:

```json
{
  "id": 1,
  "name": "总公司",
  "parent_id": 0,
  "order": 1,
  "is_active": true
}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Update Successfully",
  "data": null
}
```

### 5. 删除部门
  
**接口地址**: `DELETE /api/v1/depts/delete`
  
**接口描述**: 删除部门
  
**请求参数**:
- `dept_id` (int, 必需): 部门ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Deleted Success",
  "data": null
}
```
  
## API管理接口
 
### 1. API列表
  
**接口地址**: `GET /api/v1/apis/list`
  
**接口描述**: 获取API列表，支持分页和搜索
  
**请求参数**:
- `page` (int, 可选): 页码，默认1
- `page_size` (int, 可选): 每页数量，默认10
- `path` (str, 可选): API路径搜索
- `summary` (str, 可选): API简介搜索
- `tags` (str, 可选): API模块搜索
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "id": 1,
      "path": "/api/v1/users/list",
      "method": "GET",
      "summary": "用户列表",
      "tags": "用户管理",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```
 
### 2. 查看API
  
**接口地址**: `GET /api/v1/apis/get`
  
**接口描述**: 根据ID获取API详细信息
  
**请求参数**:
- `id` (int, 必需): API ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "path": "/api/v1/users/list",
    "method": "GET",
    "summary": "用户列表",
    "tags": "用户管理",
    "description": "获取用户列表，支持分页和搜索"
  }
}
```
  
### 3. 创建API
  
**接口地址**: `POST /api/v1/apis/create`
  
**接口描述**: 创建新API
  
**请求参数**:

```json
{
  "path": "/api/v1/devices/list",
  "method": "GET",
  "summary": "设备列表",
  "tags": "设备管理",
  "description": "获取设备列表"
}
```
 
**响应示例**:

```json
{
  "code": 200,
  "msg": "Created Successfully",
  "data": null
}
```
  
### 4. 更新API
  
**接口地址**: `POST /api/v1/apis/update`
  
**接口描述**: 更新API信息
  
**请求参数**:

```json
{
  "id": 1,
  "path": "/api/v1/users/list",
  "method": "GET",
  "summary": "用户列表",
  "tags": "用户管理",
  "description": "获取用户列表，支持分页和搜索"
}
```
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Update Successfully",
  "data": null
}
```
  
### 5. 删除API
  
**接口地址**: `DELETE /api/v1/apis/delete`
  
**接口描述**: 删除API
  
**请求参数**:
- `api_id` (int, 必需): API ID
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "Deleted Success",
  "data": null
}
```
  
### 6. 刷新API列表
  
**接口地址**: `POST /api/v1/apis/refresh`
  
**接口描述**: 从代码中自动扫描并刷新API列表
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": null
}
```
  
## 审计日志接口
### 1. 操作日志列表
  
**接口地址**: `GET /api/v1/auditlog/list`
  
**接口描述**: 获取系统操作日志列表，支持分页和多条件搜索
  
**请求参数**:
- `page` (int, 可选): 页码，默认1
- `page_size` (int, 可选): 每页数量，默认10
- `username` (str, 可选): 操作人名称搜索
- `module` (str, 可选): 功能模块搜索
- `method` (str, 可选): 请求方法搜索
- `summary` (str, 可选): 接口描述搜索
- `status` (int, 可选): 状态码搜索
- `start_time` (datetime, 可选): 开始时间
- `end_time` (datetime, 可选): 结束时间
  
**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "id": 1,
      "username": "admin",
      "module": "用户管理",
      "method": "POST",
      "summary": "创建用户",
      "path": "/api/v1/users/create",
      "status": 200,
      "ip": "127.0.0.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```
 
## 设备实时数据接口

### 1. 获取设备实时数据

**接口地址**: `GET /api/v1/devices/realtime`

**接口描述**: 获取设备实时数据，支持单设备或多设备查询

**请求参数**:
- `device_codes` (str, 可选): 设备编号列表，逗号分隔，如"DEV001,DEV002"
- `device_id` (int, 可选): 单个设备ID
- `limit` (int, 可选): 返回记录数限制，默认100

**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "device_code": "DEV001",
      "device_name": "温度传感器01",
      "voltage": 220.5,
      "current": 10.2,
      "power": 2249.1,
      "temperature": 25.6,
      "pressure": 101325.0,
      "vibration": 0.02,
      "status": "online",
      "error_code": null,
      "error_message": null,
      "data_timestamp": "2024-12-20T10:30:00Z",
      "updated_at": "2024-12-20T10:30:05Z"
    }
  ]
}
```

### 2. 获取设备历史数据

**接口地址**: `GET /api/v1/devices/history`

**接口描述**: 获取设备历史数据，支持时间范围查询

**请求参数**:
- `device_code` (str, 必需): 设备编号
- `start_time` (datetime, 必需): 开始时间，ISO格式
- `end_time` (datetime, 必需): 结束时间，ISO格式
- `page` (int, 可选): 页码，默认1
- `page_size` (int, 可选): 每页数量，默认100
- `fields` (str, 可选): 指定返回字段，逗号分隔

**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "device_code": "DEV001",
      "voltage": 220.3,
      "current": 10.1,
      "power": 2225.03,
      "temperature": 25.4,
      "status": "online",
      "data_timestamp": "2024-12-20T10:25:00Z"
    }
  ],
  "total": 1440,
  "page": 1,
  "page_size": 100
}
```

### 3. 设备数据统计

**接口地址**: `GET /api/v1/devices/statistics/data`

**接口描述**: 获取设备数据统计信息

**请求参数**:
- `device_code` (str, 必需): 设备编号
- `metric` (str, 必需): 统计指标，如"voltage","current","power","temperature"
- `start_time` (datetime, 必需): 开始时间
- `end_time` (datetime, 必需): 结束时间
- `interval` (str, 可选): 统计间隔，如"1h","1d"，默认"1h"

**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "device_code": "DEV001",
    "metric": "temperature",
    "interval": "1h",
    "statistics": [
      {
        "timestamp": "2024-12-20T10:00:00Z",
        "avg": 25.6,
        "min": 24.8,
        "max": 26.4,
        "count": 120
      }
    ]
  }
}
```

## TDengine时序数据接口

### 1. 查询焊机实时数据

**接口地址**: `GET /api/v1/tdengine/welding/realtime`

**接口描述**: 从TDengine查询焊机实时数据

**请求参数**:
- `device_codes` (str, 可选): 设备编号列表，逗号分隔
- `start_time` (datetime, 可选): 开始时间
- `end_time` (datetime, 可选): 结束时间
- `limit` (int, 可选): 返回记录数限制，默认1000

**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "ts": "2024-12-20T10:30:00Z",
      "device_code": "14412T0006",
      "team_name": "班组一",
      "device_status": "焊接",
      "lock_status": false,
      "preset_current": 10.5,
      "preset_voltage": 220.0,
      "weld_current": 11.0,
      "weld_voltage": 225.0,
      "material": "Q235",
      "wire_diameter": 1.2,
      "gas_type": "CO2",
      "weld_method": "MIG",
      "weld_control": "脉冲",
      "staff_id": "W123456",
      "workpiece_id": "WP123456",
      "ip_quality": 100
    }
  ]
}
```

### 2. 查询设备状态统计

**接口地址**: `GET /api/v1/tdengine/device/status-summary`

**接口描述**: 查询设备状态实时统计数据

**请求参数**:
- `start_time` (datetime, 可选): 开始时间
- `end_time` (datetime, 可选): 结束时间
- `interval` (str, 可选): 统计间隔，默认"1m"

**响应示例**:

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {
      "ts": "2024-12-20T10:30:00Z",
      "status_standby": 655,
      "status_welding": 67,
      "status_alarm": 2,
      "status_shutdown": 6457,
      "ip_quality": 100
    }
  ]
}
```

## WebSocket实时数据推送

### 1. 连接WebSocket

**连接地址**: `ws://localhost:8000/ws/realtime`

**连接参数**:
- `token` (str, 必需): JWT认证令牌
- `device_codes` (str, 可选): 订阅的设备编号列表，逗号分隔

**连接示例**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/realtime?token=your_jwt_token&device_codes=DEV001,DEV002');
```

### 2. 消息格式

**设备数据推送消息**:
```json
{
  "type": "device_data",
  "device_code": "DEV001",
  "data": {
    "voltage": 220.5,
    "current": 10.2,
    "power": 2249.1,
    "temperature": 25.6,
    "status": "online",
    "timestamp": "2024-12-20T10:30:00Z"
  }
}
```

**设备状态变更消息**:
```json
{
  "type": "device_status",
  "device_code": "DEV001",
  "old_status": "online",
  "new_status": "error",
  "error_code": "E001",
  "error_message": "温度超限",
  "timestamp": "2024-12-20T10:30:00Z"
}
```

**系统告警消息**:
```json
{
  "type": "system_alert",
  "level": "warning",
  "message": "设备DEV001温度异常",
  "device_code": "DEV001",
  "timestamp": "2024-12-20T10:30:00Z"
}
```

### 3. 客户端订阅管理

**订阅设备**:
```json
{
  "action": "subscribe",
  "device_codes": ["DEV001", "DEV002"]
}
```

**取消订阅**:
```json
{
  "action": "unsubscribe",
  "device_codes": ["DEV001"]
}
```

**心跳检测**:
```json
{
  "action": "ping"
}
```

## 错误码说明
  
| 错误码 | 说明        |
| --- | --------- |
| 200 | 请求成功      |
| 400 | 请求参数错误    |
| 401 | 未授权，需要登录  |
| 403 | 禁止访问，权限不足 |
| 404 | 资源不存在     |
| 422 | 请求参数验证失败  |
| 500 | 服务器内部错误   |
| 1001 | 设备不存在     |
| 1002 | 设备离线      |
| 1003 | 数据查询超时    |
| 1004 | TDengine连接失败 |
| 1005 | WebSocket连接失败 |
 
## 注意事项
 
1. 所有需要认证的接口都需要在请求头中携带JWT Token
2. 分页参数中，page从1开始计数
3. 时间格式统一使用ISO 8601格式：`YYYY-MM-DDTHH:mm:ss
4. 所有删除操作都是物理删除，请谨慎操作
5. 超级管理员拥有所有权限，普通用户权限由角色控制
6. API权限控制基于角色-API关联关系
7. 菜单权限控制基于角色-菜单关联关系
 
## 开发环境
 
- **框架**: FastAPI
- **数据库**: SQLite/PostgreSQL/MySQL（可配置）
- **ORM**: Tortoise ORM
- **认证**: JWT
- **文档**: 自动生成Swagger文档，访问 `/docs` 查看