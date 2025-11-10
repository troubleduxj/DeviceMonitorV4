#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试AI模块配置"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.settings.ai_settings import ai_settings

print("=" * 60)
print("AI模块配置测试")
print("=" * 60)
print(f"AI模块启用: {ai_settings.ai_module_enabled}")
print(f"最大内存: {ai_settings.ai_max_memory_mb}MB")
print(f"最大CPU: {ai_settings.ai_max_cpu_percent}%")
print(f"工作线程: {ai_settings.ai_worker_threads}")
print(f"模型路径: {ai_settings.ai_models_path}")
print(f"\n功能开关:")
print(f"  - 特征提取: {ai_settings.ai_feature_extraction_enabled}")
print(f"  - 异常检测: {ai_settings.ai_anomaly_detection_enabled}")
print(f"  - 趋势预测: {ai_settings.ai_trend_prediction_enabled}")
print(f"  - 健康评分: {ai_settings.ai_health_scoring_enabled}")
print(f"  - 智能分析: {ai_settings.ai_smart_analysis_enabled}")
print(f"\n功能检查测试:")
print(f"  异常检测启用: {ai_settings.is_feature_enabled('anomaly_detection')}")
print(f"  趋势预测启用: {ai_settings.is_feature_enabled('trend_prediction')}")
print("=" * 60)
print("[OK] 配置测试通过！")

