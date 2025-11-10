## 2025-06-27
set http_proxy=http://127.0.0.1:7890
set https_proxy=http://127.0.0.1:7890


页面上数据实现，其中可以通过连接tdengine的超级表{suptable}，使用select last_row(*) from hlzg_db.{suptable},该{suptable}的表名存储在了postgreSQL数据库字典数据表的数据标签为”平均在线率（日）“对应的数据值列里。该{suptable}表可获取的字段分别为：
焊接时间（welding_minutes）,
待机时间（standby_minutes）,
报警时间（alarm_minutes）,
关机时间（shutdown_minutes）,
在线时间（online_minutes），
总时间（total_minutes）,
在线率（online_rate）


我再说一下逻辑，你应该先查询“字典类型”表里“字典类型名称”为“焊机统计指标对照”对照的ID为2，然后这个2是和“字典数据”表里“dict_type_id”相同的，再“字典数据”表里找到“dict_type_id”=2,"data_label"=“实时状态统计”的那条数据，读取“data_value”值，该值即为tdengine中对应的超级表的表名，利用select last_row(*) from hlzg_db.超级表明，即可查询到该条数据，实现“焊机监测看板”上的实时数据获取，进行页面数据绑定

我后面有些页面要通过接口API调用tdengine时序库的相关数据，所以现在我要开发一些新的功能，具体如下：
1. 开发tdengine连接器，实现REST API的方式连接，方便后续接口调用；
2. 开发tdengine时序库的接口，实现数据的存储和查询；
3. 开发页面的接口，实现页面的调用。
帮我把如上内容更新到memory-bank，作为近期开发任务，并添加到项目开发计划中。
通过mcp里的sequential-thinking插件来辅助分解任务，并用mcp里的mcp-feedback-enhance工具及时与我沟通。


运行以下命令生成一个安全的SECRET_KEY
openssl rand -hex 32

API需要按照如下我确认的信息进行修正，已创建的需要逐个清理删除
1.数据源整合策略：
不需要整合，设备实时数据接口完全从TDengine获取数据，按频率进行获取查询； 
2.实时数据API具体需求：查询该超级表test_db.welding_real_data下所有设备的字段参数信息，即每个子表的最新一条数据，查询频率为5秒，需要分页处理；
3.welding_real_data超级表的具体字段结构如下：
**数据字段（Columns）：**

| 字段名            | 数据类型      | 描述         | 示例                  |
| -------------- | --------- | ---------- | ------------------- |
| ts             | TIMESTAMP | 时间戳        | 2023-08-23 10:00:00 |
| team_name      | NCHAR(50) | D02 班组名称   | 班组一                 |
| device_status  | NCHAR(50) | D03 设备状态   | 焊接/待机               |
| lock_status    | BOOL      | D04 锁状态    | true / false        |
| preset_current | FLOAT     | D05 预设电流   | 10.5                |
| preset_voltage | FLOAT     | D06 预设电压   | 220.0               |
| weld_current   | FLOAT     | D07 焊接电流   | 11.0                |
| weld_voltage   | FLOAT     | D08 焊接电压   | 225.0               |
| material       | NCHAR(50) | D09 预设功率   | Q235                |
| wire_diameter  | FLOAT     | D10 丝径（mm） | 1.2                 |
| gas_type       | NCHAR(50) | D11 气体类型   | CO2                 |
| weld_method    | NCHAR(50) | D12 焊接方式   | MIG                 |
| weld_control   | NCHAR(50) | D13 焊接控制   | 脉冲                  |
| staff_id       | NCHAR(50) | D14 焊工编号   | W123456             |
| workpiece_id   | NCHAR(50) | D15 工件编号   | WP123456            |
| ip_quality     | INT       | 数据质量       | 100                 |

🏷️**标签字段（Tags）:**

| 字段名         | 数据类型      | 描述         | 示例              |
| ----------- | --------- | ---------- | --------------- |
| device_code | NCHAR(50) | D01 设备生产编码 | 14412T0006      |
| name        | NCHAR(50) | 设备名称       | t_{device_code} |

所有子表命名规则为:t+{device_code}

4.API设计偏好:
接口路径建议：/api/v1/device/realtime-data
需要WebSocket实时推送
响应格式沿用现有的DeviceRealTimeDataResponse

如上任务如果没有得到我的确认，自动断开会话，不要继续任务,保持继续沟通

我想设计一个新的接口，/api/v1/device/realtime-data，用来查询实时数据，具体如下：
1. 根据不同的设备类型来通过tdengine查询不同的超级表下的所有子表，例如：焊机（weld）,则采集test_db.welding_real_data下所有子表的最新数据。 每个子表代表一个设备，每个设备有多个字段参数，例如：t_14412T0006这个子表有15个字段参数；
2. 为后期其它类型的设备提供扩展，后期可能有切割机等其它类型的设备，其超级表也会不同，如果采集切割机的所有设备的实时数据，则会采集该超级表下的所有子表的最新数据。
3. 我需要在前端页面显示所有设备的实时数据，由于不同种类的设备，其超级表字段设计不同，包含的参数字段也不同。
4. 我设计了websocket为ws://localhost:8000/api/v1/device/realtime-data/ws，前端页面通过该websocket来实时获取所有设备的实时数据。
5. 我需要在前端页面设计一个下拉框，用来选择不同的设备类型，例如：焊机、切割机等，下拉框的选项从数据库中查询。

我关系数据库用的为postgreSQL数据库，我该怎么设计数据库表结构呢？以及怎么优化接口为前端服务。


我已经设计了设备基础信息表（t_device_info），具体创建语句如下：
```sql
CREATE TABLE IF NOT EXISTS t_device_info (
    id                  SERIAL PRIMARY KEY,              -- 内部唯一 ID，自增主键
    device_code         VARCHAR(50) UNIQUE NOT NULL,     -- 设备编号，唯一标识
    device_name         VARCHAR(100) NOT NULL,           -- 设备名称
    device_model        VARCHAR(50),                     -- 设备型号
    device_type         VARCHAR(50),                     -- 设备类型，如 焊机
    manufacturer        VARCHAR(100),                    -- 制造商名称
    production_date     DATE,                            -- 出厂日期
    install_date        DATE,                            -- 安装日期
    install_location    VARCHAR(255),                   -- 安装位置描述，如A栋2F-东区
    online_address      VARCHAR(255), -- 设备在线地址（如IP、RTU 编号、MQTT Topic 等）
    team_name           VARCHAR(100),            -- 所属班组/区域，如 一工厂、夜班A组
    is_locked           BOOLEAN DEFAULT false,           -- 是否锁定（如维修或异常）
    description         TEXT,                            -- 备注信息或扩展描述
    created_at          TIMESTAMP DEFAULT now(),         -- 创建时间
    updated_at          TIMESTAMP DEFAULT now() -- 更新时间（建议配合触发器自动更新）
);

```
我创建设备类型表中是否可以关联tdengine的超级表名称呢？这样调用/api/v1/device/realtime-data接口时，根据设备类型来查询不同的超级表下的所有子表的实时数据。


请帮我更新/api/v1/device/data/realtime接口逻辑，
1. 接口路径：/api/v1/device/data/realtime
2. 接口方法：GET
3. 接口参数：
    - type_code：设备类型编码，可选参数，默认值为 'welding'
    - page：分页页码，可选参数，默认值为 1
    - page_size：每页数量，可选参数，默认值为 10
    - use_dynamic_fields：是否使用动态字段支持，可选参数，默认值为 false
4. 接口响应：
    - 响应状态码：200

在控制器中使用静态字段查询时，若type_code为welding,则先检索postgreSQL数据库中t_device_info表里device_type为welding的设备，获取所有device_code，
然后根据device_code分批次到tdengine数据库里查询所t_{device_code}为表名的有子表的最新数据。可以每次根据页面展示条数来实现批次查询。

如上接口逻辑更新是否可以改善当前tdengine批量查询数据带来延迟无法响应返回结果的问题？

---

## 调度任务日志统一规划实施方案

### 项目背景
当前调度任务日志记录存在以下问题：
- 每个任务只有一条最终日志，缺少执行过程记录
- 重试过程信息丢失，无法追踪重试详情
- 缺少细分的日志分类，难以进行问题诊断
- RetryManager的重试统计信息未持久化到数据库

### 统一规划目标
1. **完整的执行轨迹追踪**：记录任务从开始到结束的完整过程
2. **详细的重试过程记录**：每次重试都有独立的日志记录
3. **统一的日志分类**：建立标准化的日志类型和执行阶段分类
4. **向后兼容性**：保持现有API和查询方式的兼容性

### 实施步骤

#### 第一阶段：数据库扩展 ⏳ 待开始

**1.1 扩展SyncJobLog模型字段** ✅ 已完成
- [x] 添加 `log_type` 字段（枚举类型）
  - `execution_start`: 执行开始
  - `retry_attempt`: 重试尝试
  - `success`: 成功完成
  - `failure`: 失败终止
  - `timeout`: 超时
  - `exception`: 异常
  - `strategy_change`: 策略调整

- [x] 添加 `execution_phase` 字段（枚举类型）
  - `initial`: 初始执行
  - `retry`: 重试执行
  - `final`: 最终结果

- [x] 添加 `parent_log_id` 字段（外键，建立日志层次关系）

- [x] 扩展 `retry_context` 字段（JSON格式）
  ```json
  {
    "strategy_name": "exponential_backoff",
    "delay_seconds": 2.5,
    "attempt_number": 2,
    "max_attempts": 3,
    "error_category": "network_error",
    "adaptive_adjustments": {
      "delay_multiplier": 1.5,
      "timeout_extended": true
    }
  }
  ```

- [x] 添加 `performance_metrics` 字段（JSON格式）
  ```json
  {
    "cpu_usage_percent": 15.2,
    "memory_usage_mb": 128.5,
    "network_latency_ms": 45,
    "database_query_time_ms": 120,
    "api_response_time_ms": 850
  }
  ```

**1.2 创建数据库迁移脚本** ✅ 已完成
- [x] 编写迁移脚本添加新字段
- [x] 为现有数据设置默认值
- [x] 创建新的数据库索引
  - `idx_sync_job_log_type`
  - `idx_sync_job_log_phase`
  - `idx_sync_job_parent_log`
  - `idx_sync_job_log_hierarchy`
- [x] 创建迁移脚本：`scripts/migrate_sync_job_log_unified_logging.py`

**1.3 更新模型定义** ✅ 已完成
- [x] 修改 `app/models/task.py` 中的 `SyncJobLog` 模型
- [x] 添加新字段的验证规则
- [x] 更新模型的 `__repr__` 方法
- [x] 添加枚举类型：`LogType` 和 `ExecutionPhase`

**1.4 执行数据库迁移** ✅ 已完成
- [x] 运行迁移脚本
- [x] 验证字段添加成功
- [x] 检查索引创建情况
- [x] 确认现有数据迁移正确
- [x] 迁移脚本执行成功，所有新字段和索引已创建

#### 第一阶段总结 ✅ 已完成
所有数据库扩展工作已完成，包括：
- 新增枚举类型：`LogType` 和 `ExecutionPhase`
- 扩展 `SyncJobLog` 模型字段
- 创建数据库迁移脚本并成功执行
- 添加性能优化索引

#### 第二阶段：代码逻辑修改 ⏳ 待开始

**2.1 修改调度器逻辑**
- [ ] 更新 `app/core/scheduler.py` 中的 `_execute_sync_job` 方法
- [ ] 实现分层日志记录：
  ```python
  # 创建主日志（execution_start）
  main_log = SyncJobLog(
      job=job,
      log_type='execution_start',
      execution_phase='initial',
      status='running'
  )
  
  # 执行过程中创建阶段日志
  # 最终创建结果日志（success/failure）
  ```

**2.2 修改重试管理器**
- [ ] 更新 `app/core/retry.py` 中的 `RetryManager.execute_with_retry` 方法
- [ ] 为每次重试创建独立的日志记录：
  ```python
  # 每次重试创建子日志
  retry_log = SyncJobLog(
      job=job,
      log_type='retry_attempt',
      execution_phase='retry',
      parent_log_id=main_log.id,
      retry_context=retry_context_json
  )
  ```

**2.3 持久化重试统计信息**
- [ ] 将 `RetryStats` 信息保存到数据库
- [ ] 在任务完成后更新主日志的统计信息

#### 第三阶段：API和前端优化 ⏳ 待开始

**3.1 更新日志查询API**
- [ ] 扩展现有的日志查询接口
- [ ] 支持按 `log_type` 和 `execution_phase` 筛选
- [ ] 添加日志层次关系查询
- [ ] 实现日志时间线视图API

**3.2 前端展示优化**
- [ ] 更新日志列表页面，支持分类展示
- [ ] 实现日志时间线视图
- [ ] 添加重试过程的可视化展示
- [ ] 支持日志详情的层次化展示

#### 第四阶段：系统优化 ⏳ 待开始

**4.1 性能优化**
- [ ] 实现日志分区策略（按时间分区）
- [ ] 添加日志清理策略（自动清理过期日志）
- [ ] 优化查询性能（合理使用索引）

**4.2 监控和告警**
- [ ] 添加日志量监控
- [ ] 实现异常日志告警
- [ ] 添加性能指标监控

### 预期效果

**提升的能力：**
1. **完整的执行轨迹**：可以追踪任务从开始到结束的完整过程
2. **详细的重试过程**：每次重试的原因、延迟、结果都有记录
3. **智能问题诊断**：通过日志分类快速定位问题类型
4. **性能优化依据**：通过性能指标分析系统瓶颈
5. **向后兼容**：现有功能不受影响

**注意事项：**
1. **日志量增长**：需要合理的清理策略
2. **查询性能**：需要优化索引和查询逻辑
3. **存储成本**：考虑日志压缩和归档
4. **迁移策略**：确保平滑升级

### 当前进度
- ✅ 需求分析和方案设计完成
- ⏳ 等待开始实施第一阶段

---

