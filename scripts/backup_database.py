#!/usr/bin/env python3
"""
数据库备份脚本
在执行清理操作前创建安全备份
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.cleanup import DatabaseCleaner
from tortoise import Tortoise
from app.settings.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_database_backup(backup_type: str = "full", backup_dir: str = None):
    """创建数据库备份"""
    try:
        # 初始化Tortoise ORM
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        # 创建清理器（用于备份功能）
        if backup_dir:
            cleaner = DatabaseCleaner(backup_dir=backup_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cleaner = DatabaseCleaner(backup_dir=f"backup/manual_backup_{timestamp}")
        
        logger.info(f"开始创建{backup_type}备份...")
        
        if backup_type == "full":
            # 创建完整备份
            backup_file = await cleaner.create_full_backup()
            print(f"✅ 完整数据库备份已创建: {backup_file}")
            
        elif backup_type == "tables":
            # 创建所有表的备份
            from database.audit import DatabaseAuditor
            auditor = DatabaseAuditor()
            tables = await auditor.get_all_tables()
            
            backup_files = []
            for table in tables:
                try:
                    backup_file = await cleaner.create_table_backup(table)
                    backup_files.append(backup_file)
                    logger.info(f"表 {table} 备份完成")
                except Exception as e:
                    logger.error(f"备份表 {table} 失败: {e}")
            
            print(f"✅ 表备份已创建: {len(backup_files)} 个文件")
            print(f"备份目录: {cleaner.backup_dir}")
        
        # 保存备份日志
        log_file = cleaner.save_cleanup_log()
        print(f"📄 备份日志: {log_file}")
        
        return str(cleaner.backup_dir)
        
    except Exception as e:
        logger.error(f"创建数据库备份时出错: {e}")
        raise
    finally:
        await Tortoise.close_connections()


async def restore_from_backup(backup_file: str):
    """从备份恢复数据库"""
    try:
        # 初始化Tortoise ORM
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_file}")
        
        logger.info(f"开始从备份恢复数据库: {backup_file}")
        
        # 获取数据库连接信息
        db_config = settings.tortoise_orm.connections.postgres.credentials
        
        # 使用psql恢复数据库
        restore_command = [
            "psql",
            f"--host={db_config.host}",
            f"--port={db_config.port}",
            f"--username={db_config.user}",
            f"--dbname={db_config.database}",
            "--no-password",
            f"--file={backup_file}"
        ]
        
        # 设置密码环境变量
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config.password
        
        import subprocess
        result = subprocess.run(restore_command, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 数据库恢复成功")
            logger.info(f"数据库从 {backup_file} 恢复成功")
        else:
            print(f"❌ 数据库恢复失败: {result.stderr}")
            logger.error(f"数据库恢复失败: {result.stderr}")
            raise Exception(f"恢复失败: {result.stderr}")
        
    except Exception as e:
        logger.error(f"恢复数据库时出错: {e}")
        raise
    finally:
        await Tortoise.close_connections()


def list_backups(backup_root: str = "backup"):
    """列出可用的备份"""
    backup_path = Path(backup_root)
    
    if not backup_path.exists():
        print(f"备份目录不存在: {backup_root}")
        return
    
    print(f"📁 备份目录: {backup_path.absolute()}")
    print(f"")
    
    # 查找备份目录
    backup_dirs = [d for d in backup_path.iterdir() if d.is_dir()]
    backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not backup_dirs:
        print("没有找到备份目录")
        return
    
    print(f"可用备份:")
    for i, backup_dir in enumerate(backup_dirs, 1):
        # 获取目录信息
        create_time = datetime.fromtimestamp(backup_dir.stat().st_mtime)
        
        # 统计备份文件
        sql_files = list(backup_dir.glob("*.sql"))
        json_files = list(backup_dir.glob("*.json"))
        
        print(f"{i:2d}. {backup_dir.name}")
        print(f"    创建时间: {create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    SQL文件: {len(sql_files)} 个")
        print(f"    日志文件: {len(json_files)} 个")
        print(f"    路径: {backup_dir}")
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据库备份工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 备份命令
    backup_parser = subparsers.add_parser("backup", help="创建数据库备份")
    backup_parser.add_argument(
        "--type", 
        choices=["full", "tables"], 
        default="full",
        help="备份类型: full=完整备份, tables=按表备份"
    )
    backup_parser.add_argument(
        "--dir", 
        help="备份目录"
    )
    
    # 恢复命令
    restore_parser = subparsers.add_parser("restore", help="从备份恢复数据库")
    restore_parser.add_argument(
        "backup_file", 
        help="备份文件路径"
    )
    
    # 列表命令
    list_parser = subparsers.add_parser("list", help="列出可用备份")
    list_parser.add_argument(
        "--dir", 
        default="backup",
        help="备份根目录"
    )
    
    args = parser.parse_args()
    
    if args.command == "backup":
        asyncio.run(create_database_backup(
            backup_type=args.type,
            backup_dir=args.dir
        ))
    elif args.command == "restore":
        asyncio.run(restore_from_backup(args.backup_file))
    elif args.command == "list":
        list_backups(args.dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()