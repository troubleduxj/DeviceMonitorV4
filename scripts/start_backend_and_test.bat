@echo off
echo ============================================================
echo   AI Prediction Management - Start and Test
echo ============================================================
echo.

echo [STEP 1] Stopping existing backend service...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    taskkill /F /PID %%a 2>nul
)

echo [STEP 2] Waiting for port release...
timeout /t 5 /nobreak > nul

echo [STEP 3] Starting backend service...
start "DeviceMonitor Backend" .venv\Scripts\python.exe run.py

echo [STEP 4] Waiting for backend to initialize...
timeout /t 12 /nobreak > nul

echo [STEP 5] Testing API endpoints...
echo.
.venv\Scripts\python.exe scripts\test_prediction_api.py

echo.
echo ============================================================
echo   Test Complete
echo ============================================================
echo.
pause

