# master_startup.ps1
# Responsibility: Orchestrate the full startup process.

$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$scriptDir = Join-Path $PSScriptRoot "scripts"

Write-Host "--- Master Startup Initiated ---" -ForegroundColor White -BackgroundColor Blue

# 1. Run Carla Startup
& (Join-Path $scriptDir "start_carla.ps1")

# 2. Run Terminal Startup
& (Join-Path $scriptDir "start_terminals.ps1")

Write-Host "--- All components started ---" -ForegroundColor White -BackgroundColor Blue
