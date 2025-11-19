"""
验证字典菜单配置的简单脚本
直接使用psycopg2连接数据库，避免Tortoise依赖问题
"""
import os
import psycopg2
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env')

# 数据库连接配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'devicemonitor'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

def check_dict_menus():
    """检查字典相关菜单的配置"""
    try:
        # 连接数据库
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("字典菜单配置检查")
        print("=" * 80)
        
        # 查询字典相关菜单
        query = """
        SELECT 
            id, 
            name, 
            menu_type, 
            parent_id, 
            order_num,
            path,
            component
        FROM t_sys_menu
        WHERE name LIKE '%字典%'
        ORDER BY parent_id, order_num;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"\n找到 {len(results)} 个字典相关菜单项：\n")
        
        for row in results:
            id, name, menu_type, parent_id, order_num, path, component = row
            print(f"ID: {id:3d} | 名称: {name:20s} | 类型: {menu_type:10s} | 父ID: {parent_id:3d} | 排序: {order_num:3d}")
            if path:
                print(f"       路径: {path}")
            if component:
                print(f"       组件: {component}")
            print()
        
        # 检查父菜单
        print("\n" + "=" * 80)
        print("检查父菜单（系统管理）")
        print("=" * 80)
        
        parent_query = """
        SELECT id, name, menu_type, order_num
        FROM t_sys_menu
        WHERE id IN (
            SELECT DISTINCT parent_id 
            FROM t_sys_menu 
            WHERE name LIKE '%字典%' AND parent_id IS NOT NULL
        );
        """
        
        cursor.execute(parent_query)
        parent_results = cursor.fetchall()
        
        for row in parent_results:
            id, name, menu_type, order_num = row
            print(f"父菜单 ID: {id} | 名称: {name} | 类型: {menu_type} | 排序: {order_num}")
        
        # 统计菜单总数
        print("\n" + "=" * 80)
        print("菜单总数统计")
        print("=" * 80)
        
        count_query = "SELECT COUNT(*) FROM t_sys_menu;"
        cursor.execute(count_query)
        total_count = cursor.fetchone()[0]
        print(f"数据库中总共有 {total_count} 个菜单项")
        
        # 检查order_num最大值
        max_order_query = "SELECT MAX(order_num) FROM t_sys_menu;"
        cursor.execute(max_order_query)
        max_order = cursor.fetchone()[0]
        print(f"最大的 order_num 值: {max_order}")
        
        # 检查字典菜单的order_num
        dict_order_query = """
        SELECT name, order_num 
        FROM t_sys_menu 
        WHERE name IN ('字典类型', '字典数据')
        ORDER BY order_num;
        """
        cursor.execute(dict_order_query)
        dict_orders = cursor.fetchall()
        
        print("\n字典菜单的排序号：")
        for name, order_num in dict_orders:
            print(f"  {name}: {order_num}")
            if order_num > 100:
                print(f"    ⚠️  警告：排序号 {order_num} 超过了 100，如果前端使用 page_size=100 将无法获取此菜单！")
        
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
    check_dict_menus()
