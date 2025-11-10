@echo off
chcp 65001 >nul
echo ========================================
echo   创建Mock功能快捷方式
echo ========================================
echo.

set DESKTOP=%USERPROFILE%\Desktop
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%~dp0..

echo 正在创建桌面快捷方式...
echo.

REM 创建"安装Mock功能"快捷方式
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\1-安装Mock功能.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%install_mock_feature.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%PROJECT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "安装Mock功能数据库表" >> CreateShortcut.vbs
echo oLink.IconLocation = "shell32.dll,165" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs
echo ✅ 已创建：1-安装Mock功能.lnk

REM 创建"启动后端"快捷方式
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\2-启动后端服务.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%start_backend.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%PROJECT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "启动DeviceMonitor后端服务" >> CreateShortcut.vbs
echo oLink.IconLocation = "shell32.dll,77" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs
echo ✅ 已创建：2-启动后端服务.lnk

REM 创建"权限初始化"快捷方式
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\3-初始化Mock权限.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%init_mock_permissions.html" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%PROJECT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "初始化Mock功能按钮权限" >> CreateShortcut.vbs
echo oLink.IconLocation = "shell32.dll,13" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs
echo ✅ 已创建：3-初始化Mock权限.lnk

echo.
echo ========================================
echo   🎉 快捷方式创建完成！
echo ========================================
echo.
echo 已在桌面创建3个快捷方式：
echo   1-安装Mock功能.lnk
echo   2-启动后端服务.lnk
echo   3-初始化Mock权限.lnk
echo.
echo 请按顺序双击运行这3个快捷方式！
echo.
pause

