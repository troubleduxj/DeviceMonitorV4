@echo off
echo Cleaning up remaining root files...
echo.

REM 创建目录
if not exist docs\archived mkdir docs\archived
if not exist docs\device-data-model mkdir docs\device-data-model

REM 移动剩余文档
if exist "AI-API审查总结-最终报告.md" move /Y "AI-API审查总结-最终报告.md" docs\device-data-model\ 2>nul && echo Moved AI-API审查总结
if exist "Java环境核查-最终总结.md" move /Y "Java环境核查-最终总结.md" docs\archived\ 2>nul && echo Moved Java核查1
if exist "Java环境核查结果-最终报告.md" move /Y "Java环境核查结果-最终报告.md" docs\archived\ 2>nul && echo Moved Java核查2
if exist "权限控制系统文档.md" move /Y "权限控制系统文档.md" docs\archived\ 2>nul && echo Moved 权限文档
if exist "环境检查报告.md" move /Y "环境检查报告.md" docs\archived\ 2>nul && echo Moved 环境报告

echo.
echo Cleanup complete!
echo.
echo Final root directory files:
dir /b *.md 2>nul
echo.
pause

