"""
修复设备维护管理分组中重复的API
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

async def fix_duplicate_apis():
    """修复重复的API"""
    print("="*80)
    print("🔧 修复设备维护管理分组中重复的API")
    print("="*80)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 查找重复的维修记录API
        print("\n🔍 查找重复的维修记录API...\n")
        
        duplicate_apis = await conn.fetch("""
            SELECT 
                a.id,
                a.api_code,
                a.api_name,
                a.api_path,
                a.http_method,
                a.description
            FROM t_sys_api_endpoints a
            WHERE a.api_path LIKE '%repair-records/{record_id}%'
            ORDER BY a.http_method
        """)
        
        print(f"找到 {len(duplicate_apis)} 个使用 {{record_id}} 的API:\n")
        
        for api in duplicate_apis:
            print(f"  ID: {api['id']}")
            print(f"  方法: {api['http_method']}")
            print(f"  路径: {api['api_path']}")
            print(f"  名称: {api['api_name']}")
            print(f"  描述: {api['description']}")
            print()
        
        # 查找对应的使用 {id} 的API
        print("🔍 查找对应的使用 {id} 的API...\n")
        
        original_apis = await conn.fetch("""
            SELECT 
                a.id,
                a.api_code,
                a.api_name,
                a.api_path,
                a.http_method,
                a.description
            FROM t_sys_api_endpoints a
            WHERE a.api_path = '/api/v2/device/maintenance/repair-records/{id}'
            ORDER BY a.http_method
        """)
        
        print(f"找到 {len(original_apis)} 个使用 {{id}} 的API:\n")
        
        for api in original_apis:
            print(f"  ID: {api['id']}")
            print(f"  方法: {api['http_method']}")
            print(f"  路径: {api['api_path']}")
            print(f"  名称: {api['api_name']}")
            print(f"  描述: {api['description']}")
            print()
        
        # 询问是否删除重复的API
        print("="*80)
        print("⚠️  建议操作:")
        print("="*80)
        print("\n保留使用 {id} 的API（更简洁、更标准）")
        print("删除使用 {record_id} 的API（重复、冗余）\n")
        
        confirm = input("确认删除重复的API? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            print("\n🗑️  开始删除重复的API...\n")
            
            deleted_count = 0
            for api in duplicate_apis:
                try:
                    # 先检查是否有角色使用这个API
                    role_count = await conn.fetchval("""
                        SELECT COUNT(*) FROM t_sys_role_api
                        WHERE api_id = $1
                    """, api['id'])
                    
                    if role_count > 0:
                        print(f"  ⚠️  API {api['id']} 被 {role_count} 个角色使用，需要先迁移权限")
                        
                        # 找到对应的原始API
                        original_api = next(
                            (a for a in original_apis if a['http_method'] == api['http_method']),
                            None
                        )
                        
                        if original_api:
                            # 迁移权限
                            await conn.execute("""
                                UPDATE t_sys_role_api
                                SET api_id = $1
                                WHERE api_id = $2
                                AND NOT EXISTS (
                                    SELECT 1 FROM t_sys_role_api
                                    WHERE role_id = t_sys_role_api.role_id
                                    AND api_id = $1
                                )
                            """, original_api['id'], api['id'])
                            
                            # 删除重复的权限记录
                            await conn.execute("""
                                DELETE FROM t_sys_role_api
                                WHERE api_id = $1
                            """, api['id'])
                            
                            print(f"  ✅ 已迁移权限到 API {original_api['id']}")
                    
                    # 删除API
                    await conn.execute("""
                        DELETE FROM t_sys_api_endpoints
                        WHERE id = $1
                    """, api['id'])
                    
                    print(f"  ✅ 已删除: {api['http_method']} {api['api_path']} (ID: {api['id']})")
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"  ❌ 删除失败: {api['id']} - {str(e)}")
            
            print(f"\n✅ 成功删除 {deleted_count} 个重复的API")
            
        else:
            print("\n❌ 已取消操作")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(fix_duplicate_apis())
