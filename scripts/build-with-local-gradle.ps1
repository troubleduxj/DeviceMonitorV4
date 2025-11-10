# 使用本地 Gradle 进行构建

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  使用本地 Gradle 构建" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Gradle ZIP 是否存在
$gradleZip = "C:\Users\duxia\.gradle\wrapper\dists\gradle-8.14.3-bin\abc123\gradle-8.14.3-bin.zip"

Write-Host "[1/4] 检查 Gradle ZIP 文件..." -ForegroundColor Yellow
if (Test-Path $gradleZip) {
    $fileSize = [math]::Round((Get-Item $gradleZip).Length / 1MB, 2)
    Write-Host "  ✓ 找到文件 ($fileSize MB)" -ForegroundColor Green
    
    # 解压
    Write-Host ""
    Write-Host "[2/4] 解压 Gradle..." -ForegroundColor Yellow
    $extractPath = "C:\Users\duxia\.gradle\wrapper\dists\gradle-8.14.3-bin\abc123"
    $gradleDir = Join-Path $extractPath "gradle-8.14.3"
    
    if (Test-Path $gradleDir) {
        Write-Host "  ✓ Gradle 已解压" -ForegroundColor Green
    } else {
        Write-Host "  正在解压（请稍候）..." -ForegroundColor Gray
        try {
            Expand-Archive -Path $gradleZip -DestinationPath $extractPath -Force
            New-Item -Path "$gradleZip.ok" -ItemType File -Force | Out-Null
            Write-Host "  ✓ 解压完成" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ 解压失败: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "  请手动解压 $gradleZip 到 $extractPath" -ForegroundColor Yellow
            exit 1
        }
    }
    
    # 设置环境变量
    Write-Host ""
    Write-Host "[3/4] 配置环境变量..." -ForegroundColor Yellow
    $env:GRADLE_USER_HOME = "C:\Users\duxia\.gradle"
    Write-Host "  ✓ GRADLE_USER_HOME = $env:GRADLE_USER_HOME" -ForegroundColor Green
    
    # 进入项目目录
    Write-Host ""
    Write-Host "[4/4] 开始构建..." -ForegroundColor Yellow
    Set-Location "D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile"
    
    Write-Host "  执行: npm run android" -ForegroundColor Gray
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 运行构建
    npm run android
    
} else {
    Write-Host "  ✗ 未找到文件: $gradleZip" -ForegroundColor Red
    Write-Host ""
    Write-Host "请确认文件位置，或从以下地址下载：" -ForegroundColor Yellow
    Write-Host "  https://mirrors.cloud.tencent.com/gradle/gradle-8.14.3-bin.zip" -ForegroundColor Cyan
    exit 1
}

