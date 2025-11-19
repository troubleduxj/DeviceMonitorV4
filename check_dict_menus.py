"""检查字典相关菜单的层级结构"""
import asyncio
import os
from dotenv import load_dotenv
from tortoise import Tortoise
from app.models.admin import Menu

load_dotenv('.env')

async def check_dict_menus():
    """检查字典相关菜单"""
    # 初始化数据库连接
    from app.settings.config import PostgresCredentials
    
    pg_creds = PostgresCredentials()
    db_url = f"postgres://{pg_creds.user}:{pg_creds.password}@{pg_creds.host}:{pg_creds.port}/{pg_creds.database}"
    
    await Tortoise.init(
        db_url=db_url,
        modules={'models': ['app.models.admin']}
    )
    
    print("=" * 80)
    print("检查字典相关菜单的层级结构")
    print("=" * 80)
    
    # 查找所有字典相关的菜单
    dict_menus = await Menu.filter(name__icontains='字典').order_by('parent_id', 'order_num')
    
    print(f"\n找到 {len(dict_menus)} 个字典相关菜单:\n")
    
    for menu in dict_menus:
        parent_name = "无"
        if menu.parent_id and menu.parent_id > 0:
            parent = await Menu.get_or_none(id=menu.parent_id)
            if parent:
                parent_name = parent.name
        
        print(f"ID: {menu.id:4d} | 名称: {menu.name:20s} | 类型: {menu.menu_type:10s} | "
              f"父菜单ID: {menu.parent_id or 0:4d} | 父菜单: {parent_name:20s} | "
              f"排序: {menu.order_num or 0:3d}")
    
    # 查找字典类型和字典数据菜单
    print("\n" + "=" * 80)
    print("查找字典类型和字典数据菜单")
    print("=" * 80 + "\n")
    
    dict_type_menu = await Menu.filter(name='字典类型', menu_type='menu').first()
    dict_data_menu = await Menu.filter(name='字典数据', menu_type='menu').first()
    
    if dict_type_menu:
        print(f"字典类型菜单: ID={dict_type_menu.id}, Parent={dict_type_menu.parent_id}")
        # 查找其子菜单
        children = await Menu.filter(parent_id=dict_type_menu.id).order_by('order_num')
        print(f"  子菜单数量: {len(children)}")
        for child in children:
            print(f"    - {child.name} (ID: {child.id}, Type: {child.menu_type}, Order: {child.order_num})")
    else:
        print("未找到'字典类型'菜单")
    
    print()
    
    if dict_data_menu:
        print(f"字典数据菜单: ID={dict_data_menu.id}, Parent={dict_data_menu.parent_id}")
        # 查找其子菜单
        children = await Menu.filter(parent_id=dict_data_menu.id).order_by('order_num')
        print(f"  子菜单数量: {len(children)}")
        for child in children:
            print(f"    - {child.name} (ID: {child.id}, Type: {child.menu_type}, Order: {child.order_num})")
    else:
        print("未找到'字典数据'菜单")
    
    # 查找所有顶层的字典按钮权限（parent_id为0或NULL）
    print("\n" + "=" * 80)
    print("查找顶层的字典按钮权限（这些应该有父菜单）")
    print("=" * 80 + "\n")
    
    orphan_buttons = await Menu.filter(
        name__icontains='字典',
        menu_type='button',
        parent_id__isnull=True
    ).order_by('order_num')
    
    if orphan_buttons:
        print(f"找到 {len(orphan_buttons)} 个没有父菜单的字典按钮权限:")
        for btn in orphan_buttons:
            print(f"  - {btn.name} (ID: {btn.id}, Perms: {btn.perms})")
    else:
        print("没有找到孤立的字典按钮权限")
    
    # 也检查parent_id=0的情况
    orphan_buttons_zero = await Menu.filter(
        name__icontains='字典',
        menu_type='button',
        parent_id=0
    ).order_by('order_num')
    
    if orphan_buttons_zero:
        print(f"\n找到 {len(orphan_buttons_zero)} 个parent_id=0的字典按钮权限:")
        for btn in orphan_buttons_zero:
            print(f"  - {btn.name} (ID: {btn.id}, Perms: {btn.perms})")
    
    await Tortoise.close_connections()

if __name__ == '__main__':
    asyncio.run(check_dict_menus())
