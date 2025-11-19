"""
检查按钮权限配置
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

def check_button_permissions():
    """检查按钮权限配置"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("检查按钮权限配置")
        print("=" * 80)
        
        # 查询所有按钮类型的菜单
        cursor.execute("""
            SELECT 
                id,
                name,
                menu_type,
                parent_id,
                perms,
                path,
                component
            FROM t_sys_menu
            WHERE menu_type = 'button'
            ORDER BY parent_id, order_num
            LIMIT 20;
        """)
        
        buttons = cursor.fetchall()
        
        print(f"\n找到 {len(buttons)} 个按钮权限（显示前20个）：\n")
        
        for id, name, menu_type, parent_id, perms, path, component in buttons:
            print(f"ID: {id}")
            print(f"  名称: {name}")
            print(f"  类型: {menu_type}")
            print(f"  父ID: {parent_id}")
            print(f"  权限标识 (perms): {perms}")
            print(f"  路径: {path}")
            print(f"  组件: {component}")
            print()
        
        # 检查管理员角色的权限
        print("=" * 80)
        print("检查管理员角色的权限")
        print("=" * 80)
        
        # 查找管理员角色
        cursor.execute("""
            SELECT id, role_name
            FROM t_sys_role
            WHERE role_name LIKE '%管理员%'
            LIMIT 5;
        """)
        
        roles = cursor.fetchall()
        print(f"\n找到 {len(roles)} 个管理员角色：\n")
        
        for role_id, role_name in roles:
            print(f"角色: {role_name} (ID: {role_id})")
            
            # 查询该角色的菜单权限
            cursor.execute("""
                SELECT COUNT(*)
                FROM t_sys_role_menu
                WHERE role_id = %s;
            """, (role_id,))
            menu_count = cursor.fetchone()[0]
            print(f"  菜单权限数量: {menu_count}")
            
            # 查询该角色的API权限
            cursor.execute("""
                SELECT COUNT(*)
                FROM t_sys_role_api
                WHERE role_id = %s;
            """, (role_id,))
            api_count = cursor.fetchone()[0]
            print(f"  API权限数量: {api_count}")
            
            # 查询该角色的按钮权限（通过菜单）
            cursor.execute("""
                SELECT m.id, m.name, m.perms
                FROM t_sys_menu m
                INNER JOIN t_sys_role_menu rm ON m.id = rm.menu_id
                WHERE rm.role_id = %s AND m.menu_type = 'button'
                LIMIT 10;
            """, (role_id,))
            
            button_perms = cursor.fetchall()
            print(f"  按钮权限数量: {len(button_perms)}")
            if button_perms:
                print(f"  前10个按钮权限:")
                for btn_id, btn_name, btn_perms in button_perms:
                    print(f"    - {btn_name}: {btn_perms}")
            print()
        
        # 检查hlzg_admin用户
        print("=" * 80)
        print("检查hlzg_admin用户")
        print("=" * 80)
        
        cursor.execute("""
            SELECT id, username
            FROM t_sys_user
            WHERE username = 'hlzg_admin';
        """)
        
        user = cursor.fetchone()
        if user:
            user_id, username = user
            print(f"\n用户: {username} (ID: {user_id})")
            
            # 查询用户的角色
            cursor.execute("""
                SELECT r.id, r.role_name
                FROM t_sys_role r
                INNER JOIN t_sys_user_role ur ON r.id = ur.role_id
                WHERE ur.user_id = %s;
            """, (user_id,))
            
            user_roles = cursor.fetchall()
            print(f"  角色数量: {len(user_roles)}")
            for role_id, role_name in user_roles:
                print(f"    - {role_name} (ID: {role_id})")
        else:
            print("\n未找到hlzg_admin用户")
        
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
    check_button_permissions()
