# start_terminals.ps1
# Responsibility: Open 4 Windows Terminal windows in the correct directory using PowerShell.

$simDir = "$HOME\Documents\checkout_carla\CARLA_extensions"

# Check if directory exists
if (!(Test-Path $simDir)) {
    Write-Error "Directory not found: $simDir"
    return
}

Write-Host "Opening 4 Windows..." -ForegroundColor Cyan

function Open-TerminalWindow($title, $command) {
    # -w -1: New Window
    # powershell -NoExit: Keep terminal open
    # We Write-Host the command for visibility.
    
    if ($command) {
        $innerCommand = "Write-Host '$command' -ForegroundColor Yellow"
        $args = @(
            "-w", "-1", 
            "--title", $title, 
            "-d", $simDir, 
            "powershell.exe", "-NoExit", "-Command", $innerCommand
        )
    } else {
        $args = @(
            "-w", "-1", 
            "--title", $title, 
            "-d", $simDir, 
            "powershell.exe", "-NoExit"
        )
    }
    
    Start-Process "wt.exe" -ArgumentList $args
}

# Supervisor
Open-TerminalWindow "supervisor" "python3.12 .\manual_control.py --profile supervisor"

# Simulator
Open-TerminalWindow "simulator" "python3.12 .\manual_control.py --profile simulator"

# Rear View
Open-TerminalWindow "rear_view" "python3.12 .\rear_view.py"

# Other
Open-TerminalWindow "other" $null

Write-Host "Terminal windows opened." -ForegroundColor Green
