# 权限系统监控和运维指南

## 概述

本指南提供权限系统的监控、运维和故障排除方法，帮助运维人员确保系统稳定运行。

## 目录

- [监控指标](#监控指标)
- [告警配置](#告警配置)
- [日志管理](#日志管理)
- [性能监控](#性能监控)
- [故障排除](#故障排除)
- [备份恢复](#备份恢复)

## 监控指标

### 1. 应用指标

#### 核心业务指标
```yaml
# 认证相关
auth_login_total: 登录总次数
auth_login_success_rate: 登录成功率
auth_token_generation_total: 令牌生成总数
auth_token_validation_total: 令牌验证总数

# 权限相关  
permission_check_total: 权限检查总次数
permission_check_success_rate: 权限检查成功率
permission_cache_hit_rate: 权限缓存命中率
permission_check_duration: 权限检查耗时

# 用户相关
active_users_total: 活跃用户数
concurrent_sessions_total: 并发会话数
user_operations_total: 用户操作总数
```#### 系统
性能指标
```yaml
# HTTP 请求
http_requests_total: HTTP请求总数
http_request_duration_seconds: HTTP请求耗时
http_requests_per_second: 每秒请求数
http_response_size_bytes: 响应大小

# 数据库
db_connections_active: 活跃数据库连接数
db_connections_idle: 空闲数据库连接数
db_query_duration_seconds: 数据库查询耗时
db_slow_queries_total: 慢查询总数

# 缓存
redis_connections_active: Redis活跃连接数
redis_memory_usage_bytes: Redis内存使用量
redis_operations_total: Redis操作总数
redis_hit_rate: Redis命中率
```

#### 错误指标
```yaml
# 应用错误
app_errors_total: 应用错误总数
app_exceptions_total: 异常总数
permission_denied_total: 权限拒绝总数
authentication_failures_total: 认证失败总数

# HTTP 错误
http_4xx_errors_total: 4xx错误总数
http_5xx_errors_total: 5xx错误总数
timeout_errors_total: 超时错误总数
```

### 2. 基础设施指标

#### 服务器资源
```yaml
# CPU
cpu_usage_percent: CPU使用率
cpu_load_average: CPU负载平均值

# 内存
memory_usage_percent: 内存使用率
memory_available_bytes: 可用内存

# 磁盘
disk_usage_percent: 磁盘使用率
disk_io_read_bytes: 磁盘读取字节数
disk_io_write_bytes: 磁盘写入字节数

# 网络
network_receive_bytes: 网络接收字节数
network_transmit_bytes: 网络发送字节数
```

## 告警配置

### 1. 关键告警规则

#### 服务可用性告警
```yaml
# 服务下线告警
- alert: ServiceDown
  expr: up == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "服务 {{ $labels.instance }} 下线"
    description: "服务已下线超过1分钟"

# HTTP错误率告警
- alert: HighErrorRate
  expr: rate(http_5xx_errors_total[5m]) > 0.1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "HTTP 5xx错误率过高"
    description: "5分钟内5xx错误率超过10%"
```

#### 性能告警
```yaml
# 响应时间告警
- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
  for: 3m
  labels:
    severity: warning
  annotations:
    summary: "响应时间过长"
    description: "95%的请求响应时间超过1秒"

# 权限检查延迟告警
- alert: PermissionCheckSlow
  expr: histogram_quantile(0.95, rate(permission_check_duration_bucket[5m])) > 0.1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "权限检查延迟过高"
    description: "95%的权限检查耗时超过100ms"
```

#### 资源告警
```yaml
# CPU使用率告警
- alert: HighCPUUsage
  expr: cpu_usage_percent > 80
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "CPU使用率过高"
    description: "CPU使用率持续5分钟超过80%"

# 内存使用率告警
- alert: HighMemoryUsage
  expr: memory_usage_percent > 85
  for: 3m
  labels:
    severity: critical
  annotations:
    summary: "内存使用率过高"
    description: "内存使用率持续3分钟超过85%"
```

#### 安全告警
```yaml
# 认证失败率告警
- alert: HighAuthFailureRate
  expr: rate(authentication_failures_total[5m]) > 10
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "认证失败率过高"
    description: "5分钟内认证失败率超过每分钟10次"

# 权限拒绝率告警
- alert: HighPermissionDeniedRate
  expr: rate(permission_denied_total[5m]) > 50
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "权限拒绝率过高"
    description: "5分钟内权限拒绝率超过每分钟50次"
```

### 2. 告警通知配置

#### Slack 通知
```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts'
    title: '权限系统告警'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

#### 邮件通知
```yaml
receivers:
- name: 'email'
  email_configs:
  - to: 'admin@example.com'
    from: 'alerts@example.com'
    smarthost: 'smtp.example.com:587'
    auth_username: 'alerts@example.com'
    auth_password: 'password'
    subject: '权限系统告警: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      告警: {{ .Annotations.summary }}
      描述: {{ .Annotations.description }}
      时间: {{ .StartsAt }}
      {{ end }}
```

## 日志管理

### 1. 日志分类

#### 应用日志
```python
# 日志级别和用途
DEBUG: 调试信息，开发环境使用
INFO: 一般信息，如用户登录、操作记录
WARNING: 警告信息，如权限检查失败
ERROR: 错误信息，如系统异常
CRITICAL: 严重错误，如服务无法启动
```

#### 审计日志
```json
{
  "timestamp": "2025-10-10T10:00:00Z",
  "user_id": 123,
  "username": "admin",
  "action": "LOGIN",
  "resource": "AUTH",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "result": "SUCCESS",
  "details": {
    "login_method": "password"
  }
}
```

#### 安全日志
```json
{
  "timestamp": "2025-10-10T10:00:00Z",
  "event_type": "SUSPICIOUS_ACTIVITY",
  "severity": "HIGH",
  "user_id": 123,
  "ip_address": "192.168.1.100",
  "description": "Multiple failed login attempts",
  "details": {
    "failed_attempts": 5,
    "time_window": "5m"
  }
}
```

### 2. 日志收集和分析

#### ELK Stack 配置
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /app/logs/*.log
  fields:
    service: permission-system
    environment: production

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "permission-system-%{+yyyy.MM.dd}"

# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "permission-system" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "permission-system-%{+YYYY.MM.dd}"
  }
}
```

#### 日志查询示例
```bash
# 查询登录失败日志
curl -X GET "elasticsearch:9200/permission-system-*/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        {"match": {"action": "LOGIN"}},
        {"match": {"result": "FAILED"}}
      ],
      "range": {
        "timestamp": {
          "gte": "now-1h"
        }
      }
    }
  }
}'

# 查询权限拒绝日志
curl -X GET "elasticsearch:9200/permission-system-*/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        {"match": {"level": "WARNING"}},
        {"match": {"message": "permission denied"}}
      ]
    }
  },
  "aggs": {
    "top_users": {
      "terms": {
        "field": "user_id",
        "size": 10
      }
    }
  }
}'
```

## 性能监控

### 1. 关键性能指标

#### 响应时间监控
```python
# 性能监控装饰器
import time
import functools
from prometheus_client import Histogram

REQUEST_TIME = Histogram('request_processing_seconds', 'Time spent processing request')

def monitor_performance(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            REQUEST_TIME.observe(time.time() - start_time)
    return wrapper

# 使用示例
@monitor_performance
def check_permission(user_id, permission):
    # 权限检查逻辑
    pass
```

#### 数据库性能监控
```sql
-- 慢查询监控
SELECT 
    query,
    mean_time,
    calls,
    total_time,
    mean_time/calls as avg_time_per_call
FROM pg_stat_statements 
WHERE mean_time > 100  -- 超过100ms的查询
ORDER BY mean_time DESC;

-- 连接数监控
SELECT 
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active_connections,
    count(*) FILTER (WHERE state = 'idle') as idle_connections
FROM pg_stat_activity;
```

#### 缓存性能监控
```python
# Redis 性能监控
def get_redis_stats():
    info = redis_client.info()
    return {
        'used_memory': info['used_memory'],
        'used_memory_human': info['used_memory_human'],
        'connected_clients': info['connected_clients'],
        'total_commands_processed': info['total_commands_processed'],
        'keyspace_hits': info['keyspace_hits'],
        'keyspace_misses': info['keyspace_misses'],
        'hit_rate': info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses'])
    }
```

### 2. 性能优化建议

#### 数据库优化
```sql
-- 创建必要的索引
CREATE INDEX CONCURRENTLY idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX CONCURRENTLY idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX CONCURRENTLY idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX CONCURRENTLY idx_audit_logs_user_id ON audit_logs(user_id);

-- 分析表统计信息
ANALYZE users;
ANALYZE roles;
ANALYZE permissions;
ANALYZE user_roles;
ANALYZE role_permissions;
```

#### 缓存优化
```python
# 缓存预热
def warm_up_cache():
    """预热权限缓存"""
    active_users = get_active_users()
    for user in active_users:
        # 预加载用户权限
        get_user_permissions(user.id)
        # 预加载用户菜单
        get_user_menus(user.id)

# 批量缓存更新
def batch_update_cache(user_ids):
    """批量更新用户权限缓存"""
    pipeline = redis_client.pipeline()
    for user_id in user_ids:
        permissions = load_user_permissions_from_db(user_id)
        cache_key = f"permissions:{user_id}"
        pipeline.setex(cache_key, 3600, json.dumps(permissions))
    pipeline.execute()
```

## 故障排除

### 1. 常见问题诊断

#### 服务无法启动
```bash
# 检查服务状态
docker-compose ps

# 查看服务日志
docker-compose logs permission-app

# 检查端口占用
netstat -tlnp | grep :8000

# 检查配置文件
docker-compose config
```

#### 数据库连接问题
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U postgres

# 查看数据库日志
docker-compose logs postgres

# 测试数据库连接
docker-compose exec permission-app python -c "
from app.core.database import database
print('Database connection:', database.is_connected)
"
```

#### Redis连接问题
```bash
# 检查Redis状态
docker-compose exec redis redis-cli ping

# 查看Redis日志
docker-compose logs redis

# 检查Redis内存使用
docker-compose exec redis redis-cli info memory
```

#### 权限检查异常
```python
# 权限检查调试
def debug_permission_check(user_id, permission):
    print(f"检查用户 {user_id} 的权限 {permission}")
    
    # 1. 检查用户是否存在
    user = get_user(user_id)
    if not user:
        print("用户不存在")
        return False
    
    # 2. 检查用户状态
    if not user.is_active:
        print("用户已禁用")
        return False
    
    # 3. 检查超级用户
    if user.is_superuser:
        print("超级用户，拥有所有权限")
        return True
    
    # 4. 检查用户角色
    roles = get_user_roles(user_id)
    print(f"用户角色: {[r.role_key for r in roles]}")
    
    # 5. 检查角色权限
    for role in roles:
        role_permissions = get_role_permissions(role.id)
        print(f"角色 {role.role_key} 权限: {role_permissions}")
        if permission in role_permissions:
            print(f"在角色 {role.role_key} 中找到权限")
            return True
    
    print("未找到权限")
    return False
```

### 2. 性能问题排查

#### 慢查询分析
```sql
-- 启用慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 记录超过1秒的查询
SELECT pg_reload_conf();

-- 查看慢查询
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    stddev_time
FROM pg_stat_statements 
WHERE mean_time > 1000
ORDER BY mean_time DESC;
```

#### 内存泄漏检查
```python
# 内存使用监控
import psutil
import gc

def check_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # 检查Python对象数量
    print(f"Python objects: {len(gc.get_objects())}")
    
    # 强制垃圾回收
    collected = gc.collect()
    print(f"Collected objects: {collected}")
```

## 备份恢复

### 1. 数据备份策略

#### 数据库备份
```bash
#!/bin/bash
# 数据库备份脚本

BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
docker-compose exec -T postgres pg_dump -U postgres permission_system > $BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_FILE

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "数据库备份完成: $BACKUP_FILE.gz"
```

#### 配置文件备份
```bash
#!/bin/bash
# 配置备份脚本

BACKUP_DIR="/app/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份配置文件
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" \
    deploy/environments/ \
    deploy/docker/ \
    config/

echo "配置备份完成: $BACKUP_DIR/config_backup_$DATE.tar.gz"
```

### 2. 数据恢复流程

#### 数据库恢复
```bash
#!/bin/bash
# 数据库恢复脚本

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file>"
    exit 1
fi

# 停止应用服务
docker-compose stop permission-app

# 恢复数据库
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | docker-compose exec -T postgres psql -U postgres permission_system
else
    docker-compose exec -T postgres psql -U postgres permission_system < $BACKUP_FILE
fi

# 重启服务
docker-compose start permission-app

echo "数据库恢复完成"
```

#### 灾难恢复计划
```yaml
# 灾难恢复步骤
1. 评估损坏程度:
   - 检查服务状态
   - 检查数据完整性
   - 评估恢复时间

2. 停止服务:
   - 停止应用服务
   - 停止数据库服务
   - 通知用户维护

3. 数据恢复:
   - 恢复数据库备份
   - 恢复配置文件
   - 验证数据完整性

4. 服务重启:
   - 启动数据库服务
   - 启动应用服务
   - 执行健康检查

5. 验证恢复:
   - 测试核心功能
   - 检查数据一致性
   - 通知用户恢复完成
```

## 运维自动化

### 1. 定时任务

#### Crontab 配置
```bash
# 权限系统定时任务
# 每天凌晨2点备份数据库
0 2 * * * /app/scripts/backup_database.sh

# 每小时清理过期会话
0 * * * * /app/scripts/cleanup_sessions.sh

# 每天凌晨3点清理日志
0 3 * * * /app/scripts/cleanup_logs.sh

# 每周日凌晨4点生成性能报告
0 4 * * 0 /app/scripts/generate_performance_report.sh
```

#### 健康检查脚本
```bash
#!/bin/bash
# 健康检查脚本

check_service() {
    local service=$1
    local url=$2
    
    if curl -f -s $url > /dev/null; then
        echo "✓ $service 正常"
        return 0
    else
        echo "✗ $service 异常"
        return 1
    fi
}

# 检查各个服务
check_service "应用服务" "http://localhost:8000/health"
check_service "数据库" "http://localhost:5432"
check_service "Redis" "http://localhost:6379"

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠ 磁盘使用率过高: $DISK_USAGE%"
fi

# 检查内存使用
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -gt 85 ]; then
    echo "⚠ 内存使用率过高: $MEMORY_USAGE%"
fi
```

### 2. 自动化部署

#### CI/CD 流水线
```yaml
# .github/workflows/deploy.yml
name: Deploy Permission System

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run Tests
      run: |
        python -m pytest tests/
        
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build Docker Image
      run: |
        docker build -t permission-system:${{ github.sha }} .
        
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to Production
      run: |
        ./deploy/scripts/deploy.sh production ${{ github.sha }}
```

---

**文档版本**: v2.0  
**最后更新**: 2025-10-10  
**适用版本**: 权限系统 v2.0+