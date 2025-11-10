#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
菜单问题诊断脚本
"""

import sys
import psycopg2
from psycopg2 import sql

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

def diagnose():
    print("=" * 80)
    print("  菜单问题诊断")
    print("=" * 80)
    print()
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. 检查菜单记录
        print("1. 检查数据模型菜单记录")
        print("-" * 80)
        cur.execute("""
            SELECT id, parent_id, name, path, visible, status, menu_type, order_num
            FROM t_sys_menu 
            WHERE path LIKE '/data-model%' 
            ORDER BY COALESCE(parent_id, id), order_num
        """)
        menus = cur.fetchall()
        
        if not menus:
            print("❌ 错误: 数据库中没有找到数据模型菜单！")
            print("请重新执行菜单创建脚本。")
            return
        
        print(f"✓ 找到 {len(menus)} 个菜单记录:\n")
        for menu in menus:
            menu_id, parent_id, name, path, visible, status, menu_type, order_num = menu
            indent = "  " if parent_id else ""
            print(f"{indent}ID:{menu_id:3d} | Parent:{parent_id or 'NULL':4} | {name:12s} | {path:25s} | Visible:{visible} | Status:{status} | Type:{menu_type}")
        
        # 检查问题
        print()
        has_issue = False
        for menu in menus:
            menu_id, parent_id, name, path, visible, status, menu_type, order_num = menu
            if not visible:
                print(f"⚠️  警告: 菜单 '{name}' (ID:{menu_id}) 的 visible=False")
                has_issue = True
            if not status:
                print(f"⚠️  警告: 菜单 '{name}' (ID:{menu_id}) 的 status=False")
                has_issue = True
        
        if not has_issue:
            print("✓ 所有菜单的 visible 和 status 都是 true")
        
        print()
        
        # 2. 检查权限分配
        print("2. 检查权限分配")
        print("-" * 80)
        cur.execute("""
            SELECT r.id, r.role_name, COUNT(rm.menu_id) as menu_count
            FROM t_sys_role r
            LEFT JOIN t_sys_role_menu rm ON r.id = rm.role_id
            LEFT JOIN t_sys_menu m ON rm.menu_id = m.id AND m.path LIKE '/data-model%'
            GROUP BY r.id, r.role_name
            HAVING COUNT(rm.menu_id) > 0 OR r.role_name LIKE '%管理员%'
        """)
        roles = cur.fetchall()
        
        if not roles:
            print("❌ 错误: 没有任何角色分配了数据模型菜单权限！")
        else:
            print(f"✓ 找到 {len(roles)} 个角色:\n")
            for role_id, role_name, menu_count in roles:
                print(f"  角色 ID:{role_id:3d} | {role_name:20s} | 菜单数: {menu_count}")
        
        print()
        
        # 3. 检查具体的角色-菜单关联
        print("3. 检查角色-菜单关联详情")
        print("-" * 80)
        cur.execute("""
            SELECT r.role_name, m.name, m.path
            FROM t_sys_role r
            JOIN t_sys_role_menu rm ON r.id = rm.role_id
            JOIN t_sys_menu m ON rm.menu_id = m.id
            WHERE m.path LIKE '/data-model%'
            ORDER BY r.id, m.order_num
        """)
        associations = cur.fetchall()
        
        if not associations:
            print("❌ 错误: 没有角色-菜单关联记录！")
            print("\n建议: 重新执行菜单脚本，或手动分配权限：")
            print("   系统管理 → 角色管理 → 选择角色 → 分配菜单权限")
        else:
            print(f"✓ 找到 {len(associations)} 条关联记录:\n")
            current_role = None
            for role_name, menu_name, menu_path in associations:
                if role_name != current_role:
                    print(f"\n  [{role_name}]")
                    current_role = role_name
                print(f"    - {menu_name:15s} ({menu_path})")
        
        print()
        
        # 4. 检查用户角色
        print("4. 检查用户角色分配 (前5个用户)")
        print("-" * 80)
        cur.execute("""
            SELECT u.id, u.username, STRING_AGG(r.role_name, ', ') as roles
            FROM t_sys_user u
            LEFT JOIN t_sys_user_role ur ON u.id = ur.user_id
            LEFT JOIN t_sys_role r ON ur.role_id = r.id
            GROUP BY u.id, u.username
            ORDER BY u.id
            LIMIT 5
        """)
        users = cur.fetchall()
        
        if not users:
            print("❌ 错误: 没有找到用户！")
        else:
            print()
            for user_id, username, roles in users:
                print(f"  用户 ID:{user_id:3d} | {username:20s} | 角色: {roles or '(无)'}")
        
        print()
        print("=" * 80)
        print("  诊断完成")
        print("=" * 80)
        
        # 5. 修复建议
        print("\n修复建议:")
        print("-" * 80)
        
        if not menus:
            print("1. ❌ 菜单不存在 → 重新执行: python database/migrations/device-data-model/execute_menu_migration.py")
        elif has_issue:
            print("1. ⚠️  菜单状态有问题 → 运行以下SQL修复:")
            print("   UPDATE t_sys_menu SET visible=true, status=true WHERE path LIKE '/data-model%';")
        else:
            print("1. ✅ 菜单状态正常")
        
        if not associations:
            print("2. ❌ 权限未分配 → 重新执行菜单脚本，或手动分配权限")
        else:
            print("2. ✅ 权限已分配")
        
        print("3. 🔄 清除前端缓存:")
        print("   - 强制刷新浏览器: Ctrl+F5")
        print("   - 清除浏览器缓存")
        print("   - 重新登录系统")
        
        print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose()

