"""
检查AI相关的API是否已在数据库中
"""
import asyncio
import asyncpg

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

async def check_ai_apis():
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 查询AI相关的API
        ai_apis = await conn.fetch("""
            SELECT 
                g.group_name,
                e.api_name,
                e.http_method,
                e.api_path
            FROM t_sys_api_endpoints e
            LEFT JOIN t_sys_api_groups g ON e.group_id = g.id
            WHERE e.api_path LIKE '%/ai/%'
            ORDER BY g.group_name, e.api_path
        """)
        
        print("="*80)
        print("🔍 数据库中的AI相关API")
        print("="*80)
        print(f"\n找到 {len(ai_apis)} 个AI相关的API\n")
        
        if ai_apis:
            current_group = None
            for api in ai_apis:
                group = api['group_name'] or '未分组'
                if group != current_group:
                    print(f"\n## {group}")
                    current_group = group
                print(f"  {api['http_method']:6} {api['api_path']}")
                print(f"         {api['api_name']}")
        else:
            print("❌ 数据库中没有AI相关的API！")
            print("\n这意味着AI监测功能的API还没有同步到权限系统中。")
        
        # 查询所有分组
        groups = await conn.fetch("""
            SELECT group_name, COUNT(*) as api_count
            FROM t_sys_api_endpoints e
            JOIN t_sys_api_groups g ON e.group_id = g.id
            GROUP BY group_name
            ORDER BY group_name
        """)
        
        print(f"\n{'='*80}")
        print("📊 所有API分组统计")
        print(f"{'='*80}\n")
        for group in groups:
            print(f"  {group['group_name']}: {group['api_count']} 个API")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(check_ai_apis())
