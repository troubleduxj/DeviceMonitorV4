#!/usr/bin/env python3
"""
检查数据同步结果
"""

import asyncio
import asyncpg


async def check_sync_result():
    """检查同步结果"""
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='Hanatech@123',
        database='devicemonitor'
    )
    
    try:
        print("=== 检查数据同步结果 ===")
        
        # 检查字典类型表
        print("\n--- t_sys_dict_type 表 ---")
        count = await conn.fetchval("SELECT COUNT(*) FROM t_sys_dict_type")
        print(f"总记录数: {count}")
        
        if count > 0:
            rows = await conn.fetch("SELECT id, type_code, type_name FROM t_sys_dict_type ORDER BY id LIMIT 10")
            for i, row in enumerate(rows, 1):
                print(f"  类型{i}: ID={row['id']}, Code={row['type_code']}, Name={row['type_name']}")
        
        # 检查字典数据表
        print("\n--- t_sys_dict_data 表 ---")
        count = await conn.fetchval("SELECT COUNT(*) FROM t_sys_dict_data")
        print(f"总记录数: {count}")
        
        if count > 0:
            rows = await conn.fetch("""
                SELECT d.id, d.data_label, d.data_value, t.type_code, t.type_name 
                FROM t_sys_dict_data d 
                JOIN t_sys_dict_type t ON d.dict_type_id = t.id 
                ORDER BY d.id LIMIT 10
            """)
            for i, row in enumerate(rows, 1):
                print(f"  数据{i}: ID={row['id']}, Label={row['data_label']}, Value={row['data_value']}, Type={row['type_code']}")
        
        # 检查系统配置表
        print("\n--- t_sys_config 表 ---")
        count = await conn.fetchval("SELECT COUNT(*) FROM t_sys_config")
        print(f"总记录数: {count}")
        
        if count > 0:
            rows = await conn.fetch("SELECT param_key, param_name, param_value FROM t_sys_config ORDER BY param_key LIMIT 10")
            for i, row in enumerate(rows, 1):
                print(f"  配置{i}: Key={row['param_key']}, Name={row['param_name']}, Value={row['param_value'][:50]}...")
        
        # 检查备份表中的字典数据
        print("\n--- sys_dict_data_backup 表样本 ---")
        backup_count = await conn.fetchval("SELECT COUNT(*) FROM sys_dict_data_backup")
        print(f"备份表总记录数: {backup_count}")
        
        if backup_count > 0:
            backup_rows = await conn.fetch("""
                SELECT id, dict_type_id, data_label, data_value 
                FROM sys_dict_data_backup 
                ORDER BY id LIMIT 5
            """)
            for i, row in enumerate(backup_rows, 1):
                print(f"  备份数据{i}: ID={row['id']}, TypeID={row['dict_type_id']}, Label={row['data_label']}, Value={row['data_value']}")
        
        # 检查字典类型ID映射问题
        print("\n--- 检查字典类型ID映射 ---")
        backup_type_ids = await conn.fetch("SELECT DISTINCT dict_type_id FROM sys_dict_data_backup ORDER BY dict_type_id")
        main_type_ids = await conn.fetch("SELECT id FROM t_sys_dict_type ORDER BY id")
        
        backup_ids = [row['dict_type_id'] for row in backup_type_ids]
        main_ids = [row['id'] for row in main_type_ids]
        
        print(f"备份表中的字典类型ID: {backup_ids}")
        print(f"正式表中的字典类型ID: {main_ids}")
        
        missing_ids = set(backup_ids) - set(main_ids)
        if missing_ids:
            print(f"❌ 缺失的字典类型ID: {missing_ids}")
        else:
            print("✅ 所有字典类型ID都存在")
            
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_sync_result())