# run_experiment.ps1
# 实验运行脚本模板
# 此文件应复制到实验目录并根据具体任务修改

param(
    [string]$ExperimentDir,
    [string]$Command,
    [int]$TotalEpochs = 100
)

#========================================
# 配置
#========================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# 路径
if (-not $ExperimentDir) {
    $ExperimentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$LogFile = Join-Path $ExperimentDir "logs\train.log"
$MetricsFile = Join-Path $ExperimentDir "outputs\metrics.json"
$StatusFile = Join-Path $ExperimentDir "experiment_status.json"
$OutputDir = Join-Path $ExperimentDir "outputs"

# 确保目录存在
@($LogFile, $MetricsFile) | ForEach-Object {
    $dir = Split-Path -Parent $_
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}

#========================================
# 日志函数
#========================================

function Write-Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR", "DEBUG")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logLine = "[$timestamp] [$Level] $Message"

    # 写入日志文件
    $logLine | Out-File -FilePath $LogFile -Append -Encoding UTF8

    # 同时输出到控制台
    switch ($Level) {
        "ERROR"   { Write-Host $logLine -ForegroundColor Red }
        "WARNING" { Write-Host $logLine -ForegroundColor Yellow }
        "DEBUG"   { Write-Host $logLine -ForegroundColor Gray }
        default   { Write-Host $logLine }
    }
}

#========================================
# 状态更新函数
#========================================

function Update-Status {
    param(
        [ValidateSet("pending", "running", "completed", "failed")]
        [string]$Status,
        [int]$CurrentEpoch = 0,
        [int]$TotalEpochsVal = 0,
        [double]$Progress = 0,
        [double]$BestMetric = $null,
        [string]$Error = $null,
        [string]$Traceback = $null
    )

    if (Test-Path $StatusFile) {
        $statusObj = Get-Content $StatusFile | ConvertFrom-Json
    } else {
        $statusObj = [PSCustomObject]@{
            status = "pending"
            experiment_name = ""
            experiment_dir = $ExperimentDir
            platform = "windows"
            launcher_type = "psmux"
            pid = $PID
            psmux_session = ""
            host = $env:COMPUTERNAME
            workdir = $PWD.Path
            start_time = $null
            end_time = $null
            progress = 0
            current_epoch = 0
            total_epochs = 0
            best_metric = $null
            result_files = [PSCustomObject]@{
                logs = $LogFile
                metrics = $MetricsFile
                checkpoint = Join-Path $OutputDir "best.pt"
            }
            error = $null
            traceback = $null
            last_update_time = $null
        }
    }

    # 更新字段
    $statusObj.status = $Status
    $statusObj.last_update_time = (Get-Date -Format "o")

    if ($Status -eq "running" -and -not $statusObj.start_time) {
        $statusObj.start_time = (Get-Date -Format "o")
    }

    if ($Status -in @("completed", "failed")) {
        $statusObj.end_time = (Get-Date -Format "o")
    }

    if ($CurrentEpoch -gt 0) {
        $statusObj.current_epoch = $CurrentEpoch
    }

    if ($TotalEpochsVal -gt 0) {
        $statusObj.total_epochs = $TotalEpochsVal
    }

    if ($Progress -gt 0) {
        $statusObj.progress = [math]::Round($Progress, 2)
    }

    if ($null -ne $BestMetric) {
        $statusObj.best_metric = $BestMetric
    }

    if ($Error) {
        $statusObj.error = $Error
    }

    if ($Traceback) {
        $statusObj.traceback = $Traceback
    }

    # 保存状态
    $statusObj | ConvertTo-Json -Depth 10 | Out-File $StatusFile -Encoding UTF8
}

#========================================
# 指标记录函数
#========================================

function Save-Metrics {
    param(
        [hashtable]$Metrics
    )

    $metricsObj = [PSCustomObject]$Metrics
    $metricsObj | ConvertTo-Json -Depth 10 | Out-File $MetricsFile -Encoding UTF8
    Write-Log "Metrics saved: $MetricsFile"
}

#========================================
# 通知触发函数
#========================================

function Invoke-ExperimentNotification {
    param(
        [string]$ExperimentDir
    )

    Write-Log "Triggering experiment notification..."

    # Find notifier script using environment variables (avoid encoding issues)
    $notifierScript = $null

    # Method 1: Use workdir from status file
    if (Test-Path "$ExperimentDir\experiment_status.json") {
        try {
            $status = Get-Content "$ExperimentDir\experiment_status.json" -Encoding UTF8 | ConvertFrom-Json
            $workdir = $status.workdir
            if ($workdir) {
                $notifierPath = Join-Path $workdir ".claude\templates\experiment_notifier.ps1"
                if (Test-Path $notifierPath) {
                    $notifierScript = $notifierPath
                }
            }
        } catch {}
    }

    # Method 2: Use relative path from experiment dir
    if (-not $notifierScript) {
        $notifierPath = Join-Path $ExperimentDir "..\..\templates\experiment_notifier.ps1"
        try {
            $resolved = (Resolve-Path $notifierPath -ErrorAction SilentlyContinue).Path
            if ($resolved -and (Test-Path $resolved)) {
                $notifierScript = $resolved
            }
        } catch {}
    }

    # Method 3: Search in common locations
    if (-not $notifierScript) {
        $searchPaths = @(
            "$env:USERPROFILE\Desktop\近期文件\.claude\templates\experiment_notifier.ps1",
            "D:\Desktop\近期文件\.claude\templates\experiment_notifier.ps1"
        )
        foreach ($p in $searchPaths) {
            if (Test-Path $p) {
                $notifierScript = $p
                break
            }
        }
    }

    if (-not $notifierScript) {
        Write-Log "WARNING: Notifier script not found, skipping notification" -Level "WARNING"
        return
    }

    try {
        & powershell -NoProfile -File $notifierScript -ExperimentDir $ExperimentDir
        Write-Log "Notification generated successfully"
    } catch {
        Write-Log "WARNING: Failed to generate notification: $_" -Level "WARNING"
    }
}

#========================================
# 主执行逻辑
#========================================

try {
    Write-Log "实验开始"
    Write-Log "实验目录: $ExperimentDir"
    Write-Log "PID: $PID"

    # 更新状态为运行中
    Update-Status -Status "running"

    #========================================
    # 在此处插入实际任务
    #========================================

    # 示例：模拟训练循环
    # 替换为实际命令：python train.py --output-dir $OutputDir
    if ($Command) {
        Write-Log "执行命令: $Command"

        # 执行命令并捕获输出
        $process = Start-Process -FilePath "powershell" `
            -ArgumentList "-Command", $Command `
            -RedirectStandardOutput "$OutputDir\stdout.log" `
            -RedirectStandardError "$OutputDir\stderr.log" `
            -PassThru -NoNewWindow

        # 等待完成
        $process.WaitForExit()

        if ($process.ExitCode -ne 0) {
            throw "命令执行失败，退出码: $($process.ExitCode)"
        }
    } else {
        # 默认示例：模拟训练
        Write-Log "运行示例训练（无实际命令）"

        $losses = @()
        $bestLoss = [double]::MaxValue
        $bestEpoch = 0

        for ($epoch = 1; $epoch -le $TotalEpochs; $epoch++) {
            # 模拟训练
            Start-Sleep -Milliseconds 100

            # 模拟损失下降
            $loss = 1.0 / $epoch + (Get-Random -Minimum 0 -Maximum 100) / 10000
            $losses += $loss

            # 更新最佳
            if ($loss -lt $bestLoss) {
                $bestLoss = $loss
                $bestEpoch = $epoch
            }

            # 每 10 轮更新状态
            if ($epoch % 10 -eq 0) {
                $progress = ($epoch / $TotalEpochs) * 100
                Update-Status -Status "running" `
                    -CurrentEpoch $epoch `
                    -TotalEpochsVal $TotalEpochs `
                    -Progress $progress `
                    -BestMetric $bestLoss

                Write-Log "Epoch $epoch/$TotalEpochs - Loss: $([math]::Round($loss, 4)) - Best: $([math]::Round($bestLoss, 4))"
            }
        }

        # 保存指标
        Save-Metrics @{
            final_loss = $losses[-1]
            best_loss = $bestLoss
            best_epoch = $bestEpoch
            total_epochs = $TotalEpochs
            all_losses = $losses
        }
    }

    #========================================
    # 完成处理
    #========================================

    Update-Status -Status "completed"
    Write-Log "实验成功完成"

    #========================================
    # 触发通知
    #========================================
    Invoke-ExperimentNotification -ExperimentDir $ExperimentDir

    exit 0

} catch {
    # 错误处理
    $errorMsg = $_.Exception.Message
    $traceback = $_.ScriptStackTrace

    Write-Log "实验失败: $errorMsg" -Level "ERROR"
    Write-Log "堆栈: $traceback" -Level "ERROR"

    Update-Status -Status "failed" -Error $errorMsg -Traceback $traceback

    #========================================
    # 触发通知（失败时也通知）
    #========================================
    Invoke-ExperimentNotification -ExperimentDir $ExperimentDir

    exit 1
}