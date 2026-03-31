# /check-run

检查实验运行状态。

## 适用场景

- 检查后台训练是否完成
- 查看实验进度
- 确认实验是否失败
- 监控长时间任务

## 执行步骤

### 1. 确定实验目录

如果用户指定：

```powershell
$experiment_dir = "<user_specified_path>"
```

如果未指定，查找最近实验：

```powershell
$recent = Get-ChildItem ".claude/runs" -Directory |
          Sort-Object LastWriteTime -Descending |
          Select-Object -First 1
$experiment_dir = $recent.FullName
```

### 2. 读取状态文件

```powershell
$status_file = "$experiment_dir/experiment_status.json"

if (-not (Test-Path $status_file)) {
    Write-Error "状态文件不存在: $status_file"
    exit 1
}

$status = Get-Content $status_file | ConvertFrom-Json
```

### 3. 分析状态

根据 `status` 字段判断：

#### status = "pending"

```
状态：等待启动
说明：实验已初始化但主任务未启动
建议：检查启动脚本是否正确执行
```

#### status = "running"

检查进程是否存在：

```powershell
# 检查 PID
$process = Get-Process -Id $status.pid -ErrorAction SilentlyContinue

if ($null -eq $process) {
    Write-Warning "进程不存在，但状态仍为 running"
    Write-Output "可能：进程异常退出或状态未更新"
} else {
    Write-Output "进程运行中: PID=$($status.pid)"
}
```

检查 psmux 会话（如适用）：

```powershell
if ($status.launcher_type -eq "psmux") {
    psmux list | Select-String $status.psmux_session
}
```

检查日志最新内容：

```powershell
$log_file = "$experiment_dir/logs/train.log"
if (Test-Path $log_file) {
    Write-Output "=== 最近日志 ==="
    Get-Content $log_file -Tail 20
}
```

#### status = "completed"

检查输出文件：

```powershell
$metrics_file = "$experiment_dir/outputs/metrics.json"
$checkpoint_file = "$experiment_dir/outputs/best.pt"

Write-Output "=== 输出文件检查 ==="

if (Test-Path $metrics_file) {
    $metrics = Get-Content $metrics_file | ConvertFrom-Json
    Write-Output "指标文件: 存在"
    Write-Output "最佳指标: $($metrics | ConvertTo-Json -Compress)"
} else {
    Write-Warning "指标文件: 不存在"
}

if (Test-Path $checkpoint_file) {
    Write-Output "检查点: 存在"
} else {
    Write-Warning "检查点: 不存在"
}
```

读取关键指标：

```powershell
$metrics = Get-Content $metrics_file | ConvertFrom-Json
Write-Output "=== 关键结果 ==="
Write-Output "最终 Loss: $($metrics.final_loss)"
Write-Output "最佳 Accuracy: $($metrics.best_accuracy)"
Write-Output "训练轮次: $($metrics.total_epochs)"
```

#### status = "failed"

汇总错误信息：

```powershell
Write-Output "=== 失败信息 ==="
Write-Output "错误: $($status.error)"
Write-Output ""
Write-Output "=== 错误堆栈 ==="
Write-Output $status.traceback
Write-Output ""
Write-Output "=== 日志最后 100 行 ==="
Get-Content "$experiment_dir/logs/train.log" -Tail 100
```

### 4. 计算运行时长

```powershell
if ($status.start_time) {
    $start = [DateTime]::Parse($status.start_time)
    if ($status.end_time) {
        $end = [DateTime]::Parse($status.end_time)
    } else {
        $end = Get-Date
    }
    $duration = $end - $start
    Write-Output "运行时长: $($duration.TotalHours.ToString('F2')) 小时"
}
```

### 5. 输出状态摘要

```
========================================
实验状态报告
========================================
实验名称: <name>
实验目录: <experiment_dir>
当前状态: <status>

进程信息:
  PID: <pid>
  会话: <psmux_session>

时间信息:
  开始时间: <start_time>
  结束时间: <end_time>
  运行时长: <duration>

进度信息:
  当前轮次: <current_epoch>/<total_epochs>
  进度: <progress>%
  最佳指标: <best_metric>

文件路径:
  状态文件: <experiment_dir>/experiment_status.json
  日志文件: <experiment_dir>/logs/train.log
  输出目录: <experiment_dir>/outputs/

下一步建议:
  <suggestions>
========================================
```

## 列出所有实验

```powershell
Get-ChildItem ".claude/runs" -Directory | ForEach-Object {
    $statusFile = "$($_.FullName)/experiment_status.json"
    if (Test-Path $statusFile) {
        $status = Get-Content $statusFile | ConvertFrom-Json
        [PSCustomObject]@{
            Name = $status.experiment_name
            Status = $status.status
            StartTime = $status.start_time
            Dir = $_.Name
        }
    }
} | Format-Table -AutoSize
```

## 参数

| 参数 | 说明 |
|------|------|
| `<experiment_dir>` | 指定实验目录 |
| `--all` | 列出所有实验 |
| `--running` | 只显示运行中的实验 |
| `--failed` | 只显示失败的实验 |
| `--tail N` | 显示最后 N 行日志 |

## 返回值

- 状态正常：返回状态信息
- 状态异常：返回错误信息和修复建议
- 实验不存在：返回错误和可用实验列表