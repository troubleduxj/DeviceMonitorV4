"""
测试数据库连接
"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import psycopg2
except ImportError:
    print("正在安装 psycopg2...")
    import os
    os.system("pip install psycopg2-binary")
    import psycopg2

# 尝试两个可能的密码
passwords = ['Hanatech@123', '123456']

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'device_monitor',
    'user': 'postgres'
}

print("=" * 60)
print("   数据库连接测试")
print("=" * 60)
print()
print(f"主机: {DB_CONFIG['host']}")
print(f"端口: {DB_CONFIG['port']}")
print(f"数据库: {DB_CONFIG['database']}")
print(f"用户: {DB_CONFIG['user']}")
print()

for pwd in passwords:
    print(f"尝试密码: {pwd}")
    try:
        conn = psycopg2.connect(**DB_CONFIG, password=pwd)
        print("[OK] 连接成功！")
        print()
        
        # 检查数据库版本
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"PostgreSQL版本: {version[:50]}...")
        print()
        
        # 检查表是否已存在
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('t_sys_mock_data', 't_sys_menu')
        """)
        tables = cursor.fetchall()
        print(f"已存在的表: {[t[0] for t in tables]}")
        print()
        
        cursor.close()
        conn.close()
        
        print("[SUCCESS] 数据库配置正确!")
        print(f"正确的密码是: {pwd}")
        print()
        break
        
    except Exception as e:
        print(f"[ERROR] 连接失败: {str(e)[:100]}")
        print()
        continue
else:
    print("[ERROR] 所有密码都无法连接")
    print()
    print("可能的原因:")
    print("1. PostgreSQL服务未启动")
    print("2. 数据库 'device_monitor' 不存在")
    print("3. 密码不是 'Hanatech@123' 也不是 '123456'")
    print("4. PostgreSQL未监听在 localhost:5432")

input("\n按回车键退出...")
