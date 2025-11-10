@echo off
echo ============================================================
echo   Restart Backend with Unified API Prefix
echo ============================================================
echo.

echo [1/4] Stopping backend...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak > nul

echo [2/4] Starting backend with unified prefix...
start "DeviceMonitor-Backend-Unified" .venv\Scripts\python.exe run.py

echo [3/4] Waiting for initialization (15 seconds)...
timeout /t 15 /nobreak

echo [4/4] Testing unified API...
echo.
.venv\Scripts\python.exe -c "import httpx, asyncio; async def test(): async with httpx.AsyncClient(timeout=10) as c: r = await c.get('http://localhost:8001/api/v2/ai/predictions/tasks'); print(f'Status: {r.status_code}'); print(f'Unified prefix working!' if r.status_code in [200,400] else 'Check logs'); asyncio.run(test())"

echo.
echo ============================================================
echo   Backend Restarted with Unified Prefix
echo ============================================================
echo.
echo API Documentation: http://localhost:8001/docs
echo Search for: "AI预测" to see unified routes
echo.
echo All AI APIs now under: /api/v2/ai/
echo   - /api/v2/ai/predictions/tasks/
echo   - /api/v2/ai/predictions/execute/
echo   - /api/v2/ai/predictions/analytics/
echo   - /api/v2/ai/health-scores/calculate/
echo   - /api/v2/ai/health-scores/records/
echo.
pause

