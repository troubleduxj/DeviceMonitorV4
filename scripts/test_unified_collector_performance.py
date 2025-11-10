#!/usr/bin/env python3
"""
统一采集器系统性能测试脚本

此脚本用于测试统一采集器系统的性能，包括：
1. 大量采集器创建性能测试
2. 并发查询性能测试
3. 数据库连接池性能测试
4. 内存使用情况测试
5. 响应时间测试

使用方法:
    python scripts/test_unified_collector_performance.py
"""

import asyncio
import json
import logging
import sys
import os
import time
import psutil
import statistics
from datetime import datetime
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_collector_performance_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """性能指标类"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.memory_before = None
        self.memory_after = None
        self.cpu_before = None
        self.cpu_after = None
        self.response_times = []
        self.success_count = 0
        self.error_count = 0
    
    def start_measurement(self):
        """开始性能测量"""
        self.start_time = time.time()
        process = psutil.Process()
        self.memory_before = process.memory_info().rss / 1024 / 1024  # MB
        self.cpu_before = process.cpu_percent()
    
    def end_measurement(self):
        """结束性能测量"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        process = psutil.Process()
        self.memory_after = process.memory_info().rss / 1024 / 1024  # MB
        self.cpu_after = process.cpu_percent()
    
    def add_response_time(self, response_time: float):
        """添加响应时间"""
        self.response_times.append(response_time)
    
    def add_success(self):
        """添加成功计数"""
        self.success_count += 1
    
    def add_error(self):
        """添加错误计数"""
        self.error_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'duration_seconds': self.duration,
            'memory_usage_mb': {
                'before': self.memory_before,
                'after': self.memory_after,
                'increase': self.memory_after - self.memory_before if self.memory_before else 0
            },
            'cpu_usage_percent': {
                'before': self.cpu_before,
                'after': self.cpu_after
            },
            'operations': {
                'total': self.success_count + self.error_count,
                'success': self.success_count,
                'error': self.error_count,
                'success_rate': (self.success_count / (self.success_count + self.error_count)) * 100 if (self.success_count + self.error_count) > 0 else 0
            }
        }
        
        if self.response_times:
            stats['response_times'] = {
                'count': len(self.response_times),
                'min': min(self.response_times),
                'max': max(self.response_times),
                'avg': statistics.mean(self.response_times),
                'median': statistics.median(self.response_times),
                'p95': statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else max(self.response_times),
                'p99': statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) >= 100 else max(self.response_times)
            }
        
        if self.duration and self.duration > 0:
            stats['throughput'] = {
                'operations_per_second': (self.success_count + self.error_count) / self.duration,
                'successful_operations_per_second': self.success_count / self.duration
            }
        
        return stats


class UnifiedCollectorPerformanceTest:
    """统一采集器性能测试类"""
    
    def __init__(self):
        self.test_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.test_results = {
            'test_info': {
                'timestamp': self.test_timestamp,
                'start_time': datetime.now().isoformat()
            },
            'performance_tests': {},
            'summary': {}
        }
        self.created_test_data = []
    
    async def test_bulk_create_performance(self, count: int = 100) -> Dict[str, Any]:
        """测试批量创建性能"""
        logger.info(f"开始批量创建性能测试 (数量: {count})")
        
        metrics = PerformanceMetrics()
        metrics.start_measurement()
        
        try:
            from app.models.unified_collector import ApiCollector, CollectorType
            
            # 批量创建API采集器
            for i in range(count):
                start_time = time.time()
                
                try:
                    collector = await ApiCollector.create(
                        name=f"perf_test_api_{self.test_timestamp}_{i:04d}",
                        display_name=f"性能测试API采集器 {i+1}",
                        description=f"性能测试用API采集器 #{i+1}",
                        collector_type=CollectorType.API,
                        cron_expression="0 */30 * * * *",
                        timeout_seconds=300,
                        retry_count=3,
                        config={"test_config": f"test_value_{i}"},
                        api_url=f"http://test.example.com/api/data/{i}",
                        request_method="GET",
                        request_headers={"Content-Type": "application/json"},
                        auth_type="none"
                    )
                    
                    self.created_test_data.append(('api_collectors', collector.id))
                    metrics.add_success()
                    
                except Exception as e:
                    logger.error(f"创建采集器 {i} 失败: {e}")
                    metrics.add_error()
                
                response_time = time.time() - start_time
                metrics.add_response_time(response_time)
                
                # 每10个操作记录一次进度
                if (i + 1) % 10 == 0:
                    logger.info(f"已创建 {i + 1}/{count} 个采集器")
            
            metrics.end_measurement()
            
            stats = metrics.get_statistics()
            logger.info(f"批量创建性能测试完成: {stats['operations']['success']}/{count} 成功")
            logger.info(f"平均响应时间: {stats['response_times']['avg']:.3f}s")
            logger.info(f"吞吐量: {stats['throughput']['operations_per_second']:.2f} ops/s")
            
            return stats
            
        except Exception as e:
            logger.error(f"批量创建性能测试失败: {e}")
            metrics.end_measurement()
            return metrics.get_statistics()
    
    async def test_concurrent_query_performance(self, concurrent_count: int = 20, queries_per_thread: int = 10) -> Dict[str, Any]:
        """测试并发查询性能"""
        logger.info(f"开始并发查询性能测试 (并发数: {concurrent_count}, 每线程查询数: {queries_per_thread})")
        
        metrics = PerformanceMetrics()
        metrics.start_measurement()
        
        async def query_task():
            """单个查询任务"""
            from app.models.unified_collector import ApiCollector
            
            for _ in range(queries_per_thread):
                start_time = time.time()
                
                try:
                    # 执行查询
                    collectors = await ApiCollector.all().limit(50)
                    metrics.add_success()
                    
                except Exception as e:
                    logger.error(f"查询失败: {e}")
                    metrics.add_error()
                
                response_time = time.time() - start_time
                metrics.add_response_time(response_time)
        
        try:
            # 创建并发任务
            tasks = [query_task() for _ in range(concurrent_count)]
            
            # 执行并发查询
            await asyncio.gather(*tasks)
            
            metrics.end_measurement()
            
            stats = metrics.get_statistics()
            total_queries = concurrent_count * queries_per_thread
            logger.info(f"并发查询性能测试完成: {stats['operations']['success']}/{total_queries} 成功")
            logger.info(f"平均响应时间: {stats['response_times']['avg']:.3f}s")
            logger.info(f"P95响应时间: {stats['response_times']['p95']:.3f}s")
            logger.info(f"吞吐量: {stats['throughput']['operations_per_second']:.2f} queries/s")
            
            return stats
            
        except Exception as e:
            logger.error(f"并发查询性能测试失败: {e}")
            metrics.end_measurement()
            return metrics.get_statistics()
    
    async def test_database_connection_pool_performance(self) -> Dict[str, Any]:
        """测试数据库连接池性能"""
        logger.info("开始数据库连接池性能测试")
        
        metrics = PerformanceMetrics()
        metrics.start_measurement()
        
        try:
            from tortoise import connections
            
            # 测试连接获取和释放性能
            for i in range(100):
                start_time = time.time()
                
                try:
                    db = connections.get('postgres')
                    result = await db.execute_query("SELECT COUNT(*) FROM api_collectors")
                    metrics.add_success()
                    
                except Exception as e:
                    logger.error(f"数据库操作失败: {e}")
                    metrics.add_error()
                
                response_time = time.time() - start_time
                metrics.add_response_time(response_time)
                
                if (i + 1) % 20 == 0:
                    logger.info(f"已完成 {i + 1}/100 次数据库操作")
            
            metrics.end_measurement()
            
            stats = metrics.get_statistics()
            logger.info(f"数据库连接池性能测试完成: {stats['operations']['success']}/100 成功")
            logger.info(f"平均响应时间: {stats['response_times']['avg']:.3f}s")
            
            return stats
            
        except Exception as e:
            logger.error(f"数据库连接池性能测试失败: {e}")
            metrics.end_measurement()
            return metrics.get_statistics()
    
    async def test_memory_usage_under_load(self) -> Dict[str, Any]:
        """测试负载下的内存使用情况"""
        logger.info("开始内存使用负载测试")
        
        metrics = PerformanceMetrics()
        metrics.start_measurement()
        
        memory_samples = []
        
        try:
            from app.models.unified_collector import ApiCollector
            
            # 模拟持续负载
            for cycle in range(10):
                cycle_start = time.time()
                
                # 每个周期执行多种操作
                tasks = []
                
                # 查询操作
                for _ in range(5):
                    tasks.append(ApiCollector.all().limit(20))
                
                # 执行任务
                try:
                    await asyncio.gather(*tasks)
                    metrics.add_success()
                except Exception as e:
                    logger.error(f"周期 {cycle} 操作失败: {e}")
                    metrics.add_error()
                
                # 记录内存使用
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
                
                cycle_time = time.time() - cycle_start
                metrics.add_response_time(cycle_time)
                
                logger.info(f"周期 {cycle + 1}/10 完成，内存使用: {memory_mb:.1f}MB")
                
                # 短暂休息
                await asyncio.sleep(0.1)
            
            metrics.end_measurement()
            
            stats = metrics.get_statistics()
            stats['memory_samples'] = {
                'samples': memory_samples,
                'min': min(memory_samples),
                'max': max(memory_samples),
                'avg': statistics.mean(memory_samples),
                'increase': max(memory_samples) - min(memory_samples)
            }
            
            logger.info(f"内存使用负载测试完成")
            logger.info(f"内存使用范围: {min(memory_samples):.1f}MB - {max(memory_samples):.1f}MB")
            logger.info(f"内存增长: {max(memory_samples) - min(memory_samples):.1f}MB")
            
            return stats
            
        except Exception as e:
            logger.error(f"内存使用负载测试失败: {e}")
            metrics.end_measurement()
            return metrics.get_statistics()
    
    async def cleanup_test_data(self):
        """清理测试数据"""
        logger.info("清理性能测试数据...")
        
        cleanup_count = 0
        for table_name, record_id in self.created_test_data:
            try:
                from tortoise import connections
                db = connections.get('postgres')
                await db.execute_query(f"DELETE FROM {table_name} WHERE id = $1", [record_id])
                cleanup_count += 1
            except Exception as e:
                logger.warning(f"删除测试数据失败: {table_name}.id={record_id} - {e}")
        
        logger.info(f"清理完成，删除了 {cleanup_count} 条测试数据")
    
    async def run_all_performance_tests(self) -> bool:
        """运行所有性能测试"""
        logger.info("开始统一采集器系统性能测试...")
        logger.info(f"测试时间戳: {self.test_timestamp}")
        
        try:
            # 1. 批量创建性能测试
            logger.info("\n=== 1. 批量创建性能测试 ===")
            bulk_create_stats = await self.test_bulk_create_performance(50)
            self.test_results['performance_tests']['bulk_create'] = bulk_create_stats
            
            # 2. 并发查询性能测试
            logger.info("\n=== 2. 并发查询性能测试 ===")
            concurrent_query_stats = await self.test_concurrent_query_performance(10, 5)
            self.test_results['performance_tests']['concurrent_query'] = concurrent_query_stats
            
            # 3. 数据库连接池性能测试
            logger.info("\n=== 3. 数据库连接池性能测试 ===")
            db_pool_stats = await self.test_database_connection_pool_performance()
            self.test_results['performance_tests']['database_pool'] = db_pool_stats
            
            # 4. 内存使用负载测试
            logger.info("\n=== 4. 内存使用负载测试 ===")
            memory_stats = await self.test_memory_usage_under_load()
            self.test_results['performance_tests']['memory_usage'] = memory_stats
            
            # 清理测试数据
            await self.cleanup_test_data()
            
            # 生成测试摘要
            self.generate_test_summary()
            
            # 输出测试结果
            logger.info("\n" + "="*60)
            logger.info("性能测试结果汇总:")
            
            for test_name, stats in self.test_results['performance_tests'].items():
                logger.info(f"\n{test_name.upper()}:")
                if 'operations' in stats:
                    logger.info(f"  成功率: {stats['operations']['success_rate']:.1f}%")
                if 'response_times' in stats:
                    logger.info(f"  平均响应时间: {stats['response_times']['avg']:.3f}s")
                    logger.info(f"  P95响应时间: {stats['response_times']['p95']:.3f}s")
                if 'throughput' in stats:
                    logger.info(f"  吞吐量: {stats['throughput']['operations_per_second']:.2f} ops/s")
                if 'memory_usage_mb' in stats:
                    logger.info(f"  内存增长: {stats['memory_usage_mb']['increase']:.1f}MB")
            
            logger.info("\n" + self.test_results['summary']['overall_assessment'])
            logger.info("="*60)
            
            # 保存测试报告
            report_file = f"unified_collector_performance_report_{self.test_timestamp}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            logger.info(f"性能测试报告已保存: {report_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"性能测试过程中发生严重错误: {e}")
            return False
    
    def generate_test_summary(self):
        """生成测试摘要"""
        summary = {
            'test_count': len(self.test_results['performance_tests']),
            'end_time': datetime.now().isoformat(),
            'recommendations': [],
            'performance_issues': [],
            'overall_assessment': ''
        }
        
        # 分析性能指标
        issues = []
        recommendations = []
        
        for test_name, stats in self.test_results['performance_tests'].items():
            if 'operations' in stats and stats['operations']['success_rate'] < 95:
                issues.append(f"{test_name}: 成功率过低 ({stats['operations']['success_rate']:.1f}%)")
                recommendations.append(f"检查{test_name}的错误处理和重试机制")
            
            if 'response_times' in stats and stats['response_times']['avg'] > 1.0:
                issues.append(f"{test_name}: 平均响应时间过长 ({stats['response_times']['avg']:.3f}s)")
                recommendations.append(f"优化{test_name}的查询性能")
            
            if 'memory_usage_mb' in stats and stats['memory_usage_mb']['increase'] > 100:
                issues.append(f"{test_name}: 内存增长过多 ({stats['memory_usage_mb']['increase']:.1f}MB)")
                recommendations.append(f"检查{test_name}的内存泄漏问题")
        
        summary['performance_issues'] = issues
        summary['recommendations'] = recommendations
        
        # 总体评估
        if not issues:
            summary['overall_assessment'] = "✓ 性能测试全部通过，系统性能良好"
        elif len(issues) <= 2:
            summary['overall_assessment'] = "⚠ 发现少量性能问题，建议优化"
        else:
            summary['overall_assessment'] = "✗ 发现多个性能问题，需要重点优化"
        
        self.test_results['summary'] = summary


async def main():
    """主函数"""
    # 初始化 Tortoise ORM
    from app.settings.config import settings
    
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    try:
        test_runner = UnifiedCollectorPerformanceTest()
        success = await test_runner.run_all_performance_tests()
        
        if success:
            print("\n✓ 性能测试完成！")
            print("\n后续步骤:")
            print("1. 查看性能测试报告分析结果")
            print("2. 根据建议优化系统性能")
            print("3. 继续进行兼容性测试")
        else:
            print("\n✗ 性能测试失败，请检查日志文件获取详细信息")
            
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())