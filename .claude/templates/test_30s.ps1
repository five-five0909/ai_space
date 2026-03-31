# test_30s.ps1
# 30秒测试脚本 - 用于验证实验系统

param(
    [string]$ExperimentDir
)

#========================================
# 配置
#========================================

$ErrorActionPreference = "Stop"

if (-not $ExperimentDir) {
    $ExperimentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$LogFile = Join-Path $ExperimentDir "logs\train.log"
$MetricsFile = Join-Path $ExperimentDir "outputs\metrics.json"
$StatusFile = Join-Path $ExperimentDir "experiment_status.json"

# 确保目录存在
@($LogFile, $MetricsFile) | ForEach-Object {
    $dir = Split-Path -Parent $_
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}

#========================================
# 函数
#========================================

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] $Message" | Out-File -FilePath $LogFile -Append
    Write-Host "[$timestamp] $Message"
}

function Update-Status {
    param(
        [string]$Status,
        [int]$Progress = 0,
        [string]$Error = $null
    )

    $status = Get-Content $StatusFile | ConvertFrom-Json
    $status.status = $Status
    $status.progress = $Progress
    $status.last_update_time = (Get-Date -Format "o")

    if ($Status -eq "running" -and -not $status.start_time) {
        $status.start_time = (Get-Date -Format "o")
    }

    if ($Status -in @("completed", "failed")) {
        $status.end_time = (Get-Date -Format "o")
    }

    if ($Error) {
        $status.error = $Error
    }

    $status | ConvertTo-Json -Depth 10 | Out-File $StatusFile
}

#========================================
# 主逻辑
#========================================

try {
    Write-Log "30秒测试开始"
    Update-Status "running"

    # 模拟 30 秒训练
    $totalSeconds = 30
    $bestValue = [double]::MaxValue

    for ($i = 1; $i -le $totalSeconds; $i++) {
        Start-Sleep -Seconds 1

        # 模拟指标变化
        $value = 1.0 / $i + (Get-Random -Minimum 0 -Maximum 100) / 10000
        if ($value -lt $bestValue) {
            $bestValue = $value
        }

        $progress = ($i / $totalSeconds) * 100
        Update-Status "running" -Progress $progress

        Write-Log "秒 $i/$totalSeconds - 值: $([math]::Round($value, 4)) - 最佳: $([math]::Round($bestValue, 4))"
    }

    # 保存结果
    @{
        test_name = "30s_test"
        duration_seconds = $totalSeconds
        final_value = $value
        best_value = $bestValue
        completed_at = (Get-Date -Format "o")
    } | ConvertTo-Json | Out-File $MetricsFile

    Update-Status "completed"
    Write-Log "测试完成"
    exit 0

} catch {
    Update-Status "failed" -Error $_.Exception.Message
    Write-Log "测试失败: $_"
    exit 1
}