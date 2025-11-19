"""使用SQL直接检查字典相关菜单的层级结构"""
import asyncio
import asyncpg
from dotenv import load_dotenv
from app.settings.config import PostgresCredentials

load_dotenv('.env')

async def check_dict_menus():
    """检查字典相关菜单"""
    pg_creds = PostgresCredentials()
    
    # 连接数据库
    conn = await asyncpg.connect(
        host=pg_creds.host,
        port=pg_creds.port,
        user=pg_creds.user,
        password=pg_creds.password,
        database=pg_creds.database
    )
    
    print("=" * 80)
    print("检查字典相关菜单的层级结构")
    print("=" * 80)
    
    # 查找所有字典相关的菜单
    query = """
        SELECT id, name, menu_type, parent_id, order_num, perms
        FROM t_sys_menu
        WHERE name LIKE '%字典%'
        ORDER BY parent_id, order_num
    """
    
    rows = await conn.fetch(query)
    
    print(f"\n找到 {len(rows)} 个字典相关菜单:\n")
    
    for row in rows:
        parent_name = "无"
        if row['parent_id'] and row['parent_id'] > 0:
            parent_query = "SELECT name FROM t_sys_menu WHERE id = $1"
            parent_row = await conn.fetchrow(parent_query, row['parent_id'])
            if parent_row:
                parent_name = parent_row['name']
        
        print(f"ID: {row['id']:4d} | 名称: {row['name']:20s} | 类型: {row['menu_type']:10s} | "
              f"父菜单ID: {row['parent_id'] or 0:4d} | 父菜单: {parent_name:20s} | "
              f"排序: {row['order_num'] or 0:3d}")
        if row['perms']:
            print(f"       权限: {row['perms']}")
    
    # 查找字典类型和字典数据菜单
    print("\n" + "=" * 80)
    print("查找字典类型和字典数据菜单")
    print("=" * 80 + "\n")
    
    dict_type_query = "SELECT * FROM t_sys_menu WHERE name = '字典类型' AND menu_type = 'menu'"
    dict_type_row = await conn.fetchrow(dict_type_query)
    
    if dict_type_row:
        print(f"字典类型菜单: ID={dict_type_row['id']}, Parent={dict_type_row['parent_id']}")
        # 查找其子菜单
        children_query = "SELECT * FROM t_sys_menu WHERE parent_id = $1 ORDER BY order_num"
        children = await conn.fetch(children_query, dict_type_row['id'])
        print(f"  子菜单数量: {len(children)}")
        for child in children:
            print(f"    - {child['name']} (ID: {child['id']}, Type: {child['menu_type']}, Order: {child['order_num']})")
    else:
        print("未找到'字典类型'菜单")
    
    print()
    
    dict_data_query = "SELECT * FROM t_sys_menu WHERE name = '字典数据' AND menu_type = 'menu'"
    dict_data_row = await conn.fetchrow(dict_data_query)
    
    if dict_data_row:
        print(f"字典数据菜单: ID={dict_data_row['id']}, Parent={dict_data_row['parent_id']}")
        # 查找其子菜单
        children_query = "SELECT * FROM t_sys_menu WHERE parent_id = $1 ORDER BY order_num"
        children = await conn.fetch(children_query, dict_data_row['id'])
        print(f"  子菜单数量: {len(children)}")
        for child in children:
            print(f"    - {child['name']} (ID: {child['id']}, Type: {child['menu_type']}, Order: {child['order_num']})")
    else:
        print("未找到'字典数据'菜单")
    
    # 查找所有顶层的字典按钮权限（parent_id为0或NULL）
    print("\n" + "=" * 80)
    print("查找顶层的字典按钮权限（这些应该有父菜单）")
    print("=" * 80 + "\n")
    
    orphan_query = """
        SELECT * FROM t_sys_menu
        WHERE name LIKE '%字典%'
        AND menu_type = 'button'
        AND (parent_id IS NULL OR parent_id = 0)
        ORDER BY order_num
    """
    orphan_buttons = await conn.fetch(orphan_query)
    
    if orphan_buttons:
        print(f"找到 {len(orphan_buttons)} 个没有父菜单的字典按钮权限:")
        for btn in orphan_buttons:
            print(f"  - {btn['name']} (ID: {btn['id']}, Perms: {btn['perms']})")
    else:
        print("没有找到孤立的字典按钮权限")
    
    await conn.close()

if __name__ == '__main__':
    asyncio.run(check_dict_menus())
