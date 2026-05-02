# Kill process occupying port 8000
$conn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    $pidNum = $conn.OwningProcess
    taskkill /f /pid $pidNum
    Write-Output "Killed PID: $pidNum"
    Start-Sleep 2
} else {
    Write-Output "Port 8000 is free"
}
