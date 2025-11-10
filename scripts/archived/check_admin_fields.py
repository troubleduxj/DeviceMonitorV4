#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 admin 用户字段
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
    print("  检查 t_sys_user 表结构和 admin 用户")
    print("=" * 80)
    print()
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. 查看表结构
        print("1. 查看 t_sys_user 表的字段:")
        print("-" * 80)
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 't_sys_user' 
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        
        print("字段列表:")
        for col_name, col_type in columns:
            print(f"  - {col_name:20s} ({col_type})")
        
        print()
        
        # 2. 查询admin用户的所有字段
        print("2. 查询 admin 用户的信息:")
        print("-" * 80)
        cur.execute("SELECT * FROM t_sys_user WHERE username = 'admin'")
        
        if cur.description:
            col_names = [desc[0] for desc in cur.description]
            result = cur.fetchone()
            
            if result:
                print()
                for col_name, col_value in zip(col_names, result):
                    # 隐藏密码
                    if 'password' in col_name.lower():
                        col_value = '***'
                    print(f"  {col_name:20s} = {col_value}")
                
                # 检查关键字段
                print()
                print("3. 关键字段检查:")
                print("-" * 80)
                
                # 查找可能的超级管理员标志字段
                superuser_fields = [name for name in col_names if 'super' in name.lower() or 'admin' in name.lower()]
                if superuser_fields:
                    print(f"✓ 找到可能的超级管理员字段: {', '.join(superuser_fields)}")
                    
                    for field in superuser_fields:
                        idx = col_names.index(field)
                        value = result[idx]
                        print(f"  {field} = {value}")
                else:
                    print("⚠️  未找到明确的超级管理员字段")
                    print("   可能通过角色判断权限")
            else:
                print("❌ 找不到 admin 用户！")
        
        print()
        
        # 3. 查看后端如何判断超级管理员
        print("4. 后端获取菜单的逻辑:")
        print("-" * 80)
        print()
        print("根据代码 app/api/v2/auth.py:")
        print()
        print("  if user_obj.is_superuser:")
        print("      # 超级管理员获取所有菜单")
        print("      all_menus = await Menu.all()")
        print("  else:")
        print("      # 普通用户通过角色获取菜单")
        print("      roles = await user_obj.roles.all()")
        print()
        
        print("User 模型的 is_superuser 可能是:")
        print("  1. 数据库字段 (如: is_superuser, is_admin, admin_flag)")
        print("  2. 模型属性/方法 (@property)")
        print("  3. 通过角色判断")
        print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_admin()

