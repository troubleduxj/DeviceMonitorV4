#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端是否可以正常导入和启动
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("Testing backend imports...")
print()

try:
    print("[1/3] Importing app...")
    from app import app
    print("[OK] App imported successfully")
    print()
    
    print("[2/3] Checking routes...")
    route_count = len(app.routes)
    print(f"[OK] Total routes: {route_count}")
    
    # 查找AI预测相关路由
    prediction_routes = [r for r in app.routes if hasattr(r, 'path') and 'prediction' in r.path.lower()]
    print(f"[OK] Prediction routes: {len(prediction_routes)}")
    for route in prediction_routes[:10]:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            print(f"   - {list(route.methods)} {route.path}")
    print()
    
    print("[3/3] App configuration...")
    print(f"[OK] App title: {app.title}")
    print(f"[OK] App version: {app.version}")
    print()
    
    print("=" * 60)
    print("[SUCCESS] All imports successful!")
    print("=" * 60)
    print()
    print("Backend is ready to start with: python run.py")
    
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

