# 12 数据库初始化WEB工具设计

## 1. 项目背景与需求分析

### 1.1 问题描述
当前DeviceMonitorV2系统在数据库未创建的情况下无法正常启动，存在以下问题：
- 系统启动时强制要求数据库已存在并可用
- 缺乏独立的数据库初始化工具
- 新环境部署时必须先手动创建数据库
- 数据库连接失败导致整个应用无法启动

### 1.2 解决目标
创建一个独立的Web工具，提供可视化界面完成以下功能：
- 数据库连接测试与配置
- 数据库初始化与表结构创建
- 基础数据导入（管理员账户、菜单权限等）
- 数据库状态检查与诊断
- 支持PostgreSQL和TDengine双数据库

## 2. 系统架构设计

### 2.1 整体架构
```
┌─────────────────────────────────────────┐
│           数据库初始化WEB工具             │
├─────────────────┬───────────────────────┤
│   前端界面       │      后端API          │
│  (Vue.js 3)    │   (FastAPI)          │
├─────────────────┼───────────────────────┤
│ • 连接配置      │ • 数据库连接测试      │
│ • 初始化向导    │ • 表结构创建          │
│ • 状态监控      │ • 基础数据导入        │
│ • 日志查看      │ • 进度跟踪            │
└─────────────────┴───────────────────────┘
         │                      │
         └──────────────────────┘
                  ↓
         ┌───────────────────────┐
         │   PostgreSQL &        │
         │   TDengine 数据库     │
         └───────────────────────┘
```

### 2.2 技术栈选择
- **后端**: FastAPI + asyncpg + SQLAlchemy + Tortoise-ORM
- **前端**: Vue.js 3 + Naive UI + Axios
- **数据库**: PostgreSQL 13+ (主库) + TDengine (时序数据)
- **运行环境**: Python 3.8+ + Node.js 16+
- **部署**: 独立进程，端口8001

### 2.3 目录结构
```
tools/db-init-web/
├── app.py                 # FastAPI主应用
├── config.py             # 配置文件
├── requirements.txt      # Python依赖
├── static/               # 静态文件
│   ├── css/
│   ├── js/
│   └── images/
├── templates/            # HTML模板
│   ├── index.html
│   ├── setup.html
│   └── status.html
├── api/                  # API路由
│   ├── __init__.py
│   ├── database.py
│   └── init.py
├── services/             # 业务逻辑
│   ├── __init__.py
│   ├── db_service.py
│   └── init_service.py
├── models/               # 数据模型
│   ├── __init__.py
│   └── schemas.py
└── utils/                # 工具函数
    ├── __init__.py
    ├── logger.py
    └── validators.py
```

## 3. 功能模块设计

### 3.1 数据库连接测试模块
**功能描述**: 测试数据库连接是否可用
**API接口**:
- `POST /api/test-connection` - 测试数据库连接
- `GET /api/check-status` - 检查数据库状态

**输入参数**:
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "devicemonitor",
  "username": "postgres",
  "password": "password",
  "tdengine_host": "localhost",
  "tdengine_port": 6041
}
```

**返回结果**:
```json
{
  "success": true,
  "message": "连接成功",
  "details": {
    "postgresql": {"connected": true, "version": "13.5"},
    "tdengine": {"connected": true, "version": "3.0.1.0"}
  }
}
```

### 3.2 数据库初始化模块
**功能描述**: 创建数据库表结构和基础数据
**API接口**:
- `POST /api/init-database` - 初始化数据库
- `GET /api/init-progress` - 获取初始化进度
- `POST /api/cancel-init` - 取消初始化

**初始化步骤**:
1. 创建PostgreSQL表结构
2. 创建TDengine超级表
3. 导入基础数据（菜单、权限、管理员账户）
4. 创建索引和约束
5. 验证数据完整性

**进度返回**:
```json
{
  "step": 3,
  "total_steps": 5,
  "progress": 60,
  "current_task": "创建用户权限表",
  "status": "running"
}
```

### 3.3 配置管理模块
**功能描述**: 管理数据库连接配置
**API接口**:
- `GET /api/config` - 获取当前配置
- `POST /api/config` - 保存配置
- `PUT /api/config` - 更新配置

**配置文件格式**:
```json
{
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "database": "devicemonitor",
    "username": "postgres",
    "password": "encrypted_password"
  },
  "tdengine": {
    "host": "localhost",
    "port": 6041,
    "database": "devicemonitor"
  },
  "security": {
    "encrypt_passwords": true,
    "config_file": ".env.dbinit"
  }
}
```

### 3.4 日志与监控模块
**功能描述**: 记录初始化过程和错误信息
**API接口**:
- `GET /api/logs` - 获取日志列表
- `GET /api/logs/{log_id}` - 获取详细日志
- `DELETE /api/logs/{log_id}` - 删除日志

**日志格式**:
```json
{
  "timestamp": "2024-01-15 14:30:25",
  "level": "INFO",
  "module": "db_service",
  "message": "开始创建用户表",
  "details": {"sql": "CREATE TABLE users...", "duration": 125}
}
```

## 4. 用户界面设计

### 4.1 主界面设计
**页面布局**:
- 顶部导航栏：工具名称、版本信息
- 左侧菜单：连接测试、初始化、配置、日志
- 主内容区：根据菜单切换不同功能页面
- 状态栏：显示当前连接状态和操作进度

### 4.2 连接测试页面
**功能元素**:
- PostgreSQL连接配置表单 (Naive UI表单组件)
- TDengine连接配置表单 (Naive UI表单组件)
- 测试连接按钮 (Naive UI按钮组件)
- 连接结果显示区域 (Naive UI卡片和提示组件)
- 保存配置按钮 (Naive UI按钮组件)

**交互流程**:
1. 用户填写数据库连接信息
2. 点击"测试连接"按钮
3. 显示连接测试结果
4. 可选择保存配置

### 4.3 初始化向导页面
**功能元素**:
- 初始化步骤导航（5步骤）
- 当前步骤详细说明
- 进度条显示
- 实时日志输出区域
- 开始/暂停/取消按钮

**初始化步骤**:
1. **环境检查**: 检查Python版本、依赖库
2. **连接验证**: 验证数据库连接
3. **表结构创建**: 创建所有必需表
4. **基础数据导入**: 导入管理员、菜单、权限
5. **验证与完成**: 验证数据完整性

### 4.4 配置管理页面
**功能元素**:
- 配置表单（可编辑）
- 配置验证
- 保存/重置按钮
- 导入/导出配置

### 4.5 日志查看页面
**功能元素**:
- 日志列表（分页）
- 日志详情弹窗
- 日志搜索/过滤
- 日志导出功能

## 5. 数据库初始化流程

### 5.1 PostgreSQL初始化
**表结构创建顺序**:
1. 用户相关表
   - users (用户基础信息)
   - user_profiles (用户详细信息)
   - user_roles (用户角色关联)
2. 权限相关表
   - roles (角色定义)
   - permissions (权限定义)
   - role_permissions (角色权限关联)
3. 系统配置表
   - system_settings (系统配置)
   - device_types (设备类型)
   - alert_rules (告警规则)
4. 业务数据表
   - devices (设备信息)
   - device_data (设备数据)
   - alerts (告警记录)

**索引创建策略**:
- 主键索引：自动创建
- 外键索引：手动创建
- 查询优化索引：基于常用查询
- 复合索引：针对多条件查询

### 5.2 TDengine初始化
**超级表设计**:
```sql
-- 设备数据超级表
CREATE STABLE device_data (
    ts TIMESTAMP,
    value DOUBLE,
    status INT,
    quality INT
) TAGS (
    device_id VARCHAR(64),
    metric_type VARCHAR(32),
    unit VARCHAR(16)
);

-- 告警数据超级表
CREATE STABLE alerts (
    ts TIMESTAMP,
    alert_level INT,
    alert_type VARCHAR(32),
    message VARCHAR(512),
    resolved BOOLEAN
) TAGS (
    device_id VARCHAR(64),
    rule_id VARCHAR(64)
);
```

### 5.3 基础数据导入
**管理员账户**:
- 用户名：admin
- 密码：admin123（首次登录强制修改）
- 角色：超级管理员
- 权限：所有权限

**系统菜单**:
- 系统管理
  - 用户管理
  - 角色管理
  - 权限配置
  - 系统设置
- 设备管理
  - 设备列表
  - 设备类型
  - 数据采集
- 告警管理
  - 告警规则
  - 告警记录
  - 告警统计

## 6. 安全设计

### 6.1 认证与授权
**认证机制**:
- 首次使用无需认证
- 初始化完成后生成访问令牌
- 令牌有效期：24小时
- 支持令牌刷新

**权限控制**:
- 初始化工具独立运行，不影响主系统
- 仅允许本地访问（127.0.0.1）
- 配置文件权限：仅所有者读写

### 6.2 数据安全
**密码安全**:
- 密码加密存储（AES-256）
- 内存中不存储明文密码
- 连接后立即清除敏感信息

**日志安全**:
- 日志中不记录密码
- 敏感信息脱敏处理
- 日志文件权限控制

## 7. 性能优化

### 7.1 数据库优化
**连接池管理**:
- PostgreSQL：连接池大小10-50
- TDengine：连接池大小5-20
- 连接超时：30秒
- 连接重试：3次

**批量操作**:
- 批量插入：每批1000条
- 事务管理：每批一个事务
- 错误处理：批量回滚

### 7.2 前端优化
**加载优化**:
- 静态资源压缩
- CDN加速（可选）
- 懒加载实现

**响应优化**:
- API响应缓存
- 分页加载
- 异步操作

## 8. 错误处理与恢复

### 8.1 错误分类
**连接错误**:
- 网络不可达
- 认证失败
- 数据库不存在
- 权限不足

**初始化错误**:
- SQL语法错误
- 表已存在
- 数据冲突
- 存储空间不足

**系统错误**:
- 内存不足
- 文件权限问题
- 配置错误

### 8.2 恢复策略
**自动恢复**:
- 网络重连：3次重试
- 事务回滚：失败后自动回滚
- 断点续传：支持从失败步骤继续

**手动恢复**:
- 错误日志详细记录
- 一键回滚功能
- 手动SQL执行界面

## 9. 部署方案

### 9.1 独立部署
**启动命令**:
```bash
# 安装依赖
pip install -r requirements.txt

# 启动工具
python app.py

# 或指定端口
python app.py --port 8001
```

**访问地址**:
```
http://localhost:8001
```

### 9.2 集成部署
**作为子模块**:
```bash
# 在主项目目录下
git submodule add tools/db-init-web

# 启动时同时启动
python run.py --with-db-init
```

### 9.3 容器化部署
**Dockerfile**:
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "app.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  db-init:
    build: ./tools/db-init-web
    ports:
      - "8001:8001"
    environment:
      - ENV=production
```

## 10. 测试策略

### 10.1 单元测试
**测试范围**:
- 数据库连接测试
- 配置验证测试
- 错误处理测试

**测试框架**:
- pytest + pytest-asyncio
- 测试覆盖率 > 80%

### 10.2 集成测试
**测试场景**:
- 全新数据库初始化
- 已存在数据库的升级
- 网络中断恢复
- 并发初始化测试

### 10.3 用户验收测试
**测试用例**:
1. 管理员首次使用流程
2. 错误配置处理
3. 大容量数据初始化
4. 多浏览器兼容性

## 11. 监控与维护

### 11.1 运行监控
**监控指标**:
- 初始化成功率
- 平均初始化时间
- 错误率统计
- 用户操作日志

**监控工具**:
- 内置状态页面
- 日志分析工具
- 性能监控面板

### 11.2 维护计划
**定期检查**:
- 依赖库安全更新
- 数据库版本兼容性
- 配置文件备份

**升级策略**:
- 向后兼容
- 平滑升级
- 回滚机制

## 12. 开发计划

### 12.1 阶段划分
**第一阶段**（1-2周）：
- 基础框架搭建
- 数据库连接测试
- 基本界面实现

**第二阶段**（2-3周）：
- 初始化流程实现
- 进度跟踪功能
- 错误处理完善

**第三阶段**（1周）：
- 测试与优化
- 文档完善
- 部署脚本

### 12.2 里程碑
- **M1**: 基础功能完成（连接测试+简单初始化）
- **M2**: 完整初始化流程
- **M3**: 用户界面优化
- **M4**: 测试通过，文档完成

## 13. 风险评估与应对

### 13.1 技术风险
**风险**: 数据库版本不兼容
**应对**: 版本检测 + 兼容性提示

**风险**: 权限不足导致初始化失败
**应对**: 权限预检查 + 详细错误提示

### 13.2 安全风险
**风险**: 配置文件泄露
**应对**: 加密存储 + 访问控制

**风险**: 恶意SQL注入
**应对**: 参数化查询 + 输入验证

### 13.3 运维风险
**风险**: 初始化过程中系统崩溃
**应对**: 事务机制 + 断点续传

**风险**: 并发初始化冲突
**应对**: 分布式锁 + 状态检查

## 14. 附录

### 14.1 配置文件示例
**config.json**:
```json
{
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "database": "devicemonitor",
    "username": "postgres",
    "password": "your_password"
  },
  "tdengine": {
    "host": "localhost",
    "port": 6041,
    "database": "devicemonitor"
  },
  "init": {
    "create_admin": true,
    "admin_username": "admin",
    "admin_password": "admin123"
  }
}
```

### 14.2 环境要求
**系统要求**:
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- TDengine 3.0+

**依赖库**:
```txt
fastapi==0.104.1
uvicorn==0.24.0
asyncpg==0.29.0
sqlalchemy==2.0.23
tortoise-orm==0.20.0
pydantic==2.5.0
cryptography==41.0.7
python-multipart==0.0.6
```

### 14.3 联系方式
**项目负责人**: [待填写]
**技术支持**: [待填写]
**文档维护**: [待填写]