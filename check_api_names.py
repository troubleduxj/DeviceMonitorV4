#!/usr/bin/env python3
"""
检查API的名称配置
"""
import asyncio
import os
import sys
from tortoise import Tortoise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.settings.config import settings


async def check_api_names():
    """检查API名称"""
    try:
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        from app.models.admin import SysApiEndpoint
        
        print("=" * 100)
        print("设备相关API名称检查")
        print("=" * 100)
        
        # 查找设备相关的API
        apis = await SysApiEndpoint.filter(api_path__contains='/devices').all()
        
        print(f"\n找到 {len(apis)} 个设备相关API:\n")
        print(f"{'方法':<8} {'路径':<45} {'名称':<30}")
        print("-" * 100)
        
        for api in sorted(apis, key=lambda x: (x.api_path, x.http_method)):
            print(f"{api.http_method:<8} {api.api_path:<45} {api.api_name:<30}")
        
        print("\n" + "=" * 100)
        print("当前API名称的优缺点")
        print("=" * 100)
        
        print("\n✅ 优点：")
        print("  - API已经有中文名称")
        print("  - 名称描述了API的功能")
        
        print("\n❌ 问题：")
        print("  - 在接口权限树中，可能只显示了路径，没有显示名称")
        print("  - 管理员看到 'POST /api/v2/devices' 不知道是什么功能")
        
        print("\n💡 解决方案：")
        print("  - 修改前端ApiPermissionTree组件")
        print("  - 显示格式改为：'新增设备 (POST /api/v2/devices)'")
        print("  - 或者：'POST /api/v2/devices - 新增设备'")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(check_api_names())
