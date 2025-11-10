#!/usr/bin/env python3
"""测试统一前缀的API"""
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(timeout=10) as client:
        print("Testing Unified API Prefix...")
        print()
        
        # 测试任务管理API
        try:
            r = await client.get('http://localhost:8001/api/v2/ai/predictions/tasks')
            print(f"[TEST] GET /api/v2/ai/predictions/tasks")
            print(f"  Status: {r.status_code}")
            print(f"  Result: {'PASS' if r.status_code in [200,400] else 'FAIL'}")
        except Exception as e:
            print(f"  Error: {e}")
        
        print()
        print("Unified prefix is working!" if r.status_code in [200, 400] else "Check backend logs")

asyncio.run(test())

