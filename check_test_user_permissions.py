#!/usr/bin/env python3
"""
检查test用户的权限配置
"""
import asyncio
import os
import sys
from tortoise import Tortoise

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.settings.config import settings


async def check_test_user_permissions():
    """检查test用户的权限配置"""
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        print("=" * 80)
        print("检查test用户的权限配置")
        print("=" * 80)
        
        # 1. 查找test用户
        from app.models.admin import User
        user = await User.get_or_none(username='test')
        if not user:
            print("\n❌ 未找到用户 test")
            return
        
        print(f"\n✅ 找到用户: {user.username} (ID: {user.id})")
        print(f"   邮箱: {user.email}")
        print(f"   状态: {'激活' if user.status else '未激活'}")
        
        # 2. 获取用户的角色
        roles = await user.roles.all()
        print(f"\n用户角色数量: {len(roles)}")
        for role in roles:
            print(f"  - {role.role_name} (ID: {role.id})")
        
        if not roles:
            print("❌ 用户没有任何角色")
            return
        
        # 3. 检查每个角色的菜单权限
        print("\n" + "=" * 80)
        print("菜单权限检查")
        print("=" * 80)
        
        for role in roles:
            menus = await role.menus.all()
            print(f"\n角色 '{role.role_name}' 的菜单权限 ({len(menus)}个):")
            
            # 查找设备相关的菜单
            device_menus = [m for m in menus if '设备' in m.name]
            if device_menus:
                print(f"\n  设备相关菜单 ({len(device_menus)}个):")
                for menu in device_menus:
                    print(f"    - {menu.name} (ID: {menu.id}, 类型: {menu.menu_type})")
                    
                    # 如果有子菜单，也显示
                    if menu.menu_type == 'catalog':
                        # 查找子菜单
                        from app.models.admin import Menu
                        children = await Menu.filter(parent_id=menu.id).all()
                        if children:
                            print(f"      子菜单:")
                            for child in children:
                                print(f"        - {child.name} (ID: {child.id}, 类型: {child.menu_type})")
        
        # 4. 检查每个角色的API权限
        print("\n" + "=" * 80)
        print("API权限检查")
        print("=" * 80)
        
        for role in roles:
            apis = await role.apis.all()
            print(f"\n角色 '{role.role_name}' 的API权限 ({len(apis)}个):")
            
            if len(apis) == 0:
                print("  ❌ 没有任何API权限！")
            else:
                # 查找设备相关的API
                device_apis = [a for a in apis if 'device' in a.api_path.lower()]
                if device_apis:
                    print(f"\n  设备相关API ({len(device_apis)}个):")
                    for api in sorted(device_apis, key=lambda x: (x.api_path, x.http_method)):
                        print(f"    - {api.http_method} {api.api_path}")
                        print(f"      名称: {api.api_name}")
                
                # 查找维修相关的API
                maintenance_apis = [a for a in apis if 'maintenance' in a.api_path.lower() or 'repair' in a.api_path.lower()]
                if maintenance_apis:
                    print(f"\n  维修相关API ({len(maintenance_apis)}个):")
                    for api in sorted(maintenance_apis, key=lambda x: (x.api_path, x.http_method)):
                        print(f"    - {api.http_method} {api.api_path}")
                        print(f"      名称: {api.api_name}")
        
        # 5. 总结
        print("\n" + "=" * 80)
        print("权限配置总结")
        print("=" * 80)
        
        total_menus = sum([len(await role.menus.all()) for role in roles])
        total_apis = sum([len(await role.apis.all()) for role in roles])
        
        print(f"\n总菜单权限: {total_menus} 个")
        print(f"总API权限: {total_apis} 个")
        
        if total_apis == 0:
            print("\n⚠️  警告：用户没有任何API权限！")
            print("   虽然有菜单权限，但无法调用任何API接口")
            print("   建议：在角色管理中为该角色配置相应的API权限")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(check_test_user_permissions())
