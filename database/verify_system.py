#!/usr/bin/env python3
"""
验证分阶段迁移系统是否准备就绪
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_header():
    """打印标题"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 🔍 系统验证工具                              ║
║              System Verification Tool                       ║
╚══════════════════════════════════════════════════════════════╝
    """)

async def verify_database_connection():
    """验证数据库连接"""
    print("🔗 验证数据库连接...")
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ 未设置 DATABASE_URL 环境变量")
        print("请设置: export DATABASE_URL='postgresql://user:password@localhost:5432/database'")
        return False
    
    try:
        import asyncpg
        conn = await asyncpg.connect(db_url)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        
        if result == 1:
            print("✅ 数据库连接成功")
            return True
        else:
            print("❌ 数据库连接测试失败")
            return False
    except ImportError:
        print("❌ 缺少 asyncpg 依赖，请运行: pip install asyncpg")
        return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def verify_required_files():
    """验证必需文件"""
    print("\n📁 验证必需文件...")
    
    required_files = [
        'phased_migration_strategy.py',
        'data_consistency_validator.py',
        'configurable_read_switch.py',
        'migration_alerting_system.py',
        'config.json'
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 文件不存在")
            all_exist = False
    
    return all_exist

def verify_config_files():
    """验证配置文件"""
    print("\n⚙️ 验证配置文件...")
    
    config_files = [
        ('config.json', '主配置文件'),
        ('migration_configs.json', '迁移配置'),
        ('read_switch_configs.json', '切换配置'),
        ('alerting_config.json', '告警配置'),
        ('validation_rules.json', '验证规则')
    ]
    
    all_valid = True
    for file, description in config_files:
        try:
            if Path(file).exists():
                with open(file, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✅ {file} - {description}")
            else:
                print(f"⚠️ {file} - {description} (可选)")
        except json.JSONDecodeError as e:
            print(f"❌ {file} - JSON格式错误: {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {file} - 读取失败: {e}")
            all_valid = False
    
    return all_valid

async def verify_system_components():
    """验证系统组件"""
    print("\n🔧 验证系统组件...")
    
    try:
        # 测试导入
        from phased_migration_strategy import PhasedMigrationStrategy
        from data_consistency_validator import DataConsistencyValidator
        from configurable_read_switch import ConfigurableReadSwitch
        from migration_alerting_system import MigrationAlertingSystem
        
        print("✅ 所有组件导入成功")
        
        # 测试初始化
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            strategy = PhasedMigrationStrategy(db_url)
            validator = DataConsistencyValidator(db_url)
            switch = ConfigurableReadSwitch(db_url)
            alerting = MigrationAlertingSystem(db_url)
            
            print("✅ 组件初始化成功")
            return True
        else:
            print("⚠️ 无法测试组件初始化（缺少数据库连接）")
            return True
            
    except ImportError as e:
        print(f"❌ 组件导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 组件验证失败: {e}")
        return False

def verify_dependencies():
    """验证依赖"""
    print("\n📦 验证Python依赖...")
    
    required_packages = [
        ('asyncpg', '数据库连接'),
        ('aiohttp', 'HTTP客户端')
    ]
    
    all_available = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (请运行: pip install {package})")
            all_available = False
    
    return all_available

def show_system_info():
    """显示系统信息"""
    print("\n📊 系统信息:")
    print(f"  Python版本: {sys.version.split()[0]}")
    print(f"  当前目录: {Path.cwd()}")
    print(f"  数据库URL: {os.getenv('DATABASE_URL', '未设置')[:50]}...")
    
    # 显示配置文件状态
    print("\n📋 配置文件状态:")
    config_files = ['config.json', 'migration_configs.json', 'read_switch_configs.json', 
                   'alerting_config.json', 'validation_rules.json']
    
    for file in config_files:
        if Path(file).exists():
            size = Path(file).stat().st_size
            print(f"  ✅ {file} ({size} bytes)")
        else:
            print(f"  ❌ {file} (不存在)")

async def run_verification():
    """运行完整验证"""
    print_header()
    
    tests = [
        ("Python依赖", verify_dependencies),
        ("必需文件", verify_required_files),
        ("配置文件", verify_config_files),
        ("数据库连接", verify_database_connection),
        ("系统组件", verify_system_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"💥 {test_name} 验证异常: {e}")
    
    # 显示系统信息
    show_system_info()
    
    # 显示结果
    print("\n" + "=" * 60)
    print(f"📊 验证结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 系统验证通过！准备执行迁移")
        print("\n🚀 下一步:")
        print("  python execute_migration.py")
        return True
    else:
        print(f"⚠️ {total - passed} 项验证失败，请解决问题后重试")
        print("\n🔧 解决方案:")
        if not os.getenv('DATABASE_URL'):
            print("  1. 设置数据库连接: export DATABASE_URL='postgresql://...'")
        print("  2. 安装依赖: pip install asyncpg aiohttp")
        print("  3. 检查文件完整性")
        return False

async def main():
    """主函数"""
    try:
        success = await run_verification()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 验证被用户中断")
    except Exception as e:
        print(f"\n💥 验证过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())