@echo off
chcp 65001 >nul
echo ========================================
echo   Mock功能自动安装脚本
echo ========================================
echo.

set PGPASSWORD=Hanatech@123

echo 【步骤1】正在创建Mock数据表...
echo.
psql -U postgres -d device_monitor -f "%~dp0..\database\migrations\add_mock_data_table.sql"
if %errorlevel% neq 0 (
    echo.
    echo ❌ 创建数据表失败！
    echo.
    echo 可能的原因：
    echo 1. PostgreSQL未安装或未启动
    echo 2. 数据库名称不正确（应为 device_monitor）
    echo 3. 用户名或密码不正确
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Mock数据表创建成功！
echo.

echo 【步骤2】正在添加Mock管理菜单...
echo.
psql -U postgres -d device_monitor -f "%~dp0..\database\migrations\add_mock_management_menu.sql"
if %errorlevel% neq 0 (
    echo.
    echo ❌ 添加菜单失败！
    pause
    exit /b 1
)

echo.
echo ✅ Mock管理菜单添加成功！
echo.

echo ========================================
echo   🎉 数据库安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 运行后端服务
echo 2. 登录系统
echo 3. 初始化权限
echo.
pause

