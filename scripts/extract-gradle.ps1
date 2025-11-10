# 手动解压 Gradle 脚本

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Gradle 解压工具" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$gradleVersion = "gradle-8.14.3-bin"
$gradleBaseDir = "$env:USERPROFILE\.gradle\wrapper\dists\$gradleVersion"

Write-Host "[1/5] 搜索 Gradle ZIP 文件..." -ForegroundColor Yellow

# 查找所有可能的位置
$possibleDirs = @(
    "$gradleBaseDir\abc123",
    "$gradleBaseDir",
    "$env:USERPROFILE\Downloads"
)

$zipFile = $null
foreach ($dir in $possibleDirs) {
    $testPath = Join-Path $dir "$gradleVersion.zip"
    if (Test-Path $testPath) {
        $zipFile = $testPath
        Write-Host "  ✓ 找到: $zipFile" -ForegroundColor Green
        break
    }
}

if (-not $zipFile) {
    Write-Host "  ✗ 未找到 ZIP 文件" -ForegroundColor Red
    Write-Host ""
    Write-Host "请确认文件位置:" -ForegroundColor Yellow
    Write-Host "  1. $gradleBaseDir\abc123\$gradleVersion.zip" -ForegroundColor Gray
    Write-Host "  2. 或运行脚本时手动选择" -ForegroundColor Gray
    Write-Host ""
    
    # 打开文件选择对话框
    Add-Type -AssemblyName System.Windows.Forms
    $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $openFileDialog.Title = "选择 gradle-8.14.3-bin.zip"
    $openFileDialog.Filter = "ZIP 文件 (*.zip)|*.zip"
    $openFileDialog.InitialDirectory = $env:USERPROFILE
    
    $result = $openFileDialog.ShowDialog()
    if ($result -eq 'OK') {
        $zipFile = $openFileDialog.FileName
        Write-Host "  ✓ 已选择: $zipFile" -ForegroundColor Green
    } else {
        Write-Host "  已取消" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[2/5] 验证文件..." -ForegroundColor Yellow

$fileSize = [math]::Round((Get-Item $zipFile).Length / 1MB, 2)
Write-Host "  文件大小: $fileSize MB" -ForegroundColor Gray

if ($fileSize -lt 80 -or $fileSize -gt 150) {
    Write-Host "  ⚠ 警告：文件大小异常，可能不完整" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/5] 准备解压目录..." -ForegroundColor Yellow

# 使用文件的父目录作为目标
$targetParentDir = Split-Path $zipFile -Parent
$extractDir = $targetParentDir

Write-Host "  目标目录: $extractDir" -ForegroundColor Gray

# 检查是否已解压
$gradleExtracted = Join-Path $extractDir "gradle-8.14.3"
if (Test-Path $gradleExtracted) {
    Write-Host "  ⚠ 检测到已解压的 Gradle" -ForegroundColor Yellow
    $overwrite = Read-Host "  是否重新解压？(Y/N)"
    if ($overwrite -ne "Y" -and $overwrite -ne "y") {
        Write-Host "  跳过解压" -ForegroundColor Gray
    } else {
        Remove-Item $gradleExtracted -Recurse -Force
        Write-Host "  已删除旧文件" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[4/5] 解压 Gradle..." -ForegroundColor Yellow
Write-Host "  这可能需要 1-2 分钟，请稍候..." -ForegroundColor Gray

try {
    Expand-Archive -Path $zipFile -DestinationPath $extractDir -Force
    Write-Host "  ✓ 解压完成" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 解压失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[5/5] 创建标记文件..." -ForegroundColor Yellow

$okFile = "$zipFile.ok"
New-Item -Path $okFile -ItemType File -Force | Out-Null
Write-Host "  ✓ 已创建: $okFile" -ForegroundColor Green

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  ✓ 完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "解压位置:" -ForegroundColor White
Write-Host "  $gradleExtracted" -ForegroundColor Gray
Write-Host ""

Write-Host "验证安装:" -ForegroundColor White
$gradleBin = Join-Path $gradleExtracted "bin\gradle.bat"
if (Test-Path $gradleBin) {
    Write-Host "  ✓ Gradle 可执行文件存在" -ForegroundColor Green
    
    # 显示目录结构
    Write-Host ""
    Write-Host "目录结构:" -ForegroundColor White
    Get-ChildItem $extractDir | Select-Object Name, @{Name="Size";Expression={if($_.PSIsContainer){"<DIR>"}else{"{0:N2} MB" -f ($_.Length/1MB)}}} | Format-Table -AutoSize
} else {
    Write-Host "  ✗ 警告：未找到 Gradle 可执行文件" -ForegroundColor Red
}

Write-Host ""
Write-Host "下一步：在项目目录运行" -ForegroundColor Yellow
Write-Host "  cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile" -ForegroundColor Cyan
Write-Host "  npm run android" -ForegroundColor Cyan
Write-Host ""

Write-Host "按任意键退出..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

