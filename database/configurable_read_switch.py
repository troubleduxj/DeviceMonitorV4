#!/usr/bin/env python3
"""
配置化读取切换机制
实现动态的数据源切换，支持灰度发布、A/B测试和故障回退
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import asyncpg
from contextlib import asynccontextmanager
import threading
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('configurable_read_switch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SwitchStrategy(Enum):
    """切换策略枚举"""
    IMMEDIATE = "immediate"           # 立即切换
    GRADUAL = "gradual"              # 渐进切换
    CANARY = "canary"                # 金丝雀发布
    AB_TEST = "ab_test"              # A/B测试
    BLUE_GREEN = "blue_green"        # 蓝绿部署
    CONDITIONAL = "conditional"       # 条件切换

class ReadSource(Enum):
    """读取源枚举"""
    SOURCE = "source"                # 源表
    TARGET = "target"                # 目标表
    BOTH = "both"                    # 双读（用于验证）

class SwitchStatus(Enum):
    """切换状态枚举"""
    INACTIVE = "inactive"            # 未激活
    PREPARING = "preparing"          # 准备中
    ACTIVE = "active"                # 激活中
    COMPLETED = "completed"          # 已完成
    FAILED = "failed"                # 失败
    ROLLED_BACK = "rolled_back"      # 已回滚

@dataclass
class SwitchRule:
    """切换规则"""
    rule_id: str
    rule_name: str
    table_name: str
    source_table: str
    target_table: str
    strategy: SwitchStrategy
    conditions: Dict[str, Any]
    rollback_conditions: Dict[str, Any]
    enabled: bool = True
    priority: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class SwitchConfig:
    """切换配置"""
    config_id: str
    table_name: str
    current_source: ReadSource
    target_source: ReadSource
    strategy: SwitchStrategy
    switch_percentage: float = 0.0    # 切换百分比（0-100）
    user_groups: List[str] = None     # 用户组（用于A/B测试）
    conditions: Dict[str, Any] = None
    rollback_enabled: bool = True
    auto_rollback_threshold: float = 0.05  # 自动回滚错误率阈值
    status: SwitchStatus = SwitchStatus.INACTIVE
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.user_groups is None:
            self.user_groups = []
        if self.conditions is None:
            self.conditions = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class SwitchMetrics:
    """切换指标"""
    config_id: str
    total_requests: int = 0
    source_requests: int = 0
    target_requests: int = 0
    source_errors: int = 0
    target_errors: int = 0
    source_avg_latency: float = 0.0
    target_avg_latency: float = 0.0
    switch_rate: float = 0.0
    error_rate: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

class ConfigurableReadSwitch:
    """配置化读取切换器"""
    
    def __init__(self, db_url: str, config_file: str = None):
        self.db_url = db_url
        self.connection: Optional[asyncpg.Connection] = None
        self.config_file = config_file or "database/read_switch_configs.json"
        self.switch_configs: Dict[str, SwitchConfig] = {}
        self.switch_rules: Dict[str, SwitchRule] = {}
        self.metrics: Dict[str, SwitchMetrics] = {}
        self.request_handlers: Dict[str, Callable] = {}
        self.error_handlers: Dict[str, Callable] = {}
        
        # 线程锁
        self._lock = threading.RLock()
        
        # 加载配置
        self._load_configurations()
    
    def _load_configurations(self):
        """加载切换配置"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 加载切换配置
                for config_data in data.get('switch_configs', []):
                    config = SwitchConfig(**config_data)
                    config.current_source = ReadSource(config_data['current_source'])
                    config.target_source = ReadSource(config_data['target_source'])
                    config.strategy = SwitchStrategy(config_data['strategy'])
                    config.status = SwitchStatus(config_data['status'])
                    self.switch_configs[config.config_id] = config
                
                # 加载切换规则
                for rule_data in data.get('switch_rules', []):
                    rule = SwitchRule(**rule_data)
                    rule.strategy = SwitchStrategy(rule_data['strategy'])
                    self.switch_rules[rule.rule_id] = rule
                    
                logger.info(f"加载了 {len(self.switch_configs)} 个切换配置和 {len(self.switch_rules)} 个切换规则")
            else:
                logger.warning(f"配置文件不存在: {config_path}")
                self._create_default_configs()
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            self._create_default_configs()
    
    def _create_default_configs(self):
        """创建默认配置"""
        # 创建示例配置
        default_config = SwitchConfig(
            config_id="users_table_switch",
            table_name="users",
            current_source=ReadSource.SOURCE,
            target_source=ReadSource.TARGET,
            strategy=SwitchStrategy.GRADUAL,
            conditions={
                "consistency_threshold": 0.99,
                "error_rate_threshold": 0.01,
                "latency_threshold": 100
            }
        )
        self.switch_configs[default_config.config_id] = default_config
    
    def _save_configurations(self):
        """保存切换配置"""
        try:
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'switch_configs': [
                    {
                        **asdict(config),
                        'current_source': config.current_source.value,
                        'target_source': config.target_source.value,
                        'strategy': config.strategy.value,
                        'status': config.status.value
                    }
                    for config in self.switch_configs.values()
                ],
                'switch_rules': [
                    {
                        **asdict(rule),
                        'strategy': rule.strategy.value
                    }
                    for rule in self.switch_rules.values()
                ],
                'updated_at': datetime.now().isoformat()
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                
            logger.info(f"配置已保存到: {config_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    async def connect(self):
        """连接数据库"""
        try:
            self.connection = await asyncpg.connect(self.db_url)
            await self._initialize_switch_tables()
            logger.info("配置化读取切换器数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            await self.connection.close()
            logger.info("配置化读取切换器数据库连接已关闭")
    
    async def _initialize_switch_tables(self):
        """初始化切换相关表"""
        # 创建切换配置表
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS t_sys_read_switch_configs (
                id BIGSERIAL PRIMARY KEY,
                config_id VARCHAR(100) NOT NULL UNIQUE,
                table_name VARCHAR(100) NOT NULL,
                current_source VARCHAR(20) NOT NULL,
                target_source VARCHAR(20) NOT NULL,
                strategy VARCHAR(20) NOT NULL,
                switch_percentage DECIMAL(5,2) DEFAULT 0.0,
                user_groups JSONB DEFAULT '[]',
                conditions JSONB DEFAULT '{}',
                rollback_enabled BOOLEAN DEFAULT TRUE,
                auto_rollback_threshold DECIMAL(5,4) DEFAULT 0.05,
                status VARCHAR(20) DEFAULT 'inactive',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT chk_current_source CHECK (current_source IN ('source', 'target', 'both')),
                CONSTRAINT chk_target_source CHECK (target_source IN ('source', 'target', 'both')),
                CONSTRAINT chk_strategy CHECK (strategy IN ('immediate', 'gradual', 'canary', 'ab_test', 'blue_green', 'conditional')),
                CONSTRAINT chk_status CHECK (status IN ('inactive', 'preparing', 'active', 'completed', 'failed', 'rolled_back')),
                CONSTRAINT chk_switch_percentage CHECK (switch_percentage >= 0.0 AND switch_percentage <= 100.0)
            );
            
            CREATE INDEX IF NOT EXISTS idx_read_switch_configs_id ON t_sys_read_switch_configs(config_id);
            CREATE INDEX IF NOT EXISTS idx_read_switch_configs_table ON t_sys_read_switch_configs(table_name);
            CREATE INDEX IF NOT EXISTS idx_read_switch_configs_status ON t_sys_read_switch_configs(status);
        """)
        
        # 创建切换指标表
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS t_sys_read_switch_metrics (
                id BIGSERIAL PRIMARY KEY,
                config_id VARCHAR(100) NOT NULL,
                total_requests BIGINT DEFAULT 0,
                source_requests BIGINT DEFAULT 0,
                target_requests BIGINT DEFAULT 0,
                source_errors BIGINT DEFAULT 0,
                target_errors BIGINT DEFAULT 0,
                source_avg_latency DECIMAL(8,2) DEFAULT 0.0,
                target_avg_latency DECIMAL(8,2) DEFAULT 0.0,
                switch_rate DECIMAL(5,4) DEFAULT 0.0,
                error_rate DECIMAL(5,4) DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (config_id) REFERENCES t_sys_read_switch_configs(config_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_read_switch_metrics_config ON t_sys_read_switch_metrics(config_id);
            CREATE INDEX IF NOT EXISTS idx_read_switch_metrics_created ON t_sys_read_switch_metrics(created_at);
        """)
        
        # 创建切换日志表
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS t_sys_read_switch_logs (
                id BIGSERIAL PRIMARY KEY,
                config_id VARCHAR(100) NOT NULL,
                request_id VARCHAR(100),
                user_id VARCHAR(100),
                table_name VARCHAR(100) NOT NULL,
                selected_source VARCHAR(20) NOT NULL,
                request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time_ms INTEGER,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                metadata JSONB,
                
                CONSTRAINT chk_selected_source CHECK (selected_source IN ('source', 'target'))
            );
            
            CREATE INDEX IF NOT EXISTS idx_read_switch_logs_config ON t_sys_read_switch_logs(config_id);
            CREATE INDEX IF NOT EXISTS idx_read_switch_logs_table ON t_sys_read_switch_logs(table_name);
            CREATE INDEX IF NOT EXISTS idx_read_switch_logs_user ON t_sys_read_switch_logs(user_id);
            CREATE INDEX IF NOT EXISTS idx_read_switch_logs_time ON t_sys_read_switch_logs(request_time);
            CREATE INDEX IF NOT EXISTS idx_read_switch_logs_success ON t_sys_read_switch_logs(success);
        """)
    
    async def register_switch_config(self, config: SwitchConfig) -> bool:
        """注册切换配置"""
        try:
            with self._lock:
                self.switch_configs[config.config_id] = config
                
                # 初始化指标
                if config.config_id not in self.metrics:
                    self.metrics[config.config_id] = SwitchMetrics(config_id=config.config_id)
            
            # 保存到数据库
            await self.connection.execute("""
                INSERT INTO t_sys_read_switch_configs 
                (config_id, table_name, current_source, target_source, strategy,
                 switch_percentage, user_groups, conditions, rollback_enabled,
                 auto_rollback_threshold, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (config_id) DO UPDATE SET
                    table_name = EXCLUDED.table_name,
                    current_source = EXCLUDED.current_source,
                    target_source = EXCLUDED.target_source,
                    strategy = EXCLUDED.strategy,
                    switch_percentage = EXCLUDED.switch_percentage,
                    user_groups = EXCLUDED.user_groups,
                    conditions = EXCLUDED.conditions,
                    rollback_enabled = EXCLUDED.rollback_enabled,
                    auto_rollback_threshold = EXCLUDED.auto_rollback_threshold,
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
            """, 
                config.config_id, config.table_name, config.current_source.value,
                config.target_source.value, config.strategy.value, config.switch_percentage,
                json.dumps(config.user_groups), json.dumps(config.conditions),
                config.rollback_enabled, config.auto_rollback_threshold, config.status.value
            )
            
            self._save_configurations()
            logger.info(f"切换配置已注册: {config.config_id}")
            return True
            
        except Exception as e:
            logger.error(f"注册切换配置失败: {e}")
            return False
    
    def register_request_handler(self, table_name: str, handler: Callable):
        """注册请求处理器"""
        self.request_handlers[table_name] = handler
        logger.info(f"请求处理器已注册: {table_name}")
    
    def register_error_handler(self, table_name: str, handler: Callable):
        """注册错误处理器"""
        self.error_handlers[table_name] = handler
        logger.info(f"错误处理器已注册: {table_name}")
    
    async def get_read_source(self, table_name: str, user_id: str = None, 
                            request_id: str = None, metadata: Dict = None) -> str:
        """获取读取源"""
        config = self._get_config_by_table(table_name)
        if not config:
            logger.warning(f"表 {table_name} 没有配置切换规则，使用默认源")
            return "source"
        
        if config.status != SwitchStatus.ACTIVE:
            return config.current_source.value
        
        start_time = time.time()
        selected_source = None
        success = True
        error_message = None
        
        try:
            # 根据策略选择读取源
            if config.strategy == SwitchStrategy.IMMEDIATE:
                selected_source = config.target_source.value
            
            elif config.strategy == SwitchStrategy.GRADUAL:
                selected_source = self._gradual_switch(config)
            
            elif config.strategy == SwitchStrategy.CANARY:
                selected_source = self._canary_switch(config, user_id)
            
            elif config.strategy == SwitchStrategy.AB_TEST:
                selected_source = self._ab_test_switch(config, user_id)
            
            elif config.strategy == SwitchStrategy.BLUE_GREEN:
                selected_source = self._blue_green_switch(config)
            
            elif config.strategy == SwitchStrategy.CONDITIONAL:
                selected_source = await self._conditional_switch(config, metadata)
            
            else:
                selected_source = config.current_source.value
            
            # 更新指标
            await self._update_metrics(config.config_id, selected_source, success, 
                                     time.time() - start_time)
            
            # 记录日志
            await self._log_switch_request(config.config_id, request_id, user_id, 
                                         table_name, selected_source, 
                                         int((time.time() - start_time) * 1000),
                                         success, error_message, metadata)
            
            return selected_source
            
        except Exception as e:
            success = False
            error_message = str(e)
            selected_source = config.current_source.value  # 出错时回退到当前源
            
            logger.error(f"获取读取源失败: {e}")
            
            # 更新指标
            await self._update_metrics(config.config_id, selected_source, success, 
                                     time.time() - start_time)
            
            # 记录错误日志
            await self._log_switch_request(config.config_id, request_id, user_id, 
                                         table_name, selected_source,
                                         int((time.time() - start_time) * 1000),
                                         success, error_message, metadata)
            
            return selected_source
    
    def _get_config_by_table(self, table_name: str) -> Optional[SwitchConfig]:
        """根据表名获取配置"""
        for config in self.switch_configs.values():
            if config.table_name == table_name:
                return config
        return None
    
    def _gradual_switch(self, config: SwitchConfig) -> str:
        """渐进切换"""
        # 根据切换百分比决定
        if random.random() * 100 < config.switch_percentage:
            return config.target_source.value
        else:
            return config.current_source.value
    
    def _canary_switch(self, config: SwitchConfig, user_id: str = None) -> str:
        """金丝雀发布"""
        if not user_id:
            return config.current_source.value
        
        # 基于用户ID的哈希值决定
        user_hash = hash(user_id) % 100
        if user_hash < config.switch_percentage:
            return config.target_source.value
        else:
            return config.current_source.value
    
    def _ab_test_switch(self, config: SwitchConfig, user_id: str = None) -> str:
        """A/B测试切换"""
        if not user_id:
            return config.current_source.value
        
        # 检查用户是否在指定组中
        if config.user_groups:
            # 这里需要实际的用户组查询逻辑
            # 简化实现：基于用户ID哈希
            user_hash = hash(user_id) % len(config.user_groups)
            if user_hash == 0:  # 假设第一组使用目标源
                return config.target_source.value
        
        return config.current_source.value
    
    def _blue_green_switch(self, config: SwitchConfig) -> str:
        """蓝绿部署切换"""
        # 蓝绿部署通常是全量切换
        return config.target_source.value
    
    async def _conditional_switch(self, config: SwitchConfig, metadata: Dict = None) -> str:
        """条件切换"""
        conditions = config.conditions
        
        # 检查时间条件
        if 'time_range' in conditions:
            time_range = conditions['time_range']
            current_hour = datetime.now().hour
            if not (time_range.get('start', 0) <= current_hour <= time_range.get('end', 23)):
                return config.current_source.value
        
        # 检查负载条件
        if 'load_threshold' in conditions:
            # 这里需要实际的负载检查逻辑
            pass
        
        # 检查错误率条件
        if 'error_rate_threshold' in conditions:
            metrics = self.metrics.get(config.config_id)
            if metrics and metrics.error_rate > conditions['error_rate_threshold']:
                return config.current_source.value
        
        # 检查自定义条件
        if metadata and 'custom_conditions' in conditions:
            for condition_key, condition_value in conditions['custom_conditions'].items():
                if metadata.get(condition_key) != condition_value:
                    return config.current_source.value
        
        return config.target_source.value
    
    async def _update_metrics(self, config_id: str, selected_source: str, 
                            success: bool, latency: float):
        """更新指标"""
        try:
            with self._lock:
                if config_id not in self.metrics:
                    self.metrics[config_id] = SwitchMetrics(config_id=config_id)
                
                metrics = self.metrics[config_id]
                metrics.total_requests += 1
                
                if selected_source == "source":
                    metrics.source_requests += 1
                    if not success:
                        metrics.source_errors += 1
                    # 更新平均延迟
                    if metrics.source_requests > 1:
                        metrics.source_avg_latency = (
                            (metrics.source_avg_latency * (metrics.source_requests - 1) + latency * 1000) /
                            metrics.source_requests
                        )
                    else:
                        metrics.source_avg_latency = latency * 1000
                
                elif selected_source == "target":
                    metrics.target_requests += 1
                    if not success:
                        metrics.target_errors += 1
                    # 更新平均延迟
                    if metrics.target_requests > 1:
                        metrics.target_avg_latency = (
                            (metrics.target_avg_latency * (metrics.target_requests - 1) + latency * 1000) /
                            metrics.target_requests
                        )
                    else:
                        metrics.target_avg_latency = latency * 1000
                
                # 计算切换率和错误率
                if metrics.total_requests > 0:
                    metrics.switch_rate = metrics.target_requests / metrics.total_requests
                    total_errors = metrics.source_errors + metrics.target_errors
                    metrics.error_rate = total_errors / metrics.total_requests
                
                metrics.last_updated = datetime.now()
            
            # 定期保存到数据库（每100次请求保存一次）
            if metrics.total_requests % 100 == 0:
                await self._save_metrics_to_db(config_id)
                
        except Exception as e:
            logger.error(f"更新指标失败: {e}")
    
    async def _save_metrics_to_db(self, config_id: str):
        """保存指标到数据库"""
        try:
            metrics = self.metrics.get(config_id)
            if not metrics:
                return
            
            await self.connection.execute("""
                INSERT INTO t_sys_read_switch_metrics 
                (config_id, total_requests, source_requests, target_requests,
                 source_errors, target_errors, source_avg_latency, target_avg_latency,
                 switch_rate, error_rate)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
                config_id, metrics.total_requests, metrics.source_requests, metrics.target_requests,
                metrics.source_errors, metrics.target_errors, metrics.source_avg_latency,
                metrics.target_avg_latency, metrics.switch_rate, metrics.error_rate
            )
            
        except Exception as e:
            logger.error(f"保存指标到数据库失败: {e}")
    
    async def _log_switch_request(self, config_id: str, request_id: str, user_id: str,
                                table_name: str, selected_source: str, response_time_ms: int,
                                success: bool, error_message: str = None, 
                                metadata: Dict = None):
        """记录切换请求日志"""
        try:
            await self.connection.execute("""
                INSERT INTO t_sys_read_switch_logs 
                (config_id, request_id, user_id, table_name, selected_source,
                 response_time_ms, success, error_message, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                config_id, request_id, user_id, table_name, selected_source,
                response_time_ms, success, error_message, 
                json.dumps(metadata) if metadata else None
            )
            
        except Exception as e:
            logger.error(f"记录切换日志失败: {e}")
    
    async def update_switch_percentage(self, config_id: str, percentage: float) -> bool:
        """更新切换百分比"""
        try:
            if config_id not in self.switch_configs:
                logger.error(f"切换配置不存在: {config_id}")
                return False
            
            if not (0.0 <= percentage <= 100.0):
                logger.error(f"切换百分比必须在0-100之间: {percentage}")
                return False
            
            with self._lock:
                self.switch_configs[config_id].switch_percentage = percentage
                self.switch_configs[config_id].updated_at = datetime.now()
            
            # 更新数据库
            await self.connection.execute("""
                UPDATE t_sys_read_switch_configs 
                SET switch_percentage = $1, updated_at = CURRENT_TIMESTAMP
                WHERE config_id = $2
            """, percentage, config_id)
            
            self._save_configurations()
            logger.info(f"切换百分比已更新: {config_id} -> {percentage}%")
            return True
            
        except Exception as e:
            logger.error(f"更新切换百分比失败: {e}")
            return False
    
    async def activate_switch(self, config_id: str) -> bool:
        """激活切换"""
        try:
            if config_id not in self.switch_configs:
                logger.error(f"切换配置不存在: {config_id}")
                return False
            
            with self._lock:
                self.switch_configs[config_id].status = SwitchStatus.ACTIVE
                self.switch_configs[config_id].updated_at = datetime.now()
            
            # 更新数据库
            await self.connection.execute("""
                UPDATE t_sys_read_switch_configs 
                SET status = 'active', updated_at = CURRENT_TIMESTAMP
                WHERE config_id = $1
            """, config_id)
            
            self._save_configurations()
            logger.info(f"切换已激活: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"激活切换失败: {e}")
            return False
    
    async def deactivate_switch(self, config_id: str) -> bool:
        """停用切换"""
        try:
            if config_id not in self.switch_configs:
                logger.error(f"切换配置不存在: {config_id}")
                return False
            
            with self._lock:
                self.switch_configs[config_id].status = SwitchStatus.INACTIVE
                self.switch_configs[config_id].updated_at = datetime.now()
            
            # 更新数据库
            await self.connection.execute("""
                UPDATE t_sys_read_switch_configs 
                SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
                WHERE config_id = $1
            """, config_id)
            
            self._save_configurations()
            logger.info(f"切换已停用: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"停用切换失败: {e}")
            return False
    
    async def rollback_switch(self, config_id: str) -> bool:
        """回滚切换"""
        try:
            if config_id not in self.switch_configs:
                logger.error(f"切换配置不存在: {config_id}")
                return False
            
            config = self.switch_configs[config_id]
            if not config.rollback_enabled:
                logger.error(f"切换配置未启用回滚: {config_id}")
                return False
            
            with self._lock:
                # 交换当前源和目标源
                config.current_source, config.target_source = config.target_source, config.current_source
                config.switch_percentage = 0.0
                config.status = SwitchStatus.ROLLED_BACK
                config.updated_at = datetime.now()
            
            # 更新数据库
            await self.connection.execute("""
                UPDATE t_sys_read_switch_configs 
                SET current_source = $1, target_source = $2, switch_percentage = 0.0,
                    status = 'rolled_back', updated_at = CURRENT_TIMESTAMP
                WHERE config_id = $3
            """, config.current_source.value, config.target_source.value, config_id)
            
            self._save_configurations()
            logger.info(f"切换已回滚: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"回滚切换失败: {e}")
            return False
    
    async def check_auto_rollback(self):
        """检查自动回滚条件"""
        try:
            for config_id, config in self.switch_configs.items():
                if (config.status == SwitchStatus.ACTIVE and 
                    config.rollback_enabled and 
                    config.auto_rollback_threshold > 0):
                    
                    metrics = self.metrics.get(config_id)
                    if metrics and metrics.error_rate > config.auto_rollback_threshold:
                        logger.warning(
                            f"错误率 {metrics.error_rate:.4f} 超过阈值 "
                            f"{config.auto_rollback_threshold:.4f}，触发自动回滚: {config_id}"
                        )
                        await self.rollback_switch(config_id)
                        
        except Exception as e:
            logger.error(f"检查自动回滚失败: {e}")
    
    async def get_switch_status(self, config_id: str = None) -> Dict[str, Any]:
        """获取切换状态"""
        try:
            if config_id:
                # 获取单个配置状态
                config = self.switch_configs.get(config_id)
                if not config:
                    return {}
                
                metrics = self.metrics.get(config_id, SwitchMetrics(config_id=config_id))
                
                return {
                    'config': asdict(config),
                    'metrics': asdict(metrics)
                }
            else:
                # 获取所有配置状态
                all_status = {}
                for cid in self.switch_configs.keys():
                    all_status[cid] = await self.get_switch_status(cid)
                return all_status
                
        except Exception as e:
            logger.error(f"获取切换状态失败: {e}")
            return {}
    
    async def get_switch_analytics(self, config_id: str, hours: int = 24) -> Dict[str, Any]:
        """获取切换分析数据"""
        try:
            # 获取指定时间范围内的日志
            logs = await self.connection.fetch("""
                SELECT 
                    DATE_TRUNC('hour', request_time) as hour,
                    selected_source,
                    COUNT(*) as request_count,
                    COUNT(CASE WHEN success = FALSE THEN 1 END) as error_count,
                    AVG(response_time_ms) as avg_response_time
                FROM t_sys_read_switch_logs
                WHERE config_id = $1 
                    AND request_time > CURRENT_TIMESTAMP - INTERVAL '%s hours'
                GROUP BY DATE_TRUNC('hour', request_time), selected_source
                ORDER BY hour DESC
            """ % hours, config_id)
            
            # 获取用户分布
            user_distribution = await self.connection.fetch("""
                SELECT 
                    selected_source,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(*) as total_requests
                FROM t_sys_read_switch_logs
                WHERE config_id = $1 
                    AND request_time > CURRENT_TIMESTAMP - INTERVAL '%s hours'
                    AND user_id IS NOT NULL
                GROUP BY selected_source
            """ % hours, config_id)
            
            # 获取错误分析
            error_analysis = await self.connection.fetch("""
                SELECT 
                    selected_source,
                    error_message,
                    COUNT(*) as error_count
                FROM t_sys_read_switch_logs
                WHERE config_id = $1 
                    AND request_time > CURRENT_TIMESTAMP - INTERVAL '%s hours'
                    AND success = FALSE
                    AND error_message IS NOT NULL
                GROUP BY selected_source, error_message
                ORDER BY error_count DESC
                LIMIT 10
            """ % hours, config_id)
            
            return {
                'config_id': config_id,
                'time_range_hours': hours,
                'hourly_stats': [dict(log) for log in logs],
                'user_distribution': [dict(dist) for dist in user_distribution],
                'error_analysis': [dict(error) for error in error_analysis],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取切换分析数据失败: {e}")
            return {}
    
    async def export_switch_report(self, config_id: str = None, output_file: str = None) -> str:
        """导出切换报告"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"switch_report_{config_id or 'all'}_{timestamp}.json"
        
        try:
            if config_id:
                # 导出单个配置报告
                status = await self.get_switch_status(config_id)
                analytics = await self.get_switch_analytics(config_id)
                
                report = {
                    'switch_status': status,
                    'switch_analytics': analytics,
                    'export_time': datetime.now().isoformat()
                }
            else:
                # 导出所有配置报告
                all_status = await self.get_switch_status()
                
                report = {
                    'all_switch_status': all_status,
                    'export_time': datetime.now().isoformat()
                }
            
            # 保存到文件
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"切换报告已导出: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"导出切换报告失败: {e}")
            return ""

# 使用示例配置
EXAMPLE_SWITCH_CONFIG = {
    "switch_configs": [
        {
            "config_id": "users_gradual_switch",
            "table_name": "users",
            "current_source": "source",
            "target_source": "target",
            "strategy": "gradual",
            "switch_percentage": 10.0,
            "conditions": {
                "consistency_threshold": 0.99,
                "error_rate_threshold": 0.01
            },
            "rollback_enabled": True,
            "auto_rollback_threshold": 0.05,
            "status": "inactive"
        }
    ],
    "switch_rules": []
}

async def main():
    """主函数示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description='配置化读取切换工具')
    parser.add_argument('--db-url', required=True, help='数据库连接URL')
    parser.add_argument('--config-file', help='配置文件路径')
    parser.add_argument('--action', 
                       choices=['status', 'activate', 'deactivate', 'rollback', 
                               'update-percentage', 'analytics', 'export'],
                       required=True, help='执行的操作')
    parser.add_argument('--config-id', help='配置ID')
    parser.add_argument('--percentage', type=float, help='切换百分比')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    switch = ConfigurableReadSwitch(args.db_url, args.config_file)
    
    try:
        await switch.connect()
        
        if args.action == 'status':
            status = await switch.get_switch_status(args.config_id)
            print(json.dumps(status, indent=2, ensure_ascii=False, default=str))
        
        elif args.action == 'activate':
            if not args.config_id:
                print("需要指定 --config-id")
                return
            success = await switch.activate_switch(args.config_id)
            print(f"激活切换: {'成功' if success else '失败'}")
        
        elif args.action == 'deactivate':
            if not args.config_id:
                print("需要指定 --config-id")
                return
            success = await switch.deactivate_switch(args.config_id)
            print(f"停用切换: {'成功' if success else '失败'}")
        
        elif args.action == 'rollback':
            if not args.config_id:
                print("需要指定 --config-id")
                return
            success = await switch.rollback_switch(args.config_id)
            print(f"回滚切换: {'成功' if success else '失败'}")
        
        elif args.action == 'update-percentage':
            if not args.config_id or args.percentage is None:
                print("需要指定 --config-id 和 --percentage")
                return
            success = await switch.update_switch_percentage(args.config_id, args.percentage)
            print(f"更新切换百分比: {'成功' if success else '失败'}")
        
        elif args.action == 'analytics':
            if not args.config_id:
                print("需要指定 --config-id")
                return
            analytics = await switch.get_switch_analytics(args.config_id)
            print(json.dumps(analytics, indent=2, ensure_ascii=False, default=str))
        
        elif args.action == 'export':
            report_file = await switch.export_switch_report(args.config_id, args.output)
            print(f"报告已导出: {report_file}")
    
    finally:
        await switch.disconnect()

if __name__ == "__main__":
    asyncio.run(main())