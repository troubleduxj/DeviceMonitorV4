# API备份和迁移实施指南

## 📋 概述

本指南详细说明如何在实施API v2的过程中，安全地备份现有API实现，并提供平滑的迁移路径。

## 🎯 核心原则

1. **零停机迁移**: 确保服务持续可用
2. **向后兼容**: 保持现有客户端正常工作
3. **渐进式迁移**: 分阶段实施，降低风险
4. **完整备份**: 保留所有原始实现
5. **可回滚**: 任何时候都能快速回滚

## 📁 备份策略

### 1. 完整代码备份

```bash
# 创建备份目录
mkdir -p app/api/v1_backup

# 备份现有API实现
cp -r app/routers/ app/api/v1_backup/routers/
cp -r app/services/ app/api/v1_backup/services/
cp -r app/models/ app/api/v1_backup/models/
cp -r app/schemas/ app/api/v1_backup/schemas/
cp -r app/middleware/ app/api/v1_backup/middleware/
cp -r app/core/ app/api/v1_backup/core/
cp -r app/utils/ app/api/v1_backup/utils/

# 备份配置文件
cp -r app/config/ app/api/v1_backup/config/
cp requirements.txt app/api/v1_backup/
cp main.py app/api/v1_backup/

# 备份数据库模式
pg_dump --schema-only your_database > app/api/v1_backup/schema_backup.sql
```

### 2. 创建备份清单

```bash
# 生成文件清单
find app/api/v1_backup -type f -name "*.py" > app/api/v1_backup/file_list.txt

# 记录API端点
python -c "
import sys
sys.path.append('.')
from main import app
from fastapi.routing import APIRoute

with open('app/api/v1_backup/api_endpoints.txt', 'w') as f:
    for route in app.routes:
        if isinstance(route, APIRoute):
            f.write(f'{route.methods} {route.path} -> {route.endpoint.__name__}\n')
"
```

### 3. 数据库备份

```sql
-- 创建完整数据库备份
pg_dump your_database > backups/database_backup_$(date +%Y%m%d_%H%M%S).sql

-- 创建表结构备份
pg_dump --schema-only your_database > backups/schema_backup_$(date +%Y%m%d_%H%M%S).sql

-- 备份关键表数据
pg_dump --data-only --table=user --table=role --table=api --table=menu your_database > backups/core_data_backup_$(date +%Y%m%d_%H%M%S).sql
```

## 🔄 迁移实施步骤

### 阶段1: 准备阶段 (第1周)

#### 1.1 环境准备
```bash
# 1. 创建开发分支
git checkout -b feature/api-v2-migration

# 2. 设置备份目录结构
mkdir -p {app/api/v1_backup,app/api/v2,app/api/compatibility,database/backups}

# 3. 安装依赖
pip install -r requirements.txt
```

#### 1.2 备份现有实现
```bash
# 执行完整备份脚本
./scripts/backup_v1_api.sh

# 验证备份完整性
python scripts/verify_backup.py
```

#### 1.3 创建兼容层基础
```python
# app/api/compatibility/__init__.py
from .api_compatibility_adapter import compatibility_adapter
from .version_router import APIVersionRouter

__all__ = ['compatibility_adapter', 'APIVersionRouter']
```

### 阶段2: 基础设施搭建 (第2周)

#### 2.1 实现响应格式标准化
```python
# 基于备份的v1实现，创建v2响应格式器
# 参考: app/api/v1_backup/utils/response.py

class V2ResponseFormatter:
    @staticmethod
    def format_success_response(data, message="success", meta=None):
        # 实现v2格式，同时保持v1兼容
        pass
```

#### 2.2 实现权限验证中间件
```python
# 基于备份的v1权限实现，创建v2权限验证
# 参考: app/api/v1_backup/middleware/auth.py

class V2PermissionMiddleware:
    def __init__(self):
        # 复用v1的权限逻辑，扩展v2功能
        self.v1_permission_checker = V1PermissionChecker()
    
    async def check_permission(self, user, resource, action):
        # 先使用v1逻辑验证，再应用v2增强
        pass
```

#### 2.3 设置版本路由
```python
# main.py 修改
from app.api.version_router import setup_api_versioning

app = FastAPI()

# 设置版本管理
version_router = setup_api_versioning(app)

# 保持v1路由不变
app.include_router(v1_router, prefix="", tags=["v1"])

# 添加v2路由
app.include_router(v2_router, prefix="/api/v2", tags=["v2"])
```

### 阶段3: 逐步迁移API (第3-4周)

#### 3.1 用户管理API迁移
```python
# 1. 复制v1实现作为基础
cp app/api/v1_backup/routers/user.py app/api/v2/routers/user.py

# 2. 修改为v2格式
class V2UserRouter:
    def __init__(self):
        # 复用v1的业务逻辑
        self.v1_user_service = V1UserService()
        self.v2_formatter = V2ResponseFormatter()
    
    async def get_users(self, request: Request):
        # 使用v1的查询逻辑
        users = await self.v1_user_service.get_users(request)
        
        # 转换为v2响应格式
        return self.v2_formatter.format_user_list(users)
```

#### 3.2 渐进式替换策略
```python
# 配置文件控制迁移进度
API_MIGRATION_CONFIG = {
    "users": {
        "v2_enabled": True,
        "v1_fallback": True,
        "migration_percentage": 50  # 50%流量到v2
    },
    "roles": {
        "v2_enabled": False,
        "v1_fallback": True,
        "migration_percentage": 0
    }
}
```

### 阶段4: 测试和验证 (第5周)

#### 4.1 兼容性测试
```python
# tests/test_api_compatibility.py
import pytest
from app.api.v1_backup.test_cases import V1TestCases

class TestAPICompatibility:
    def test_v1_v2_response_compatibility(self):
        """测试v1和v2响应的兼容性"""
        # 使用相同输入测试v1和v2
        v1_response = self.call_v1_api("/user/list")
        v2_response = self.call_v2_api("/api/v2/users")
        
        # 验证数据一致性
        assert self.compare_user_data(v1_response, v2_response)
    
    def test_backward_compatibility(self):
        """测试向后兼容性"""
        # 使用v1格式请求v2端点
        response = self.call_v2_with_v1_format("/api/v2/users")
        assert response.status_code == 200
```

#### 4.2 性能对比测试
```python
# tests/test_performance_comparison.py
def test_api_performance_comparison():
    """对比v1和v2的性能"""
    v1_time = measure_api_performance("/user/list")
    v2_time = measure_api_performance("/api/v2/users")
    
    # v2性能不应显著劣于v1
    assert v2_time <= v1_time * 1.2  # 允许20%的性能差异
```

### 阶段5: 生产部署 (第6周)

#### 5.1 蓝绿部署策略
```yaml
# docker-compose.yml
version: '3.8'
services:
  api-blue:  # 当前生产环境(v1)
    image: your-api:v1
    ports:
      - "8000:8000"
  
  api-green:  # 新版本(v2)
    image: your-api:v2
    ports:
      - "8001:8000"
  
  nginx:
    image: nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
```

#### 5.2 流量切换配置
```nginx
# nginx.conf
upstream api_v1 {
    server api-blue:8000;
}

upstream api_v2 {
    server api-green:8000;
}

server {
    listen 80;
    
    # v2 API路由
    location /api/v2/ {
        proxy_pass http://api_v2;
    }
    
    # v1 API路由(兼容)
    location / {
        # 根据配置决定路由到v1还是v2
        if ($http_x_api_version = "2") {
            proxy_pass http://api_v2;
        }
        proxy_pass http://api_v1;
    }
}
```

## 🔧 工具和脚本

### 1. 备份脚本
```bash
#!/bin/bash
# scripts/backup_v1_api.sh

set -e

BACKUP_DIR="app/api/v1_backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "开始备份API v1实现..."

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份代码
rsync -av --exclude='__pycache__' app/ $BACKUP_DIR/

# 备份数据库模式
pg_dump --schema-only $DATABASE_URL > $BACKUP_DIR/schema_$TIMESTAMP.sql

# 创建备份清单
find $BACKUP_DIR -name "*.py" | wc -l > $BACKUP_DIR/file_count.txt

echo "备份完成: $BACKUP_DIR"
```

### 2. 迁移验证脚本
```python
#!/usr/bin/env python3
# scripts/verify_migration.py

import requests
import json
import sys

def verify_api_compatibility():
    """验证API兼容性"""
    test_cases = [
        {
            "name": "用户列表",
            "v1_url": "/user/list",
            "v2_url": "/api/v2/users",
            "method": "GET"
        },
        {
            "name": "用户创建",
            "v1_url": "/user/create",
            "v2_url": "/api/v2/users",
            "method": "POST",
            "data": {"username": "test", "email": "test@example.com"}
        }
    ]
    
    for case in test_cases:
        print(f"测试: {case['name']}")
        
        # 调用v1 API
        v1_response = call_api(case['v1_url'], case['method'], case.get('data'))
        
        # 调用v2 API
        v2_response = call_api(case['v2_url'], case['method'], case.get('data'))
        
        # 比较响应
        if compare_responses(v1_response, v2_response):
            print(f"✅ {case['name']} 兼容性测试通过")
        else:
            print(f"❌ {case['name']} 兼容性测试失败")
            return False
    
    return True

if __name__ == "__main__":
    if verify_api_compatibility():
        print("🎉 所有兼容性测试通过")
        sys.exit(0)
    else:
        print("💥 兼容性测试失败")
        sys.exit(1)
```

### 3. 回滚脚本
```bash
#!/bin/bash
# scripts/rollback_to_v1.sh

set -e

echo "开始回滚到API v1..."

# 停止v2服务
docker-compose stop api-green

# 切换nginx配置到v1
cp nginx/nginx.v1.conf nginx/nginx.conf
nginx -s reload

# 恢复数据库(如果需要)
if [ "$1" = "--restore-db" ]; then
    psql $DATABASE_URL < app/api/v1_backup/schema_backup.sql
fi

echo "回滚完成"
```

## 📊 监控和告警

### 1. API使用监控
```python
# monitoring/api_usage_monitor.py
import logging
from prometheus_client import Counter, Histogram

# 定义指标
api_requests_total = Counter('api_requests_total', 'Total API requests', ['version', 'endpoint', 'method'])
api_response_time = Histogram('api_response_time_seconds', 'API response time', ['version', 'endpoint'])

class APIUsageMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def record_request(self, version, endpoint, method, response_time):
        """记录API请求"""
        api_requests_total.labels(version=version, endpoint=endpoint, method=method).inc()
        api_response_time.labels(version=version, endpoint=endpoint).observe(response_time)
        
        self.logger.info(f"API请求: {version} {method} {endpoint} - {response_time:.3f}s")
```

### 2. 告警规则
```yaml
# monitoring/alerts.yml
groups:
  - name: api_migration
    rules:
      - alert: V1APIHighUsage
        expr: rate(api_requests_total{version="v1"}[5m]) > 100
        for: 5m
        annotations:
          summary: "V1 API使用率过高"
          description: "V1 API在过去5分钟内请求率超过100/s，需要加速迁移"
      
      - alert: V2APIErrorRate
        expr: rate(api_requests_total{version="v2",status=~"5.."}[5m]) > 0.1
        for: 2m
        annotations:
          summary: "V2 API错误率过高"
          description: "V2 API错误率超过10%，可能需要回滚"
```

## 📋 检查清单

### 迁移前检查
- [ ] 完整备份所有v1代码
- [ ] 备份数据库模式和关键数据
- [ ] 创建详细的API端点清单
- [ ] 设置监控和告警
- [ ] 准备回滚方案
- [ ] 通知相关团队和用户

### 迁移中检查
- [ ] 逐步启用v2功能
- [ ] 监控系统性能和错误率
- [ ] 验证数据一致性
- [ ] 测试兼容性
- [ ] 收集用户反馈
- [ ] 记录问题和解决方案

### 迁移后检查
- [ ] 验证所有功能正常
- [ ] 性能指标达标
- [ ] 用户反馈良好
- [ ] 文档更新完成
- [ ] 培训材料准备
- [ ] 制定v1废弃计划

## 🚨 风险缓解

### 1. 技术风险
- **数据不一致**: 实施双写验证机制
- **性能下降**: 提前进行性能测试和优化
- **兼容性问题**: 完善的兼容层和测试覆盖

### 2. 业务风险
- **服务中断**: 蓝绿部署和快速回滚机制
- **用户体验**: 渐进式迁移和充分的用户沟通
- **数据丢失**: 多重备份和验证机制

### 3. 应急预案
- **立即回滚**: 一键回滚脚本和流程
- **降级服务**: 关闭非核心功能，保证核心服务
- **数据恢复**: 从备份快速恢复数据

## 📚 参考资料

1. [API版本管理最佳实践](https://example.com/api-versioning)
2. [微服务迁移指南](https://example.com/microservice-migration)
3. [数据库迁移策略](https://example.com/database-migration)
4. [蓝绿部署实践](https://example.com/blue-green-deployment)

---

**重要提醒**: 
- 在生产环境执行任何迁移操作前，务必在测试环境完整验证
- 保持与团队的密切沟通，确保所有人了解迁移计划和风险
- 准备充分的回滚方案，确保能够快速恢复服务