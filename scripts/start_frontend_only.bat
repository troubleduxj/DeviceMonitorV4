@echo off
echo Starting frontend...
cd web
if exist "node_modules\.vite" (
    echo Cleaning Vite cache...
    rmdir /s /q "node_modules\.vite" 2>nul
)
start "Frontend Server" cmd /c "npm run dev"
cd ..
echo Frontend started!

