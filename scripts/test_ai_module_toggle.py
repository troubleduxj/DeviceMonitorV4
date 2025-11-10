# -*- coding: utf-8 -*-
"""
Day 7: AI模块启用/禁用功能综合测试
测试目标：
1. 测试AI模块配置的启用/禁用
2. 测试细粒度功能开关
3. 测试资源限制配置
4. 测试路由动态加载
5. 测试装饰器功能开关检查
"""

import os
import sys
import asyncio
from typing import Dict, List

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 测试结果收集
test_results: List[Dict] = []


def log_test(test_name: str, passed: bool, message: str = ""):
    """记录测试结果"""
    status = "[PASS]" if passed else "[FAIL]"
    result = {
        "test": test_name,
        "passed": passed,
        "message": message
    }
    test_results.append(result)
    try:
        print(f"{status}: {test_name}")
        if message:
            print(f"  -> {message}")
    except UnicodeEncodeError:
        # Windows PowerShell编码兼容处理
        print(f"{status}: {test_name}".encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
        if message:
            print(f"  -> {message}".encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))


def print_section(title: str):
    """打印测试章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


async def test_ai_settings_loading():
    """测试1: AI配置加载"""
    print_section("测试1: AI配置加载")
    
    try:
        from app.settings.ai_settings import ai_settings
        
        # 检查配置对象是否正确加载
        log_test(
            "配置对象加载",
            ai_settings is not None,
            f"AI模块启用状态: {ai_settings.ai_module_enabled}"
        )
        
        # 检查各项配置
        log_test(
            "资源限制配置",
            ai_settings.ai_max_memory_mb > 0 and ai_settings.ai_max_cpu_percent > 0,
            f"内存限制: {ai_settings.ai_max_memory_mb}MB, CPU限制: {ai_settings.ai_max_cpu_percent}%"
        )
        
        log_test(
            "工作线程配置",
            ai_settings.ai_worker_threads > 0,
            f"线程数: {ai_settings.ai_worker_threads}"
        )
        
        # 检查功能开关方法
        anomaly_enabled = ai_settings.is_feature_enabled('anomaly_detection')
        log_test(
            "功能开关检查方法",
            isinstance(anomaly_enabled, bool),
            f"异常检测启用: {anomaly_enabled}"
        )
        
    except Exception as e:
        log_test("配置对象加载", False, f"错误: {str(e)}")


async def test_ai_loader():
    """测试2: AI模块加载器"""
    print_section("测试2: AI模块加载器")
    
    try:
        from app.ai_module.loader import ai_loader
        from app.settings.ai_settings import ai_settings
        
        # 测试加载器状态检查
        is_enabled = ai_loader.is_enabled()
        log_test(
            "加载器启用状态检查",
            is_enabled == ai_settings.ai_module_enabled,
            f"启用状态: {is_enabled}"
        )
        
        # 如果模块已启用，检查是否已加载
        if is_enabled:
            is_loaded = ai_loader.is_loaded()
            log_test(
                "模块加载状态",
                is_loaded,
                f"已加载: {is_loaded}"
            )
            
            # 检查路由是否注册
            routers = ai_loader.get_routers()
            log_test(
                "AI路由注册",
                len(routers) > 0,
                f"路由数量: {len(routers)}"
            )
        else:
            log_test(
                "模块未启用（符合预期）",
                True,
                "AI模块在配置中被禁用"
            )
            
    except Exception as e:
        log_test("AI模块加载器测试", False, f"错误: {str(e)}")


async def test_feature_decorators():
    """测试3: 功能开关装饰器"""
    print_section("测试3: 功能开关装饰器")
    
    try:
        from app.ai_module.decorators import require_ai_module, require_ai_feature
        from app.settings.ai_settings import ai_settings
        
        # 测试模块开关装饰器
        @require_ai_module
        async def mock_ai_endpoint():
            return {"status": "ok"}
        
        # 如果AI模块启用，应该正常执行
        if ai_settings.ai_module_enabled:
            try:
                result = await mock_ai_endpoint()
                log_test(
                    "require_ai_module装饰器(启用)",
                    result.get("status") == "ok",
                    "装饰器允许执行"
                )
            except Exception as e:
                log_test(
                    "require_ai_module装饰器(启用)",
                    False,
                    f"意外错误: {str(e)}"
                )
        else:
            # 如果AI模块禁用，应该抛出异常
            try:
                result = await mock_ai_endpoint()
                log_test(
                    "require_ai_module装饰器(禁用)",
                    False,
                    "装饰器应该阻止执行但没有"
                )
            except Exception as e:
                log_test(
                    "require_ai_module装饰器(禁用)",
                    "AI模块未启用" in str(e) or "not enabled" in str(e).lower(),
                    f"装饰器正确阻止执行: {type(e).__name__}"
                )
        
        # 测试细粒度功能开关装饰器
        @require_ai_feature("anomaly_detection")
        async def mock_anomaly_endpoint():
            return {"status": "ok"}
        
        if ai_settings.is_feature_enabled("anomaly_detection"):
            try:
                result = await mock_anomaly_endpoint()
                log_test(
                    "require_ai_feature装饰器(启用)",
                    result.get("status") == "ok",
                    "异常检测功能可用"
                )
            except Exception as e:
                log_test(
                    "require_ai_feature装饰器(启用)",
                    False,
                    f"意外错误: {str(e)}"
                )
        else:
            try:
                result = await mock_anomaly_endpoint()
                log_test(
                    "require_ai_feature装饰器(禁用)",
                    False,
                    "装饰器应该阻止执行但没有"
                )
            except Exception as e:
                log_test(
                    "require_ai_feature装饰器(禁用)",
                    "功能未启用" in str(e) or "not enabled" in str(e).lower(),
                    f"装饰器正确阻止执行: {type(e).__name__}"
                )
                
    except Exception as e:
        log_test("功能开关装饰器测试", False, f"错误: {str(e)}")


async def test_resource_monitor():
    """测试4: 资源监控"""
    print_section("测试4: 资源监控")
    
    try:
        from app.ai_module.monitor import AIResourceMonitor
        from app.settings.ai_settings import ai_settings
        
        if not ai_settings.ai_module_enabled:
            log_test(
                "资源监控（模块禁用）",
                True,
                "AI模块禁用，跳过资源监控测试"
            )
            return
        
        monitor = AIResourceMonitor()
        
        # 测试资源使用获取
        usage = monitor.get_usage()
        log_test(
            "资源使用数据获取",
            "cpu_percent" in usage and "memory_mb" in usage,
            f"CPU: {usage.get('cpu_percent', 'N/A')}%, 内存: {usage.get('memory_mb', 'N/A')}MB"
        )
        
        # 测试资源限制检查
        is_within_limit = monitor.check_limits()
        log_test(
            "资源限制检查",
            isinstance(is_within_limit, bool),
            f"资源在限制内: {is_within_limit}"
        )
        
        # 测试资源统计
        stats = monitor.get_statistics()
        log_test(
            "资源统计信息",
            isinstance(stats, dict),
            f"统计信息获取成功，包含 {len(stats)} 项数据"
        )
        
    except Exception as e:
        log_test("资源监控测试", False, f"错误: {str(e)}")


async def test_system_health_api():
    """测试5: 系统健康检查API"""
    print_section("测试5: 系统健康检查API")
    
    try:
        from fastapi.testclient import TestClient
        from app import app as fastapi_app
        
        client = TestClient(fastapi_app)
        
        # 测试系统健康API
        response = client.get("/api/v2/system/health")
        
        log_test(
            "系统健康API响应",
            response.status_code == 200,
            f"状态码: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            
            log_test(
                "健康状态字段",
                "status" in data,
                f"系统状态: {data.get('status', 'N/A')}"
            )
            
            log_test(
                "AI模块状态字段",
                "ai_module_status" in data,
                f"AI模块信息完整"
            )
            
            ai_status = data.get("ai_module_status", {})
            from app.settings.ai_settings import ai_settings
            
            log_test(
                "AI模块启用状态一致性",
                ai_status.get("module_enabled") == ai_settings.ai_module_enabled,
                f"API返回: {ai_status.get('module_enabled')}, 配置: {ai_settings.ai_module_enabled}"
            )
            
    except Exception as e:
        log_test("系统健康API测试", False, f"错误: {str(e)}")


async def test_frontend_integration():
    """测试6: 前端集成"""
    print_section("测试6: 前端集成")
    
    try:
        # 检查前端Store文件（可能是ai-module-store.ts或index.ts）
        store_path_specific = "web/src/store/modules/ai/ai-module-store.ts"
        store_path_index = "web/src/store/modules/ai/index.ts"
        store_exists = os.path.exists(store_path_specific) or os.path.exists(store_path_index)
        actual_store_path = store_path_specific if os.path.exists(store_path_specific) else store_path_index
        log_test(
            "AI模块Store文件",
            store_exists,
            f"文件路径: {actual_store_path}"
        )
        
        # 检查前端API客户端文件
        api_path = "web/src/api/v2/ai-module.js"
        log_test(
            "AI模块API客户端文件",
            os.path.exists(api_path),
            f"文件路径: {api_path}"
        )
        
        # 检查路由配置文件（可能是.js或.ts）
        route_path_js = "web/src/views/ai-monitor/route.js"
        route_path_ts = "web/src/views/ai-monitor/route.ts"
        route_exists = os.path.exists(route_path_js) or os.path.exists(route_path_ts)
        actual_path = route_path_js if os.path.exists(route_path_js) else route_path_ts
        log_test(
            "AI监测路由文件",
            route_exists,
            f"文件路径: {actual_path}"
        )
        
        # 检查main.js中的AI模块初始化
        main_js_path = "web/src/main.js"
        if os.path.exists(main_js_path):
            with open(main_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
                log_test(
                    "main.js中AI模块初始化",
                    "aiModuleStore.checkAIModule" in content,
                    "AI模块初始化代码存在"
                )
        
    except Exception as e:
        log_test("前端集成测试", False, f"错误: {str(e)}")


def print_summary():
    """打印测试摘要"""
    print_section("测试摘要")
    
    total = len(test_results)
    passed = sum(1 for r in test_results if r["passed"])
    failed = total - passed
    
    print(f"总测试数: {total}")
    print(f"通过: {passed} [OK]")
    print(f"失败: {failed} [FAILED]")
    print(f"通过率: {(passed / total * 100) if total > 0 else 0:.1f}%")
    
    if failed > 0:
        print("\n失败的测试:")
        for r in test_results:
            if not r["passed"]:
                print(f"  [X] {r['test']}")
                if r["message"]:
                    print(f"     {r['message']}")
    
    print("\n" + "=" * 60)
    
    # 返回状态码
    return 0 if failed == 0 else 1


async def main():
    """主测试流程"""
    print("=" * 60)
    print("  Day 7: AI模块启用/禁用功能综合测试")
    print("=" * 60)
    
    # 运行所有测试
    await test_ai_settings_loading()
    await test_ai_loader()
    await test_feature_decorators()
    await test_resource_monitor()
    await test_system_health_api()
    await test_frontend_integration()
    
    # 打印摘要
    exit_code = print_summary()
    
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

