# 按钮权限初始化脚本 (PowerShell版本)
# 使用方法: .\scripts\init_button_permissions.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "开始初始化按钮权限" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 数据库连接信息（根据实际情况修改）
$dbHost = "localhost"
$dbPort = "3306"
$dbName = "device_monitor"
$dbUser = "root"
$dbPassword = "root"

# SQL文件路径
$sqlFile = "database\button_permissions_init.sql"

# 检查SQL文件是否存在
if (-not (Test-Path $sqlFile)) {
    Write-Host "❌ 错误: SQL文件不存在: $sqlFile" -ForegroundColor Red
    exit 1
}

Write-Host "`n📄 SQL文件: $sqlFile" -ForegroundColor Green
Write-Host "📊 数据库: $dbName@$dbHost" -ForegroundColor Green

# 提示用户确认
Write-Host "`n⚠️  即将执行SQL脚本，确认继续? (Y/N): " -ForegroundColor Yellow -NoNewline
$confirm = Read-Host
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "❌ 已取消操作" -ForegroundColor Red
    exit 0
}

Write-Host "`n🚀 正在执行SQL脚本..." -ForegroundColor Cyan

# 使用mysql命令行执行SQL
try {
    # 构建mysql命令
    $mysqlCmd = "mysql -h $dbHost -P $dbPort -u $dbUser -p$dbPassword $dbName < $sqlFile"
    
    # 执行命令
    Invoke-Expression $mysqlCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ 按钮权限初始化成功！" -ForegroundColor Green
        Write-Host "`n请登录系统查看 系统管理 -> 角色管理 -> 分配权限" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ SQL执行失败，退出码: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`n❌ 执行SQL时发生错误:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "完成！" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

