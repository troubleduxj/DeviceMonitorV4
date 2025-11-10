# 完整数据库迁移指南

## 概述

这是一个完整的数据库迁移系统，用于API权限重构项目。该系统将现有的数据库结构迁移到标准化的新架构，并确保数据完整性和系统兼容性。

## 文件说明

### 核心文件
- `complete_migration_system.py` - 完整的迁移系统核心代码
- `run_complete_migration.py` - 简化的迁移执行脚本
- `verify_migration_result.py` - 迁移结果验证脚本

### 配置文件
- `COMPLETE_MIGRATION_GUIDE.md` - 本使用指南

## 快速开始

### 1. 环境准备

确保已安装必要的Python包：
```bash
pip install asyncpg
```

### 2. 数据库配置

设置数据库连接环境变量（可选，脚本中有默认值）：
```bash
export DATABASE_URL="postgresql://postgres:Hanatech%40123@127.0.0.1:5432/devicemonitor"
```

### 3. 执行迁移

运行完整迁移：
```bash
python run_complete_migration.py
```

### 4. 验证结果

验证迁移结果：
```bash
python verify_migration_result.py
```

## 迁移内容

### 表结构创建
- ✅ 系统配置表 (`t_sys_config`)
- ✅ 系统字典表 (`t_sys_dict_type`, `t_sys_dict_data`)
- ✅ 部门表 (`t_sys_dept`)
- ✅ 用户表 (`t_sys_user`)
- ✅ 角色表 (`t_sys_role`)
- ✅ 用户角色关联表 (`t_sys_user_role`)
- ✅ 菜单表 (`t_sys_menu`)
- ✅ 角色菜单关联表 (`t_sys_role_menu`)
- ✅ API分组表 (`t_sys_api_groups`)
- ✅ API端点表 (`t_sys_api_endpoints`)
- ✅ 权限表 (`t_sys_permission`)
- ✅ 角色权限关联表 (`t_sys_role_permission`)
- ✅ 用户权限表 (`t_sys_user_permission`)
- ✅ 迁移日志表 (`t_sys_migration_logs`)

### 数据迁移
- ✅ 部门数据迁移 (`dept` → `t_sys_dept`)
- ✅ 用户数据迁移 (`user` → `t_sys_user`)
- ✅ 角色数据迁移 (`role` → `t_sys_role`)
- ✅ 用户角色关联迁移 (`user_role` → `t_sys_user_role`)
- ✅ 菜单数据迁移 (`menu` → `t_sys_menu`)
- ✅ 角色菜单关联迁移 (`role_menu` → `t_sys_role_menu`)
- ✅ API数据迁移和标准化
- ✅ 权限数据创建和映射

### 索引和约束
- ✅ 性能优化索引
- ✅ 外键约束
- ✅ 数据完整性约束

## 迁移特性

### 🔄 数据兼容性
- 自动处理旧表结构差异
- 智能数据类型转换
- 保持现有数据完整性

### 📊 详细日志
- 完整的迁移过程记录
- 错误信息和执行时间
- 可追溯的迁移历史

### 🛡️ 安全保障
- 冲突处理机制 (ON CONFLICT DO UPDATE)
- 事务安全
- 回滚支持准备

### 📈 标准化改进
- 统一的表命名规范 (`t_` 前缀)
- RESTful API路径标准化
- 权限标识格式统一

## API路径标准化

### 旧格式 → 新格式
```
/api/users → /api/v2/system/users
/api/roles → /api/v2/system/roles
/api/devices → /api/v2/devices/assets
/api/ai/predict → /api/v2/ai/predictions
```

### 权限标识标准化
```
user:list → api:system.users.list
role:create → api:system.roles.create
device:update → api:devices.assets.update
```

## 验证检查项

### 表结构验证
- ✅ 所有必需表是否存在
- ✅ 表结构是否正确
- ✅ 约束是否建立

### 数据完整性验证
- ✅ 数据迁移数量统计
- ✅ 关联关系完整性
- ✅ 权限映射完整性

### 性能优化验证
- ✅ 重要索引是否存在
- ✅ 外键约束是否建立
- ✅ 查询性能是否优化

## 生成的报告

### 迁移报告
- `migration_report_[timestamp].json` - 详细的迁移执行报告
- 包含每个步骤的执行时间和结果
- 统计信息和错误详情

### 验证报告
- `migration_verification_report_[timestamp].json` - 迁移结果验证报告
- 包含所有验证检查的详细结果
- 整体成功率和问题汇总

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```
❌ 数据库连接失败: connection refused
```
**解决方案：**
- 检查数据库服务是否启动
- 验证连接参数是否正确
- 确认网络连接是否正常

#### 2. 权限不足
```
❌ permission denied for table
```
**解决方案：**
- 确保数据库用户有足够权限
- 检查表的所有者和权限设置

#### 3. 表已存在冲突
```
❌ relation already exists
```
**解决方案：**
- 脚本使用 `IF NOT EXISTS`，通常会自动处理
- 如需重新创建，可先删除相关表

#### 4. 数据类型不匹配
```
❌ column type mismatch
```
**解决方案：**
- 检查源表和目标表的字段定义
- 可能需要手动调整数据类型转换逻辑

### 日志文件
- `complete_migration.log` - 详细的执行日志
- 包含所有操作的时间戳和详细信息
- 错误堆栈跟踪信息

## 性能优化

### 批量操作
- 使用批量插入减少数据库往返
- 事务优化减少锁定时间

### 索引策略
- 在数据迁移完成后创建索引
- 针对查询模式优化索引设计

### 内存使用
- 流式处理大量数据
- 避免一次性加载所有数据到内存

## 安全考虑

### 数据备份
**强烈建议在迁移前备份数据库：**
```bash
pg_dump -h 127.0.0.1 -U postgres -d devicemonitor > backup_before_migration.sql
```

### 权限控制
- 迁移过程中保持现有用户权限
- 新权限系统向后兼容

### 审计日志
- 所有迁移操作都有详细记录
- 支持问题追踪和回滚准备

## 后续步骤

### 1. 应用程序更新
- 更新API调用路径
- 修改权限检查逻辑
- 测试新权限系统

### 2. 前端适配
- 更新权限配置工具
- 修改API调用接口
- 测试用户界面

### 3. 监控和维护
- 监控新系统性能
- 定期检查数据一致性
- 优化查询性能

## 联系支持

如果在迁移过程中遇到问题：

1. 查看 `complete_migration.log` 日志文件
2. 运行验证脚本检查具体问题
3. 检查生成的报告文件
4. 参考本指南的故障排除部分

---

**注意：** 这是一个重要的数据库结构变更，请在生产环境使用前充分测试！