#!/usr/bin/env python3
"""
API文档生成脚本
自动生成和更新API文档
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.api_changelog import changelog_manager


async def generate_all_docs():
    """生成所有格式的API文档"""
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    print("🚀 开始生成API文档...")
    
    # 生成变更日志
    print("📝 生成API变更日志...")
    
    # Markdown格式
    markdown_content = changelog_manager.generate_markdown_changelog()
    with open(docs_dir / "api_changelog.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print("✅ Markdown格式变更日志已生成: docs/api_changelog.md")
    
    # HTML格式
    html_content = changelog_manager.generate_html_changelog()
    with open(docs_dir / "api_changelog.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ HTML格式变更日志已生成: docs/api_changelog.html")
    
    # JSON格式
    json_content = changelog_manager.load_changelog()
    with open(docs_dir / "api_changelog.json", "w", encoding="utf-8") as f:
        json.dump(json_content, f, ensure_ascii=False, indent=2)
    print("✅ JSON格式变更日志已生成: docs/api_changelog.json")
    
    # 生成API使用指南
    print("📖 生成API使用指南...")
    generate_api_guide(docs_dir)
    
    # 生成版本迁移指南
    print("🔄 生成版本迁移指南...")
    generate_migration_guide(docs_dir)
    
    print("🎉 所有API文档生成完成！")


def generate_api_guide(docs_dir: Path):
    """生成API使用指南"""
    guide_content = """# API使用指南

## 概述

DeviceMonitor API 是一个现代化的RESTful API，提供设备监控和管理功能。

## 基础信息

- **基础URL**: `http://localhost:8000/api`
- **当前版本**: v2 (推荐)
- **支持版本**: v1 (已弃用), v2
- **认证方式**: Bearer Token

## 快速开始

### 1. 获取访问令牌

```bash
curl -X POST "http://localhost:8000/api/v2/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "admin",
    "password": "123456"
  }'
```

### 2. 使用令牌访问API

```bash
curl -X GET "http://localhost:8000/api/v2/users" \\
  -H "Authorization: Bearer <your-token>" \\
  -H "API-Version: v2"
```

## API版本控制

### 版本指定方式

1. **URL路径方式** (推荐):
   ```
   GET /api/v1/users  # 使用v1版本
   GET /api/v2/users  # 使用v2版本
   ```

2. **请求头方式**:
   ```
   GET /api/users
   API-Version: v2
   ```

### 版本差异

| 特性 | v1 | v2 |
|------|----|----|
| 响应格式 | 传统格式 | 标准化格式 |
| 错误处理 | 基础 | 增强 |
| 文档支持 | 基础 | 完整 |
| 状态 | 已弃用 | 当前版本 |

## 响应格式

### v2版本标准响应格式

#### 成功响应
```json
{
  "success": true,
  "code": 200,
  "message": "OK",
  "data": {...},
  "timestamp": "2025-01-06T00:00:00"
}
```

#### 分页响应
```json
{
  "success": true,
  "code": 200,
  "message": "OK",
  "data": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5,
  "timestamp": "2025-01-06T00:00:00"
}
```

#### 错误响应
```json
{
  "success": false,
  "code": 404,
  "message": "资源未找到",
  "details": {
    "error_code": "RESOURCE_NOT_FOUND",
    "path": "/api/v2/users/999",
    "method": "GET"
  },
  "timestamp": "2025-01-06T00:00:00"
}
```

## 认证和授权

### 认证方式

1. **Bearer Token** (推荐):
   ```
   Authorization: Bearer <your-token>
   ```

2. **Token参数**:
   ```
   GET /api/v2/users?token=<your-token>
   ```

### 权限系统

API使用基于角色的访问控制(RBAC)：
- **超级管理员**: 拥有所有权限
- **管理员**: 拥有大部分管理权限
- **普通用户**: 拥有基础查看权限

## 错误处理

### 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| AUTHENTICATION_ERROR | 401 | 认证失败 |
| AUTHORIZATION_ERROR | 403 | 权限不足 |
| VALIDATION_ERROR | 422 | 参数验证失败 |
| RESOURCE_NOT_FOUND | 404 | 资源未找到 |
| INTERNAL_SERVER_ERROR | 500 | 服务器内部错误 |

### 错误处理最佳实践

1. 检查响应的 `success` 字段
2. 根据 `code` 字段处理不同类型的错误
3. 使用 `details.error_code` 进行精确的错误处理
4. 向用户显示 `message` 字段的内容

## 限流和配额

- **请求频率限制**: 每分钟100次请求
- **并发连接限制**: 每个IP最多10个并发连接
- **数据传输限制**: 单次请求最大10MB

## SDK和工具

### 官方SDK
- Python SDK (计划中)
- JavaScript SDK (计划中)

### 第三方工具
- Postman Collection: `/api/v2/docs/postman`
- Insomnia Collection: `/api/v2/docs/insomnia`

## 支持和反馈

- **文档**: [在线文档](http://localhost:8000/docs)
- **变更日志**: [API变更日志](http://localhost:8000/api/v2/docs/changelog)
- **问题反馈**: support@devicemonitor.com

## 更新日志

查看 [API变更日志](./api_changelog.md) 了解最新的API变更信息。
"""
    
    with open(docs_dir / "api_guide.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    print("✅ API使用指南已生成: docs/api_guide.md")


def generate_migration_guide(docs_dir: Path):
    """生成版本迁移指南"""
    migration_content = """# API版本迁移指南

## 从v1迁移到v2

### 概述

v2版本引入了标准化的响应格式和增强的错误处理，提供了更好的开发体验。

### 主要变更

#### 1. 响应格式变更

**v1格式**:
```json
{
  "code": 200,
  "msg": "OK",
  "data": {...}
}
```

**v2格式**:
```json
{
  "success": true,
  "code": 200,
  "message": "OK",
  "data": {...},
  "timestamp": "2025-01-06T00:00:00"
}
```

#### 2. 错误处理增强

**v1错误响应**:
```json
{
  "code": 404,
  "msg": "Object has not found",
  "data": null
}
```

**v2错误响应**:
```json
{
  "success": false,
  "code": 404,
  "message": "资源未找到",
  "details": {
    "error_code": "RESOURCE_NOT_FOUND",
    "path": "/api/v2/users/999",
    "method": "GET"
  },
  "timestamp": "2025-01-06T00:00:00"
}
```

### 迁移步骤

#### 步骤1: 更新URL路径

将所有API调用的URL从 `/api/v1/` 更改为 `/api/v2/`：

```javascript
// 旧版本
const response = await fetch('/api/v1/users');

// 新版本
const response = await fetch('/api/v2/users');
```

#### 步骤2: 更新响应处理逻辑

更新客户端代码以处理新的响应格式：

```javascript
// 旧版本
const response = await fetch('/api/v1/users');
const result = await response.json();
if (result.code === 200) {
  console.log('成功:', result.data);
} else {
  console.error('错误:', result.msg);
}

// 新版本
const response = await fetch('/api/v2/users');
const result = await response.json();
if (result.success) {
  console.log('成功:', result.data);
} else {
  console.error('错误:', result.message);
  console.error('错误详情:', result.details);
}
```

#### 步骤3: 更新错误处理

利用v2版本的增强错误处理：

```javascript
// 新版本错误处理
const response = await fetch('/api/v2/users');
const result = await response.json();

if (!result.success) {
  switch (result.details?.error_code) {
    case 'AUTHENTICATION_ERROR':
      // 处理认证错误
      redirectToLogin();
      break;
    case 'AUTHORIZATION_ERROR':
      // 处理权限错误
      showPermissionError();
      break;
    case 'VALIDATION_ERROR':
      // 处理验证错误
      showValidationErrors(result.details.validation_errors);
      break;
    default:
      // 处理其他错误
      showGenericError(result.message);
  }
}
```

#### 步骤4: 更新分页处理

v2版本提供了更详细的分页信息：

```javascript
// 新版本分页处理
const response = await fetch('/api/v2/users?page=1&page_size=20');
const result = await response.json();

if (result.success) {
  console.log('数据:', result.data);
  console.log('总数:', result.total);
  console.log('当前页:', result.page);
  console.log('每页大小:', result.page_size);
  console.log('总页数:', result.total_pages);
}
```

### 渐进式迁移策略

#### 阶段1: 并行运行
- 保持v1版本API正常运行
- 逐步将新功能迁移到v2版本
- 在客户端添加v2版本支持

#### 阶段2: 功能迁移
- 将核心功能迁移到v2版本
- 更新客户端代码以使用v2版本
- 保持v1版本作为后备

#### 阶段3: 完全迁移
- 所有功能使用v2版本
- 停止v1版本的新功能开发
- 计划v1版本的下线时间

### 兼容性工具

#### 响应格式转换器

如果需要临时兼容v1格式，可以使用转换器：

```javascript
function convertV2ToV1(v2Response) {
  return {
    code: v2Response.code,
    msg: v2Response.message,
    data: v2Response.data
  };
}
```

#### 错误处理适配器

```javascript
function handleError(response) {
  if (response.success !== undefined) {
    // v2格式
    return {
      isError: !response.success,
      code: response.code,
      message: response.message,
      details: response.details
    };
  } else {
    // v1格式
    return {
      isError: response.code !== 200,
      code: response.code,
      message: response.msg,
      details: null
    };
  }
}
```

### 测试建议

1. **并行测试**: 同时测试v1和v2版本的相同功能
2. **错误场景测试**: 重点测试错误处理的差异
3. **性能测试**: 确保v2版本的性能不低于v1版本
4. **兼容性测试**: 测试客户端在两个版本间的切换

### 常见问题

#### Q: v1版本何时会被移除？
A: v1版本计划在2025年12月31日停止支持。

#### Q: 是否可以在同一个应用中混用v1和v2？
A: 可以，但不推荐。建议尽快完成迁移。

#### Q: v2版本是否向后兼容？
A: v2版本在响应格式上不向后兼容，但功能上保持兼容。

#### Q: 如何处理迁移过程中的问题？
A: 可以通过以下方式获取帮助：
- 查看详细的错误信息和错误码
- 参考API文档和示例
- 联系技术支持

### 迁移检查清单

- [ ] 更新所有API调用的URL路径
- [ ] 更新响应处理逻辑
- [ ] 更新错误处理代码
- [ ] 更新分页处理逻辑
- [ ] 测试所有功能
- [ ] 更新文档和注释
- [ ] 培训团队成员
- [ ] 制定回滚计划
"""
    
    with open(docs_dir / "migration_guide.md", "w", encoding="utf-8") as f:
        f.write(migration_content)
    print("✅ 版本迁移指南已生成: docs/migration_guide.md")


if __name__ == "__main__":
    asyncio.run(generate_all_docs())