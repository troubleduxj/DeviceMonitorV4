@echo off
echo ============================================================
echo   AI Prediction - Complete Test Procedure
echo ============================================================
echo.

echo [1/4] Starting backend service in background...
start "DeviceMonitor-Backend" /min .venv\Scripts\python.exe run.py

echo [2/4] Waiting for backend to initialize (15 seconds)...
timeout /t 15 /nobreak

echo [3/4] Testing API endpoints...
echo.
.venv\Scripts\python.exe scripts\test_prediction_api.py

echo.
echo [4/4] Checking backend service status...
netstat -ano | findstr :8001

echo.
echo ============================================================
echo   Test Complete
echo ============================================================
echo.
echo Next Steps:
echo   1. If tests passed, start frontend: cd web ^&^& npm run dev
echo   2. Access: http://localhost:3000
echo   3. Navigate to: AI Monitor ^> Trend Prediction
echo   4. Click: Refresh Data button
echo.
pause

