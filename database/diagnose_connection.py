#!/usr/bin/env python3
"""
诊断数据库连接问题
"""

import socket
import sys
import asyncio

def test_socket_connection():
    """测试socket连接"""
    print("🔍 测试socket连接...")
    
    hosts_to_test = ['localhost', '127.0.0.1', '::1']
    port = 5432
    
    for host in hosts_to_test:
        try:
            print(f"测试连接到 {host}:{port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host}:{port} 连接成功")
                return host
            else:
                print(f"❌ {host}:{port} 连接失败 (错误码: {result})")
        except Exception as e:
            print(f"❌ {host}:{port} 连接异常: {e}")
    
    return None

async def test_asyncpg_connection(host):
    """测试asyncpg连接"""
    print(f"\n🔗 测试asyncpg连接到 {host}...")
    
    try:
        import asyncpg
        
        # 尝试不同的连接方式
        connection_strings = [
            f"postgresql://postgres:Hanatech@123@{host}:5432/devicemonitor",
            f"postgresql://postgres:Hanatech%40123@{host}:5432/devicemonitor",
        ]
        
        for i, conn_str in enumerate(connection_strings, 1):
            try:
                print(f"尝试连接方式 {i}: {conn_str.replace('Hanatech@123', '***').replace('Hanatech%40123', '***')}")
                conn = await asyncpg.connect(conn_str)
                version = await conn.fetchval("SELECT version()")
                await conn.close()
                print(f"✅ 连接成功！数据库版本: {version[:50]}...")
                return conn_str
            except Exception as e:
                print(f"❌ 连接方式 {i} 失败: {e}")
        
        # 尝试分别指定参数
        try:
            print("尝试使用参数方式连接...")
            conn = await asyncpg.connect(
                host=host,
                port=5432,
                user='postgres',
                password='Hanatech@123',
                database='devicemonitor'
            )
            version = await conn.fetchval("SELECT version()")
            await conn.close()
            print(f"✅ 参数方式连接成功！数据库版本: {version[:50]}...")
            return f"postgresql://postgres:Hanatech@123@{host}:5432/devicemonitor"
        except Exception as e:
            print(f"❌ 参数方式连接失败: {e}")
        
        return None
        
    except ImportError:
        print("❌ asyncpg 未安装")
        return None

async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🔍 数据库连接诊断工具                         ║
║              Database Connection Diagnostic                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 1. 测试socket连接
    working_host = test_socket_connection()
    
    if not working_host:
        print("\n❌ 无法通过socket连接到PostgreSQL")
        print("请检查:")
        print("1. PostgreSQL服务是否正在运行")
        print("2. 防火墙设置")
        print("3. PostgreSQL配置文件 (postgresql.conf, pg_hba.conf)")
        return False
    
    # 2. 测试asyncpg连接
    working_conn_str = await test_asyncpg_connection(working_host)
    
    if working_conn_str:
        print(f"\n✅ 找到可用的连接字符串:")
        print(f"   {working_conn_str.replace('Hanatech@123', '***')}")
        
        # 保存可用的连接字符串
        with open('working_connection.txt', 'w') as f:
            f.write(working_conn_str)
        
        print("\n📄 连接字符串已保存到 working_connection.txt")
        return True
    else:
        print("\n❌ 所有连接方式都失败了")
        print("可能的原因:")
        print("1. 用户名或密码错误")
        print("2. 数据库不存在")
        print("3. 用户权限不足")
        print("4. PostgreSQL配置问题")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)