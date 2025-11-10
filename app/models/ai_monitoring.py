#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI监控模块数据模型
包含趋势预测、模型管理、数据标注、健康评分等功能的数据模型

⚠️ 模块归属: AI监测模块 (ai_module)
注意: 这些模型属于AI模块，但保留在 models/ 目录下便于 Tortoise-ORM 管理。
当 AI_MODULE_ENABLED=false 时，这些表可选不创建。
参见: app/settings/ai_settings.py
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from tortoise import fields
from tortoise.models import Model

from app.models.base import BaseModel


class PredictionStatus(str, Enum):
    """预测状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelStatus(str, Enum):
    """模型状态枚举"""
    DRAFT = "draft"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class AnnotationStatus(str, Enum):
    """标注状态枚举"""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class HealthScoreStatus(str, Enum):
    """健康评分状态枚举"""
    CALCULATING = "calculating"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisStatus(str, Enum):
    """分析状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# =====================================================
# 趋势预测模型
# =====================================================

class AIPrediction(BaseModel):
    """AI趋势预测模型"""
    
    class Meta:
        table = "t_ai_predictions"
        table_description = "AI趋势预测表"
    
    # 基本信息
    prediction_name = fields.CharField(max_length=200, description="预测名称")
    description = fields.TextField(null=True, description="预测描述")
    
    # 预测配置
    target_variable = fields.CharField(max_length=100, description="目标变量")
    prediction_horizon = fields.IntField(description="预测时间范围(小时)")
    model_type = fields.CharField(max_length=50, description="模型类型")
    parameters = fields.JSONField(default=dict, description="预测参数(JSON)")
    
    # 数据源配置
    data_source = fields.CharField(max_length=100, description="数据源")
    data_filters = fields.JSONField(default=dict, description="数据过滤条件(JSON)")
    
    # 状态和结果
    status = fields.CharEnumField(PredictionStatus, default=PredictionStatus.PENDING, description="预测状态")
    progress = fields.IntField(default=0, description="执行进度(0-100)")
    
    # 结果数据
    result_data = fields.JSONField(null=True, description="预测结果数据(JSON)")
    accuracy_score = fields.FloatField(null=True, description="准确率分数")
    confidence_interval = fields.JSONField(null=True, description="置信区间(JSON)")
    
    # 执行信息
    started_at = fields.DatetimeField(null=True, description="开始时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")
    error_message = fields.TextField(null=True, description="错误信息")
    
    # 导出和分享
    export_formats = fields.JSONField(default=list, description="支持的导出格式")
    shared_with = fields.JSONField(default=list, description="分享给的用户列表")
    is_public = fields.BooleanField(default=False, description="是否公开")
    
    # 审计字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    created_by = fields.BigIntField(null=True, description="创建人ID")
    updated_by = fields.BigIntField(null=True, description="更新人ID")


# =====================================================
# 模型管理模型
# =====================================================

class AIModel(BaseModel):
    """AI模型管理模型"""
    
    class Meta:
        table = "t_ai_models"
        table_description = "AI模型管理表"
    
    # 基本信息
    model_name = fields.CharField(max_length=200, description="模型名称")
    model_version = fields.CharField(max_length=50, description="模型版本")
    description = fields.TextField(null=True, description="模型描述")
    
    # 模型配置
    model_type = fields.CharField(max_length=50, description="模型类型")
    algorithm = fields.CharField(max_length=100, description="算法名称")
    framework = fields.CharField(max_length=50, description="框架名称")
    
    # 文件信息
    model_file_path = fields.CharField(max_length=500, description="模型文件路径")
    model_file_size = fields.BigIntField(null=True, description="模型文件大小(字节)")
    model_file_hash = fields.CharField(max_length=64, null=True, description="模型文件哈希")
    
    # 训练信息
    training_dataset = fields.CharField(max_length=200, null=True, description="训练数据集")
    training_parameters = fields.JSONField(default=dict, description="训练参数(JSON)")
    training_metrics = fields.JSONField(null=True, description="训练指标(JSON)")
    
    # 状态信息
    status = fields.CharEnumField(ModelStatus, default=ModelStatus.DRAFT, description="模型状态")
    
    # 性能指标
    accuracy = fields.FloatField(null=True, description="准确率")
    precision = fields.FloatField(null=True, description="精确率")
    recall = fields.FloatField(null=True, description="召回率")
    f1_score = fields.FloatField(null=True, description="F1分数")
    
    # 部署信息
    deployment_config = fields.JSONField(null=True, description="部署配置(JSON)")
    deployed_at = fields.DatetimeField(null=True, description="部署时间")
    
    # 审计字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    created_by = fields.BigIntField(null=True, description="创建人ID")
    updated_by = fields.BigIntField(null=True, description="更新人ID")


# =====================================================
# 数据标注模型
# =====================================================

class AIAnnotationProject(BaseModel):
    """AI数据标注项目模型"""
    
    class Meta:
        table = "t_ai_annotation_projects"
        table_description = "AI数据标注项目表"
    
    # 基本信息
    project_name = fields.CharField(max_length=200, description="项目名称")
    description = fields.TextField(null=True, description="项目描述")
    
    # 项目配置
    annotation_type = fields.CharField(max_length=50, description="标注类型")
    data_type = fields.CharField(max_length=50, description="数据类型")
    label_schema = fields.JSONField(default=dict, description="标签模式(JSON)")
    
    # 数据信息
    total_samples = fields.IntField(default=0, description="总样本数")
    annotated_samples = fields.IntField(default=0, description="已标注样本数")
    reviewed_samples = fields.IntField(default=0, description="已审核样本数")
    
    # 状态信息
    status = fields.CharEnumField(AnnotationStatus, default=AnnotationStatus.CREATED, description="项目状态")
    progress = fields.FloatField(default=0.0, description="完成进度(0-100)")
    
    # 质量控制
    quality_threshold = fields.FloatField(default=0.8, description="质量阈值")
    inter_annotator_agreement = fields.FloatField(null=True, description="标注者间一致性")
    
    # 导入导出
    import_config = fields.JSONField(null=True, description="导入配置(JSON)")
    export_config = fields.JSONField(null=True, description="导出配置(JSON)")
    
    # 审计字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    created_by = fields.BigIntField(null=True, description="创建人ID")
    updated_by = fields.BigIntField(null=True, description="更新人ID")


# =====================================================
# 健康评分模型
# =====================================================

class AIHealthScore(BaseModel):
    """AI健康评分模型"""
    
    class Meta:
        table = "t_ai_health_scores"
        table_description = "AI健康评分表"
    
    # 基本信息
    score_name = fields.CharField(max_length=200, description="评分名称")
    description = fields.TextField(null=True, description="评分描述")
    
    # 评分对象
    target_type = fields.CharField(max_length=50, description="评分对象类型")
    target_id = fields.BigIntField(description="评分对象ID")
    
    # 评分配置
    scoring_algorithm = fields.CharField(max_length=100, description="评分算法")
    weight_config = fields.JSONField(default=dict, description="权重配置(JSON)")
    threshold_config = fields.JSONField(default=dict, description="阈值配置(JSON)")
    
    # 评分结果
    overall_score = fields.FloatField(null=True, description="总体评分(0-100)")
    dimension_scores = fields.JSONField(null=True, description="维度评分(JSON)")
    risk_level = fields.CharField(max_length=20, null=True, description="风险等级")
    
    # 状态信息
    status = fields.CharEnumField(HealthScoreStatus, default=HealthScoreStatus.CALCULATING, description="评分状态")
    
    # 计算信息
    calculated_at = fields.DatetimeField(null=True, description="计算时间")
    data_period_start = fields.DatetimeField(null=True, description="数据周期开始")
    data_period_end = fields.DatetimeField(null=True, description="数据周期结束")
    
    # 趋势信息
    trend_direction = fields.CharField(max_length=20, null=True, description="趋势方向")
    trend_confidence = fields.FloatField(null=True, description="趋势置信度")
    
    # 审计字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    created_by = fields.BigIntField(null=True, description="创建人ID")
    updated_by = fields.BigIntField(null=True, description="更新人ID")


# =====================================================
# 智能分析模型
# =====================================================

class AIAnalysis(BaseModel):
    """AI智能分析模型"""
    
    class Meta:
        table = "t_ai_analysis"
        table_description = "AI智能分析表"
    
    # 基本信息
    analysis_name = fields.CharField(max_length=200, description="分析名称")
    description = fields.TextField(null=True, description="分析描述")
    
    # 分析配置
    analysis_type = fields.CharField(max_length=50, description="分析类型")
    algorithm = fields.CharField(max_length=100, description="分析算法")
    parameters = fields.JSONField(default=dict, description="分析参数(JSON)")
    
    # 数据源
    data_sources = fields.JSONField(default=list, description="数据源列表(JSON)")
    data_filters = fields.JSONField(default=dict, description="数据过滤条件(JSON)")
    
    # 状态信息
    status = fields.CharEnumField(AnalysisStatus, default=AnalysisStatus.PENDING, description="分析状态")
    progress = fields.IntField(default=0, description="执行进度(0-100)")
    
    # 结果信息
    result_data = fields.JSONField(null=True, description="分析结果(JSON)")
    insights = fields.JSONField(null=True, description="洞察信息(JSON)")
    recommendations = fields.JSONField(null=True, description="建议信息(JSON)")
    
    # 执行信息
    started_at = fields.DatetimeField(null=True, description="开始时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")
    error_message = fields.TextField(null=True, description="错误信息")
    
    # 定时分析
    is_scheduled = fields.BooleanField(default=False, description="是否定时分析")
    schedule_config = fields.JSONField(null=True, description="定时配置(JSON)")
    next_run_at = fields.DatetimeField(null=True, description="下次运行时间")
    
    # 审计字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    created_by = fields.BigIntField(null=True, description="创建人ID")
    updated_by = fields.BigIntField(null=True, description="更新人ID")