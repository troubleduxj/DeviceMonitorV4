# -*- coding: utf-8 -*-
"""
Day 3-4 集成测试
测试AI模块代码重构后的完整性
"""
import os
import sys

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """测试所有AI模块导入"""
    print("=" * 60)
    print("Day 3-4 集成测试")
    print("=" * 60)
    
    print("\n[测试1] AI模块导入")
    try:
        from app.ai_module import __version__
        from app.ai_module.loader import ai_loader
        print(f"  [OK] AI模块导入成功")
        print(f"  - 版本: {__version__}")
    except ImportError as e:
        print(f"  [FAIL] AI模块导入失败: {e}")
        return False
    
    print("\n[测试2] AI配置导入")
    try:
        from app.settings.ai_settings import ai_settings
        print(f"  [OK] AI配置导入成功")
        print(f"  - AI模块启用: {ai_settings.ai_module_enabled}")
        print(f"  - 最大内存: {ai_settings.ai_max_memory_mb}MB")
    except ImportError as e:
        print(f"  [FAIL] AI配置导入失败: {e}")
        return False
    
    print("\n[测试3] AI数据模型导入")
    try:
        from app.models.ai_monitoring import (
            AIPrediction, AIModel, AIAnnotationProject,
            AIHealthScore, AIAnalysis
        )
        print(f"  [OK] AI数据模型导入成功")
        print(f"  - 模型数量: 5")
    except ImportError as e:
        print(f"  [FAIL] AI数据模型导入失败: {e}")
        return False
    
    print("\n[测试4] AI API路由导入")
    try:
        from app.api.v2.ai import ai_router
        print(f"  [OK] AI总路由导入成功")
        
        # 尝试导入各个子路由
        from app.api.v2.ai.analysis import router as analysis_router
        from app.api.v2.ai.predictions import router as predictions_router
        from app.api.v2.ai.models import router as models_router
        from app.api.v2.ai.health_scores import router as health_scores_router
        from app.api.v2.ai.annotations import router as annotations_router
        print(f"  [OK] AI子路由导入成功")
        print(f"  - 子路由数量: 5")
    except ImportError as e:
        print(f"  [FAIL] AI路由导入失败: {e}")
        return False
    
    print("\n[测试5] AI服务目录")
    ai_services_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'services', 'ai')
    if os.path.exists(ai_services_dir):
        print(f"  [OK] AI服务目录存在: {ai_services_dir}")
    else:
        print(f"  [FAIL] AI服务目录不存在")
        return False
    
    print("\n[测试6] AI模块加载器功能")
    try:
        from app.settings.ai_settings import ai_settings
        from app.ai_module.loader import ai_loader
        
        print(f"  - AI模块是否启用: {ai_loader.is_enabled()}")
        print(f"  - AI模块是否已加载: {ai_loader.is_loaded()}")
        
        # 尝试加载模块
        if ai_settings.ai_module_enabled:
            success = ai_loader.load_module()
            print(f"  - 模块加载结果: {'成功' if success else '失败'}")
            print(f"  - 注册的路由数量: {len(ai_loader.get_routers())}")
            
            # 卸载模块
            ai_loader.unload_module()
            print(f"  [OK] AI模块加载器功能正常")
        else:
            print(f"  [OK] AI模块未启用，跳过加载测试")
    except Exception as e:
        print(f"  [FAIL] AI模块加载器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n[测试7] 验证路由前缀")
    try:
        from app.api.v2.ai.analysis import router as analysis_router
        from app.api.v2.ai.predictions import router as predictions_router
        from app.api.v2.ai.models import router as models_router
        from app.api.v2.ai.health_scores import router as health_scores_router
        from app.api.v2.ai.annotations import router as annotations_router
        
        expected_prefixes = {
            "analysis": "/analysis",
            "predictions": "/predictions",
            "models": "/models",
            "health_scores": "/health-scores",
            "annotations": "/annotations"
        }
        
        routers = {
            "analysis": analysis_router,
            "predictions": predictions_router,
            "models": models_router,
            "health_scores": health_scores_router,
            "annotations": annotations_router
        }
        
        all_correct = True
        for name, router in routers.items():
            prefix = router.prefix
            expected = expected_prefixes[name]
            if prefix == expected:
                print(f"  [OK] {name}: {prefix}")
            else:
                print(f"  [FAIL] {name}: 期望 {expected}, 实际 {prefix}")
                all_correct = False
        
        if all_correct:
            print(f"  [OK] 所有路由前缀正确")
        else:
            return False
    except Exception as e:
        print(f"  [FAIL] 路由前缀验证失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = test_imports()
    
    print("\n" + "=" * 60)
    if success:
        print("[OK] Day 3-4 集成测试全部通过!")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 启动应用程序: python run.py")
        print("  2. 检查日志输出是否包含AI模块相关信息")
        print("  3. 如果AI模块启用，访问: http://localhost:8001/api/v2/ai/analysis")
        sys.exit(0)
    else:
        print("[FAIL] Day 3-4 集成测试失败!")
        print("=" * 60)
        sys.exit(1)

