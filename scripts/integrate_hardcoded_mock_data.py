#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合页面硬编码数据到Mock规则
从AI监测页面提取硬编码数据，插入到Mock管理系统
"""

import asyncio
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncpg
from app.settings.config import Settings

settings = Settings()


# 从页面提取的硬编码数据
MOCK_RULES = [
    # 1. 设备风险评估数据（趋势预测页面）
    {
        "name": "AI预测-设备风险评估列表",
        "description": "设备风险评估数据（整合自trend-prediction/index.vue的riskData）",
        "method": "GET",
        "url_pattern": "/api/v2/ai-monitor/risk-assessment",
        "response_code": 200,
        "delay": 300,
        "response_data": {
            "success": True,
            "code": 200,
            "message": "获取风险评估数据成功",
            "data": {
                "items": [
                    {
                        "deviceId": "WLD-001",
                        "deviceName": "焊接设备01",
                        "deviceType": "焊接设备",
                        "riskLevel": "high",
                        "riskLevelName": "高风险",
                        "failureProbability": 85.2,
                        "predictionRange": "7-14天",
                        "lastMaintenance": "2024-01-01",
                        "nextMaintenance": "2024-01-20",
                        "riskFactors": [
                            {"name": "温度异常", "impact": 85},
                            {"name": "振动增强", "impact": 72},
                            {"name": "使用时长", "impact": 68}
                        ],
                        "maintenanceAdvice": "建议立即检查冷却系统和振动传感器，安排紧急维护。"
                    },
                    {
                        "deviceId": "WLD-002",
                        "deviceName": "焊接设备02",
                        "deviceType": "焊接设备",
                        "riskLevel": "medium",
                        "riskLevelName": "中风险",
                        "failureProbability": 65.8,
                        "predictionRange": "15-30天",
                        "lastMaintenance": "2024-01-05",
                        "nextMaintenance": "2024-01-25",
                        "riskFactors": [
                            {"name": "压力波动", "impact": 58},
                            {"name": "电流不稳", "impact": 45},
                            {"name": "运行时间", "impact": 42}
                        ],
                        "maintenanceAdvice": "建议在下次计划维护时重点检查压力系统和电气连接。"
                    },
                    {
                        "deviceId": "WLD-003",
                        "deviceName": "焊接设备03",
                        "deviceType": "焊接设备",
                        "riskLevel": "low",
                        "riskLevelName": "低风险",
                        "failureProbability": 25.3,
                        "predictionRange": "30-60天",
                        "lastMaintenance": "2024-01-10",
                        "nextMaintenance": "2024-02-10",
                        "riskFactors": [
                            {"name": "正常磨损", "impact": 25},
                            {"name": "环境因素", "impact": 18},
                            {"name": "使用频率", "impact": 15}
                        ],
                        "maintenanceAdvice": "设备状态良好，按计划进行常规维护即可。"
                    }
                ]
            }
        }
    },
    
    # 2. 健康趋势数据（直接返回数组格式，不包装在data中）
    {
        "name": "AI预测-健康趋势数据",
        "description": "设备健康趋势数据（整合自页面healthTrendData）",
        "method": "GET",
        "url_pattern": "/api/v2/ai-monitor/health-trend",
        "response_code": 200,
        "delay": 200,
        "response_data": {
            "success": True,
            "code": 200,
            "message": "获取健康趋势成功",
            "data": [
                {"time": "2024-01-01", "healthy": 85, "warning": 12, "error": 3},
                {"time": "2024-01-02", "healthy": 83, "warning": 14, "error": 3},
                {"time": "2024-01-03", "healthy": 82, "warning": 15, "error": 3},
                {"time": "2024-01-04", "healthy": 80, "warning": 16, "error": 4},
                {"time": "2024-01-05", "healthy": 78, "warning": 17, "error": 5},
                {"time": "2024-01-06", "healthy": 76, "warning": 18, "error": 6},
                {"time": "2024-01-07", "healthy": 75, "warning": 19, "error": 6}
            ]
        }
    },
    
    # 3. 预测报告数据
    {
        "name": "AI预测-预测分析报告",
        "description": "预测分析报告数据（整合自页面reportData）",
        "method": "GET",
        "url_pattern": "/api/v2/ai-monitor/prediction-report",
        "response_code": 200,
        "delay": 400,
        "response_data": {
            "success": True,
            "code": 200,
            "message": "获取预测报告成功",
            "data": {
                "generatedAt": "2025-11-05T10:00:00Z",
                "summary": {
                    "totalDevices": 156,
                    "highRiskDevices": 12,
                    "mediumRiskDevices": 28,
                    "lowRiskDevices": 116,
                    "averageRiskScore": 35.2
                },
                "recommendations": [
                    "建议对12台高风险设备进行紧急检查",
                    "优化预测模型参数以提高准确率",
                    "增加温度和振动传感器的监控频率"
                ]
            }
        }
    },
    
    # 4. 设备健康列表（健康评分页面）
    {
        "name": "AI健康评分-设备健康列表",
        "description": "设备健康评分列表（整合自health-scoring/index.vue的deviceList）",
        "method": "GET",
        "url_pattern": "/api/v2/ai/health-scoring/devices",
        "response_code": 200,
        "delay": 300,
        "response_data": {
            "success": True,
            "code": 200,
            "message": "获取设备健康列表成功",
            "data": {
                "items": [
                    {
                        "id": 1,
                        "name": "生产线A-设备001",
                        "type": "注塑机",
                        "location": "车间A-01",
                        "healthScore": 92,
                        "healthLevel": "healthy",
                        "lastUpdate": "2024-01-15 14:30:25",
                        "factors": {
                            "temperature": {"score": 95, "status": "normal", "value": "65°C"},
                            "vibration": {"score": 88, "status": "normal", "value": "2.1mm/s"},
                            "pressure": {"score": 94, "status": "normal", "value": "8.5MPa"},
                            "efficiency": {"score": 91, "status": "normal", "value": "91%"}
                        },
                        "trend": "stable",
                        "riskLevel": "low",
                        "nextMaintenance": "2024-02-15",
                        "operatingHours": 1250
                    },
                    {
                        "id": 2,
                        "name": "生产线B-设备002",
                        "type": "冲压机",
                        "location": "车间B-02",
                        "healthScore": 76,
                        "healthLevel": "warning",
                        "lastUpdate": "2024-01-15 14:28:15",
                        "factors": {
                            "temperature": {"score": 82, "status": "warning", "value": "78°C"},
                            "vibration": {"score": 75, "status": "warning", "value": "3.8mm/s"},
                            "pressure": {"score": 88, "status": "normal", "value": "7.2MPa"},
                            "efficiency": {"score": 69, "status": "warning", "value": "69%"}
                        },
                        "trend": "declining",
                        "riskLevel": "medium",
                        "nextMaintenance": "2024-01-25",
                        "operatingHours": 2100
                    },
                    {
                        "id": 3,
                        "name": "生产线C-设备003",
                        "type": "焊接机",
                        "location": "车间C-03",
                        "healthScore": 45,
                        "healthLevel": "error",
                        "lastUpdate": "2024-01-15 14:25:40",
                        "factors": {
                            "temperature": {"score": 35, "status": "error", "value": "95°C"},
                            "vibration": {"score": 42, "status": "error", "value": "5.2mm/s"},
                            "pressure": {"score": 58, "status": "warning", "value": "6.8MPa"},
                            "efficiency": {"score": 45, "status": "error", "value": "45%"}
                        },
                        "trend": "declining",
                        "riskLevel": "high",
                        "nextMaintenance": "立即维护",
                        "operatingHours": 3200
                    }
                ],
                "total": 3
            }
        }
    },
    
    # 5. 评分分布数据
    {
        "name": "AI健康评分-评分分布统计",
        "description": "健康评分分布统计（整合自页面scoreDistributionData）",
        "method": "GET",
        "url_pattern": "/api/v2/ai/health-scoring/distribution",
        "response_code": 200,
        "delay": 200,
        "response_data": {
            "success": True,
            "code": 200,
            "message": "获取评分分布成功",
            "data": [
                {"range": "90-100", "count": 15, "percentage": 25},
                {"range": "80-89", "count": 20, "percentage": 33.3},
                {"range": "70-79", "count": 15, "percentage": 25},
                {"range": "60-69", "count": 7, "percentage": 11.7},
                {"range": "0-59", "count": 3, "percentage": 5}
            ]
        }
    },
    
    # 6. 健康评分概览统计
    {
        "name": "AI健康评分-概览统计",
        "description": "健康评分概览统计（整合自页面overviewStats）",
        "method": "GET",
        "url_pattern": "/api/v2/ai/health-scoring/overview",
        "response_code": 200,
        "delay": 200,
        "response_data": {
            "success": True,
            "code": 200,
            "message": "获取概览统计成功",
            "data": {
                "averageScore": 78.5,
                "healthyDevices": 45,
                "warningDevices": 12,
                "errorDevices": 3
            }
        }
    }
]


async def insert_mock_rules():
    """插入Mock规则"""
    
    print("=" * 70)
    print("  Integrate Hardcoded Data to Mock Rules")
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
    
    print(f"[CONNECT] Database connected")
    print()
    
    # 删除旧的AI相关Mock规则
    print("[CLEAN] Removing old AI mock rules...")
    await conn.execute("""
        DELETE FROM t_sys_mock_data 
        WHERE url_pattern LIKE '%/ai-monitor/%'
           OR url_pattern LIKE '%/ai/trend-prediction%'
           OR url_pattern LIKE '%/ai/health-scoring%'
           OR url_pattern LIKE '%/ai/anomaly%';
    """)
    print("[SUCCESS] Old rules removed")
    print()
    
    # 插入新的Mock规则
    print(f"[INSERT] Inserting {len(MOCK_RULES)} mock rules...")
    print("-" * 70)
    
    inserted = 0
    for rule in MOCK_RULES:
        try:
            await conn.execute("""
                INSERT INTO t_sys_mock_data (
                    name, description, method, url_pattern, 
                    response_data, response_code, delay, 
                    enabled, priority, creator_id, creator_name, 
                    created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5::jsonb, $6, $7, $8, $9, $10, $11, NOW(), NOW()
                )
            """, 
                rule['name'],
                rule['description'],
                rule['method'],
                rule['url_pattern'],
                json.dumps(rule['response_data']),
                rule['response_code'],
                rule['delay'],
                True,  # enabled
                100,   # priority
                1,     # creator_id
                'admin'  # creator_name
            )
            
            inserted += 1
            print(f"   [{inserted}/{len(MOCK_RULES)}] {rule['method']:6} {rule['url_pattern']}")
            print(f"       {rule['name']}")
            
        except Exception as e:
            print(f"   [ERROR] Failed to insert {rule['name']}: {e}")
    
    print()
    print(f"[SUCCESS] Inserted {inserted} mock rules")
    print()
    
    # 验证
    print("[VERIFY] Checking results...")
    print("-" * 70)
    
    rows = await conn.fetch("""
        SELECT 
            id, name, method, url_pattern, enabled,
            LENGTH(response_data::text) as data_size
        FROM t_sys_mock_data
        WHERE url_pattern LIKE '%ai%'
        ORDER BY priority DESC, id;
    """)
    
    print(f"[INFO] Total AI mock rules in database: {len(rows)}")
    for row in rows:
        status = "[ON]" if row['enabled'] else "[OFF]"
        print(f"   {status} {row['method']:6} {row['url_pattern']}")
        print(f"       {row['name']} (data: {row['data_size']} bytes)")
    
    await conn.close()
    
    print()
    print("=" * 70)
    print("[COMPLETE] Integration successful!")
    print("=" * 70)
    print()
    print("[NEXT STEPS]:")
    print("   1. Check Mock Management page - should see new rules")
    print("   2. Enable mock in browser console:")
    print("      window.__mockInterceptor.enable()")
    print("      await window.__mockInterceptor.reload()")
    print("   3. Refresh AI Monitor pages")
    print("   4. Data will come from Mock Management system")
    print()
    
    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(insert_mock_rules())
    sys.exit(exit_code)

