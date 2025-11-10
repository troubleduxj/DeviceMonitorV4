#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断后端启动问题
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Backend Diagnosis")
print("=" * 60)
print()

# 1. 检查Settings导入
print("[1/5] Checking Settings import...")
try:
    from app.settings.config import Settings
    settings = Settings()
    print(f"   [OK] Settings loaded")
    print(f"   PORT: {settings.PORT}")
    print(f"   DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print()
except Exception as e:
    print(f"   [ERROR] {e}")
    print()

# 2. 检查模型导入
print("[2/5] Checking models import...")
try:
    from app.models.ai_monitoring import AIPrediction
    print(f"   [OK] AIPrediction model loaded")
    print()
except Exception as e:
    print(f"   [ERROR] {e}")
    print()

# 3. 检查Schema导入
print("[3/5] Checking schemas import...")
try:
    from app.schemas.ai_monitoring import PredictionResponse, BatchPredictionCreate
    print(f"   [OK] AI schemas loaded")
    print()
except Exception as e:
    print(f"   [ERROR] {e}")
    print()

# 4. 检查API路由导入
print("[4/5] Checking API router import...")
try:
    from app.api.v2.ai.predictions import router
    print(f"   [OK] Predictions router loaded")
    print(f"   Prefix: {router.prefix}")
    print(f"   Routes: {len(router.routes)}")
    print()
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()
    print()

# 5. 检查v2路由注册
print("[5/5] Checking v2 router registration...")
try:
    from app.api.v2 import v2_router
    print(f"   [OK] V2 router loaded")
    print(f"   Total routes: {len(v2_router.routes)}")
    
    # 查找AI预测相关路由
    ai_routes = [r for r in v2_router.routes if 'prediction' in r.path.lower()]
    print(f"   AI prediction routes: {len(ai_routes)}")
    for route in ai_routes[:5]:  # 显示前5个
        print(f"      - {route.methods} {route.path}")
    print()
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()
    print()

print("=" * 60)
print("Diagnosis Complete")
print("=" * 60)

