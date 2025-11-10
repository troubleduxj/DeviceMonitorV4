# Android 环境检测脚本

Write-Host "`n=== Android 环境检测 ===`n" -ForegroundColor Cyan

# 检测 Android SDK 位置
$sdkPaths = @(
    "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk",
    "C:\Android\Sdk",
    "$env:LOCALAPPDATA\Android\Sdk"
)

$found = $false
foreach ($path in $sdkPaths) {
    if (Test-Path $path) {
        Write-Host "找到 Android SDK: $path" -ForegroundColor Green
        $found = $true
        $sdkPath = $path
        break
    }
}

if (-not $found) {
    Write-Host "未找到 Android SDK" -ForegroundColor Red
    Write-Host "`n请先安装 Android Studio:" -ForegroundColor Yellow
    Write-Host "下载: https://developer.android.com/studio`n" -ForegroundColor Yellow
    exit 1
}

# 检查环境变量
Write-Host "`n当前 ANDROID_HOME: $env:ANDROID_HOME" -ForegroundColor Cyan

if ($env:ANDROID_HOME) {
    Write-Host "环境变量已设置" -ForegroundColor Green
} else {
    Write-Host "环境变量未设置" -ForegroundColor Red
}

# 检查 ADB
Write-Host "`n检查 ADB..." -ForegroundColor Cyan
try {
    $version = adb --version 2>&1 | Select-Object -First 1
    Write-Host "ADB 可用: $version" -ForegroundColor Green
} catch {
    Write-Host "ADB 不可用" -ForegroundColor Red
}

Write-Host "`n"

