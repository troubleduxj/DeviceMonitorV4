@echo off
chcp 65001 >nul
title 一键修复数据库连接问题

echo ========================================
echo 一键修复数据库连接问题
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

echo [步骤 1/5] 检查 .env 配置文件...
if exist .env (
    echo ✓ .env 文件已存在
) else (
    echo ! .env 文件不存在，正在创建...
    copy .env.example .env >nul 2>&1
    if exist .env (
        echo ✓ .env 文件创建成功
    ) else (
        echo ✗ .env 文件创建失败
    )
)
echo.

echo [步骤 2/5] 检查 PostgreSQL 服务状态...
sc query postgresql-x64-17 | findstr "RUNNING" >nul
if %errorlevel% equ 0 (
    echo ✓ PostgreSQL 服务已在运行
) else (
    echo ! PostgreSQL 服务未运行，正在启动...
    net start postgresql-x64-17
    if %errorlevel% equ 0 (
        echo ✓ PostgreSQL 服务启动成功
        timeout /t 3 /nobreak >nul
    ) else (
        echo ✗ PostgreSQL 服务启动失败
        echo.
        echo 请检查：
        echo 1. PostgreSQL 是否正确安装
        echo 2. 查看日志：D:\Program Files\PostgreSQL\17\data\log\
        echo.
        pause
        exit /b 1
    )
)
echo.

echo [步骤 3/5] 检查端口 5432...
timeout /t 2 /nobreak >nul
netstat -ano | findstr ":5432" >nul
if %errorlevel% equ 0 (
    echo ✓ 端口 5432 正在监听
) else (
    echo ✗ 端口 5432 未监听
    echo 等待服务完全启动...
    timeout /t 5 /nobreak >nul
    netstat -ano | findstr ":5432" >nul
    if %errorlevel% equ 0 (
        echo ✓ 端口 5432 现在正在监听
    ) else (
        echo ✗ 端口 5432 仍未监听，可能存在问题
    )
)
echo.

echo [步骤 4/5] 检查数据库是否存在...
where psql >nul 2>&1
if %errorlevel% equ 0 (
    echo 正在检查数据库 devicemonitor...
    psql -h 127.0.0.1 -p 5432 -U postgres -l 2>nul | findstr "devicemonitor" >nul
    if %errorlevel% equ 0 (
        echo ✓ 数据库 devicemonitor 已存在
    ) else (
        echo ! 数据库 devicemonitor 不存在
        echo 提示：首次运行时，后端会自动创建数据库表
    )
) else (
    echo ! psql 未安装，跳过数据库检查
)
echo.

echo [步骤 5/5] 设置服务自动启动...
sc config postgresql-x64-17 start= auto >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 已设置 PostgreSQL 服务为自动启动
) else (
    echo ! 无法设置自动启动（可能已经是自动启动）
)
echo.

echo ========================================
echo ✓ 修复完成！
echo ========================================
echo.
echo 现在可以启动后端服务：
echo   python run.py
echo.
echo 或者使用虚拟环境：
echo   .venv\Scripts\activate
echo   python run.py
echo.
pause
