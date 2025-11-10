@echo off
chcp 65001 >nul
echo ================================================================================
echo 菜单移动工具 - 将主题管理和组件管理移动到高级设置
echo ================================================================================
echo.

cd /d "%~dp0.."

set PGPASSWORD=Hanatech@123
set PGCLIENTENCODING=UTF8

echo [提示] 即将执行SQL迁移...
echo.
echo 数据库配置:
echo   - 主机: localhost
echo   - 端口: 5432
echo   - 数据库: device_monitor  
echo   - 用户: postgres
echo.
pause

echo.
echo [执行] 运行SQL迁移...
echo.

psql -h localhost -p 5432 -U postgres -d device_monitor -f database\migrations\move_menus_to_advanced_settings.sql

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ SQL执行失败
    echo.
    echo 可能的原因:
    echo   1. PostgreSQL服务未启动
    echo   2. psql命令不在PATH中
    echo   3. 数据库连接配置错误
    echo.
    echo 请尝试:
    echo   1. 在pgAdmin或其他数据库工具中手动执行SQL
    echo   2. SQL文件位置: database\migrations\move_menus_to_advanced_settings.sql
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo ✅ 菜单移动完成！
echo ================================================================================
echo.
echo 下一步:
echo   1. 刷新浏览器页面 (Ctrl + Shift + R)
echo   2. 在左侧菜单中查看"高级设置"
echo   3. 应该可以看到3个子菜单:
echo      - Mock数据管理
echo      - 主题管理
echo      - 组件管理
echo.
pause

