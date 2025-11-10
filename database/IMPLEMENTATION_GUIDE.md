# 分阶段数据库迁移 - 实施指南

## 🎯 概述

本指南将帮助你实际执行分阶段数据库迁移，从环境准备到迁移完成的完整流程。

## 🚀 快速开始

### 方法1：使用主启动脚本（推荐）

```bash
# 1. 进入数据库目录
cd database

# 2. 设置数据库连接
export DATABASE_URL="postgresql://user:password@localhost:5432/database"

# 3. 运行主启动脚本
python run_phased_migration.py
```

### 方法2：使用Makefile

```bash
# 1. 进入数据库目录
cd database

# 2. 设置数据库连接
export DATABASE_URL="postgresql://user:password@localhost:5432/database"

# 3. 验证系统
make verify

# 4. 执行迁移
make migrate
```

### 方法3：分步执行

```bash
# 1. 系统验证
python verify_system.py

# 2. 执行迁移
python execute_migration.py
```

## 📋 详细实施步骤

### 步骤1：环境准备

#### 1.1 检查Python环境
```bash
python --version  # 需要Python 3.7+
```

#### 1.2 安装依赖
```bash
pip install asyncpg aiohttp
```

#### 1.3 设置数据库连接
```bash
# 替换为你的实际数据库连接信息
export DATABASE_URL="postgresql://username:password@host:port/database"
```

#### 1.4 验证数据库连接
```bash
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('$DATABASE_URL').fetchval('SELECT 1'))"
```

### 步骤2：系统验证

运行系统验证工具：
```bash
python verify_system.py
```

验证项目包括：
- ✅ Python依赖检查
- ✅ 必需文件检查
- ✅ 配置文件验证
- ✅ 数据库连接测试
- ✅ 系统组件测试

### 步骤3：配置检查

确认以下配置文件存在且正确：

#### 主配置文件 (`config.json`)
```json
{
  "database_url": "postgresql://...",
  "migrations": [
    {
      "migration_id": "api_permission_migration",
      "source_table": "api",
      "target_table": "t_sys_api_endpoints",
      "description": "API权限系统迁移"
    }
  ],
  "monitoring": {
    "enabled": true,
    "interval": 30
  }
}
```

#### 其他配置文件
- `migration_configs.json` - 迁移详细配置
- `read_switch_configs.json` - 读取切换配置
- `alerting_config.json` - 告警配置
- `validation_rules.json` - 验证规则

### 步骤4：执行迁移

#### 4.1 使用主启动脚本（推荐）
```bash
python run_phased_migration.py
```

选择菜单选项：
1. 🔍 系统验证
2. 🚀 执行迁移
3. 📚 查看文档
4. 🛠️ 故障排除
5. ❌ 退出

#### 4.2 直接执行迁移
```bash
python execute_migration.py
```

### 步骤5：监控迁移过程

迁移将按以下6个阶段执行：

#### 阶段1：准备阶段 (Preparation)
- 创建迁移配置
- 设置告警规则
- 初始数据一致性检查

#### 阶段2：双写阶段 (Dual Write)
- 启用双写机制
- 监控双写指标
- 验证双写成功率

#### 阶段3：验证阶段 (Validation)
- 详细数据一致性检查
- 生成差异报告
- 分析修复建议

#### 阶段4：读取切换阶段 (Read Switch)
- 配置切换策略
- 渐进式切换 (10% → 25% → 50% → 75% → 100%)
- 实时监控切换指标

#### 阶段5：清理阶段 (Cleanup)
- 禁用双写
- 最终一致性验证
- 生成完成报告

#### 阶段6：完成阶段 (Completed)
- 更新迁移状态
- 生成总结报告
- 系统清理

## 📊 监控和日志

### 日志文件
- `migration_execution.log` - 迁移执行日志
- `migration_system.log` - 系统运行日志
- `phased_migration_implementation.log` - 实施日志

### 生成的报告
- `validation_report_*.json` - 验证报告
- `final_validation_report_*.json` - 最终验证报告
- `migration_summary_*.json` - 迁移总结报告

### 实时监控
```bash
# 查看迁移状态
python phased_migration_strategy.py --db-url $DATABASE_URL --action status

# 查看切换分析
python configurable_read_switch.py --db-url $DATABASE_URL --action analytics --config-id api_migration_switch

# 查看告警状态
python migration_alerting_system.py --db-url $DATABASE_URL --action status
```

## 🛠️ 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查连接
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('$DATABASE_URL'))"

# 解决方案
- 检查数据库服务是否运行
- 验证连接字符串格式
- 确认用户名密码正确
- 检查网络连接
```

#### 2. 依赖安装失败
```bash
# 重新安装
pip install --upgrade asyncpg aiohttp

# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install asyncpg aiohttp
```

#### 3. 迁移阶段失败
```bash
# 查看详细日志
tail -f migration_execution.log

# 检查数据库状态
python phased_migration_strategy.py --db-url $DATABASE_URL --action status

# 考虑回滚
python phased_migration_strategy.py --db-url $DATABASE_URL --action rollback --migration-id api_permission_migration
```

#### 4. 一致性检查失败
```bash
# 重新验证
python data_consistency_validator.py --db-url $DATABASE_URL --source-table api --target-table t_sys_api_endpoints --level detailed

# 查看差异详情
cat validation_report_*.json
```

### 紧急回滚

如果迁移过程中出现严重问题：

```bash
# 立即回滚
python phased_migration_strategy.py --db-url $DATABASE_URL --action rollback --migration-id api_permission_migration

# 或使用实施器回滚
python -c "
import asyncio
from implement_phased_migration import PhasedMigrationImplementor
async def rollback():
    impl = PhasedMigrationImplementor('config.json')
    await impl.initialize_systems()
    await impl.rollback_migration('api_permission_migration')
    await impl.cleanup_systems()
asyncio.run(rollback())
"
```

## 📈 性能优化

### 数据库优化
```sql
-- 创建必要索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_id ON api(id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_endpoints_id ON t_sys_api_endpoints(id);

-- 更新统计信息
ANALYZE api;
ANALYZE t_sys_api_endpoints;
```

### 系统优化
- 调整批处理大小
- 优化连接池配置
- 监控内存使用
- 调整切换间隔

## ✅ 迁移后验证

### 1. 功能验证
```bash
# 验证API功能
curl -X GET "http://your-api/api/v2/users" -H "Authorization: Bearer token"

# 验证权限系统
# 测试各种权限场景
```

### 2. 性能验证
```bash
# 监控响应时间
# 检查数据库性能
# 验证缓存效果
```

### 3. 数据完整性验证
```bash
# 最终一致性检查
python data_consistency_validator.py --db-url $DATABASE_URL --source-table api --target-table t_sys_api_endpoints --level comprehensive --export final_check.json
```

## 📚 相关文档

- **[快速开始指南](QUICK_START_GUIDE.md)** - 新用户入门
- **[详细操作手册](PHASED_MIGRATION_MANUAL.md)** - 完整操作流程
- **[系统概述](README_PHASED_MIGRATION.md)** - 架构和特性

## 🎉 完成检查清单

迁移完成后，请确认以下项目：

- [ ] 所有6个迁移阶段都成功完成
- [ ] 生成了完整的验证报告
- [ ] 应用程序功能正常
- [ ] 性能指标符合预期
- [ ] 监控系统正常运行
- [ ] 备份和回滚方案已准备
- [ ] 团队已了解新系统
- [ ] 文档已更新

## 📞 支持

如果遇到问题：

1. 查看日志文件
2. 运行系统验证
3. 查看故障排除指南
4. 检查配置文件
5. 考虑回滚操作

---

**祝你迁移顺利！** 🚀

记住：
- 🔍 始终先验证系统
- 📊 密切监控过程
- 🚨 及时响应告警
- 🔄 必要时快速回滚