@echo off
echo 即将同步优先级1（核心业务）API到数据库
echo.
echo 这将创建约97个新的API记录
echo.
set /p confirm="确认继续? (yes/no): "
if /i "%confirm%"=="yes" (
    .venv\Scripts\python.exe sync_priority1_apis.py
) else (
    echo 已取消
)
pause
