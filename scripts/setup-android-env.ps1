# Android 环境配置脚本
# 用于快速设置 ANDROID_HOME 环境变量

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Android 环境配置脚本" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 检查是否以管理员身份运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  警告: 未以管理员身份运行" -ForegroundColor Yellow
    Write-Host "   建议右键 PowerShell → 以管理员身份运行，以便永久设置环境变量`n" -ForegroundColor Yellow
}

# 1. 检测 Android SDK 位置
Write-Host "步骤 1: 检测 Android SDK..." -ForegroundColor Green

$possiblePaths = @(
    "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk",
    "C:\Android\Sdk",
    "$env:LOCALAPPDATA\Android\Sdk",
    "$env:ProgramFiles\Android\Sdk",
    "${env:ProgramFiles(x86)}\Android\Sdk"
)

$androidHome = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $androidHome = $path
        Write-Host "✓ 找到 Android SDK: $path" -ForegroundColor Green
        break
    }
}

if (-not $androidHome) {
    Write-Host "✗ 未找到 Android SDK" -ForegroundColor Red
    Write-Host "`n请先安装 Android Studio:" -ForegroundColor Yellow
    Write-Host "  下载地址: https://developer.android.com/studio`n" -ForegroundColor Yellow
    Write-Host "安装完成后重新运行此脚本`n" -ForegroundColor Yellow
    exit 1
}

# 2. 检查必需的目录
Write-Host "`n步骤 2: 检查 SDK 组件..." -ForegroundColor Green

$requiredDirs = @(
    "platform-tools",
    "build-tools",
    "platforms"
)

$allExist = $true
foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $androidHome $dir
    if (Test-Path $fullPath) {
        Write-Host "✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "✗ $dir (缺失)" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Host "`n⚠️  警告: 某些 SDK 组件缺失" -ForegroundColor Yellow
    Write-Host "请在 Android Studio 中安装:" -ForegroundColor Yellow
    Write-Host "  Tools → SDK Manager → SDK Tools" -ForegroundColor Yellow
    Write-Host "  - Android SDK Platform-Tools" -ForegroundColor Yellow
    Write-Host "  - Android SDK Build-Tools" -ForegroundColor Yellow
    Write-Host "`n继续配置环境变量..." -ForegroundColor Yellow
}

# 3. 设置环境变量
Write-Host "`n步骤 3: 配置环境变量..." -ForegroundColor Green

if ($isAdmin) {
    # 永久设置（系统级）
    Write-Host "设置 ANDROID_HOME (系统级)..." -ForegroundColor Cyan
    [System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidHome, 'Machine')
    
    # 添加到 Path
    Write-Host "添加到 Path (系统级)..." -ForegroundColor Cyan
    $currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
    
    $pathsToAdd = @(
        "$androidHome\platform-tools",
        "$androidHome\emulator",
        "$androidHome\tools",
        "$androidHome\tools\bin"
    )
    
    $pathUpdated = $false
    foreach ($path in $pathsToAdd) {
        if ($currentPath -notlike "*$path*") {
            $currentPath += ";$path"
            $pathUpdated = $true
            Write-Host "  + $path" -ForegroundColor Gray
        }
    }
    
    if ($pathUpdated) {
        [System.Environment]::SetEnvironmentVariable('Path', $currentPath, 'Machine')
        Write-Host "✓ Path 已更新" -ForegroundColor Green
    } else {
        Write-Host "✓ Path 已包含所有必需路径" -ForegroundColor Green
    }
    
    Write-Host "`n✓ 环境变量已永久设置" -ForegroundColor Green
    Write-Host "⚠️  请重启 PowerShell 使配置生效`n" -ForegroundColor Yellow
    
} else {
    # 临时设置（当前会话）
    Write-Host "设置 ANDROID_HOME (当前会话)..." -ForegroundColor Cyan
    $env:ANDROID_HOME = $androidHome
    
    Write-Host "添加到 Path (当前会话)..." -ForegroundColor Cyan
    $env:Path += ";$androidHome\platform-tools"
    $env:Path += ";$androidHome\emulator"
    $env:Path += ";$androidHome\tools"
    $env:Path += ";$androidHome\tools\bin"
    
    Write-Host "✓ 环境变量已设置（当前会话）" -ForegroundColor Green
    Write-Host "`n⚠️  警告: 这是临时设置，关闭 PowerShell 后失效" -ForegroundColor Yellow
    Write-Host "   要永久设置，请以管理员身份重新运行此脚本`n" -ForegroundColor Yellow
}

# 4. 验证配置
Write-Host "`n步骤 4: 验证配置..." -ForegroundColor Green

# 刷新当前会话的环境变量（如果是管理员模式）
if ($isAdmin) {
    $env:ANDROID_HOME = [System.Environment]::GetEnvironmentVariable('ANDROID_HOME', 'Machine')
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
}

Write-Host "ANDROID_HOME = $env:ANDROID_HOME" -ForegroundColor Cyan

# 检查 adb
Write-Host "`n检查 ADB..." -ForegroundColor Cyan
try {
    $adbVersion = & adb --version 2>&1 | Select-Object -First 1
    Write-Host "✓ ADB: $adbVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ADB 未找到" -ForegroundColor Red
    Write-Host "  请重启 PowerShell 后重试" -ForegroundColor Yellow
}

# 检查 Java
Write-Host "`n检查 Java..." -ForegroundColor Cyan
try {
    $javaVersion = & javac -version 2>&1
    Write-Host "✓ Java: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Java 未找到" -ForegroundColor Red
    Write-Host "  Android Studio 会自带 JDK，通常在:" -ForegroundColor Yellow
    Write-Host "  $env:ProgramFiles\Android\Android Studio\jbr" -ForegroundColor Yellow
}

# 5. 下一步提示
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   配置完成！" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($isAdmin) {
    Write-Host "下一步操作:" -ForegroundColor Yellow
    Write-Host "1. 重启 PowerShell（重要！）" -ForegroundColor White
    Write-Host "2. 进入项目目录: cd mobile" -ForegroundColor White
    Write-Host "3. 运行诊断: npx ns doctor" -ForegroundColor White
    Write-Host "4. 创建 AVD（在 Android Studio 中）" -ForegroundColor White
    Write-Host "5. 运行应用: pnpm android`n" -ForegroundColor White
} else {
    Write-Host "下一步操作:" -ForegroundColor Yellow
    Write-Host "1. 以管理员身份重新运行此脚本（永久设置）" -ForegroundColor White
    Write-Host "   或者" -ForegroundColor White
    Write-Host "2. 在当前会话继续:" -ForegroundColor White
    Write-Host "   - cd mobile" -ForegroundColor White
    Write-Host "   - npx ns doctor" -ForegroundColor White
    Write-Host "   - pnpm android`n" -ForegroundColor White
}

Write-Host "详细配置指南: docs\Android环境配置指南-Windows.md`n" -ForegroundColor Gray

