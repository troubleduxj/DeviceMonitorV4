# 数据库迁移和版本控制系统

## 📋 概述

本系统是为API权限重构项目开发的完整数据库迁移和版本控制解决方案，提供了：

- 🔄 **数据库迁移管理**: 自动化的数据库结构和数据迁移
- 📊 **版本控制**: 完整的数据库版本管理和追踪
- 👁️ **实时监控**: 迁移过程的实时监控和告警
- 📈 **性能分析**: 详细的迁移性能分析和优化建议
- 🔧 **自动化工具**: 一键式迁移执行和回滚

## 🏗️ 系统架构

```
数据库迁移系统
├── migration_system.py          # 核心迁移系统
├── migration_automation.py      # 自动化迁移管理
├── migration_monitor.py         # 监控和告警系统
├── run_migration_system.py      # 统一入口脚本
├── config.json.example          # 配置文件示例
└── README_MIGRATION_SYSTEM.md   # 使用文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install asyncpg aiohttp

# 设置数据库连接
export DATABASE_URL="postgresql://user:password@localhost:5432/database"

# 或者创建配置文件
cp database/config.json.example database/config.json
# 编辑 config.json 设置数据库连接信息
```

### 2. 初始化系统

```bash
# 初始化迁移系统
python database/run_migration_system.py --init

# 或使用交互式菜单
python database/run_migration_system.py --interactive
```

### 3. 执行迁移

```bash
# 预览迁移(不实际执行)
python database/run_migration_system.py --migrate --dry-run

# 执行迁移
python database/run_migration_system.py --migrate

# 查看迁移状态
python database/run_migration_system.py --status
```

## 📚 详细使用指南

### 命令行接口

```bash
# 基本操作
python database/run_migration_system.py --init          # 初始化系统
python database/run_migration_system.py --migrate       # 执行迁移
python database/run_migration_system.py --rollback      # 回滚迁移
python database/run_migration_system.py --status        # 查看状态

# 监控和分析
python database/run_migration_system.py --dashboard     # 显示仪表板
python database/run_migration_system.py --monitor       # 启动监控
python database/run_migration_system.py --analyze       # 性能分析
python database/run_migration_system.py --export report.json  # 导出报告

# 交互式菜单
python database/run_migration_system.py --interactive   # 交互式操作
```

### 交互式菜单

运行 `python database/run_migration_system.py --interactive` 进入交互式菜单：

```
╔══════════════════════════════════════════════════════════════╗
║                    数据库迁移和版本控制系统                    ║
║                   Database Migration & Version Control        ║
╠══════════════════════════════════════════════════════════════╣
║  功能: 数据库迁移、版本控制、监控告警、性能分析                ║
║  版本: 2.0.0                                                 ║
║  作者: API权限重构项目组                                      ║
╚══════════════════════════════════════════════════════════════╝

🎛️  数据库迁移系统 - 交互式菜单
============================================================
1. 初始化迁移系统
2. 查看迁移状态
3. 执行迁移 (预览)
4. 执行迁移 (实际)
5. 回滚迁移
6. 显示仪表板
7. 启动监控
8. 性能分析
9. 导出报告
0. 退出
============================================================
```

## 🔧 系统组件详解

### 1. 核心迁移系统 (migration_system.py)

负责数据库迁移的核心功能：

- **迁移记录表**: `t_sys_migration_logs` - 记录所有迁移执行历史
- **权限映射表**: `t_sys_permission_migrations` - 权限迁移映射关系
- **API分组表**: `t_sys_api_groups` - API分组管理
- **API接口表**: `t_sys_api_endpoints` - API接口定义
- **版本控制表**: `t_sys_database_versions` - 数据库版本管理

### 2. 自动化迁移 (migration_automation.py)

提供预定义的迁移任务：

1. **表结构标准化**: 将现有表名标准化为 `t_` 前缀格式
2. **API分组迁移**: 将现有API数据迁移到新的分组结构
3. **权限数据迁移**: 将v1权限数据迁移到v2格式
4. **性能优化索引**: 创建权限查询优化索引
5. **业务视图创建**: 创建常用的业务查询视图
6. **权限验证函数**: 创建v2权限验证相关函数

### 3. 监控告警系统 (migration_monitor.py)

实时监控迁移过程：

- **性能监控**: 执行时间、成功率、失败率
- **告警机制**: 邮件、Webhook、日志告警
- **仪表板**: 实时迁移状态展示
- **性能分析**: 详细的性能分析报告

### 4. 业务视图

系统创建的常用业务视图：

```sql
-- 迁移状态概览
v_migration_overview

-- 权限迁移统计
v_permission_migration_stats

-- API分组层次结构
v_api_group_hierarchy

-- API接口详情
v_api_endpoint_details

-- 迁移执行历史
v_migration_execution_history

-- 用户权限详情
v_user_permissions

-- 角色权限统计
v_role_permission_stats

-- API使用统计
v_api_usage_stats

-- 部门用户权限
v_department_user_permissions
```

### 5. 权限验证函数

系统提供的权限验证函数：

```sql
-- 检查用户权限
check_user_permission(user_id, api_path, http_method)

-- 获取用户所有权限
get_user_permissions(user_id)

-- 批量检查权限
batch_check_permissions(user_id, api_requests)

-- 权限继承检查
check_permission_inheritance(role_id, api_path, http_method)

-- 验证权限迁移结果
validate_permission_migration()
```

## 📊 监控和告警

### 告警类型

- **LONG_RUNNING_MIGRATION**: 迁移执行时间过长
- **HIGH_FAILURE_RATE**: 迁移失败率过高
- **STALE_PENDING_MIGRATION**: 待处理迁移时间过长
- **LOW_SUCCESS_RATE**: 迁移成功率过低
- **DATABASE_CONNECTION_ERROR**: 数据库连接异常

### 告警配置

在 `config.json` 中配置告警阈值和通知方式：

```json
{
  "monitoring": {
    "alert_thresholds": {
      "max_execution_time": 300000,  // 最大执行时间(毫秒)
      "max_failure_rate": 0.1,       // 最大失败率
      "max_pending_time": 3600,      // 最大待处理时间(秒)
      "min_success_rate": 0.9        // 最小成功率
    },
    "notifications": {
      "email": {
        "enabled": true,
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "from": "monitor@example.com",
        "to": ["admin@example.com"]
      },
      "webhook": {
        "enabled": true,
        "url": "https://hooks.slack.com/services/xxx/yyy/zzz"
      }
    }
  }
}
```

## 🔄 迁移流程

### 标准迁移流程

1. **初始化系统**
   ```bash
   python database/run_migration_system.py --init
   ```

2. **预览迁移**
   ```bash
   python database/run_migration_system.py --migrate --dry-run
   ```

3. **执行迁移**
   ```bash
   python database/run_migration_system.py --migrate
   ```

4. **验证结果**
   ```bash
   python database/run_migration_system.py --status
   python database/run_migration_system.py --dashboard
   ```

5. **启动监控**
   ```bash
   python database/run_migration_system.py --monitor
   ```

### 回滚流程

如果迁移出现问题，可以执行回滚：

```bash
# 回滚所有迁移
python database/run_migration_system.py --rollback

# 或者使用SQL直接回滚特定迁移
SELECT * FROM t_sys_migration_logs WHERE status = 'success';
-- 手动执行回滚SQL
```

## 📈 性能优化

### 索引优化

系统自动创建的性能优化索引：

```sql
-- 用户权限查询优化
idx_user_roles_composite
idx_role_permissions_composite
idx_api_endpoints_lookup

-- 覆盖索引
idx_user_permissions_covering
idx_role_api_permissions_covering

-- API查询优化
idx_api_endpoints_group_status
idx_api_groups_hierarchy

-- 权限迁移查询优化
idx_permission_migrations_confidence
idx_permission_migrations_group_type
```

### 查询优化

使用系统提供的优化查询：

```sql
-- 高效的用户权限查询
SELECT * FROM v_user_permissions WHERE user_id = ?;

-- 批量权限检查
SELECT batch_check_permissions(?, '[{"method":"GET","path":"/api/v2/users"}]');

-- 权限验证
SELECT check_user_permission(?, '/api/v2/users', 'GET');
```

## 🚨 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查数据库连接
   psql $DATABASE_URL -c "SELECT 1"
   
   # 检查配置文件
   cat database/config.json
   ```

2. **迁移执行失败**
   ```bash
   # 查看详细日志
   tail -f migration_system.log
   
   # 检查迁移状态
   python database/run_migration_system.py --status
   ```

3. **权限验证失败**
   ```sql
   -- 验证权限迁移结果
   SELECT * FROM validate_permission_migration();
   
   -- 检查权限映射
   SELECT * FROM t_sys_permission_migrations WHERE confidence_score < 0.7;
   ```

### 日志文件

- `migration_system.log` - 系统主日志
- `migration_automation.log` - 自动化迁移日志
- `migration_monitor.log` - 监控系统日志
- `migration_validation.log` - 验证日志

### 调试模式

启用详细日志：

```bash
export LOG_LEVEL=DEBUG
python database/run_migration_system.py --migrate
```

## 📋 最佳实践

### 迁移前准备

1. **完整备份数据库**
   ```bash
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **在测试环境验证**
   ```bash
   # 在测试环境执行完整流程
   python database/run_migration_system.py --migrate --dry-run
   python database/run_migration_system.py --migrate
   ```

3. **检查系统资源**
   - 确保足够的磁盘空间
   - 检查数据库连接数限制
   - 验证网络连接稳定性

### 迁移执行

1. **分阶段执行**
   - 先执行结构迁移
   - 再执行数据迁移
   - 最后执行索引和视图

2. **实时监控**
   ```bash
   # 在另一个终端启动监控
   python database/run_migration_system.py --monitor
   ```

3. **记录执行过程**
   - 保存所有日志文件
   - 记录执行时间和资源使用
   - 文档化任何异常情况

### 迁移后验证

1. **功能验证**
   ```bash
   python database/run_migration_system.py --analyze
   python database/run_migration_system.py --dashboard
   ```

2. **性能测试**
   - 执行权限查询性能测试
   - 验证API响应时间
   - 检查数据库查询计划

3. **数据一致性检查**
   ```sql
   SELECT * FROM validate_permission_migration();
   ```

## 🔗 相关文档

- [API v2规范文档](api-v2-specification.md)
- [权限迁移策略](permission_migration_strategy.py)
- [API备份迁移指南](api_backup_migration_guide.md)
- [数据库优化指南](database_optimization.sql)

## 📞 支持和联系

如有问题或需要支持：

1. 查看日志文件获取详细错误信息
2. 使用 `--analyze` 命令分析性能问题
3. 导出详细报告: `--export report.json`
4. 联系开发团队获取技术支持

---

**重要提醒**: 
- 在生产环境执行迁移前，务必在测试环境完整验证
- 始终保持数据库的完整备份
- 监控迁移过程，及时发现和处理问题
- 遵循最佳实践，确保迁移的安全性和可靠性