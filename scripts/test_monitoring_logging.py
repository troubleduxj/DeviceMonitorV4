#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控和日志系统测试
验证性能监控装饰器、结构化日志记录和系统监控功能
"""

import asyncio
import time
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.log import get_logger
from app.core.monitoring import (
    monitor_performance, 
    monitor_database_query, 
    monitor_api_endpoint,
    monitor_background_task,
    performance_monitor,
    start_monitoring,
    stop_monitoring
)

# 获取结构化日志记录器
logger = get_logger(__name__)


# 测试函数
@monitor_performance(name="test_sync_function", include_memory=True, threshold_ms=100.0)
def test_sync_function(duration: float = 0.1):
    """测试同步函数"""
    logger.info("Executing sync function", duration=duration)
    time.sleep(duration)
    return f"Completed in {duration}s"


@monitor_performance(name="test_async_function", include_memory=True, include_cpu=True)
async def test_async_function(duration: float = 0.1):
    """测试异步函数"""
    logger.info("Executing async function", duration=duration)
    await asyncio.sleep(duration)
    return f"Completed in {duration}s"


@monitor_database_query("SELECT")
def test_database_query():
    """测试数据库查询监控"""
    logger.info("Executing database query")
    time.sleep(0.05)  # 模拟数据库查询
    return "Query result"


@monitor_api_endpoint("test_endpoint")
async def test_api_endpoint():
    """测试API端点监控"""
    logger.info("Processing API request")
    await asyncio.sleep(0.02)  # 模拟API处理
    return {"status": "success"}


@monitor_background_task("data_processing")
def test_background_task():
    """测试后台任务监控"""
    logger.info("Starting background task")
    
    # 模拟一些处理
    for i in range(5):
        logger.debug(f"Processing item {i+1}", item_id=i+1)
        time.sleep(0.01)
    
    logger.info("Background task completed")
    return "Task completed"


def test_error_function():
    """测试错误函数"""
    logger.error("This is a test error")
    raise ValueError("Test error for monitoring")


async def test_structured_logging():
    """测试结构化日志记录"""
    print("\n" + "="*60)
    print("测试结构化日志记录")
    print("="*60)
    
    # 测试不同级别的日志
    logger.debug("This is a debug message", component="test", action="debug_test")
    logger.info("This is an info message", component="test", action="info_test")
    logger.warning("This is a warning message", component="test", action="warning_test")
    logger.error("This is an error message", component="test", action="error_test")
    
    # 测试性能日志
    logger.performance("Function execution completed", duration_ms=123.45, function="test_function")
    
    # 测试审计日志
    logger.audit("User action performed", user_id="user123", action="login", ip_address="192.168.1.1")
    
    # 测试访问日志
    logger.access("API request processed", method="GET", path="/api/test", status_code=200, duration_ms=45.67)
    
    print("✅ 结构化日志记录测试完成")


async def test_performance_monitoring():
    """测试性能监控"""
    print("\n" + "="*60)
    print("测试性能监控")
    print("="*60)
    
    # 测试同步函数监控
    print("测试同步函数监控...")
    result = test_sync_function(0.05)
    print(f"同步函数结果: {result}")
    
    # 测试异步函数监控
    print("测试异步函数监控...")
    result = await test_async_function(0.03)
    print(f"异步函数结果: {result}")
    
    # 测试数据库查询监控
    print("测试数据库查询监控...")
    result = test_database_query()
    print(f"数据库查询结果: {result}")
    
    # 测试API端点监控
    print("测试API端点监控...")
    result = await test_api_endpoint()
    print(f"API端点结果: {result}")
    
    # 测试后台任务监控
    print("测试后台任务监控...")
    result = test_background_task()
    print(f"后台任务结果: {result}")
    
    # 测试错误监控
    print("测试错误监控...")
    try:
        test_error_function()
    except ValueError as e:
        print(f"捕获到预期错误: {e}")
    
    print("✅ 性能监控测试完成")


def test_system_monitoring():
    """测试系统监控"""
    print("\n" + "="*60)
    print("测试系统监控")
    print("="*60)
    
    # 启动系统监控
    print("启动系统监控...")
    start_monitoring()
    
    # 等待一段时间收集指标
    print("等待收集系统指标...")
    time.sleep(3)
    
    # 收集系统指标
    print("收集系统指标...")
    metrics = performance_monitor.collect_system_metrics()
    if metrics:
        print(f"CPU使用率: {metrics.cpu_percent:.1f}%")
        print(f"内存使用率: {metrics.memory_percent:.1f}%")
        print(f"磁盘使用率: {metrics.disk_usage_percent:.1f}%")
        print(f"活跃连接数: {metrics.active_connections}")
    
    # 获取系统指标摘要
    print("获取系统指标摘要...")
    summary = performance_monitor.get_system_metrics_summary(minutes=1)
    if summary:
        print(f"CPU平均使用率: {summary.get('cpu', {}).get('avg', 0):.1f}%")
        print(f"内存平均使用率: {summary.get('memory', {}).get('avg', 0):.1f}%")
    
    # 停止系统监控
    print("停止系统监控...")
    stop_monitoring()
    
    print("✅ 系统监控测试完成")


def test_performance_statistics():
    """测试性能统计"""
    print("\n" + "="*60)
    print("测试性能统计")
    print("="*60)
    
    # 获取函数统计
    print("获取函数统计...")
    function_stats = performance_monitor.get_function_stats()
    print(f"监控的函数数量: {len(function_stats)}")
    
    for func_name, stats in list(function_stats.items())[:5]:  # 显示前5个
        print(f"  {func_name}:")
        print(f"    调用次数: {stats['count']}")
        print(f"    平均耗时: {stats['avg_duration']:.2f}ms")
        print(f"    最大耗时: {stats['max_duration']:.2f}ms")
        print(f"    错误次数: {stats['error_count']}")
    
    # 获取慢函数
    print("\n获取慢函数...")
    slow_functions = performance_monitor.get_slow_functions(threshold_ms=50.0, limit=5)
    for func in slow_functions:
        print(f"  {func['function']}: 平均 {func['avg_duration_ms']:.2f}ms")
    
    # 获取错误函数
    print("\n获取错误函数...")
    error_functions = performance_monitor.get_error_functions(limit=5)
    for func in error_functions:
        print(f"  {func['function']}: 错误率 {func['error_rate']:.1%}")
    
    # 获取最近的指标
    print("\n获取最近的指标...")
    recent_metrics = performance_monitor.get_recent_metrics(limit=5)
    for metric in recent_metrics:
        print(f"  {metric.name}: {metric.duration_ms:.2f}ms ({'成功' if metric.success else '失败'})")
    
    print("✅ 性能统计测试完成")


def test_metrics_export():
    """测试指标导出"""
    print("\n" + "="*60)
    print("测试指标导出")
    print("="*60)
    
    # 导出指标
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = f"test_metrics_export_{timestamp}.json"
    
    try:
        performance_monitor.export_metrics(export_file)
        print(f"✅ 指标导出成功: {export_file}")
        
        # 检查文件是否存在
        if os.path.exists(export_file):
            file_size = os.path.getsize(export_file)
            print(f"导出文件大小: {file_size} 字节")
            
            # 清理测试文件
            os.remove(export_file)
            print("测试文件已清理")
        
    except Exception as e:
        print(f"❌ 指标导出失败: {e}")
    
    print("✅ 指标导出测试完成")


async def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 开始监控和日志系统综合测试")
    print(f"测试时间: {datetime.now()}")
    
    try:
        # 1. 测试结构化日志记录
        await test_structured_logging()
        
        # 2. 测试性能监控
        await test_performance_monitoring()
        
        # 3. 测试系统监控
        test_system_monitoring()
        
        # 4. 测试性能统计
        test_performance_statistics()
        
        # 5. 测试指标导出
        test_metrics_export()
        
        print("\n" + "🎉"*20)
        print("✅ 所有测试完成！")
        print("🎉"*20)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 设置日志级别
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    asyncio.run(run_comprehensive_test())