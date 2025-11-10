# 检查 Java 安装状态

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host " Java 17 安装状态检查" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查安装程序
Write-Host "1. 安装程序下载状态" -ForegroundColor Yellow
Write-Host "-------------------------------------------"
$installerPath = "C:\Users\duxia\Downloads\microsoft-jdk-17-installer.msi"
if (Test-Path $installerPath) {
    $size = [math]::Round((Get-Item $installerPath).Length / 1MB, 2)
    Write-Host "状态: 已下载" -ForegroundColor Green
    Write-Host "位置: $installerPath"
    Write-Host "大小: $size MB"
} else {
    Write-Host "状态: 未下载" -ForegroundColor Red
}
Write-Host ""

# 2. 检查 Java 17 安装
Write-Host "2. Java 17 安装检测" -ForegroundColor Yellow
Write-Host "-------------------------------------------"

$javaInstalled = $false
$javaPath = $null

# 检查 Microsoft JDK
if (Test-Path "C:\Program Files\Microsoft") {
    $microsoftJdk = Get-ChildItem "C:\Program Files\Microsoft" -Filter "jdk-*" -Directory -ErrorAction SilentlyContinue
    if ($microsoftJdk) {
        Write-Host "找到 Microsoft JDK:" -ForegroundColor Green
        foreach ($jdk in $microsoftJdk) {
            Write-Host "  - $($jdk.FullName)" -ForegroundColor Cyan
            if ($jdk.Name -like "jdk-17*") {
                $javaInstalled = $true
                $javaPath = $jdk.FullName
            }
        }
    }
}

# 检查其他 Java 安装
if (Test-Path "C:\Program Files\Java") {
    $javaJdk = Get-ChildItem "C:\Program Files\Java" -Filter "jdk-*" -Directory -ErrorAction SilentlyContinue
    if ($javaJdk) {
        Write-Host "找到其他 JDK:" -ForegroundColor Yellow
        foreach ($jdk in $javaJdk) {
            Write-Host "  - $($jdk.FullName)" -ForegroundColor Gray
        }
    }
}

if ($javaInstalled) {
    Write-Host ""
    Write-Host "Java 17 安装路径: $javaPath" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "未检测到 Java 17 安装" -ForegroundColor Red
}
Write-Host ""

# 3. 检查当前 Java 版本
Write-Host "3. 当前系统 Java 版本" -ForegroundColor Yellow
Write-Host "-------------------------------------------"
try {
    $javaVersion = & java -version 2>&1
    if ($javaVersion -match "version") {
        Write-Host $javaVersion[0] -ForegroundColor Cyan
        
        if ($javaVersion[0] -match '"(\d+)') {
            $version = [int]$Matches[1]
            if ($version -ge 17) {
                Write-Host "状态: Java $version (满足要求)" -ForegroundColor Green
            } elseif ($version -ge 11) {
                Write-Host "状态: Java $version (可用，建议升级到 17)" -ForegroundColor Yellow
            } else {
                Write-Host "状态: Java $version (版本过低)" -ForegroundColor Red
            }
        }
    }
} catch {
    Write-Host "未配置或未找到 Java" -ForegroundColor Red
}
Write-Host ""

# 4. 环境变量
Write-Host "4. 环境变量" -ForegroundColor Yellow
Write-Host "-------------------------------------------"
if ($env:JAVA_HOME) {
    Write-Host "JAVA_HOME: $env:JAVA_HOME" -ForegroundColor Cyan
} else {
    Write-Host "JAVA_HOME: 未设置" -ForegroundColor Gray
}
Write-Host ""

# 5. 建议操作
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host " 建议操作" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $installerPath)) {
    Write-Host "需要下载 Java 17:" -ForegroundColor Yellow
    Write-Host "  运行: .\scripts\download-java17.ps1" -ForegroundColor White
}
elseif (-not $javaInstalled) {
    Write-Host "需要安装 Java 17:" -ForegroundColor Yellow
    Write-Host "  1. 双击: $installerPath" -ForegroundColor White
    Write-Host "  2. 按照向导完成安装" -ForegroundColor White
    Write-Host "  3. 重新运行此脚本检查" -ForegroundColor White
}
elseif ($javaInstalled) {
    Write-Host "Java 17 已安装，需要配置环境变量:" -ForegroundColor Yellow
    Write-Host "  运行: .\scripts\configure-java17.ps1" -ForegroundColor White
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

