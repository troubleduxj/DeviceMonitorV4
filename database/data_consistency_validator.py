#!/usr/bin/env python3
"""
数据一致性验证工具
提供全面的数据一致性检查、差异分析和修复建议
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_consistency_validator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """验证级别枚举"""
    BASIC = "basic"           # 基础验证（记录数量）
    STANDARD = "standard"     # 标准验证（主键匹配）
    DETAILED = "detailed"     # 详细验证（字段级别）
    COMPREHENSIVE = "comprehensive"  # 全面验证（包含数据完整性）

class DifferenceType(Enum):
    """差异类型枚举"""
    MISSING_IN_TARGET = "missing_in_target"
    EXTRA_IN_TARGET = "extra_in_target"
    FIELD_MISMATCH = "field_mismatch"
    TYPE_MISMATCH = "type_mismatch"
    NULL_MISMATCH = "null_mismatch"
    CONSTRAINT_VIOLATION = "constraint_violation"

@dataclass
class ValidationRule:
    """验证规则"""
    rule_id: str
    rule_name: str
    rule_type: str
    source_query: str
    target_query: str
    comparison_fields: List[str]
    tolerance: float = 0.0  # 容差值
    enabled: bool = True
    description: str = ""

@dataclass
class DataDifference:
    """数据差异"""
    difference_type: DifferenceType
    source_table: str
    target_table: str
    record_id: Any
    field_name: str = None
    source_value: Any = None
    target_value: Any = None
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    description: str = ""
    suggested_fix: str = ""

@dataclass
class ValidationResult:
    """验证结果"""
    validation_id: str
    source_table: str
    target_table: str
    validation_level: ValidationLevel
    start_time: datetime
    end_time: datetime
    total_source_records: int
    total_target_records: int
    matched_records: int
    differences: List[DataDifference]
    consistency_score: float
    validation_rules_applied: List[str]
    summary: Dict[str, Any]
    recommendations: List[str]

class DataConsistencyValidator:
    """数据一致性验证器"""
    
    def __init__(self, db_url: str, rules_file: str = None):
        self.db_url = db_url
        self.connection: Optional[asyncpg.Connection] = None
        self.rules_file = rules_file or "database/validation_rules.json"
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.table_schemas: Dict[str, Dict] = {}
        
        # 加载验证规则
        self._load_validation_rules()
    
    def _load_validation_rules(self):
        """加载验证规则"""
        try:
            rules_path = Path(self.rules_file)
            if rules_path.exists():
                with open(rules_path, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    
                for rule_data in rules_data.get('rules', []):
                    rule = ValidationRule(**rule_data)
                    self.validation_rules[rule.rule_id] = rule
                    
                logger.info(f"加载了 {len(self.validation_rules)} 个验证规则")
            else:
                logger.warning(f"验证规则文件不存在: {rules_path}")
                self._create_default_rules()
        except Exception as e:
            logger.error(f"加载验证规则失败: {e}")
            self._create_default_rules()
    
    def _create_default_rules(self):
        """创建默认验证规则"""
        default_rules = [
            ValidationRule(
                rule_id="count_comparison",
                rule_name="记录数量比较",
                rule_type="count",
                source_query="SELECT COUNT(*) FROM {source_table}",
                target_query="SELECT COUNT(*) FROM {target_table}",
                comparison_fields=[],
                description="比较源表和目标表的记录总数"
            ),
            ValidationRule(
                rule_id="primary_key_match",
                rule_name="主键匹配检查",
                rule_type="primary_key",
                source_query="SELECT {pk_field} FROM {source_table}",
                target_query="SELECT {pk_field} FROM {target_table}",
                comparison_fields=["id"],
                description="检查主键在两个表中的匹配情况"
            ),
            ValidationRule(
                rule_id="field_value_comparison",
                rule_name="字段值比较",
                rule_type="field_comparison",
                source_query="SELECT * FROM {source_table} WHERE {pk_field} = $1",
                target_query="SELECT * FROM {target_table} WHERE {pk_field} = $1",
                comparison_fields=[],
                description="逐字段比较记录内容"
            )
        ]
        
        for rule in default_rules:
            self.validation_rules[rule.rule_id] = rule
    
    async def connect(self):
        """连接数据库"""
        try:
            self.connection = await asyncpg.connect(self.db_url)
            logger.info("数据一致性验证器数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            await self.connection.close()
            logger.info("数据一致性验证器数据库连接已关闭")
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """获取表结构信息"""
        if table_name in self.table_schemas:
            return self.table_schemas[table_name]
        
        try:
            # 获取表的列信息
            columns = await self.connection.fetch("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, table_name)
            
            # 获取主键信息
            primary_keys = await self.connection.fetch("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = $1 AND tc.constraint_type = 'PRIMARY KEY'
            """, table_name)
            
            # 获取外键信息
            foreign_keys = await self.connection.fetch("""
                SELECT 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu 
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.table_name = $1 AND tc.constraint_type = 'FOREIGN KEY'
            """, table_name)
            
            schema = {
                'table_name': table_name,
                'columns': [dict(col) for col in columns],
                'primary_keys': [pk['column_name'] for pk in primary_keys],
                'foreign_keys': [dict(fk) for fk in foreign_keys],
                'column_names': [col['column_name'] for col in columns]
            }
            
            self.table_schemas[table_name] = schema
            return schema
            
        except Exception as e:
            logger.error(f"获取表结构失败 {table_name}: {e}")
            return {}
    
    async def validate_table_consistency(self, source_table: str, target_table: str,
                                       validation_level: ValidationLevel = ValidationLevel.STANDARD,
                                       sample_size: int = None,
                                       specific_rules: List[str] = None) -> ValidationResult:
        """验证表数据一致性"""
        validation_id = f"validation_{source_table}_{target_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"开始数据一致性验证: {source_table} -> {target_table}")
        
        try:
            # 获取表结构
            source_schema = await self.get_table_schema(source_table)
            target_schema = await self.get_table_schema(target_table)
            
            if not source_schema or not target_schema:
                raise ValueError("无法获取表结构信息")
            
            # 初始化结果
            differences = []
            validation_rules_applied = []
            
            # 获取记录总数
            total_source_records = await self.connection.fetchval(
                f"SELECT COUNT(*) FROM {source_table}"
            )
            total_target_records = await self.connection.fetchval(
                f"SELECT COUNT(*) FROM {target_table}"
            )
            
            # 根据验证级别执行不同的检查
            if validation_level in [ValidationLevel.BASIC, ValidationLevel.STANDARD, 
                                  ValidationLevel.DETAILED, ValidationLevel.COMPREHENSIVE]:
                # 基础验证：记录数量比较
                count_diff = await self._validate_record_count(
                    source_table, target_table, total_source_records, total_target_records
                )
                if count_diff:
                    differences.extend(count_diff)
                validation_rules_applied.append("count_comparison")
            
            if validation_level in [ValidationLevel.STANDARD, ValidationLevel.DETAILED, 
                                  ValidationLevel.COMPREHENSIVE]:
                # 标准验证：主键匹配
                pk_diff = await self._validate_primary_key_match(
                    source_table, target_table, source_schema, target_schema, sample_size
                )
                differences.extend(pk_diff)
                validation_rules_applied.append("primary_key_match")
            
            if validation_level in [ValidationLevel.DETAILED, ValidationLevel.COMPREHENSIVE]:
                # 详细验证：字段级别比较
                field_diff = await self._validate_field_values(
                    source_table, target_table, source_schema, target_schema, sample_size
                )
                differences.extend(field_diff)
                validation_rules_applied.append("field_value_comparison")
            
            if validation_level == ValidationLevel.COMPREHENSIVE:
                # 全面验证：数据完整性检查
                integrity_diff = await self._validate_data_integrity(
                    source_table, target_table, source_schema, target_schema
                )
                differences.extend(integrity_diff)
                validation_rules_applied.append("data_integrity_check")
            
            # 应用自定义验证规则
            if specific_rules:
                for rule_id in specific_rules:
                    if rule_id in self.validation_rules:
                        rule_diff = await self._apply_custom_rule(
                            self.validation_rules[rule_id], source_table, target_table
                        )
                        differences.extend(rule_diff)
                        validation_rules_applied.append(rule_id)
            
            # 计算匹配记录数和一致性分数
            matched_records = max(0, min(total_source_records, total_target_records) - 
                                len([d for d in differences if d.difference_type in 
                                    [DifferenceType.MISSING_IN_TARGET, DifferenceType.EXTRA_IN_TARGET]]))
            
            consistency_score = self._calculate_consistency_score(
                total_source_records, total_target_records, differences
            )
            
            # 生成摘要和建议
            summary = self._generate_summary(differences, total_source_records, total_target_records)
            recommendations = self._generate_recommendations(differences, consistency_score)
            
            end_time = datetime.now()
            
            result = ValidationResult(
                validation_id=validation_id,
                source_table=source_table,
                target_table=target_table,
                validation_level=validation_level,
                start_time=start_time,
                end_time=end_time,
                total_source_records=total_source_records,
                total_target_records=total_target_records,
                matched_records=matched_records,
                differences=differences,
                consistency_score=consistency_score,
                validation_rules_applied=validation_rules_applied,
                summary=summary,
                recommendations=recommendations
            )
            
            # 保存验证结果
            await self._save_validation_result(result)
            
            logger.info(f"数据一致性验证完成: {validation_id}, 一致性分数: {consistency_score:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"数据一致性验证失败: {e}")
            raise
    
    async def _validate_record_count(self, source_table: str, target_table: str,
                                   source_count: int, target_count: int) -> List[DataDifference]:
        """验证记录数量"""
        differences = []
        
        if source_count != target_count:
            if source_count > target_count:
                differences.append(DataDifference(
                    difference_type=DifferenceType.MISSING_IN_TARGET,
                    source_table=source_table,
                    target_table=target_table,
                    record_id="COUNT",
                    source_value=source_count,
                    target_value=target_count,
                    severity="HIGH",
                    description=f"目标表缺少 {source_count - target_count} 条记录",
                    suggested_fix="检查数据迁移过程，确保所有记录都已正确迁移"
                ))
            else:
                differences.append(DataDifference(
                    difference_type=DifferenceType.EXTRA_IN_TARGET,
                    source_table=source_table,
                    target_table=target_table,
                    record_id="COUNT",
                    source_value=source_count,
                    target_value=target_count,
                    severity="MEDIUM",
                    description=f"目标表多出 {target_count - source_count} 条记录",
                    suggested_fix="检查目标表是否有重复数据或额外插入的记录"
                ))
        
        return differences
    
    async def _validate_primary_key_match(self, source_table: str, target_table: str,
                                        source_schema: Dict, target_schema: Dict,
                                        sample_size: int = None) -> List[DataDifference]:
        """验证主键匹配"""
        differences = []
        
        # 获取主键字段
        source_pk = source_schema.get('primary_keys', [])
        target_pk = target_schema.get('primary_keys', [])
        
        if not source_pk or not target_pk:
            logger.warning(f"表 {source_table} 或 {target_table} 没有主键")
            return differences
        
        # 假设主键字段相同（实际应用中可能需要映射）
        pk_field = source_pk[0] if source_pk else 'id'
        
        try:
            # 构建查询
            limit_clause = f"LIMIT {sample_size}" if sample_size else ""
            
            # 获取源表主键
            source_pks = await self.connection.fetch(
                f"SELECT {pk_field} FROM {source_table} ORDER BY {pk_field} {limit_clause}"
            )
            
            # 检查每个主键在目标表中是否存在
            for record in source_pks:
                pk_value = record[pk_field]
                
                target_exists = await self.connection.fetchval(
                    f"SELECT COUNT(*) FROM {target_table} WHERE {pk_field} = $1",
                    pk_value
                )
                
                if target_exists == 0:
                    differences.append(DataDifference(
                        difference_type=DifferenceType.MISSING_IN_TARGET,
                        source_table=source_table,
                        target_table=target_table,
                        record_id=pk_value,
                        field_name=pk_field,
                        source_value=pk_value,
                        target_value=None,
                        severity="HIGH",
                        description=f"主键 {pk_value} 在目标表中不存在",
                        suggested_fix=f"将主键为 {pk_value} 的记录迁移到目标表"
                    ))
            
            # 检查目标表中是否有多余的记录
            target_pks = await self.connection.fetch(
                f"SELECT {pk_field} FROM {target_table} ORDER BY {pk_field} {limit_clause}"
            )
            
            source_pk_set = {record[pk_field] for record in source_pks}
            
            for record in target_pks:
                pk_value = record[pk_field]
                
                if pk_value not in source_pk_set:
                    differences.append(DataDifference(
                        difference_type=DifferenceType.EXTRA_IN_TARGET,
                        source_table=source_table,
                        target_table=target_table,
                        record_id=pk_value,
                        field_name=pk_field,
                        source_value=None,
                        target_value=pk_value,
                        severity="MEDIUM",
                        description=f"主键 {pk_value} 在源表中不存在",
                        suggested_fix=f"检查主键为 {pk_value} 的记录是否应该存在于目标表中"
                    ))
            
        except Exception as e:
            logger.error(f"主键匹配验证失败: {e}")
        
        return differences
    
    async def _validate_field_values(self, source_table: str, target_table: str,
                                   source_schema: Dict, target_schema: Dict,
                                   sample_size: int = None) -> List[DataDifference]:
        """验证字段值"""
        differences = []
        
        # 获取共同的字段
        source_columns = set(source_schema.get('column_names', []))
        target_columns = set(target_schema.get('column_names', []))
        common_columns = source_columns.intersection(target_columns)
        
        if not common_columns:
            logger.warning(f"表 {source_table} 和 {target_table} 没有共同字段")
            return differences
        
        # 获取主键字段
        pk_field = source_schema.get('primary_keys', ['id'])[0]
        
        try:
            # 获取要比较的记录
            limit_clause = f"LIMIT {sample_size}" if sample_size else ""
            
            source_records = await self.connection.fetch(
                f"SELECT * FROM {source_table} ORDER BY {pk_field} {limit_clause}"
            )
            
            for source_record in source_records:
                pk_value = source_record[pk_field]
                
                # 获取目标表中对应的记录
                target_record = await self.connection.fetchrow(
                    f"SELECT * FROM {target_table} WHERE {pk_field} = $1",
                    pk_value
                )
                
                if not target_record:
                    continue  # 这个差异在主键匹配中已经处理
                
                # 比较每个字段
                for column in common_columns:
                    if column == pk_field:
                        continue  # 跳过主键字段
                    
                    source_value = source_record.get(column)
                    target_value = target_record.get(column)
                    
                    if not self._values_equal(source_value, target_value):
                        differences.append(DataDifference(
                            difference_type=DifferenceType.FIELD_MISMATCH,
                            source_table=source_table,
                            target_table=target_table,
                            record_id=pk_value,
                            field_name=column,
                            source_value=source_value,
                            target_value=target_value,
                            severity="MEDIUM",
                            description=f"字段 {column} 值不匹配",
                            suggested_fix=f"更新目标表中主键为 {pk_value} 的记录的 {column} 字段"
                        ))
        
        except Exception as e:
            logger.error(f"字段值验证失败: {e}")
        
        return differences
    
    async def _validate_data_integrity(self, source_table: str, target_table: str,
                                     source_schema: Dict, target_schema: Dict) -> List[DataDifference]:
        """验证数据完整性"""
        differences = []
        
        try:
            # 检查外键约束
            source_fks = source_schema.get('foreign_keys', [])
            target_fks = target_schema.get('foreign_keys', [])
            
            # 检查NULL值约束
            for column_info in source_schema.get('columns', []):
                column_name = column_info['column_name']
                is_nullable = column_info['is_nullable'] == 'YES'
                
                if not is_nullable:
                    # 检查目标表中是否有NULL值
                    null_count = await self.connection.fetchval(
                        f"SELECT COUNT(*) FROM {target_table} WHERE {column_name} IS NULL"
                    )
                    
                    if null_count > 0:
                        differences.append(DataDifference(
                            difference_type=DifferenceType.CONSTRAINT_VIOLATION,
                            source_table=source_table,
                            target_table=target_table,
                            record_id="CONSTRAINT",
                            field_name=column_name,
                            source_value="NOT NULL",
                            target_value=f"{null_count} NULL values",
                            severity="HIGH",
                            description=f"字段 {column_name} 不允许NULL值，但目标表中有 {null_count} 个NULL值",
                            suggested_fix=f"修复目标表中 {column_name} 字段的NULL值"
                        ))
            
            # 检查数据类型一致性
            source_columns = {col['column_name']: col for col in source_schema.get('columns', [])}
            target_columns = {col['column_name']: col for col in target_schema.get('columns', [])}
            
            for column_name in source_columns:
                if column_name in target_columns:
                    source_type = source_columns[column_name]['data_type']
                    target_type = target_columns[column_name]['data_type']
                    
                    if source_type != target_type:
                        differences.append(DataDifference(
                            difference_type=DifferenceType.TYPE_MISMATCH,
                            source_table=source_table,
                            target_table=target_table,
                            record_id="SCHEMA",
                            field_name=column_name,
                            source_value=source_type,
                            target_value=target_type,
                            severity="MEDIUM",
                            description=f"字段 {column_name} 数据类型不匹配",
                            suggested_fix=f"统一字段 {column_name} 的数据类型"
                        ))
        
        except Exception as e:
            logger.error(f"数据完整性验证失败: {e}")
        
        return differences
    
    async def _apply_custom_rule(self, rule: ValidationRule, source_table: str, 
                               target_table: str) -> List[DataDifference]:
        """应用自定义验证规则"""
        differences = []
        
        try:
            if rule.rule_type == "count":
                source_query = rule.source_query.format(source_table=source_table)
                target_query = rule.target_query.format(target_table=target_table)
                
                source_result = await self.connection.fetchval(source_query)
                target_result = await self.connection.fetchval(target_query)
                
                if abs(source_result - target_result) > rule.tolerance:
                    differences.append(DataDifference(
                        difference_type=DifferenceType.FIELD_MISMATCH,
                        source_table=source_table,
                        target_table=target_table,
                        record_id=rule.rule_id,
                        field_name="custom_rule",
                        source_value=source_result,
                        target_value=target_result,
                        severity="MEDIUM",
                        description=f"自定义规则 {rule.rule_name} 验证失败",
                        suggested_fix=rule.description
                    ))
            
            # 可以添加更多自定义规则类型的处理
            
        except Exception as e:
            logger.error(f"应用自定义规则失败 {rule.rule_id}: {e}")
        
        return differences
    
    def _values_equal(self, value1: Any, value2: Any) -> bool:
        """比较两个值是否相等"""
        # 处理NULL值
        if value1 is None and value2 is None:
            return True
        if value1 is None or value2 is None:
            return False
        
        # 处理数值类型
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            return abs(value1 - value2) < 1e-10
        
        # 处理字符串类型
        if isinstance(value1, str) and isinstance(value2, str):
            return value1.strip() == value2.strip()
        
        # 处理日期时间类型
        if isinstance(value1, datetime) and isinstance(value2, datetime):
            return abs((value1 - value2).total_seconds()) < 1
        
        # 默认比较
        return value1 == value2
    
    def _calculate_consistency_score(self, source_count: int, target_count: int,
                                   differences: List[DataDifference]) -> float:
        """计算一致性分数"""
        if source_count == 0 and target_count == 0:
            return 1.0
        
        total_records = max(source_count, target_count)
        if total_records == 0:
            return 1.0
        
        # 计算不同类型差异的权重
        critical_diff_count = len([d for d in differences if d.severity == "CRITICAL"])
        high_diff_count = len([d for d in differences if d.severity == "HIGH"])
        medium_diff_count = len([d for d in differences if d.severity == "MEDIUM"])
        low_diff_count = len([d for d in differences if d.severity == "LOW"])
        
        # 加权计算一致性分数
        weighted_diff_count = (
            critical_diff_count * 4 +
            high_diff_count * 3 +
            medium_diff_count * 2 +
            low_diff_count * 1
        )
        
        # 计算分数（0-1之间）
        max_possible_score = total_records * 4  # 假设所有记录都是CRITICAL差异
        consistency_score = max(0, 1 - (weighted_diff_count / max_possible_score))
        
        return round(consistency_score, 4)
    
    def _generate_summary(self, differences: List[DataDifference], 
                         source_count: int, target_count: int) -> Dict[str, Any]:
        """生成验证摘要"""
        summary = {
            'total_differences': len(differences),
            'source_record_count': source_count,
            'target_record_count': target_count,
            'record_count_difference': abs(source_count - target_count),
            'difference_by_type': {},
            'difference_by_severity': {},
            'affected_fields': set(),
            'affected_records': set()
        }
        
        for diff in differences:
            # 按类型统计
            diff_type = diff.difference_type.value
            summary['difference_by_type'][diff_type] = summary['difference_by_type'].get(diff_type, 0) + 1
            
            # 按严重程度统计
            severity = diff.severity
            summary['difference_by_severity'][severity] = summary['difference_by_severity'].get(severity, 0) + 1
            
            # 收集受影响的字段和记录
            if diff.field_name:
                summary['affected_fields'].add(diff.field_name)
            if diff.record_id:
                summary['affected_records'].add(str(diff.record_id))
        
        # 转换集合为列表
        summary['affected_fields'] = list(summary['affected_fields'])
        summary['affected_records'] = list(summary['affected_records'])
        summary['affected_field_count'] = len(summary['affected_fields'])
        summary['affected_record_count'] = len(summary['affected_records'])
        
        return summary
    
    def _generate_recommendations(self, differences: List[DataDifference], 
                                consistency_score: float) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        if consistency_score >= 0.95:
            recommendations.append("数据一致性良好，建议继续监控")
        elif consistency_score >= 0.90:
            recommendations.append("数据一致性较好，建议修复少量差异")
        elif consistency_score >= 0.80:
            recommendations.append("数据一致性一般，需要重点关注和修复")
        else:
            recommendations.append("数据一致性较差，需要立即修复")
        
        # 根据差异类型生成具体建议
        diff_types = set(diff.difference_type for diff in differences)
        
        if DifferenceType.MISSING_IN_TARGET in diff_types:
            recommendations.append("检查数据迁移过程，确保所有记录都已迁移")
        
        if DifferenceType.EXTRA_IN_TARGET in diff_types:
            recommendations.append("检查目标表是否有重复或多余的数据")
        
        if DifferenceType.FIELD_MISMATCH in diff_types:
            recommendations.append("检查字段映射和数据转换逻辑")
        
        if DifferenceType.TYPE_MISMATCH in diff_types:
            recommendations.append("统一源表和目标表的字段数据类型")
        
        if DifferenceType.CONSTRAINT_VIOLATION in diff_types:
            recommendations.append("修复违反约束的数据")
        
        # 添加优先级建议
        critical_count = len([d for d in differences if d.severity == "CRITICAL"])
        high_count = len([d for d in differences if d.severity == "HIGH"])
        
        if critical_count > 0:
            recommendations.append(f"优先修复 {critical_count} 个严重问题")
        if high_count > 0:
            recommendations.append(f"重点关注 {high_count} 个高优先级问题")
        
        return recommendations
    
    async def _save_validation_result(self, result: ValidationResult):
        """保存验证结果"""
        try:
            # 创建验证结果表（如果不存在）
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS t_sys_validation_results (
                    id BIGSERIAL PRIMARY KEY,
                    validation_id VARCHAR(200) NOT NULL UNIQUE,
                    source_table VARCHAR(100) NOT NULL,
                    target_table VARCHAR(100) NOT NULL,
                    validation_level VARCHAR(20) NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    duration_ms INTEGER,
                    total_source_records BIGINT NOT NULL,
                    total_target_records BIGINT NOT NULL,
                    matched_records BIGINT NOT NULL,
                    total_differences INTEGER NOT NULL,
                    consistency_score DECIMAL(5,4) NOT NULL,
                    validation_rules_applied JSONB,
                    summary JSONB,
                    recommendations JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_validation_results_id ON t_sys_validation_results(validation_id);
                CREATE INDEX IF NOT EXISTS idx_validation_results_tables ON t_sys_validation_results(source_table, target_table);
                CREATE INDEX IF NOT EXISTS idx_validation_results_score ON t_sys_validation_results(consistency_score);
                CREATE INDEX IF NOT EXISTS idx_validation_results_created ON t_sys_validation_results(created_at);
            """)
            
            # 创建差异详情表（如果不存在）
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS t_sys_validation_differences (
                    id BIGSERIAL PRIMARY KEY,
                    validation_id VARCHAR(200) NOT NULL,
                    difference_type VARCHAR(50) NOT NULL,
                    source_table VARCHAR(100) NOT NULL,
                    target_table VARCHAR(100) NOT NULL,
                    record_id VARCHAR(100),
                    field_name VARCHAR(100),
                    source_value TEXT,
                    target_value TEXT,
                    severity VARCHAR(20) NOT NULL,
                    description TEXT,
                    suggested_fix TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (validation_id) REFERENCES t_sys_validation_results(validation_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_validation_differences_validation ON t_sys_validation_differences(validation_id);
                CREATE INDEX IF NOT EXISTS idx_validation_differences_type ON t_sys_validation_differences(difference_type);
                CREATE INDEX IF NOT EXISTS idx_validation_differences_severity ON t_sys_validation_differences(severity);
            """)
            
            # 保存验证结果
            duration_ms = int((result.end_time - result.start_time).total_seconds() * 1000)
            
            await self.connection.execute("""
                INSERT INTO t_sys_validation_results 
                (validation_id, source_table, target_table, validation_level,
                 start_time, end_time, duration_ms, total_source_records, total_target_records,
                 matched_records, total_differences, consistency_score,
                 validation_rules_applied, summary, recommendations)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (validation_id) DO UPDATE SET
                    end_time = EXCLUDED.end_time,
                    duration_ms = EXCLUDED.duration_ms,
                    total_differences = EXCLUDED.total_differences,
                    consistency_score = EXCLUDED.consistency_score,
                    summary = EXCLUDED.summary,
                    recommendations = EXCLUDED.recommendations
            """, 
                result.validation_id, result.source_table, result.target_table, result.validation_level.value,
                result.start_time, result.end_time, duration_ms, result.total_source_records, 
                result.total_target_records, result.matched_records, len(result.differences),
                result.consistency_score, json.dumps(result.validation_rules_applied),
                json.dumps(result.summary, default=str), json.dumps(result.recommendations)
            )
            
            # 保存差异详情
            for diff in result.differences:
                await self.connection.execute("""
                    INSERT INTO t_sys_validation_differences 
                    (validation_id, difference_type, source_table, target_table,
                     record_id, field_name, source_value, target_value,
                     severity, description, suggested_fix)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, 
                    result.validation_id, diff.difference_type.value, diff.source_table, diff.target_table,
                    str(diff.record_id) if diff.record_id else None, diff.field_name,
                    str(diff.source_value) if diff.source_value is not None else None,
                    str(diff.target_value) if diff.target_value is not None else None,
                    diff.severity, diff.description, diff.suggested_fix
                )
            
            logger.info(f"验证结果已保存: {result.validation_id}")
            
        except Exception as e:
            logger.error(f"保存验证结果失败: {e}")
    
    async def get_validation_history(self, source_table: str = None, target_table: str = None,
                                   days: int = 30) -> List[Dict[str, Any]]:
        """获取验证历史"""
        try:
            where_conditions = ["created_at > CURRENT_TIMESTAMP - INTERVAL '%s days'" % days]
            params = []
            
            if source_table:
                where_conditions.append("source_table = $%d" % (len(params) + 1))
                params.append(source_table)
            
            if target_table:
                where_conditions.append("target_table = $%d" % (len(params) + 1))
                params.append(target_table)
            
            where_clause = " AND ".join(where_conditions)
            
            history = await self.connection.fetch(f"""
                SELECT * FROM t_sys_validation_results
                WHERE {where_clause}
                ORDER BY created_at DESC
            """, *params)
            
            return [dict(record) for record in history]
            
        except Exception as e:
            logger.error(f"获取验证历史失败: {e}")
            return []
    
    async def export_validation_report(self, validation_id: str, output_file: str = None) -> str:
        """导出验证报告"""
        if output_file is None:
            output_file = f"validation_report_{validation_id}.json"
        
        try:
            # 获取验证结果
            result = await self.connection.fetchrow("""
                SELECT * FROM t_sys_validation_results WHERE validation_id = $1
            """, validation_id)
            
            if not result:
                logger.error(f"验证结果不存在: {validation_id}")
                return ""
            
            # 获取差异详情
            differences = await self.connection.fetch("""
                SELECT * FROM t_sys_validation_differences WHERE validation_id = $1
                ORDER BY severity DESC, difference_type, record_id
            """, validation_id)
            
            # 构建报告
            report = {
                'validation_result': dict(result),
                'differences': [dict(diff) for diff in differences],
                'export_time': datetime.now().isoformat()
            }
            
            # 保存到文件
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"验证报告已导出: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"导出验证报告失败: {e}")
            return ""

# 默认验证规则配置
DEFAULT_VALIDATION_RULES = {
    "rules": [
        {
            "rule_id": "count_comparison",
            "rule_name": "记录数量比较",
            "rule_type": "count",
            "source_query": "SELECT COUNT(*) FROM {source_table}",
            "target_query": "SELECT COUNT(*) FROM {target_table}",
            "comparison_fields": [],
            "tolerance": 0.0,
            "enabled": True,
            "description": "比较源表和目标表的记录总数"
        },
        {
            "rule_id": "primary_key_match",
            "rule_name": "主键匹配检查",
            "rule_type": "primary_key",
            "source_query": "SELECT {pk_field} FROM {source_table}",
            "target_query": "SELECT {pk_field} FROM {target_table}",
            "comparison_fields": ["id"],
            "tolerance": 0.0,
            "enabled": True,
            "description": "检查主键在两个表中的匹配情况"
        }
    ]
}

async def main():
    """主函数示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据一致性验证工具')
    parser.add_argument('--db-url', required=True, help='数据库连接URL')
    parser.add_argument('--source-table', required=True, help='源表名')
    parser.add_argument('--target-table', required=True, help='目标表名')
    parser.add_argument('--level', choices=['basic', 'standard', 'detailed', 'comprehensive'],
                       default='standard', help='验证级别')
    parser.add_argument('--sample-size', type=int, help='采样大小')
    parser.add_argument('--export', help='导出报告文件路径')
    
    args = parser.parse_args()
    
    validator = DataConsistencyValidator(args.db_url)
    
    try:
        await validator.connect()
        
        # 执行验证
        validation_level = ValidationLevel(args.level)
        result = await validator.validate_table_consistency(
            args.source_table, args.target_table, validation_level, args.sample_size
        )
        
        # 输出结果摘要
        print(f"验证完成: {result.validation_id}")
        print(f"一致性分数: {result.consistency_score:.4f}")
        print(f"总差异数: {len(result.differences)}")
        print(f"源表记录数: {result.total_source_records}")
        print(f"目标表记录数: {result.total_target_records}")
        print(f"匹配记录数: {result.matched_records}")
        
        # 导出报告
        if args.export:
            report_file = await validator.export_validation_report(result.validation_id, args.export)
            print(f"报告已导出: {report_file}")
        
        # 输出建议
        print("\n修复建议:")
        for i, recommendation in enumerate(result.recommendations, 1):
            print(f"{i}. {recommendation}")
    
    finally:
        await validator.disconnect()

if __name__ == "__main__":
    asyncio.run(main())