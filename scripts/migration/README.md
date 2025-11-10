# 统一采集器数据迁移脚本

本目录包含用于将现有的设备采集器和同步任务数据迁移到统一采集器管理模块的脚本。

## 文件说明

### 核心迁移脚本

- **`run_migration.py`** - 主迁移脚本，协调整个迁移流程
- **`migrate_device_collectors.py`** - 设备采集器数据迁移脚本
- **`migrate_api_collectors.py`** - API采集器（同步任务）数据迁移脚本
- **`rollback_migration.py`** - 迁移回滚脚本

### 支持文件

- **`README.md`** - 本说明文档

## 迁移概述

### 迁移内容

1. **设备采集器迁移**
   - 从 `collector_tasks` 表迁移到 `collectors` 表
   - 创建 `device_collectors` 子表数据
   - 迁移设备配置和数据点配置
   - 迁移执行历史和统计数据
   - 迁移执行日志数据

2. **API采集器迁移**
   - 从 `sync_jobs` 表迁移到 `collectors` 表
   - 创建 `api_collectors` 子表数据
   - 迁移API配置和认证信息
   - 迁移数据映射配置
   - 迁移执行历史和日志数据

### 迁移流程

1. **数据备份** - 备份现有数据到指定目录
2. **设备采集器迁移** - 迁移设备相关的采集器任务
3. **API采集器迁移** - 迁移同步任务到API采集器
4. **数据验证** - 验证迁移结果的完整性和正确性
5. **生成报告** - 生成详细的迁移报告

## 使用方法

### 前置条件

1. 确保数据库连接正常
2. 确保有足够的磁盘空间用于备份
3. 建议在非生产环境先进行测试
4. 停止相关的采集器和同步任务服务

### 1. 试运行（推荐）

在正式迁移前，建议先进行试运行以检查潜在问题：

```bash
# 进入项目根目录
cd /path/to/DeviceMonitorV1

# 执行试运行
python scripts/migration/run_migration.py --dry-run --verbose
```

试运行会：
- 分析现有数据结构
- 模拟迁移过程
- 检查潜在的数据问题
- 生成迁移预览报告
- **不会修改任何数据**

### 2. 正式迁移

确认试运行结果无误后，执行正式迁移：

```bash
# 执行完整迁移
python scripts/migration/run_migration.py --verbose

# 或者跳过备份（仅用于测试环境）
python scripts/migration/run_migration.py --skip-backup --verbose
```

### 3. 单独执行迁移组件

如果需要单独执行某个迁移组件：

```bash
# 仅迁移设备采集器
python scripts/migration/migrate_device_collectors.py --verbose

# 仅迁移API采集器
python scripts/migration/migrate_api_collectors.py --verbose

# 试运行单个组件
python scripts/migration/migrate_device_collectors.py --dry-run --verbose
```

### 4. 迁移回滚

如果迁移出现问题，可以使用回滚脚本恢复到迁移前状态：

```bash
# 回滚迁移（需要指定备份目录）
python scripts/migration/rollback_migration.py backup/migration_20241201_143022 --verbose

# 强制回滚（即使备份当前状态失败）
python scripts/migration/rollback_migration.py backup/migration_20241201_143022 --force --verbose
```

## 命令行参数

### run_migration.py

- `--dry-run` - 试运行模式，不实际执行迁移
- `--skip-backup` - 跳过数据备份（仅用于测试）
- `--verbose, -v` - 详细输出

### migrate_device_collectors.py / migrate_api_collectors.py

- `--dry-run` - 试运行模式，不实际执行迁移
- `--verbose, -v` - 详细输出

### rollback_migration.py

- `backup_dir` - 备份目录路径（必需参数）
- `--force` - 强制执行回滚，即使备份当前状态失败
- `--verbose, -v` - 详细输出

## 输出文件

### 备份文件

迁移过程会在 `backup/migration_YYYYMMDD_HHMMSS/` 目录下创建以下备份文件：

- `collector_tasks.json` - 原始采集器任务数据
- `sync_jobs.json` - 原始同步任务数据
- `sync_job_logs.json` - 原始同步任务日志数据
- `existing_*.json` - 现有的统一采集器数据（如果有）

### 日志文件

- `migration_main.log` - 主迁移流程日志
- `migration_device_collectors.log` - 设备采集器迁移日志
- `migration_api_collectors.log` - API采集器迁移日志
- `rollback_migration.log` - 回滚操作日志

### 报告文件

- `migration_report.json` - 详细的迁移报告
- `rollback_report.json` - 回滚操作报告

## 数据映射说明

### 设备采集器映射

| 原字段 (collector_tasks) | 新字段 (collectors) | 说明 |
|-------------------------|-------------------|------|
| task_name | name | 采集器名称 |
| task_description | description | 描述信息 |
| collector_type | collector_type | 采集器类型（映射到枚举） |
| status | status | 状态（映射到枚举） |
| is_active | is_active | 是否激活 |
| schedule_config | cron_expression | 调度配置（提取Cron表达式） |
| config | config | 基础配置 |
| - | device_id | 设备ID（从config提取） |
| - | device_type | 设备类型（从config提取） |
| - | connection_config | 连接配置（从config提取） |
| - | data_points | 数据点配置（从config提取） |

### API采集器映射

| 原字段 (sync_jobs) | 新字段 (collectors) | 说明 |
|-------------------|-------------------|------|
| job_name | name | 采集器名称 |
| description | description | 描述信息 |
| - | collector_type | 固定为 API |
| is_active | is_active | 是否激活 |
| cron_expression | cron_expression | Cron表达式 |
| api_url | api_config.url | API地址 |
| request_method | api_config.method | 请求方法 |
| request_headers | api_config.headers | 请求头 |
| request_params | api_config.params | 请求参数 |
| auth_config | api_config.auth | 认证配置 |
| target_table | data_mapping.target_table | 目标表 |
| data_mapping | data_mapping.mapping_rules | 数据映射规则 |

## 注意事项

### 迁移前

1. **备份数据库** - 强烈建议在迁移前完整备份数据库
2. **停止服务** - 停止所有相关的采集器和同步任务服务
3. **检查磁盘空间** - 确保有足够空间存储备份文件
4. **测试环境验证** - 在测试环境先执行完整的迁移流程

### 迁移中

1. **监控日志** - 密切关注迁移过程中的日志输出
2. **网络稳定** - 确保数据库连接稳定
3. **避免中断** - 不要在迁移过程中中断脚本执行

### 迁移后

1. **验证数据** - 仔细检查迁移报告和验证结果
2. **功能测试** - 测试新的统一采集器功能
3. **性能监控** - 监控系统性能是否正常
4. **保留备份** - 保留备份文件一段时间以备回滚

## 故障排除

### 常见问题

#### 1. 数据库连接失败

**错误信息：** `数据库连接初始化失败`

**解决方案：**
- 检查数据库服务是否运行
- 验证数据库连接配置
- 确认网络连接正常

#### 2. 权限不足

**错误信息：** `Permission denied` 或 `Access denied`

**解决方案：**
- 确保数据库用户有足够权限
- 检查文件系统写入权限
- 以适当的用户身份运行脚本

#### 3. 磁盘空间不足

**错误信息：** `No space left on device`

**解决方案：**
- 清理磁盘空间
- 选择其他备份目录
- 使用 `--skip-backup` 跳过备份（仅测试环境）

#### 4. 数据格式错误

**错误信息：** `数据格式不匹配` 或 `字段映射失败`

**解决方案：**
- 检查原始数据的完整性
- 查看详细错误日志
- 手动修复有问题的数据记录

#### 5. 迁移中断

**错误信息：** 脚本意外终止

**解决方案：**
- 检查系统资源（内存、CPU）
- 查看系统日志
- 使用回滚脚本恢复状态
- 重新执行迁移

### 调试技巧

1. **使用详细模式** - 添加 `--verbose` 参数获取更多信息
2. **查看日志文件** - 检查生成的日志文件获取详细错误信息
3. **试运行模式** - 使用 `--dry-run` 模式预先发现问题
4. **分步执行** - 单独执行各个迁移组件定位问题
5. **检查报告** - 仔细阅读迁移报告中的错误和警告信息

### 回滚策略

如果迁移失败或出现问题：

1. **立即停止** - 停止所有相关服务
2. **评估影响** - 检查哪些数据受到影响
3. **执行回滚** - 使用回滚脚本恢复到迁移前状态
4. **分析原因** - 查看日志和报告分析失败原因
5. **修复问题** - 修复发现的问题后重新迁移

## 性能优化

### 大数据量迁移

如果数据量很大，可以考虑以下优化：

1. **分批处理** - 修改脚本支持分批迁移
2. **并行处理** - 设备采集器和API采集器可以并行迁移
3. **索引优化** - 临时删除非必要索引加速插入
4. **事务控制** - 适当调整事务大小

### 监控指标

迁移过程中需要监控的指标：

- 数据库连接数
- 内存使用率
- 磁盘I/O
- 网络带宽
- 迁移进度

## 联系支持

如果遇到无法解决的问题，请：

1. 收集相关日志文件
2. 记录错误信息和重现步骤
3. 提供系统环境信息
4. 联系技术支持团队

---

**重要提醒：** 数据迁移是关键操作，请务必在生产环境执行前进行充分测试，并确保有完整的数据备份。