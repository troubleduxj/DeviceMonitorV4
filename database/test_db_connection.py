#!/usr/bin/env python3
"""
测试数据库连接
"""

import asyncio
import os
import sys

# 设置数据库连接
os.environ['DATABASE_URL'] = 'postgresql://postgres:Hanatech%40123@127.0.0.1:5432/devicemonitor'

async def test_connection():
    """测试数据库连接"""
    try:
        import asyncpg
        
        db_url = os.environ['DATABASE_URL']
        print(f"🔗 连接到: {db_url.split('@')[1]}")
        
        conn = await asyncpg.connect(db_url)
        
        # 测试基本查询
        version = await conn.fetchval("SELECT version()")
        print(f"✅ 连接成功!")
        print(f"📊 PostgreSQL版本: {version.split(',')[0]}")
        
        # 检查现有表
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        print(f"\n📋 现有表 ({len(tables)} 个):")
        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['table_name']}")
            print(f"   - {table['table_name']}: {count} 条记录")
        
        await conn.close()
        return True
        
    except ImportError:
        print("❌ 缺少 asyncpg 依赖")
        print("请运行: pip install asyncpg")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("\n🎉 数据库连接测试成功！可以执行迁移了。")
        print("运行: python run_migration_now.py")
    else:
        print("\n❌ 数据库连接测试失败，请检查配置。")
    sys.exit(0 if success else 1)