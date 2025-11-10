# 开发环境自动重启脚本
# 用于清理Python缓存、终止进程并重启服务

param(
    [switch]$SkipCache,
    [switch]$SkipKill,
    [switch]$OnlyClean,
    [int]$Port = 8001
)

Write-Host "🔄 开发环境重启脚本启动..." -ForegroundColor Green

# 1. 终止现有Python进程
if (-not $SkipKill) {
    Write-Host "🔪 终止现有Python进程..." -ForegroundColor Yellow
    try {
        $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue
        if ($processes) {
            $processes | ForEach-Object {
                Write-Host "  终止进程 PID: $($_.Id)" -ForegroundColor Gray
                Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            }
            Start-Sleep -Seconds 2
            Write-Host "✅ Python进程已终止" -ForegroundColor Green
        } else {
            Write-Host "ℹ️  没有找到运行中的Python进程" -ForegroundColor Blue
        }
    } catch {
        Write-Host "⚠️  终止进程时出现错误: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 2. 清理Python缓存
if (-not $SkipCache) {
    Write-Host "🧹 清理Python缓存..." -ForegroundColor Yellow
    
    # 清理.pyc文件
    $pycFiles = Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
    if ($pycFiles) {
        $pycFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "  清理了 $($pycFiles.Count) 个 .pyc 文件" -ForegroundColor Gray
    }
    
    # 清理__pycache__目录
    $pycacheDir = Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue
    if ($pycacheDir) {
        $pycacheDir | ForEach-Object {
            Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue
        }
        Write-Host "  清理了 $($pycacheDir.Count) 个 __pycache__ 目录" -ForegroundColor Gray
    }
    
    # 清理.pytest_cache
    $pytestCache = Get-ChildItem -Path . -Recurse -Directory -Name ".pytest_cache" -ErrorAction SilentlyContinue
    if ($pytestCache) {
        $pytestCache | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  清理了pytest缓存" -ForegroundColor Gray
    }
    
    Write-Host "✅ Python缓存清理完成" -ForegroundColor Green
}

# 3. 检查端口占用
Write-Host "🔍 检查端口 $Port 占用情况..." -ForegroundColor Yellow
try {
    $portProcess = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($portProcess) {
        $pid = $portProcess.OwningProcess
        Write-Host "  端口 $Port 被进程 PID:$pid 占用，尝试终止..." -ForegroundColor Gray
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        Write-Host "✅ 端口已释放" -ForegroundColor Green
    } else {
        Write-Host "✅ 端口 $Port 可用" -ForegroundColor Green
    }
} catch {
    Write-Host "ℹ️  无法检查端口状态，继续执行..." -ForegroundColor Blue
}

# 4. 如果只是清理，则退出
if ($OnlyClean) {
    Write-Host "🎯 仅清理模式，任务完成" -ForegroundColor Green
    exit 0
}

# 5. 验证虚拟环境
Write-Host "🔍 验证虚拟环境..." -ForegroundColor Yellow
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "❌ 虚拟环境不存在，请先创建虚拟环境" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 虚拟环境验证通过" -ForegroundColor Green

# 6. 测试导入
Write-Host "🧪 测试应用导入..." -ForegroundColor Yellow
try {
    $importTest = & .\.venv\Scripts\python.exe -c "from app import app; print('Import successful')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 应用导入测试通过" -ForegroundColor Green
    } else {
        Write-Host "❌ 应用导入失败:" -ForegroundColor Red
        Write-Host $importTest -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ 导入测试异常: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 7. 启动开发服务器
Write-Host "🚀 启动开发服务器..." -ForegroundColor Green
Write-Host "   端口: $Port" -ForegroundColor Gray
Write-Host "   访问地址: http://127.0.0.1:$Port" -ForegroundColor Gray
Write-Host "   按 Ctrl+C 停止服务器" -ForegroundColor Gray
Write-Host ""

try {
    & .\.venv\Scripts\python.exe run.py
} catch {
    Write-Host "❌ 服务器启动失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}