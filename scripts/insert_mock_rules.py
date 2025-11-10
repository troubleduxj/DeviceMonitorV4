#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock规则批量插入工具
插入系统核心API的Mock模拟数据到数据库
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
    print("Mock规则批量插入工具")
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
    
    print("[说明] 本脚本将插入以下类型的Mock规则:\n")
    print("  ✓ 认证相关: 登录、用户信息")
    print("  ✓ 用户管理: 用户列表、用户详情")
    print("  ✓ 菜单管理: 菜单列表、菜单树")
    print("  ✓ 角色管理: 角色列表、角色详情")
    print("  ✓ 设备管理: 设备列表、设备统计")
    print("  ✓ 系统参数: 参数配置")
    print("  ✓ 错误场景: 超时、权限、服务器错误")
    print("  ✓ 特殊场景: 加载中、空数据")
    print("\n[注意] 所有规则默认为禁用状态，使用前需要在页面上启用\n")
    
    confirm = input("确认执行插入操作? (Y/N): ")
    if confirm.upper() != 'Y':
        print("\n操作已取消")
        sys.exit(0)
    
    print("\n" + "=" * 80)
    print("[1/3] 连接数据库...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    print("✓ 连接成功\n")
    
    print("[2/3] 读取SQL文件...")
    sql_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'database', 'migrations', 'insert_mock_rules.sql'
    )
    
    if not os.path.exists(sql_file):
        print(f"\n❌ 错误: SQL文件不存在: {sql_file}")
        sys.exit(1)
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"✓ SQL文件读取成功: {sql_file}\n")
    
    print("[3/3] 执行SQL...")
    cursor.execute(sql_content)
    conn.commit()
    print("✓ SQL执行成功\n")
    
    # 查询插入结果
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN enabled = true THEN 1 ELSE 0 END) as enabled_count,
            SUM(CASE WHEN enabled = false THEN 1 ELSE 0 END) as disabled_count
        FROM t_sys_mock_data
    """)
    
    result = cursor.fetchone()
    total, enabled_count, disabled_count = result
    
    print("=" * 80)
    print("✅ Mock规则插入成功！")
    print("=" * 80)
    print("\n📊 统计信息:")
    print(f"  • 总规则数: {total}条")
    print(f"  • 已启用: {enabled_count}条")
    print(f"  • 已禁用: {disabled_count}条")
    
    print("\n📋 已插入的Mock规则类型:")
    print("  • 认证相关: 3条规则")
    print("  • 用户管理: 1条规则")
    print("  • 菜单管理: 2条规则")
    print("  • 角色管理: 1条规则")
    print("  • 设备管理: 2条规则")
    print("  • 系统参数: 1条规则")
    print("  • 错误场景: 3条规则")
    print("  • 特殊场景: 2条规则")
    
    print("\n🚀 下一步操作:")
    print("  1. 刷新浏览器 (Ctrl + Shift + R)")
    print("  2. 访问: 高级设置 → Mock数据管理")
    print("  3. 查看已插入的Mock规则")
    print("  4. 启用需要测试的规则")
    print("  5. 启用Mock全局开关")
    
    print("\n💡 使用提示:")
    print("  • 所有规则默认为禁用状态")
    print("  • 在Mock管理页面启用对应规则")
    print("  • 点击'测试'按钮可预览规则效果")
    print("  • 使用'命中次数'查看规则使用情况")
    print("  • 测试完成后记得禁用Mock功能")
    print()
    
    cursor.close()
    conn.close()
    
except ImportError:
    print("\n❌ 错误: psycopg2未安装")
    print("\n请在虚拟环境中运行此脚本:")
    print("  1. 激活虚拟环境: venv\\Scripts\\activate.bat")
    print("  2. 确保psycopg2已安装")
    sys.exit(1)
    
except psycopg2.OperationalError as e:
    print(f"\n❌ 数据库连接失败: {e}")
    print("\n请检查:")
    print("  1. PostgreSQL服务是否启动")
    print("  2. 数据库配置是否正确")
    print("  3. 用户权限是否足够")
    print(f"  4. 密码是否正确: {DB_PASSWORD}")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
    sys.exit(1)

