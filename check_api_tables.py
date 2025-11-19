"""
检查数据库中的API相关表
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('.env')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'devicemonitor'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

def check_api_tables():
    """检查API相关表"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("检查数据库中的API相关表")
        print("=" * 80)
        
        # 查找所有包含'api'的表
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE '%api%'
            ORDER BY table_name;
        """)
        
        api_tables = cursor.fetchall()
        
        if api_tables:
            print(f"\n找到 {len(api_tables)} 个API相关表：\n")
            for (table_name,) in api_tables:
                print(f"  - {table_name}")
                
                # 获取表结构
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                
                columns = cursor.fetchall()
                print(f"    字段: {', '.join([col[0] for col in columns])}")
                
                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"    记录数: {count}\n")
        else:
            print("\n没有找到API相关表")
        
        # 检查所有表
        print("\n" + "=" * 80)
        print("所有表列表")
        print("=" * 80)
        
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        all_tables = cursor.fetchall()
        print(f"\n数据库中共有 {len(all_tables)} 个表：\n")
        for (table_name,) in all_tables:
            print(f"  - {table_name}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_api_tables()
