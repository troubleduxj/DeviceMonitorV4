#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立的Mock数据生成脚本
为已创建的预测任务填充完整的预测结果数据
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncpg
from app.settings.config import Settings

settings = Settings()


async def generate_mock_result_data(device_code, metric_name, horizon=24):
    """生成Mock预测结果数据"""
    
    # 生成基础值和趋势
    base_value = random.uniform(75, 95)
    trend_types = ['increasing', 'decreasing', 'stable']
    trend = random.choice(trend_types)
    
    if trend == 'increasing':
        trend_value = random.uniform(0.1, 0.3)
    elif trend == 'decreasing':
        trend_value = random.uniform(-0.3, -0.1)
    else:
        trend_value = random.uniform(-0.05, 0.05)
    
    # 生成24小时预测点
    predictions = []
    for hour in range(horizon):
        time_point = datetime.now() + timedelta(hours=hour+1)
        value = base_value + hour * trend_value + random.gauss(0, 1.5)
        confidence = random.uniform(0.85, 0.95)
        
        predictions.append({
            "time": time_point.isoformat(),
            "value": round(value, 2),
            "confidence": round(confidence, 2),
            "lower_bound": round(value - 3.5, 2),
            "upper_bound": round(value + 3.5, 2)
        })
    
    # 构建完整结构
    avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
    
    result_data = {
        "predictions": predictions,
        "metadata": {
            "device_code": device_code,
            "device_name": f"设备{device_code}",
            "metric_name": metric_name,
            "prediction_method": "ARIMA",
            "total_points": horizon,
            "avg_confidence": round(avg_confidence, 2),
            "data_period_start": (datetime.now() - timedelta(days=7)).isoformat(),
            "data_period_end": datetime.now().isoformat()
        },
        "actual_values": []
    }
    
    return result_data, round(random.uniform(0.85, 0.95), 2)


async def main():
    """主函数"""
    print("=" * 70)
    print("  Generate Mock Prediction Data")
    print("=" * 70)
    print()
    
    # 从Settings获取数据库连接信息
    pg_creds = settings.tortoise_orm.connections.postgres.credentials
    
    print(f"[CONNECT] {pg_creds.host}:{pg_creds.port}/{pg_creds.database}")
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host=pg_creds.host,
            port=pg_creds.port,
            database=pg_creds.database,
            user=pg_creds.user,
            password=pg_creds.password
        )
        
        print("[SUCCESS] Database connected")
        print()
        
        # 查找所有pending状态的预测任务
        rows = await conn.fetch("""
            SELECT id, prediction_name, data_filters, prediction_horizon
            FROM t_ai_predictions
            WHERE status = 'pending'
            ORDER BY id;
        """)
        
        print(f"[INFO] Found {len(rows)} pending predictions")
        print()
        
        if not rows:
            print("[WARNING] No pending predictions found")
            print("[TIP] Run batch create API first")
            return 0
        
        # 为每个预测生成Mock数据
        updated_count = 0
        
        for row in rows:
            pred_id = row['id']
            pred_name = row['prediction_name']
            data_filters = row['data_filters']
            horizon = row['prediction_horizon']
            
            device_code = data_filters.get('device_code', 'UNKNOWN')
            metric_name = data_filters.get('metric_name', 'unknown')
            
            # 生成Mock数据
            result_data, accuracy = await generate_mock_result_data(
                device_code,
                metric_name,
                horizon
            )
            
            # 更新数据库
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
            """, str(result_data).replace("'", '"'), accuracy, pred_id)
            
            updated_count += 1
            print(f"   [{updated_count}/{len(rows)}] Updated: {pred_name}")
            print(f"       Device: {device_code}, Metric: {metric_name}, Points: {horizon}")
        
        print()
        print(f"[SUCCESS] Updated {updated_count} predictions with mock data")
        print()
        
        # 验证结果
        completed = await conn.fetchval("""
            SELECT COUNT(*) FROM t_ai_predictions WHERE status = 'completed';
        """)
        
        print(f"[VERIFY] Total completed predictions: {completed}")
        
        await conn.close()
        
        print()
        print("=" * 70)
        print("[COMPLETE] Mock data generation successful!")
        print("=" * 70)
        print()
        print("[NEXT STEPS]:")
        print("   1. Test API: http://localhost:8001/docs")
        print("   2. Query: GET /api/v2/ai-monitor/predictions/history?device_code=WLD-001")
        print("   3. Start frontend: cd web && npm run dev")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

