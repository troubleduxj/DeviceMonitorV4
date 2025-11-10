@echo off
echo 正在清理进程...
taskkill /F /IM node.exe /T 2>nul
taskkill /F /IM python.exe /T 2>nul
echo 清理完成！

