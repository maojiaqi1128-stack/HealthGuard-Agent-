# HealthGuard-Agent 启动脚本

Write-Host "=== HealthGuard-Agent 启动脚本 ===" -ForegroundColor Cyan

# 检查 Ollama
$ollama = Get-Process ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Write-Host "[警告] Ollama 未运行，正在启动..." -ForegroundColor Yellow
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Minimized
    Start-Sleep 3
}

# 激活虚拟环境并启动
& "E:\HealthGuard-Agent\.venv\Scripts\Activate.ps1"
Set-Location "E:\HealthGuard-Agent"

Write-Host "[信息] 启动 FastAPI 服务，按 Ctrl+C 停止..." -ForegroundColor Green
python -m uvicorn healthguard.main:app --host 0.0.0.0 --port 8000 --reload
