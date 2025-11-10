#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加重试策略类型字典数据脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from app.models.system import SysDictType, SysDictData
from app.settings.config import settings


async def add_retry_strategy_dict():
    """添加重试策略类型字典数据"""
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.tortoise_orm.model_dump())
        
        # 创建重试策略类型字典类型
        dict_type, created = await SysDictType.get_or_create(
            type_code="retry_strategy_type",
            defaults={
                "type_name": "重试策略类型",
                "description": "任务失败时的重试策略类型配置"
            }
        )
        
        if created:
            print(f"创建字典类型成功: {dict_type.type_name}")
        else:
            print(f"字典类型已存在: {dict_type.type_name}")
        
        # 重试策略类型数据
        retry_strategies = [
            {
                "data_label": "固定间隔",
                "data_value": "fixed",
                "sort_order": 1,
                "description": "每次重试间隔固定时间"
            },
            {
                "data_label": "指数退避",
                "data_value": "exponential",
                "sort_order": 2,
                "description": "重试间隔按指数递增"
            },
            {
                "data_label": "线性递增",
                "data_value": "linear",
                "sort_order": 3,
                "description": "重试间隔线性递增"
            },
            {
                "data_label": "随机间隔",
                "data_value": "random",
                "sort_order": 4,
                "description": "随机重试间隔，避免雪崩效应"
            },
            {
                "data_label": "立即重试",
                "data_value": "immediate",
                "sort_order": 5,
                "description": "失败后立即重试，无延迟"
            }
        ]
        
        # 添加字典数据
        for strategy in retry_strategies:
            dict_data, created = await SysDictData.get_or_create(
                dict_type=dict_type,
                data_value=strategy["data_value"],
                defaults={
                    "data_label": strategy["data_label"],
                    "sort_order": strategy["sort_order"],
                    "is_enabled": True
                }
            )
            
            if created:
                print(f"创建字典数据成功: {dict_data.data_label} ({dict_data.data_value})")
            else:
                print(f"字典数据已存在: {dict_data.data_label} ({dict_data.data_value})")
        
        print("\n重试策略类型字典数据添加完成！")
        
    except Exception as e:
        print(f"添加字典数据失败: {str(e)}")
        raise
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(add_retry_strategy_dict())