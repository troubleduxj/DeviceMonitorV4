"""
删除修复路径后产生的重复API
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

async def remove_duplicate_user_apis():
    """删除重复的用户API"""
    print("="*80)
    print("🗑️  删除修复路径后产生的重复API")
    print("="*80)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 查找所有重复的API
        duplicates = await conn.fetch("""
            SELECT api_path, http_method, array_agg(id ORDER BY id) as ids, array_agg(api_name ORDER BY id) as names
            FROM t_sys_api_endpoints
            WHERE api_path LIKE '/api/v2/departments/{dept_id}%'
               OR api_path LIKE '/api/v2/roles/{role_id}%'
            GROUP BY api_path, http_method
            HAVING COUNT(*) > 1
            ORDER BY api_path, http_method
        """)
        
        print(f"\n找到 {len(duplicates)} 组重复的API\n")
        
        deleted_count = 0
        
        for dup in duplicates:
            path = dup['api_path']
            method = dup['http_method']
            ids = dup['ids']
            names = dup['names']
            
            print(f"{method} {path}")
            print(f"  重复数量: {len(ids)}")
            
            # 显示所有重复的API
            for i, (api_id, name) in enumerate(zip(ids, names)):
                print(f"    [{i+1}] ID:{api_id:4} | {name}")
            
            # 保留第一个（通常是原始的），删除其他的
            keep_id = ids[0]
            delete_ids = ids[1:]
            
            print(f"  ✅ 保留: ID {keep_id} | {names[0]}")
            print(f"  🗑️  删除: {len(delete_ids)} 个")
            
            for del_id in delete_ids:
                # 先删除相关的权限记录
                await conn.execute("""
                    DELETE FROM t_sys_role_api
                    WHERE api_id = $1
                """, del_id)
                
                # 删除API
                await conn.execute("""
                    DELETE FROM t_sys_api_endpoints
                    WHERE id = $1
                """, del_id)
                
                deleted_count += 1
                print(f"    ✅ 已删除 ID {del_id}")
            
            print()
        
        # 验证结果
        print("="*80)
        print("验证结果")
        print("="*80 + "\n")
        
        remaining = await conn.fetch("""
            SELECT api_path, http_method, COUNT(*) as count
            FROM t_sys_api_endpoints
            GROUP BY api_path, http_method
            HAVING COUNT(*) > 1
        """)
        
        if remaining:
            print(f"⚠️  仍有 {len(remaining)} 组重复")
            for r in remaining:
                print(f"  {r['http_method']} {r['api_path']} (x{r['count']})")
        else:
            print("✅ 所有重复已清理完成")
        
        print(f"\n✅ 共删除 {deleted_count} 个重复的API")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(remove_duplicate_user_apis())
