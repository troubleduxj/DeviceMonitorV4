"""
测试角色菜单权限更新
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

def test_role_menu_permissions():
    """测试角色菜单权限"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("测试角色菜单权限")
        print("=" * 80)
        
        # 查询管理员角色的所有菜单权限
        cursor.execute("""
            SELECT 
                m.id,
                m.name,
                m.menu_type,
                m.parent_id,
                m.perms
            FROM t_sys_menu m
            INNER JOIN t_sys_role_menu rm ON m.id = rm.menu_id
            WHERE rm.role_id = 1
            ORDER BY m.menu_type, m.parent_id, m.order_num;
        """)
        
        menus = cursor.fetchall()
        
        print(f"\n管理员角色的菜单权限（共{len(menus)}个）：\n")
        
        # 按类型分组
        catalogs = []
        menu_items = []
        buttons = []
        
        for id, name, menu_type, parent_id, perms in menus:
            if menu_type == 'catalog':
                catalogs.append((id, name, parent_id, perms))
            elif menu_type == 'menu':
                menu_items.append((id, name, parent_id, perms))
            elif menu_type == 'button':
                buttons.append((id, name, parent_id, perms))
        
        print(f"目录 (catalog): {len(catalogs)}个")
        for id, name, parent_id, perms in catalogs[:5]:
            print(f"  - {name} (ID: {id}, 父ID: {parent_id})")
        
        print(f"\n菜单 (menu): {len(menu_items)}个")
        for id, name, parent_id, perms in menu_items[:5]:
            print(f"  - {name} (ID: {id}, 父ID: {parent_id})")
        
        print(f"\n按钮 (button): {len(buttons)}个")
        if buttons:
            for id, name, parent_id, perms in buttons[:10]:
                print(f"  - {name} (ID: {id}, 父ID: {parent_id}, perms: {perms})")
        else:
            print("  ⚠️  没有按钮权限！")
        
        # 查询用户管理菜单下的所有按钮
        print("\n" + "=" * 80)
        print("用户管理菜单下的按钮权限")
        print("=" * 80)
        
        cursor.execute("""
            SELECT 
                id,
                name,
                perms,
                order_num
            FROM t_sys_menu
            WHERE parent_id = 2 AND menu_type = 'button'
            ORDER BY order_num;
        """)
        
        user_buttons = cursor.fetchall()
        print(f"\n用户管理下有 {len(user_buttons)} 个按钮：\n")
        
        for id, name, perms, order_num in user_buttons:
            # 检查是否在管理员角色的权限中
            cursor.execute("""
                SELECT COUNT(*)
                FROM t_sys_role_menu
                WHERE role_id = 1 AND menu_id = %s;
            """, (id,))
            has_perm = cursor.fetchone()[0] > 0
            
            status = "✅ 已授权" if has_perm else "❌ 未授权"
            print(f"  {status} - {name} (ID: {id})")
            print(f"           perms: {perms}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("测试完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_role_menu_permissions()
