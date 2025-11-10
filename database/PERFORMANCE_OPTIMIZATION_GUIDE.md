# 数据库性能优化指南

**API权限重构项目 - 任务3.5**  
**创建时间**: 2025-01-10  
**版本**: 1.0

## 概述

本指南提供了API权限系统数据库性能优化的完整解决方案，包括索引优化、查询优化、性能监控和报告生成等功能。

## 🎯 优化目标

- **查询性能提升**: 权限验证查询响应时间 < 100ms
- **索引效率优化**: 减少顺序扫描，提高索引命中率
- **缓存命中率**: 数据库缓存命中率 > 95%
- **监控覆盖**: 建立完整的性能监控体系

## 📁 文件结构

```
database/
├── performance_optimization_indexes.sql      # 核心索引创建脚本
├── performance_optimization_queries.sql      # 查询优化脚本
├── performance_monitoring.py                 # 性能监控系统
├── performance_optimization_report.py        # 性能报告生成器
├── run_performance_optimization.py           # 优化执行脚本
└── PERFORMANCE_OPTIMIZATION_GUIDE.md         # 本指南文档
```

## 🚀 快速开始

### 1. 环境准备

确保已安装必要的Python依赖：

```bash
pip install asyncpg matplotlib pandas
```

### 2. 执行完整优化

```bash
# 执行完整的性能优化
python database/run_performance_optimization.py --db-url "postgresql://user:password@host:port/database"

# 仅验证优化结果
python database/run_performance_optimization.py --db-url "postgresql://user:password@host:port/database" --action verify
```

### 3. 启动性能监控

```bash
# 启动实时监控（60秒间隔）
python database/performance_monitoring.py --db-url "postgresql://user:password@host:port/database" --action monitor --interval 60

# 生成性能报告
python database/performance_monitoring.py --db-url "postgresql://user:password@host:port/database" --action report --hours 24
```

### 4. 生成优化报告

```bash
# 生成综合性能优化报告
python database/performance_optimization_report.py --db-url "postgresql://user:password@host:port/database" --output-dir reports
```

## 📊 优化内容详解

### 1. 核心索引优化

#### 1.1 权限查询核心索引

**API端点表索引**:
```sql
-- 权限验证查询覆盖索引
CREATE INDEX CONCURRENTLY idx_api_endpoints_permission_check 
ON t_sys_api_endpoints(api_path, http_method, api_code, status, is_public) 
WHERE status = 'active';

-- API列表查询覆盖索引
CREATE INDEX CONCURRENTLY idx_api_endpoints_list_query 
ON t_sys_api_endpoints(group_id, status, sort_order, api_name, api_code) 
WHERE status IN ('active', 'inactive');
```

**用户权限表索引**:
```sql
-- 用户权限检查覆盖索引
CREATE INDEX CONCURRENTLY idx_user_permissions_check_cover 
ON t_sys_user_permissions(user_id, permission_code, is_active, expires_at) 
WHERE is_active = true;

-- 用户权限列表覆盖索引
CREATE INDEX CONCURRENTLY idx_user_permissions_list_cover 
ON t_sys_user_permissions(user_id, is_active, permission_code, resource_id, granted_at) 
WHERE is_active = true;
```

**角色权限表索引**:
```sql
-- 角色权限检查覆盖索引
CREATE INDEX CONCURRENTLY idx_role_permissions_check_cover 
ON t_sys_role_permissions(role_id, permission_code, is_active, resource_type) 
WHERE is_active = true;
```

#### 1.2 索引设计原则

1. **覆盖索引**: 包含查询所需的所有列，避免回表查询
2. **部分索引**: 使用WHERE条件过滤，减少索引大小
3. **复合索引**: 按查询频率和选择性排序列
4. **并发创建**: 使用CONCURRENTLY避免锁表

### 2. 查询优化

#### 2.1 权限验证函数

**单个权限验证**:
```sql
CREATE OR REPLACE FUNCTION check_user_permission(
    p_user_id BIGINT,
    p_permission_code VARCHAR(255),
    p_resource_id VARCHAR(100) DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM t_sys_user_permissions up
        WHERE up.user_id = p_user_id 
          AND up.permission_code = p_permission_code
          AND (p_resource_id IS NULL OR up.resource_id = p_resource_id OR up.resource_id IS NULL)
          AND up.is_active = true
          AND (up.expires_at IS NULL OR up.expires_at > NOW())
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql STABLE;
```

**批量权限检查**:
```sql
CREATE OR REPLACE FUNCTION check_user_permissions_batch(
    p_user_id BIGINT,
    p_permission_codes VARCHAR(255)[]
) RETURNS TABLE(permission_code VARCHAR(255), has_permission BOOLEAN);
```

#### 2.2 查询优化原则

1. **使用EXISTS替代COUNT**: 提前终止查询
2. **LIMIT 1优化**: 找到第一个匹配即返回
3. **批量查询**: 减少数据库往返次数
4. **函数稳定性**: 标记为STABLE提升缓存效果

### 3. 性能监控

#### 3.1 监控指标

**表级别监控**:
- 顺序扫描比例
- 死元组比例
- 表大小变化
- VACUUM/ANALYZE执行情况

**索引级别监控**:
- 索引使用频率
- 索引效率
- 未使用索引识别

**查询级别监控**:
- 慢查询识别
- 查询执行计划
- 缓存命中率

**系统级别监控**:
- 连接使用率
- 缓存命中率
- I/O性能

#### 3.2 告警机制

**性能告警阈值**:
```python
thresholds = {
    'slow_query_ms': 100,           # 慢查询阈值
    'very_slow_query_ms': 500,      # 非常慢查询阈值
    'high_rows_examined': 10000,    # 高扫描行数阈值
    'seq_scan_ratio': 0.8,          # 顺序扫描比例阈值
    'cache_hit_ratio': 0.95,        # 缓存命中率阈值
    'connection_usage': 0.8,        # 连接使用率阈值
}
```

### 4. 性能测试

#### 4.1 基准测试

**权限验证性能测试**:
```python
# 测试单个权限检查性能
test_results = await monitor.test_permission_query_performance(
    test_user_id=1, 
    iterations=1000
)
```

**预期性能指标**:
- 单个权限检查: < 5ms
- API权限验证: < 10ms
- 批量权限检查: < 20ms

#### 4.2 压力测试

**并发测试场景**:
- 100个并发用户权限验证
- 1000次/秒的权限检查请求
- 大数据量下的查询性能

## 📈 监控和维护

### 1. 日常监控

#### 1.1 启动监控服务

```bash
# 后台启动监控服务
nohup python database/performance_monitoring.py \
  --db-url "postgresql://user:password@host:port/database" \
  --action monitor \
  --interval 60 > monitoring.log 2>&1 &
```

#### 1.2 查看监控数据

```sql
-- 查看最近24小时的性能指标
SELECT 
    query_type,
    COUNT(*) as count,
    AVG(execution_time_ms) as avg_time,
    MAX(execution_time_ms) as max_time
FROM t_sys_performance_metrics 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY query_type
ORDER BY avg_time DESC;

-- 查看未解决的性能告警
SELECT 
    alert_type,
    severity,
    message,
    created_at
FROM t_sys_performance_alerts 
WHERE is_resolved = FALSE
ORDER BY created_at DESC;
```

### 2. 定期维护

#### 2.1 每日维护任务

```sql
-- 更新表统计信息
ANALYZE t_sys_api_endpoints;
ANALYZE t_sys_user_permissions;
ANALYZE t_sys_role_permissions;

-- 刷新权限缓存
SELECT refresh_user_permissions_cache();
```

#### 2.2 每周维护任务

```sql
-- 清理死元组
VACUUM ANALYZE t_sys_api_endpoints;
VACUUM ANALYZE t_sys_user_permissions;
VACUUM ANALYZE t_sys_role_permissions;

-- 重建索引（如果需要）
REINDEX INDEX CONCURRENTLY idx_user_permissions_check_cover;
```

#### 2.3 每月维护任务

```bash
# 生成月度性能报告
python database/performance_optimization_report.py \
  --db-url "postgresql://user:password@host:port/database" \
  --output-dir monthly_reports

# 清理历史监控数据（保留3个月）
DELETE FROM t_sys_performance_metrics 
WHERE created_at < NOW() - INTERVAL '3 months';

DELETE FROM t_sys_performance_alerts 
WHERE created_at < NOW() - INTERVAL '3 months' AND is_resolved = TRUE;
```

## 🔧 故障排除

### 1. 常见问题

#### 1.1 索引创建失败

**问题**: 索引创建时出现锁等待或超时

**解决方案**:
```sql
-- 使用CONCURRENTLY创建索引
CREATE INDEX CONCURRENTLY idx_name ON table_name(column);

-- 如果失败，先删除无效索引
DROP INDEX CONCURRENTLY IF EXISTS idx_name;
```

#### 1.2 查询性能下降

**问题**: 权限验证查询突然变慢

**诊断步骤**:
```sql
-- 1. 检查执行计划
EXPLAIN (ANALYZE, BUFFERS) 
SELECT check_user_permission(1, 'GET /api/v2/users');

-- 2. 检查索引使用情况
SELECT * FROM v_permission_index_stats 
WHERE tablename = 't_sys_user_permissions';

-- 3. 检查表统计信息
SELECT * FROM v_permission_query_stats 
WHERE tablename = 't_sys_user_permissions';
```

**解决方案**:
```sql
-- 更新统计信息
ANALYZE t_sys_user_permissions;

-- 如果索引膨胀，重建索引
REINDEX INDEX CONCURRENTLY idx_user_permissions_check_cover;
```

#### 1.3 监控服务异常

**问题**: 性能监控服务停止工作

**诊断步骤**:
1. 检查监控进程状态
2. 查看监控日志文件
3. 验证数据库连接

**解决方案**:
```bash
# 重启监控服务
pkill -f performance_monitoring.py
nohup python database/performance_monitoring.py \
  --db-url "postgresql://user:password@host:port/database" \
  --action monitor \
  --interval 60 > monitoring.log 2>&1 &
```

### 2. 性能调优建议

#### 2.1 PostgreSQL配置优化

```ini
# postgresql.conf 推荐配置
shared_buffers = 256MB                    # 内存的25%
effective_cache_size = 1GB                # 系统缓存大小
work_mem = 4MB                           # 排序和哈希操作内存
maintenance_work_mem = 64MB              # 维护操作内存
checkpoint_completion_target = 0.9       # 检查点完成目标
wal_buffers = 16MB                       # WAL缓冲区大小
random_page_cost = 1.1                   # SSD存储建议值
```

#### 2.2 连接池配置

```ini
# PgBouncer配置示例
[databases]
devicemonitor = host=localhost port=5432 dbname=devicemonitor

[pgbouncer]
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
reserve_pool_size = 5
```

## 📋 性能报告解读

### 1. 报告结构

生成的性能报告包含以下部分：

1. **执行摘要**: 优化机会总数和优先级分布
2. **表统计分析**: 表大小、访问模式、维护状态
3. **索引分析**: 索引使用情况、缺失索引建议
4. **查询性能分析**: 慢查询识别和优化建议
5. **缓存性能分析**: 缓存命中率和优化建议
6. **连接分析**: 连接使用情况和配置建议
7. **优化建议**: 按优先级排序的具体优化措施

### 2. 关键指标解读

#### 2.1 表性能指标

- **顺序扫描比例**: < 30% 为良好，> 50% 需要优化
- **死元组比例**: < 10% 为良好，> 20% 需要VACUUM
- **索引命中率**: > 95% 为良好

#### 2.2 查询性能指标

- **平均响应时间**: < 100ms 为良好
- **缓存命中率**: > 95% 为良好
- **并发连接数**: < 80% 最大连接数为安全

### 3. 优化建议优先级

- **高优先级**: 影响用户体验的性能问题
- **中优先级**: 影响系统效率的配置问题
- **低优先级**: 长期维护和预防性优化

## 🔄 持续优化

### 1. 性能基线建立

在优化前后建立性能基线，用于对比优化效果：

```bash
# 优化前基线测试
python database/performance_monitoring.py \
  --db-url "postgresql://user:password@host:port/database" \
  --action test \
  --test-user 1 \
  --iterations 1000 > baseline_before.json

# 执行优化
python database/run_performance_optimization.py \
  --db-url "postgresql://user:password@host:port/database"

# 优化后基线测试
python database/performance_monitoring.py \
  --db-url "postgresql://user:password@host:port/database" \
  --action test \
  --test-user 1 \
  --iterations 1000 > baseline_after.json
```

### 2. 定期评估

建议每月执行一次完整的性能评估：

1. 生成性能报告
2. 分析性能趋势
3. 识别新的优化机会
4. 更新优化策略

### 3. 容量规划

根据业务增长预测，提前进行容量规划：

- 监控数据增长趋势
- 预测查询负载增长
- 规划硬件资源需求
- 制定扩容策略

## 📞 支持和反馈

如果在使用过程中遇到问题或有改进建议，请：

1. 查看本指南的故障排除部分
2. 检查监控日志和错误信息
3. 联系数据库管理团队
4. 提交问题报告和改进建议

---

**文档版本**: 1.0  
**最后更新**: 2025-01-10  
**维护团队**: API权限重构项目组