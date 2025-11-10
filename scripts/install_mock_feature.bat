@echo off
chcp 65001 >nul
echo ========================================
echo   Mock功能数据库安装脚本
echo ========================================
echo.

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
    echo 3. 用户名不正确（应为 postgres）
    echo.
    echo 请检查后重试。
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
echo 1. 关闭此窗口
echo 2. 双击运行 "start_backend.bat" 启动后端
echo 3. 等待后端启动完成后，刷新浏览器页面（按F5）
echo.
pause

