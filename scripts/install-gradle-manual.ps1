# 手动安装 Gradle 辅助脚本
# 使用方法：在 PowerShell 中运行此脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Gradle 8.14.3 手动安装向导" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 定义目标目录
$gradleDir = "$env:USERPROFILE\.gradle\wrapper\dists\gradle-8.14.3-bin"
$subDirName = "abc123"  # 随机子目录名
$targetDir = Join-Path $gradleDir $subDirName

Write-Host "[步骤 1/4] 检查目标目录..." -ForegroundColor Yellow
if (-not (Test-Path $targetDir)) {
    Write-Host "  创建目录: $targetDir" -ForegroundColor Gray
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    Write-Host "  ✓ 目录已创建" -ForegroundColor Green
} else {
    Write-Host "  ✓ 目录已存在" -ForegroundColor Green
}

Write-Host ""
Write-Host "[步骤 2/4] 请选择您下载的 gradle-8.14.3-bin.zip 文件..." -ForegroundColor Yellow

# 2. 打开文件选择对话框
Add-Type -AssemblyName System.Windows.Forms
$openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
$openFileDialog.Title = "选择 gradle-8.14.3-bin.zip"
$openFileDialog.Filter = "ZIP 文件 (*.zip)|*.zip|所有文件 (*.*)|*.*"
$openFileDialog.InitialDirectory = [Environment]::GetFolderPath("Downloads")

$result = $openFileDialog.ShowDialog()

if ($result -eq 'OK') {
    $sourceZip = $openFileDialog.FileName
    Write-Host "  已选择: $sourceZip" -ForegroundColor Gray
    
    # 验证文件名
    $fileName = [System.IO.Path]::GetFileName($sourceZip)
    if ($fileName -ne "gradle-8.14.3-bin.zip") {
        Write-Host "  ⚠ 警告：文件名不是 gradle-8.14.3-bin.zip，但仍会继续..." -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "[步骤 3/4] 复制文件到目标位置..." -ForegroundColor Yellow
    
    # 3. 复制文件
    $destZip = Join-Path $targetDir "gradle-8.14.3-bin.zip"
    
    if (Test-Path $destZip) {
        Write-Host "  目标位置已存在文件，是否覆盖？" -ForegroundColor Yellow
        $overwrite = Read-Host "  输入 Y 继续，其他键取消"
        if ($overwrite -ne "Y" -and $overwrite -ne "y") {
            Write-Host "  已取消" -ForegroundColor Red
            exit
        }
    }
    
    Copy-Item -Path $sourceZip -Destination $destZip -Force
    Write-Host "  ✓ 文件已复制" -ForegroundColor Green
    
    # 验证文件大小
    $fileSize = (Get-Item $destZip).Length / 1MB
    Write-Host "  文件大小: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "[步骤 4/4] 打开目标目录确认..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    explorer.exe $targetDir
    Write-Host "  ✓ 文件资源管理器已打开" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  ✓ 安装完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "文件位置：" -ForegroundColor White
    Write-Host "  $destZip" -ForegroundColor Gray
    Write-Host ""
    Write-Host "下一步：" -ForegroundColor White
    Write-Host "  1. 确认文件在正确位置" -ForegroundColor Gray
    Write-Host "  2. 在项目目录运行：npm run android" -ForegroundColor Gray
    Write-Host ""
    
} else {
    Write-Host "  已取消" -ForegroundColor Red
    Write-Host ""
    Write-Host "如果您想手动操作：" -ForegroundColor Yellow
    Write-Host "  1. 打开目录：$targetDir" -ForegroundColor Gray
    Write-Host "  2. 复制 gradle-8.14.3-bin.zip 到此目录" -ForegroundColor Gray
    Write-Host ""
    Write-Host "是否现在打开目标目录？(Y/N)" -ForegroundColor Yellow
    $openDir = Read-Host
    if ($openDir -eq "Y" -or $openDir -eq "y") {
        explorer.exe $targetDir
    }
}

Write-Host "按任意键退出..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

