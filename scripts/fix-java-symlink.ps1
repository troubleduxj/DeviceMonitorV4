# 修复 Java 符号链接
# 需要以管理员身份运行

$oldPath = "C:\Program Files\Microsoft\jdk-17.0.12.7-hotspot"
$newPath = "C:\Program Files\Microsoft\jdk-17.0.13.11-hotspot"

Write-Host "创建 Java 符号链接..." -ForegroundColor Yellow
Write-Host "从: $oldPath" -ForegroundColor Cyan
Write-Host "到: $newPath" -ForegroundColor Cyan

if (Test-Path $oldPath) {
    Write-Host "旧路径已存在，删除..." -ForegroundColor Yellow
    Remove-Item $oldPath -Force -Recurse -ErrorAction SilentlyContinue
}

try {
    New-Item -ItemType SymbolicLink -Path $oldPath -Target $newPath -Force
    Write-Host "符号链接创建成功！" -ForegroundColor Green
} catch {
    Write-Host "创建失败: $_" -ForegroundColor Red
    Write-Host "请确保以管理员身份运行此脚本" -ForegroundColor Yellow
}

Write-Host "`n按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

