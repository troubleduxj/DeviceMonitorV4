"""
检查管理员角色的角色管理相关权限
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

def check_role_permissions():
    """检查角色管理相关权限"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("检查管理员角色的角色管理相关权限")
        print("=" * 80)
        
        # 1. 检查角色管理菜单权限
        print("\n1. 角色管理菜单权限:")
        cursor.execute("""
            SELECT m.id, m.name, m.menu_type, m.perms
            FROM t_sys_menu m
            INNER JOIN t_sys_role_menu rm ON m.id = rm.menu_id
            WHERE rm.role_id = 1 
            AND (m.name LIKE '%角色%' OR m.parent_id = 3)
            ORDER BY m.menu_type, m.order_num;
        """)
        
        role_menus = cursor.fetchall()
        if role_menus:
            for id, name, menu_type, perms in role_menus:
                print(f"   ✓ {name} (类型: {menu_type}, perms: {perms})")
        else:
            print("   ❌ 没有角色管理相关的菜单权限")
        
        # 2. 检查角色管理相关的API权限
        print("\n2. 角色管理相关的API权限:")
        cursor.execute("""
            SELECT ae.id, ae.api_path, ae.http_method, ae.api_name
            FROM t_sys_api_endpoints ae
            INNER JOIN t_sys_role_api ra ON ae.id = ra.api_id
            WHERE ra.role_id = 1
            AND ae.api_path LIKE '%/roles%'
            ORDER BY ae.api_path, ae.http_method;
        """)
        
        role_apis = cursor.fetchall()
        if role_apis:
            for id, api_path, http_method, api_name in role_apis:
                print(f"   ✓ {http_method} {api_path}")
        else:
            print("   ❌ 没有角色管理相关的API权限")
        
        # 3. 检查关键的GET /api/v2/roles权限
        print("\n3. 检查关键权限 'GET /api/v2/roles':")
        cursor.execute("""
            SELECT ae.id, ae.api_path, ae.http_method
            FROM t_sys_api_endpoints ae
            WHERE ae.api_path = '/api/v2/roles' AND ae.http_method = 'GET';
        """)
        
        get_roles_api = cursor.fetchone()
        if get_roles_api:
            api_id, api_path, http_method = get_roles_api
            print(f"   API存在: ID={api_id}, {http_method} {api_path}")
            
            # 检查是否已授权
            cursor.execute("""
                SELECT COUNT(*)
                FROM t_sys_role_api
                WHERE role_id = 1 AND api_id = %s;
            """, (api_id,))
            
            is_granted = cursor.fetchone()[0] > 0
            if is_granted:
                print(f"   ✅ 已授权给管理员角色")
            else:
                print(f"   ❌ 未授权给管理员角色")
                print(f"\n   修复SQL:")
                print(f"   INSERT INTO t_sys_role_api (role_id, api_id) VALUES (1, {api_id});")
        else:
            print("   ❌ API不存在于数据库中")
        
        # 4. 列出所有角色相关的API
        print("\n4. 数据库中所有角色相关的API:")
        cursor.execute("""
            SELECT id, api_path, http_method, api_name
            FROM t_sys_api_endpoints
            WHERE api_path LIKE '%/roles%'
            ORDER BY api_path, http_method;
        """)
        
        all_role_apis = cursor.fetchall()
        print(f"   共 {len(all_role_apis)} 个API:")
        for id, api_path, http_method, api_name in all_role_apis[:20]:
            # 检查是否已授权
            cursor.execute("""
                SELECT COUNT(*)
                FROM t_sys_role_api
                WHERE role_id = 1 AND api_id = %s;
            """, (id,))
            is_granted = cursor.fetchone()[0] > 0
            status = "✅" if is_granted else "❌"
            print(f"   {status} {http_method:6s} {api_path}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("检查完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_role_permissions()
