#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API分组数据更新脚本
根据老API表的分组信息完善当前API端点的分组
"""

import asyncio
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from app.settings.config import settings
from app.models.admin import SysApiGroup, SysApiEndpoint


async def create_api_groups():
    """
    创建API分组
    """
    groups_data = [
        {'group_code': 'user_module', 'group_name': '用户模块', 'description': '用户相关API接口', 'sort_order': 1},
        {'group_code': 'role_module', 'group_name': '角色模块', 'description': '角色相关API接口', 'sort_order': 2},
        {'group_code': 'menu_module', 'group_name': '菜单模块', 'description': '菜单相关API接口', 'sort_order': 3},
        {'group_code': 'dept_module', 'group_name': '部门模块', 'description': '部门相关API接口', 'sort_order': 4},
        {'group_code': 'api_module', 'group_name': 'API模块', 'description': 'API管理相关接口', 'sort_order': 5},
        {'group_code': 'device_module', 'group_name': '设备模块', 'description': '设备相关API接口', 'sort_order': 6},
        {'group_code': 'device_data', 'group_name': '设备数据', 'description': '设备数据相关API接口', 'sort_order': 7},
        {'group_code': 'device_type', 'group_name': '设备类型管理', 'description': '设备类型管理相关API接口', 'sort_order': 8},
        {'group_code': 'device_alarm', 'group_name': '设备报警', 'description': '设备报警相关API接口', 'sort_order': 9},
        {'group_code': 'basic_module', 'group_name': '基础模块', 'description': '基础功能相关API接口', 'sort_order': 10},
        {'group_code': 'dashboard_module', 'group_name': '仪表板模块', 'description': '仪表板相关API接口', 'sort_order': 11},
        {'group_code': 'audit_module', 'group_name': '审计日志模块', 'description': '审计日志相关API接口', 'sort_order': 12},
    ]
    
    for group_data in groups_data:
        # 检查分组是否已存在
        existing_group = await SysApiGroup.filter(group_code=group_data['group_code']).first()
        if not existing_group:
            await SysApiGroup.create(
                group_code=group_data['group_code'],
                group_name=group_data['group_name'],
                parent_id=0,
                description=group_data['description'],
                sort_order=group_data['sort_order'],
                status='active'
            )
            print(f"创建分组: {group_data['group_name']}")
        else:
            print(f"分组已存在: {group_data['group_name']}")


async def update_api_endpoints_groups():
    """
    更新API端点的分组分配
    """
    # 分组映射规则
    group_mappings = [
        {'keywords': ['user'], 'group_code': 'user_module'},
        {'keywords': ['role'], 'group_code': 'role_module'},
        {'keywords': ['menu'], 'group_code': 'menu_module'},
        {'keywords': ['dept'], 'group_code': 'dept_module'},
        {'keywords': ['api'], 'group_code': 'api_module'},
        {'keywords': ['device'], 'group_code': 'device_module'},
        {'keywords': ['data'], 'group_code': 'device_data'},
        {'keywords': ['alarm'], 'group_code': 'device_alarm'},
        {'keywords': ['analysis', 'config', 'version'], 'group_code': 'basic_module'},
    ]
    
    # 获取所有API端点
    endpoints = await SysApiEndpoint.all()
    
    for endpoint in endpoints:
        # 跳过已经分配了非默认分组的API
        if endpoint.group_id and endpoint.group_id != 1:
            continue
            
        # 根据关键词匹配分组
        matched_group = None
        for mapping in group_mappings:
            for keyword in mapping['keywords']:
                if (keyword in (endpoint.api_path or '').lower() or 
                    keyword in (endpoint.api_code or '').lower() or
                    keyword in (endpoint.api_name or '').lower()):
                    matched_group = mapping['group_code']
                    break
            if matched_group:
                break
        
        if matched_group:
            # 获取分组ID
            group = await SysApiGroup.filter(group_code=matched_group).first()
            if group:
                endpoint.group_id = group.id
                await endpoint.save()
                print(f"更新API [{endpoint.api_name}] 到分组 [{group.group_name}]")


async def main():
    """
    主函数
    """
    try:
        # 构建数据库URL
        postgres_creds = settings.tortoise_orm.connections.postgres.credentials
        db_url = f"postgres://{postgres_creds.user}:{postgres_creds.password}@{postgres_creds.host}:{postgres_creds.port}/{postgres_creds.database}"
        
        # 初始化Tortoise ORM
        await Tortoise.init(
            config={
                "connections": {
                    "default": db_url
                },
                "apps": {
                    "models": {
                        "models": ["app.models.admin", "app.models.system"],
                        "default_connection": "default"
                    }
                }
            }
        )
        
        print("开始更新API分组数据...")
        
        # 创建API分组
        await create_api_groups()
        
        # 更新API端点分组
        await update_api_endpoints_groups()
        
        print("API分组数据更新完成！")
        
    except Exception as e:
        print(f"更新失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        try:
            await Tortoise.close_connections()
        except Exception:
            pass  # 忽略关闭连接时的错误


if __name__ == "__main__":
    asyncio.run(main())