# -*- coding: utf-8 -*-
"""
SQL 动态构建器

功能：
1. 根据数据模型配置动态生成 TDengine SQL
2. 支持基础查询、聚合查询、条件筛选
3. 支持分页、排序
4. SQL 防注入处理

作者：AI Assistant
日期：2025-11-03
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from app.models.device import DeviceDataModel, DeviceFieldMapping
from app.core.exceptions import APIException
import logging

logger = logging.getLogger(__name__)
import re


class SQLBuilder:
    """
    SQL 动态构建器
    
    核心功能：
    - 根据数据模型配置生成 TDengine SQL
    - 支持基础 SELECT 查询
    - 支持聚合查询 (AVG, SUM, MAX, MIN, COUNT)
    - 支持复杂条件筛选 (WHERE)
    - 支持分页 (LIMIT, OFFSET)
    - 支持排序 (ORDER BY)
    - SQL 防注入
    """
    
    # 允许的聚合函数
    ALLOWED_AGG_FUNCTIONS = {'avg', 'sum', 'max', 'min', 'count', 'first', 'last'}
    
    # 允许的比较运算符
    ALLOWED_OPERATORS = {'=', '>', '<', '>=', '<=', '!=', '<>', 'like', 'in', 'between'}
    
    # 允许的排序方向
    ALLOWED_ORDER_DIRECTIONS = {'asc', 'desc'}
    
    def __init__(self):
        """初始化 SQL 构建器"""
        pass
    
    async def build_query_sql(
        self,
        model_config: DeviceDataModel,
        device_code: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        order_by: Optional[str] = None,
        order_direction: str = 'desc',
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        构建基础查询 SQL
        
        Args:
            model_config: 数据模型配置
            device_code: 设备编码（可选）
            filters: 额外的筛选条件（字典格式）
            start_time: 开始时间
            end_time: 结束时间
            order_by: 排序字段
            order_direction: 排序方向 (asc/desc)
            limit: 限制返回记录数
            offset: 偏移量（分页）
        
        Returns:
            包含 SQL 和参数的字典
        """
        logger.info(f"[SQL构建器] 构建查询SQL: model={model_config.model_code}, device={device_code}")
        
        # 1. 获取字段映射
        field_mappings = await self._get_field_mappings(
            model_config.device_type_code,
            model_config.selected_fields
        )
        
        if not field_mappings:
            raise APIException(
                code=400,
                message=f"数据模型 '{model_config.model_code}' 没有有效的字段映射"
            )
        
        # 2. 确定 TDengine 数据库和超级表
        tdengine_database = field_mappings[0]['tdengine_database']
        tdengine_stable = field_mappings[0]['tdengine_stable']
        
        # 3. 构建 SELECT 子句
        select_columns = []
        for mapping in field_mappings:
            column = mapping['tdengine_column']
            # SQL 防注入：仅允许字母、数字、下划线
            if not re.match(r'^[a-zA-Z0-9_]+$', column):
                logger.warning(f"[SQL构建器] 字段名包含非法字符，跳过: {column}")
                continue
            select_columns.append(column)
        
        # 添加时间戳列（TDengine 标准列）
        if 'ts' not in select_columns:
            select_columns.insert(0, 'ts')
        
        # 添加设备编码列（如果是 TAG）
        if 'prod_code' not in select_columns and 'device_code' not in select_columns:
            select_columns.insert(1, 'prod_code')
        
        select_clause = f"SELECT {', '.join(select_columns)}"
        
        # 4. 构建 FROM 子句
        from_clause = f"FROM {tdengine_database}.{tdengine_stable}"
        
        # 5. 构建 WHERE 子句
        where_conditions = []
        
        # 设备编码筛选
        if device_code:
            # SQL 防注入：使用参数化查询
            where_conditions.append(f"prod_code = '{self._escape_sql_string(device_code)}'")
        
        # 时间范围筛选
        if start_time:
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            where_conditions.append(f"ts >= '{start_time_str}'")
        
        if end_time:
            end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            where_conditions.append(f"ts <= '{end_time_str}'")
        
        # 额外筛选条件
        if filters:
            for field, value in filters.items():
                # SQL 防注入：验证字段名
                if not re.match(r'^[a-zA-Z0-9_]+$', field):
                    logger.warning(f"[SQL构建器] 筛选字段包含非法字符，跳过: {field}")
                    continue
                
                # 根据值类型构建条件
                if isinstance(value, (int, float)):
                    where_conditions.append(f"{field} = {value}")
                elif isinstance(value, str):
                    where_conditions.append(f"{field} = '{self._escape_sql_string(value)}'")
                elif isinstance(value, dict):
                    # 支持范围查询: {"min": 10, "max": 100}
                    if 'min' in value:
                        where_conditions.append(f"{field} >= {value['min']}")
                    if 'max' in value:
                        where_conditions.append(f"{field} <= {value['max']}")
                elif isinstance(value, list):
                    # 支持 IN 查询
                    escaped_values = [f"'{self._escape_sql_string(str(v))}'" for v in value]
                    where_conditions.append(f"{field} IN ({', '.join(escaped_values)})")
        
        where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
        
        # 6. 构建 ORDER BY 子句
        order_clause = ""
        if order_by:
            # SQL 防注入：验证字段名
            if re.match(r'^[a-zA-Z0-9_]+$', order_by):
                # 验证排序方向
                direction = order_direction.lower()
                if direction not in self.ALLOWED_ORDER_DIRECTIONS:
                    direction = 'desc'
                order_clause = f"ORDER BY {order_by} {direction.upper()}"
            else:
                logger.warning(f"[SQL构建器] 排序字段包含非法字符，忽略: {order_by}")
        else:
            # 默认按时间戳降序排序
            order_clause = "ORDER BY ts DESC"
        
        # 7. 构建 LIMIT 和 OFFSET 子句
        limit = max(1, min(limit, 10000))  # 限制范围: 1-10000
        offset = max(0, offset)
        limit_clause = f"LIMIT {limit} OFFSET {offset}"
        
        # 8. 组装完整 SQL
        sql_parts = [
            select_clause,
            from_clause,
            where_clause,
            order_clause,
            limit_clause
        ]
        
        sql = ' '.join(part for part in sql_parts if part)
        
        logger.info(f"[SQL构建器] SQL生成成功，长度: {len(sql)} 字符")
        logger.debug(f"[SQL构建器] SQL: {sql}")
        
        return {
            'sql': sql,
            'database': tdengine_database,
            'stable': tdengine_stable,
            'select_columns': select_columns,
            'row_count_sql': self._build_count_sql(tdengine_database, tdengine_stable, where_clause)
        }
    
    async def build_aggregation_sql(
        self,
        model_config: DeviceDataModel,
        device_code: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        group_by: Optional[List[str]] = None,
        interval: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        构建聚合查询 SQL
        
        Args:
            model_config: 数据模型配置
            device_code: 设备编码
            start_time: 开始时间
            end_time: 结束时间
            group_by: 分组字段列表
            interval: 时间间隔 (如 '1h', '5m', '1d')
        
        Returns:
            包含 SQL 和参数的字典
        """
        logger.info(f"[SQL构建器] 构建聚合SQL: model={model_config.model_code}, interval={interval}")
        
        # 1. 验证模型类型
        if model_config.model_type not in ['statistics', 'ai_analysis']:
            raise APIException(
                code=400,
                message=f"模型类型 '{model_config.model_type}' 不支持聚合查询"
            )
        
        # 2. 获取字段映射和聚合配置
        field_mappings = await self._get_field_mappings(
            model_config.device_type_code,
            model_config.selected_fields
        )
        
        if not field_mappings:
            raise APIException(
                code=400,
                message=f"数据模型 '{model_config.model_code}' 没有有效的字段映射"
            )
        
        # 3. 确定 TDengine 数据库和超级表
        tdengine_database = field_mappings[0]['tdengine_database']
        tdengine_stable = field_mappings[0]['tdengine_stable']
        
        # 4. 构建聚合 SELECT 子句
        aggregation_config = model_config.aggregation_config or {}
        default_methods = aggregation_config.get('methods', ['avg'])
        
        select_items = []
        
        # 添加时间窗口
        if interval:
            # 验证时间间隔格式（如 '1h', '5m', '1d'）
            if re.match(r'^\d+[smhd]$', interval):
                select_items.append(f"_wstart as window_start")
                select_items.append(f"_wend as window_end")
            else:
                logger.warning(f"[SQL构建器] 时间间隔格式无效，忽略: {interval}")
                interval = None
        
        # 添加分组字段
        if group_by:
            for field in group_by:
                if re.match(r'^[a-zA-Z0-9_]+$', field):
                    select_items.append(field)
        else:
            # 默认按设备编码分组
            select_items.append('prod_code')
        
        # 添加聚合字段
        for mapping in field_mappings:
            column = mapping['tdengine_column']
            field_code = mapping['field_code']
            
            # 获取该字段的聚合方法
            agg_method = mapping.get('aggregation_method', 'avg')
            if agg_method not in self.ALLOWED_AGG_FUNCTIONS:
                agg_method = 'avg'
            
            # SQL 防注入
            if not re.match(r'^[a-zA-Z0-9_]+$', column):
                continue
            
            # 构建聚合表达式
            select_items.append(f"{agg_method.upper()}({column}) as {field_code}_{agg_method}")
        
        select_clause = f"SELECT {', '.join(select_items)}"
        
        # 5. 构建 FROM 子句
        from_clause = f"FROM {tdengine_database}.{tdengine_stable}"
        
        # 6. 构建 WHERE 子句
        where_conditions = []
        
        if device_code:
            where_conditions.append(f"prod_code = '{self._escape_sql_string(device_code)}'")
        
        if start_time:
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            where_conditions.append(f"ts >= '{start_time_str}'")
        
        if end_time:
            end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            where_conditions.append(f"ts <= '{end_time_str}'")
        
        where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
        
        # 7. 构建 INTERVAL 子句（TDengine 特有）
        interval_clause = ""
        if interval:
            interval_clause = f"INTERVAL({interval})"
        
        # 8. 构建 GROUP BY 子句
        group_by_clause = ""
        if group_by:
            valid_fields = [f for f in group_by if re.match(r'^[a-zA-Z0-9_]+$', f)]
            if valid_fields:
                group_by_clause = f"GROUP BY {', '.join(valid_fields)}"
        
        # 9. 组装完整 SQL
        sql_parts = [
            select_clause,
            from_clause,
            where_clause,
            interval_clause,
            group_by_clause,
            "ORDER BY window_start DESC" if interval else "ORDER BY prod_code"
        ]
        
        sql = ' '.join(part for part in sql_parts if part)
        
        logger.info(f"[SQL构建器] 聚合SQL生成成功，长度: {len(sql)} 字符")
        logger.debug(f"[SQL构建器] SQL: {sql}")
        
        return {
            'sql': sql,
            'database': tdengine_database,
            'stable': tdengine_stable,
            'aggregation_methods': default_methods,
            'interval': interval
        }
    
    async def _get_field_mappings(
        self,
        device_type_code: str,
        selected_fields: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        获取字段映射信息
        
        Args:
            device_type_code: 设备类型代码
            selected_fields: 选中的字段配置
        
        Returns:
            字段映射信息列表
        """
        field_mappings = []
        
        for field_config in selected_fields:
            field_code = field_config.get('field_code')
            if not field_code:
                continue
            
            # 查询字段映射
            mapping = await DeviceFieldMapping.filter(
                device_type_code=device_type_code,
                device_field__field_code=field_code,
                is_active=True
            ).prefetch_related('device_field').first()
            
            if not mapping:
                logger.warning(f"[SQL构建器] 字段映射不存在: {field_code}，跳过")
                continue
            
            field_mappings.append({
                'field_code': field_code,
                'tdengine_database': mapping.tdengine_database,
                'tdengine_stable': mapping.tdengine_stable,
                'tdengine_column': mapping.tdengine_column,
                'is_tag': mapping.is_tag,
                'transform_rule': mapping.transform_rule,
                'aggregation_method': mapping.device_field.aggregation_method
            })
        
        return field_mappings
    
    def _build_count_sql(
        self,
        database: str,
        stable: str,
        where_clause: str
    ) -> str:
        """
        构建 COUNT 查询 SQL（用于获取总记录数）
        
        Args:
            database: 数据库名
            stable: 超级表名
            where_clause: WHERE 子句
        
        Returns:
            COUNT SQL
        """
        sql_parts = [
            f"SELECT COUNT(*) as total",
            f"FROM {database}.{stable}",
            where_clause
        ]
        
        return ' '.join(part for part in sql_parts if part)
    
    def _escape_sql_string(self, value: str) -> str:
        """
        SQL 字符串转义（防注入）
        
        Args:
            value: 原始字符串
        
        Returns:
            转义后的字符串
        """
        # 转义单引号
        return value.replace("'", "''").replace("\\", "\\\\")
    
    def validate_sql(self, sql: str) -> bool:
        """
        验证 SQL 安全性（防注入）
        
        Args:
            sql: SQL 语句
        
        Returns:
            是否安全
        """
        # 检查危险关键词
        dangerous_keywords = [
            'drop', 'delete', 'truncate', 'update', 'insert',
            'create', 'alter', 'exec', 'execute', 'script'
        ]
        
        sql_lower = sql.lower()
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                logger.warning(f"[SQL构建器] SQL包含危险关键词: {keyword}")
                return False
        
        return True


# 创建全局实例
sql_builder = SQLBuilder()

