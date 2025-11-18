"""
数据库迁移脚本：为设备类型表添加图标字段（简化版）
"""
import psycopg2
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('app/.env')

def migrate():
    """执行数据库迁移"""
    try:
        # 从环境变量获取数据库配置
        db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'database': os.getenv('POSTGRES_DATABASE', 'devicemonitor')
        }
        
        print(f"连接数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        # 连接数据库
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("\n开始执行迁移...")
        
        # 1. 添加 icon 字段
        print("1. 添加 icon 字段...")
        cursor.execute(
            "ALTER TABLE t_device_type ADD COLUMN IF NOT EXISTS icon VARCHAR(100)"
        )
        print("   ✓ icon 字段添加成功")
        
        # 2. 添加字段注释
        print("2. 添加字段注释...")
        cursor.execute(
            "COMMENT ON COLUMN t_device_type.icon IS '设备类型图标（Iconify图标名称）'"
        )
        print("   ✓ 字段注释添加成功")
        
        # 3. 为现有数据设置默认图标
        print("3. 为现有数据设置默认图标...")
        cursor.execute(
            "UPDATE t_device_type SET icon = 'material-symbols:precision-manufacturing' WHERE icon IS NULL"
        )
        affected_rows = cursor.rowcount
        print(f"   ✓ 已更新 {affected_rows} 条记录")
        
        # 提交事务
        conn.commit()
        
        print("\n✅ 迁移完成！")
        
        # 验证迁移结果
        print("\n验证迁移结果...")
        cursor.execute("SELECT type_code, type_name, icon FROM t_device_type LIMIT 5")
        rows = cursor.fetchall()
        print("\n前5条记录:")
        for row in rows:
            print(f"  - {row[0]}: {row[1]} -> {row[2]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = migrate()
    sys.exit(0 if success else 1)
