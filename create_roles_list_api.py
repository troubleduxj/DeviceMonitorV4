#!/usr/bin/env python3
"""
创建并授权角色列表API
"""
import asyncio
import os
import sys
from tortoise import Tortoise

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.settings.config import settings


async def create_and_grant_roles_list_api():
    """创建并授权角色列表API"""
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        print("=" * 80)
        print("创建并授权角色列表API")
        print("=" * 80)
        
        # 1. 查找或创建API分组
        from app.models.admin import SysApiGroup, SysApiEndpoint, User, Role
        
        # 查找角色管理API分组
        group = await SysApiGroup.get_or_none(group_code='role_management')
        if not group:
            print("\n创建API分组: role_management")
            group = await SysApiGroup.create(
                group_code='role_management',
                group_name='角色管理',
                description='角色管理相关API',
                status=1  # 1表示启用
            )
            print(f"✅ 已创建API分组: {group.group_name} (ID: {group.id})")
        else:
            print(f"\n✅ 找到API分组: {group.group_name} (ID: {group.id})")
        
        # 2. 创建角色列表API
        api = await SysApiEndpoint.get_or_none(api_path='/api/v2/roles', http_method='GET')
        
        if api:
            print(f"\n✅ API已存在: {api.http_method} {api.api_path} (ID: {api.id})")
        else:
            print("\n创建API: GET /api/v2/roles")
            api = await SysApiEndpoint.create(
                api_code='role_list',
                api_name='获取角色列表',
                api_path='/api/v2/roles',
                http_method='GET',
                description='获取角色列表（支持分页、搜索、树形结构）',
                group=group,
                status='active',  # active表示启用
                is_public=False,
                is_deprecated=False,
                permission_code='system:role:list',
                version='v2'
            )
            print(f"✅ 已创建API: {api.http_method} {api.api_path} (ID: {api.id})")
        
        # 3. 查找用户和角色
        user = await User.get_or_none(username='hlzg_admin')
        if not user:
            print("\n❌ 未找到用户 hlzg_admin")
            return
        
        print(f"\n✅ 找到用户: {user.username} (ID: {user.id})")
        
        roles = await user.roles.all()
        print(f"用户角色数量: {len(roles)}")
        for role in roles:
            print(f"  - {role.role_name} (ID: {role.id})")
        
        if not roles:
            print("❌ 用户没有任何角色")
            return
        
        # 4. 为每个角色授权
        for role in roles:
            # 检查是否已有权限
            role_apis = await role.apis.all()
            has_permission = api in role_apis
            
            if has_permission:
                print(f"\n✅ 角色 '{role.role_name}' 已有权限")
            else:
                print(f"\n❌ 角色 '{role.role_name}' 缺少权限，正在授予...")
                
                # 授予权限
                await role.apis.add(api)
                print(f"✅ 已授予角色 '{role.role_name}' 权限: GET /api/v2/roles")
        
        # 5. 验证权限
        print("\n" + "=" * 80)
        print("验证权限授予结果")
        print("=" * 80)
        
        for role in roles:
            role_apis = await role.apis.all()
            roles_apis = [a for a in role_apis if '/roles' in a.api_path]
            
            print(f"\n角色 '{role.role_name}' 的角色相关API权限 ({len(roles_apis)}个):")
            for a in sorted(roles_apis, key=lambda x: (x.api_path, x.http_method)):
                print(f"  - {a.http_method} {a.api_path}")
        
        print("\n" + "=" * 80)
        print("✅ 完成！请刷新前端页面测试")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(create_and_grant_roles_list_api())
