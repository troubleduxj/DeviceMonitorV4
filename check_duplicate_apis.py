"""
检查数据库中重复的API
"""
import asyncio
import asyncpg
from collections import defaultdict

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

async def check_duplicate_apis():
    """检查重复的API"""
    print("="*80)
    print("🔍 检查数据库中重复的API")
    print("="*80)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 获取所有API
        apis = await conn.fetch("""
            SELECT 
                a.id,
                a.api_code,
                a.api_name,
                a.api_path,
                a.http_method,
                g.group_name,
                g.group_code
            FROM t_sys_api_endpoints a
            LEFT JOIN t_sys_api_groups g ON a.group_id = g.id
            ORDER BY g.group_name, a.api_path, a.http_method
        """)
        
        print(f"\n✅ 查询到 {len(apis)} 个API\n")
        
        # 按 (api_path, http_method) 分组，查找重复
        path_method_map = defaultdict(list)
        for api in apis:
            key = (api['api_path'], api['http_method'])
            path_method_map[key].append(api)
        
        # 找出重复的API
        duplicates = {k: v for k, v in path_method_map.items() if len(v) > 1}
        
        if duplicates:
            print(f"⚠️  发现 {len(duplicates)} 组重复的API:\n")
            
            for (path, method), api_list in sorted(duplicates.items()):
                print(f"{'='*80}")
                print(f"🔴 重复: {method} {path}")
                print(f"{'='*80}")
                
                for api in api_list:
                    print(f"  ID: {api['id']}")
                    print(f"  名称: {api['api_name']}")
                    print(f"  代码: {api['api_code']}")
                    print(f"  分组: {api['group_name']} ({api['group_code']})")
                    print(f"  ---")
                print()
        else:
            print("✅ 没有发现重复的API")
        
        # 按分组统计
        print(f"\n{'='*80}")
        print("📊 按分组统计API数量")
        print(f"{'='*80}\n")
        
        group_stats = defaultdict(list)
        for api in apis:
            group_name = api['group_name'] or '未分组'
            group_stats[group_name].append(api)
        
        for group_name, api_list in sorted(group_stats.items()):
            print(f"{group_name}: {len(api_list)} 个API")
            
            # 检查该分组内是否有重复
            group_path_method = defaultdict(list)
            for api in api_list:
                key = (api['api_path'], api['http_method'])
                group_path_method[key].append(api)
            
            group_duplicates = {k: v for k, v in group_path_method.items() if len(v) > 1}
            if group_duplicates:
                print(f"  ⚠️  该分组内有 {len(group_duplicates)} 组重复:")
                for (path, method), dup_list in group_duplicates.items():
                    print(f"    - {method} {path} (重复{len(dup_list)}次)")
        
        # 特别检查维修记录分组
        print(f"\n{'='*80}")
        print("🔍 详细检查维修记录分组")
        print(f"{'='*80}\n")
        
        maintenance_apis = [api for api in apis if '维修' in (api['group_name'] or '')]
        
        if maintenance_apis:
            print(f"维修记录相关分组共有 {len(maintenance_apis)} 个API:\n")
            
            # 按路径分组
            path_groups = defaultdict(list)
            for api in maintenance_apis:
                path_groups[api['api_path']].append(api)
            
            for path, api_list in sorted(path_groups.items()):
                if len(api_list) > 1:
                    print(f"⚠️  路径 {path} 有 {len(api_list)} 个API:")
                    for api in api_list:
                        print(f"  - {api['http_method']:6} | ID:{api['id']:4} | {api['api_name']}")
                    print()
        else:
            print("未找到维修记录相关的API")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(check_duplicate_apis())
