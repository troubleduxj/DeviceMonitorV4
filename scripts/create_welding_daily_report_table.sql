-- 焊机日报数据表创建脚本（简化版）
-- 创建时间: 2025-01-21
-- 用途: 存储从焊云平台采集的焊机日报数据

-- 创建主表
CREATE TABLE t_welding_daily_report (
    id SERIAL PRIMARY KEY,
    prod_code VARCHAR(50) NOT NULL,              -- 设备制造编码（D01）
    team_name VARCHAR(100),                      -- 班组名称（D02）
    shift_name VARCHAR(50),                      -- 班次（D03）
    report_date DATE NOT NULL,                   -- 日报时间（D04）

    welding_duration_seconds NUMERIC(10, 2),     -- 焊接时长（秒）D05
    power_on_duration_seconds NUMERIC(10, 2),    -- 开机时长（秒）D06
    wire_consumption_kg NUMERIC(10, 3),          -- 焊丝消耗（千克）D07
    gas_consumption_l NUMERIC(10, 3),            -- 气体消耗（升）D08
    energy_consumption_kwh NUMERIC(10, 3),       -- 电能消耗（千瓦时）D09

    raw_execution_code SMALLINT DEFAULT 0,       -- 接口Execution字段，用于记录采集状态

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_welding_daily_report_prod_code_date
ON t_welding_daily_report (prod_code, report_date);

CREATE INDEX idx_welding_daily_report_date
ON t_welding_daily_report (report_date);

CREATE INDEX idx_welding_daily_report_created_at
ON t_welding_daily_report (created_at);

-- 添加唯一性约束（防止重复数据）
ALTER TABLE t_welding_daily_report
ADD CONSTRAINT unique_device_day_shift 
UNIQUE (prod_code, report_date, shift_name);

-- 添加表注释
COMMENT ON TABLE t_welding_daily_report IS '焊机日报数据表，存储从焊云平台采集的设备运行数据';

-- 添加字段注释
COMMENT ON COLUMN t_welding_daily_report.prod_code IS '设备制造编码，对应API返回的D01字段';
COMMENT ON COLUMN t_welding_daily_report.team_name IS '班组名称，对应API返回的D02字段';
COMMENT ON COLUMN t_welding_daily_report.shift_name IS '班次，对应API返回的D03字段';
COMMENT ON COLUMN t_welding_daily_report.report_date IS '日报时间，对应API返回的D04字段';
COMMENT ON COLUMN t_welding_daily_report.welding_duration_seconds IS '焊接时长（秒），对应API返回的D05字段';
COMMENT ON COLUMN t_welding_daily_report.power_on_duration_seconds IS '开机时长（秒），对应API返回的D06字段';
COMMENT ON COLUMN t_welding_daily_report.wire_consumption_kg IS '焊丝消耗（千克），对应API返回的D07字段';
COMMENT ON COLUMN t_welding_daily_report.gas_consumption_l IS '气体消耗（升），对应API返回的D08字段';
COMMENT ON COLUMN t_welding_daily_report.energy_consumption_kwh IS '电能消耗（千瓦时），对应API返回的D09字段';
COMMENT ON COLUMN t_welding_daily_report.raw_execution_code IS 'API返回的Execution状态码，0表示成功';
COMMENT ON COLUMN t_welding_daily_report.created_at IS '记录创建时间';
COMMENT ON COLUMN t_welding_daily_report.updated_at IS '记录更新时间';

-- 输出创建结果
SELECT 'Table t_welding_daily_report created successfully' AS result;