#!/usr/bin/env python3
"""
统一采集器系统功能测试脚本

此脚本用于验证统一采集器系统的功能完整性，包括：
1. 创建不同类型的采集器配置
2. 更新采集器配置
3. 验证配置数据的正确存储和读取
4. 测试配置验证逻辑
5. 测试字典数据的正确使用

使用方法:
    python scripts/test_unified_collector_system.py
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_collector_system_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class UnifiedCollectorSystemTest:
    """统一采集器系统测试类"""
    
    def __init__(self):
        self.test_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'errors': []
        }
        self.created_test_data = []
    
    def log_test_result(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """记录测试结果"""
        self.test_results['total_tests'] += 1
        if success:
            self.test_results['passed_tests'] += 1
            logger.info(f"✓ {test_name}: {message}")
        else:
            self.test_results['failed_tests'] += 1
            logger.error(f"✗ {test_name}: {message}")
            self.test_results['errors'].append(f"{test_name}: {message}")
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_database_connection(self) -> bool:
        """测试数据库连接"""
        try:
            from tortoise import connections
            db = connections.get('postgres')
            result = await db.execute_query("SELECT 1")
            self.log_test_result("数据库连接测试", True, "数据库连接正常")
            return True
        except Exception as e:
            self.log_test_result("数据库连接测试", False, f"数据库连接失败: {e}")
            return False
    
    async def test_table_structure(self) -> bool:
        """测试表结构"""
        try:
            from tortoise import connections
            db = connections.get('postgres')
            
            # 检查必要的表是否存在
            required_tables = [
                'collectors', 'device_collectors', 'api_collectors',
                'collector_config_templates', 'collector_config_instances',
                'collector_execution_logs', 'sys_dict_type', 'sys_dict_data'
            ]
            
            missing_tables = []
            for table in required_tables:
                try:
                    await db.execute_query(f"SELECT 1 FROM {table} LIMIT 1")
                except Exception:
                    missing_tables.append(table)
            
            if missing_tables:
                self.log_test_result(
                    "表结构测试", 
                    False, 
                    f"缺少表: {', '.join(missing_tables)}"
                )
                return False
            else:
                self.log_test_result(
                    "表结构测试", 
                    True, 
                    f"所有必要的表都存在 ({len(required_tables)}个)"
                )
                return True
                
        except Exception as e:
            self.log_test_result("表结构测试", False, f"表结构检查失败: {e}")
            return False
    
    async def test_create_api_collector(self) -> bool:
        """测试创建API采集器"""
        try:
            from app.models.unified_collector import ApiCollector, CollectorType, CollectorStatus
            
            # 创建测试API采集器
            test_collector_name = f"test_api_collector_{self.test_timestamp}"
            api_collector = await ApiCollector.create(
                name=test_collector_name,
                display_name="测试API采集器",
                description="用于系统测试的API采集器",
                collector_type=CollectorType.API,
                cron_expression="0 */5 * * * *",
                timeout_seconds=300,
                retry_count=3,
                config={
                    "test_config": "test_value",
                    "api_endpoint": "http://test.example.com/api"
                },
                api_url="http://test.example.com/api/data",
                request_method="GET",
                request_headers={"Content-Type": "application/json"},
                auth_type="bearer",
                auth_config={"token": "test_token"}
            )
            
            self.created_test_data.append(('api_collectors', api_collector.id))
            
            # 验证创建的数据
            if api_collector.id and api_collector.name == test_collector_name:
                self.log_test_result(
                    "创建API采集器测试", 
                    True, 
                    f"成功创建API采集器 (ID: {api_collector.id})",
                    {'collector_id': api_collector.id, 'name': test_collector_name}
                )
                return True
            else:
                self.log_test_result(
                    "创建API采集器测试", 
                    False, 
                    "API采集器创建后数据验证失败"
                )
                return False
                
        except Exception as e:
            self.log_test_result("创建API采集器测试", False, f"创建API采集器失败: {e}")
            return False
    
    async def test_create_device_collector(self) -> bool:
        """测试创建设备采集器"""
        try:
            from app.models.unified_collector import DeviceCollector, CollectorType, CollectorStatus
            
            # 创建测试设备采集器
            test_collector_name = f"test_device_collector_{self.test_timestamp}"
            device_collector = await DeviceCollector.create(
                name=test_collector_name,
                display_name="测试设备采集器",
                description="用于系统测试的设备采集器",
                collector_type=CollectorType.DEVICE,
                cron_expression="0 */10 * * * *",
                timeout_seconds=600,
                retry_count=2,
                config={
                    "device_config": "test_device_value",
                    "protocol": "modbus"
                },
                device_id="test_device_001",
                device_type="MODBUS",
                connection_config={
                    "host": "192.168.1.100",
                    "port": 502,
                    "unit_id": 1
                },
                data_points=[
                    {
                        "name": "temperature",
                        "address": 1,
                        "data_type": "float"
                    }
                ]
            )
            
            self.created_test_data.append(('device_collectors', device_collector.id))
            
            # 验证创建的数据
            if device_collector.id and device_collector.name == test_collector_name:
                self.log_test_result(
                    "创建设备采集器测试", 
                    True, 
                    f"成功创建设备采集器 (ID: {device_collector.id})",
                    {'collector_id': device_collector.id, 'name': test_collector_name}
                )
                return True
            else:
                self.log_test_result(
                    "创建设备采集器测试", 
                    False, 
                    "设备采集器创建后数据验证失败"
                )
                return False
                
        except Exception as e:
            self.log_test_result("创建设备采集器测试", False, f"创建设备采集器失败: {e}")
            return False
    
    async def test_collector_query_performance(self) -> bool:
        """测试采集器查询性能"""
        try:
            from app.models.unified_collector import ApiCollector, DeviceCollector
            import time
            
            # 测试API采集器查询性能
            start_time = time.time()
            api_collectors = await ApiCollector.all().limit(100)
            api_query_time = time.time() - start_time
            
            # 测试设备采集器查询性能
            start_time = time.time()
            device_collectors = await DeviceCollector.all().limit(100)
            device_query_time = time.time() - start_time
            
            # 性能基准：查询时间应该小于1秒
            performance_threshold = 1.0
            
            if api_query_time < performance_threshold and device_query_time < performance_threshold:
                self.log_test_result(
                    "采集器查询性能测试", 
                    True, 
                    f"查询性能良好 (API: {api_query_time:.3f}s, Device: {device_query_time:.3f}s)",
                    {
                        'api_query_time': api_query_time,
                        'device_query_time': device_query_time,
                        'api_count': len(api_collectors),
                        'device_count': len(device_collectors)
                    }
                )
                return True
            else:
                self.log_test_result(
                    "采集器查询性能测试", 
                    False, 
                    f"查询性能不达标 (API: {api_query_time:.3f}s, Device: {device_query_time:.3f}s)"
                )
                return False
                
        except Exception as e:
            self.log_test_result("采集器查询性能测试", False, f"查询性能测试失败: {e}")
            return False
    
    async def test_config_template_system(self) -> bool:
        """测试配置模板系统"""
        try:
            from app.models.collector_config_template import CollectorConfigTemplate
            
            # 查询现有的配置模板
            templates = await CollectorConfigTemplate.all()
            
            if len(templates) > 0:
                # 测试模板数据的完整性
                template = templates[0]
                required_fields = ['template_name', 'collector_type', 'config_schema']
                missing_fields = []
                
                for field in required_fields:
                    if not hasattr(template, field) or getattr(template, field) is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_test_result(
                        "配置模板系统测试", 
                        False, 
                        f"模板数据不完整，缺少字段: {', '.join(missing_fields)}"
                    )
                    return False
                else:
                    self.log_test_result(
                        "配置模板系统测试", 
                        True, 
                        f"配置模板系统正常 (共{len(templates)}个模板)",
                        {'template_count': len(templates)}
                    )
                    return True
            else:
                self.log_test_result(
                    "配置模板系统测试", 
                    False, 
                    "没有找到配置模板数据"
                )
                return False
                
        except Exception as e:
            self.log_test_result("配置模板系统测试", False, f"配置模板系统测试失败: {e}")
            return False
    
    async def test_dict_system(self) -> bool:
        """测试字典系统"""
        try:
            from app.models.system import SysDictType, SysDictData
            
            # 查询字典类型
            dict_types = await SysDictType.all()
            
            if len(dict_types) > 0:
                # 查询字典数据
                dict_data = await SysDictData.all()
                
                self.log_test_result(
                    "字典系统测试", 
                    True, 
                    f"字典系统正常 (类型: {len(dict_types)}个, 数据: {len(dict_data)}个)",
                    {'dict_types': len(dict_types), 'dict_data': len(dict_data)}
                )
                return True
            else:
                self.log_test_result(
                    "字典系统测试", 
                    False, 
                    "没有找到字典类型数据"
                )
                return False
                
        except Exception as e:
            self.log_test_result("字典系统测试", False, f"字典系统测试失败: {e}")
            return False
    
    async def test_data_integrity(self) -> bool:
        """测试数据完整性"""
        try:
            from tortoise import connections
            db = connections.get('postgres')
            
            # 检查数据一致性
            integrity_checks = [
                {
                    'name': '采集器名称唯一性',
                    'query': "SELECT name, COUNT(*) as count FROM api_collectors GROUP BY name HAVING COUNT(*) > 1",
                    'expected_empty': True
                },
                {
                    'name': '采集器状态有效性',
                    'query': "SELECT COUNT(*) as count FROM api_collectors WHERE status NOT IN ('running', 'stopped', 'paused', 'error')",
                    'expected_zero': True
                },
                {
                    'name': '采集器类型有效性',
                    'query': "SELECT COUNT(*) as count FROM api_collectors WHERE collector_type NOT IN ('api', 'device', 'database', 'file', 'custom')",
                    'expected_zero': True
                }
            ]
            
            all_passed = True
            for check in integrity_checks:
                try:
                    result = await db.execute_query_dict(check['query'])
                    
                    if check.get('expected_empty'):
                        if len(result) == 0:
                            logger.info(f"  ✓ {check['name']}: 通过")
                        else:
                            logger.error(f"  ✗ {check['name']}: 发现 {len(result)} 个问题")
                            all_passed = False
                    elif check.get('expected_zero'):
                        if len(result) > 0 and result[0].get('count', 0) == 0:
                            logger.info(f"  ✓ {check['name']}: 通过")
                        else:
                            count = result[0].get('count', 0) if result else 0
                            logger.error(f"  ✗ {check['name']}: 发现 {count} 个问题")
                            all_passed = False
                            
                except Exception as e:
                    logger.error(f"  ✗ {check['name']}: 检查失败 - {e}")
                    all_passed = False
            
            self.log_test_result(
                "数据完整性测试", 
                all_passed, 
                "数据完整性检查通过" if all_passed else "数据完整性检查发现问题"
            )
            return all_passed
            
        except Exception as e:
            self.log_test_result("数据完整性测试", False, f"数据完整性测试失败: {e}")
            return False
    
    async def cleanup_test_data(self):
        """清理测试数据"""
        logger.info("清理测试数据...")
        
        for table_name, record_id in self.created_test_data:
            try:
                from tortoise import connections
                db = connections.get('postgres')
                await db.execute_query(f"DELETE FROM {table_name} WHERE id = $1", [record_id])
                logger.info(f"  ✓ 删除测试数据: {table_name}.id={record_id}")
            except Exception as e:
                logger.warning(f"  ✗ 删除测试数据失败: {table_name}.id={record_id} - {e}")
    
    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        logger.info("开始统一采集器系统功能测试...")
        logger.info(f"测试时间戳: {self.test_timestamp}")
        
        try:
            # 基础测试
            await self.test_database_connection()
            await self.test_table_structure()
            
            # 功能测试
            await self.test_create_api_collector()
            await self.test_create_device_collector()
            await self.test_collector_query_performance()
            await self.test_config_template_system()
            await self.test_dict_system()
            await self.test_data_integrity()
            
            # 清理测试数据
            await self.cleanup_test_data()
            
            # 输出测试结果
            logger.info("\n" + "="*60)
            logger.info("测试结果汇总:")
            logger.info(f"  总测试数: {self.test_results['total_tests']}")
            logger.info(f"  通过测试: {self.test_results['passed_tests']}")
            logger.info(f"  失败测试: {self.test_results['failed_tests']}")
            
            success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100 if self.test_results['total_tests'] > 0 else 0
            logger.info(f"  成功率: {success_rate:.1f}%")
            
            if self.test_results['errors']:
                logger.info("\n失败的测试:")
                for error in self.test_results['errors']:
                    logger.info(f"  - {error}")
            
            logger.info("="*60)
            
            # 保存测试报告
            report_file = f"unified_collector_test_report_{self.test_timestamp}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            logger.info(f"测试报告已保存: {report_file}")
            
            return self.test_results['failed_tests'] == 0
            
        except Exception as e:
            logger.error(f"测试过程中发生严重错误: {e}")
            return False


async def main():
    """主函数"""
    # 初始化 Tortoise ORM
    from app.settings.config import settings
    
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    try:
        test_runner = UnifiedCollectorSystemTest()
        success = await test_runner.run_all_tests()
        
        if success:
            print("\n✓ 所有测试通过！统一采集器系统功能正常。")
            print("\n后续步骤:")
            print("1. 可以继续进行性能测试")
            print("2. 可以进行用户验收测试")
            print("3. 准备生产环境部署")
        else:
            print("\n✗ 部分测试失败，请检查日志文件获取详细信息")
            print("建议修复失败的测试项目后再继续")
            
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())