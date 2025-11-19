"""检查字典菜单的component字段"""
import asyncio
import asyncpg
from app.settings.config import PostgresCredentials

async def check():
    pg = PostgresCredentials()
    conn = await asyncpg.connect(
        host=pg.host,
        port=pg.port,
        user=pg.user,
        password=pg.password,
        database=pg.database
    )
    
    rows = await conn.fetch(
        "SELECT id, name, component, path, menu_type FROM t_sys_menu WHERE name IN ('字典类型', '字典数据')"
    )
    
    print("字典菜单的component字段:")
    for r in rows:
        print(f"  {r['name']}:")
        print(f"    ID: {r['id']}")
        print(f"    Type: {r['menu_type']}")
        print(f"    Component: '{r['component']}'")
        print(f"    Path: '{r['path']}'")
        print()
    
    await conn.close()

asyncio.run(check())
