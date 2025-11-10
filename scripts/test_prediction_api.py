#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI预测管理API接口
验证批量创建预测和查询历史功能
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from httpx import AsyncClient
import json


class PredictionAPITester:
    """预测API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.client = None
        self.test_results = []
    
    async def __aenter__(self):
        self.client = AsyncClient(base_url=self.base_url, timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def log_test(self, name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {name}")
        if message:
            print(f"   {message}")
        self.test_results.append({
            "name": name,
            "success": success,
            "message": message
        })
    
    async def test_batch_create_predictions(self):
        """测试批量创建预测任务"""
        print("\n" + "=" * 60)
        print("[TEST 1] Batch Create Predictions")
        print("=" * 60)
        
        try:
            # 准备测试数据
            payload = {
                "device_codes": ["WLD-001", "WLD-002", "WLD-003"],
                "metric_name": "temperature",
                "prediction_horizon": 24,
                "model_type": "ARIMA"
            }
            
            print(f"\n[POST] /api/v2/ai-monitor/predictions/batch")
            print(f"   Payload: {json.dumps(payload, indent=2)}")
            
            response = await self.client.post(
                "/api/v2/ai-monitor/predictions/batch",
                json=payload
            )
            
            print(f"\n[RESPONSE] Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
                
                if data.get('code') in [200, 201]:
                    result = data.get('data', {})
                    total = result.get('total', 0)
                    successful = result.get('successful', 0)
                    
                    self.log_test(
                        "批量创建预测任务",
                        successful > 0,
                        f"成功创建 {successful}/{total} 个预测任务"
                    )
                    
                    # 保存预测ID供后续测试
                    predictions = result.get('predictions', [])
                    if predictions:
                        self.first_prediction_id = predictions[0].get('id')
                        self.test_device_code = predictions[0].get('device_code', 'WLD-001')
                    
                    return True
                else:
                    self.log_test("批量创建预测任务", False, f"API返回错误: {data.get('message')}")
                    return False
            else:
                error_text = response.text[:200]
                self.log_test("批量创建预测任务", False, f"HTTP {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("批量创建预测任务", False, f"异常: {str(e)}")
            return False
    
    async def test_get_prediction_history(self):
        """测试查询预测历史"""
        print("\n" + "=" * 60)
        print("[TEST 2] Query Prediction History")
        print("=" * 60)
        
        try:
            device_code = getattr(self, 'test_device_code', 'WLD-001')
            
            params = {
                "device_code": device_code,
                "metric_name": "temperature",
                "page": 1,
                "page_size": 20
            }
            
            print(f"\n[GET] /api/v2/ai-monitor/predictions/history")
            print(f"   Params: {params}")
            
            response = await self.client.get(
                "/api/v2/ai-monitor/predictions/history",
                params=params
            )
            
            print(f"\n[RESPONSE] Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
                
                if data.get('code') == 200:
                    result = data.get('data', {})
                    total = result.get('total', 0)
                    items = result.get('items', [])
                    
                    self.log_test(
                        "查询预测历史",
                        True,
                        f"查询到 {total} 条记录，返回 {len(items)} 条"
                    )
                    
                    # 验证返回的数据结构
                    if items:
                        first_item = items[0]
                        has_device_code = 'device_code' in first_item
                        has_metric_name = 'metric_name' in first_item
                        
                        self.log_test(
                            "数据结构验证",
                            has_device_code and has_metric_name,
                            f"device_code: {has_device_code}, metric_name: {has_metric_name}"
                        )
                    
                    return True
                else:
                    self.log_test("查询预测历史", False, f"API返回错误: {data.get('message')}")
                    return False
            else:
                error_text = response.text[:200]
                self.log_test("查询预测历史", False, f"HTTP {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("查询预测历史", False, f"异常: {str(e)}")
            return False
    
    async def test_get_prediction_list(self):
        """测试获取预测列表"""
        print("\n" + "=" * 60)
        print("[TEST 3] Get Prediction List")
        print("=" * 60)
        
        try:
            params = {
                "page": 1,
                "page_size": 10
            }
            
            print(f"\n[GET] /api/v2/ai-monitor/predictions")
            print(f"   Params: {params}")
            
            response = await self.client.get(
                "/api/v2/ai-monitor/predictions",
                params=params
            )
            
            print(f"\n[RESPONSE] Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
                
                if data.get('code') == 200:
                    result = data.get('data', {})
                    total = result.get('total', 0)
                    
                    self.log_test(
                        "获取预测列表",
                        True,
                        f"共 {total} 条预测记录"
                    )
                    return True
                else:
                    self.log_test("获取预测列表", False, f"API返回错误: {data.get('message')}")
                    return False
            else:
                error_text = response.text[:200]
                self.log_test("获取预测列表", False, f"HTTP {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("获取预测列表", False, f"异常: {str(e)}")
            return False
    
    async def test_get_prediction_detail(self):
        """测试获取预测详情"""
        if not hasattr(self, 'first_prediction_id'):
            print("\n[WARNING] Skip TEST 4: No prediction ID available")
            return False
        
        print("\n" + "=" * 60)
        print("[TEST 4] Get Prediction Detail")
        print("=" * 60)
        
        try:
            prediction_id = self.first_prediction_id
            
            print(f"\n[GET] /api/v2/ai-monitor/predictions/{prediction_id}")
            
            response = await self.client.get(
                f"/api/v2/ai-monitor/predictions/{prediction_id}"
            )
            
            print(f"\n[RESPONSE] Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
                
                if data.get('code') == 200:
                    self.log_test("获取预测详情", True, "成功获取预测详情")
                    return True
                else:
                    self.log_test("获取预测详情", False, f"API返回错误: {data.get('message')}")
                    return False
            else:
                error_text = response.text[:200]
                self.log_test("获取预测详情", False, f"HTTP {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("获取预测详情", False, f"异常: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 60)
        print("[START] AI Prediction Management API Test")
        print("=" * 60)
        print(f"[URL] {self.base_url}")
        print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 运行测试
        await self.test_batch_create_predictions()
        await asyncio.sleep(1)  # 等待预测任务创建
        
        await self.test_get_prediction_history()
        await asyncio.sleep(0.5)
        
        await self.test_get_prediction_list()
        await asyncio.sleep(0.5)
        
        await self.test_get_prediction_detail()
        
        # 输出测试总结
        print("\n" + "=" * 60)
        print("[SUMMARY] Test Summary")
        print("=" * 60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        
        print(f"   Total: {total}")
        print(f"   [PASS] {passed}")
        print(f"   [FAIL] {failed}")
        print(f"   Pass Rate: {passed/total*100:.1f}%")
        print()
        
        if failed > 0:
            print("[FAILED TESTS]:")
            for r in self.test_results:
                if not r['success']:
                    print(f"   - {r['name']}: {r['message']}")
            print()
        
        print("=" * 60)
        
        return failed == 0


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试AI预测管理API')
    parser.add_argument(
        '--url',
        default='http://localhost:8001',
        help='API基础URL (默认: http://localhost:8001)'
    )
    
    args = parser.parse_args()
    
    async with PredictionAPITester(base_url=args.url) as tester:
        success = await tester.run_all_tests()
        return 0 if success else 1


if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test execution exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

