# 下载 Java 17 安装程序

Write-Host "下载 Java 17 (Microsoft OpenJDK)..." -ForegroundColor Cyan
Write-Host ""

$url = "https://aka.ms/download-jdk/microsoft-jdk-17.0.13-windows-x64.msi"
$output = "$env:USERPROFILE\Downloads\microsoft-jdk-17-installer.msi"

Write-Host "下载地址: $url" -ForegroundColor Gray
Write-Host "保存位置: $output" -ForegroundColor Gray
Write-Host ""
Write-Host "正在下载... (约 180 MB)" -ForegroundColor Yellow
Write-Host ""

try {
    Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
    
    $fileSize = [math]::Round((Get-Item $output).Length / 1MB, 2)
    Write-Host "下载完成！文件大小: $fileSize MB" -ForegroundColor Green
    Write-Host ""
    Write-Host "安装程序位置：" -ForegroundColor White
    Write-Host "$output" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "正在打开安装程序..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    
    # 打开安装程序
    Start-Process $output
    
    Write-Host ""
    Write-Host "请按照安装向导完成安装：" -ForegroundColor Yellow
    Write-Host "  1. 接受许可协议" -ForegroundColor White
    Write-Host "  2. 使用默认安装路径" -ForegroundColor White
    Write-Host "  3. 点击 Install" -ForegroundColor White
    Write-Host "  4. 完成安装" -ForegroundColor White
    Write-Host ""
    Write-Host "安装完成后，运行：" -ForegroundColor Cyan
    Write-Host "  .\scripts\configure-java17.ps1" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "下载失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动下载：" -ForegroundColor Yellow
    Write-Host "  https://www.microsoft.com/openjdk" -ForegroundColor Cyan
    Write-Host ""
    
    $openBrowser = Read-Host "是否在浏览器中打开下载页面？(Y/N)"
    if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
        Start-Process "https://www.microsoft.com/openjdk"
    }
}

