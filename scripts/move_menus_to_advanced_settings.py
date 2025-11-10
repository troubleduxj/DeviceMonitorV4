#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将主题管理和组件管理从系统设置移动到高级设置
"""

import sys
import io
import psycopg2

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'device_monitor',
    'user': 'postgres',
    'password': 'Hanatech@123'
}

def main():
    conn = None
    cursor = None
    
    try:
        print("=" * 80)
        print("菜单移动工具 - 将主题管理和组件管理移动到高级设置")
        print("=" * 80)
        
        # 连接数据库
        print("\n[1/4] 连接数据库...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✓ 数据库连接成功")
        
        # 查询当前菜单结构
        print("\n[2/4] 查询当前菜单结构...")
        cursor.execute("""
            SELECT id, name, parent_id, component, path, sort, icon
            FROM t_sys_menu 
            WHERE name IN ('系统设置', '高级设置', '主题管理', '组件管理', 'Mock数据管理')
            ORDER BY sort
        """)
        
        menus = cursor.fetchall()
        print(f"✓ 找到 {len(menus)} 个相关菜单\n")
        
        print("当前菜单结构:")
        print("-" * 100)
        print(f"{'ID':<5} {'名称':<15} {'父ID':<8} {'组件路径':<40} {'排序':<5}")
        print("-" * 100)
        
        menu_map = {}
        for row in menus:
            menu_id, name, parent_id, component, path, sort, icon = row
            menu_map[name] = menu_id
            print(f"{menu_id:<5} {name:<15} {parent_id or 'NULL':<8} {component or '':<40} {sort:<5}")
        
        # 检查必要的菜单是否存在
        if '高级设置' not in menu_map:
            print("\n❌ 错误：未找到'高级设置'菜单")
            return False
        
        if '主题管理' not in menu_map:
            print("\n⚠️ 警告：未找到'主题管理'菜单")
        
        if '组件管理' not in menu_map:
            print("\n⚠️ 警告：未找到'组件管理'菜单")
        
        advanced_settings_id = menu_map['高级设置']
        print(f"\n✓ 高级设置菜单ID: {advanced_settings_id}")
        
        # 更新菜单的parent_id
        print("\n[3/4] 更新菜单父级关系...")
        
        updates = []
        
        if '主题管理' in menu_map:
            theme_id = menu_map['主题管理']
            cursor.execute("""
                UPDATE t_sys_menu 
                SET parent_id = %s, sort = 200
                WHERE id = %s
            """, (advanced_settings_id, theme_id))
            updates.append(f"  - 主题管理 (ID: {theme_id}) -> 高级设置")
        
        if '组件管理' in menu_map:
            component_id = menu_map['组件管理']
            cursor.execute("""
                UPDATE t_sys_menu 
                SET parent_id = %s, sort = 300
                WHERE id = %s
            """, (advanced_settings_id, component_id))
            updates.append(f"  - 组件管理 (ID: {component_id}) -> 高级设置")
        
        # Mock数据管理的排序
        if 'Mock数据管理' in menu_map:
            mock_id = menu_map['Mock数据管理']
            cursor.execute("""
                UPDATE t_sys_menu 
                SET sort = 100
                WHERE id = %s
            """, (mock_id,))
            updates.append(f"  - Mock数据管理 (ID: {mock_id}) 排序更新为 100")
        
        if updates:
            print("✓ 已更新以下菜单:")
            for update in updates:
                print(update)
        else:
            print("⚠️ 没有需要更新的菜单")
        
        # 提交更改
        print("\n[4/4] 提交更改...")
        conn.commit()
        print("✓ 更改已提交")
        
        # 查询更新后的结构
        print("\n" + "=" * 100)
        print("更新后的菜单结构:")
        print("-" * 100)
        
        cursor.execute("""
            SELECT m.id, m.name, m.parent_id, p.name as parent_name, m.sort
            FROM t_sys_menu m
            LEFT JOIN t_sys_menu p ON m.parent_id = p.id
            WHERE m.name IN ('高级设置', '主题管理', '组件管理', 'Mock数据管理')
               OR m.id = %s
            ORDER BY m.parent_id NULLS FIRST, m.sort
        """, (advanced_settings_id,))
        
        result_menus = cursor.fetchall()
        print(f"{'ID':<5} {'名称':<20} {'父ID':<8} {'父菜单名称':<15} {'排序':<5}")
        print("-" * 100)
        for row in result_menus:
            menu_id, name, parent_id, parent_name, sort = row
            print(f"{menu_id:<5} {name:<20} {parent_id or 'NULL':<8} {parent_name or '-':<15} {sort:<5}")
        
        print("\n" + "=" * 100)
        print("✅ 菜单移动完成！")
        print("=" * 100)
        print("\n提示:")
        print("  1. 请刷新浏览器页面（Ctrl + Shift + R）")
        print("  2. 在左侧菜单中查看'高级设置'菜单")
        print("  3. 应该可以看到3个子菜单: Mock数据管理、主题管理、组件管理")
        print()
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ 数据库错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        if conn:
            conn.rollback()
        return False
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("\n数据库连接已关闭")

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

