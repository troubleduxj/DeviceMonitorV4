#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试查询API
"""

import asyncio
import httpx
import json


async def test_apis():
    """测试所有查询API"""
    
    print("=" * 70)
    print("  Testing Query APIs")
    print("=" * 70)
    print()
    
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Test 1: 获取预测列表
        print("[TEST 1] GET /api/v2/ai-monitor/predictions")
        try:
            response = await client.get(
                f"{base_url}/api/v2/ai-monitor/predictions",
                params={"page": 1, "page_size": 10}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                total = data.get('data', {}).get('total', 0)
                print(f"   [PASS] Found {total} predictions")
            else:
                print(f"   [FAIL] {response.text[:200]}")
        except Exception as e:
            print(f"   [ERROR] {e}")
        print()
        
        # Test 2: 查询设备历史
        print("[TEST 2] GET /api/v2/ai-monitor/predictions/history")
        try:
            response = await client.get(
                f"{base_url}/api/v2/ai-monitor/predictions/history",
                params={
                    "device_code": "WLD-001",
                    "page": 1,
                    "page_size": 20
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                total = data.get('data', {}).get('total', 0)
                items = data.get('data', {}).get('items', [])
                print(f"   [PASS] Found {total} records for WLD-001")
                if items:
                    first = items[0]
                    print(f"   Sample: {first.get('prediction_name')}")
                    print(f"      Device: {first.get('device_code')}")
                    print(f"      Metric: {first.get('metric_name')}")
                    print(f"      Status: {first.get('status')}")
                    print(f"      Accuracy: {first.get('accuracy_score')}")
            else:
                print(f"   [FAIL] {response.text[:200]}")
        except Exception as e:
            print(f"   [ERROR] {e}")
        print()
        
        # Test 3: 获取预测详情
        print("[TEST 3] GET /api/v2/ai-monitor/predictions/1")
        try:
            response = await client.get(f"{base_url}/api/v2/ai-monitor/predictions/1")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                pred = data.get('data', {})
                print(f"   [PASS] Got prediction details")
                print(f"      Name: {pred.get('prediction_name')}")
                print(f"      Device: {pred.get('device_code')}")
                print(f"      Status: {pred.get('status')}")
                print(f"      Progress: {pred.get('progress')}%")
                if pred.get('result_data'):
                    metadata = pred['result_data'].get('metadata', {})
                    print(f"      Points: {metadata.get('total_points')}")
                    print(f"      Confidence: {metadata.get('avg_confidence')}")
            else:
                print(f"   [FAIL] {response.text[:200]}")
        except Exception as e:
            print(f"   [ERROR] {e}")
        print()
    
    print("=" * 70)
    print("[COMPLETE] Query API tests finished")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(test_apis())

