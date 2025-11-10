#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一采集器数据迁移模块初始化文件

本模块提供数据迁移的初始化功能，包括：
- 环境检查和依赖验证
- 目录结构创建
- 数据库连接测试
- 配置验证
- 模块导入

作者: DeviceMonitor开发团队
创建时间: 2024-12-01
"""

import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'app'))

# 版本信息
__version__ = '1.0.0'
__author__ = 'DeviceMonitor开发团队'
__email__ = 'dev@devicemonitor.com'
__description__ = '统一采集器数据迁移工具'

# 模块导入
try:
    from .config import MigrationConfig, config
    from .utils import (
        MigrationStats,
        ProgressTracker,
        DataValidator,
        DataCleaner,
        BackupManager,
        PerformanceMonitor,
        ReportGenerator,
        DatabaseUtils,
        setup_logging,
        format_duration,
        format_size,
        retry_on_failure
    )
except ImportError as e:
    print(f"模块导入失败: {e}")
    print("请确保所有依赖已正确安装")
    sys.exit(1)


class MigrationEnvironment:
    """
    迁移环境管理器
    
    负责初始化和管理迁移环境，包括依赖检查、
    目录创建、数据库连接测试等。
    """
    
    def __init__(self):
        self.logger = None
        self.initialized = False
        self.check_results = {}
    
    def initialize(self, verbose: bool = False) -> bool:
        """
        初始化迁移环境
        
        Args:
            verbose: 是否显示详细信息
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 设置日志
            self.logger = setup_logging('migration.init')
            
            if verbose:
                self.logger.info("开始初始化迁移环境...")
            
            # 执行各项检查
            checks = [
                ('Python版本检查', self._check_python_version),
                ('依赖包检查', self._check_dependencies),
                ('目录结构检查', self._check_directories),
                ('配置文件检查', self._check_configuration),
                ('数据库连接检查', self._check_database_connection),
                ('权限检查', self._check_permissions)
            ]
            
            all_passed = True
            for check_name, check_func in checks:
                if verbose:
                    self.logger.info(f"执行 {check_name}...")
                
                try:
                    result = check_func()
                    self.check_results[check_name] = result
                    
                    if result['success']:
                        if verbose:
                            self.logger.info(f"✓ {check_name} 通过")
                    else:
                        self.logger.error(f"✗ {check_name} 失败: {result['message']}")
                        all_passed = False
                        
                        # 如果有建议的解决方案，显示它们
                        if 'suggestions' in result:
                            for suggestion in result['suggestions']:
                                self.logger.info(f"  建议: {suggestion}")
                                
                except Exception as e:
                    self.logger.error(f"✗ {check_name} 执行失败: {e}")
                    self.check_results[check_name] = {
                        'success': False,
                        'message': str(e)
                    }
                    all_passed = False
            
            if all_passed:
                self.initialized = True
                if verbose:
                    self.logger.info("✓ 迁移环境初始化成功")
            else:
                if verbose:
                    self.logger.error("✗ 迁移环境初始化失败，请解决上述问题后重试")
            
            return all_passed
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"初始化过程中发生错误: {e}")
            else:
                print(f"初始化过程中发生错误: {e}")
            return False
    
    def _check_python_version(self) -> Dict[str, Any]:
        """
        检查Python版本
        
        Returns:
            Dict[str, Any]: 检查结果
        """
        required_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version >= required_version:
            return {
                'success': True,
                'message': f'Python版本 {sys.version} 满足要求',
                'current_version': current_version,
                'required_version': required_version
            }
        else:
            return {
                'success': False,
                'message': f'Python版本过低，当前: {current_version}, 要求: {required_version}+',
                'current_version': current_version,
                'required_version': required_version,
                'suggestions': [
                    f'请升级Python到 {required_version[0]}.{required_version[1]} 或更高版本',
                    '可以使用 pyenv 或 conda 管理Python版本'
                ]
            }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """
        检查依赖包
        
        Returns:
            Dict[str, Any]: 检查结果
        """
        required_packages = [
            'sqlalchemy',
            'psycopg2',
            'psutil',
            'alembic'
        ]
        
        missing_packages = []
        installed_packages = {}
        
        for package in required_packages:
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                installed_packages[package] = version
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            return {
                'success': True,
                'message': '所有依赖包已安装',
                'installed_packages': installed_packages
            }
        else:
            return {
                'success': False,
                'message': f'缺少依赖包: {", ".join(missing_packages)}',
                'missing_packages': missing_packages,
                'installed_packages': installed_packages,
                'suggestions': [
                    f'运行: pip install {", ".join(missing_packages)}',
                    '或者运行: pip install -r requirements.txt'
                ]
            }
    
    def _check_directories(self) -> Dict[str, Any]:
        """
        检查目录结构
        
        Returns:
            Dict[str, Any]: 检查结果
        """
        try:
            # 确保目录存在
            config.ensure_directories()
            
            # 检查关键目录
            directories = {
                '备份目录': config.BACKUP_CONFIG['base_dir'],
                '日志目录': Path(config.LOGGING_CONFIG['handlers']['file_main']['filename']).parent,
                '迁移脚本目录': Path(__file__).parent
            }
            
            created_dirs = []
            for name, path in directories.items():
                path = Path(path)
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(str(path))
            
            return {
                'success': True,
                'message': '目录结构检查完成',
                'directories': {name: str(path) for name, path in directories.items()},
                'created_directories': created_dirs
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'目录创建失败: {e}',
                'suggestions': [
                    '检查文件系统权限',
                    '确保有足够的磁盘空间',
                    '检查路径是否有效'
                ]
            }
    
    def _check_configuration(self) -> Dict[str, Any]:
        """
        检查配置文件
        
        Returns:
            Dict[str, Any]: 检查结果
        """
        try:
            # 验证配置
            config_errors = config.validate_config()
            
            if not config_errors:
                return {
                    'success': True,
                    'message': '配置验证通过',
                    'database_url': config.get_database_url(),
                    'environment': config.ENVIRONMENT['name']
                }
            else:
                return {
                    'success': False,
                    'message': '配置验证失败',
                    'errors': config_errors,
                    'suggestions': [
                        '检查环境变量设置',
                        '验证数据库连接参数',
                        '确保配置文件格式正确'
                    ]
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'配置检查失败: {e}',
                'suggestions': [
                    '检查配置文件是否存在',
                    '验证配置文件语法',
                    '确保所有必需的配置项都已设置'
                ]
            }
    
    def _check_database_connection(self) -> Dict[str, Any]:
        """
        检查数据库连接
        
        Returns:
            Dict[str, Any]: 检查结果
        """
        try:
            from sqlalchemy import create_engine, text
            
            # 创建数据库引擎
            engine = create_engine(config.get_database_url())
            
            # 测试连接
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                db_version = result.fetchone()[0]
            
            # 检查必要的表是否存在
            table_checks = {}
            required_tables = ['collector_tasks', 'sync_jobs']
            
            with engine.connect() as conn:
                for table in required_tables:
                    result = conn.execute(text(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"
                    ), {'table_name': table})
                    table_checks[table] = result.fetchone()[0]
            
            missing_tables = [table for table, exists in table_checks.items() if not exists]
            
            if missing_tables:
                return {
                    'success': False,
                    'message': f'缺少必要的数据表: {", ".join(missing_tables)}',
                    'db_version': db_version,
                    'table_checks': table_checks,
                    'suggestions': [
                        '确保数据库已正确初始化',
                        '运行数据库迁移脚本',
                        '检查数据库用户权限'
                    ]
                }
            else:
                return {
                    'success': True,
                    'message': '数据库连接正常',
                    'db_version': db_version,
                    'table_checks': table_checks
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'数据库连接失败: {e}',
                'suggestions': [
                    '检查数据库服务是否运行',
                    '验证数据库连接参数',
                    '确保网络连接正常',
                    '检查数据库用户权限'
                ]
            }
    
    def _check_permissions(self) -> Dict[str, Any]:
        """
        检查文件系统权限
        
        Returns:
            Dict[str, Any]: 检查结果
        """
        try:
            import tempfile
            
            # 检查关键目录的读写权限
            directories_to_check = [
                config.BACKUP_CONFIG['base_dir'],
                Path(config.LOGGING_CONFIG['handlers']['file_main']['filename']).parent
            ]
            
            permission_results = {}
            
            for directory in directories_to_check:
                directory = Path(directory)
                try:
                    # 测试写权限
                    with tempfile.NamedTemporaryFile(dir=directory, delete=True) as tmp:
                        tmp.write(b'test')
                    permission_results[str(directory)] = {'read': True, 'write': True}
                except PermissionError:
                    permission_results[str(directory)] = {'read': True, 'write': False}
                except Exception as e:
                    permission_results[str(directory)] = {'read': False, 'write': False, 'error': str(e)}
            
            # 检查是否有权限问题
            permission_issues = []
            for path, perms in permission_results.items():
                if not perms.get('write', False):
                    permission_issues.append(f'{path}: 无写权限')
                if not perms.get('read', False):
                    permission_issues.append(f'{path}: 无读权限')
            
            if not permission_issues:
                return {
                    'success': True,
                    'message': '文件系统权限检查通过',
                    'permission_results': permission_results
                }
            else:
                return {
                    'success': False,
                    'message': '文件系统权限不足',
                    'permission_results': permission_results,
                    'issues': permission_issues,
                    'suggestions': [
                        '使用管理员权限运行脚本',
                        '修改目录权限: chmod 755 <directory>',
                        '检查磁盘空间是否充足'
                    ]
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'权限检查失败: {e}',
                'suggestions': [
                    '检查文件系统状态',
                    '确保目录存在且可访问'
                ]
            }
    
    def get_check_results(self) -> Dict[str, Any]:
        """
        获取检查结果
        
        Returns:
            Dict[str, Any]: 所有检查结果
        """
        return self.check_results.copy()
    
    def is_ready(self) -> bool:
        """
        检查环境是否就绪
        
        Returns:
            bool: 环境是否就绪
        """
        return self.initialized


# 创建全局环境管理器实例
environment = MigrationEnvironment()


def init_migration_environment(verbose: bool = False) -> bool:
    """
    初始化迁移环境
    
    Args:
        verbose: 是否显示详细信息
        
    Returns:
        bool: 初始化是否成功
    """
    return environment.initialize(verbose=verbose)


def check_environment() -> bool:
    """
    检查环境是否就绪
    
    Returns:
        bool: 环境是否就绪
    """
    return environment.is_ready()


def get_environment_info() -> Dict[str, Any]:
    """
    获取环境信息
    
    Returns:
        Dict[str, Any]: 环境信息
    """
    return {
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'initialized': environment.is_ready(),
        'check_results': environment.get_check_results(),
        'python_version': sys.version,
        'platform': sys.platform
    }


# 模块级别的导出
__all__ = [
    # 版本信息
    '__version__',
    '__author__',
    '__description__',
    
    # 配置
    'MigrationConfig',
    'config',
    
    # 工具类
    'MigrationStats',
    'ProgressTracker',
    'DataValidator',
    'DataCleaner',
    'BackupManager',
    'PerformanceMonitor',
    'ReportGenerator',
    'DatabaseUtils',
    
    # 环境管理
    'MigrationEnvironment',
    'environment',
    'init_migration_environment',
    'check_environment',
    'get_environment_info',
    
    # 工具函数
    'setup_logging',
    'format_duration',
    'format_size',
    'retry_on_failure'
]


if __name__ == '__main__':
    # 如果直接运行此文件，执行环境检查
    print(f"统一采集器数据迁移工具 v{__version__}")
    print(f"作者: {__author__}")
    print(f"描述: {__description__}")
    print()
    
    print("正在检查迁移环境...")
    success = init_migration_environment(verbose=True)
    
    if success:
        print("\n✓ 环境检查完成，可以开始数据迁移")
        sys.exit(0)
    else:
        print("\n✗ 环境检查失败，请解决上述问题后重试")
        sys.exit(1)