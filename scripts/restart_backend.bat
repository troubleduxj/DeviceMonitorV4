@echo off
echo [RESTART] Restarting backend service...

REM Stop existing python process on port 8001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    taskkill /F /PID %%a 2>nul
)

echo [WAIT] Waiting for port release...
timeout /t 3 /nobreak > nul

echo [START] Starting backend service...
start "DeviceMonitor Backend" /min .venv\Scripts\python.exe run.py

echo [WAIT] Waiting for service to start...
timeout /t 8 /nobreak > nul

echo [DONE] Backend service restarted
echo.
echo [INFO] Service running on http://localhost:8001
echo [INFO] Check http://localhost:8001/docs for API documentation
echo.

