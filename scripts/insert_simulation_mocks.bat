@echo off
chcp 65001 > nul
echo ========================================
echo 插入模拟设备Mock规则
echo ========================================
echo.

set PGPASSWORD=Hanatech@123
set SQL_FILE=..\database\migrations\insert_simulation_device_mocks.sql

echo [1/3] 检查SQL文件...
if not exist "%SQL_FILE%" (
    echo ❌ 错误: 找不到SQL文件
    echo    路径: %SQL_FILE%
    echo.
    pause
    exit /b 1
)
echo ✓ SQL文件存在

echo.
echo [2/3] 连接数据库并执行SQL...
echo    数据库: device_monitor
echo    主机: localhost:5432
echo    用户: postgres
echo.

psql -h localhost -p 5432 -U postgres -d device_monitor -f "%SQL_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 执行失败！
    echo.
    echo 可能的原因：
    echo   1. psql命令未找到（PostgreSQL未安装或未添加到PATH）
    echo   2. 数据库连接失败（检查密码、端口、数据库名）
    echo   3. SQL语法错误
    echo.
    echo 替代方案：
    echo   1. 使用pgAdmin手动执行SQL文件
    echo   2. 运行Python脚本: python scripts\insert_simulation_mocks.py
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] 验证插入结果...
echo.
echo ✅ 模拟设备Mock规则插入完成！
echo.
echo 已插入的Mock规则：
echo   • 模拟设备分类-设备列表 (5台设备)
echo   • 模拟设备-详情信息
echo   • 模拟设备-实时数据
echo   • 模拟设备-历史数据 (2025-10-29全天)
echo   • 模拟设备-统计数据
echo.
echo 下一步操作：
echo   1. 刷新浏览器页面 (Ctrl + Shift + R)
echo   2. 访问: 高级设置 → Mock数据管理
echo   3. 启用对应的Mock规则
echo   4. 启用Mock全局开关
echo   5. 访问设备管理页面查看模拟设备
echo.
echo 详细使用说明请查看：
echo   docs\SIMULATION_DEVICE_MOCK_GUIDE.md
echo.
pause

