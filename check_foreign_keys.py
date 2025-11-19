"""
检查t_sys_role_api表的外键约束
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

def check_foreign_keys():
    """检查外键约束"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 't_sys_role_api'
            ORDER BY tc.table_name, kcu.column_name;
        """)
        
        print("=" * 80)
        print("t_sys_role_api 表的外键约束")
        print("=" * 80)
        
        rows = cursor.fetchall()
        if rows:
            print("\n外键约束：\n")
            for table_name, column_name, foreign_table, foreign_column, constraint_name in rows:
                print(f"  {column_name} -> {foreign_table}.{foreign_column}")
                print(f"    约束名: {constraint_name}\n")
        else:
            print("\n没有找到外键约束")
        
        # 检查api_id引用的记录是否存在
        print("=" * 80)
        print("检查api_id的有效性")
        print("=" * 80)
        
        cursor.execute("""
            SELECT DISTINCT ra.api_id
            FROM t_sys_role_api ra
            LEFT JOIN t_sys_api_endpoints ae ON ra.api_id = ae.id
            WHERE ae.id IS NULL
            LIMIT 10;
        """)
        
        invalid_ids = cursor.fetchall()
        if invalid_ids:
            print(f"\n找到 {len(invalid_ids)} 个无效的api_id（在t_sys_api_endpoints中不存在）：")
            for (api_id,) in invalid_ids:
                print(f"  - {api_id}")
        else:
            print("\n所有api_id都有效")
        
        # 检查示例数据
        print("\n" + "=" * 80)
        print("t_sys_api_endpoints 表示例数据")
        print("=" * 80)
        
        cursor.execute("""
            SELECT id, api_code, api_name, api_path, http_method
            FROM t_sys_api_endpoints
            ORDER BY id
            LIMIT 5;
        """)
        
        rows = cursor.fetchall()
        print("\n前5条记录：\n")
        for id, api_code, api_name, api_path, http_method in rows:
            print(f"  ID: {id}")
            print(f"    编码: {api_code}")
            print(f"    名称: {api_name}")
            print(f"    路径: {api_path}")
            print(f"    方法: {http_method}\n")
        
        cursor.close()
        conn.close()
        
        print("=" * 80)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_foreign_keys()
