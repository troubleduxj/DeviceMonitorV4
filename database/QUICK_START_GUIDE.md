# 分阶段数据库迁移 - 快速开始指南

## 🚀 快速开始

### 1. 环境准备

#### 1.1 安装依赖
```bash
pip install asyncpg aiohttp
```

#### 1.2 设置数据库连接
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/database"
```

#### 1.3 验证系统
```bash
cd database
python test_migration_system.py
```

### 2. 配置迁移

#### 2.1 使用交互式配置（推荐）
```bash
python start_migration.py
```

#### 2.2 手动配置
复制并修改配置文件：
```bash
cp config.json.example config.json
# 编辑 config.json 文件
```

### 3. 执行迁移

#### 3.1 完整迁移流程
```bash
python start_migration.py
# 选择 "1. 执行所有迁移"
```

#### 3.2 单个迁移
```bash
python start_migration.py
# 选择 "2. 执行指定迁移"
# 输入迁移ID，如：api_permission_migration
```

#### 3.3 试运行
```bash
python start_migration.py
# 选择 "3. 试运行模式"
```

## 📋 迁移阶段说明

### 阶段1：准备阶段 (Preparation)
- ✅ 创建迁移配置
- ✅ 设置告警规则
- ✅ 初始数据一致性检查

### 阶段2：双写阶段 (Dual Write)
- ✅ 启用双写机制
- ✅ 监控双写指标
- ✅ 验证双写成功率

### 阶段3：验证阶段 (Validation)
- ✅ 详细数据一致性检查
- ✅ 生成差异报告
- ✅ 分析修复建议

### 阶段4：读取切换阶段 (Read Switch)
- ✅ 配置切换策略
- ✅ 渐进式切换 (10% → 25% → 50% → 75% → 100%)
- ✅ 实时监控切换指标

### 阶段5：清理阶段 (Cleanup)
- ✅ 禁用双写
- ✅ 最终一致性验证
- ✅ 生成完成报告

### 阶段6：完成阶段 (Completed)
- ✅ 更新迁移状态
- ✅ 生成总结报告
- ✅ 系统清理

## 🔧 高级用法

### 命令行工具

#### 分阶段迁移策略
```bash
# 查看迁移状态
python phased_migration_strategy.py --db-url $DATABASE_URL --action status

# 启用双写
python phased_migration_strategy.py --db-url $DATABASE_URL --action enable-dual-write --migration-id api_permission_migration

# 回滚迁移
python phased_migration_strategy.py --db-url $DATABASE_URL --action rollback --migration-id api_permission_migration
```

#### 数据一致性验证
```bash
# 基础验证
python data_consistency_validator.py --db-url $DATABASE_URL --source-table api --target-table t_sys_api_endpoints --level basic

# 详细验证
python data_consistency_validator.py --db-url $DATABASE_URL --source-table api --target-table t_sys_api_endpoints --level detailed --sample-size 10000

# 导出报告
python data_consistency_validator.py --db-url $DATABASE_URL --source-table api --target-table t_sys_api_endpoints --level comprehensive --export validation_report.json
```

#### 配置化读取切换
```bash
# 激活切换
python configurable_read_switch.py --db-url $DATABASE_URL --action activate --config-id api_gradual_switch

# 更新切换百分比
python configurable_read_switch.py --db-url $DATABASE_URL --action update-percentage --config-id api_gradual_switch --percentage 50.0

# 获取切换分析
python configurable_read_switch.py --db-url $DATABASE_URL --action analytics --config-id api_gradual_switch

# 回滚切换
python configurable_read_switch.py --db-url $DATABASE_URL --action rollback --config-id api_gradual_switch
```

#### 迁移告警系统
```bash
# 启动监控
python migration_alerting_system.py --db-url $DATABASE_URL --action monitor

# 查看告警状态
python migration_alerting_system.py --db-url $DATABASE_URL --action status

# 确认告警
python migration_alerting_system.py --db-url $DATABASE_URL --action acknowledge --alert-id alert_123 --user admin

# 解决告警
python migration_alerting_system.py --db-url $DATABASE_URL --action resolve --alert-id alert_123 --user admin

# 获取统计
python migration_alerting_system.py --db-url $DATABASE_URL --action statistics --days 7

# 导出报告
python migration_alerting_system.py --db-url $DATABASE_URL --action export --output alert_report.json
```

## 📊 监控和告警

### 关键指标
- **迁移成功率**: 成功迁移的记录比例
- **数据一致性分数**: 源表和目标表的一致性程度
- **双写成功率**: 双写操作的成功比例
- **切换错误率**: 读取切换的错误比例
- **平均响应时间**: 操作的平均响应时间

### 告警类型
- **迁移失败告警**: 迁移过程中的失败
- **数据一致性问题**: 数据不一致检测
- **双写错误**: 双写机制异常
- **切换失败**: 读取切换问题
- **性能下降**: 响应时间增加

### 通知渠道
- **邮件通知**: SMTP邮件发送
- **Webhook**: HTTP回调通知
- **Slack**: Slack消息通知
- **钉钉**: 钉钉机器人通知

## 🛠️ 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查数据库连接
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('$DATABASE_URL').fetchval('SELECT 1'))"
```

#### 2. 双写失败
```sql
-- 查看双写日志
SELECT * FROM t_sys_dual_write_logs 
WHERE migration_id = 'api_permission_migration' 
  AND target_success = FALSE 
ORDER BY created_at DESC LIMIT 10;
```

#### 3. 一致性问题
```bash
# 重新验证数据一致性
python data_consistency_validator.py --db-url $DATABASE_URL --source-table api --target-table t_sys_api_endpoints --level comprehensive
```

#### 4. 切换性能问题
```bash
# 查看切换分析
python configurable_read_switch.py --db-url $DATABASE_URL --action analytics --config-id api_gradual_switch
```

### 紧急回滚

#### 自动回滚
系统会在以下情况自动回滚：
- 错误率超过阈值
- 一致性分数低于阈值
- 关键告警触发

#### 手动回滚
```bash
# 立即回滚所有操作
python phased_migration_strategy.py --db-url $DATABASE_URL --action rollback --migration-id api_permission_migration
```

## 📁 文件结构

```
database/
├── phased_migration_strategy.py      # 分阶段迁移策略
├── data_consistency_validator.py     # 数据一致性验证器
├── configurable_read_switch.py       # 配置化读取切换器
├── migration_alerting_system.py      # 迁移告警系统
├── implement_phased_migration.py     # 迁移实施器
├── start_migration.py               # 启动脚本
├── test_migration_system.py         # 测试脚本
├── config.json.example              # 配置文件示例
├── migration_configs.json           # 迁移配置
├── read_switch_configs.json         # 切换配置
├── alerting_config.json             # 告警配置
├── validation_rules.json            # 验证规则
├── PHASED_MIGRATION_MANUAL.md       # 详细操作手册
└── QUICK_START_GUIDE.md             # 快速开始指南
```

## 🎯 最佳实践

### 1. 迁移前准备
- ✅ 备份数据
- ✅ 测试环境验证
- ✅ 性能基准测试
- ✅ 监控配置

### 2. 迁移过程中
- ✅ 渐进式切换
- ✅ 持续监控
- ✅ 定期验证
- ✅ 记录操作

### 3. 迁移后维护
- ✅ 性能监控
- ✅ 数据质量检查
- ✅ 清理工作
- ✅ 经验总结

## 📞 支持

如果遇到问题，请：

1. 查看日志文件：
   - `migration_startup.log`
   - `phased_migration_implementation.log`
   - `migration_system.log`

2. 运行系统测试：
   ```bash
   python test_migration_system.py
   ```

3. 查看详细手册：
   ```bash
   cat PHASED_MIGRATION_MANUAL.md
   ```

## 🎉 完成

恭喜！你已经成功设置了分阶段数据库迁移系统。现在可以安全、可靠地执行数据库迁移了。

记住：
- 🔍 始终先在测试环境验证
- 📊 密切监控迁移过程
- 🚨 及时响应告警
- 🔄 必要时快速回滚

祝你迁移顺利！🚀