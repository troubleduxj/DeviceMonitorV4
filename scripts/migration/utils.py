#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一采集器数据迁移工具模块

本模块包含数据迁移过程中使用的通用工具函数，包括：
- 数据验证和清理
- 备份和恢复
- 进度跟踪
- 错误处理
- 性能监控
- 报告生成

作者: DeviceMonitor开发团队
创建时间: 2024-12-01
"""

import json
import logging
import time
import hashlib
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import psutil
import re

from config import MigrationConfig


@dataclass
class MigrationStats:
    """
    迁移统计信息
    """
    start_time: datetime
    end_time: Optional[datetime] = None
    total_records: int = 0
    processed_records: int = 0
    success_records: int = 0
    error_records: int = 0
    skipped_records: int = 0
    errors: List[Dict[str, Any]] = None
    warnings: List[str] = None
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.performance_metrics is None:
            self.performance_metrics = {}
    
    @property
    def duration(self) -> Optional[timedelta]:
        """获取迁移持续时间"""
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def success_rate(self) -> float:
        """获取成功率"""
        if self.processed_records == 0:
            return 0.0
        return (self.success_records / self.processed_records) * 100
    
    @property
    def error_rate(self) -> float:
        """获取错误率"""
        if self.processed_records == 0:
            return 0.0
        return (self.error_records / self.processed_records) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['duration_seconds'] = self.duration.total_seconds() if self.duration else None
        data['success_rate'] = self.success_rate
        data['error_rate'] = self.error_rate
        return data


class ProgressTracker:
    """
    进度跟踪器
    """
    
    def __init__(self, total: int, description: str = "", logger: Optional[logging.Logger] = None):
        self.total = total
        self.current = 0
        self.description = description
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = time.time()
        self.last_update = 0
        self.update_interval = MigrationConfig.get_migration_option('progress_interval', 100)
    
    def update(self, increment: int = 1) -> None:
        """更新进度"""
        self.current += increment
        
        # 按间隔报告进度
        if self.current - self.last_update >= self.update_interval or self.current >= self.total:
            self._report_progress()
            self.last_update = self.current
    
    def _report_progress(self) -> None:
        """报告进度"""
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            elapsed = time.time() - self.start_time
            
            if self.current > 0:
                eta = (elapsed / self.current) * (self.total - self.current)
                eta_str = f", ETA: {timedelta(seconds=int(eta))}"
            else:
                eta_str = ""
            
            self.logger.info(
                f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%) "
                f"- 耗时: {timedelta(seconds=int(elapsed))}{eta_str}"
            )
    
    def finish(self) -> None:
        """完成进度跟踪"""
        self.current = self.total
        elapsed = time.time() - self.start_time
        self.logger.info(
            f"{self.description}: 完成 {self.total} 条记录 - "
            f"总耗时: {timedelta(seconds=int(elapsed))}"
        )


class DataValidator:
    """
    数据验证器
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.validation_rules = MigrationConfig.VALIDATION_RULES
    
    def validate_record(self, record: Dict[str, Any], table_name: str) -> Tuple[bool, List[str]]:
        """
        验证单条记录
        
        Args:
            record: 记录数据
            table_name: 表名
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误列表)
        """
        errors = []
        
        # 检查必需字段
        required_fields = self.validation_rules['required_fields'].get(table_name, [])
        for field in required_fields:
            if field not in record or record[field] is None:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查字段约束
        field_constraints = self.validation_rules['field_constraints']
        for field, value in record.items():
            if field in field_constraints and value is not None:
                constraint = field_constraints[field]
                
                # 检查长度约束
                if isinstance(value, str):
                    if 'max_length' in constraint and len(value) > constraint['max_length']:
                        errors.append(f"字段 {field} 长度超过限制: {len(value)} > {constraint['max_length']}")
                    if 'min_length' in constraint and len(value) < constraint['min_length']:
                        errors.append(f"字段 {field} 长度不足: {len(value)} < {constraint['min_length']}")
                
                # 检查模式匹配
                if 'pattern' in constraint and isinstance(value, str):
                    if not re.match(constraint['pattern'], value):
                        errors.append(f"字段 {field} 格式不匹配: {value}")
        
        # 检查JSON格式
        if self.validation_rules['data_integrity']['check_json_format']:
            for field, value in record.items():
                if field.endswith('_config') or field.endswith('_mapping') and isinstance(value, str):
                    try:
                        json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        errors.append(f"字段 {field} JSON格式无效: {value}")
        
        return len(errors) == 0, errors
    
    def validate_batch(self, records: List[Dict[str, Any]], table_name: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        批量验证记录
        
        Args:
            records: 记录列表
            table_name: 表名
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (有效记录, 无效记录)
        """
        valid_records = []
        invalid_records = []
        
        for i, record in enumerate(records):
            is_valid, errors = self.validate_record(record, table_name)
            
            if is_valid:
                valid_records.append(record)
            else:
                invalid_record = {
                    'index': i,
                    'record': record,
                    'errors': errors
                }
                invalid_records.append(invalid_record)
                self.logger.warning(f"记录验证失败 (索引 {i}): {', '.join(errors)}")
        
        return valid_records, invalid_records


class DataCleaner:
    """
    数据清理器
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.type_mapping = MigrationConfig.DATA_TYPE_MAPPING
    
    def clean_record(self, record: Dict[str, Any], table_name: str) -> Dict[str, Any]:
        """
        清理单条记录
        
        Args:
            record: 原始记录
            table_name: 表名
            
        Returns:
            Dict[str, Any]: 清理后的记录
        """
        cleaned = record.copy()
        
        # 清理字符串字段
        for key, value in cleaned.items():
            if isinstance(value, str):
                # 去除首尾空白
                cleaned[key] = value.strip()
                
                # 空字符串转为None
                if cleaned[key] == '':
                    cleaned[key] = None
        
        # 应用类型映射
        if table_name in ['collectors', 'device_collectors', 'api_collectors']:
            # 映射采集器类型
            if 'collector_type' in cleaned and cleaned['collector_type']:
                original_type = cleaned['collector_type'].lower()
                if original_type in self.type_mapping['collector_type']:
                    cleaned['collector_type'] = self.type_mapping['collector_type'][original_type]
            
            # 映射状态
            if 'status' in cleaned and cleaned['status']:
                original_status = cleaned['status'].lower()
                if original_status in self.type_mapping['status']:
                    cleaned['status'] = self.type_mapping['status'][original_status]
        
        if table_name == 'api_collectors':
            # 映射请求方法
            if 'api_config' in cleaned and isinstance(cleaned['api_config'], dict):
                api_config = cleaned['api_config']
                if 'method' in api_config and api_config['method']:
                    original_method = api_config['method'].lower()
                    if original_method in self.type_mapping['request_method']:
                        api_config['method'] = self.type_mapping['request_method'][original_method]
        
        return cleaned
    
    def clean_batch(self, records: List[Dict[str, Any]], table_name: str) -> List[Dict[str, Any]]:
        """
        批量清理记录
        
        Args:
            records: 记录列表
            table_name: 表名
            
        Returns:
            List[Dict[str, Any]]: 清理后的记录列表
        """
        return [self.clean_record(record, table_name) for record in records]


class BackupManager:
    """
    备份管理器
    """
    
    def __init__(self, backup_dir: Path, logger: Optional[logging.Logger] = None):
        self.backup_dir = Path(backup_dir)
        self.logger = logger or logging.getLogger(__name__)
        self.config = MigrationConfig.BACKUP_CONFIG
    
    def create_backup(self, data: List[Dict[str, Any]], table_name: str, compress: bool = True) -> Path:
        """
        创建数据备份
        
        Args:
            data: 要备份的数据
            table_name: 表名
            compress: 是否压缩
            
        Returns:
            Path: 备份文件路径
        """
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{table_name}_{timestamp}.json"
        if compress:
            filename += ".gz"
        
        backup_file = self.backup_dir / filename
        
        # 写入备份数据
        backup_data = {
            'table_name': table_name,
            'timestamp': timestamp,
            'record_count': len(data),
            'data': data
        }
        
        if compress:
            with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        else:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"备份完成: {backup_file} ({len(data)} 条记录)")
        return backup_file
    
    def restore_backup(self, backup_file: Path) -> Tuple[str, List[Dict[str, Any]]]:
        """
        恢复备份数据
        
        Args:
            backup_file: 备份文件路径
            
        Returns:
            Tuple[str, List[Dict]]: (表名, 数据列表)
        """
        if not backup_file.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_file}")
        
        # 读取备份数据
        if backup_file.suffix == '.gz':
            with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
        else:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
        
        table_name = backup_data['table_name']
        data = backup_data['data']
        
        self.logger.info(f"恢复备份: {backup_file} ({len(data)} 条记录)")
        return table_name, data
    
    def list_backups(self, table_name: Optional[str] = None) -> List[Path]:
        """
        列出备份文件
        
        Args:
            table_name: 表名过滤（可选）
            
        Returns:
            List[Path]: 备份文件列表
        """
        if not self.backup_dir.exists():
            return []
        
        pattern = f"{table_name}_*.json*" if table_name else "*.json*"
        return sorted(self.backup_dir.glob(pattern), reverse=True)
    
    def cleanup_old_backups(self, retention_days: int = None) -> int:
        """
        清理旧备份文件
        
        Args:
            retention_days: 保留天数
            
        Returns:
            int: 删除的文件数量
        """
        if retention_days is None:
            retention_days = self.config['retention_days']
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        
        for backup_file in self.list_backups():
            # 从文件名提取时间戳
            try:
                parts = backup_file.stem.split('_')
                if len(parts) >= 3:
                    timestamp_str = f"{parts[-2]}_{parts[-1]}"
                    file_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    
                    if file_date < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1
                        self.logger.info(f"删除旧备份: {backup_file}")
            except (ValueError, IndexError) as e:
                self.logger.warning(f"无法解析备份文件时间戳: {backup_file} - {e}")
        
        return deleted_count


class PerformanceMonitor:
    """
    性能监控器
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None
        self.metrics = {}
    
    def start_monitoring(self) -> None:
        """开始监控"""
        self.start_time = time.time()
        self.metrics = {
            'start_time': self.start_time,
            'start_memory': psutil.virtual_memory().used,
            'start_cpu': psutil.cpu_percent()
        }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """停止监控并返回指标"""
        if self.start_time is None:
            return {}
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        end_cpu = psutil.cpu_percent()
        
        self.metrics.update({
            'end_time': end_time,
            'duration': end_time - self.start_time,
            'end_memory': end_memory,
            'memory_delta': end_memory - self.metrics['start_memory'],
            'end_cpu': end_cpu,
            'peak_memory': psutil.virtual_memory().used,
            'avg_cpu': (self.metrics['start_cpu'] + end_cpu) / 2
        })
        
        return self.metrics.copy()
    
    @contextmanager
    def monitor_operation(self, operation_name: str):
        """监控操作的上下文管理器"""
        self.logger.info(f"开始监控操作: {operation_name}")
        self.start_monitoring()
        
        try:
            yield
        finally:
            metrics = self.stop_monitoring()
            self.logger.info(
                f"操作完成: {operation_name} - "
                f"耗时: {metrics.get('duration', 0):.2f}秒, "
                f"内存变化: {metrics.get('memory_delta', 0) / 1024 / 1024:.2f}MB"
            )


class ReportGenerator:
    """
    报告生成器
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.config = MigrationConfig.REPORT_CONFIG
    
    def generate_migration_report(self, stats: MigrationStats, output_file: Optional[Path] = None) -> Path:
        """
        生成迁移报告
        
        Args:
            stats: 迁移统计信息
            output_file: 输出文件路径
            
        Returns:
            Path: 报告文件路径
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Path(self.config['report_file_path']).parent / f"migration_report_{timestamp}.json"
        
        # 生成报告数据
        report_data = {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0',
                'migration_type': 'unified_collector'
            },
            'summary': {
                'total_records': stats.total_records,
                'processed_records': stats.processed_records,
                'success_records': stats.success_records,
                'error_records': stats.error_records,
                'skipped_records': stats.skipped_records,
                'success_rate': stats.success_rate,
                'error_rate': stats.error_rate,
                'duration_seconds': stats.duration.total_seconds() if stats.duration else None,
                'start_time': stats.start_time.isoformat(),
                'end_time': stats.end_time.isoformat() if stats.end_time else None
            }
        }
        
        # 添加错误信息
        if self.config['include_errors'] and stats.errors:
            report_data['errors'] = stats.errors
        
        # 添加警告信息
        if self.config['include_warnings'] and stats.warnings:
            report_data['warnings'] = stats.warnings
        
        # 添加性能指标
        if self.config['include_performance'] and stats.performance_metrics:
            report_data['performance'] = stats.performance_metrics
        
        # 写入报告文件
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"迁移报告已生成: {output_file}")
        return output_file


class DatabaseUtils:
    """
    数据库工具类
    """
    
    @staticmethod
    def generate_id() -> str:
        """
        生成唯一ID
        
        Returns:
            str: 唯一ID
        """
        timestamp = str(int(time.time() * 1000000))
        random_str = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"{timestamp}_{random_str}"
    
    @staticmethod
    def safe_json_loads(value: Any, default: Dict = None) -> Dict[str, Any]:
        """
        安全的JSON解析
        
        Args:
            value: 要解析的值
            default: 默认值
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        if default is None:
            default = {}
        
        if value is None:
            return default
        
        if isinstance(value, dict):
            return value
        
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return default
        
        return default
    
    @staticmethod
    def safe_json_dumps(value: Any, default: str = '{}') -> str:
        """
        安全的JSON序列化
        
        Args:
            value: 要序列化的值
            default: 默认值
            
        Returns:
            str: JSON字符串
        """
        if value is None:
            return default
        
        if isinstance(value, str):
            # 验证是否为有效JSON
            try:
                json.loads(value)
                return value
            except (json.JSONDecodeError, TypeError):
                return default
        
        try:
            return json.dumps(value, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            return default


def setup_logging(config_name: str = 'migration.main') -> logging.Logger:
    """
    设置日志记录
    
    Args:
        config_name: 日志配置名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    import logging.config
    
    # 确保日志目录存在
    MigrationConfig.ensure_directories()
    
    # 配置日志
    logging.config.dictConfig(MigrationConfig.LOGGING_CONFIG)
    
    return logging.getLogger(config_name)


def format_duration(seconds: float) -> str:
    """
    格式化持续时间
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.2f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def format_size(bytes_size: int) -> str:
    """
    格式化文件大小
    
    Args:
        bytes_size: 字节大小
        
    Returns:
        str: 格式化的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}PB"


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff: 退避倍数
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator