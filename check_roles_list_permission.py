#!/usr/bin/env python3
"""
检查并授予角色列表API权限
"""
import asyncio
import os
import sys
from tortoise import Tortoise

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.settings.config import settings


async def check_and_grant_roles_list_permission():
    """检查并授予角色列表API权限"""
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        print("=" * 80)
        print("检查角色列表API权限")
        print("=" * 80)
        
        # 1. 查找用户
        from app.models.admin import User
        user = await User.get_or_none(username='hlzg_admin')
        if not user:
            print("❌ 未找到用户 hlzg_admin")
            return
        
        print(f"\n✅ 找到用户: {user.username} (ID: {user.id})")
        
        # 2. 获取用户的角色
        roles = await user.roles.all()
        print(f"\n用户角色数量: {len(roles)}")
        for role in roles:
            print(f"  - {role.name} (ID: {role.id})")
        
        if not roles:
            print("❌ 用户没有任何角色")
            return
        
        # 3. 查找角色列表API
        from app.models.admin import SysApiEndpoint
        api = await SysApiEndpoint.get_or_none(api_path='/api/v2/roles', http_method='GET')
        
        if not api:
            print("\n❌ 未找到API: GET /api/v2/roles")
            print("需要先在系统中创建这个API")
            
            # 查找类似的API
            similar_apis = await SysApiEndpoint.filter(api_path__contains='/roles').all()
            print(f"\n找到 {len(similar_apis)} 个相关API:")
            for a in similar_apis:
                print(f"  - {a.http_method} {a.api_path} (ID: {a.id})")
            return
        
        print(f"\n✅ 找到API: {api.http_method} {api.api_path} (ID: {api.id})")
        
        # 4. 检查每个角色是否有这个API权限
        from app.models.admin import SysRoleApi
        
        for role in roles:
            # 检查是否已有权限
            has_permission = await SysRoleApi.exists(role=role, api=api)
            
            if has_permission:
                print(f"\n✅ 角色 '{role.name}' 已有权限")
            else:
                print(f"\n❌ 角色 '{role.name}' 缺少权限，正在授予...")
                
                # 授予权限
                await SysRoleApi.create(role=role, api=api)
                print(f"✅ 已授予角色 '{role.name}' 权限: GET /api/v2/roles")
        
        # 5. 验证权限
        print("\n" + "=" * 80)
        print("验证权限授予结果")
        print("=" * 80)
        
        for role in roles:
            role_apis = await SysRoleApi.filter(role=role).prefetch_related('api')
            roles_apis = [ra for ra in role_apis if '/roles' in ra.api.api_path]
            
            print(f"\n角色 '{role.name}' 的角色相关API权限 ({len(roles_apis)}个):")
            for ra in sorted(roles_apis, key=lambda x: (x.api.api_path, x.api.http_method)):
                print(f"  - {ra.api.http_method} {ra.api.api_path}")
        
        print("\n" + "=" * 80)
        print("✅ 检查完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(check_and_grant_roles_list_permission())
