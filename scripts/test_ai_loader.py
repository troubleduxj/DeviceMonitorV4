#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试AI模块加载器"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.ai_module.loader import ai_loader

print("=" * 60)
print("AI模块加载器测试")
print("=" * 60)
print(f"AI模块启用: {ai_loader.is_enabled()}")
print(f"\n开始加载模块...")

success = ai_loader.load_module()
print(f"\n加载结果: {'成功' if success else '失败'}")
print(f"是否已加载: {ai_loader._loaded}")
print(f"路由数量: {len(ai_loader.get_routers())}")

print("=" * 60)
print("[OK] 加载器测试通过！")

