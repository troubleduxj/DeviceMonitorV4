#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
import os

# 修复Windows控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.settings.config import settings
    DB_HOST = settings.DATABASE_HOST
    DB_PORT = settings.DATABASE_PORT  
    DB_NAME = settings.DATABASE_NAME
    DB_USER = settings.DATABASE_USER
    DB_PASSWORD = settings.DATABASE_PASSWORD
except:
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'device_monitor'
    DB_USER = 'postgres'
    DB_PASSWORD = '123456'

try:
    import psycopg2
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("Mock数据检查")
    print("=" * 80)
    
    # 检查表是否存在
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 't_sys_mock_data'
        )
    """)
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        print("\n❌ 错误: t_sys_mock_data 表不存在")
        print("\n解决方案:")
        print("  1. 执行建表SQL: database/migrations/add_mock_data_table.sql")
        print("  2. 或运行: scripts/install_mock_db.py")
        sys.exit(1)
    
    print("\n✓ Mock数据表存在")
    
    # 检查数据数量
    cursor.execute('SELECT COUNT(*) FROM t_sys_mock_data')
    count = cursor.fetchone()[0]
    
    print(f"\n数据库中Mock规则数量: {count}条")
    
    if count == 0:
        print("\n⚠️ 警告: 数据库中没有Mock规则")
        print("\n解决方案:")
        print("  1. 运行: scripts/insert_mock_rules.bat")
        print("  2. 或运行: python scripts/insert_mock_rules.py")
        print("  3. 或手动执行: database/migrations/insert_mock_rules.sql")
    else:
        print("\n✓ 数据库中有Mock规则")
        
        # 显示前5条规则
        cursor.execute("""
            SELECT id, name, url_pattern, method, enabled 
            FROM t_sys_mock_data 
            ORDER BY id 
            LIMIT 5
        """)
        
        print("\n前5条Mock规则:")
        print("-" * 80)
        print(f"{'ID':<5} {'名称':<25} {'URL':<30} {'方法':<8} {'启用':<5}")
        print("-" * 80)
        
        for row in cursor.fetchall():
            mock_id, name, url, method, enabled = row
            status = '✓' if enabled else '✗'
            print(f"{mock_id:<5} {name:<25} {url:<30} {method:<8} {status:<5}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    
except ImportError:
    print("\n❌ 错误: psycopg2未安装")
    print("请在虚拟环境中运行此脚本")
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

