#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向 app/.env.dev 文件添加AI模块配置
"""
import os

def add_ai_config():
    env_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'app',
        '.env.dev'
    )
    
    # 读取现有内容
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    else:
        print(f"[ERROR] 文件不存在: {env_file}")
        return
    
    # 检查是否已有AI配置
    if 'AI_MODULE_ENABLED' in existing_content:
        print("[OK] AI配置已存在，无需添加")
        return
    
    # 准备AI配置内容
    ai_config = """
# ============================================================================
# AI监测模块配置
# ============================================================================

# 全局开关：是否启用AI监测模块
AI_MODULE_ENABLED=false

# 功能开关：细粒度控制各个AI功能
AI_FEATURE_EXTRACTION_ENABLED=true
AI_ANOMALY_DETECTION_ENABLED=true
AI_TREND_PREDICTION_ENABLED=true
AI_HEALTH_SCORING_ENABLED=true
AI_SMART_ANALYSIS_ENABLED=true

# 资源限制
AI_MAX_MEMORY_MB=1024
AI_MAX_CPU_PERCENT=75
AI_WORKER_THREADS=4

# AI模型文件存储路径
AI_MODELS_PATH=./data/ai_models

# 后台任务：是否启用AI模块的后台任务（如定时训练、数据同步）
AI_BACKGROUND_TASKS_ENABLED=true
"""
    
    # 追加AI配置
    with open(env_file, 'a', encoding='utf-8') as f:
        f.write(ai_config)
    
    print(f"[OK] AI配置已添加到: {env_file}")
    print("\n[配置内容]")
    print(ai_config)
    print("\n[提示]")
    print("  - 如需启用AI模块，将 AI_MODULE_ENABLED 设置为 true")
    print("  - 修改后需要重启后端服务: python run.py")

if __name__ == '__main__':
    add_ai_config()

