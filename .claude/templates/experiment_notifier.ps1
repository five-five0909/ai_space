# experiment_notifier.ps1
# Experiment completion notification script
# Called when experiment status changes to completed or failed

param(
    [Parameter(Mandatory=$true)]
    [string]$ExperimentDir
)

$ErrorActionPreference = "Stop"

#========================================
# Functions
#========================================

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

function Get-LastNLines {
    param(
        [string]$FilePath,
        [int]$LineCount = 100
    )

    if (-not (Test-Path $FilePath)) {
        return "(File not found: $FilePath)"
    }

    $lines = Get-Content $FilePath -Tail $LineCount -ErrorAction SilentlyContinue
    if ($lines) {
        return $lines -join "`n"
    }
    return "(Empty file)"
}

function Get-JsonContent {
    param([string]$FilePath)

    if (-not (Test-Path $FilePath)) {
        return $null
    }

    try {
        return Get-Content $FilePath -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

#========================================
# Main Logic
#========================================

Write-Log "Generating notification for: $ExperimentDir"

# Validate experiment directory
if (-not (Test-Path $ExperimentDir)) {
    Write-Log "ERROR: Experiment directory not found: $ExperimentDir"
    exit 1
}

# Define file paths
$statusFile = Join-Path $ExperimentDir "experiment_status.json"
$metricsFile = Join-Path $ExperimentDir "outputs\metrics.json"
$logFile = Join-Path $ExperimentDir "logs\train.log"
$notificationFile = Join-Path $ExperimentDir "notification_prompt.txt"
$launcherFile = Join-Path $ExperimentDir "launch_claude_notification.ps1"

# Check status file
if (-not (Test-Path $statusFile)) {
    Write-Log "ERROR: Status file not found: $statusFile"
    exit 1
}

$status = Get-JsonContent $statusFile
if (-not $status) {
    Write-Log "ERROR: Failed to parse status file"
    exit 1
}

# Check if status is completed or failed
if ($status.status -notin @("completed", "failed")) {
    Write-Log "WARNING: Experiment status is '$($status.status)', not completed/failed. Skipping notification."
    exit 0
}

# Get project context
$projectDir = Split-Path -Parent (Split-Path -Parent $ExperimentDir)
$projectName = Split-Path -Leaf $projectDir

# Get metrics
$metrics = Get-JsonContent $metricsFile
$metricsContent = if ($metrics) {
    $metrics | ConvertTo-Json -Depth 10
} else {
    "(metrics.json not found)"
}

# Get last 100 lines of log
$logContent = Get-LastNLines $logFile 100

# Get Claude CLI path
$claudePath = (Get-Command claude -ErrorAction SilentlyContinue).Source
if (-not $claudePath) {
    $claudePath = "claude"  # Fallback to PATH
}

#========================================
# Generate notification prompt
#========================================

$notificationContent = @"
================================================================================
EXPERIMENT NOTIFICATION - ACTION REQUIRED
================================================================================

A new Claude Code session is needed to analyze the completed experiment.

--------------------------------------------------------------------------------
PROJECT CONTEXT
--------------------------------------------------------------------------------
Project Name: $projectName
Project Directory: $projectDir
Experiment Name: $($status.experiment_name)
Experiment Directory: $ExperimentDir
Status: $($status.status)
Start Time: $($status.start_time)
End Time: $($status.end_time)

--------------------------------------------------------------------------------
EXPERIMENT STATUS (experiment_status.json)
--------------------------------------------------------------------------------
$($status | ConvertTo-Json -Depth 10)

--------------------------------------------------------------------------------
METRICS (outputs/metrics.json)
--------------------------------------------------------------------------------
$metricsContent

--------------------------------------------------------------------------------
LOG (last 100 lines of logs/train.log)
--------------------------------------------------------------------------------
$logContent

--------------------------------------------------------------------------------
INSTRUCTIONS FOR NEW CLAUDE CODE SESSION
--------------------------------------------------------------------------------
Please analyze the experiment results above and:

1. If status is 'completed':
   - Summarize the final metrics and results
   - Identify any patterns or insights from the training log
   - Suggest next steps or improvements

2. If status is 'failed':
   - Analyze the error message and traceback
   - Identify the root cause from the log
   - Suggest fixes and recovery steps

3. Provide a brief summary suitable for the user to understand what happened.

================================================================================
END OF NOTIFICATION
================================================================================
"@

$notificationContent | Out-File $notificationFile -Encoding UTF8
Write-Log "Generated: $notificationFile"

#========================================
# Generate launcher script
#========================================

$launcherContent = @"
# launch_claude_notification.ps1
# Launch a new Claude Code session to analyze experiment results

param(
    [string]`$ExperimentDir = "$ExperimentDir"
)

`$ErrorActionPreference = "Stop"

# Claude CLI path
`$ClaudePath = "$claudePath"

# Notification file path
`$NotificationFile = Join-Path `$ExperimentDir "notification_prompt.txt"

if (-not (Test-Path `$NotificationFile)) {
    Write-Host "ERROR: Notification file not found: `$NotificationFile"
    Read-Host "Press Enter to exit"
    exit 1
}

# Read notification content
`$NotificationContent = Get-Content `$NotificationFile -Raw

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Launching Claude Code for analysis..." -ForegroundColor Cyan
Write-Host "Experiment: `$ExperimentDir" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Launch Claude Code with the notification
# Using -p for print mode to show the prompt
`$processArgs = @(
    "-p",
    "--allowedTools", "Read,Edit,Write,Bash,Glob,Grep",
    "`$NotificationContent"
)

try {
    Start-Process `$ClaudePath -ArgumentList `$processArgs -NoNewWindow
} catch {
    Write-Host "Failed to launch Claude Code directly. Trying interactive mode..." -ForegroundColor Yellow

    # Fallback: open new PowerShell and run Claude interactively
    `$psArgs = @(
        "-NoExit",
        "-Command",
        "Write-Host '========================================' -ForegroundColor Cyan; " +
        "Write-Host 'Claude Code Analysis Session' -ForegroundColor Cyan; " +
        "Write-Host '========================================' -ForegroundColor Cyan; " +
        "Write-Host ''; " +
        "Write-Host 'Project: $projectDir' -ForegroundColor Green; " +
        "Write-Host 'Experiment: `$ExperimentDir' -ForegroundColor Green; " +
        "Write-Host ''; " +
        "Write-Host 'Please paste the notification prompt or describe your analysis needs.' -ForegroundColor Yellow; " +
        "Write-Host ''; " +
        "Set-Location '$projectDir'; " +
        "claude"
    )

    Start-Process powershell -ArgumentList `$psArgs
}

Write-Host "Launcher completed."
"@

$launcherContent | Out-File $launcherFile -Encoding UTF8
Write-Log "Generated: $launcherFile"

#========================================
# Auto-launch notification (optional)
#========================================

Write-Log ""
Write-Log "========================================" -ForegroundColor Cyan
Write-Log "EXPERIMENT NOTIFICATION GENERATED" -ForegroundColor Cyan
Write-Log "========================================" -ForegroundColor Cyan
Write-Log "Status: $($status.status)"
Write-Log "Experiment: $($status.experiment_name)"
Write-Log ""
Write-Log "To analyze results, run:"
Write-Log "  powershell -File `"$launcherFile`"" -ForegroundColor Yellow
Write-Log ""
Write-Log "Or paste the content of:"
Write-Log "  $notificationFile" -ForegroundColor Yellow
Write-Log "========================================" -ForegroundColor Cyan

exit 0