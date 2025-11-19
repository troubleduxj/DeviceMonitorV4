"""
详细检查设备维护管理分组的API
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

async def check_maintenance_apis():
    """检查设备维护管理分组的API"""
    print("="*80)
    print("🔍 详细检查设备维护管理分组的API")
    print("="*80)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 获取设备维护管理分组的所有API
        apis = await conn.fetch("""
            SELECT 
                a.id,
                a.api_code,
                a.api_name,
                a.api_path,
                a.http_method,
                a.description,
                g.group_name,
                g.group_code
            FROM t_sys_api_endpoints a
            LEFT JOIN t_sys_api_groups g ON a.group_id = g.id
            WHERE g.group_name LIKE '%维护%' OR g.group_name LIKE '%维修%'
            ORDER BY a.api_path, a.http_method
        """)
        
        print(f"\n✅ 找到 {len(apis)} 个维护/维修相关的API\n")
        
        if not apis:
            print("未找到相关API")
            return
        
        # 按路径分组
        path_groups = defaultdict(list)
        for api in apis:
            path_groups[api['api_path']].append(api)
        
        print(f"{'='*80}")
        print("📋 按路径分组的API列表")
        print(f"{'='*80}\n")
        
        for path, api_list in sorted(path_groups.items()):
            print(f"路径: {path}")
            print(f"数量: {len(api_list)} 个")
            
            if len(api_list) > 1:
                print(f"⚠️  可能存在重复或相似的API:")
            
            for api in api_list:
                print(f"  {api['http_method']:6} | ID:{api['id']:4} | {api['api_name']}")
                if api['description']:
                    print(f"         描述: {api['description'][:60]}")
            print()
        
        # 检查相似的API名称
        print(f"{'='*80}")
        print("🔍 检查相似的API名称")
        print(f"{'='*80}\n")
        
        name_groups = defaultdict(list)
        for api in apis:
            # 提取API名称的关键词
            name_key = api['api_name'].replace('获取', '').replace('创建', '').replace('更新', '').replace('删除', '').strip()
            name_groups[name_key].append(api)
        
        for name_key, api_list in sorted(name_groups.items()):
            if len(api_list) > 1:
                print(f"相似名称: {name_key}")
                for api in api_list:
                    print(f"  {api['http_method']:6} {api['api_path']:50} | {api['api_name']}")
                print()
        
        # 检查路径模式
        print(f"{'='*80}")
        print("📊 路径模式分析")
        print(f"{'='*80}\n")
        
        # 提取路径的基础部分（去掉参数）
        base_paths = defaultdict(list)
        for api in apis:
            # 去掉路径参数
            base_path = api['api_path']
            # 替换 {xxx} 为 *
            import re
            base_path = re.sub(r'\{[^}]+\}', '*', base_path)
            base_paths[base_path].append(api)
        
        for base_path, api_list in sorted(base_paths.items()):
            if len(api_list) > 1:
                print(f"路径模式: {base_path}")
                print(f"匹配数量: {len(api_list)}")
                
                # 按HTTP方法分组
                method_groups = defaultdict(list)
                for api in api_list:
                    method_groups[api['http_method']].append(api)
                
                for method, method_apis in sorted(method_groups.items()):
                    print(f"  {method}:")
                    for api in method_apis:
                        print(f"    {api['api_path']:50} | {api['api_name']}")
                print()
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(check_maintenance_apis())
