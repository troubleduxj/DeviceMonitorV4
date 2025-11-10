-- 权限系统数据库初始化脚本

-- 创建数据库（如果不存在）
SELECT 'CREATE DATABASE permission_system'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'permission_system')\gexec

-- 连接到权限系统数据库
\c permission_system;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- 设置时区
SET timezone = 'UTC';

-- 创建应用用户（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'app_user') THEN
        CREATE USER app_user WITH PASSWORD 'app_password';
    END IF;
END
$$;

-- 授权
GRANT CONNECT ON DATABASE permission_system TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT CREATE ON SCHEMA public TO app_user;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- 创建审计触发器函数
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (
            table_name,
            operation,
            new_values,
            user_id,
            timestamp
        ) VALUES (
            TG_TABLE_NAME,
            TG_OP,
            row_to_json(NEW),
            COALESCE(current_setting('app.current_user_id', true)::integer, 0),
            NOW()
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (
            table_name,
            operation,
            old_values,
            new_values,
            user_id,
            timestamp
        ) VALUES (
            TG_TABLE_NAME,
            TG_OP,
            row_to_json(OLD),
            row_to_json(NEW),
            COALESCE(current_setting('app.current_user_id', true)::integer, 0),
            NOW()
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (
            table_name,
            operation,
            old_values,
            user_id,
            timestamp
        ) VALUES (
            TG_TABLE_NAME,
            TG_OP,
            row_to_json(OLD),
            COALESCE(current_setting('app.current_user_id', true)::integer, 0),
            NOW()
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建性能监控视图
CREATE OR REPLACE VIEW performance_stats AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY tablename, attname;

-- 创建连接监控视图
CREATE OR REPLACE VIEW connection_stats AS
SELECT 
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active_connections,
    count(*) FILTER (WHERE state = 'idle') as idle_connections,
    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity
WHERE datname = current_database();

-- 设置日志参数
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;

-- 重新加载配置
SELECT pg_reload_conf();

-- 输出初始化完成信息
SELECT 'Database initialization completed successfully' as status;