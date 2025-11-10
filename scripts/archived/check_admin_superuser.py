#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 admin 用户的超级管理员状态
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

def check_admin():
    print("=" * 80)
    print("  检查 admin 用户状态")
    print("=" * 80)
    print()
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 查询admin用户信息
        cur.execute("""
            SELECT id, username, is_superuser, is_active
            FROM t_sys_user 
            WHERE username = 'admin'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ 错误: 找不到 admin 用户！")
            cur.close()
            conn.close()
            return
        
        user_id, username, is_superuser, is_active = result
        
        print(f"用户信息:")
        print(f"  ID: {user_id}")
        print(f"  用户名: {username}")
        print(f"  超级管理员 (is_superuser): {is_superuser}")
        print(f"  激活状态 (is_active): {is_active}")
        print()
        
        if not is_superuser:
            print("❌ 问题: admin 用户的 is_superuser 字段为 False!")
            print()
            print("修复方法:")
            print("  UPDATE t_sys_user SET is_superuser = true WHERE username = 'admin';")
            print()
            
            # 询问是否修复
            print("正在修复...")
            cur.execute("UPDATE t_sys_user SET is_superuser = true WHERE username = 'admin'")
            conn.commit()
            print("✅ 已设置 admin 为超级管理员！")
        else:
            print("✅ admin 用户已经是超级管理员")
        
        if not is_active:
            print("⚠️  警告: admin 用户未激活 (is_active=False)")
            print("   正在激活...")
            cur.execute("UPDATE t_sys_user SET is_active = true WHERE username = 'admin'")
            conn.commit()
            print("✅ 已激活 admin 用户！")
        
        print()
        print("=" * 80)
        print("  后端API获取菜单逻辑:")
        print("=" * 80)
        print()
        print("  if user.is_superuser:")
        print("      # 超级管理员获取所有菜单")
        print("      all_menus = await Menu.all().order_by('order_num', 'id')")
        print("  else:")
        print("      # 普通用户通过角色获取菜单")
        print()
        print("现在 admin 应该可以看到所有菜单了！")
        print()
        print("请:")
        print("  1. 退出登录")
        print("  2. 清除浏览器缓存 (Ctrl+Shift+Delete)")
        print("  3. 重新登录 admin")
        print("  4. 查看左侧菜单")
        print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_admin()

