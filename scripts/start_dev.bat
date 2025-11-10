@echo off
chcp 65001 > nul

echo ========================================
echo   设备监控系统 - 开发环境启动
echo ========================================
echo.

REM 设置项目根目录
SET PROJECT_ROOT=%~dp0..

echo [1/3] 清理前端缓存...
echo.
cd /d %PROJECT_ROOT%\web
if exist node_modules\.vite (
    rmdir /s /q node_modules\.vite
    echo ✅ Vite缓存已清理
) else (
    echo ℹ️ 未发现Vite缓存
)
echo.

echo [2/3] 启动后端服务...
echo.
start "后端服务 (Backend)" cmd /k "cd /d %PROJECT_ROOT% && .\.venv\Scripts\activate && python run.py"

echo [3/3] 启动前端服务...
echo.
start "前端服务 (Frontend)" cmd /k "cd /d %PROJECT_ROOT%\web && npm run dev"

echo.
echo ========================================
echo   ✅ 服务启动命令已执行
echo ========================================
echo.
echo 🚀 后端服务: http://localhost:8001
echo 🌐 前端服务: http://localhost:3000
echo.
echo 💡 提示:
echo   - 两个服务会在单独的窗口中运行
echo   - 关闭窗口即可停止对应服务
echo   - 如果启动失败，请检查端口是否被占用
echo.
pause

