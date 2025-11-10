# 权限数据迁移系统

本系统用于将现有的权限数据迁移到新的API v2权限体系，包含完整的分析、验证、执行和回滚功能。

## 系统架构

```
权限迁移系统
├── permission_migration_strategy.py    # 权限数据分析和映射策略
├── permission_migration_validator.py   # 迁移验证器
├── permission_migration_executor.py    # 迁移执行器
├── run_permission_migration.py        # 主控脚本
├── migration_config.py                # 配置文件
└── README_MIGRATION.md                # 使用文档
```

## 功能特性

### 1. 权限数据分析
- 分析现有API和权限数据结构
- 自动生成权限映射规则
- 计算映射置信度
- 生成详细分析报告

### 2. 迁移验证
- 迁移前数据完整性检查
- 权限覆盖度验证
- 迁移后结果验证
- 自动生成验证报告

### 3. 迁移执行
- 分步骤执行迁移
- 完整的事务支持
- 详细的日志记录
- 自动备份和回滚

### 4. 配置管理
- 灵活的配置系统
- 支持环境变量
- API路径标准化规则
- 置信度阈值配置

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install asyncpg

# 设置数据库连接
export DATABASE_URL="postgresql://user:password@localhost:5432/database"

# 创建输出目录
mkdir -p database/migration_output
```

### 2. 配置检查

```bash
# 检查配置
python database/migration_config.py
```

### 3. 执行完整迁移

```bash
# 干运行模式（推荐先执行）
python database/run_permission_migration.py --dry-run

# 实际执行迁移
python database/run_permission_migration.py
```

### 4. 分阶段执行

```bash
# 只执行分析阶段
python database/run_permission_migration.py --phase analysis

# 只执行迁移前验证
python database/run_permission_migration.py --phase pre-validation

# 只执行迁移
python database/run_permission_migration.py --phase migration

# 只执行迁移后验证
python database/run_permission_migration.py --phase post-validation
```

## 详细使用指南

### 权限数据分析

```bash
# 运行权限数据分析
python database/permission_migration_strategy.py

# 输出文件:
# - permission_analysis_YYYYMMDD_HHMMSS.json    # 详细分析数据
# - permission_mappings_YYYYMMDD_HHMMSS.json    # 权限映射数据
# - permission_migration_YYYYMMDD_HHMMSS.sql    # 迁移SQL脚本
# - permission_rollback_YYYYMMDD_HHMMSS.sql     # 回滚SQL脚本
# - permission_migration_report_YYYYMMDD_HHMMSS.md  # 迁移报告
```

### 迁移验证

```bash
# 运行迁移验证
python database/permission_migration_validator.py

# 输出文件:
# - validation_results_YYYYMMDD_HHMMSS.json     # 验证结果数据
# - validation_report_YYYYMMDD_HHMMSS.md        # 验证报告
```

### 迁移执行

```bash
# 执行迁移（需要映射文件）
python database/permission_migration_executor.py \
  --mappings-file database/migration_output/permission_mappings_YYYYMMDD_HHMMSS.json

# 干运行模式
python database/permission_migration_executor.py \
  --mappings-file database/migration_output/permission_mappings_YYYYMMDD_HHMMSS.json \
  --dry-run

# 回滚迁移
python database/permission_migration_executor.py \
  --rollback \
  --migration-id YYYYMMDD_HHMMSS
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/database` | 数据库连接URL |
| `MIGRATION_BATCH_SIZE` | `1000` | 批处理大小 |
| `MIGRATION_TIMEOUT` | `300` | 迁移超时时间(秒) |
| `HIGH_CONFIDENCE_THRESHOLD` | `0.9` | 高置信度阈值 |
| `MEDIUM_CONFIDENCE_THRESHOLD` | `0.7` | 中等置信度阈值 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `MIGRATION_OUTPUT_DIR` | `database/migration_output` | 输出目录 |

### API路径映射规则

系统内置了完整的API路径映射规则，支持以下模块：

- **系统管理**: 用户、角色、菜单、部门管理
- **设备管理**: 设备信息、类型、监控、维护、工艺
- **AI监控**: 预测、模型、标注、健康评分、分析
- **统计分析**: 各类统计和报告
- **仪表板**: 概览和组件管理
- **报警管理**: 报警处理和统计

### 置信度说明

- **高置信度 (≥0.9)**: 直接映射，可自动迁移
- **中等置信度 (0.7-0.9)**: 推断映射，建议人工确认
- **低置信度 (<0.7)**: 需要人工检查和修正

## 迁移流程

### 1. 分析阶段
1. 连接数据库，读取现有权限数据
2. 分析API路径和权限关联
3. 应用标准化规则生成映射
4. 计算映射置信度
5. 生成分析报告和映射文件

### 2. 验证阶段
1. 检查迁移表是否存在
2. 验证数据完整性
3. 检查权限覆盖度
4. 验证API分组
5. 生成验证报告

### 3. 执行阶段
1. 创建数据备份表
2. 创建迁移相关表
3. 加载权限映射数据
4. 创建新的API结构表
5. 迁移API数据到新结构
6. 创建验证函数
7. 记录迁移日志

### 4. 验证阶段
1. 重新运行所有验证检查
2. 确认迁移结果正确性
3. 生成最终验证报告

## 数据库表结构

### 迁移相关表

```sql
-- 权限迁移映射表
t_sys_permission_migrations
├── old_permission      # 旧权限标识
├── new_permission      # 新权限标识
├── api_path           # API路径
├── http_method        # HTTP方法
├── api_group          # API分组
├── migration_type     # 迁移类型
├── confidence_score   # 置信度分数
└── migration_batch    # 迁移批次

-- 数据迁移记录表
t_sys_migration_logs
├── migration_name     # 迁移名称
├── migration_type     # 迁移类型
├── status            # 状态
├── execution_time_ms # 执行时间
├── error_message     # 错误信息
└── executed_at       # 执行时间
```

### 新权限结构表

```sql
-- API分组表
t_sys_api_groups
├── group_code        # 分组编码
├── group_name        # 分组名称
├── parent_id         # 父分组ID
└── description       # 描述

-- API接口表
t_sys_api_endpoints
├── api_code          # API编码
├── api_name          # API名称
├── api_path          # API路径
├── http_method       # HTTP方法
├── group_id          # 所属分组ID
├── version           # API版本
└── status            # 状态
```

## 验证和监控

### 内置验证函数

```sql
-- 验证权限迁移结果
SELECT * FROM validate_permission_migration();

-- 获取用户权限（v2版本）
SELECT * FROM get_user_permissions_v2(user_id);
```

### 监控查询

```sql
-- 检查置信度分布
SELECT 
    CASE 
        WHEN confidence_score >= 0.9 THEN 'High'
        WHEN confidence_score >= 0.7 THEN 'Medium'
        ELSE 'Low'
    END as confidence_level,
    COUNT(*) as count,
    ROUND(AVG(confidence_score), 2) as avg_score
FROM t_sys_permission_migrations
GROUP BY 1
ORDER BY avg_score DESC;

-- 检查API分组统计
SELECT api_group, COUNT(*) as count
FROM t_sys_permission_migrations
GROUP BY api_group
ORDER BY count DESC;

-- 检查迁移日志
SELECT migration_name, status, execution_time_ms, executed_at
FROM t_sys_migration_logs
ORDER BY executed_at DESC
LIMIT 10;
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `DATABASE_URL` 配置
   - 确认数据库服务运行正常
   - 验证用户权限

2. **权限映射置信度低**
   - 检查API路径是否符合预期格式
   - 更新 `migration_config.py` 中的映射规则
   - 人工确认低置信度映射

3. **迁移执行失败**
   - 查看详细错误日志
   - 检查数据库表结构
   - 确认数据完整性

4. **验证失败**
   - 检查迁移是否完整执行
   - 验证数据一致性
   - 重新运行验证程序

### 日志文件

- `migration_analysis.log` - 分析阶段日志
- `migration_validation.log` - 验证阶段日志
- `migration_execution.log` - 执行阶段日志
- `permission_migration_main.log` - 主控脚本日志

### 回滚操作

如果迁移出现问题，可以使用回滚功能：

```bash
# 回滚指定迁移
python database/permission_migration_executor.py \
  --rollback \
  --migration-id YYYYMMDD_HHMMSS

# 或者手动执行回滚SQL
psql -d database_name -f database/migration_output/permission_rollback_YYYYMMDD_HHMMSS.sql
```

## 最佳实践

### 迁移前准备
1. **备份数据库**: 在生产环境执行前务必完整备份
2. **测试环境验证**: 先在测试环境完整执行一遍
3. **停机窗口**: 选择合适的维护窗口执行迁移
4. **团队协调**: 确保相关团队了解迁移计划

### 迁移执行
1. **分阶段执行**: 先执行分析和验证，确认无误后再执行迁移
2. **干运行测试**: 使用 `--dry-run` 模式先测试
3. **监控日志**: 实时监控迁移日志，及时发现问题
4. **验证结果**: 迁移完成后立即验证结果

### 迁移后处理
1. **功能测试**: 全面测试权限相关功能
2. **性能监控**: 监控系统性能是否受影响
3. **清理工作**: 确认无问题后清理备份表
4. **文档更新**: 更新相关技术文档

## 支持和联系

如有问题或需要支持，请：

1. 查看日志文件获取详细错误信息
2. 检查本文档的故障排除部分
3. 联系开发团队获取技术支持

---

**注意**: 本迁移系统涉及核心权限数据，请务必在充分测试后再在生产环境使用。