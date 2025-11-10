"""
Mock功能数据库安装脚本 - Python版本
自动执行SQL文件，无需psql命令
"""

import sys
import os
import io

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 尝试导入psycopg2
try:
    import psycopg2
    from psycopg2 import OperationalError
except ImportError:
    print("[ERROR] 未安装 psycopg2 模块")
    print("正在尝试安装...")
    os.system("pip install psycopg2-binary")
    try:
        import psycopg2
        from psycopg2 import OperationalError
        print("[OK] psycopg2 安装成功")
    except:
        print("[ERROR] psycopg2 安装失败")
        print("请手动运行: pip install psycopg2-binary")
        input("按回车键退出...")
        sys.exit(1)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'device_monitor',
    'user': 'postgres',
    'password': 'Hanatech@123'
}

def execute_sql_file(conn, sql_file_path):
    """执行SQL文件"""
    print(f"正在执行: {os.path.basename(sql_file_path)}")
    print("-" * 60)
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        
        print(f"[OK] {os.path.basename(sql_file_path)} 执行成功")
        return True
        
    except Exception as e:
        print(f"[ERROR] 执行失败: {str(e)}")
        conn.rollback()
        return False

def main():
    print("=" * 60)
    print("   Mock功能数据库安装脚本")
    print("=" * 60)
    print()
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    migrations_dir = os.path.join(project_dir, 'database', 'migrations')
    
    # SQL文件路径
    sql_files = [
        os.path.join(migrations_dir, 'add_mock_data_table.sql'),
        os.path.join(migrations_dir, 'add_mock_management_menu.sql')
    ]
    
    # 检查文件是否存在
    for sql_file in sql_files:
        if not os.path.exists(sql_file):
            print(f"[ERROR] 文件不存在: {sql_file}")
            input("按回车键退出...")
            sys.exit(1)
    
    print("[步骤1] 连接数据库...")
    print(f"  主机: {DB_CONFIG['host']}")
    print(f"  端口: {DB_CONFIG['port']}")
    print(f"  数据库: {DB_CONFIG['database']}")
    print(f"  用户: {DB_CONFIG['user']}")
    print()
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("[OK] 数据库连接成功")
        print()
        
    except OperationalError as e:
        print(f"[ERROR] 数据库连接失败")
        print(f"错误详情: {str(e)}")
        print()
        print("可能的原因:")
        print("1. PostgreSQL服务未启动")
        print("2. 数据库名称不正确 (当前: device_monitor)")
        print("3. 用户名或密码不正确")
        print("4. 端口被占用或防火墙阻止")
        print()
        print("请检查:")
        print("- PostgreSQL服务是否运行")
        print("- 数据库 'device_monitor' 是否存在")
        print("- 用户 'postgres' 密码是否为 'Hanatech@123'")
        print()
        input("按回车键退出...")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 未知错误: {str(e)}")
        input("按回车键退出...")
        sys.exit(1)
    
    # 执行SQL文件
    success_count = 0
    
    print("[步骤2] 执行SQL脚本...")
    print()
    
    for i, sql_file in enumerate(sql_files, 1):
        print(f"[{i}/{len(sql_files)}] {os.path.basename(sql_file)}")
        if execute_sql_file(conn, sql_file):
            success_count += 1
        print()
    
    conn.close()
    
    # 结果汇总
    print("=" * 60)
    if success_count == len(sql_files):
        print("   [SUCCESS] 数据库安装完成！")
        print("=" * 60)
        print()
        print("[OK] 成功执行:", success_count, "个SQL文件")
        print()
        print("下一步操作:")
        print("1. 启动后端服务 (运行 start_backend.bat)")
        print("2. 登录系统 (http://localhost:3000)")
        print("3. 初始化权限 (运行 init_mock_permissions.html)")
        print()
    else:
        print("   [WARNING] 安装未完全成功")
        print("=" * 60)
        print()
        print(f"成功: {success_count}/{len(sql_files)}")
        print(f"失败: {len(sql_files) - success_count}/{len(sql_files)}")
        print()
    
    input("按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] 用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)

