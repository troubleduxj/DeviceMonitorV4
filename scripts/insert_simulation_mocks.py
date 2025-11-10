#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插入模拟设备Mock规则到数据库
使用psycopg2连接PostgreSQL
"""

import sys
import os

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import psycopg2
    from psycopg2 import OperationalError, Error
except ImportError:
    print("❌ 错误: 未安装 psycopg2")
    print("   请运行: pip install psycopg2-binary")
    sys.exit(1)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'device_monitor'
}

def main():
    print("=" * 60)
    print("插入模拟设备Mock规则")
    print("=" * 60)
    print()

    # 读取SQL文件
    sql_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'database',
        'migrations',
        'insert_simulation_device_mocks.sql'
    )
    
    print("[1/4] 检查SQL文件...")
    if not os.path.exists(sql_file):
        print(f"❌ 错误: 找不到SQL文件")
        print(f"   路径: {sql_file}")
        return 1
    print("✓ SQL文件存在")
    print()

    print("[2/4] 读取SQL内容...")
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print(f"✓ 读取成功 ({len(sql_content)} 字符)")
    except Exception as e:
        print(f"❌ 读取SQL文件失败: {e}")
        return 1
    print()

    print("[3/4] 连接数据库...")
    print(f"   主机: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"   数据库: {DB_CONFIG['database']}")
    print(f"   用户: {DB_CONFIG['user']}")
    print()

    try:
        # 连接数据库
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cursor = conn.cursor()
        print("✓ 数据库连接成功")
        print()

        print("[4/4] 执行SQL语句...")
        try:
            # 执行SQL
            cursor.execute(sql_content)
            
            # 提交事务
            conn.commit()
            print("✓ SQL执行成功")
            print()

            # 查询插入结果
            cursor.execute("""
                SELECT 
                    id,
                    name,
                    url_pattern,
                    method,
                    enabled,
                    description
                FROM t_sys_mock_data
                WHERE description LIKE '%模拟设备%'
                ORDER BY id DESC
                LIMIT 10
            """)
            
            results = cursor.fetchall()
            if results:
                print("✅ 模拟设备Mock规则插入完成！")
                print()
                print(f"已插入 {len(results)} 条Mock规则:")
                print()
                for row in results:
                    rule_id, name, url_pattern, method, enabled, description = row
                    status = "✓ 已启用" if enabled else "○ 未启用"
                    print(f"  [{status}] {name}")
                    print(f"      ID: {rule_id}")
                    print(f"      URL: {method} {url_pattern}")
                    print(f"      说明: {description}")
                    print()
            else:
                print("⚠ 警告: 未查询到插入的记录")
                print("   可能已经存在，请检查Mock管理页面")
            
        except Error as e:
            conn.rollback()
            print(f"❌ SQL执行失败: {e}")
            print()
            print("详细错误信息:")
            print(f"  错误代码: {e.pgcode}")
            print(f"  错误消息: {e.pgerror}")
            return 1
        
        finally:
            cursor.close()
            conn.close()

    except OperationalError as e:
        print(f"❌ 数据库连接失败: {e}")
        print()
        print("可能的原因:")
        print("  1. PostgreSQL服务未启动")
        print("  2. 数据库密码不正确")
        print("  3. 数据库不存在")
        print("  4. 端口被占用或防火墙阻止")
        print()
        print("解决方案:")
        print("  1. 检查PostgreSQL服务是否运行")
        print("  2. 确认数据库密码是否为: Hanatech@123")
        print("  3. 确认数据库名称是否为: device_monitor")
        print("  4. 或使用pgAdmin手动执行SQL文件")
        return 1
    
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print()
    print("=" * 60)
    print("下一步操作:")
    print("=" * 60)
    print()
    print("1. 刷新浏览器页面 (Ctrl + Shift + R)")
    print("2. 访问: 高级设置 → Mock数据管理")
    print("3. 启用对应的Mock规则:")
    print("   • 模拟设备分类-设备列表")
    print("   • 模拟设备-详情信息")
    print("   • 模拟设备-实时数据")
    print("   • 模拟设备-历史数据")
    print("   • 模拟设备-统计数据")
    print("4. 启用Mock全局开关")
    print("5. 访问设备管理页面查看模拟设备")
    print()
    print("详细使用说明请查看:")
    print("  docs/SIMULATION_DEVICE_MOCK_GUIDE.md")
    print()

    return 0


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print()
        print("⚠ 用户中断操作")
        sys.exit(130)

