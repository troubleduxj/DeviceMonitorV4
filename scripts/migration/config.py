#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一采集器数据迁移配置文件

本文件包含数据迁移脚本的所有配置参数，包括数据库连接、
备份设置、日志配置、迁移选项等。

作者: DeviceMonitor开发团队
创建时间: 2024-12-01
"""

import os
from pathlib import Path
from typing import Dict, Any, List

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 迁移脚本目录
MIGRATION_DIR = Path(__file__).parent

# 备份目录
BACKUP_DIR = PROJECT_ROOT / "backup"

# 日志目录
LOG_DIR = PROJECT_ROOT / "logs" / "migration"

class MigrationConfig:
    """
    迁移配置类
    
    包含所有迁移相关的配置参数和设置。
    """
    
    # ==================== 数据库配置 ====================
    
    # 数据库连接配置（从环境变量或默认值获取）
    DATABASE_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'device_monitor'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600
    }
    
    # 数据库表名配置
    TABLE_NAMES = {
        # 原始表
        'collector_tasks': 'collector_tasks',
        'sync_jobs': 'sync_jobs',
        'sync_job_logs': 'sync_job_logs',
        'collector_execution_logs': 'collector_execution_logs',
        'collector_metrics': 'collector_metrics',
        'collector_alerts': 'collector_alerts',
        
        # 新统一表
        'collectors': 'collectors',
        'device_collectors': 'device_collectors',
        'api_collectors': 'api_collectors',
        'collector_execution_logs_new': 'collector_execution_logs',
        'collector_templates': 'collector_templates'
    }
    
    # ==================== 备份配置 ====================
    
    # 备份设置
    BACKUP_CONFIG = {
        'enabled': True,
        'base_dir': BACKUP_DIR,
        'compression': True,
        'retention_days': 30,
        'include_logs': True,
        'chunk_size': 10000  # 分块备份大小
    }
    
    # 需要备份的表
    BACKUP_TABLES = [
        'collector_tasks',
        'sync_jobs', 
        'sync_job_logs',
        'collector_execution_logs',
        'collector_metrics',
        'collector_alerts',
        'collectors',
        'device_collectors',
        'api_collectors',
        'collector_templates'
    ]
    
    # ==================== 日志配置 ====================
    
    # 日志配置
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'file_main': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': str(LOG_DIR / 'migration_main.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            },
            'file_device': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': str(LOG_DIR / 'migration_device_collectors.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            },
            'file_api': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': str(LOG_DIR / 'migration_api_collectors.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            },
            'file_rollback': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': str(LOG_DIR / 'rollback_migration.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            'migration.main': {
                'handlers': ['console', 'file_main'],
                'level': 'DEBUG',
                'propagate': False
            },
            'migration.device_collectors': {
                'handlers': ['console', 'file_device'],
                'level': 'DEBUG',
                'propagate': False
            },
            'migration.api_collectors': {
                'handlers': ['console', 'file_api'],
                'level': 'DEBUG',
                'propagate': False
            },
            'migration.rollback': {
                'handlers': ['console', 'file_rollback'],
                'level': 'DEBUG',
                'propagate': False
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
    
    # ==================== 迁移配置 ====================
    
    # 迁移选项
    MIGRATION_OPTIONS = {
        'batch_size': 1000,  # 批处理大小
        'max_retries': 3,    # 最大重试次数
        'retry_delay': 5,    # 重试延迟（秒）
        'timeout': 300,      # 操作超时（秒）
        'parallel_workers': 4,  # 并行工作线程数
        'memory_limit_mb': 512,  # 内存限制（MB）
        'progress_interval': 100,  # 进度报告间隔
        'validation_enabled': True,  # 是否启用数据验证
        'strict_mode': False,  # 严格模式（遇到错误立即停止）
        'skip_existing': True,  # 跳过已存在的记录
        'preserve_ids': False,  # 是否保留原始ID
        'create_indexes': True,  # 是否创建索引
        'analyze_tables': True   # 是否分析表统计信息
    }
    
    # 数据类型映射
    DATA_TYPE_MAPPING = {
        # 采集器类型映射
        'collector_type': {
            'modbus': 'MODBUS',
            'opcua': 'OPCUA', 
            'snmp': 'SNMP',
            'http': 'HTTP',
            'mqtt': 'MQTT',
            'tcp': 'TCP',
            'serial': 'SERIAL',
            'api': 'API',
            'database': 'DATABASE',
            'file': 'FILE'
        },
        
        # 状态映射
        'status': {
            'active': 'RUNNING',
            'inactive': 'STOPPED',
            'running': 'RUNNING',
            'stopped': 'STOPPED',
            'error': 'ERROR',
            'pending': 'PENDING',
            'disabled': 'DISABLED'
        },
        
        # 请求方法映射
        'request_method': {
            'get': 'GET',
            'post': 'POST',
            'put': 'PUT',
            'delete': 'DELETE',
            'patch': 'PATCH',
            'head': 'HEAD',
            'options': 'OPTIONS'
        }
    }
    
    # ==================== 验证配置 ====================
    
    # 数据验证规则
    VALIDATION_RULES = {
        'required_fields': {
            'collectors': ['name', 'collector_type', 'status'],
            'device_collectors': ['collector_id', 'device_id', 'device_type'],
            'api_collectors': ['collector_id', 'api_config']
        },
        
        'field_constraints': {
            'name': {'max_length': 255, 'min_length': 1},
            'description': {'max_length': 1000},
            'cron_expression': {'pattern': r'^[\s\*\d\/\,\-]+$'},
            'device_id': {'max_length': 100},
            'device_type': {'max_length': 50}
        },
        
        'data_integrity': {
            'check_foreign_keys': True,
            'check_unique_constraints': True,
            'check_data_types': True,
            'check_json_format': True
        }
    }
    
    # ==================== 性能配置 ====================
    
    # 性能优化设置
    PERFORMANCE_CONFIG = {
        'use_bulk_insert': True,
        'disable_triggers': False,
        'disable_foreign_keys': False,
        'use_transactions': True,
        'transaction_size': 1000,
        'vacuum_analyze': True,
        'parallel_degree': 2
    }
    
    # 索引配置
    INDEX_CONFIG = {
        'create_during_migration': False,  # 迁移过程中不创建索引
        'create_after_migration': True,   # 迁移完成后创建索引
        'drop_before_migration': False,   # 迁移前不删除索引
        'rebuild_after_migration': True   # 迁移后重建索引
    }
    
    # ==================== 错误处理配置 ====================
    
    # 错误处理设置
    ERROR_HANDLING = {
        'continue_on_error': True,  # 遇到错误是否继续
        'log_errors': True,         # 是否记录错误
        'error_threshold': 100,     # 错误阈值
        'rollback_on_failure': True, # 失败时是否回滚
        'save_error_records': True,  # 是否保存错误记录
        'error_file_path': str(LOG_DIR / 'migration_errors.json')
    }
    
    # ==================== 报告配置 ====================
    
    # 报告生成设置
    REPORT_CONFIG = {
        'generate_report': True,
        'report_format': 'json',  # json, html, csv
        'include_statistics': True,
        'include_errors': True,
        'include_warnings': True,
        'include_performance': True,
        'report_file_path': str(LOG_DIR / 'migration_report.json')
    }
    
    # ==================== 环境配置 ====================
    
    # 环境设置
    ENVIRONMENT = {
        'name': os.getenv('ENVIRONMENT', 'development'),
        'debug': os.getenv('DEBUG', 'false').lower() == 'true',
        'testing': os.getenv('TESTING', 'false').lower() == 'true',
        'production': os.getenv('PRODUCTION', 'false').lower() == 'true'
    }
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        获取数据库连接URL
        
        Returns:
            str: 数据库连接URL
        """
        config = cls.DATABASE_CONFIG
        return f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    
    @classmethod
    def ensure_directories(cls) -> None:
        """
        确保必要的目录存在
        """
        directories = [
            cls.BACKUP_CONFIG['base_dir'],
            LOG_DIR,
            LOG_DIR.parent
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_backup_path(cls, timestamp: str) -> Path:
        """
        获取备份路径
        
        Args:
            timestamp: 时间戳字符串
            
        Returns:
            Path: 备份目录路径
        """
        return cls.BACKUP_CONFIG['base_dir'] / f"migration_{timestamp}"
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """
        验证配置的有效性
        
        Returns:
            List[str]: 验证错误列表
        """
        errors = []
        
        # 验证数据库配置
        db_config = cls.DATABASE_CONFIG
        required_db_fields = ['host', 'port', 'database', 'username', 'password']
        for field in required_db_fields:
            if not db_config.get(field):
                errors.append(f"数据库配置缺少必需字段: {field}")
        
        # 验证目录权限
        try:
            cls.ensure_directories()
        except PermissionError as e:
            errors.append(f"目录权限错误: {e}")
        
        # 验证批处理大小
        batch_size = cls.MIGRATION_OPTIONS.get('batch_size', 0)
        if batch_size <= 0:
            errors.append("批处理大小必须大于0")
        
        return errors
    
    @classmethod
    def get_logger_config(cls, logger_name: str) -> Dict[str, Any]:
        """
        获取特定日志记录器的配置
        
        Args:
            logger_name: 日志记录器名称
            
        Returns:
            Dict[str, Any]: 日志记录器配置
        """
        return cls.LOGGING_CONFIG['loggers'].get(logger_name, cls.LOGGING_CONFIG['root'])
    
    @classmethod
    def is_development(cls) -> bool:
        """
        检查是否为开发环境
        
        Returns:
            bool: 是否为开发环境
        """
        return cls.ENVIRONMENT['name'] == 'development'
    
    @classmethod
    def is_production(cls) -> bool:
        """
        检查是否为生产环境
        
        Returns:
            bool: 是否为生产环境
        """
        return cls.ENVIRONMENT['name'] == 'production'
    
    @classmethod
    def get_migration_option(cls, key: str, default=None):
        """
        获取迁移选项值
        
        Args:
            key: 选项键名
            default: 默认值
            
        Returns:
            迁移选项值
        """
        return cls.MIGRATION_OPTIONS.get(key, default)


# 创建全局配置实例
config = MigrationConfig()

# 确保目录存在
config.ensure_directories()

# 验证配置
config_errors = config.validate_config()
if config_errors:
    print("配置验证错误:")
    for error in config_errors:
        print(f"  - {error}")
    print("请修复配置错误后重新运行脚本。")