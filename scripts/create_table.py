#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
焊机日报数据表创建脚本
用途：创建t_welding_daily_report表及相关索引和约束
"""

import asyncio
import asyncpg
import os
from pathlib import Path

# 数据库连接配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

async def create_welding_daily_report_table():
    """
    创建焊机日报数据表
    """
    connection = None
    try:
        # 连接数据库
        print("正在连接数据库...")
        connection = await asyncpg.connect(**DB_CONFIG)
        print("数据库连接成功")
        
        # 检查表是否已存在
        table_exists = await connection.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 't_welding_daily_report')"
        )
        
        if table_exists:
            print("⚠ 表 t_welding_daily_report 已存在，跳过创建")
            return True
        
        print("正在创建表 t_welding_daily_report...")
        
        # 创建主表
        create_table_sql = """
        CREATE TABLE t_welding_daily_report (
            id SERIAL PRIMARY KEY,
            prod_code VARCHAR(50) NOT NULL,
            team_name VARCHAR(100),
            shift_name VARCHAR(50),
            report_date DATE NOT NULL,
            welding_duration_seconds NUMERIC(10, 2),
            power_on_duration_seconds NUMERIC(10, 2),
            wire_consumption_kg NUMERIC(10, 3),
            gas_consumption_l NUMERIC(10, 3),
            energy_consumption_kwh NUMERIC(10, 3),
            raw_execution_code SMALLINT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        await connection.execute(create_table_sql)
        print("✓ 主表创建成功")
        
        # 创建索引
        print("正在创建索引...")
        
        index_sqls = [
            "CREATE INDEX idx_welding_daily_report_prod_code_date ON t_welding_daily_report (prod_code, report_date)",
            "CREATE INDEX idx_welding_daily_report_date ON t_welding_daily_report (report_date)",
            "CREATE INDEX idx_welding_daily_report_created_at ON t_welding_daily_report (created_at)"
        ]
        
        for i, sql in enumerate(index_sqls, 1):
            await connection.execute(sql)
            print(f"✓ 索引 {i} 创建成功")
        
        # 添加唯一性约束
        print("正在添加约束...")
        constraint_sql = """
        ALTER TABLE t_welding_daily_report
        ADD CONSTRAINT unique_device_day_shift 
        UNIQUE (prod_code, report_date, shift_name)
        """
        await connection.execute(constraint_sql)
        print("✓ 唯一性约束添加成功")
        
        # 添加表注释
        print("正在添加注释...")
        comment_sqls = [
            "COMMENT ON TABLE t_welding_daily_report IS '焊机日报数据表，存储从焊云平台采集的设备运行数据'",
            "COMMENT ON COLUMN t_welding_daily_report.prod_code IS '设备制造编码，对应API返回的D01字段'",
            "COMMENT ON COLUMN t_welding_daily_report.team_name IS '班组名称，对应API返回的D02字段'",
            "COMMENT ON COLUMN t_welding_daily_report.shift_name IS '班次，对应API返回的D03字段'",
            "COMMENT ON COLUMN t_welding_daily_report.report_date IS '日报时间，对应API返回的D04字段'",
            "COMMENT ON COLUMN t_welding_daily_report.welding_duration_seconds IS '焊接时长（秒），对应API返回的D05字段'",
            "COMMENT ON COLUMN t_welding_daily_report.power_on_duration_seconds IS '开机时长（秒），对应API返回的D06字段'",
            "COMMENT ON COLUMN t_welding_daily_report.wire_consumption_kg IS '焊丝消耗（千克），对应API返回的D07字段'",
            "COMMENT ON COLUMN t_welding_daily_report.gas_consumption_l IS '气体消耗（升），对应API返回的D08字段'",
            "COMMENT ON COLUMN t_welding_daily_report.energy_consumption_kwh IS '电能消耗（千瓦时），对应API返回的D09字段'",
            "COMMENT ON COLUMN t_welding_daily_report.raw_execution_code IS 'API返回的Execution状态码，0表示成功'",
            "COMMENT ON COLUMN t_welding_daily_report.created_at IS '记录创建时间'",
            "COMMENT ON COLUMN t_welding_daily_report.updated_at IS '记录更新时间'"
        ]
        
        for sql in comment_sqls:
            await connection.execute(sql)
        print("✓ 注释添加成功")
        
        # 验证表是否创建成功
        print("\n验证表创建结果...")
        table_exists = await connection.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 't_welding_daily_report')"
        )
        
        if table_exists:
            print("✓ 表 t_welding_daily_report 创建成功")
            
            # 查看表结构
            columns = await connection.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 't_welding_daily_report'
                ORDER BY ordinal_position
            """)
            
            print("\n表结构信息:")
            print(f"{'字段名':<30} {'数据类型':<20} {'允许空值':<10} {'默认值':<20}")
            print("-" * 80)
            for col in columns:
                print(f"{col['column_name']:<30} {col['data_type']:<20} {col['is_nullable']:<10} {str(col['column_default'] or ''):<20}")
            
            # 查看索引信息
            indexes = await connection.fetch("""
                SELECT indexname, indexdef
                FROM pg_indexes 
                WHERE tablename = 't_welding_daily_report'
            """)
            
            print("\n索引信息:")
            for idx in indexes:
                print(f"✓ {idx['indexname']}: {idx['indexdef']}")
            
        else:
            print("✗ 表创建失败")
            return False
        
        print("\n🎉 焊机日报数据表创建完成！")
        return True
        
    except Exception as e:
        print(f"❌ 创建表时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if connection:
            await connection.close()
            print("数据库连接已关闭")

async def main():
    """
    主函数
    """
    print("=" * 60)
    print("焊机日报数据表创建工具")
    print("=" * 60)
    
    success = await create_welding_daily_report_table()
    
    if success:
        print("\n✅ 任务1.1完成: 目标数据表创建成功")
        print("下一步: 验证设备信息表数据 (任务1.2)")
    else:
        print("\n❌ 任务1.1失败: 目标数据表创建失败")
        print("请检查错误信息并重试")

if __name__ == "__main__":
    asyncio.run(main())