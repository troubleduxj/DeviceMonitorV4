#!/usr/bin/env python3
"""
添加权限按钮显示模式的系统参数
"""
import asyncio
import os
import sys
from tortoise import Tortoise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.settings.config import settings


async def add_permission_button_mode_param():
    """添加权限按钮显示模式参数"""
    try:
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        from app.models.system import SysConfig
        
        print("=" * 80)
        print("添加权限按钮显示模式系统参数")
        print("=" * 80)
        
        # 检查参数是否已存在
        param = await SysConfig.get_or_none(param_key='PERMISSION_BUTTON_MODE')
        
        if param:
            print(f"\n✅ 参数已存在")
            print(f"   键: {param.param_key}")
            print(f"   值: {param.param_value}")
            print(f"   名称: {param.param_name}")
            print(f"   描述: {param.description}")
        else:
            print("\n创建新参数...")
            param = await SysConfig.create(
                param_key='PERMISSION_BUTTON_MODE',
                param_value='disable',  # 默认值：hide（隐藏）或 disable（禁用）
                param_name='权限按钮显示模式',
                param_type='string',
                description='控制无权限按钮的显示方式：hide=隐藏按钮，disable=禁用按钮（灰色显示）',
                is_editable=True,
                is_system=False,
                is_active=True
            )
            print(f"✅ 已创建参数")
            print(f"   键: {param.param_key}")
            print(f"   值: {param.param_value}")
            print(f"   描述: {param.description}")
        
        print("\n" + "=" * 80)
        print("使用说明")
        print("=" * 80)
        print("\n在系统管理 → 系统参数中，可以修改 PERMISSION_BUTTON_MODE 的值：")
        print("  - hide: 无权限时隐藏按钮（推荐用于生产环境）")
        print("  - disable: 无权限时禁用按钮（推荐用于开发调试）")
        print("\n修改后刷新页面即可生效。")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(add_permission_button_mode_param())
