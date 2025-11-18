"""
数据库迁移脚本：为设备类型表添加图标字段
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from app.core.database import TORTOISE_ORM


async def migrate():
    """执行数据库迁移"""
    try:
        # 初始化数据库连接
        await Tortoise.init(config=TORTOISE_ORM)
        
        # 获取数据库连接
        conn = Tortoise.get_connection("default")
        
        print("开始执行迁移...")
        
        # 添加 icon 字段
        print("1. 添加 icon 字段...")
        await conn.execute_query(
            "ALTER TABLE t_device_type ADD COLUMN IF NOT EXISTS icon VARCHAR(100)"
        )
        print("   ✓ icon 字段添加成功")
        
        # 添加字段注释
        print("2. 添加字段注释...")
        await conn.execute_query(
            "COMMENT ON COLUMN t_device_type.icon IS '设备类型图标（Iconify图标名称）'"
        )
        print("   ✓ 字段注释添加成功")
        
        # 为现有数据设置默认图标
        print("3. 为现有数据设置默认图标...")
        result = await conn.execute_query(
            "UPDATE t_device_type SET icon = 'material-symbols:precision-manufacturing' WHERE icon IS NULL"
        )
        print(f"   ✓ 已更新 {result[0]} 条记录")
        
        print("\n✅ 迁移完成！")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await Tortoise.close_connections()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(migrate())
    sys.exit(0 if success else 1)
