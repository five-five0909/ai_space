# monitor_experiment.ps1
# Monitor experiment status and trigger notification on completion
# Usage: powershell -File monitor_experiment.ps1 -ExperimentDir <path>

param(
    [Parameter(Mandatory=$true)]
    [string]$ExperimentDir,

    [int]$CheckInterval = 5,
    [int]$MaxWaitMinutes = 60
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

function Get-ExperimentStatus {
    param([string]$StatusFile)

    if (-not (Test-Path $StatusFile)) {
        return $null
    }

    try {
        return Get-Content $StatusFile -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

#========================================
# Main Logic
#========================================

Write-Log "========================================"
Write-Log "Experiment Monitor Started"
Write-Log "========================================"
Write-Log "Experiment: $ExperimentDir"
Write-Log "Check Interval: $CheckInterval seconds"
Write-Log "Max Wait: $MaxWaitMinutes minutes"
Write-Log ""

# Validate paths
if (-not (Test-Path $ExperimentDir)) {
    Write-Log "ERROR: Experiment directory not found"
    exit 1
}

$statusFile = Join-Path $ExperimentDir "experiment_status.json"
$notifierScript = Join-Path (Split-Path -Parent $ExperimentDir) "..\templates\experiment_notifier.ps1"

if (-not (Test-Path $notifierScript)) {
    # Try template path
    $notifierScript = "D:\Desktop\近期文件\.claude\templates\experiment_notifier.ps1"
}

if (-not (Test-Path $notifierScript)) {
    Write-Log "ERROR: Notifier script not found"
    exit 1
}

# Track initial status
$previousStatus = Get-ExperimentStatus $statusFile
if (-not $previousStatus) {
    Write-Log "ERROR: Could not read status file"
    exit 1
}

Write-Log "Initial Status: $($previousStatus.status)"
Write-Log "Progress: $($previousStatus.progress)%"
Write-Log ""

# Check if already completed
if ($previousStatus.status -in @("completed", "failed")) {
    Write-Log "Experiment already in terminal state: $($previousStatus.status)"
    Write-Log "Triggering notification..."

    & powershell -File $notifierScript -ExperimentDir $ExperimentDir
    exit 0
}

# Monitor loop
$startTime = Get-Date
$maxWaitSeconds = $MaxWaitMinutes * 60
$checkCount = 0

while ($true) {
    $elapsed = (Get-Date) - $startTime
    $elapsedSeconds = $elapsed.TotalSeconds

    if ($elapsedSeconds -gt $maxWaitSeconds) {
        Write-Log "Max wait time exceeded. Exiting."
        exit 1
    }

    Start-Sleep -Seconds $CheckInterval
    $checkCount++

    $currentStatus = Get-ExperimentStatus $statusFile
    if (-not $currentStatus) {
        Write-Log "WARNING: Could not read status at check #$checkCount"
        continue
    }

    # Log progress
    $progress = if ($currentStatus.progress) { $currentStatus.progress } else { 0 }
    $status = $currentStatus.status

    if ($checkCount % 12 -eq 0 -or $status -ne $previousStatus.status) {
        # Log every minute or on status change
        Write-Log "Status: $status | Progress: $progress% | Elapsed: $([math]::Round($elapsedSeconds))s"
    }

    # Check for terminal state
    if ($status -in @("completed", "failed")) {
        Write-Log ""
        Write-Log "========================================"
        Write-Log "EXPERIMENT TERMINATED"
        Write-Log "========================================"
        Write-Log "Final Status: $status"
        Write-Log "Total Wait: $([math]::Round($elapsedSeconds)) seconds"
        Write-Log ""
        Write-Log "Triggering notification..."

        & powershell -File $notifierScript -ExperimentDir $ExperimentDir
        exit 0
    }

    $previousStatus = $currentStatus
}