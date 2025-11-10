#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL按钮权限初始化脚本（简化版）
使用psycopg2直接执行SQL
使用方法：python scripts/init_button_permissions_simple.py
"""

import os
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ 错误: 未安装 psycopg2")
    print("请运行: pip install psycopg2-binary")
    exit(1)


# 数据库连接配置（请根据实际情况修改）
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'device_monitor',
    'user': 'postgres',
    'password': '123456'
}


def read_sql_file():
    """读取SQL文件"""
    sql_file = Path(__file__).parent.parent / 'database' / 'button_permissions_init_postgresql.sql'
    
    if not sql_file.exists():
        print(f"❌ SQL文件不存在: {sql_file}")
        return None
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        return f.read()


def execute_sql():
    """执行SQL初始化"""
    print("=" * 60)
    print("开始初始化按钮权限 (PostgreSQL)")
    print("=" * 60)
    print()
    
    # 读取SQL文件
    sql_content = read_sql_file()
    if not sql_content:
        return False
    
    try:
        # 连接数据库
        print(f"[*] 连接数据库: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False  # 使用事务
        
        cur = conn.cursor()
        
        # 执行SQL
        print("[*] 正在执行SQL脚本...")
        print()
        cur.execute(sql_content)
        
        # 提交事务
        conn.commit()
        
        # 查询结果（最后两个SELECT语句的结果）
        print("\n[*] 统计信息:")
        print("-" * 60)
        
        # 查询按钮权限总数
        cur.execute("""
            SELECT 
                COUNT(*) as button_count,
                COUNT(DISTINCT parent_id) as menu_count
            FROM t_sys_menu 
            WHERE menu_type = 'button'
        """)
        result = cur.fetchone()
        print(f"  按钮权限总数: {result[0]}")
        print(f"  涉及菜单数: {result[1]}")
        
        # 查询各菜单的按钮权限
        print("\n[*] 各菜单下的按钮权限:")
        print("-" * 60)
        cur.execute("""
            SELECT 
                pm.name as parent_menu,
                m.name as button_name,
                m.perms as permission
            FROM t_sys_menu m
            LEFT JOIN t_sys_menu pm ON m.parent_id = pm.id
            WHERE m.menu_type = 'button'
            ORDER BY pm.name, m.order_num
        """)
        
        current_menu = None
        for row in cur.fetchall():
            parent_menu, button_name, permission = row
            if parent_menu != current_menu:
                current_menu = parent_menu
                print(f"\n  [{parent_menu}]")
            print(f"    - {button_name} ({permission})")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("[OK] 按钮权限初始化完成！")
        print("=" * 60)
        print()
        print("请刷新浏览器页面，然后查看：")
        print("  系统管理 -> 角色管理 -> 分配权限 -> 菜单权限")
        print()
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n[ERROR] 数据库错误: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"\n[ERROR] 执行失败: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


def main():
    """主函数"""
    success = execute_sql()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

