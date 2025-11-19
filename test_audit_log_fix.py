"""
测试审计日志修复

这个脚本用于验证审计日志的数据库连接问题是否已修复
"""
import asyncio
from tortoise import Tortoise
from app.settings.config import settings
from app.models.admin import AuditLog
from datetime import datetime


async def test_audit_log():
    """测试审计日志创建"""
    print("=" * 60)
    print("测试审计日志数据库连接")
    print("=" * 60)
    
    try:
        # 初始化Tortoise ORM
        print("\n1. 初始化Tortoise ORM...")
        config = settings.tortoise_orm.model_dump()
        print(f"   配置: {config['apps']['models']['default_connection']}")
        print(f"   连接: {list(config['connections'].keys())}")
        
        await Tortoise.init(config=config)
        print("   ✓ Tortoise ORM初始化成功")
        
        # 检查连接
        print("\n2. 检查数据库连接...")
        from tortoise.connection import connections
        
        for conn_name in ["default", "postgres"]:
            try:
                conn = connections.get(conn_name)
                print(f"   ✓ 连接 '{conn_name}' 可用: {conn is not None}")
            except KeyError:
                print(f"   ✗ 连接 '{conn_name}' 不存在")
        
        # 测试创建审计日志
        print("\n3. 测试创建审计日志...")
        test_data = {
            "user_id": 1,
            "username": "test_user",
            "module": "测试模块",
            "summary": "测试审计日志创建",
            "method": "GET",
            "path": "/test/path",
            "status": 200,
            "response_time": 100,
            "request_args": {"test": "data"},
            "response_body": {"code": 200, "msg": "success"}
        }
        
        audit_log = AuditLog(**test_data)
        
        # 手动设置时间戳
        now = datetime.now()
        if now.tzinfo is not None:
            now = now.replace(tzinfo=None)
        audit_log.created_at = now
        audit_log.updated_at = now
        
        # 保存到数据库
        await audit_log.save()
        print(f"   ✓ 审计日志创建成功，ID: {audit_log.id}")
        
        # 验证保存
        print("\n4. 验证审计日志...")
        saved_log = await AuditLog.get(id=audit_log.id)
        print(f"   ✓ 审计日志读取成功")
        print(f"   - 用户: {saved_log.username}")
        print(f"   - 模块: {saved_log.module}")
        print(f"   - 摘要: {saved_log.summary}")
        print(f"   - 创建时间: {saved_log.created_at}")
        
        # 清理测试数据
        print("\n5. 清理测试数据...")
        await saved_log.delete()
        print("   ✓ 测试数据已清理")
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！审计日志功能正常")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        
    finally:
        # 关闭连接
        await Tortoise.close_connections()
        print("\n数据库连接已关闭")


if __name__ == "__main__":
    asyncio.run(test_audit_log())
