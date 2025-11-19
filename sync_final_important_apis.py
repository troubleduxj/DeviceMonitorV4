"""
同步最后几个重要的基础API
"""
import asyncio
import asyncpg
from datetime import datetime

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

# 需要同步的重要API
IMPORTANT_APIS = [
    {
        'api_code': 'post_api_v2_base_logout',
        'api_name': '用户登出',
        'api_path': '/api/v2/base/logout',
        'http_method': 'POST',
        'description': '用户登出，清除token',
        'group_name': '用户认证',
        'version': 'v2'
    },
    {
        'api_code': 'post_api_v2_base_refresh',
        'api_name': '刷新Token',
        'api_path': '/api/v2/base/refresh',
        'http_method': 'POST',
        'description': '刷新访问令牌',
        'group_name': '用户认证',
        'version': 'v2'
    },
    {
        'api_code': 'post_api_v2_init_button_permissions_system_init_button_permissions',
        'api_name': '初始化按钮权限',
        'api_path': '/api/v2/init-button-permissions/system/init-button-permissions',
        'http_method': 'POST',
        'description': '系统初始化按钮权限',
        'group_name': '系统初始化',
        'version': 'v2'
    },
    {
        'api_code': 'get_root',
        'api_name': '健康检查',
        'api_path': '/',
        'http_method': 'GET',
        'description': '系统根路径健康检查',
        'group_name': '健康检查',
        'version': 'v1'
    },
    {
        'api_code': 'post_api_v1_base_access_token',
        'api_name': '获取访问令牌',
        'api_path': '/api/v1/base/access_token',
        'http_method': 'POST',
        'description': 'V1版本获取访问令牌',
        'group_name': '用户认证',
        'version': 'v1'
    },
]

async def sync_final_apis():
    """同步最后的重要API"""
    print("="*80)
    print("🚀 同步最后的重要基础API")
    print("="*80)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 获取已存在的API
        existing = await conn.fetch("SELECT api_path, http_method FROM t_sys_api_endpoints")
        existing_set = {(row['api_path'], row['http_method']) for row in existing}
        
        created = 0
        skipped = 0
        
        for api in IMPORTANT_APIS:
            # 检查是否已存在
            if (api['api_path'], api['http_method']) in existing_set:
                print(f"⏭️  已存在: {api['http_method']:6} {api['api_path']}")
                skipped += 1
                continue
            
            # 获取或创建分组
            group = await conn.fetchrow("""
                SELECT id FROM t_sys_api_groups WHERE group_name = $1
            """, api['group_name'])
            
            if not group:
                # 创建分组
                group_code = api['group_name'].replace(' ', '_').lower()
                group = await conn.fetchrow("""
                    INSERT INTO t_sys_api_groups (group_code, group_name, description, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                """, group_code, api['group_name'], f"{api['group_name']}相关API", datetime.now(), datetime.now())
                print(f"✅ 创建分组: {api['group_name']} (ID: {group['id']})")
            
            group_id = group['id']
            
            # 插入API
            try:
                await conn.execute("""
                    INSERT INTO t_sys_api_endpoints (
                        api_code, api_name, api_path, http_method,
                        description, version, group_id, is_public,
                        status, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                    api['api_code'],
                    api['api_name'],
                    api['api_path'],
                    api['http_method'],
                    api['description'],
                    api['version'],
                    group_id,
                    False,
                    'active',
                    datetime.now(),
                    datetime.now()
                )
                print(f"✅ {api['http_method']:6} {api['api_path']} - {api['api_name']}")
                created += 1
            except Exception as e:
                print(f"❌ 失败: {api['http_method']} {api['api_path']} - {str(e)[:100]}")
        
        print(f"\n{'='*80}")
        print(f"📊 总计")
        print(f"{'='*80}")
        print(f"新创建: {created}")
        print(f"已跳过: {skipped}")
        print(f"{'='*80}")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(sync_final_apis())
