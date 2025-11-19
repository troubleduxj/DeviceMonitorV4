#!/usr/bin/env python3
"""
验证test用户是否真的有维修记录API权限
"""
import asyncio
import os
import sys
from tortoise import Tortoise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.settings.config import settings


async def verify_permissions():
    """验证权限"""
    try:
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        from app.models.admin import User
        
        # 查找test用户
        user = await User.get_or_none(username='test')
        if not user:
            print("❌ 未找到test用户")
            return
        
        print(f"✅ 用户: {user.username}")
        
        # 获取角色
        roles = await user.roles.all()
        print(f"\n角色: {[r.role_name for r in roles]}")
        
        # 获取所有API权限
        all_apis = []
        for role in roles:
            apis = await role.apis.all()
            all_apis.extend(apis)
        
        print(f"\n总API权限数: {len(all_apis)}")
        
        # 查找维修记录列表API
        target_api = 'GET /api/v2/device/maintenance/repair-records'
        has_permission = any(
            f"{api.http_method} {api.api_path}" == target_api 
            for api in all_apis
        )
        
        print(f"\n检查权限: {target_api}")
        print(f"结果: {'✅ 有权限' if has_permission else '❌ 无权限'}")
        
        if has_permission:
            print("\n这就是为什么'维修记录'按钮可以显示的原因！")
            print("因为按钮配置的权限是: GET /api/v2/device/maintenance/repair-records")
            print("而test用户的角色确实被授予了这个API权限。")
        
        # 检查设备编辑权限
        device_edit_api = 'PUT /api/v2/devices/{id}'
        has_device_edit = any(
            f"{api.http_method} {api.api_path}" == device_edit_api 
            for api in all_apis
        )
        
        print(f"\n检查权限: {device_edit_api}")
        print(f"结果: {'✅ 有权限' if has_device_edit else '❌ 无权限'}")
        
        if not has_device_edit:
            print("这就是为什么'编辑'按钮应该被隐藏的原因！")
        
        # 列出所有设备相关的API权限
        print("\n" + "="*80)
        print("test用户的所有API权限:")
        print("="*80)
        for api in sorted(all_apis, key=lambda x: (x.api_path, x.http_method)):
            print(f"  {api.http_method:6s} {api.api_path}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(verify_permissions())
