"""
测试角色权限更新API
用于诊断500错误
"""
import asyncio
import sys
from tortoise import Tortoise
from app.settings.config import PostgresCredentials
from app.models.admin import Role, Menu, SysApiEndpoint

async def test_update_permissions():
    """测试更新角色权限"""
    try:
        # 初始化数据库连接
        postgres_creds = PostgresCredentials()
        await Tortoise.init(
            db_url=postgres_creds.DATABASE_URL,
            modules={'models': ['app.models.admin']}
        )
        
        print("=" * 80)
        print("测试角色权限更新")
        print("=" * 80)
        
        # 获取测试角色（ID=3）
        role = await Role.get_or_none(id=3)
        if not role:
            print("错误：找不到ID为3的角色")
            return
        
        print(f"\n角色信息：")
        print(f"  ID: {role.id}")
        print(f"  名称: {role.role_name}")
        print(f"  备注: {role.remark}")
        
        # 获取当前权限
        current_menus = await role.menus.all()
        current_apis = await role.apis.all()
        
        print(f"\n当前权限：")
        print(f"  菜单权限数量: {len(current_menus)}")
        print(f"  API权限数量: {len(current_apis)}")
        
        # 测试数据
        test_menu_ids = [1, 2, 3]  # 测试菜单ID
        test_api_ids = [1, 2, 3]   # 测试API ID
        
        print(f"\n测试数据：")
        print(f"  菜单ID: {test_menu_ids}")
        print(f"  API ID: {test_api_ids}")
        
        # 验证菜单是否存在
        menus = await Menu.filter(id__in=test_menu_ids).all()
        print(f"\n找到的菜单：")
        for menu in menus:
            print(f"  - ID: {menu.id}, 名称: {menu.name}, 类型: {menu.menu_type}")
        
        # 验证API是否存在
        apis = await SysApiEndpoint.filter(id__in=test_api_ids).all()
        print(f"\n找到的API：")
        for api in apis:
            print(f"  - ID: {api.id}, 路径: {api.api_path}, 方法: {api.http_method}")
        
        # 尝试更新权限
        print(f"\n开始更新权限...")
        
        try:
            # 清除现有权限
            await role.apis.clear()
            await role.menus.clear()
            print("  ✓ 清除现有权限成功")
            
            # 添加新的API权限
            for api in apis:
                await role.apis.add(api)
            print(f"  ✓ 添加 {len(apis)} 个API权限成功")
            
            # 添加新的菜单权限
            for menu in menus:
                await role.menus.add(menu)
            print(f"  ✓ 添加 {len(menus)} 个菜单权限成功")
            
            # 验证更新后的权限
            updated_menus = await role.menus.all()
            updated_apis = await role.apis.all()
            
            print(f"\n更新后的权限：")
            print(f"  菜单权限数量: {len(updated_menus)}")
            print(f"  API权限数量: {len(updated_apis)}")
            
            print("\n✅ 权限更新测试成功！")
            
        except Exception as update_error:
            print(f"\n❌ 权限更新失败：")
            print(f"  错误类型: {type(update_error).__name__}")
            print(f"  错误信息: {str(update_error)}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"\n❌ 测试失败：")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()

if __name__ == '__main__':
    asyncio.run(test_update_permissions())
