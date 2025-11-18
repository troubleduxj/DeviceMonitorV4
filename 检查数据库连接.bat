@echo off
chcp 65001 >nul
echo ========================================
echo 数据库连接检查工具
echo ========================================
echo.

echo [1/4] 检查 PostgreSQL 服务状态...
sc query postgresql-x64-17 | findstr "STATE"
if %errorlevel% neq 0 (
    echo ✗ 无法查询服务状态
) else (
    echo ✓ 服务状态查询成功
)
echo.

echo [2/4] 检查 PostgreSQL 端口 5432...
netstat -ano | findstr ":5432" >nul
if %errorlevel% neq 0 (
    echo ✗ 端口 5432 未监听（PostgreSQL 可能未启动）
) else (
    echo ✓ 端口 5432 正在监听
)
echo.

echo [3/4] 检查 .env 配置文件...
if exist .env (
    echo ✓ .env 文件存在
    echo.
    echo 数据库配置：
    findstr /B "DB_HOST DB_PORT DB_NAME DB_USER" .env
) else (
    echo ✗ .env 文件不存在
    echo 提示：请从 .env.example 复制并修改配置
)
echo.

echo [4/4] 尝试连接数据库...
echo 使用 psql 测试连接（如果已安装）...
where psql >nul 2>&1
if %errorlevel% equ 0 (
    echo psql -h 127.0.0.1 -p 5432 -U postgres -d devicemonitor -c "SELECT version();"
    psql -h 127.0.0.1 -p 5432 -U postgres -d devicemonitor -c "SELECT version();"
) else (
    echo psql 未安装或不在 PATH 中
)
echo.

echo ========================================
echo 检查完成
echo ========================================
echo.
echo 如果 PostgreSQL 服务未启动，请：
echo 1. 右键点击 "启动PostgreSQL服务.bat"
echo 2. 选择 "以管理员身份运行"
echo.
pause
