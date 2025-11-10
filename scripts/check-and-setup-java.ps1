# Java 版本检查和配置脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Java 环境检查工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查当前 Java 版本
Write-Host "[1/4] 检查当前 Java 版本..." -ForegroundColor Yellow

try {
    $javaVersion = & java -version 2>&1
    Write-Host $javaVersion -ForegroundColor Gray
    
    if ($javaVersion -match "version `"(\d+)") {
        $majorVersion = [int]$Matches[1]
        Write-Host ""
        if ($majorVersion -ge 11) {
            Write-Host "✓ Java $majorVersion 符合要求（需要 11+）" -ForegroundColor Green
            Write-Host ""
            Write-Host "您可以直接运行构建：" -ForegroundColor Cyan
            Write-Host "  cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile" -ForegroundColor White
            Write-Host "  npm run android" -ForegroundColor White
            exit 0
        } else {
            Write-Host "✗ Java $majorVersion 版本过低（需要 11+）" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "✗ 未找到 Java 或无法执行" -ForegroundColor Red
}

Write-Host ""
Write-Host "[2/4] 搜索已安装的 Java 17..." -ForegroundColor Yellow

# 搜索可能的 Java 17 安装位置
$possiblePaths = @(
    "C:\Program Files\Java\jdk-17*",
    "C:\Program Files\Java\jdk17*",
    "C:\Program Files\Eclipse Adoptium\jdk-17*",
    "C:\Program Files\OpenJDK\jdk-17*",
    "C:\Program Files\AdoptOpenJDK\jdk-17*",
    "C:\Program Files\Zulu\zulu-17*"
)

$javaHome = $null
foreach ($pattern in $possiblePaths) {
    $found = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $javaHome = $found.FullName
        Write-Host "  ✓ 找到: $javaHome" -ForegroundColor Green
        break
    }
}

if (-not $javaHome) {
    Write-Host "  ✗ 未找到 Java 17 安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "  请安装 Java 17" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "下载链接（选择一个）：" -ForegroundColor White
    Write-Host ""
    Write-Host "1. Oracle JDK（官方）：" -ForegroundColor Cyan
    Write-Host "   https://www.oracle.com/java/technologies/downloads/#java17" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Adoptium（开源，推荐）：" -ForegroundColor Cyan
    Write-Host "   https://adoptium.net/temurin/releases/?version=17" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Microsoft OpenJDK：" -ForegroundColor Cyan
    Write-Host "   https://www.microsoft.com/openjdk" -ForegroundColor Gray
    Write-Host ""
    Write-Host "安装完成后，重新运行此脚本" -ForegroundColor Yellow
    Write-Host ""
    
    # 询问是否打开下载页面
    $openBrowser = Read-Host "是否在浏览器中打开下载页面？(Y/N)"
    if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
        Start-Process "https://adoptium.net/temurin/releases/?version=17"
    }
    
    exit 1
}

Write-Host ""
Write-Host "[3/4] 配置环境变量..." -ForegroundColor Yellow

# 设置当前会话的环境变量
$env:JAVA_HOME = $javaHome
$env:PATH = "$javaHome\bin;$env:PATH"

Write-Host "  ✓ JAVA_HOME = $javaHome" -ForegroundColor Green

# 尝试设置系统环境变量（可能需要管理员权限）
try {
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome, "Machine")
    Write-Host "  ✓ 系统环境变量已设置" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ 无法设置系统环境变量（需要管理员权限）" -ForegroundColor Yellow
    Write-Host "    当前会话已生效，但重启后需要手动设置" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[4/4] 验证配置..." -ForegroundColor Yellow

try {
    $newVersion = & "$javaHome\bin\java.exe" -version 2>&1
    Write-Host $newVersion -ForegroundColor Gray
    Write-Host ""
    Write-Host "  ✓ Java 17 配置成功！" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 验证失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ 配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：在此 PowerShell 窗口中运行构建" -ForegroundColor Yellow
Write-Host ""
Write-Host "cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile" -ForegroundColor Cyan
Write-Host "npm run android" -ForegroundColor Cyan
Write-Host ""
Write-Host "注意：如果关闭此窗口，需要重新运行此脚本配置环境" -ForegroundColor Gray
Write-Host "或手动设置系统环境变量（见文档）" -ForegroundColor Gray
Write-Host ""

# 询问是否立即开始构建
$startBuild = Read-Host "是否立即开始构建？(Y/N)"
if ($startBuild -eq "Y" -or $startBuild -eq "y") {
    Write-Host ""
    Write-Host "开始构建..." -ForegroundColor Cyan
    Set-Location "D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile"
    
    # 清理
    Write-Host "清理旧文件..." -ForegroundColor Yellow
    Remove-Item -Path "platforms/android/.gradle" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "platforms/tempPlugin" -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host ""
    npm run android
}

