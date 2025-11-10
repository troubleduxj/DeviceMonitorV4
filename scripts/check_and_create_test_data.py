#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库状态并创建测试数据
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncpg
from app.settings.config import Settings

settings = Settings()


async def main():
    """主函数"""
    print("=" * 70)
    print("  Check Database and Create Test Data")
    print("=" * 70)
    print()
    
    pg_creds = settings.tortoise_orm.connections.postgres.credentials
    
    conn = await asyncpg.connect(
        host=pg_creds.host,
        port=pg_creds.port,
        database=pg_creds.database,
        user=pg_creds.user,
        password=pg_creds.password
    )
    
    print("[SUCCESS] Database connected")
    print()
    
    # 1. 检查现有预测
    print("[1/3] Checking existing predictions...")
    
    stats = await conn.fetch("""
        SELECT status, COUNT(*) as count
        FROM t_ai_predictions
        GROUP BY status
        ORDER BY status;
    """)
    
    print("   Current status:")
    for row in stats:
        print(f"      {row['status']}: {row['count']}")
    
    total = sum(row['count'] for row in stats)
    print(f"   Total: {total}")
    print()
    
    # 2. 为所有预测生成Mock数据
    print("[2/3] Generating mock data for all predictions...")
    
    all_predictions = await conn.fetch("""
        SELECT id, prediction_name, data_filters, prediction_horizon, status
        FROM t_ai_predictions
        ORDER BY id;
    """)
    
    updated = 0
    
    for row in all_predictions:
        pred_id = row['id']
        data_filters = row['data_filters']
        horizon = row['prediction_horizon']
        current_status = row['status']
        
        # 解析JSON（asyncpg返回的可能是字符串）
        if isinstance(data_filters, str):
            import json
            data_filters = json.loads(data_filters)
        
        device_code = data_filters.get('device_code', 'UNKNOWN')
        metric_name = data_filters.get('metric_name', 'unknown')
        
        # 生成预测点
        base_value = random.uniform(75, 95)
        trend_value = random.uniform(-0.2, 0.2)
        
        predictions = []
        for hour in range(horizon):
            time_point = datetime.now() + timedelta(hours=hour+1)
            value = base_value + hour * trend_value + random.gauss(0, 1.5)
            
            predictions.append({
                "time": time_point.isoformat(),
                "value": round(value, 2),
                "confidence": round(random.uniform(0.85, 0.95), 2),
                "lower_bound": round(value - 3.5, 2),
                "upper_bound": round(value + 3.5, 2)
            })
        
        result_data = {
            "predictions": predictions,
            "metadata": {
                "device_code": device_code,
                "device_name": data_filters.get('device_name', f"设备{device_code}"),
                "metric_name": metric_name,
                "prediction_method": "ARIMA",
                "total_points": horizon,
                "avg_confidence": round(sum(p['confidence'] for p in predictions) / horizon, 2),
                "data_period_start": (datetime.now() - timedelta(days=7)).isoformat(),
                "data_period_end": datetime.now().isoformat()
            },
            "actual_values": []
        }
        
        # 更新记录
        await conn.execute("""
            UPDATE t_ai_predictions
            SET 
                result_data = $1::jsonb,
                status = 'completed',
                progress = 100,
                accuracy_score = $2,
                completed_at = NOW(),
                updated_at = NOW()
            WHERE id = $3
        """, json.dumps(result_data), round(random.uniform(0.85, 0.95), 2), pred_id)
        
        updated += 1
        print(f"   [{updated}/{len(all_predictions)}] {device_code} - {metric_name}")
    
    print()
    print(f"[SUCCESS] Updated {updated} predictions")
    print()
    
    # 3. 验证结果
    print("[3/3] Verifying results...")
    
    final_stats = await conn.fetch("""
        SELECT status, COUNT(*) as count
        FROM t_ai_predictions
        GROUP BY status;
    """)
    
    print("   Final status:")
    for row in final_stats:
        print(f"      {row['status']}: {row['count']}")
    
    # 测试查询性能
    import time
    start = time.time()
    result = await conn.fetchval("""
        SELECT COUNT(*) FROM t_ai_predictions
        WHERE data_filters->>'device_code' = 'WLD-001';
    """)
    elapsed = (time.time() - start) * 1000
    
    print(f"\n[PERFORMANCE] JSONB query: {elapsed:.2f}ms for {result} records")
    
    await conn.close()
    
    print()
    print("=" * 70)
    print("[COMPLETE] Test data ready!")
    print("=" * 70)
    print()
    print("[NEXT]:")
    print("   1. Test API: http://localhost:8001/docs")
    print("   2. Try: GET /api/v2/ai-monitor/predictions/history?device_code=WLD-001")
    print("   3. Frontend: cd web && npm run dev")
    print()
    
    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

