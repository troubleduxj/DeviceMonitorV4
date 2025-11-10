#!/usr/bin/env python3
"""
检查备份表和正式表的结构
"""

import asyncio
import asyncpg
from typing import List, Dict, Any


class TableChecker:
    """表结构检查器"""
    
    def __init__(self):
        self.db_config = {
            'host': '127.0.0.1',
            'port': 5432,
            'user': 'postgres',
            'password': 'Hanatech@123',
            'database': 'devicemonitor'
        }
    
    async def check_tables(self):
        """检查表结构"""
        conn = await asyncpg.connect(**self.db_config)
        
        try:
            # 查找所有备份表
            backup_tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%backup%' 
                ORDER BY table_name
            """)
            
            print("=== 备份表列表 ===")
            for table in backup_tables:
                print(f"  - {table['table_name']}")
            
            # 查找目标表
            target_tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('t_sys_dict_type', 't_sys_dict_data', 't_sys_config')
                ORDER BY table_name
            """)
            
            print("\n=== 目标表列表 ===")
            for table in target_tables:
                print(f"  - {table['table_name']}")
            
            # 检查具体的备份表结构
            backup_table_names = ['sys_dict_type_backup', 'sys_dict_data_backup', 'sys_config_backup']
            
            for table_name in backup_table_names:
                print(f"\n=== 检查表 {table_name} ===")
                
                # 检查表是否存在
                exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = $1
                    )
                """, table_name)
                
                if exists:
                    # 获取表结构
                    columns = await conn.fetch("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' AND table_name = $1
                        ORDER BY ordinal_position
                    """, table_name)
                    
                    print(f"表结构:")
                    for col in columns:
                        print(f"  {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
                    
                    # 获取数据行数
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                    print(f"数据行数: {count}")
                    
                    # 如果有数据，显示前几行
                    if count > 0:
                        sample_data = await conn.fetch(f"SELECT * FROM {table_name} LIMIT 3")
                        print("样本数据:")
                        for i, row in enumerate(sample_data, 1):
                            print(f"  行{i}: {dict(row)}")
                else:
                    print("表不存在")
            
        finally:
            await conn.close()


async def main():
    """主函数"""
    checker = TableChecker()
    await checker.check_tables()


if __name__ == "__main__":
    asyncio.run(main())