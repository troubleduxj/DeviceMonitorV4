# 配置 Java 17 环境变量

Write-Host "配置 Java 17 环境变量..." -ForegroundColor Cyan
Write-Host ""

# 搜索 Java 17 安装
Write-Host "搜索 Java 17 安装..." -ForegroundColor Yellow

$searchPaths = @(
    "C:\Program Files\Microsoft\jdk-17*",
    "C:\Program Files\Java\jdk-17*", 
    "C:\Program Files\Eclipse Adoptium\jdk-17*",
    "C:\Program Files\OpenJDK\jdk-17*"
)

$java17Path = $null
foreach ($pattern in $searchPaths) {
    $found = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $java17Path = $found.FullName
        Write-Host "找到: $java17Path" -ForegroundColor Green
        break
    }
}

if (-not $java17Path) {
    Write-Host "未找到 Java 17 安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "请确认已完成安装，或手动指定路径" -ForegroundColor Yellow
    $java17Path = Read-Host "输入 Java 17 安装路径"
    
    if (-not (Test-Path $java17Path)) {
        Write-Host "路径无效" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "配置环境变量..." -ForegroundColor Yellow

# 设置当前会话
$env:JAVA_HOME = $java17Path
$env:PATH = "$java17Path\bin;$env:PATH"

Write-Host "当前会话已配置" -ForegroundColor Green
Write-Host "  JAVA_HOME = $java17Path" -ForegroundColor Gray
Write-Host ""

# 验证
Write-Host "验证安装..." -ForegroundColor Yellow
$javaExe = Join-Path $java17Path "bin\java.exe"
& $javaExe -version

Write-Host ""
Write-Host "配置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "现在可以运行构建：" -ForegroundColor Cyan
Write-Host "  cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile" -ForegroundColor White
Write-Host "  npm run android" -ForegroundColor White
Write-Host ""

$startBuild = Read-Host "是否立即开始构建？(Y/N)"
if ($startBuild -eq "Y" -or $startBuild -eq "y") {
    Write-Host ""
    cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile
    Remove-Item -Path "platforms/android/.gradle" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "platforms/tempPlugin" -Recurse -Force -ErrorAction SilentlyContinue
    npm run android
}

