好的，以下是一份 **完整、结构清晰、可直接交付给 AI IDE 实施开发的接口设计方案**，用于实现你提出的设备实时数据查询接口（支持 WebSocket 和 REST，基于 PostgreSQL + TDengine 架构）。

---

# 🌐 设备实时数据查询系统设计方案

## 🎯 目标

构建一个统一的接口 `/api/v1/device/realtime-data`，支持前端实时查询/订阅各类型设备的实时数据（如焊机、切割机等），并支持设备类型扩展。

---

## 🧱 技术栈

| 模块           | 技术                           |
| ------------ | ---------------------------- |
| 后端 API       | FastAPI                      |
| WebSocket 服务 | FastAPI WebSocket            |
| 元数据存储        | PostgreSQL                   |
| 时序数据存储       | TDengine                     |
| 实时数据查询       | TDengine REST 或 WebSocket 接口 |
| 异步任务调度       | asyncio（并发 TDengine 查询）      |
| 前端           | 当前vue框架 + WebSocket 客户端         |

---

## 🧩 数据库结构设计（PostgreSQL）

### 1. `t_device_type`（设备类型表）

```sql
CREATE TABLE IF NOT EXISTS t_device_type (
    code VARCHAR(50) PRIMARY KEY,             -- 类型代码，如 weld, cut
    name VARCHAR(100) NOT NULL,               -- 类型名称，如 焊机
    tdengine_stable VARCHAR(100) NOT NULL,    -- 对应 TDengine 超级表名
    description TEXT
);
```

---

### 2. `t_device_info`（设备信息表）

```sql
CREATE TABLE IF NOT EXISTS t_device_info (
    id SERIAL PRIMARY KEY,
    device_code VARCHAR(50) UNIQUE NOT NULL,     -- 子表名，如 t_14412T0006
    device_name VARCHAR(100) NOT NULL,
    device_model VARCHAR(50),
    device_type VARCHAR(50) NOT NULL,            -- 对应 t_device_type.code
    manufacturer VARCHAR(100),
    production_date DATE,
    install_date DATE,
    install_location VARCHAR(255),
    online_address VARCHAR(255),
    team_name VARCHAR(100),
    is_locked BOOLEAN DEFAULT false,
    description TEXT,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (device_type) REFERENCES t_device_type(code)
);
```

---

### 3. （可选）`t_device_field`（设备字段元信息）

用于前端动态展示字段含义、顺序、单位等。

```sql
CREATE TABLE IF NOT EXISTS t_device_field (
    id SERIAL PRIMARY KEY,
    device_type VARCHAR(50) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    unit VARCHAR(20),
    sort_order INT DEFAULT 0,
    FOREIGN KEY (device_type) REFERENCES t_device_type(code)
);
```

---

## 🔗 REST API 接口定义

### ✅ 获取设备类型下拉选项

**GET** `/api/v1/device/types`

```json
[
  { "code": "weld", "name": "焊机" },
  { "code": "cut", "name": "切割机" }
]
```

---

### ✅ 获取实时数据（所有或指定类型）

**GET** `/api/v1/device/realtime-data?type_code=weld`

* `type_code` 可选：如果为空，返回所有设备类型下的实时数据；
* 按每台设备返回 TDengine 子表的最新一条数据；

**返回示例**：

```json
[
  {
    "device_code": "t_14412T0006",
    "device_type": "weld",
    "ts": "2025-06-27T10:01:00Z",
    "weld_current": 135,
    "weld_voltage": 26.2,
    ...
  },
  ...
]
```

---

## 🔌 WebSocket 实时推送接口

### ✅ WebSocket 地址

`ws://localhost:8000/api/v1/device/realtime-data/ws`

---

### 🔻 客户端消息格式（订阅）

```json
{
  "type": "subscribe",
  "device_type": "weld"
}
```

如需订阅所有类型：

```json
{
  "type": "subscribe"
}
```

---

### 🔺 服务端推送格式（周期性推送）

```json
[
  {
    "device_code": "t_14412T0006",
    "device_type": "weld",
    "ts": "2025-06-27T10:01:00Z",
    "weld_current": 135,
    "weld_voltage": 26.2,
    ...
  }
]
```

---

## ⚙️ 后端服务逻辑流程

### 🔁 1. 查询逻辑（REST + WebSocket 共享）

1. 若 `type_code` 非空：

   * 查询 `t_device_type` 表，获取其 `tdengine_stable`
   * 查询 `t_device_info` 表，获取所有设备子表名
   * 查询 TDengine 子表：`SELECT * FROM <stable>.<subtable> ORDER BY ts DESC LIMIT 1`

2. 若 `type_code` 为空：

   * 查询所有 `t_device_type` → 遍历每类设备的 `tdengine_stable`
   * 查询对应的 `t_device_info`，获取全部子表
   * 查询每个子表最新数据并聚合

---

### 🔀 2. WebSocket 订阅与推送

* 后端通过 `asyncio` 周期性查询并推送；
* 每个客户端订阅的设备类型不同，按连接维度隔离推送内容；
* 可设置 `push_interval = 2s` 或前端传入。

---

## 🔒 安全建议

| 项目     | 建议                                 |
| ------ | ---------------------------------- |
| 鉴权     | 建议 WebSocket 与 REST 接口均加入 token 校验 |
| 查询频率限制 | 避免 WebSocket 推送过频导致服务器过载           |
| 日志与审计  | 建议记录每次请求的类型与来源                     |
| 错误处理   | 所有接口应返回结构化异常信息                     |

---

## 📱 前端设计建议

### 📌 1. 下拉选择设备类型

* 通过 `/api/v1/device/types` 动态加载选项；
* 选择后发起 WebSocket 连接或 HTTP 请求订阅数据。

### 📌 2. 动态字段展示

* 建议通过 `t_device_field` 加载字段定义，用于构建表头与数据展示。

### 📌 3. 实时表格渲染

* 接收 WebSocket 推送数据；
* 多设备一行展示，字段根据类型动态适配；
* 支持设备锁定/报警状态标记；

---

## ✅ 总结：系统架构一览图

```
+-----------+       REST / WS      +-----------------+
|  Frontend | <------------------> |   FastAPI API   |
+-----------+                      +--------+--------+
                                            |
                          +-----------------+------------------+
                          | PostgreSQL (设备元数据)           |
                          | - t_device_type                   |
                          | - t_device_info                   |
                          | - t_device_field (可选)           |
                          +------------------------------------+
                                            |
                          +-----------------+------------------+
                          | TDengine (实时数据)                |
                          | - welding_real_data.t_xxxxxx       |
                          | - cutting_real_data.t_xxxxxx       |
                          +------------------------------------+
```


## 方案重构分析

当前实现逻辑分析结果

🔍 问题诊断

当前实现存在根本性架构问题：



数据混淆：我们将API返回的 items（当前页的20条实时数据）同时赋值给了 devices.value 和 allDevices.value

功能缺失：allDevices 应该包含全部7182个设备的基本信息，但现在只包含当前页20个设备

搜索过滤失效：用户无法在全部设备中搜索过滤，只能在当前页20个设备中操作


💡 正确的架构设计

根据您的设计思路，应该采用两阶段数据加载模式：


阶段1：获取设备列表



获取所有设备的基本信息（设备编码、名称、类型等）

存储在 allDevices.value（7182条记录）

用于搜索、过滤、分页计算


阶段2：获取实时数据



根据过滤结果和当前页码

只获取当前页20个设备的实时数据

存储在 devices.value（20条记录）

用于页面显示


🚀 建议的重构方案


新增设备列表API：/api/devices/list - 返回所有设备基本信息

修改实时数据API：/api/devices/realtime - 接受设备编码数组参数

重构前端逻辑：分离设备列表管理和实时数据获取

这样既能实现全局搜索过滤，又能减少数据传输压力。您觉得这个分析和方案如何？



---

# 数据统计模块设计方案

## 1.1 焊机-在线率

### 1）Tdengine数据库结构设计

**目前tdengine设计的超级表主要有如下：**

welding_real_data：焊机各设备数据实时采集表

welding_status_minutely：焊机各设备每分钟状态时长统计数据表（统计单位：分钟）

welding_status_hourly：焊机各设备每小时统计数据表（统计单位：分钟）

welding_status_hourly_summary：所有焊机设备每小时统计数据表（统计单位：分钟）

welding_status_daily：焊机各设备每天统计数据表（统计单位：分钟）

welding_status_daily_summary：所有焊机设备每天统计数据表（统计单位：分钟）



---

#### welding_real_data

**表描述：**

焊机各设备数据实时采集表

📄**数据字段（Columns）：**

| 字段名         | 数据类型  | 描述           | 示例                |
| -------------- | --------- | -------------- | ------------------- |
| ts             | TIMESTAMP | 时间戳         | 2023-08-23 10:00:00 |
| team_name      | NCHAR(50) | D02 班组名称   | 班组一              |
| device_status  | NCHAR(50) | D03 设备状态   | 焊接/待机           |
| lock_status    | BOOL      | D04 锁状态     | true / false        |
| preset_current | FLOAT     | D05 预设电流   | 10.5                |
| preset_voltage | FLOAT     | D06 预设电压   | 220.0               |
| weld_current   | FLOAT     | D07 焊接电流   | 11.0                |
| weld_voltage   | FLOAT     | D08 焊接电压   | 225.0               |
| material       | NCHAR(50) | D09 预设功率   | Q235                |
| wire_diameter  | FLOAT     | D10 丝径（mm） | 1.2                 |
| gas_type       | NCHAR(50) | D11 气体类型   | CO2                 |
| weld_method    | NCHAR(50) | D12 焊接方式   | MIG                 |
| weld_control   | NCHAR(50) | D13 焊接控制   | 脉冲                |
| staff_id       | NCHAR(50) | D14 焊工编号   | W123456             |
| workpiece_id   | NCHAR(50) | D15 工件编号   | WP123456            |
| ip_quality     | INT       | 数据质量       | 100                 |

🏷️**标签字段（Tags）:**

| 字段名      | 数据类型  | 描述             | 示例            |
| ----------- | --------- | ---------------- | --------------- |
| device_code | NCHAR(50) | D01 设备生产编码 | 14412T0006      |
| name        | NCHAR(50) | 设备名称         | t_{device_code} |



---

#### welding_status_minutely

**表描述：**

焊机各设备每分钟状态时长统计数据表（统计单位：分钟）

📄**数据字段（Columns）：**

| name | type      |
| :--- | :-------- |
| ts   | TIMESTAMP |

| ts               | TIMESTAMP |
| ---------------- | --------- |
| device_code      | NCHAR     |
| welding_minutes  | DOUBLE    |
| standby_minutes  | DOUBLE    |
| alarm_minutes    | DOUBLE    |
| shutdown_minutes | DOUBLE    |
| ip_quality       |           |



🏷️**标签字段（Tags）:**
