# 分阶段数据库迁移操作手册

## 概述

本手册详细介绍了分阶段数据库迁移策略的操作流程、最佳实践和故障排除方法。分阶段迁移策略通过双写机制、数据一致性验证、配置化读取切换和监控告警系统，确保数据库迁移的安全性和可靠性。

## 系统架构

### 核心组件

1. **分阶段迁移策略管理器** (`PhasedMigrationStrategy`)
   - 管理迁移配置和状态
   - 实现双写机制
   - 提供迁移阶段控制

2. **数据一致性验证器** (`DataConsistencyValidator`)
   - 执行多级别数据一致性检查
   - 生成详细的差异报告
   - 提供修复建议

3. **配置化读取切换器** (`ConfigurableReadSwitch`)
   - 支持多种切换策略
   - 实现灰度发布和A/B测试
   - 提供实时指标监控

4. **迁移告警系统** (`MigrationAlertingSystem`)
   - 实时监控迁移状态
   - 智能告警和通知
   - 自动恢复机制

### 迁移阶段

```mermaid
graph TD
    A[准备阶段] --> B[双写阶段]
    B --> C[验证阶段]
    C --> D[读取切换阶段]
    D --> E[清理阶段]
    E --> F[完成阶段]
    
    C --> G[回滚]
    D --> G
    G --> A
```

## 操作流程

### 阶段1：准备阶段 (Preparation)

#### 1.1 环境准备

```bash
# 1. 安装依赖
pip install asyncpg aiohttp

# 2. 配置数据库连接
export DATABASE_URL="postgresql://user:password@localhost:5432/database"

# 3. 初始化迁移系统
python database/phased_migration_strategy.py --db-url $DATABASE_URL --action status
```

#### 1.2 创建迁移配置

```python
from database.phased_migration_strategy import PhasedMigrationStrategy, MigrationConfig, MigrationPhase, ConsistencyLevel

# 创建迁移配置
config = MigrationConfig(
    migration_id="users_table_migration",
    source_table="users",
    target_table="t_sys_users",
    phase=MigrationPhase.PREPARATION,
    consistency_level=ConsistencyLevel.STRICT,
    dual_write_enabled=False,
    read_from_target=False,
    validation_enabled=True,
    auto_switch_threshold=0.99,
    rollback_enabled=True
)

# 注册配置
strategy = PhasedMigrationStrategy(DATABASE_URL)
await strategy.connect()
await strategy.register_migration(config)
```

#### 1.3 设置告警规则

```python
from database.migration_alerting_system import MigrationAlertingSystem, AlertRule, AlertType, AlertSeverity

# 创建告警规则
rule = AlertRule(
    rule_id="users_migration_failure",
    rule_name="用户表迁移失败告警",
    alert_type=AlertType.MIGRATION_FAILURE,
    severity=AlertSeverity.CRITICAL,
    condition="SELECT COUNT(*) FROM t_sys_migration_logs WHERE migration_id = 'users_table_migration' AND status = 'failed' AND created_at > NOW() - INTERVAL '5 minutes'",
    threshold=1.0,
    duration=60,
    auto_recovery=True,
    recovery_action="retry_migration"
)

# 注册告警规则
alerting = MigrationAlertingSystem(DATABASE_URL)
await alerting.connect()
await alerting.register_alert_rule(rule)
```

### 阶段2：双写阶段 (Dual Write)

#### 2.1 启用双写

```bash
# 启用双写机制
python database/phased_migration_strategy.py \
    --db-url $DATABASE_URL \
    --action enable-dual-write \
    --migration-id users_table_migration
```

#### 2.2 验证双写功能

```python
# 使用双写事务
async with strategy.dual_write_transaction("users_table_migration"):
    # 执行数据操作
    await connection.execute("INSERT INTO users (name, email) VALUES ($1, $2)", "test", "test@example.com")
    # 系统会自动同时写入源表和目标表
```

#### 2.3 监控双写指标

```bash
# 获取双写指标
python database/phased_migration_strategy.py \
    --db-url $DATABASE_URL \
    --action status \
    --migration-id users_table_migration
```

### 阶段3：验证阶段 (Validation)

#### 3.1 执行数据一致性检查

```bash
# 基础验证
python database/data_consistency_validator.py \
    --db-url $DATABASE_URL \
    --source-table users \
    --target-table t_sys_users \
    --level basic

# 详细验证
python database/data_consistency_validator.py \
    --db-url $DATABASE_URL \
    --source-table users \
    --target-table t_sys_users \
    --level detailed \
    --sample-size 10000
```

#### 3.2 分析验证结果

```python
# 获取验证报告
validator = DataConsistencyValidator(DATABASE_URL)
await validator.connect()

result = await validator.validate_table_consistency(
    "users", "t_sys_users", 
    ValidationLevel.COMPREHENSIVE
)

print(f"一致性分数: {result.consistency_score}")
print(f"差异数量: {len(result.differences)}")
print(f"修复建议: {result.recommendations}")
```

#### 3.3 处理数据差异

```python
# 分析差异类型
for diff in result.differences:
    if diff.difference_type == DifferenceType.MISSING_IN_TARGET:
        print(f"目标表缺失记录: {diff.record_id}")
        print(f"修复建议: {diff.suggested_fix}")
    elif diff.difference_type == DifferenceType.FIELD_MISMATCH:
        print(f"字段不匹配: {diff.field_name}, 源值: {diff.source_value}, 目标值: {diff.target_value}")
```

### 阶段4：读取切换阶段 (Read Switch)

#### 4.1 配置读取切换

```python
from database.configurable_read_switch import ConfigurableReadSwitch, SwitchConfig, SwitchStrategy, ReadSource

# 创建切换配置
switch_config = SwitchConfig(
    config_id="users_gradual_switch",
    table_name="users",
    current_source=ReadSource.SOURCE,
    target_source=ReadSource.TARGET,
    strategy=SwitchStrategy.GRADUAL,
    switch_percentage=10.0,  # 从10%开始
    conditions={
        "consistency_threshold": 0.99,
        "error_rate_threshold": 0.01
    },
    rollback_enabled=True,
    auto_rollback_threshold=0.05
)

# 注册切换配置
switch = ConfigurableReadSwitch(DATABASE_URL)
await switch.connect()
await switch.register_switch_config(switch_config)
```

#### 4.2 渐进式切换

```bash
# 激活切换
python database/configurable_read_switch.py \
    --db-url $DATABASE_URL \
    --action activate \
    --config-id users_gradual_switch

# 逐步增加切换百分比
python database/configurable_read_switch.py \
    --db-url $DATABASE_URL \
    --action update-percentage \
    --config-id users_gradual_switch \
    --percentage 25.0

# 继续增加到50%
python database/configurable_read_switch.py \
    --db-url $DATABASE_URL \
    --action update-percentage \
    --config-id users_gradual_switch \
    --percentage 50.0

# 最终切换到100%
python database/configurable_read_switch.py \
    --db-url $DATABASE_URL \
    --action update-percentage \
    --config-id users_gradual_switch \
    --percentage 100.0
```

#### 4.3 监控切换指标

```bash
# 获取切换分析
python database/configurable_read_switch.py \
    --db-url $DATABASE_URL \
    --action analytics \
    --config-id users_gradual_switch
```

### 阶段5：清理阶段 (Cleanup)

#### 5.1 禁用双写

```bash
# 禁用双写机制
python database/phased_migration_strategy.py \
    --db-url $DATABASE_URL \
    --action disable-dual-write \
    --migration-id users_table_migration
```

#### 5.2 最终验证

```bash
# 执行最终一致性检查
python database/data_consistency_validator.py \
    --db-url $DATABASE_URL \
    --source-table users \
    --target-table t_sys_users \
    --level comprehensive \
    --export final_validation_report.json
```

#### 5.3 更新迁移状态

```python
# 更新到完成状态
await strategy.update_migration_phase("users_table_migration", MigrationPhase.COMPLETED)
```

## 监控和告警

### 启动监控系统

```bash
# 启动告警监控
python database/migration_alerting_system.py \
    --db-url $DATABASE_URL \
    --action monitor \
    --config-file database/alerting_config.json
```

### 查看告警状态

```bash
# 查看活跃告警
python database/migration_alerting_system.py \
    --db-url $DATABASE_URL \
    --action status

# 获取告警统计
python database/migration_alerting_system.py \
    --db-url $DATABASE_URL \
    --action statistics \
    --days 7
```

### 处理告警

```bash
# 确认告警
python database/migration_alerting_system.py \
    --db-url $DATABASE_URL \
    --action acknowledge \
    --alert-id alert_123 \
    --user admin

# 解决告警
python database/migration_alerting_system.py \
    --db-url $DATABASE_URL \
    --action resolve \
    --alert-id alert_123 \
    --user admin
```

## 故障处理

### 常见问题和解决方案

#### 1. 双写失败

**症状**: 双写日志显示目标表写入失败

**诊断**:
```sql
SELECT * FROM t_sys_dual_write_logs 
WHERE migration_id = 'users_table_migration' 
  AND target_success = FALSE 
ORDER BY created_at DESC LIMIT 10;
```

**解决方案**:
1. 检查目标表结构和约束
2. 验证数据类型兼容性
3. 检查外键约束
4. 修复数据转换逻辑

#### 2. 数据一致性问题

**症状**: 一致性检查显示大量差异

**诊断**:
```bash
python database/data_consistency_validator.py \
    --db-url $DATABASE_URL \
    --source-table users \
    --target-table t_sys_users \
    --level detailed \
    --export consistency_analysis.json
```

**解决方案**:
1. 分析差异类型和分布
2. 检查数据迁移脚本
3. 修复字段映射问题
4. 重新执行数据同步

#### 3. 切换性能问题

**症状**: 切换后响应时间增加

**诊断**:
```bash
python database/configurable_read_switch.py \
    --db-url $DATABASE_URL \
    --action analytics \
    --config-id users_gradual_switch
```

**解决方案**:
1. 检查目标表索引
2. 优化查询语句
3. 调整切换百分比
4. 考虑回滚到源表

#### 4. 告警风暴

**症状**: 大量重复告警

**解决方案**:
1. 调整告警阈值
2. 增加抑制时间
3. 修复根本问题
4. 临时禁用相关规则

### 紧急回滚程序

#### 自动回滚

```python
# 系统会在以下情况自动回滚：
# 1. 错误率超过阈值
# 2. 一致性分数低于阈值
# 3. 关键告警触发

# 检查自动回滚条件
await switch.check_auto_rollback()
```

#### 手动回滚

```bash
# 立即回滚读取切换
python database/configurable_read_switch.py \
    --db-url $DATABASE_URL \
    --action rollback \
    --config-id users_gradual_switch

# 回滚迁移状态
python database/phased_migration_strategy.py \
    --db-url $DATABASE_URL \
    --action rollback \
    --migration-id users_table_migration
```

## 最佳实践

### 1. 迁移前准备

- **备份数据**: 在开始迁移前创建完整备份
- **测试环境验证**: 在测试环境完整执行迁移流程
- **性能基准**: 建立源表的性能基准
- **监控准备**: 配置完整的监控和告警

### 2. 迁移过程中

- **渐进式切换**: 从小百分比开始，逐步增加
- **持续监控**: 密切关注指标和告警
- **定期验证**: 定期执行一致性检查
- **文档记录**: 记录所有操作和决策

### 3. 迁移后维护

- **性能监控**: 持续监控目标表性能
- **数据质量**: 定期检查数据质量
- **清理工作**: 及时清理临时表和日志
- **经验总结**: 总结经验教训

### 4. 安全考虑

- **权限控制**: 严格控制迁移操作权限
- **审计日志**: 记录所有关键操作
- **加密传输**: 确保数据传输安全
- **敏感数据**: 特别处理敏感数据迁移

## 配置文件示例

### 迁移配置 (migration_configs.json)

```json
{
  "migrations": [
    {
      "migration_id": "users_table_migration",
      "source_table": "users",
      "target_table": "t_sys_users",
      "phase": "preparation",
      "consistency_level": "strict",
      "dual_write_enabled": false,
      "read_from_target": false,
      "validation_enabled": true,
      "auto_switch_threshold": 0.99,
      "rollback_enabled": true
    }
  ]
}
```

### 切换配置 (read_switch_configs.json)

```json
{
  "switch_configs": [
    {
      "config_id": "users_gradual_switch",
      "table_name": "users",
      "current_source": "source",
      "target_source": "target",
      "strategy": "gradual",
      "switch_percentage": 0.0,
      "conditions": {
        "consistency_threshold": 0.99,
        "error_rate_threshold": 0.01,
        "latency_threshold": 100
      },
      "rollback_enabled": true,
      "auto_rollback_threshold": 0.05,
      "status": "inactive"
    }
  ]
}
```

### 告警配置 (alerting_config.json)

```json
{
  "alert_rules": [
    {
      "rule_id": "migration_failure_rule",
      "rule_name": "迁移失败告警",
      "alert_type": "migration_failure",
      "severity": "critical",
      "condition": "SELECT COUNT(*) FROM t_sys_migration_logs WHERE status = 'failed' AND created_at > NOW() - INTERVAL '5 minutes'",
      "threshold": 1.0,
      "duration": 60,
      "enabled": true,
      "notification_channels": ["email", "slack"],
      "suppression_duration": 300,
      "auto_recovery": true,
      "recovery_action": "retry_failed_migrations"
    }
  ],
  "notification_configs": [
    {
      "channel": "email",
      "enabled": true,
      "config": {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "username": "alert@example.com",
        "password": "password",
        "from_email": "alert@example.com",
        "to_emails": ["admin@example.com"],
        "use_tls": true
      }
    }
  ]
}
```

## 性能调优

### 数据库优化

```sql
-- 为迁移相关表创建索引
CREATE INDEX CONCURRENTLY idx_migration_logs_status_created 
ON t_sys_migration_logs(status, created_at);

CREATE INDEX CONCURRENTLY idx_dual_write_logs_migration_created 
ON t_sys_dual_write_logs(migration_id, created_at);

CREATE INDEX CONCURRENTLY idx_consistency_checks_migration_created 
ON t_sys_consistency_checks(migration_id, created_at);

-- 优化查询性能
ANALYZE t_sys_migration_logs;
ANALYZE t_sys_dual_write_logs;
ANALYZE t_sys_consistency_checks;
```

### 应用程序优化

```python
# 连接池配置
import asyncpg

async def create_connection_pool():
    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=20,
        command_timeout=60,
        server_settings={
            'application_name': 'migration_system',
            'jit': 'off'
        }
    )

# 批量操作优化
async def batch_consistency_check(validator, records, batch_size=1000):
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        await validator.validate_batch(batch)
        await asyncio.sleep(0.1)  # 避免过载
```

## 监控指标

### 关键指标

1. **迁移成功率**: 成功迁移的记录比例
2. **数据一致性分数**: 源表和目标表的一致性程度
3. **双写成功率**: 双写操作的成功比例
4. **切换错误率**: 读取切换的错误比例
5. **平均响应时间**: 操作的平均响应时间

### 告警阈值建议

| 指标 | 警告阈值 | 严重阈值 |
|------|----------|----------|
| 迁移成功率 | < 95% | < 90% |
| 一致性分数 | < 0.99 | < 0.95 |
| 双写成功率 | < 98% | < 95% |
| 切换错误率 | > 1% | > 5% |
| 响应时间 | > 100ms | > 500ms |

## 总结

分阶段数据库迁移策略通过系统化的方法，确保了数据库迁移的安全性和可靠性。通过双写机制、一致性验证、配置化切换和智能告警，可以实现零停机时间的数据库迁移。

关键成功因素：
1. 充分的准备和测试
2. 渐进式的切换策略
3. 全面的监控和告警
4. 快速的故障响应能力
5. 完善的回滚机制

遵循本手册的操作流程和最佳实践，可以大大降低数据库迁移的风险，确保业务的连续性和数据的完整性。