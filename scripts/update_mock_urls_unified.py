#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新Mock规则URL为统一前缀
将所有 /ai-monitor/ 改为 /ai/
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncpg
from app.settings.config import Settings

settings = Settings()


async def main():
    """主函数"""
    print("=" * 70)
    print("  Update Mock Rules to Unified Prefix (/ai/)")
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
    
    print("[CONNECT] Database connected")
    print()
    
    # 查看需要更新的规则
    print("[CHECK] Finding AI mock rules to update...")
    
    rules = await conn.fetch("""
        SELECT id, name, url_pattern
        FROM t_sys_mock_data
        WHERE url_pattern LIKE '%/ai-monitor/%'
           OR url_pattern LIKE '%/ai/trend-prediction%'
           OR url_pattern LIKE '%/ai/health-scoring%'
        ORDER BY id;
    """)
    
    print(f"[INFO] Found {len(rules)} rules to update:")
    for rule in rules:
        print(f"   [{rule['id']}] {rule['name']}")
        print(f"       {rule['url_pattern']}")
    print()
    
    if not rules:
        print("[INFO] No rules need updating")
        await conn.close()
        return 0
    
    # 更新URL
    print("[UPDATE] Updating URL patterns...")
    print("-" * 70)
    
    updates = [
        # 预测相关
        ('/api/v2/ai-monitor/predictions/', '/api/v2/ai/predictions/tasks/'),
        ('/api/v2/ai-monitor/prediction-analytics/', '/api/v2/ai/predictions/analytics/'),
        
        # 趋势预测
        ('/api/v2/ai/trend-prediction/', '/api/v2/ai/predictions/execute/'),
        
        # 健康评分
        ('/api/v2/ai/health-scoring/', '/api/v2/ai/health-scores/calculate/'),
        ('/api/v2/ai-monitor/health-scores/', '/api/v2/ai/health-scores/records/'),
    ]
    
    total_updated = 0
    
    for old_prefix, new_prefix in updates:
        result = await conn.execute("""
            UPDATE t_sys_mock_data
            SET url_pattern = REPLACE(url_pattern, $1, $2),
                updated_at = NOW()
            WHERE url_pattern LIKE $3
        """, old_prefix, new_prefix, f'{old_prefix}%')
        
        count = int(result.split()[-1])
        if count > 0:
            print(f"   [UPDATED] {old_prefix} -> {new_prefix}")
            print(f"             {count} rules updated")
            total_updated += count
    
    print()
    print(f"[SUCCESS] Total updated: {total_updated} rules")
    print()
    
    # 验证更新结果
    print("[VERIFY] Checking updated rules...")
    print("-" * 70)
    
    updated_rules = await conn.fetch("""
        SELECT id, name, url_pattern
        FROM t_sys_mock_data
        WHERE url_pattern LIKE '%/ai/predictions/%'
           OR url_pattern LIKE '%/ai/health-scores/%'
        ORDER BY id;
    """)
    
    print(f"[INFO] Found {len(updated_rules)} AI rules with unified prefix:")
    for rule in updated_rules:
        print(f"   [{rule['id']}] {rule['url_pattern']}")
        print(f"       {rule['name']}")
    
    await conn.close()
    
    print()
    print("=" * 70)
    print("[COMPLETE] Mock URLs updated to unified prefix!")
    print("=" * 70)
    print()
    print("[NEXT]:")
    print("   1. Restart backend: python run.py")
    print("   2. Enable mock: window.__mockInterceptor.reload()")
    print("   3. Test API docs: http://localhost:8001/docs")
    print()
    
    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

