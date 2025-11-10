#!/usr/bin/env python3
"""
检查数据库表结构
"""

import asyncio
import asyncpg

async def check_tables():
    conn = await asyncpg.connect('postgresql://postgres:Hanatech%40123@127.0.0.1:5432/devicemonitor')
    
    # 检查表是否存在
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name IN ('t_sys_api_endpoints', 't_sys_user_permissions', 't_sys_role_permissions')
    """)
    
    print('存在的表:')
    for table in tables:
        print(f'  - {table["table_name"]}')
    
    # 检查t_sys_api_endpoints表结构
    if any(t['table_name'] == 't_sys_api_endpoints' for t in tables):
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 't_sys_api_endpoints'
            ORDER BY ordinal_position
        """)
        
        print('\nt_sys_api_endpoints表结构:')
        for col in columns:
            print(f'  - {col["column_name"]}: {col["data_type"]}')
    
    await conn.close()

if __name__ == '__main__':
    asyncio.run(check_tables())