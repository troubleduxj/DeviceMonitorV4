@echo off
chcp 65001 >nul
echo ========================================
echo 启动 PostgreSQL 服务
echo ========================================
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ 需要管理员权限！
    echo.
    echo 请右键点击此脚本，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [1/3] 检查当前服务状态...
sc query postgresql-x64-17 | findstr "RUNNING" >nul
if %errorlevel% equ 0 (
    echo ✓ PostgreSQL 服务已经在运行
    goto :check_port
)

echo [2/3] 正在启动 PostgreSQL 服务...
net start postgresql-x64-17

if %errorlevel% equ 0 (
    echo ✓ PostgreSQL 服务启动成功！
    timeout /t 2 /nobreak >nul
) else (
    echo ✗ PostgreSQL 服务启动失败！
    echo.
    echo 可能的原因：
    echo 1. PostgreSQL 配置有问题
    echo 2. 端口 5432 被占用
    echo 3. 数据目录损坏
    echo.
    echo 查看详细日志：
    echo D:\Program Files\PostgreSQL\17\data\log\
    echo.
    pause
    exit /b 1
)

:check_port
echo [3/3] 检查端口 5432...
timeout /t 2 /nobreak >nul
netstat -ano | findstr ":5432" >nul
if %errorlevel% equ 0 (
    echo ✓ 端口 5432 正在监听
    echo.
    echo ========================================
    echo ✓ PostgreSQL 服务运行正常！
    echo ========================================
    echo.
    echo 现在可以启动后端服务了：
    echo   python run.py
) else (
    echo ✗ 端口 5432 未监听
    echo 服务可能正在启动中，请稍等...
)

echo.
echo 按任意键退出...
pause >nul
