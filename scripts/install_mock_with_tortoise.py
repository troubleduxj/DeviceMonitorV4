"""
使用Tortoise ORM安装Mock功能
使用后端相同的数据库配置
"""

import sys
import os
import asyncio

# 添加项目根目录到Python路径
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# 导入后端配置
from app.settings.config import get_tortoise_orm_config, PostgresCredentials

async def execute_sql_file(sql_file_path):
    """执行SQL文件"""
    print(f"\n正在执行: {os.path.basename(sql_file_path)}")
    print("-" * 60)
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 使用asyncpg执行原始SQL
        from tortoise import Tortoise
        conn = Tortoise.get_connection("default")
        
        await conn.execute_script(sql_content)
        
        print(f"[OK] {os.path.basename(sql_file_path)} 执行成功")
        return True
        
    except Exception as e:
        print(f"[ERROR] 执行失败: {str(e)}")
        return False

async def main():
    print("=" * 60)
    print("   Mock功能数据库安装 (使用Tortoise ORM)")
    print("=" * 60)
    print()
    
    # 获取Tortoise ORM配置
    tortoise_config = get_tortoise_orm_config()
    print("[步骤1] 使用后端配置连接数据库...")
    print()
    
    try:
        from tortoise import Tortoise
        await Tortoise.init(config=tortoise_config)
        print("[OK] 数据库连接成功")
        print()
        
    except Exception as e:
        print(f"[ERROR] 数据库连接失败: {str(e)}")
        print()
        print("请确保:")
        print("1. PostgreSQL服务正在运行")
        print("2. 数据库配置正确")
        print("3. 后端能正常启动")
        print()
        return
    
    # SQL文件路径
    migrations_dir = os.path.join(project_dir, 'database', 'migrations')
    sql_files = [
        os.path.join(migrations_dir, 'add_mock_data_table.sql'),
        os.path.join(migrations_dir, 'add_mock_management_menu.sql')
    ]
    
    # 检查文件
    for sql_file in sql_files:
        if not os.path.exists(sql_file):
            print(f"[ERROR] 文件不存在: {sql_file}")
            await Tortoise.close_connections()
            return
    
    # 执行SQL文件
    print("[步骤2] 执行SQL脚本...")
    success_count = 0
    
    for i, sql_file in enumerate(sql_files, 1):
        print(f"\n[{i}/{len(sql_files)}]", end=" ")
        if await execute_sql_file(sql_file):
            success_count += 1
    
    await Tortoise.close_connections()
    
    # 结果
    print("\n" + "=" * 60)
    if success_count == len(sql_files):
        print("   [SUCCESS] 数据库安装完成！")
        print("=" * 60)
        print(f"\n[OK] 成功执行 {success_count} 个SQL文件")
        print()
        print("下一步:")
        print("1. 重启后端服务")
        print("2. 登录系统")
        print("3. 初始化权限")
    else:
        print("   [WARNING] 安装未完全成功")
        print("=" * 60)
        print(f"\n成功: {success_count}/{len(sql_files)}")
        print(f"失败: {len(sql_files) - success_count}/{len(sql_files)}")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断")
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

