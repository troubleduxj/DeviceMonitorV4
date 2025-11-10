# Java 17 自动安装脚本
# 使用 Microsoft OpenJDK（官方推荐）

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Java 17 自动安装向导" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 第 1 步：检查现有安装
Write-Host "[1/6] 检查现有 Java 安装..." -ForegroundColor Yellow
Write-Host ""

$java17Found = $false
$java17Path = $null

# 搜索已安装的 Java 17
$searchPaths = @(
    "C:\Program Files\Microsoft\jdk-17*",
    "C:\Program Files\Java\jdk-17*",
    "C:\Program Files\Eclipse Adoptium\jdk-17*",
    "C:\Program Files\OpenJDK\jdk-17*"
)

foreach ($pattern in $searchPaths) {
    $found = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found -and (Test-Path $found.FullName)) {
        $java17Path = $found.FullName
        $java17Found = $true
        Write-Host "  找到 Java 17: $java17Path" -ForegroundColor Green
        break
    }
}

if ($java17Found) {
    Write-Host ""
    Write-Host "  Java 17 已安装，跳过下载" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "  未找到 Java 17，准备下载..." -ForegroundColor Yellow
    Write-Host ""
    
    # 第 2 步：下载 Java 17
    Write-Host "[2/6] 下载 Java 17..." -ForegroundColor Yellow
    Write-Host ""
    
    # 使用 Microsoft OpenJDK
    $downloadUrl = "https://aka.ms/download-jdk/microsoft-jdk-17.0.13-windows-x64.msi"
    $installerPath = "$env:TEMP\microsoft-jdk-17-installer.msi"
    
    Write-Host "  下载地址: $downloadUrl" -ForegroundColor Gray
    Write-Host "  保存位置: $installerPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  正在下载... (约 180 MB，可能需要 2-5 分钟)" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        # 显示进度的下载
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($downloadUrl, $installerPath)
        
        $fileSize = [math]::Round((Get-Item $installerPath).Length / 1MB, 2)
        Write-Host "  下载完成！文件大小: $fileSize MB" -ForegroundColor Green
        Write-Host ""
    } catch {
        Write-Host "  下载失败: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "  请手动下载：" -ForegroundColor Yellow
        Write-Host "  1. 打开: https://www.microsoft.com/openjdk" -ForegroundColor White
        Write-Host "  2. 下载 Java 17 (Windows x64 MSI)" -ForegroundColor White
        Write-Host "  3. 运行安装程序" -ForegroundColor White
        exit 1
    }
    
    # 第 3 步：安装 Java 17
    Write-Host "[3/6] 安装 Java 17..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  正在启动安装程序..." -ForegroundColor Gray
    Write-Host "  请在安装向导中：" -ForegroundColor Cyan
    Write-Host "    ☑ 接受许可协议" -ForegroundColor White
    Write-Host "    ☑ 选择默认安装路径" -ForegroundColor White
    Write-Host "    ☑ 完成安装" -ForegroundColor White
    Write-Host ""
    
    try {
        # 静默安装（需要管理员权限）
        Write-Host "  尝试静默安装..." -ForegroundColor Gray
        $process = Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$installerPath`" /quiet /norestart" -Wait -PassThru -Verb RunAs
        
        if ($process.ExitCode -eq 0) {
            Write-Host "  安装成功！" -ForegroundColor Green
        } else {
            Write-Host "  静默安装失败，启动交互式安装..." -ForegroundColor Yellow
            Start-Process -FilePath $installerPath -Wait -Verb RunAs
        }
    } catch {
        Write-Host "  自动安装失败，请手动安装" -ForegroundColor Yellow
        Write-Host "  双击打开: $installerPath" -ForegroundColor White
        Read-Host "  安装完成后按 Enter 继续"
    }
    
    Write-Host ""
    Write-Host "  搜索安装位置..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
    
    # 重新搜索
    foreach ($pattern in $searchPaths) {
        $found = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found -and (Test-Path $found.FullName)) {
            $java17Path = $found.FullName
            $java17Found = $true
            Write-Host "  找到安装: $java17Path" -ForegroundColor Green
            break
        }
    }
    
    if (-not $java17Found) {
        Write-Host "  未能定位安装，请提供 Java 17 安装路径" -ForegroundColor Yellow
        $java17Path = Read-Host "  请输入路径（如 C:\Program Files\Microsoft\jdk-17.0.13.11-hotspot）"
        if (-not (Test-Path $java17Path)) {
            Write-Host "  路径无效，退出" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""

# 第 4 步：配置环境变量
Write-Host "[4/6] 配置环境变量..." -ForegroundColor Yellow
Write-Host ""

# 设置当前会话
$env:JAVA_HOME = $java17Path
$env:PATH = "$java17Path\bin;$env:PATH"

Write-Host "  当前会话已配置:" -ForegroundColor Green
Write-Host "    JAVA_HOME = $java17Path" -ForegroundColor Gray
Write-Host ""

# 尝试设置系统环境变量
Write-Host "  尝试设置系统环境变量..." -ForegroundColor Gray
try {
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $java17Path, "Machine")
    
    # 更新系统 PATH
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $javaBinPath = "$java17Path\bin"
    
    if ($machinePath -notlike "*$javaBinPath*") {
        $newPath = "$javaBinPath;$machinePath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "  系统环境变量已更新" -ForegroundColor Green
    } else {
        Write-Host "  PATH 已包含 Java，无需修改" -ForegroundColor Gray
    }
} catch {
    Write-Host "  无法设置系统环境变量（需要管理员权限）" -ForegroundColor Yellow
    Write-Host "  当前会话仍可使用，但重启后需手动配置" -ForegroundColor Gray
}

Write-Host ""

# 第 5 步：验证安装
Write-Host "[5/6] 验证安装..." -ForegroundColor Yellow
Write-Host ""

try {
    $javaExe = Join-Path $java17Path "bin\java.exe"
    $version = & $javaExe -version 2>&1 | Select-Object -First 3
    Write-Host "  Java 版本信息:" -ForegroundColor Green
    $version | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    Write-Host ""
    Write-Host "  验证成功！" -ForegroundColor Green
} catch {
    Write-Host "  验证失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 第 6 步：询问是否立即构建
Write-Host "[6/6] 准备构建..." -ForegroundColor Yellow
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Java 17 配置完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$startBuild = Read-Host "是否立即开始 Android 构建？(Y/N)"

if ($startBuild -eq "Y" -or $startBuild -eq "y") {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  开始 Android 构建" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Set-Location "D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile"
    
    Write-Host "清理旧文件..." -ForegroundColor Yellow
    Remove-Item -Path "platforms/android/.gradle" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "platforms/tempPlugin" -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "启动构建（预计 5-10 分钟）..." -ForegroundColor Cyan
    Write-Host ""
    
    npm run android
} else {
    Write-Host ""
    Write-Host "稍后运行构建，请在此 PowerShell 窗口中执行：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2\mobile" -ForegroundColor Cyan
    Write-Host "  npm run android" -ForegroundColor Cyan
    Write-Host ""
}

