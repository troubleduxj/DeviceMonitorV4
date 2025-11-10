#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis缓存测试脚本

测试Redis缓存的基本功能和性能
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.redis_cache import (
    redis_cache_manager, 
    init_redis_cache, 
    close_redis_cache,
    redis_cache
)
from app.core.permission_cache import permission_cache_manager
from app.log import logger


async def test_basic_operations():
    """测试基本操作"""
    print("\n=== 测试基本操作 ===")
    
    # 测试设置和获取
    test_data = {
        "user_id": 123,
        "username": "test_user",
        "permissions": ["read", "write"],
        "timestamp": time.time()
    }
    
    # 设置缓存
    success = await redis_cache_manager.set("test_user_123", test_data, ttl=60)
    print(f"设置缓存: {'成功' if success else '失败'}")
    
    # 获取缓存
    cached_data = await redis_cache_manager.get("test_user_123")
    print(f"获取缓存: {cached_data}")
    
    # 检查缓存是否存在
    exists = await redis_cache_manager.exists("test_user_123")
    print(f"缓存存在: {exists}")
    
    # 获取TTL
    ttl = await redis_cache_manager.get_ttl("test_user_123")
    print(f"缓存TTL: {ttl}秒")
    
    # 删除缓存
    deleted = await redis_cache_manager.delete("test_user_123")
    print(f"删除缓存: {'成功' if deleted else '失败'}")
    
    # 再次检查
    exists_after_delete = await redis_cache_manager.exists("test_user_123")
    print(f"删除后缓存存在: {exists_after_delete}")


async def test_batch_operations():
    """测试批量操作"""
    print("\n=== 测试批量操作 ===")
    
    # 批量设置缓存
    test_keys = []
    for i in range(10):
        key = f"batch_test_{i}"
        value = {"id": i, "name": f"user_{i}", "active": i % 2 == 0}
        await redis_cache_manager.set(key, value, ttl=30)
        test_keys.append(key)
    
    print(f"批量设置了 {len(test_keys)} 个缓存项")
    
    # 批量获取
    cached_values = []
    for key in test_keys:
        value = await redis_cache_manager.get(key)
        if value:
            cached_values.append(value)
    
    print(f"批量获取了 {len(cached_values)} 个缓存项")
    
    # 模式清理
    deleted_count = await redis_cache_manager.clear_pattern("batch_test_*")
    print(f"模式清理删除了 {deleted_count} 个缓存项")


async def test_cache_decorator():
    """测试缓存装饰器"""
    print("\n=== 测试缓存装饰器 ===")
    
    @redis_cache(ttl=60, key_prefix="test_func")
    async def expensive_function(user_id: int, category: str = "default"):
        """模拟耗时函数"""
        await asyncio.sleep(0.1)  # 模拟耗时操作
        return {
            "user_id": user_id,
            "category": category,
            "result": f"processed_{user_id}_{category}",
            "timestamp": time.time()
        }
    
    # 第一次调用（应该执行函数）
    start_time = time.time()
    result1 = await expensive_function(123, "premium")
    first_call_time = time.time() - start_time
    print(f"第一次调用耗时: {first_call_time:.3f}秒")
    print(f"第一次调用结果: {result1}")
    
    # 第二次调用（应该从缓存获取）
    start_time = time.time()
    result2 = await expensive_function(123, "premium")
    second_call_time = time.time() - start_time
    print(f"第二次调用耗时: {second_call_time:.3f}秒")
    print(f"第二次调用结果: {result2}")
    
    print(f"缓存加速比: {first_call_time / second_call_time:.1f}x")


async def test_permission_cache():
    """测试权限缓存"""
    print("\n=== 测试权限缓存 ===")
    
    # 测试用户权限缓存
    user_permissions = {
        "user_id": 123,
        "roles": ["admin", "user"],
        "permissions": ["read", "write", "delete"],
        "menus": [1, 2, 3, 4, 5]
    }
    
    # 设置用户权限缓存
    success = await permission_cache_manager.set_user_permissions(123, user_permissions)
    print(f"设置用户权限缓存: {'成功' if success else '失败'}")
    
    # 获取用户权限缓存
    cached_permissions = await permission_cache_manager.get_user_permissions(123)
    print(f"获取用户权限缓存: {cached_permissions is not None}")
    
    # 测试角色权限缓存
    role_permissions = {
        "role_id": 1,
        "role_name": "admin",
        "apis": ["/api/users", "/api/roles", "/api/permissions"],
        "menus": [1, 2, 3]
    }
    
    success = await permission_cache_manager.set_role_permissions(1, role_permissions)
    print(f"设置角色权限缓存: {'成功' if success else '失败'}")
    
    # 获取缓存统计
    stats = await permission_cache_manager.get_cache_statistics()
    print(f"权限缓存统计: {stats}")
    
    # 失效用户权限缓存
    invalidated = await permission_cache_manager.invalidate_user_permissions(123)
    print(f"失效用户权限缓存: {'成功' if invalidated else '失败'}")


async def test_performance():
    """测试性能"""
    print("\n=== 测试性能 ===")
    
    # 测试写入性能
    write_count = 100
    start_time = time.time()
    
    for i in range(write_count):
        await redis_cache_manager.set(
            f"perf_test_{i}", 
            {"id": i, "data": f"test_data_{i}"}, 
            ttl=60
        )
    
    write_time = time.time() - start_time
    write_ops_per_sec = write_count / write_time
    print(f"写入性能: {write_count} 次操作耗时 {write_time:.3f}秒, {write_ops_per_sec:.1f} ops/sec")
    
    # 测试读取性能
    start_time = time.time()
    
    for i in range(write_count):
        await redis_cache_manager.get(f"perf_test_{i}")
    
    read_time = time.time() - start_time
    read_ops_per_sec = write_count / read_time
    print(f"读取性能: {write_count} 次操作耗时 {read_time:.3f}秒, {read_ops_per_sec:.1f} ops/sec")
    
    # 清理测试数据
    await redis_cache_manager.clear_pattern("perf_test_*")


async def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    # 测试获取不存在的键
    non_existent = await redis_cache_manager.get("non_existent_key", default="default_value")
    print(f"获取不存在的键: {non_existent}")
    
    # 测试删除不存在的键
    deleted = await redis_cache_manager.delete("non_existent_key")
    print(f"删除不存在的键: {'成功' if deleted else '失败'}")
    
    # 测试设置复杂对象
    complex_object = {
        "nested": {
            "list": [1, 2, 3],
            "dict": {"a": 1, "b": 2}
        },
        "timestamp": time.time()
    }
    
    success = await redis_cache_manager.set("complex_object", complex_object)
    retrieved = await redis_cache_manager.get("complex_object")
    print(f"复杂对象缓存: 设置{'成功' if success else '失败'}, 获取{'成功' if retrieved else '失败'}")


async def main():
    """主测试函数"""
    try:
        print("开始Redis缓存测试...")
        
        # 初始化Redis缓存
        await init_redis_cache()
        
        # 健康检查
        health = await redis_cache_manager.health_check()
        print(f"Redis健康检查: {health}")
        
        if health["status"] != "healthy":
            print("Redis连接不健康，跳过测试")
            return
        
        # 运行各项测试
        await test_basic_operations()
        await test_batch_operations()
        await test_cache_decorator()
        await test_permission_cache()
        await test_performance()
        await test_error_handling()
        
        # 获取缓存信息
        cache_info = await redis_cache_manager.get_cache_info()
        print(f"\n=== 缓存信息 ===")
        print(f"Redis版本: {cache_info.get('redis_version', 'unknown')}")
        print(f"已连接客户端: {cache_info.get('connected_clients', 0)}")
        print(f"内存使用: {cache_info.get('used_memory_human', '0B')}")
        print(f"总键数: {cache_info.get('total_keys', 0)}")
        
        print("\n✅ 所有测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # 关闭Redis连接
        await close_redis_cache()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)