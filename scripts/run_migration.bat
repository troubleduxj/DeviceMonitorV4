@echo off
REM 执行数据库迁移脚本
echo.
echo ============================================================
echo   执行AI预测管理功能数据库迁移
echo ============================================================
echo.

REM 激活虚拟环境并执行
call .venv\Scripts\activate.bat
python database\migrations\ai-module\execute_003_migration_fix.py

echo.
echo ============================================================
echo   迁移执行完成
echo ============================================================
echo.
pause

