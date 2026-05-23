# start_carla.ps1
# Responsibility: Start the Carla simulator and configure the map.

$carlaExe = "$HOME\Documents\CarlaQuick\CarlaUE4.exe"
$utilDir = "$HOME\Documents\CarlaQuick\PythonAPI\util"

if (Test-Path $carlaExe) {
    Write-Host "Starting CarlaUE4..." -ForegroundColor Cyan
    Start-Process $carlaExe
} else {
    Write-Error "CarlaUE4.exe not found at $carlaExe"
    return
}

Write-Host "Waiting for Carla port 2000..." -ForegroundColor Yellow
while (!(Test-NetConnection -ComputerName localhost -Port 2000 -WarningAction SilentlyContinue).TcpTestSucceeded) {
    Start-Sleep -Seconds 2
}

Write-Host "Setting map to Town02..." -ForegroundColor Cyan
Start-Process "python3.12" -ArgumentList ".\config.py --map Town02" -WorkingDirectory $utilDir -NoNewWindow -Wait

Write-Host "Carla is ready." -ForegroundColor Green
