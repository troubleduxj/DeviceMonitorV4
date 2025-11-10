#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新添加的3个API接口
"""

import asyncio
import httpx


async def test_new_apis():
    """测试新API"""
    
    print("=" * 70)
    print("  Testing New API Endpoints")
    print("=" * 70)
    print()
    
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Test 1: 风险评估
        print("[TEST 1] GET /api/v2/ai-monitor/prediction-analytics/risk-assessment")
        try:
            response = await client.get(f"{base_url}/api/v2/ai-monitor/prediction-analytics/risk-assessment")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', {}).get('items', [])
                print(f"   [PASS] Found {len(items)} risk assessments")
                if items:
                    print(f"      Sample: {items[0].get('deviceName')} - {items[0].get('riskLevelName')}")
            else:
                print(f"   [FAIL] {response.text[:200]}")
        except Exception as e:
            print(f"   [ERROR] {e}")
        print()
        
        # Test 2: 健康趋势
        print("[TEST 2] GET /api/v2/ai-monitor/prediction-analytics/health-trend")
        try:
            response = await client.get(f"{base_url}/api/v2/ai-monitor/prediction-analytics/health-trend?days=7")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                trend_data = data.get('data', [])
                print(f"   [PASS] Got {len(trend_data)} days of trend data")
                if trend_data:
                    first = trend_data[0]
                    print(f"      Sample: {first.get('time')} - Healthy:{first.get('healthy')}, Warning:{first.get('warning')}")
            else:
                print(f"   [FAIL] {response.text[:200]}")
        except Exception as e:
            print(f"   [ERROR] {e}")
        print()
        
        # Test 3: 预测报告
        print("[TEST 3] GET /api/v2/ai-monitor/prediction-analytics/prediction-report")
        try:
            response = await client.get(f"{base_url}/api/v2/ai-monitor/prediction-analytics/prediction-report")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                report = data.get('data', {})
                summary = report.get('summary', {})
                print(f"   [PASS] Got prediction report")
                print(f"      Total devices: {summary.get('totalDevices')}")
                print(f"      High risk: {summary.get('highRiskDevices')}")
            else:
                print(f"   [FAIL] {response.text[:200]}")
        except Exception as e:
            print(f"   [ERROR] {e}")
        print()
    
    print("=" * 70)
    print("[COMPLETE] New API tests finished")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(test_new_apis())

