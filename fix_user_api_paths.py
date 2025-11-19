"""
修复用户相关API的路径错误
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

async def fix_user_api_paths():
    """修复用户相关API路径"""
    print("="*80)
    print("🔧 修复用户相关API的路径错误")
    print("="*80)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 1. 修复部门用户相关API
        print("\n1️⃣  修复部门用户相关API\n")
        
        dept_apis = await conn.fetch("""
            SELECT id, api_path, http_method, api_name
            FROM t_sys_api_endpoints
            WHERE api_path LIKE '/api/v2/users/{dept_id}%'
            ORDER BY api_path
        """)
        
        print(f"找到 {len(dept_apis)} 个需要修复的部门用户API:\n")
        
        for api in dept_apis:
            old_path = api['api_path']
            new_path = old_path.replace('/api/v2/users/{dept_id}', '/api/v2/departments/{dept_id}')
            
            print(f"  {api['http_method']:6} | {api['api_name']}")
            print(f"    旧路径: {old_path}")
            print(f"    新路径: {new_path}")
            
            # 更新路径
            await conn.execute("""
                UPDATE t_sys_api_endpoints
                SET api_path = $1
                WHERE id = $2
            """, new_path, api['id'])
            
            print(f"    ✅ 已更新\n")
        
        # 2. 修复角色用户相关API
        print("2️⃣  修复角色用户相关API\n")
        
        role_apis = await conn.fetch("""
            SELECT id, api_path, http_method, api_name
            FROM t_sys_api_endpoints
            WHERE api_path LIKE '/api/v2/users/{role_id}%'
            ORDER BY api_path
        """)
        
        print(f"找到 {len(role_apis)} 个需要修复的角色用户API:\n")
        
        for api in role_apis:
            old_path = api['api_path']
            new_path = old_path.replace('/api/v2/users/{role_id}', '/api/v2/roles/{role_id}')
            
            print(f"  {api['http_method']:6} | {api['api_name']}")
            print(f"    旧路径: {old_path}")
            print(f"    新路径: {new_path}")
            
            # 更新路径
            await conn.execute("""
                UPDATE t_sys_api_endpoints
                SET api_path = $1
                WHERE id = $2
            """, new_path, api['id'])
            
            print(f"    ✅ 已更新\n")
        
        # 3. 验证修复结果
        print("="*80)
        print("3️⃣  验证修复结果")
        print("="*80 + "\n")
        
        # 检查是否还有冲突
        remaining_conflicts = await conn.fetch("""
            SELECT api_path, http_method, COUNT(*) as count
            FROM t_sys_api_endpoints
            GROUP BY api_path, http_method
            HAVING COUNT(*) > 1
        """)
        
        if remaining_conflicts:
            print(f"⚠️  仍有 {len(remaining_conflicts)} 组冲突:\n")
            for conflict in remaining_conflicts:
                print(f"  {conflict['http_method']} {conflict['api_path']} (重复{conflict['count']}次)")
        else:
            print("✅ 没有发现路径冲突")
        
        # 显示修复后的路径
        print("\n" + "="*80)
        print("修复后的API路径")
        print("="*80 + "\n")
        
        fixed_apis = await conn.fetch("""
            SELECT api_path, http_method, api_name
            FROM t_sys_api_endpoints
            WHERE api_path LIKE '/api/v2/departments/{dept_id}%'
               OR api_path LIKE '/api/v2/roles/{role_id}%'
            ORDER BY api_path, http_method
        """)
        
        for api in fixed_apis:
            print(f"{api['http_method']:6} {api['api_path']:50} | {api['api_name']}")
        
        print(f"\n✅ 共修复 {len(dept_apis) + len(role_apis)} 个API路径")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(fix_user_api_paths())
