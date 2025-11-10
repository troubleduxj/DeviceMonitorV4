#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 admin 用户分配管理员角色
"""

import sys
import psycopg2

# Windows编码支持
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

def fix_admin_role():
    print("=" * 60)
    print("  为 admin 用户分配管理员角色")
    print("=" * 60)
    print()
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor()
        
        # 读取并执行SQL
        with open('fix_admin_role.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cur.execute(sql_content)
        conn.commit()
        
        print("✅ 角色分配成功！")
        print()
        print("现在请:")
        print("1. 退出登录")
        print("2. 重新登录 admin 用户")
        print("3. 查看左侧菜单，应该可以看到'数据模型管理'")
        print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_admin_role()

