# 权限系统API文档

## 概述

本文档详细介绍了用户权限系统的所有API接口，包括认证、用户管理、角色管理、权限验证等功能。

## 目录

- [认证API](#认证api)
- [用户管理API](#用户管理api)
- [角色管理API](#角色管理api)
- [菜单权限API](#菜单权限api)
- [权限验证API](#权限验证api)
- [权限配置API](#权限配置api)
- [审计日志API](#审计日志api)
- [批量操作API](#批量操作api)

## 基础信息

### 基础URL
```
生产环境: https://api.yourdomain.com
开发环境: http://localhost:8000
```

### 认证方式
所有API（除登录接口外）都需要在请求头中包含JWT令牌：
```http
Authorization: Bearer <your_jwt_token>
```

### 响应格式
所有API响应都遵循统一格式：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": "2025-10-10T10:00:00Z"
}
```

### 错误码说明
| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或令牌无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

---

## 认证API

### 用户登录
**POST** `/api/v2/auth/login`

用户登录获取访问令牌。

#### 请求参数
```json
{
  "username": "admin",
  "password": "password123"
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user_info": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "is_superuser": true
    }
  }
}
```

### 刷新令牌
**POST** `/api/v2/auth/refresh`

使用刷新令牌获取新的访问令牌。

#### 请求参数
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "令牌刷新成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### 用户登出
**POST** `/api/v2/auth/logout`

用户登出，将令牌加入黑名单。

#### 响应示例
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

### 获取当前用户信息
**GET** `/api/v2/auth/me`

获取当前登录用户的详细信息。

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "nickname": "管理员",
    "is_superuser": true,
    "is_active": true,
    "last_login": "2025-10-10T10:00:00Z",
    "roles": [
      {
        "id": 1,
        "role_name": "超级管理员",
        "role_key": "admin"
      }
    ]
  }
}
```

---

## 用户管理API

### 获取用户列表
**GET** `/api/v2/users`

获取用户列表，支持分页和搜索。

#### 查询参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| username | string | 否 | 用户名搜索 |
| email | string | 否 | 邮箱搜索 |
| is_active | boolean | 否 | 用户状态过滤 |

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "nickname": "管理员",
        "is_superuser": true,
        "is_active": true,
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-10-10T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

### 创建用户
**POST** `/api/v2/users`

创建新用户。

#### 请求参数
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "nickname": "新用户",
  "is_active": true,
  "role_ids": [2, 3]
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "用户创建成功",
  "data": {
    "id": 2,
    "username": "newuser",
    "email": "newuser@example.com",
    "nickname": "新用户",
    "is_active": true,
    "created_at": "2025-10-10T10:00:00Z"
  }
}
```

### 获取用户详情
**GET** `/api/v2/users/{user_id}`

获取指定用户的详细信息。

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "nickname": "管理员",
    "is_superuser": true,
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-10-10T10:00:00Z",
    "roles": [
      {
        "id": 1,
        "role_name": "超级管理员",
        "role_key": "admin"
      }
    ],
    "permissions": [
      "system:user:view",
      "system:user:create",
      "system:user:update",
      "system:user:delete"
    ]
  }
}
```

### 更新用户
**PUT** `/api/v2/users/{user_id}`

更新用户信息。

#### 请求参数
```json
{
  "email": "updated@example.com",
  "nickname": "更新的昵称",
  "is_active": true,
  "role_ids": [2, 3]
}
```

### 删除用户
**DELETE** `/api/v2/users/{user_id}`

删除指定用户。

#### 响应示例
```json
{
  "code": 200,
  "message": "用户删除成功",
  "data": null
}
```

### 重置用户密码
**POST** `/api/v2/users/{user_id}/reset-password`

重置用户密码。

#### 请求参数
```json
{
  "new_password": "newpassword123"
}
```

---

## 角色管理API

### 获取角色列表
**GET** `/api/v2/roles`

获取角色列表，支持分页和搜索。

#### 查询参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| role_name | string | 否 | 角色名搜索 |
| status | string | 否 | 角色状态过滤 |

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "role_name": "超级管理员",
        "role_key": "admin",
        "description": "系统超级管理员",
        "status": "0",
        "created_at": "2025-01-01T00:00:00Z",
        "user_count": 1
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

### 创建角色
**POST** `/api/v2/roles`

创建新角色。

#### 请求参数
```json
{
  "role_name": "部门管理员",
  "role_key": "dept_admin",
  "description": "部门管理员角色",
  "status": "0",
  "menu_ids": [1, 2, 3],
  "api_endpoint_ids": [1, 2, 3]
}
```

### 获取角色详情
**GET** `/api/v2/roles/{role_id}`

获取指定角色的详细信息。

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "role_name": "超级管理员",
    "role_key": "admin",
    "description": "系统超级管理员",
    "status": "0",
    "created_at": "2025-01-01T00:00:00Z",
    "menus": [
      {
        "id": 1,
        "name": "系统管理",
        "path": "/system",
        "perms": "system:view"
      }
    ],
    "api_endpoints": [
      {
        "id": 1,
        "api_code": "system:user:view",
        "path": "/api/v2/users",
        "method": "GET"
      }
    ]
  }
}
```

### 更新角色
**PUT** `/api/v2/roles/{role_id}`

更新角色信息。

### 删除角色
**DELETE** `/api/v2/roles/{role_id}`

删除指定角色。

---

## 菜单权限API

### 获取用户菜单
**GET** `/api/v2/users/menus`

获取当前用户有权限的菜单列表。

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "系统管理",
      "path": "/system",
      "component": "Layout",
      "icon": "system",
      "sort": 1,
      "children": [
        {
          "id": 2,
          "name": "用户管理",
          "path": "/system/users",
          "component": "system/users/index",
          "icon": "user",
          "sort": 1,
          "perms": "system:user:view"
        }
      ]
    }
  ]
}
```

### 获取菜单树
**GET** `/api/v2/menus/tree`

获取完整的菜单树结构（管理员使用）。

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "系统管理",
      "path": "/system",
      "component": "Layout",
      "menu_type": "M",
      "visible": true,
      "status": "0",
      "sort": 1,
      "children": [
        {
          "id": 2,
          "name": "用户管理",
          "path": "/system/users",
          "component": "system/users/index",
          "menu_type": "C",
          "visible": true,
          "status": "0",
          "sort": 1,
          "perms": "system:user:view"
        }
      ]
    }
  ]
}
```

---

## 权限验证API

### 检查单个权限
**POST** `/api/v2/users/check-permission`

检查当前用户是否具有指定权限。

#### 请求参数
```json
{
  "permission": "system:user:view"
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "检查完成",
  "data": {
    "has_permission": true,
    "permission": "system:user:view"
  }
}
```

### 批量检查权限
**POST** `/api/v2/users/batch-check-permissions`

批量检查当前用户的多个权限。

#### 请求参数
```json
{
  "permissions": [
    "system:user:view",
    "system:user:create",
    "system:user:update"
  ]
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "检查完成",
  "data": {
    "system:user:view": true,
    "system:user:create": true,
    "system:user:update": false
  }
}
```

### 获取用户权限列表
**GET** `/api/v2/users/permissions`

获取当前用户的所有权限列表。

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    "system:user:view",
    "system:user:create",
    "system:user:update",
    "system:role:view",
    "system:menu:view"
  ]
}
```

### 获取用户角色列表
**GET** `/api/v2/users/roles`

获取当前用户的角色列表。

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "role_name": "超级管理员",
      "role_key": "admin",
      "description": "系统超级管理员"
    }
  ]
}
```

---

## 权限配置API

### 获取API端点列表
**GET** `/api/v2/api-endpoints`

获取系统中所有API端点列表。

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "api_code": "system:user:view",
      "path": "/api/v2/users",
      "method": "GET",
      "description": "获取用户列表",
      "status": "active",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### 同步API端点
**POST** `/api/v2/api-endpoints/sync`

同步系统中的API端点到数据库。

#### 响应示例
```json
{
  "code": 200,
  "message": "同步完成",
  "data": {
    "added": 5,
    "updated": 2,
    "total": 25
  }
}
```

---

## 审计日志API

### 获取审计日志
**GET** `/api/v2/audit/logs`

获取系统审计日志。

#### 查询参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| user_id | int | 否 | 用户ID过滤 |
| action | string | 否 | 操作类型过滤 |
| start_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |

#### 响应示例
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 1,
        "username": "admin",
        "action": "LOGIN",
        "resource": "AUTH",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "created_at": "2025-10-10T10:00:00Z",
        "details": {
          "login_method": "password"
        }
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

---

## 批量操作API

### 批量删除用户
**DELETE** `/api/v2/users/batch`

批量删除用户。

#### 请求参数
```json
{
  "user_ids": [2, 3, 4]
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "批量删除成功",
  "data": {
    "deleted_count": 3,
    "failed_count": 0,
    "failed_items": []
  }
}
```

### 批量更新用户状态
**PUT** `/api/v2/users/batch/status`

批量更新用户状态。

#### 请求参数
```json
{
  "user_ids": [2, 3, 4],
  "is_active": false
}
```

---

## 错误处理

### 常见错误响应

#### 401 未认证
```json
{
  "code": 401,
  "message": "未认证或令牌无效",
  "data": null,
  "error_type": "AUTHENTICATION_ERROR"
}
```

#### 403 权限不足
```json
{
  "code": 403,
  "message": "权限不足，无法访问该资源",
  "data": null,
  "error_type": "PERMISSION_DENIED"
}
```

#### 422 数据验证失败
```json
{
  "code": 422,
  "message": "请求参数验证失败",
  "data": {
    "errors": [
      {
        "field": "username",
        "message": "用户名不能为空"
      }
    ]
  },
  "error_type": "VALIDATION_ERROR"
}
```

## 使用示例

### JavaScript/TypeScript 示例

```javascript
// 登录
const login = async (username, password) => {
  const response = await fetch('/api/v2/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });
  
  const result = await response.json();
  if (result.code === 200) {
    localStorage.setItem('access_token', result.data.access_token);
    return result.data;
  }
  throw new Error(result.message);
};

// 获取用户列表
const getUsers = async (page = 1, size = 10) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`/api/v2/users?page=${page}&size=${size}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const result = await response.json();
  if (result.code === 200) {
    return result.data;
  }
  throw new Error(result.message);
};

// 检查权限
const checkPermission = async (permission) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/api/v2/users/check-permission', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ permission })
  });
  
  const result = await response.json();
  return result.code === 200 && result.data.has_permission;
};
```

### Python 示例

```python
import requests

class PermissionAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        """用户登录"""
        response = requests.post(
            f"{self.base_url}/api/v2/auth/login",
            json={"username": username, "password": password}
        )
        result = response.json()
        if result["code"] == 200:
            self.token = result["data"]["access_token"]
            return result["data"]
        raise Exception(result["message"])
    
    def get_headers(self):
        """获取请求头"""
        if not self.token:
            raise Exception("请先登录")
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_users(self, page=1, size=10):
        """获取用户列表"""
        response = requests.get(
            f"{self.base_url}/api/v2/users",
            params={"page": page, "size": size},
            headers=self.get_headers()
        )
        result = response.json()
        if result["code"] == 200:
            return result["data"]
        raise Exception(result["message"])
    
    def check_permission(self, permission):
        """检查权限"""
        response = requests.post(
            f"{self.base_url}/api/v2/users/check-permission",
            json={"permission": permission},
            headers=self.get_headers()
        )
        result = response.json()
        return result["code"] == 200 and result["data"]["has_permission"]

# 使用示例
api = PermissionAPI("http://localhost:8000")
api.login("admin", "password123")
users = api.get_users(page=1, size=20)
has_permission = api.check_permission("system:user:view")
```

## 版本信息

- **当前版本**: v2.0
- **最后更新**: 2025-10-10
- **兼容性**: 支持所有现代浏览器和HTTP客户端

## 联系支持

如有问题或建议，请联系：
- 邮箱: support@example.com
- 文档: https://docs.example.com
- GitHub: https://github.com/example/permission-system