"""
删除或隐藏测试和系统页面菜单
使用 Tortoise ORM 连接数据库
"""
import asyncio
from tortoise import Tortoise

# 数据库配置（从 config.py 读取）
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'device_monitor',
    'user': 'postgres',
    'password': '123456'
}


async def remove_test_menus():
    """删除或隐藏测试菜单"""
    
    # 初始化数据库连接
    await Tortoise.init(
        db_url=f"postgres://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}",
        modules={'models': ['app.models.admin']}
    )
    
    try:
        from app.models.admin import Menu
        
        # 需要删除的菜单名称
        test_menu_names = [
            '403',
            '404',
            '登录页',
            'Login',
            '权限调试',
            '简单测试',
            '权限测试',
            '权限组件测试',
            'PermissionDebug',
            'SimpleTest',
            'TestPermission',
            'TestComponents'
        ]
        
        print('开始查找测试菜单...\n')
        
        # 查找所有匹配的菜单
        test_menus = await Menu.filter(name__in=test_menu_names).all()
        
        if not test_menus:
            print('未找到需要删除的测试菜单')
            return
        
        print(f'找到 {len(test_menus)} 个测试菜单:\n')
        for menu in test_menus:
            print(f'  - {menu.name} (ID: {menu.id}, Path: {menu.path})')
        
        # 询问用户操作
        print('\n请选择操作:')
        print('1. 隐藏这些菜单 (推荐 - 可恢复)')
        print('2. 删除这些菜单 (不可恢复)')
        print('3. 取消操作')
        
        choice = input('\n请输入选项 (1/2/3): ').strip()
        
        if choice == '1':
            # 隐藏菜单
            for menu in test_menus:
                menu.is_hidden = True
                await menu.save()
                print(f'隐藏: {menu.name}')
            print(f'\n成功隐藏 {len(test_menus)} 个菜单')
            
        elif choice == '2':
            # 删除菜单
            confirm = input('\n确认删除？这些菜单将被永久删除！(yes/no): ').strip().lower()
            if confirm == 'yes':
                for menu in test_menus:
                    await menu.delete()
                    print(f'删除: {menu.name}')
                print(f'\n成功删除 {len(test_menus)} 个菜单')
            else:
                print('取消删除操作')
        else:
            print('取消操作')
    
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(remove_test_menus())

