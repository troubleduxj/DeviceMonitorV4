@echo off
REM ================================================================
REM 阶段1核心完善 - 快速启动脚本 (Windows)
REM ================================================================
REM 自动执行数据库迁移、启动服务、运行测试
REM ================================================================

echo.
echo ================================================================
echo   阶段1核心完善 - 快速启动脚本
echo ================================================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python环境，请先安装Python 3.9+
    pause
    exit /b 1
)

echo [1/5] 检查Python环境... OK
echo.

REM Step 1: 执行数据库迁移
echo ================================================================
echo [2/5] 执行数据库迁移
echo ================================================================
echo.

python database\migrations\ai-module\execute_003_migration.py
if errorlevel 1 (
    echo.
    echo [错误] 数据库迁移失败！
    echo 请检查：
    echo   1. PostgreSQL是否运行
    echo   2. 数据库连接配置是否正确
    echo   3. 查看上方错误信息
    echo.
    pause
    exit /b 1
)

echo.
echo [2/5] 数据库迁移完成
echo.
pause

REM Step 2: 提示启动后端服务
echo ================================================================
echo [3/5] 启动后端服务
echo ================================================================
echo.
echo 请在新的终端窗口运行以下命令启动后端：
echo.
echo   python run.py
echo.
echo 或者按Ctrl+C退出，手动启动后端服务
echo.
pause

REM Step 3: 测试API接口
echo ================================================================
echo [4/5] 测试API接口
echo ================================================================
echo.
echo 开始测试API接口...
echo 确保后端服务已启动（默认: http://localhost:8000）
echo.
pause

python scripts\test_prediction_api.py
if errorlevel 1 (
    echo.
    echo [警告] API测试未全部通过
    echo 请检查：
    echo   1. 后端服务是否运行
    echo   2. 查看测试输出了解具体失败原因
    echo.
) else (
    echo.
    echo [3/5] API测试全部通过
    echo.
)

pause

REM Step 4: 提示前端启动
echo ================================================================
echo [5/5] 前端服务
echo ================================================================
echo.
echo 要启动前端服务，请在新的终端窗口运行：
echo.
echo   cd web
echo   npm run dev
echo.
echo 然后访问: http://localhost:3000
echo.
echo 测试步骤：
echo   1. 登录系统
echo   2. 进入 AI监测 ^> 趋势预测
echo   3. 点击 刷新数据 按钮
echo   4. 查看Network面板验证API调用
echo.

REM 完成
echo ================================================================
echo   部署完成！
echo ================================================================
echo.
echo 后续步骤：
echo   1. 查看文档: docs\device-data-model\阶段1核心完善-快速开始指南.md
echo   2. 查看实施总结: docs\device-data-model\阶段1核心完善-实施总结.md
echo   3. 开始使用AI预测管理功能
echo.
echo ================================================================
echo.

pause
