# launch_claude_notification.ps1
# Launch a new Claude Code session to analyze experiment results

param(
    [string]$ExperimentDir = "D:/Desktop/近期文件/.claude/runs/20260327_213247_notification_test"
)

$ErrorActionPreference = "Stop"

# Claude CLI path
$ClaudePath = "E:\SDK-TOOL\versions\node_versions\global-module\claude.ps1"

# Notification file path
$NotificationFile = Join-Path $ExperimentDir "notification_prompt.txt"

if (-not (Test-Path $NotificationFile)) {
    Write-Host "ERROR: Notification file not found: $NotificationFile"
    Read-Host "Press Enter to exit"
    exit 1
}

# Read notification content
$NotificationContent = Get-Content $NotificationFile -Raw

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Launching Claude Code for analysis..." -ForegroundColor Cyan
Write-Host "Experiment: $ExperimentDir" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Launch Claude Code with the notification
# Using -p for print mode to show the prompt
$processArgs = @(
    "-p",
    "--allowedTools", "Read,Edit,Write,Bash,Glob,Grep",
    "$NotificationContent"
)

try {
    Start-Process $ClaudePath -ArgumentList $processArgs -NoNewWindow
} catch {
    Write-Host "Failed to launch Claude Code directly. Trying interactive mode..." -ForegroundColor Yellow

    # Fallback: open new PowerShell and run Claude interactively
    $psArgs = @(
        "-NoExit",
        "-Command",
        "Write-Host '========================================' -ForegroundColor Cyan; " +
        "Write-Host 'Claude Code Analysis Session' -ForegroundColor Cyan; " +
        "Write-Host '========================================' -ForegroundColor Cyan; " +
        "Write-Host ''; " +
        "Write-Host 'Project: D:\Desktop\近期文件\.claude' -ForegroundColor Green; " +
        "Write-Host 'Experiment: $ExperimentDir' -ForegroundColor Green; " +
        "Write-Host ''; " +
        "Write-Host 'Please paste the notification prompt or describe your analysis needs.' -ForegroundColor Yellow; " +
        "Write-Host ''; " +
        "Set-Location 'D:\Desktop\近期文件\.claude'; " +
        "claude"
    )

    Start-Process powershell -ArgumentList $psArgs
}

Write-Host "Launcher completed."
