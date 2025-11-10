#!/usr/bin/env python3
"""
数据库导出脚本
用于导出完整的数据库结构和数据，供项目部署使用
"""

import os
import sys
import subprocess
import datetime
import json
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.settings.config import get_database_config
except ImportError:
    print("❌ 无法导入数据库配置，请确保在项目根目录运行此脚本")
    sys.exit(1)

class DatabaseExporter:
    def __init__(self):
        self.config = get_database_config()
        self.export_dir = project_root / "deploy" / "database_export"
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def create_export_directory(self):
        """创建导出目录"""
        print("📁 创建导出目录...")
        
        if self.export_dir.exists():
            shutil.rmtree(self.export_dir)
        
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (self.export_dir / "structure").mkdir(exist_ok=True)
        (self.export_dir / "data").mkdir(exist_ok=True)
        (self.export_dir / "migrations").mkdir(exist_ok=True)
        (self.export_dir / "scripts").mkdir(exist_ok=True)
        
        print(f"✅ 导出目录已创建: {self.export_dir}")
    
    def export_database_structure(self):
        """导出数据库结构"""
        print("🏗️ 导出数据库结构...")
        
        structure_file = self.export_dir / "structure" / f"database_structure_{self.timestamp}.sql"
        
        # 构建mysqldump命令（仅结构）
        cmd = [
            "mysqldump",
            f"--host={self.config['host']}",
            f"--port={self.config['port']}",
            f"--user={self.config['username']}",
            f"--password={self.config['password']}",
            "--no-data",  # 仅结构，不包含数据
            "--routines",  # 包含存储过程和函数
            "--triggers",  # 包含触发器
            "--single-transaction",
            "--lock-tables=false",
            self.config['database']
        ]
        
        try:
            with open(structure_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
            if result.returncode == 0:
                print(f"✅ 数据库结构导出成功: {structure_file}")
                return True
            else:
                print(f"❌ 数据库结构导出失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 导出数据库结构时发生错误: {e}")
            return False
    
    def export_database_data(self):
        """导出数据库数据"""
        print("📊 导出数据库数据...")
        
        data_file = self.export_dir / "data" / f"database_data_{self.timestamp}.sql"
        
        # 构建mysqldump命令（仅数据）
        cmd = [
            "mysqldump",
            f"--host={self.config['host']}",
            f"--port={self.config['port']}",
            f"--user={self.config['username']}",
            f"--password={self.config['password']}",
            "--no-create-info",  # 仅数据，不包含结构
            "--single-transaction",
            "--lock-tables=false",
            "--complete-insert",  # 使用完整的INSERT语句
            self.config['database']
        ]
        
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
            if result.returncode == 0:
                print(f"✅ 数据库数据导出成功: {data_file}")
                return True
            else:
                print(f"❌ 数据库数据导出失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 导出数据库数据时发生错误: {e}")
            return False
    
    def export_complete_database(self):
        """导出完整数据库（结构+数据）"""
        print("💾 导出完整数据库...")
        
        complete_file = self.export_dir / f"complete_database_{self.timestamp}.sql"
        
        # 构建mysqldump命令（完整导出）
        cmd = [
            "mysqldump",
            f"--host={self.config['host']}",
            f"--port={self.config['port']}",
            f"--user={self.config['username']}",
            f"--password={self.config['password']}",
            "--routines",
            "--triggers",
            "--single-transaction",
            "--lock-tables=false",
            "--complete-insert",
            self.config['database']
        ]
        
        try:
            with open(complete_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
            if result.returncode == 0:
                print(f"✅ 完整数据库导出成功: {complete_file}")
                return True
            else:
                print(f"❌ 完整数据库导出失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 导出完整数据库时发生错误: {e}")
            return False
    
    def copy_migration_files(self):
        """复制迁移文件"""
        print("📋 复制数据库迁移文件...")
        
        migrations_source = project_root / "database" / "migrations"
        migrations_dest = self.export_dir / "migrations"
        
        if migrations_source.exists():
            try:
                shutil.copytree(migrations_source, migrations_dest, dirs_exist_ok=True)
                print(f"✅ 迁移文件复制成功: {migrations_dest}")
                return True
            except Exception as e:
                print(f"❌ 复制迁移文件失败: {e}")
                return False
        else:
            print("⚠️ 未找到迁移文件目录")
            return True
    
    def create_import_script(self):
        """创建数据库导入脚本"""
        print("📝 创建数据库导入脚本...")
        
        import_script = self.export_dir / "scripts" / "import_database.py"
        
        script_content = f'''#!/usr/bin/env python3
"""
数据库导入脚本
用于在新环境中导入数据库
"""

import os
import sys
import subprocess
import mysql.connector
from pathlib import Path

class DatabaseImporter:
    def __init__(self, host, port, username, password, database):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.script_dir = Path(__file__).parent.parent
        
    def create_database_if_not_exists(self):
        """创建数据库（如果不存在）"""
        print(f"🔧 检查并创建数据库: {{self.database}}")
        
        try:
            # 连接到MySQL服务器（不指定数据库）
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password
            )
            
            cursor = conn.cursor()
            
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{{self.database}}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            print(f"✅ 数据库 {{self.database}} 已准备就绪")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 创建数据库失败: {{e}}")
            return False
    
    def import_complete_database(self):
        """导入完整数据库"""
        print("📥 导入完整数据库...")
        
        # 查找最新的完整数据库文件
        db_files = list(self.script_dir.glob("complete_database_*.sql"))
        if not db_files:
            print("❌ 未找到数据库文件")
            return False
            
        latest_file = max(db_files, key=lambda x: x.stat().st_mtime)
        print(f"📁 使用数据库文件: {{latest_file}}")
        
        # 构建mysql导入命令
        cmd = [
            "mysql",
            f"--host={{self.host}}",
            f"--port={{self.port}}",
            f"--user={{self.username}}",
            f"--password={{self.password}}",
            self.database
        ]
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
                
            if result.returncode == 0:
                print("✅ 数据库导入成功")
                return True
            else:
                print(f"❌ 数据库导入失败: {{result.stderr}}")
                return False
                
        except Exception as e:
            print(f"❌ 导入数据库时发生错误: {{e}}")
            return False
    
    def run_migrations(self):
        """运行数据库迁移"""
        print("🔄 运行数据库迁移...")
        
        migrations_dir = self.script_dir / "migrations"
        if not migrations_dir.exists():
            print("⚠️ 未找到迁移文件目录")
            return True
            
        # 获取所有SQL迁移文件
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        if not migration_files:
            print("⚠️ 未找到迁移文件")
            return True
        
        try:
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database
            )
            
            cursor = conn.cursor()
            
            for migration_file in migration_files:
                print(f"📋 执行迁移: {{migration_file.name}}")
                
                with open(migration_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # 分割SQL语句并执行
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                for statement in statements:
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        print(f"⚠️ 迁移语句执行警告: {{e}}")
                        # 继续执行其他语句
                
                conn.commit()
            
            cursor.close()
            conn.close()
            
            print("✅ 数据库迁移完成")
            return True
            
        except Exception as e:
            print(f"❌ 运行迁移失败: {{e}}")
            return False

def main():
    print("🚀 数据库导入工具")
    print("=" * 50)
    
    # 获取数据库连接信息
    host = input("数据库主机 (默认: localhost): ").strip() or "localhost"
    port = input("数据库端口 (默认: 3306): ").strip() or "3306"
    username = input("数据库用户名: ").strip()
    password = input("数据库密码: ").strip()
    database = input("数据库名称: ").strip()
    
    if not all([username, password, database]):
        print("❌ 请提供完整的数据库连接信息")
        return
    
    try:
        port = int(port)
    except ValueError:
        print("❌ 端口号必须是数字")
        return
    
    # 创建导入器
    importer = DatabaseImporter(host, port, username, password, database)
    
    # 执行导入步骤
    if not importer.create_database_if_not_exists():
        return
    
    if not importer.import_complete_database():
        return
    
    if not importer.run_migrations():
        return
    
    print("\\n🎉 数据库导入完成！")
    print("💡 现在可以启动应用程序了")

if __name__ == "__main__":
    main()
'''
        
        try:
            with open(import_script, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 设置执行权限
            os.chmod(import_script, 0o755)
            
            print(f"✅ 导入脚本创建成功: {import_script}")
            return True
            
        except Exception as e:
            print(f"❌ 创建导入脚本失败: {e}")
            return False
    
    def create_database_info(self):
        """创建数据库信息文件"""
        print("📋 创建数据库信息文件...")
        
        info_file = self.export_dir / "database_info.json"
        
        info_data = {
            "export_time": datetime.datetime.now().isoformat(),
            "database_name": self.config['database'],
            "export_files": {
                "complete_database": f"complete_database_{self.timestamp}.sql",
                "structure_only": f"structure/database_structure_{self.timestamp}.sql",
                "data_only": f"data/database_data_{self.timestamp}.sql"
            },
            "import_instructions": {
                "step1": "运行 scripts/import_database.py 脚本",
                "step2": "或者手动导入 complete_database_*.sql 文件",
                "step3": "确保数据库字符集为 utf8mb4"
            },
            "requirements": {
                "mysql_version": ">=5.7",
                "python_packages": ["mysql-connector-python"],
                "charset": "utf8mb4",
                "collation": "utf8mb4_unicode_ci"
            }
        }
        
        try:
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(info_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 数据库信息文件创建成功: {info_file}")
            return True
            
        except Exception as e:
            print(f"❌ 创建数据库信息文件失败: {e}")
            return False
    
    def create_readme(self):
        """创建README文件"""
        print("📖 创建README文件...")
        
        readme_file = self.export_dir / "README.md"
        
        readme_content = f'''# 数据库导出包

导出时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
数据库名称: {self.config['database']}

## 文件说明

### 数据库文件
- `complete_database_{self.timestamp}.sql` - 完整数据库（结构+数据）
- `structure/database_structure_{self.timestamp}.sql` - 仅数据库结构
- `data/database_data_{self.timestamp}.sql` - 仅数据库数据

### 迁移文件
- `migrations/` - 数据库迁移文件目录

### 脚本文件
- `scripts/import_database.py` - 自动导入脚本

## 导入方法

### 方法1：使用自动导入脚本（推荐）

```bash
cd scripts
python3 import_database.py
```

按提示输入数据库连接信息即可自动完成导入。

### 方法2：手动导入

1. 创建数据库：
```sql
CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 导入数据：
```bash
mysql -h localhost -u username -p your_database_name < complete_database_{self.timestamp}.sql
```

3. 运行迁移（如果有）：
```bash
# 依次执行 migrations/ 目录下的SQL文件
```

## 系统要求

- MySQL >= 5.7
- Python >= 3.6
- mysql-connector-python 包

## 安装依赖

```bash
pip install mysql-connector-python
```

## 注意事项

1. 确保目标数据库字符集为 utf8mb4
2. 确保MySQL用户有足够的权限
3. 导入前请备份现有数据
4. 大型数据库导入可能需要较长时间

## 故障排除

### 常见问题

1. **字符编码问题**
   - 确保数据库和表都使用 utf8mb4 字符集

2. **权限问题**
   - 确保MySQL用户有 CREATE, INSERT, UPDATE, DELETE 权限

3. **连接问题**
   - 检查数据库服务是否运行
   - 检查防火墙设置
   - 验证连接参数

### 获取帮助

如果遇到问题，请检查：
1. MySQL错误日志
2. Python错误信息
3. 网络连接状态
'''
        
        try:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"✅ README文件创建成功: {readme_file}")
            return True
            
        except Exception as e:
            print(f"❌ 创建README文件失败: {e}")
            return False
    
    def run_export(self):
        """执行完整的导出流程"""
        print("🚀 开始数据库导出")
        print("=" * 50)
        print(f"数据库: {self.config['database']}")
        print(f"主机: {self.config['host']}:{self.config['port']}")
        print(f"导出目录: {self.export_dir}")
        print("=" * 50)
        
        steps = [
            ("创建导出目录", self.create_export_directory),
            ("导出数据库结构", self.export_database_structure),
            ("导出数据库数据", self.export_database_data),
            ("导出完整数据库", self.export_complete_database),
            ("复制迁移文件", self.copy_migration_files),
            ("创建导入脚本", self.create_import_script),
            ("创建数据库信息", self.create_database_info),
            ("创建README文件", self.create_readme)
        ]
        
        success_count = 0
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if step_func():
                success_count += 1
            else:
                print(f"❌ {step_name} 失败")
        
        print(f"\n📊 导出完成统计:")
        print(f"   成功步骤: {success_count}/{len(steps)}")
        
        if success_count == len(steps):
            print("\n🎉 数据库导出完成！")
            print(f"📁 导出文件位置: {self.export_dir}")
            print("\n📋 下一步操作:")
            print("1. 将整个 database_export 目录复制到目标服务器")
            print("2. 在目标服务器上运行 scripts/import_database.py")
            print("3. 或者手动导入 complete_database_*.sql 文件")
        else:
            print("\n⚠️ 部分导出步骤失败，请检查错误信息")
        
        return success_count == len(steps)

def main():
    """主函数"""
    print("🗄️ 数据库导出工具")
    print("=" * 50)
    
    try:
        exporter = DatabaseExporter()
        success = exporter.run_export()
        
        if success:
            print(f"\n✅ 导出成功完成")
            return 0
        else:
            print(f"\n❌ 导出过程中出现错误")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断导出过程")
        return 1
    except Exception as e:
        print(f"\n❌ 导出过程中发生未预期的错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())