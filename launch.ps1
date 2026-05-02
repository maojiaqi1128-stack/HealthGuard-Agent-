# HealthGuard-Agent 一键启动脚本

Write-Host "=== HealthGuard-Agent 启动中 ===" -ForegroundColor Cyan

# 切换目录
Set-Location "E:\HealthGuard-Agent"

# 激活虚拟环境
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
    Write-Host "[OK] 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "[ERROR] 找不到虚拟环境 .venv" -ForegroundColor Red
    exit 1
}

# 检查并杀掉占用 8001 端口的旧进程
$listening = netstat -ano | Select-String ":8001.*LISTENING"
if ($listening) {
    $pid = ($listening -split "\s+")[-1]
    Write-Host "[INFO] 正在释放端口 8001 (PID: $pid)..." -ForegroundColor Yellow
    taskkill /f /pid $pid 2>$null
    Start-Sleep -Seconds 1
}

# 启动服务
Write-Host "[INFO] 正在启动 FastAPI 服务..." -ForegroundColor Cyan
$env:PYTHONPATH = "src"
python -m uvicorn healthguard.main:app --host 0.0.0.0 --port 8001
