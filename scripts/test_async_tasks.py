#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务系统测试脚本

测试异步任务调度器和设备采集器的功能
"""

import asyncio
import sys
import os
import time
from datetime import timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.async_tasks import (
    task_scheduler, 
    init_task_scheduler, 
    shutdown_task_scheduler,
    async_task,
    scheduled_task,
    TaskPriority
)
from app.services.device_collector_optimized import (
    device_collector,
    init_device_collector,
    shutdown_device_collector
)
from app.log import logger


# 测试任务函数
@async_task(
    name="test_simple_task",
    priority=TaskPriority.NORMAL,
    max_retries=2,
    tags=["test"]
)
async def test_simple_task(message: str, delay: float = 1.0):
    """简单测试任务"""
    await asyncio.sleep(delay)
    result = f"处理消息: {message}, 延迟: {delay}s"
    logger.info(result)
    return result


@async_task(
    name="test_error_task",
    priority=TaskPriority.LOW,
    max_retries=3,
    tags=["test", "error"]
)
async def test_error_task(should_fail: bool = True):
    """测试错误处理的任务"""
    if should_fail:
        raise Exception("这是一个测试错误")
    return "任务成功完成"


@async_task(
    name="test_cpu_intensive_task",
    priority=TaskPriority.HIGH,
    timeout=10.0,
    tags=["test", "cpu"]
)
async def test_cpu_intensive_task(iterations: int = 1000000):
    """CPU密集型任务测试"""
    def cpu_work():
        total = 0
        for i in range(iterations):
            total += i * i
        return total
    
    # 在线程池中执行CPU密集型工作
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, cpu_work)
    return f"CPU密集型任务完成，结果: {result}"


@scheduled_task(
    schedule=timedelta(seconds=10),
    name="test_scheduled_task"
)
async def test_scheduled_task():
    """定时任务测试"""
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    message = f"定时任务执行于: {current_time}"
    logger.info(message)
    return message


async def test_basic_task_operations():
    """测试基本任务操作"""
    print("\n=== 测试基本任务操作 ===")
    
    # 提交简单任务
    task_id1 = await test_simple_task("Hello World", 2.0)
    print(f"提交任务1: {task_id1}")
    
    # 提交多个任务
    task_ids = []
    for i in range(5):
        task_id = await test_simple_task(f"批量任务 {i}", 1.0)
        task_ids.append(task_id)
    
    print(f"提交了 {len(task_ids)} 个批量任务")
    
    # 等待任务完成
    await asyncio.sleep(5)
    
    # 检查任务状态
    for task_id in [task_id1] + task_ids[:2]:  # 只检查前几个
        status = await task_scheduler.get_task_status(task_id)
        if status:
            print(f"任务 {task_id[:8]}... 状态: {status['status']}")


async def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    # 提交会失败的任务
    error_task_id = await test_error_task(should_fail=True)
    print(f"提交错误任务: {error_task_id}")
    
    # 等待任务完成（包括重试）
    await asyncio.sleep(10)
    
    # 检查任务状态
    status = await task_scheduler.get_task_status(error_task_id)
    if status:
        print(f"错误任务状态: {status['status']}")
        if status.get('result') and status['result'].get('error'):
            print(f"错误信息: {status['result']['error']}")


async def test_priority_and_timeout():
    """测试优先级和超时"""
    print("\n=== 测试优先级和超时 ===")
    
    # 提交不同优先级的任务
    low_priority_task = await task_scheduler.submit_task(
        test_simple_task,
        "低优先级任务",
        3.0,
        priority=TaskPriority.LOW
    )
    
    high_priority_task = await task_scheduler.submit_task(
        test_simple_task,
        "高优先级任务",
        1.0,
        priority=TaskPriority.HIGH
    )
    
    # 提交CPU密集型任务
    cpu_task_id = await test_cpu_intensive_task(500000)
    
    print(f"提交了优先级测试任务: 低优先级={low_priority_task[:8]}..., 高优先级={high_priority_task[:8]}...")
    print(f"提交了CPU密集型任务: {cpu_task_id[:8]}...")
    
    # 等待任务完成
    await asyncio.sleep(8)


async def test_scheduled_tasks():
    """测试定时任务"""
    print("\n=== 测试定时任务 ===")
    
    # 调度定时任务
    scheduled_id = await test_scheduled_task()
    print(f"调度定时任务: {scheduled_id}")
    
    # 等待几次执行
    print("等待定时任务执行...")
    await asyncio.sleep(25)


async def test_task_dependencies():
    """测试任务依赖"""
    print("\n=== 测试任务依赖 ===")
    
    # 创建依赖任务
    parent_task_id = await task_scheduler.submit_task(
        test_simple_task,
        "父任务",
        2.0,
        name="parent_task"
    )
    
    child_task_id = await task_scheduler.submit_task(
        test_simple_task,
        "子任务",
        1.0,
        name="child_task",
        depends_on=[parent_task_id]
    )
    
    print(f"创建依赖任务: 父任务={parent_task_id[:8]}..., 子任务={child_task_id[:8]}...")
    
    # 等待任务完成
    await asyncio.sleep(6)
    
    # 检查执行顺序
    parent_status = await task_scheduler.get_task_status(parent_task_id)
    child_status = await task_scheduler.get_task_status(child_task_id)
    
    if parent_status and child_status:
        print(f"父任务状态: {parent_status['status']}")
        print(f"子任务状态: {child_status['status']}")


async def test_device_collector():
    """测试设备采集器"""
    print("\n=== 测试设备采集器 ===")
    
    try:
        # 获取采集统计
        stats = await device_collector.get_collection_stats()
        print(f"当前采集统计: {stats}")
        
        # 手动触发设备健康检查
        health_task_id = await device_collector.health_check_devices()
        print(f"提交设备健康检查任务: {health_task_id}")
        
        # 等待任务完成
        await asyncio.sleep(5)
        
        # 检查任务结果
        health_status = await task_scheduler.get_task_status(health_task_id)
        if health_status and health_status['status'] == 'completed':
            result = health_status.get('result', {}).get('data', {})
            if result:
                print(f"健康检查结果: 总设备={result.get('total_devices', 0)}, "
                      f"健康设备={result.get('healthy_devices', 0)}")
        
    except Exception as e:
        print(f"设备采集器测试失败: {str(e)}")


async def test_scheduler_stats():
    """测试调度器统计"""
    print("\n=== 测试调度器统计 ===")
    
    stats = await task_scheduler.get_stats()
    print("调度器统计信息:")
    print(f"  运行状态: {stats['is_running']}")
    print(f"  队列大小: {stats['queue_size']}")
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  状态统计: {stats['status_counts']}")
    print(f"  定时任务数: {stats['scheduled_tasks_count']}")
    
    print("\n工作器统计:")
    for worker_stat in stats['workers']:
        print(f"  工作器 {worker_stat['worker_id']}:")
        print(f"    运行状态: {worker_stat['is_running']}")
        print(f"    当前任务: {worker_stat['current_task'] or '无'}")
        print(f"    处理任务数: {worker_stat['processed_count']}")
        print(f"    错误任务数: {worker_stat['error_count']}")
        print(f"    成功率: {worker_stat['success_rate']:.1f}%")
        print(f"    运行时间: {worker_stat['uptime_seconds']:.1f}s")


async def main():
    """主测试函数"""
    try:
        print("开始异步任务系统测试...")
        
        # 初始化任务调度器
        await init_task_scheduler()
        
        # 初始化设备采集器
        await init_device_collector()
        
        # 等待系统启动
        await asyncio.sleep(2)
        
        # 运行各项测试
        await test_basic_task_operations()
        await test_error_handling()
        await test_priority_and_timeout()
        await test_task_dependencies()
        await test_device_collector()
        await test_scheduler_stats()
        
        # 测试定时任务（时间较长，可选）
        print("\n是否测试定时任务？(需要等待25秒)")
        # await test_scheduled_tasks()
        
        print("\n✅ 所有测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # 关闭系统
        await shutdown_device_collector()
        await shutdown_task_scheduler()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)