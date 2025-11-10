#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按钮权限初始化脚本
为系统中的主要页面创建按钮级别的权限控制

使用方法：
    python scripts/init_button_permissions.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.db import init_db, close_db
from app.models.admin import Menu
from app.log import logger


# 定义按钮权限配置
BUTTON_PERMISSIONS = [
    # 用户管理页面的按钮权限
    {
        "parent_menu_name": "用户管理",
        "buttons": [
            {
                "name": "新建用户",
                "perms": "POST /api/v2/users",
                "icon": "material-symbols:add",
                "order": 1
            },
            {
                "name": "编辑用户",
                "perms": "PUT /api/v2/users/{id}",
                "icon": "material-symbols:edit",
                "order": 2
            },
            {
                "name": "删除用户",
                "perms": "DELETE /api/v2/users/{id}",
                "icon": "material-symbols:delete",
                "order": 3
            },
            {
                "name": "重置密码",
                "perms": "POST /api/v2/users/{id}/actions/reset-password",
                "icon": "material-symbols:lock-reset",
                "order": 4
            },
            {
                "name": "批量删除用户",
                "perms": "DELETE /api/v2/users/batch",
                "icon": "material-symbols:delete-sweep",
                "order": 5
            },
            {
                "name": "导出用户",
                "perms": "GET /api/v2/users/export",
                "icon": "material-symbols:download",
                "order": 6
            }
        ]
    },
    
    # 角色管理页面的按钮权限
    {
        "parent_menu_name": "角色管理",
        "buttons": [
            {
                "name": "新建角色",
                "perms": "POST /api/v2/roles",
                "icon": "material-symbols:add",
                "order": 1
            },
            {
                "name": "编辑角色",
                "perms": "PUT /api/v2/roles/{id}",
                "icon": "material-symbols:edit",
                "order": 2
            },
            {
                "name": "删除角色",
                "perms": "DELETE /api/v2/roles/{id}",
                "icon": "material-symbols:delete",
                "order": 3
            },
            {
                "name": "分配权限",
                "perms": "POST /api/v2/roles/{id}/permissions",
                "icon": "material-symbols:key",
                "order": 4
            }
        ]
    },
    
    # 菜单管理页面的按钮权限
    {
        "parent_menu_name": "菜单管理",
        "buttons": [
            {
                "name": "新建菜单",
                "perms": "POST /api/v2/menus",
                "icon": "material-symbols:add",
                "order": 1
            },
            {
                "name": "编辑菜单",
                "perms": "PUT /api/v2/menus/{id}",
                "icon": "material-symbols:edit",
                "order": 2
            },
            {
                "name": "删除菜单",
                "perms": "DELETE /api/v2/menus/{id}",
                "icon": "material-symbols:delete",
                "order": 3
            }
        ]
    },
    
    # 部门管理页面的按钮权限
    {
        "parent_menu_name": "部门管理",
        "buttons": [
            {
                "name": "新建部门",
                "perms": "POST /api/v2/departments",
                "icon": "material-symbols:add",
                "order": 1
            },
            {
                "name": "编辑部门",
                "perms": "PUT /api/v2/departments/{id}",
                "icon": "material-symbols:edit",
                "order": 2
            },
            {
                "name": "删除部门",
                "perms": "DELETE /api/v2/departments/{id}",
                "icon": "material-symbols:delete",
                "order": 3
            }
        ]
    },
    
    # 设备管理页面的按钮权限
    {
        "parent_menu_name": "设备基础信息",
        "buttons": [
            {
                "name": "新建设备",
                "perms": "POST /api/v2/devices",
                "icon": "material-symbols:add",
                "order": 1
            },
            {
                "name": "编辑设备",
                "perms": "PUT /api/v2/devices/{id}",
                "icon": "material-symbols:edit",
                "order": 2
            },
            {
                "name": "删除设备",
                "perms": "DELETE /api/v2/devices/{id}",
                "icon": "material-symbols:delete",
                "order": 3
            },
            {
                "name": "导出设备",
                "perms": "GET /api/v2/devices/export",
                "icon": "material-symbols:download",
                "order": 4
            }
        ]
    },
    
    # 维修记录页面的按钮权限
    {
        "parent_menu_name": "维修记录",
        "buttons": [
            {
                "name": "新建维修记录",
                "perms": "POST /api/v2/device/maintenance/repair-records",
                "icon": "material-symbols:add",
                "order": 1
            },
            {
                "name": "编辑维修记录",
                "perms": "PUT /api/v2/device/maintenance/repair-records/{id}",
                "icon": "material-symbols:edit",
                "order": 2
            },
            {
                "name": "删除维修记录",
                "perms": "DELETE /api/v2/device/maintenance/repair-records/{id}",
                "icon": "material-symbols:delete",
                "order": 3
            },
            {
                "name": "导出维修记录",
                "perms": "GET /api/v2/device/maintenance/repair-records/export",
                "icon": "material-symbols:download",
                "order": 4
            }
        ]
    },
    
    # 字典类型管理页面的按钮权限
    {
        "parent_menu_name": "字典类型",
        "buttons": [
            {
                "name": "新建字典类型",
                "perms": "POST /api/v2/dict-types",
                "icon": "material-symbols:add",
                "order": 1
            },
            {
                "name": "编辑字典类型",
                "perms": "PUT /api/v2/dict-types/{id}",
                "icon": "material-symbols:edit",
                "order": 2
            },
            {
                "name": "删除字典类型",
                "perms": "DELETE /api/v2/dict-types/{id}",
                "icon": "material-symbols:delete",
                "order": 3
            }
        ]
    },
    
    # 字典数据管理页面的按钮权限
    {
        "parent_menu_name": "字典数据",
        "buttons": [
            {
                "name": "新建字典数据",
                "perms": "POST /api/v2/dict-data",
                "icon": "material-symbols:add",
                "order": 1
            },
            {
                "name": "编辑字典数据",
                "perms": "PUT /api/v2/dict-data/{id}",
                "icon": "material-symbols:edit",
                "order": 2
            },
            {
                "name": "删除字典数据",
                "perms": "DELETE /api/v2/dict-data/{id}",
                "icon": "material-symbols:delete",
                "order": 3
            }
        ]
    }
]


async def init_button_permissions():
    """初始化按钮权限"""
    logger.info("=" * 60)
    logger.info("开始初始化按钮权限")
    logger.info("=" * 60)
    
    await init_db()
    
    try:
        total_created = 0
        total_skipped = 0
        
        for config in BUTTON_PERMISSIONS:
            parent_menu_name = config["parent_menu_name"]
            buttons = config["buttons"]
            
            # 查找父菜单
            parent_menu = await Menu.filter(name=parent_menu_name).first()
            
            if not parent_menu:
                logger.warning(f"⚠️  未找到父菜单: {parent_menu_name}，跳过其按钮权限创建")
                total_skipped += len(buttons)
                continue
            
            logger.info(f"\n处理菜单: {parent_menu_name} (ID: {parent_menu.id})")
            
            for button in buttons:
                button_name = button["name"]
                perms = button["perms"]
                
                # 检查按钮权限是否已存在
                existing = await Menu.filter(
                    name=button_name,
                    parent_id=parent_menu.id,
                    menu_type="button"
                ).first()
                
                if existing:
                    logger.info(f"  ⏭️  按钮权限已存在: {button_name}")
                    total_skipped += 1
                    continue
                
                # 创建按钮权限
                await Menu.create(
                    name=button_name,
                    path="",  # 按钮不需要路径
                    component="",  # 按钮不需要组件
                    menu_type="button",
                    icon=button.get("icon", ""),
                    order_num=button.get("order", 0),
                    parent_id=parent_menu.id,
                    perms=perms,
                    visible=True,
                    status=True,
                    is_frame=False,
                    is_cache=False
                )
                
                logger.info(f"  ✅ 创建按钮权限: {button_name} ({perms})")
                total_created += 1
        
        logger.info("\n" + "=" * 60)
        logger.info(f"按钮权限初始化完成！")
        logger.info(f"  新创建: {total_created} 个")
        logger.info(f"  已跳过: {total_skipped} 个")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 初始化按钮权限失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_db()


async def main():
    """主函数"""
    success = await init_button_permissions()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

