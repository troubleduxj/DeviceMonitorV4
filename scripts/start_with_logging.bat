@echo off
chcp 65001 > nul
echo ========================================
echo    设备监控系统 - 启动（带日志记录）
echo ========================================
echo.

REM 设置日志目录
set LOG_DIR=logs
if not exist "%LOG_DIR%" (
    echo 创建日志目录...
    mkdir "%LOG_DIR%"
)

REM 生成时间戳
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

REM 设置日志文件
set BACKEND_LOG=%LOG_DIR%\backend_%TIMESTAMP%.log
set FRONTEND_LOG=%LOG_DIR%\frontend_%TIMESTAMP%.log
set COMBINED_LOG=%LOG_DIR%\combined_%TIMESTAMP%.log

echo 📋 日志文件:
echo   - 后端: %BACKEND_LOG%
echo   - 前端: %FRONTEND_LOG%
echo   - 合并: %COMBINED_LOG%
echo.

echo ========================================
echo    步骤1: 启动后端服务
echo ========================================
echo.

REM 检查并清理旧的Python进程
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I /N "python.exe">nul
if "%ERRORLEVEL%"=="0" (
    echo ⚠️  检测到已运行的Python进程，正在清理...
    taskkill /F /IM python.exe /T > nul 2>&1
    timeout /t 2 /nobreak > nul
)

echo 🚀 启动后端服务并记录日志...
start "Backend Server" cmd /c "python run.py > %BACKEND_LOG% 2>&1"
echo ✅ 后端服务已启动
echo    日志文件: %BACKEND_LOG%
echo.

echo ⏳ 等待后端启动 (5秒)...
timeout /t 5 /nobreak > nul

echo ========================================
echo    步骤2: 启动前端服务
echo ========================================
echo.

REM 检查并清理旧的Node进程
tasklist /FI "IMAGENAME eq node.exe" 2>nul | find /I /N "node.exe">nul
if "%ERRORLEVEL%"=="0" (
    echo ⚠️  检测到已运行的Node进程，正在清理...
    taskkill /F /IM node.exe /T > nul 2>&1
    timeout /t 2 /nobreak > nul
)

echo 🧹 清理Vite缓存...
if exist "web\node_modules\.vite" (
    rmdir /s /q "web\node_modules\.vite" 2>nul
    echo ✅ Vite缓存已清理
) else (
    echo ℹ️  无需清理缓存
)
echo.

echo 🚀 启动前端服务并记录日志...
cd web
start "Frontend Server" cmd /c "npm run dev > ..\%FRONTEND_LOG% 2>&1"
cd ..
echo ✅ 前端服务已启动
echo    日志文件: %FRONTEND_LOG%
echo.

echo ========================================
echo    ✅ 启动完成！
echo ========================================
echo.
echo 📊 服务状态:
echo   - 后端: http://localhost:8001
echo   - 前端: http://localhost:3001
echo   - Mock控制面板: http://localhost:3001/mock-control.html
echo.
echo 📋 日志文件:
echo   - 后端日志: %BACKEND_LOG%
echo   - 前端日志: %FRONTEND_LOG%
echo.
echo 💡 使用以下命令分析日志:
echo    python scripts\analyze_logs.py
echo.
echo ⚠️  关闭本窗口不会停止服务
echo    使用 scripts\stop_dev.bat 停止服务
echo.
pause

