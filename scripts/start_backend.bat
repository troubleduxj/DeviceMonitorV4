@echo off
chcp 65001 >nul
echo ========================================
echo   启动后端服务
echo ========================================
echo.
echo 正在切换到项目目录...
cd /d "%~dp0.."
echo 当前目录: %cd%
echo.
echo 正在启动后端服务...
echo.
echo 【提示】看到以下信息表示启动成功：
echo   INFO:     Uvicorn running on http://0.0.0.0:8001
echo   INFO:     Application startup complete.
echo.
echo 【注意】
echo - 启动成功后，请勿关闭此窗口
echo - 按 Ctrl+C 可停止后端服务
echo.
echo ========================================
echo.

python run.py

