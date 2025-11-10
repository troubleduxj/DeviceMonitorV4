@echo off
chcp 65001 > nul
echo ========================================
echo   DeviceMonitor 服务启动脚本
echo ========================================
echo.

echo [1/3] 激活Python虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

echo.
echo [2/3] 启动后端服务 (端口: 8001)...
echo 正在后台启动...
start "DeviceMonitor后端" /MIN python run.py
echo ✅ 后端服务已启动

echo.
echo [3/3] 等待5秒，然后启动前端...
timeout /t 5 /nobreak > nul

echo 清理Vite缓存...
if exist "web\node_modules\.vite" (
    rmdir /S /Q "web\node_modules\.vite"
)

echo 启动前端服务 (端口: 3001)...
cd web
start "DeviceMonitor前端" /MIN npm run dev
cd ..

echo.
echo ========================================
echo ✅ 服务启动完成！
echo ========================================
echo.
echo 📍 后端地址: http://localhost:8001
echo 📍 前端地址: http://localhost:3001
echo.
echo 💡 提示: 两个服务窗口已最小化到任务栏
echo.
pause

