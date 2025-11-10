@echo off
echo ============================================================
echo   Organizing Root Directory Files
echo ============================================================
echo.

REM 创建目录
echo [1/3] Creating directories...
if not exist docs\archived mkdir docs\archived
if not exist docs\project mkdir docs\project
if not exist docs\system mkdir docs\system
if not exist scripts\archived mkdir scripts\archived
if not exist database\archived mkdir database\archived
echo   Created all directories
echo.

REM 移动文档
echo [2/3] Moving documents...
if exist AI-API审查总结-最终报告.md move AI-API审查总结-最终报告.md docs\device-data-model\
if exist FINAL_SUMMARY.md move FINAL_SUMMARY.md docs\device-data-model\
if exist README-AI-PREDICTION-COMPLETE.md move README-AI-PREDICTION-COMPLETE.md docs\device-data-model\
if exist CHANGELOG-AI-PREDICTION.md move CHANGELOG-AI-PREDICTION.md docs\device-data-model\
if exist final_diagnosis.md move final_diagnosis.md docs\archived\
if exist Java环境核查-最终总结.md move Java环境核查-最终总结.md docs\archived\
if exist Java环境核查结果-最终报告.md move Java环境核查结果-最终报告.md docs\archived\
if exist CRITICAL_MILESTONE.md move CRITICAL_MILESTONE.md docs\project\
if exist MIGRATION_PROGRESS.md move MIGRATION_PROGRESS.md docs\database\
if exist MIGRATION_STATUS.md move MIGRATION_STATUS.md docs\database\
if exist PERMISSION_FIX_REPORT.md move PERMISSION_FIX_REPORT.md docs\archived\
if exist VERIFICATION_GUIDE.md move VERIFICATION_GUIDE.md docs\project\
if exist project-status.md move project-status.md docs\project\
if exist 权限控制系统文档.md move 权限控制系统文档.md docs\system\
if exist 环境检查报告.md move 环境检查报告.md docs\archived\
echo   Documents moved
echo.

REM 移动脚本
echo [3/3] Moving archived scripts...
if exist check_admin_fields.py move check_admin_fields.py scripts\archived\
if exist check_admin_superuser.py move check_admin_superuser.py scripts\archived\
if exist diagnose_menu_issue.py move diagnose_menu_issue.py scripts\archived\
if exist fix_admin_role.py move fix_admin_role.py scripts\archived\
echo   Scripts moved
echo.

REM 移动SQL
if exist check_menu.sql move check_menu.sql database\archived\
if exist fix_admin_role.sql move fix_admin_role.sql database\archived\
if exist exclude_v3.txt move exclude_v3.txt docs\archived\

echo.
echo ============================================================
echo   Organization Complete
echo ============================================================
echo.
echo Files have been organized into:
echo   - docs/device-data-model/  (AI prediction docs)
echo   - docs/archived/           (old documents)
echo   - docs/project/            (project status docs)
echo   - docs/system/             (system docs)
echo   - scripts/archived/        (old scripts)
echo   - database/archived/       (old SQL files)
echo.
pause

