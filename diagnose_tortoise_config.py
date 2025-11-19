"""
诊断 Tortoise ORM 配置

检查配置是否正确，以及模型是否正确绑定到数据库连接
"""
import asyncio
import json
import sys
from tortoise import Tortoise
from app.settings.config import settings

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


async def diagnose():
    print("=" * 80)
    print("Tortoise ORM 配置诊断")
    print("=" * 80)
    
    # 1. 检查配置
    print("\n1. 检查配置结构")
    print("-" * 80)
    config = settings.tortoise_orm.model_dump()
    print(json.dumps(config, indent=2, default=str))
    
    # 2. 初始化 Tortoise
    print("\n2. 初始化 Tortoise ORM")
    print("-" * 80)
    try:
        await Tortoise.init(config=config)
        print("✓ Tortoise ORM 初始化成功")
    except Exception as e:
        print(f"✗ Tortoise ORM 初始化失败: {e}")
        import traceback
        print(traceback.format_exc())
        return
    
    # 3. 检查连接
    print("\n3. 检查数据库连接")
    print("-" * 80)
    from tortoise.connection import connections
    
    storage = connections._get_storage()
    print(f"可用连接: {list(storage.keys())}")
    
    for conn_name, conn in storage.items():
        print(f"\n连接 '{conn_name}':")
        print(f"  - 类型: {type(conn)}")
        print(f"  - 状态: {'已连接' if conn else '未连接'}")
    
    # 4. 检查模型注册
    print("\n4. 检查模型注册")
    print("-" * 80)
    
    from app.models.admin import AuditLog
    
    print(f"\nAuditLog 模型:")
    print(f"  - 表名: {AuditLog._meta.db_table}")
    print(f"  - app: {AuditLog._meta.app}")
    
    # 尝试获取 _default_connection
    try:
        print(f"  - _default_connection: {AuditLog._meta._default_connection}")
    except AttributeError:
        print(f"  - _default_connection: 不存在")
    
    # 检查 db 属性（这会触发错误）
    try:
        db_value = AuditLog._meta.db
        print(f"  - db: {db_value}")
    except Exception as e:
        print(f"  - db: 错误 - {e}")
    
    # 5. 检查 apps 配置
    print("\n5. 检查 apps 配置")
    print("-" * 80)
    
    if hasattr(Tortoise, 'apps'):
        print(f"Tortoise.apps: {Tortoise.apps}")
        for app_name, app_config in Tortoise.apps.items():
            print(f"\nApp '{app_name}':")
            print(f"  - 模型: {list(app_config.keys())}")
            print(f"  - 连接: {getattr(app_config, 'connection', 'N/A')}")
    
    # 6. 尝试创建测试记录
    print("\n6. 尝试创建测试审计日志")
    print("-" * 80)
    
    try:
        from datetime import datetime
        
        test_data = {
            "user_id": 999,
            "username": "test_diagnose",
            "module": "诊断",
            "summary": "配置诊断测试",
            "method": "GET",
            "path": "/diagnose",
            "status": 200,
            "response_time": 1,
            "request_args": {},
            "response_body": {}
        }
        
        audit_log = AuditLog(**test_data)
        now = datetime.now()
        if now.tzinfo is not None:
            now = now.replace(tzinfo=None)
        audit_log.created_at = now
        audit_log.updated_at = now
        
        print("尝试使用 using_db='default' 保存...")
        await audit_log.save(using_db="default")
        print(f"✓ 成功创建审计日志，ID: {audit_log.id}")
        
        # 清理
        await audit_log.delete()
        print("✓ 测试数据已清理")
        
    except Exception as e:
        print(f"✗ 创建审计日志失败: {e}")
        import traceback
        print(traceback.format_exc())
    
    # 关闭连接
    await Tortoise.close_connections()
    
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(diagnose())
