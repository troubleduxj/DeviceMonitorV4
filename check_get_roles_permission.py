"""
检查GET /api/v2/roles权限
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('.env')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'devicemonitor'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

def check_get_roles_permission():
    """检查GET /api/v2/roles权限"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("检查 GET /api/v2/roles 权限")
        print("=" * 80)
        
        # 查找API
        cursor.execute("""
            SELECT id, api_path, http_method, api_name
            FROM t_sys_api_endpoints
            WHERE api_path = '/api/v2/roles' AND http_method = 'GET';
        """)
        
        api = cursor.fetchone()
        if api:
            api_id, api_path, http_method, api_name = api
            print(f"\n✓ API存在:")
            print(f"  ID: {api_id}")
            print(f"  路径: {http_method} {api_path}")
            print(f"  名称: {api_name}")
            
            # 检查是否已授权给管理员角色
            cursor.execute("""
                SELECT COUNT(*)
                FROM t_sys_role_api
                WHERE role_id = 1 AND api_id = %s;
            """, (api_id,))
            
            is_granted = cursor.fetchone()[0] > 0
            
            if is_granted:
                print(f"\n✅ 已授权给管理员角色")
            else:
                print(f"\n❌ 未授权给管理员角色")
                print(f"\n修复SQL:")
                print(f"INSERT INTO t_sys_role_api (role_id, api_id) VALUES (1, {api_id});")
                
                # 执行修复
                print(f"\n是否执行修复？(y/n)")
                # 自动执行
                cursor.execute("""
                    INSERT INTO t_sys_role_api (role_id, api_id)
                    VALUES (1, %s)
                    ON CONFLICT DO NOTHING;
                """, (api_id,))
                conn.commit()
                print(f"✓ 已授权")
        else:
            print(f"\n❌ API不存在于数据库中")
            print(f"  需要的API: GET /api/v2/roles")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_get_roles_permission()
