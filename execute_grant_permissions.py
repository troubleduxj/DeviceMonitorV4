"""
执行SQL脚本为管理员角色授权按钮权限
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

def execute_grant_permissions():
    """执行授权脚本"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("为管理员角色授权按钮权限")
        print("=" * 80)
        
        # 1. 查看当前按钮权限数量
        print("\n1. 当前管理员角色的按钮权限数量:")
        cursor.execute("""
            SELECT COUNT(*) as button_count
            FROM t_sys_menu m
            INNER JOIN t_sys_role_menu rm ON m.id = rm.menu_id
            WHERE rm.role_id = 1 AND m.menu_type = 'button';
        """)
        current_count = cursor.fetchone()[0]
        print(f"   当前: {current_count} 个")
        
        # 2. 查看所有可用的按钮权限
        cursor.execute("""
            SELECT COUNT(*)
            FROM t_sys_menu
            WHERE menu_type = 'button';
        """)
        total_buttons = cursor.fetchone()[0]
        print(f"   总共: {total_buttons} 个按钮权限")
        
        # 3. 执行授权
        print("\n2. 执行授权...")
        cursor.execute("""
            INSERT INTO t_sys_role_menu (role_id, menu_id)
            SELECT 1, id
            FROM t_sys_menu
            WHERE menu_type = 'button'
            AND id NOT IN (
                SELECT menu_id 
                FROM t_sys_role_menu 
                WHERE role_id = 1
            );
        """)
        
        added_count = cursor.rowcount
        print(f"   ✓ 新增 {added_count} 个按钮权限")
        
        # 提交事务
        conn.commit()
        
        # 4. 验证结果
        print("\n3. 验证授权结果:")
        cursor.execute("""
            SELECT COUNT(*) as button_count
            FROM t_sys_menu m
            INNER JOIN t_sys_role_menu rm ON m.id = rm.menu_id
            WHERE rm.role_id = 1 AND m.menu_type = 'button';
        """)
        new_count = cursor.fetchone()[0]
        print(f"   授权后: {new_count} 个")
        
        # 5. 显示部分已授权的按钮权限
        print("\n4. 已授权的按钮权限（前10个）:")
        cursor.execute("""
            SELECT 
                m.id,
                m.name,
                m.perms,
                pm.name as parent_menu_name
            FROM t_sys_menu m
            INNER JOIN t_sys_role_menu rm ON m.id = rm.menu_id
            LEFT JOIN t_sys_menu pm ON m.parent_id = pm.id
            WHERE rm.role_id = 1 AND m.menu_type = 'button'
            ORDER BY m.parent_id, m.order_num
            LIMIT 10;
        """)
        
        buttons = cursor.fetchall()
        for id, name, perms, parent_name in buttons:
            print(f"   ✓ {name} ({parent_name})")
            print(f"     perms: {perms}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("授权完成！")
        print("=" * 80)
        print("\n⚠️  重要提示：")
        print("1. 用户需要重新登录才能获取新的权限")
        print("2. 如果后端服务已修改，需要重启后端服务")
        print("\n")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    execute_grant_permissions()
