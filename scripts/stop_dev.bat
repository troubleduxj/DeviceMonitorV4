@echo off
chcp 65001 > nul

echo ========================================
echo   设备监控系统 - 停止开发服务
echo ========================================
echo.

echo 正在停止所有Python和Node.js进程...
echo.

REM 停止Python进程
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" ^| find "python.exe"') do (
    echo 停止Python进程: %%i
    taskkill /F /PID %%i >nul 2>&1
)

REM 停止Node进程
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq node.exe" ^| find "node.exe"') do (
    echo 停止Node进程: %%i
    taskkill /F /PID %%i >nul 2>&1
)

echo.
echo ========================================
echo   ✅ 服务已停止
echo ========================================
echo.
pause

