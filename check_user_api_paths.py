"""
检查用户相关API的实际路径
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

async def check_user_api_paths():
    """检查用户相关API路径"""
    print("="*80)
    print("🔍 检查用户相关API的实际路径")
    print("="*80)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 查找包含 users 的API
        apis = await conn.fetch("""
            SELECT 
                a.id,
                a.api_path,
                a.http_method,
                a.api_name,
                g.group_name
            FROM t_sys_api_endpoints a
            LEFT JOIN t_sys_api_groups g ON a.group_id = g.id
            WHERE a.api_path LIKE '%/users%'
            ORDER BY a.api_path, a.http_method
        """)
        
        print(f"\n找到 {len(apis)} 个包含 /users 的API\n")
        
        # 按路径分组
        from collections import defaultdict
        path_groups = defaultdict(list)
        
        for api in apis:
            path_groups[api['api_path']].append(api)
        
        # 查找可能冲突的路径
        print("="*80)
        print("检查可能的路径冲突")
        print("="*80 + "\n")
        
        conflicts = []
        for path, api_list in sorted(path_groups.items()):
            # 检查是否有多个方法
            methods = [api['http_method'] for api in api_list]
            if len(set(methods)) < len(methods):
                conflicts.append((path, api_list))
                print(f"⚠️  路径冲突: {path}")
                for api in api_list:
                    print(f"  {api['http_method']:6} | {api['group_name']} | {api['api_name']}")
                print()
        
        if not conflicts:
            print("✅ 没有发现路径冲突\n")
        
        # 显示所有用户相关的API
        print("="*80)
        print("所有用户相关的API")
        print("="*80 + "\n")
        
        for path, api_list in sorted(path_groups.items()):
            print(f"路径: {path}")
            for api in api_list:
                print(f"  {api['http_method']:6} | {api['group_name']:20} | {api['api_name']}")
            print()
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(check_user_api_paths())
