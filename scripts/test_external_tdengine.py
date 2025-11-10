#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试外部TDengine支持
验证TDengine配置管理、连接测试和健康检查功能
"""

import asyncio
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.tdengine_config import tdengine_config_manager, TDengineServerConfig
from app.services.tdengine_service import tdengine_service_manager
from app.log import logger


async def test_external_tdengine():
    """测试外部TDengine支持"""
    print("=" * 80)
    print("外部TDengine支持测试")
    print(f"测试时间: {datetime.now()}")
    print("=" * 80)
    
    try:
        # 1. 测试配置管理器
        print("\n1. 测试TDengine配置管理器")
        print("-" * 40)
        
        # 列出所有服务器
        servers = tdengine_config_manager.list_servers()
        print(f"已配置的服务器: {servers}")
        print(f"默认服务器: {tdengine_config_manager.default_server}")
        
        # 获取默认服务器信息
        if servers:
            default_server = tdengine_config_manager.default_server
            server_info = tdengine_config_manager.get_server_info(default_server)
            print(f"\n默认服务器信息:")
            print(f"  名称: {server_info['name']}")
            print(f"  地址: {server_info['host']}:{server_info['port']}")
            print(f"  数据库: {server_info['database']}")
            print(f"  外部服务器: {server_info['is_external']}")
            print(f"  描述: {server_info['description']}")
        
        # 2. 测试连接
        print("\n2. 测试TDengine连接")
        print("-" * 40)
        
        if servers:
            for server_name in servers:
                print(f"\n测试服务器: {server_name}")
                try:
                    health_status = await tdengine_config_manager.test_connection(server_name)
                    print(f"  连接状态: {'✅ 健康' if health_status.is_healthy else '❌ 异常'}")
                    print(f"  响应时间: {health_status.response_time_ms:.2f}ms")
                    if health_status.server_version:
                        print(f"  服务器版本: {health_status.server_version}")
                    print(f"  数据库存在: {'是' if health_status.database_exists else '否'}")
                    if health_status.error_message:
                        print(f"  错误信息: {health_status.error_message}")
                except Exception as e:
                    print(f"  连接测试失败: {e}")
        
        # 3. 测试服务管理器
        print("\n3. 测试TDengine服务管理器")
        print("-" * 40)
        
        # 获取默认服务
        service = tdengine_service_manager.get_service()
        
        # 测试健康检查
        print("执行健康检查...")
        health_result = await service.health_check()
        print(f"健康检查结果: {health_result}")
        
        # 测试服务器信息
        print("\n获取服务器信息...")
        server_info = await service.get_server_info()
        print(f"服务器信息: {server_info}")
        
        # 4. 测试数据库操作
        print("\n4. 测试数据库操作")
        print("-" * 40)
        
        if health_result.get("status") == "healthy":
            try:
                # 获取数据库列表
                databases = await service.get_databases()
                print(f"数据库列表: {databases}")
                
                # 获取统计信息
                stats = await service.get_statistics()
                print(f"统计信息: {stats}")
                
                # 测试简单查询
                print("\n执行测试查询...")
                result = await service.execute_query("SELECT SERVER_VERSION();")
                print(f"查询结果: {result}")
                
            except Exception as e:
                print(f"数据库操作测试失败: {e}")
        else:
            print("跳过数据库操作测试（连接不健康）")
        
        # 5. 测试多服务器健康检查
        print("\n5. 测试多服务器健康检查")
        print("-" * 40)
        
        all_health = await tdengine_service_manager.health_check_all()
        for server_name, health in all_health.items():
            status_icon = "✅" if health.get("status") == "healthy" else "❌"
            print(f"  {server_name}: {status_icon} {health.get('status', 'unknown')}")
            if health.get("response_time_ms"):
                print(f"    响应时间: {health['response_time_ms']:.2f}ms")
            if health.get("error"):
                print(f"    错误: {health['error']}")
        
        # 6. 测试配置导出
        print("\n6. 测试配置导出")
        print("-" * 40)
        
        config_export = tdengine_config_manager.export_config()
        print(f"配置导出成功，包含 {len(config_export.get('servers', {}))} 个服务器配置")
        
        print("\n" + "=" * 80)
        print("✅ 外部TDengine支持测试完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        await tdengine_service_manager.close_all()


async def test_add_external_server():
    """测试添加外部服务器配置"""
    print("\n" + "=" * 80)
    print("测试添加外部TDengine服务器")
    print("=" * 80)
    
    # 添加一个测试服务器配置
    test_config = TDengineServerConfig(
        host="192.168.1.100",  # 示例外部服务器地址
        port=6041,
        user="test_user",
        password="test_password",
        database="test_external_db",
        is_external=True,
        description="测试外部TDengine服务器"
    )
    
    try:
        # 添加服务器配置
        tdengine_config_manager.add_server("external_test", test_config)
        print("✅ 外部服务器配置添加成功")
        
        # 获取服务器信息
        server_info = tdengine_config_manager.get_server_info("external_test")
        print(f"服务器信息: {server_info}")
        
        # 测试连接（预期会失败，因为是示例地址）
        print("\n测试连接到外部服务器...")
        try:
            health_status = await tdengine_config_manager.test_connection("external_test")
            print(f"连接结果: {'✅ 成功' if health_status.is_healthy else '❌ 失败'}")
            if health_status.error_message:
                print(f"错误信息: {health_status.error_message}")
        except Exception as e:
            print(f"连接测试失败（预期结果）: {e}")
        
        # 移除测试服务器
        tdengine_config_manager.remove_server("external_test")
        print("✅ 测试服务器配置已移除")
        
    except Exception as e:
        print(f"❌ 添加外部服务器测试失败: {e}")


if __name__ == "__main__":
    # 设置日志级别
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    asyncio.run(test_external_tdengine())
    asyncio.run(test_add_external_server())