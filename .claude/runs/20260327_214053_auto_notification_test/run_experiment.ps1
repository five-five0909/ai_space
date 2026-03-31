# test_30s.ps1 - Pure ASCII version with notification

param(
    [string]$ExperimentDir
)

$ErrorActionPreference = "Stop"

if (-not $ExperimentDir) {
    $ExperimentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$LogFile = Join-Path $ExperimentDir "logs\train.log"
$MetricsFile = Join-Path $ExperimentDir "outputs\metrics.json"
$StatusFile = Join-Path $ExperimentDir "experiment_status.json"

# Ensure directories exist
@($LogFile, $MetricsFile) | ForEach-Object {
    $dir = Split-Path -Parent $_
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] $Message" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    Write-Host "[$timestamp] $Message"
}

function Update-Status {
    param(
        [string]$Status,
        [int]$Progress = 0,
        [string]$ErrorMsg = ""
    )

    $statusObj = Get-Content $StatusFile -Encoding UTF8 | ConvertFrom-Json
    $statusObj.status = $Status
    $statusObj.progress = $Progress
    $statusObj.last_update_time = (Get-Date -Format "o")

    if ($Status -eq "running" -and -not $statusObj.start_time) {
        $statusObj.start_time = (Get-Date -Format "o")
    }

    if ($Status -in @("completed", "failed")) {
        $statusObj.end_time = (Get-Date -Format "o")
    }

    if ($ErrorMsg) {
        $statusObj.error = $ErrorMsg
    }

    $statusObj | ConvertTo-Json -Depth 10 | Out-File $StatusFile -Encoding UTF8
}

function Invoke-Notification {
    param([string]$ExpDir)
    
    Write-Log "Triggering notification..."
    
    $notifierPath = "D:\Desktop\近期文件\.claude\templates\experiment_notifier.ps1"
    if (Test-Path $notifierPath) {
        & powershell -NoProfile -File $notifierPath -ExperimentDir $ExpDir
        Write-Log "Notification generated"
    } else {
        Write-Log "WARNING: Notifier not found at $notifierPath"
    }
}

# Main
try {
    Write-Log "30s test started"
    Update-Status "running"

    $totalSeconds = 30
    $bestValue = [double]::MaxValue

    for ($i = 1; $i -le $totalSeconds; $i++) {
        Start-Sleep -Seconds 1

        $value = 1.0 / $i + (Get-Random -Minimum 0 -Maximum 100) / 10000
        if ($value -lt $bestValue) {
            $bestValue = $value
        }

        $progress = ($i / $totalSeconds) * 100
        Update-Status "running" -Progress $progress

        Write-Log "Second $i/$totalSeconds - value: $([math]::Round($value, 4)) - best: $([math]::Round($bestValue, 4))"
    }

    # Save metrics
    @{
        test_name = "30s_test"
        duration_seconds = $totalSeconds
        final_value = $value
        best_value = $bestValue
        completed_at = (Get-Date -Format "o")
    } | ConvertTo-Json | Out-File $MetricsFile -Encoding UTF8

    Update-Status "completed"
    Write-Log "Test completed"

    # Trigger notification
    Invoke-Notification -ExpDir $ExperimentDir

    exit 0

} catch {
    Update-Status "failed" -ErrorMsg $_.Exception.Message
    Write-Log "Test failed: $_"
    
    # Also notify on failure
    Invoke-Notification -ExpDir $ExperimentDir
    
    exit 1
}
