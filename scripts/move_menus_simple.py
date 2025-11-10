#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单版本：将主题管理和组件管理移动到高级设置
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用项目配置
try:
    from app.settings.config import settings
    
    DB_HOST = settings.DATABASE_HOST
    DB_PORT = settings.DATABASE_PORT  
    DB_NAME = settings.DATABASE_NAME
    DB_USER = settings.DATABASE_USER
    DB_PASSWORD = settings.DATABASE_PASSWORD
    
    print("=" * 80)
    print("菜单移动工具 - 从项目配置读取数据库连接")
    print("=" * 80)
    print(f"数据库: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"用户: {DB_USER}")
    print()
    
except Exception as e:
    print(f"无法导入项目配置: {e}")
    print("使用默认配置...")
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'device_monitor'
    DB_USER = 'postgres'
    DB_PASSWORD = 'Hanatech@123'

try:
    import psycopg2
    
    print("[1/4] 连接数据库...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    print("✓ 连接成功\n")
    
    print("[2/4] 查询当前菜单...")
    cursor.execute("""
        SELECT id, name, parent_id 
        FROM t_sys_menu 
        WHERE name IN ('高级设置', '主题管理', '组件管理', 'Mock数据管理')
    """)
    
    menus = {}
    for row in cursor.fetchall():
        menus[row[1]] = {'id': row[0], 'parent_id': row[2]}
        print(f"  - {row[1]}: ID={row[0]}, 父ID={row[2]}")
    
    if '高级设置' not in menus:
        print("\n❌ 错误: 未找到'高级设置'菜单")
        sys.exit(1)
    
    advanced_id = menus['高级设置']['id']
    print(f"\n✓ 高级设置ID: {advanced_id}\n")
    
    print("[3/4] 更新菜单...")
    
    # 更新主题管理
    if '主题管理' in menus:
        cursor.execute("""
            UPDATE t_sys_menu 
            SET parent_id = %s, sort = 200
            WHERE id = %s
        """, (advanced_id, menus['主题管理']['id']))
        print(f"  ✓ 主题管理 -> 高级设置 (sort=200)")
    
    # 更新组件管理
    if '组件管理' in menus:
        cursor.execute("""
            UPDATE t_sys_menu 
            SET parent_id = %s, sort = 300
            WHERE id = %s
        """, (advanced_id, menus['组件管理']['id']))
        print(f"  ✓ 组件管理 -> 高级设置 (sort=300)")
    
    # 更新Mock数据管理排序
    if 'Mock数据管理' in menus:
        cursor.execute("""
            UPDATE t_sys_menu 
            SET sort = 100
            WHERE id = %s
        """, (menus['Mock数据管理']['id'],))
        print(f"  ✓ Mock数据管理排序更新 (sort=100)")
    
    print("\n[4/4] 提交更改...")
    conn.commit()
    print("✓ 完成\n")
    
    # 验证
    cursor.execute("""
        SELECT name, sort 
        FROM t_sys_menu 
        WHERE parent_id = %s
        ORDER BY sort
    """, (advanced_id,))
    
    print("=" * 80)
    print("高级设置的子菜单:")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"  - {row[0]} (排序: {row[1]})")
    
    print("\n" + "=" * 80)
    print("✅ 菜单移动成功！")
    print("=" * 80)
    print("\n请刷新浏览器查看效果 (Ctrl + Shift + R)")
    
    cursor.close()
    conn.close()
    
except ImportError:
    print("\n❌ 错误: psycopg2未安装")
    print("\n请在虚拟环境中运行此脚本:")
    print("  1. 激活虚拟环境")
    print("  2. 确保psycopg2已安装")
    sys.exit(1)
    
except psycopg2.OperationalError as e:
    print(f"\n❌ 数据库连接失败: {e}")
    print("\n请检查:")
    print("  1. PostgreSQL服务是否启动")
    print("  2. 数据库配置是否正确")
    print("  3. 用户权限是否足够")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
    sys.exit(1)

