@echo off
chcp 65001 > nul
echo ========================================
echo   启动前端服务
echo ========================================
echo.

echo [1/2] 清理Vite缓存...
cd web
if exist "node_modules\.vite" (
    rmdir /S /Q "node_modules\.vite"
    echo ✅ Vite缓存已清理
) else (
    echo ℹ️ 无需清理缓存
)

echo.
echo [2/2] 启动前端 (端口: 3001)...
echo.
npm run dev

pause

