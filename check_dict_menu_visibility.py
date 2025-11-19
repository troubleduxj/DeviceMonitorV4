"""检查字典类型和字典数据菜单的可见性"""
import asyncio
import asyncpg
from dotenv import load_dotenv
from app.settings.config import PostgresCredentials

load_dotenv('.env')

async def check_menu_visibility():
    """检查菜单可见性"""
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
    print("检查字典类型和字典数据菜单的状态")
    print("=" * 80 + "\n")
    
    # 查询字典类型和字典数据菜单
    query = """
        SELECT id, name, menu_type, parent_id, visible, status, order_num
        FROM t_sys_menu
        WHERE name IN ('字典类型', '字典数据')
        ORDER BY id
    """
    
    rows = await conn.fetch(query)
    
    if rows:
        print(f"找到 {len(rows)} 个菜单:\n")
        for row in rows:
            print(f"菜单: {row['name']}")
            print(f"  ID: {row['id']}")
            print(f"  类型: {row['menu_type']}")
            print(f"  父菜单ID: {row['parent_id']}")
            print(f"  visible: {row['visible']}")
            print(f"  status: {row['status']}")
            print(f"  排序: {row['order_num']}")
            print()
    else:
        print("未找到字典类型和字典数据菜单！")
    
    # 检查是否有其他隐藏的菜单
    print("=" * 80)
    print("检查所有隐藏或禁用的菜单")
    print("=" * 80 + "\n")
    
    hidden_query = """
        SELECT id, name, menu_type, visible, status
        FROM t_sys_menu
        WHERE visible = false OR status = false
        ORDER BY id
    """
    
    hidden_rows = await conn.fetch(hidden_query)
    
    if hidden_rows:
        print(f"找到 {len(hidden_rows)} 个隐藏或禁用的菜单:\n")
        for row in hidden_rows:
            print(f"  - {row['name']} (ID: {row['id']}, Type: {row['menu_type']}, "
                  f"visible: {row['visible']}, status: {row['status']})")
    else:
        print("没有找到隐藏或禁用的菜单")
    
    await conn.close()

if __name__ == '__main__':
    asyncio.run(check_menu_visibility())
