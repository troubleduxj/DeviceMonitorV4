"""
检查角色API关联表
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

def check_tables():
    """检查相关表结构"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("检查角色API关联表")
        print("=" * 80)
        
        # 检查表是否存在
        tables_to_check = ['t_sys_role', 't_sys_api_endpoint', 't_sys_role_api']
        
        for table_name in tables_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            
            exists = cursor.fetchone()[0]
            status = "✓ 存在" if exists else "✗ 不存在"
            print(f"\n表 {table_name}: {status}")
            
            if exists:
                # 获取表结构
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                
                columns = cursor.fetchall()
                print(f"  字段列表：")
                for col_name, data_type, is_nullable in columns:
                    nullable = "NULL" if is_nullable == 'YES' else "NOT NULL"
                    print(f"    - {col_name:20s} {data_type:20s} {nullable}")
                
                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"  记录数: {count}")
        
        # 检查t_sys_role_api表的数据
        print("\n" + "=" * 80)
        print("t_sys_role_api 表数据示例")
        print("=" * 80)
        
        cursor.execute("""
            SELECT role_id, api_id
            FROM t_sys_role_api
            LIMIT 10;
        """)
        
        rows = cursor.fetchall()
        if rows:
            print("\n前10条记录：")
            for role_id, api_id in rows:
                print(f"  role_id: {role_id}, api_id: {api_id}")
        else:
            print("\n表中没有数据")
        
        # 检查角色ID=3的权限
        print("\n" + "=" * 80)
        print("角色ID=3的当前权限")
        print("=" * 80)
        
        cursor.execute("""
            SELECT r.id, r.role_name, COUNT(ra.api_id) as api_count
            FROM t_sys_role r
            LEFT JOIN t_sys_role_api ra ON r.id = ra.role_id
            WHERE r.id = 3
            GROUP BY r.id, r.role_name;
        """)
        
        result = cursor.fetchone()
        if result:
            role_id, role_name, api_count = result
            print(f"\n角色: {role_name} (ID: {role_id})")
            print(f"API权限数量: {api_count}")
        else:
            print("\n找不到ID为3的角色")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("检查完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_tables()
