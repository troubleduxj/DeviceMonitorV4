@echo off
chcp 65001 > nul
echo ============================================================
echo 开始初始化按钮权限数据
echo ============================================================
echo.

REM 检查SQL文件是否存在
if not exist "database\button_permissions_init.sql" (
    echo ❌ 错误: SQL文件不存在
    pause
    exit /b 1
)

echo 正在执行SQL脚本...
echo.

REM 执行SQL脚本（请根据实际情况修改数据库连接信息）
mysql -h localhost -P 3306 -u root -proot device_monitor < database\button_permissions_init.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo ✅ 按钮权限初始化成功！
    echo ============================================================
    echo.
    echo 请刷新浏览器页面，然后查看：
    echo   系统管理 -^> 角色管理 -^> 分配权限 -^> 菜单权限
    echo.
) else (
    echo.
    echo ❌ SQL执行失败，错误代码: %ERRORLEVEL%
    echo.
    echo 可能的原因：
    echo 1. MySQL未安装或未添加到PATH
    echo 2. 数据库连接信息不正确
    echo 3. 数据库 device_monitor 不存在
    echo.
    echo 请手动执行SQL脚本：
    echo   mysql -h localhost -u root -p device_monitor ^< database\button_permissions_init.sql
    echo.
)

pause

