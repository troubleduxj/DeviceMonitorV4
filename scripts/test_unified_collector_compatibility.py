#!/usr/bin/env python3
"""
统一采集器系统兼容性测试脚本

此脚本用于测试统一采集器系统的兼容性，包括：
1. 数据库版本兼容性测试
2. 配置格式兼容性测试
3. API接口兼容性测试
4. 数据迁移兼容性测试
5. 向后兼容性测试

使用方法:
    python scripts/test_unified_collector_compatibility.py
"""

import asyncio
import json
import logging
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_collector_compatibility_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CompatibilityTestResult:
    """兼容性测试结果类"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.error_message = None
        self.warnings = []
        self.details = {}
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def start(self):
        """开始测试"""
        self.start_time = time.time()
    
    def end(self, passed: bool, error_message: Optional[str] = None):
        """结束测试"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.passed = passed
        self.error_message = error_message
    
    def add_warning(self, warning: str):
        """添加警告"""
        self.warnings.append(warning)
    
    def add_detail(self, key: str, value: Any):
        """添加详细信息"""
        self.details[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'test_name': self.test_name,
            'passed': self.passed,
            'error_message': self.error_message,
            'warnings': self.warnings,
            'details': self.details,
            'duration': self.duration
        }


class UnifiedCollectorCompatibilityTest:
    """统一采集器兼容性测试类"""
    
    def __init__(self):
        self.test_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.test_results = {
            'test_info': {
                'timestamp': self.test_timestamp,
                'start_time': datetime.now().isoformat()
            },
            'compatibility_tests': {},
            'summary': {}
        }
        self.created_test_data = []
    
    async def test_database_schema_compatibility(self) -> CompatibilityTestResult:
        """测试数据库模式兼容性"""
        result = CompatibilityTestResult("database_schema_compatibility")
        result.start()
        
        try:
            from tortoise import connections
            
            db = connections.get('postgres')
            
            # 检查必需的表是否存在
            required_tables = [
                'api_collectors',
                'device_collectors', 
                'collector_config_templates',
                'collector_config_instances',
                'collector_execution_logs'
            ]
            
            existing_tables = []
            missing_tables = []
            
            for table in required_tables:
                try:
                    await db.execute_query(f"SELECT 1 FROM {table} LIMIT 1")
                    existing_tables.append(table)
                except Exception:
                    missing_tables.append(table)
            
            result.add_detail('existing_tables', existing_tables)
            result.add_detail('missing_tables', missing_tables)
            
            # 检查表结构
            table_schemas = {}
            for table in existing_tables:
                try:
                    schema_result = await db.execute_query(
                        "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = $1 ORDER BY ordinal_position",
                        [table]
                    )
                    table_schemas[table] = [{
                        'column_name': row[0],
                        'data_type': row[1],
                        'is_nullable': row[2]
                    } for row in schema_result[1]]
                except Exception as e:
                    result.add_warning(f"无法获取表 {table} 的结构: {e}")
            
            result.add_detail('table_schemas', table_schemas)
            
            # 检查关键字段
            critical_fields = {
                'api_collectors': ['id', 'name', 'collector_type', 'api_url'],
                'device_collectors': ['id', 'name', 'collector_type', 'device_id'],
                'collector_config_templates': ['id', 'name', 'collector_type'],
                'collector_config_instances': ['id', 'template_id', 'config_data']
            }
            
            field_compatibility = {}
            for table, fields in critical_fields.items():
                if table in table_schemas:
                    table_columns = [col['column_name'] for col in table_schemas[table]]
                    missing_fields = [field for field in fields if field not in table_columns]
                    field_compatibility[table] = {
                        'required_fields': fields,
                        'existing_fields': [field for field in fields if field in table_columns],
                        'missing_fields': missing_fields
                    }
                    
                    if missing_fields:
                        result.add_warning(f"表 {table} 缺少关键字段: {missing_fields}")
            
            result.add_detail('field_compatibility', field_compatibility)
            
            # 判断兼容性
            if missing_tables:
                result.end(False, f"缺少必需的表: {missing_tables}")
            elif any(info['missing_fields'] for info in field_compatibility.values()):
                result.end(False, "存在缺少关键字段的表")
            else:
                result.end(True)
            
        except Exception as e:
            result.end(False, f"数据库模式兼容性测试失败: {e}")
        
        return result
    
    async def test_config_format_compatibility(self) -> CompatibilityTestResult:
        """测试配置格式兼容性"""
        result = CompatibilityTestResult("config_format_compatibility")
        result.start()
        
        try:
            from app.models.unified_collector import ApiCollector, DeviceCollector, CollectorType
            
            # 测试不同格式的配置
            test_configs = [
                # 标准JSON格式
                {
                    'name': 'json_config_test',
                    'config': {"api_key": "test123", "timeout": 30, "retries": 3},
                    'format': 'json'
                },
                # 嵌套配置
                {
                    'name': 'nested_config_test',
                    'config': {
                        "auth": {"type": "bearer", "token": "abc123"},
                        "request": {"timeout": 60, "headers": {"User-Agent": "TestAgent"}}
                    },
                    'format': 'nested_json'
                },
                # 简单配置
                {
                    'name': 'simple_config_test',
                    'config': {"url": "http://test.com", "method": "GET"},
                    'format': 'simple'
                }
            ]
            
            config_test_results = []
            
            for test_config in test_configs:
                config_result = {
                    'name': test_config['name'],
                    'format': test_config['format'],
                    'success': False,
                    'error': None
                }
                
                try:
                    # 创建API采集器测试配置兼容性
                    collector = await ApiCollector.create(
                        name=f"compat_test_{test_config['name']}_{self.test_timestamp}",
                        display_name=f"兼容性测试 - {test_config['format']}",
                        description=f"测试{test_config['format']}格式配置兼容性",
                        collector_type=CollectorType.API,
                        cron_expression="0 0 * * * *",
                        timeout_seconds=300,
                        retry_count=3,
                        config=test_config['config'],
                        api_url="http://test.example.com/api",
                        request_method="GET",
                        auth_type="none"
                    )
                    
                    # 验证配置是否正确保存
                    saved_collector = await ApiCollector.get(id=collector.id)
                    if saved_collector.config == test_config['config']:
                        config_result['success'] = True
                        self.created_test_data.append(('api_collectors', collector.id))
                    else:
                        config_result['error'] = "配置保存后与原始配置不匹配"
                    
                except Exception as e:
                    config_result['error'] = str(e)
                
                config_test_results.append(config_result)
            
            result.add_detail('config_tests', config_test_results)
            
            # 检查成功率
            successful_tests = sum(1 for test in config_test_results if test['success'])
            total_tests = len(config_test_results)
            success_rate = (successful_tests / total_tests) * 100
            
            result.add_detail('success_rate', success_rate)
            result.add_detail('successful_tests', successful_tests)
            result.add_detail('total_tests', total_tests)
            
            if success_rate < 100:
                failed_formats = [test['format'] for test in config_test_results if not test['success']]
                result.add_warning(f"以下配置格式测试失败: {failed_formats}")
            
            result.end(success_rate >= 80, None if success_rate >= 80 else f"配置格式兼容性测试成功率过低: {success_rate}%")
            
        except Exception as e:
            result.end(False, f"配置格式兼容性测试失败: {e}")
        
        return result
    
    async def test_api_interface_compatibility(self) -> CompatibilityTestResult:
        """测试API接口兼容性"""
        result = CompatibilityTestResult("api_interface_compatibility")
        result.start()
        
        try:
            from app.models.unified_collector import ApiCollector, CollectorType
            
            # 测试不同的API接口配置
            api_test_cases = [
                {
                    'name': 'rest_api_test',
                    'api_url': 'http://api.example.com/rest/data',
                    'request_method': 'GET',
                    'request_headers': {'Content-Type': 'application/json'},
                    'auth_type': 'none'
                },
                {
                    'name': 'post_api_test',
                    'api_url': 'http://api.example.com/post/data',
                    'request_method': 'POST',
                    'request_headers': {'Content-Type': 'application/json', 'Accept': 'application/json'},
                    'auth_type': 'basic',
                    'auth_config': {'username': 'test', 'password': 'test123'}
                },
                {
                    'name': 'bearer_auth_test',
                    'api_url': 'http://api.example.com/secure/data',
                    'request_method': 'GET',
                    'request_headers': {'Authorization': 'Bearer token123'},
                    'auth_type': 'bearer'
                }
            ]
            
            api_test_results = []
            
            for test_case in api_test_cases:
                api_result = {
                    'name': test_case['name'],
                    'success': False,
                    'error': None,
                    'validation_passed': False
                }
                
                try:
                    # 创建API采集器
                    collector = await ApiCollector.create(
                        name=f"api_compat_{test_case['name']}_{self.test_timestamp}",
                        display_name=f"API兼容性测试 - {test_case['name']}",
                        description=f"测试{test_case['name']}接口兼容性",
                        collector_type=CollectorType.API,
                        cron_expression="0 0 * * * *",
                        timeout_seconds=300,
                        retry_count=3,
                        config=test_case.get('auth_config', {}),
                        api_url=test_case['api_url'],
                        request_method=test_case['request_method'],
                        request_headers=test_case['request_headers'],
                        auth_type=test_case['auth_type']
                    )
                    
                    # 验证创建的采集器
                    saved_collector = await ApiCollector.get(id=collector.id)
                    
                    # 验证字段
                    validation_checks = [
                        saved_collector.api_url == test_case['api_url'],
                        saved_collector.request_method == test_case['request_method'],
                        saved_collector.auth_type == test_case['auth_type']
                    ]
                    
                    if all(validation_checks):
                        api_result['validation_passed'] = True
                        api_result['success'] = True
                        self.created_test_data.append(('api_collectors', collector.id))
                    else:
                        api_result['error'] = "字段验证失败"
                    
                except Exception as e:
                    api_result['error'] = str(e)
                
                api_test_results.append(api_result)
            
            result.add_detail('api_tests', api_test_results)
            
            # 检查成功率
            successful_tests = sum(1 for test in api_test_results if test['success'])
            total_tests = len(api_test_results)
            success_rate = (successful_tests / total_tests) * 100
            
            result.add_detail('success_rate', success_rate)
            result.add_detail('successful_tests', successful_tests)
            result.add_detail('total_tests', total_tests)
            
            if success_rate < 100:
                failed_apis = [test['name'] for test in api_test_results if not test['success']]
                result.add_warning(f"以下API接口测试失败: {failed_apis}")
            
            result.end(success_rate >= 90, None if success_rate >= 90 else f"API接口兼容性测试成功率过低: {success_rate}%")
            
        except Exception as e:
            result.end(False, f"API接口兼容性测试失败: {e}")
        
        return result
    
    async def test_data_migration_compatibility(self) -> CompatibilityTestResult:
        """测试数据迁移兼容性"""
        result = CompatibilityTestResult("data_migration_compatibility")
        result.start()
        
        try:
            from tortoise import connections
            
            db = connections.get('postgres')
            
            # 检查迁移相关的表和数据
            migration_checks = {
                'backup_tables_exist': False,
                'migration_logs_exist': False,
                'data_consistency': False,
                'rollback_capability': False
            }
            
            # 检查备份表是否存在
            backup_tables = ['collector_tasks_backup', 'sync_jobs_backup']
            existing_backup_tables = []
            
            for table in backup_tables:
                try:
                    await db.execute_query(f"SELECT 1 FROM {table} LIMIT 1")
                    existing_backup_tables.append(table)
                except Exception:
                    pass
            
            migration_checks['backup_tables_exist'] = len(existing_backup_tables) > 0
            result.add_detail('existing_backup_tables', existing_backup_tables)
            
            # 检查数据一致性
            try:
                # 检查采集器数据
                api_count = await db.execute_query("SELECT COUNT(*) FROM api_collectors")
                device_count = await db.execute_query("SELECT COUNT(*) FROM device_collectors")
                
                total_collectors = api_count[1][0][0] + device_count[1][0][0]
                
                result.add_detail('api_collectors_count', api_count[1][0][0])
                result.add_detail('device_collectors_count', device_count[1][0][0])
                result.add_detail('total_collectors', total_collectors)
                
                # 如果有数据，认为迁移已完成且数据一致
                if total_collectors > 0:
                    migration_checks['data_consistency'] = True
                
            except Exception as e:
                result.add_warning(f"数据一致性检查失败: {e}")
            
            # 检查回滚能力（检查回滚脚本是否存在）
            rollback_script_path = os.path.join(os.path.dirname(__file__), 'migration', 'rollback_migration.py')
            if os.path.exists(rollback_script_path):
                migration_checks['rollback_capability'] = True
                result.add_detail('rollback_script_exists', True)
            else:
                result.add_detail('rollback_script_exists', False)
                result.add_warning("回滚脚本不存在")
            
            result.add_detail('migration_checks', migration_checks)
            
            # 计算兼容性分数
            passed_checks = sum(1 for check in migration_checks.values() if check)
            total_checks = len(migration_checks)
            compatibility_score = (passed_checks / total_checks) * 100
            
            result.add_detail('compatibility_score', compatibility_score)
            result.add_detail('passed_checks', passed_checks)
            result.add_detail('total_checks', total_checks)
            
            if compatibility_score < 75:
                result.add_warning(f"迁移兼容性分数较低: {compatibility_score}%")
            
            result.end(compatibility_score >= 60, None if compatibility_score >= 60 else f"数据迁移兼容性测试失败，分数: {compatibility_score}%")
            
        except Exception as e:
            result.end(False, f"数据迁移兼容性测试失败: {e}")
        
        return result
    
    async def test_backward_compatibility(self) -> CompatibilityTestResult:
        """测试向后兼容性"""
        result = CompatibilityTestResult("backward_compatibility")
        result.start()
        
        try:
            from tortoise import connections
            
            db = connections.get('postgres')
            
            # 检查旧版本表是否仍然存在且可访问
            legacy_tables = ['collector_tasks', 'sync_jobs']
            legacy_compatibility = {}
            
            for table in legacy_tables:
                table_info = {
                    'exists': False,
                    'accessible': False,
                    'record_count': 0,
                    'error': None
                }
                
                try:
                    # 检查表是否存在
                    count_result = await db.execute_query(f"SELECT COUNT(*) FROM {table}")
                    table_info['exists'] = True
                    table_info['accessible'] = True
                    table_info['record_count'] = count_result[1][0][0]
                    
                except Exception as e:
                    table_info['error'] = str(e)
                    if "does not exist" in str(e).lower():
                        table_info['exists'] = False
                    else:
                        table_info['exists'] = True
                        table_info['accessible'] = False
                
                legacy_compatibility[table] = table_info
            
            result.add_detail('legacy_tables', legacy_compatibility)
            
            # 检查是否有数据在旧表中
            legacy_data_exists = any(
                info['accessible'] and info['record_count'] > 0 
                for info in legacy_compatibility.values()
            )
            
            result.add_detail('legacy_data_exists', legacy_data_exists)
            
            # 检查新旧系统是否可以共存
            coexistence_possible = True
            coexistence_issues = []
            
            # 如果旧表存在且有数据，但新表也有数据，可能存在数据不一致
            if legacy_data_exists:
                try:
                    new_api_count = await db.execute_query("SELECT COUNT(*) FROM api_collectors")
                    new_device_count = await db.execute_query("SELECT COUNT(*) FROM device_collectors")
                    
                    new_total = new_api_count[1][0][0] + new_device_count[1][0][0]
                    
                    if new_total > 0:
                        result.add_warning("新旧系统都有数据，可能存在数据不一致")
                        coexistence_issues.append("数据重复风险")
                    
                except Exception as e:
                    coexistence_issues.append(f"无法检查新系统数据: {e}")
            
            result.add_detail('coexistence_possible', coexistence_possible)
            result.add_detail('coexistence_issues', coexistence_issues)
            
            # 评估向后兼容性
            compatibility_factors = {
                'legacy_tables_accessible': sum(1 for info in legacy_compatibility.values() if info['accessible']),
                'total_legacy_tables': len(legacy_tables),
                'coexistence_safe': len(coexistence_issues) == 0
            }
            
            result.add_detail('compatibility_factors', compatibility_factors)
            
            # 计算兼容性分数
            accessibility_score = (compatibility_factors['legacy_tables_accessible'] / compatibility_factors['total_legacy_tables']) * 70
            coexistence_score = 30 if compatibility_factors['coexistence_safe'] else 0
            
            total_score = accessibility_score + coexistence_score
            result.add_detail('backward_compatibility_score', total_score)
            
            if total_score < 70:
                result.add_warning(f"向后兼容性分数较低: {total_score}%")
            
            result.end(total_score >= 50, None if total_score >= 50 else f"向后兼容性测试失败，分数: {total_score}%")
            
        except Exception as e:
            result.end(False, f"向后兼容性测试失败: {e}")
        
        return result
    
    async def cleanup_test_data(self):
        """清理测试数据"""
        logger.info("清理兼容性测试数据...")
        
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
    
    async def run_all_compatibility_tests(self) -> bool:
        """运行所有兼容性测试"""
        logger.info("开始统一采集器系统兼容性测试...")
        logger.info(f"测试时间戳: {self.test_timestamp}")
        
        test_functions = [
            ('database_schema', self.test_database_schema_compatibility),
            ('config_format', self.test_config_format_compatibility),
            ('api_interface', self.test_api_interface_compatibility),
            ('data_migration', self.test_data_migration_compatibility),
            ('backward_compatibility', self.test_backward_compatibility)
        ]
        
        try:
            for test_name, test_func in test_functions:
                logger.info(f"\n=== {test_name.upper()} 兼容性测试 ===")
                
                test_result = await test_func()
                self.test_results['compatibility_tests'][test_name] = test_result.to_dict()
                
                if test_result.passed:
                    logger.info(f"✓ {test_name} 测试通过")
                else:
                    logger.error(f"✗ {test_name} 测试失败: {test_result.error_message}")
                
                if test_result.warnings:
                    for warning in test_result.warnings:
                        logger.warning(f"⚠ {warning}")
            
            # 清理测试数据
            await self.cleanup_test_data()
            
            # 生成测试摘要
            self.generate_test_summary()
            
            # 输出测试结果
            logger.info("\n" + "="*60)
            logger.info("兼容性测试结果汇总:")
            
            passed_tests = 0
            total_tests = len(test_functions)
            
            for test_name, test_data in self.test_results['compatibility_tests'].items():
                status = "✓ 通过" if test_data['passed'] else "✗ 失败"
                logger.info(f"  {test_name}: {status}")
                if test_data['passed']:
                    passed_tests += 1
                if test_data['warnings']:
                    logger.info(f"    警告数: {len(test_data['warnings'])}")
            
            success_rate = (passed_tests / total_tests) * 100
            logger.info(f"\n总体成功率: {success_rate:.1f}% ({passed_tests}/{total_tests})")
            logger.info("\n" + self.test_results['summary']['overall_assessment'])
            logger.info("="*60)
            
            # 保存测试报告
            report_file = f"unified_collector_compatibility_report_{self.test_timestamp}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            logger.info(f"兼容性测试报告已保存: {report_file}")
            
            return success_rate >= 60  # 60%以上认为兼容性可接受
            
        except Exception as e:
            logger.error(f"兼容性测试过程中发生严重错误: {e}")
            return False
    
    def generate_test_summary(self):
        """生成测试摘要"""
        summary = {
            'test_count': len(self.test_results['compatibility_tests']),
            'end_time': datetime.now().isoformat(),
            'passed_tests': [],
            'failed_tests': [],
            'warnings_count': 0,
            'recommendations': [],
            'compatibility_issues': [],
            'overall_assessment': ''
        }
        
        # 分析测试结果
        for test_name, test_data in self.test_results['compatibility_tests'].items():
            if test_data['passed']:
                summary['passed_tests'].append(test_name)
            else:
                summary['failed_tests'].append(test_name)
                summary['compatibility_issues'].append(f"{test_name}: {test_data['error_message']}")
            
            summary['warnings_count'] += len(test_data['warnings'])
        
        # 生成建议
        if summary['failed_tests']:
            if 'database_schema' in summary['failed_tests']:
                summary['recommendations'].append("检查数据库模式，确保所有必需的表和字段存在")
            if 'config_format' in summary['failed_tests']:
                summary['recommendations'].append("验证配置格式处理逻辑，确保支持各种配置格式")
            if 'api_interface' in summary['failed_tests']:
                summary['recommendations'].append("检查API接口实现，确保支持不同的认证和请求方式")
            if 'data_migration' in summary['failed_tests']:
                summary['recommendations'].append("完善数据迁移流程，确保数据完整性和回滚能力")
            if 'backward_compatibility' in summary['failed_tests']:
                summary['recommendations'].append("改进向后兼容性，确保新旧系统可以平滑过渡")
        
        # 总体评估
        passed_count = len(summary['passed_tests'])
        total_count = summary['test_count']
        success_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
        
        if success_rate >= 90:
            summary['overall_assessment'] = "✓ 兼容性测试优秀，系统兼容性良好"
        elif success_rate >= 70:
            summary['overall_assessment'] = "✓ 兼容性测试良好，存在少量兼容性问题"
        elif success_rate >= 50:
            summary['overall_assessment'] = "⚠ 兼容性测试一般，需要解决一些兼容性问题"
        else:
            summary['overall_assessment'] = "✗ 兼容性测试较差，存在严重兼容性问题"
        
        self.test_results['summary'] = summary


async def main():
    """主函数"""
    # 初始化 Tortoise ORM
    from app.settings.config import settings
    
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    try:
        test_runner = UnifiedCollectorCompatibilityTest()
        success = await test_runner.run_all_compatibility_tests()
        
        if success:
            print("\n✓ 兼容性测试完成！")
            print("\n后续步骤:")
            print("1. 查看兼容性测试报告分析结果")
            print("2. 根据建议解决兼容性问题")
            print("3. 准备系统上线部署")
        else:
            print("\n⚠ 兼容性测试发现问题，请查看报告并解决相关问题")
            
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())