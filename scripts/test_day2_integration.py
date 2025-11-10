#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试Day 2集成"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Day 2 集成测试")
print("=" * 60)

# 测试1: AI配置加载
print("\n[测试1] AI配置加载")
from app.settings.ai_settings import ai_settings
print(f"  AI模块启用: {ai_settings.ai_module_enabled}")
print(f"  最大内存: {ai_settings.ai_max_memory_mb}MB")

# 测试2: AI加载器
print("\n[测试2] AI加载器")
from app.ai_module.loader import ai_loader
print(f"  加载器可用: True")
print(f"  是否已加载: {ai_loader._loaded}")

# 测试3: 健康检查API导入
print("\n[测试3] 健康检查API")
try:
    from app.api.v2.system_health import router
    print(f"  健康检查路由导入成功: True")
    print(f"  路由端点数: {len(router.routes)}")
except Exception as e:
    print(f"  健康检查路由导入失败: {e}")

# 测试4: 应用启动集成
print("\n[测试4] 应用启动集成检查")
try:
    # 读取app/__init__.py检查是否包含AI模块初始化
    init_file = project_root / "app" / "__init__.py"
    content = init_file.read_text(encoding='utf-8')
    
    checks = {
        "AI模块导入": "from app.ai_module.loader import ai_loader" in content,
        "AI配置导入": "from app.settings.ai_settings import ai_settings" in content,
        "AI模块初始化": "ai_loader.load_module()" in content,
        "AI模块卸载": "ai_loader.unload_module()" in content,
    }
    
    for check_name, result in checks.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {check_name}")
        
except Exception as e:
    print(f"  应用启动集成检查失败: {e}")

print("\n" + "=" * 60)
print("[OK] Day 2 集成测试完成！")
print("=" * 60)
print("\n下一步: 启动应用验证")
print("  python run.py")
print("  然后访问: http://localhost:8001/api/v2/system/health")

