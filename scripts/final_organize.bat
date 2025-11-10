@echo off
echo ============================================================
echo   Final Root Directory Organization
echo ============================================================
echo.

REM 创建归档目录
echo [1/4] Creating archive directories...
if not exist docs\archived mkdir docs\archived
if not exist docs\project mkdir docs\project
echo   Done
echo.

REM 移动已归档的文档
echo [2/4] Moving completed project docs to docs/device-data-model/...
if exist AI-API审查总结-最终报告.md move /Y "AI-API审查总结-最终报告.md" docs\device-data-model\ 2>nul
if exist README-STAGE1-COMPLETE.md move /Y README-STAGE1-COMPLETE.md docs\device-data-model\ 2>nul
if exist WORK_COMPLETED.md move /Y WORK_COMPLETED.md docs\device-data-model\ 2>nul
echo   Done
echo.

REM 移动旧文档到归档
echo [3/4] Moving old docs to docs/archived/...
if exist "Java环境核查-最终总结.md" move /Y "Java环境核查-最终总结.md" docs\archived\ 2>nul
if exist "Java环境核查结果-最终报告.md" move /Y "Java环境核查结果-最终报告.md" docs\archived\ 2>nul
if exist "权限控制系统文档.md" move /Y "权限控制系统文档.md" docs\archived\ 2>nul
if exist "环境检查报告.md" move /Y "环境检查报告.md" docs\archived\ 2>nul
echo   Done
echo.

REM 移动迁移文档到数据库目录
echo [4/4] Moving migration docs to docs/project/...
if exist MIGRATION_PROGRESS.md move /Y MIGRATION_PROGRESS.md docs\project\ 2>nul
if exist MIGRATION_STATUS.md move /Y MIGRATION_STATUS.md docs\project\ 2>nul
echo   Done
echo.

echo ============================================================
echo   Organization Complete
echo ============================================================
echo.
echo Root directory files have been organized:
echo   - Project completion docs  -^> docs/device-data-model/
echo   - Old docs                 -^> docs/archived/
echo   - Migration docs           -^> docs/project/
echo.
echo Remaining in root (必须保留):
echo   - README.md                (项目主文档)
echo   - README-TypeScript迁移总结.md (重要文档)
echo   - run.py                   (启动脚本)
echo   - aerich_config.py         (数据库配置)
echo   - 配置文件 (.ini, .json, .yml等)
echo.
pause

