@echo off
chcp 65001 >nul
echo ================================================================================
echo Mock规则批量插入工具 - 插入系统核心API的Mock模拟数据
echo ================================================================================
echo.

cd /d "%~dp0.."

set PGPASSWORD=Hanatech@123
set PGCLIENTENCODING=UTF8

echo [说明] 本脚本将插入以下类型的Mock规则:
echo.
echo   ✓ 认证相关: 登录、用户信息
echo   ✓ 用户管理: 用户列表、用户详情
echo   ✓ 菜单管理: 菜单列表、菜单树
echo   ✓ 角色管理: 角色列表、角色详情
echo   ✓ 设备管理: 设备列表、设备统计
echo   ✓ 系统参数: 参数配置
echo   ✓ 错误场景: 超时、权限、服务器错误
echo   ✓ 特殊场景: 加载中、空数据
echo.
echo [注意] 所有规则默认为禁用状态，使用前需要在页面上启用
echo.

set /p confirm="确认执行插入操作? (Y/N): "
if /i "%confirm%" NEQ "Y" (
    echo.
    echo 操作已取消
    pause
    exit /b 0
)

echo.
echo ================================================================================
echo [执行] 插入Mock规则到数据库...
echo ================================================================================
echo.

psql -h localhost -p 5432 -U postgres -d device_monitor -f database\migrations\insert_mock_rules.sql

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ SQL执行失败
    echo.
    echo 可能的原因:
    echo   1. PostgreSQL服务未启动
    echo   2. psql命令不在PATH中
    echo   3. 数据库连接配置错误
    echo   4. 密码不正确 (当前使用: Hanatech@123)
    echo.
    echo 解决方案:
    echo   1. 检查PostgreSQL服务状态
    echo   2. 在pgAdmin或其他数据库工具中手动执行SQL
    echo   3. SQL文件位置: database\migrations\insert_mock_rules.sql
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo ✅ Mock规则插入成功！
echo ================================================================================
echo.
echo 📋 已插入的Mock规则类型:
echo   • 认证相关: 3条规则
echo   • 用户管理: 1条规则
echo   • 菜单管理: 2条规则
echo   • 角色管理: 1条规则
echo   • 设备管理: 2条规则
echo   • 系统参数: 1条规则
echo   • 错误场景: 3条规则
echo   • 特殊场景: 2条规则
echo.
echo 🚀 下一步操作:
echo   1. 刷新浏览器 (Ctrl + Shift + R)
echo   2. 访问: 高级设置 → Mock数据管理
echo   3. 查看已插入的Mock规则
echo   4. 启用需要测试的规则
echo   5. 启用Mock全局开关
echo.
echo 💡 使用提示:
echo   • 所有规则默认为禁用状态
echo   • 在Mock管理页面启用对应规则
echo   • 点击"测试"按钮可预览规则效果
echo   • 使用"命中次数"查看规则使用情况
echo   • 测试完成后记得禁用Mock功能
echo.
pause

