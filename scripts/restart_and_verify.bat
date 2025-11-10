@echo off
echo ============================================================
echo   Restart Backend and Verify New APIs
echo ============================================================
echo.

echo [1/3] Stopping backend service...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    taskkill /F /PID %%a 2>nul
)

echo [2/3] Waiting for port release...
timeout /t 3 /nobreak > nul

echo [3/3] Starting backend with new APIs...
start "DeviceMonitor-Backend" .venv\Scripts\python.exe run.py

echo.
echo Waiting for backend to initialize (12 seconds)...
timeout /t 12 /nobreak

echo.
echo ============================================================
echo   Backend Restarted
echo ============================================================
echo.
echo Check API docs: http://localhost:8001/docs
echo Look for new endpoints:
echo   - GET /api/v2/ai-monitor/risk-assessment
echo   - GET /api/v2/ai-monitor/health-trend
echo   - GET /api/v2/ai-monitor/prediction-report
echo.
pause

