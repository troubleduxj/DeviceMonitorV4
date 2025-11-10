#!/usr/bin/env python3
"""
检查数据库中所有表的结构和相似性
"""

import asyncio
import asyncpg
from collections import defaultdict

async def check_all_tables():
    conn = await asyncpg.connect('postgresql://postgres:Hanatech%40123@127.0.0.1:5432/devicemonitor')
    
    # 获取所有用户表
    tables = await conn.fetch("""
        SELECT 
            table_name,
            table_type
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    print('数据库中的所有表:')
    print('=' * 50)
    
    # 按前缀分组
    table_groups = defaultdict(list)
    
    for table in tables:
        table_name = table['table_name']
        print(f'  - {table_name}')
        
        # 按前缀分组
        if table_name.startswith('t_sys_'):
            prefix = 't_sys_'
        elif table_name.startswith('t_'):
            prefix = 't_'
        elif '_' in table_name:
            prefix = table_name.split('_')[0] + '_'
        else:
            prefix = 'other'
        
        table_groups[prefix].append(table_name)
    
    print('\n按前缀分组的表:')
    print('=' * 50)
    
    for prefix, table_list in table_groups.items():
        print(f'\n{prefix} 组 ({len(table_list)} 个表):')
        for table_name in sorted(table_list):
            print(f'  - {table_name}')
    
    # 查找相似的表名
    print('\n可能重复或相似的表:')
    print('=' * 50)
    
    all_table_names = [t['table_name'] for t in tables]
    similar_groups = defaultdict(list)
    
    for table_name in all_table_names:
        # 移除复数形式的s，查找相似表
        base_name = table_name.rstrip('s')
        for other_table in all_table_names:
            if other_table != table_name:
                other_base = other_table.rstrip('s')
                if base_name == other_base or table_name in other_table or other_table in table_name:
                    similar_groups[table_name].append(other_table)
    
    for table_name, similar_tables in similar_groups.items():
        if similar_tables:
            print(f'\n{table_name} 的相似表:')
            for similar in similar_tables:
                print(f'  - {similar}')
    
    # 检查权限相关表的详细信息
    permission_tables = [t['table_name'] for t in tables if 'permission' in t['table_name'].lower()]
    
    if permission_tables:
        print('\n权限相关表详细信息:')
        print('=' * 50)
        
        for table_name in permission_tables:
            print(f'\n表: {table_name}')
            
            # 获取表结构
            columns = await conn.fetch("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, table_name)
            
            print('  列结构:')
            for col in columns:
                nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f'    - {col["column_name"]}: {col["data_type"]} {nullable}{default}')
            
            # 获取记录数
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {table_name}')
            print(f'  记录数: {count:,}')
            
            # 获取索引
            indexes = await conn.fetch("""
                SELECT indexname, indexdef
                FROM pg_indexes 
                WHERE tablename = $1 AND schemaname = 'public'
                ORDER BY indexname
            """, table_name)
            
            if indexes:
                print('  索引:')
                for idx in indexes:
                    print(f'    - {idx["indexname"]}')
    
    await conn.close()

if __name__ == '__main__':
    asyncio.run(check_all_tables())