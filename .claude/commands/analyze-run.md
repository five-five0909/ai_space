# /analyze-run

分析实验结果。

## 适用场景

- 实验完成后分析指标
- 对比多次实验结果
- 生成实验报告
- 提取最佳模型信息

## 执行步骤

### 1. 确定实验目录

如果用户指定：

```powershell
$experiment_dir = "<user_specified_path>"
```

如果未指定，查找最近完成的实验：

```powershell
$completed = Get-ChildItem ".claude/runs" -Directory | ForEach-Object {
    $statusFile = "$($_.FullName)/experiment_status.json"
    if (Test-Path $statusFile) {
        $status = Get-Content $statusFile | ConvertFrom-Json
        if ($status.status -eq "completed") {
            [PSCustomObject]@{
                Dir = $_.FullName
                EndTime = $status.end_time
            }
        }
    }
} | Sort-Object EndTime -Descending | Select-Object -First 1

$experiment_dir = $completed.Dir
```

### 2. 读取状态和元数据

```powershell
$status = Get-Content "$experiment_dir/experiment_status.json" | ConvertFrom-Json
$metadata = Get-Content "$experiment_dir/metadata.json" | ConvertFrom-Json
```

### 3. 分析指标文件

```powershell
$metrics_file = "$experiment_dir/outputs/metrics.json"

if (Test-Path $metrics_file) {
    $metrics = Get-Content $metrics_file | ConvertFrom-Json

    Write-Output "=== 指标分析 ==="

    # 提取关键指标
    $keyMetrics = @(
        "final_loss",
        "best_loss",
        "final_accuracy",
        "best_accuracy",
        "final_f1",
        "best_f1",
        "total_epochs",
        "best_epoch"
    )

    foreach ($key in $keyMetrics) {
        if ($metrics.PSObject.Properties.Name -contains $key) {
            Write-Output "$key = $($metrics.$key)"
        }
    }
}
```

### 4. 分析日志文件

提取训练曲线：

```powershell
$log_file = "$experiment_dir/logs/train.log"

if (Test-Path $log_file) {
    Write-Output "=== 日志分析 ==="

    # 统计行数
    $totalLines = (Get-Content $log_file).Count
    Write-Output "总日志行数: $totalLines"

    # 提取 epoch 记录
    $epochs = Select-String -Path $log_file -Pattern "Epoch (\d+)/(\d+)" |
              ForEach-Object {
                  if ($_ -match "Epoch (\d+)/(\d+).*loss:\s*([\d.]+)") {
                      [PSCustomObject]@{
                          Epoch = [int]$matches[1]
                          Total = [int]$matches[2]
                          Loss = [double]$matches[3]
                      }
                  }
              }

    if ($epochs) {
        Write-Output "记录轮次数: $($epochs.Count)"
        Write-Output "最终 Loss: $($epochs[-1].Loss)"
        $minLoss = $epochs | Sort-Object Loss | Select-Object -First 1
        Write-Output "最佳 Loss: $($minLoss.Loss) (Epoch $($minLoss.Epoch))"
    }
}
```

### 5. 检查输出文件

```powershell
$outputs_dir = "$experiment_dir/outputs"

Write-Output "=== 输出文件 ==="

Get-ChildItem $outputs_dir -Recurse | ForEach-Object {
    $size = $_.Length / 1MB
    Write-Output "$($_.Name): $([math]::Round($size, 2)) MB"
}
```

### 6. 检查点分析

```powershell
$checkpoint_file = "$experiment_dir/outputs/best.pt"

if (Test-Path $checkpoint_file) {
    $checkpoint_info = Get-Item $checkpoint_file
    Write-Output "=== 检查点信息 ==="
    Write-Output "文件大小: $([math]::Round($checkpoint_info.Length / 1MB, 2)) MB"
    Write-Output "最后修改: $($checkpoint_info.LastWriteTime)"
}
```

### 7. 生成报告

创建分析报告：

```powershell
$report_file = "$experiment_dir/analysis_report.md"

$report = @"
# 实验分析报告

## 基本信息

- **实验名称**: $($status.experiment_name)
- **实验目录**: $($status.experiment_dir)
- **开始时间**: $($status.start_time)
- **结束时间**: $($status.end_time)
- **运行时长**: $duration 小时

## 命令

``````
$($metadata.command)
``````

## 关键指标

| 指标 | 值 |
|------|-----|
| 最终 Loss | $($metrics.final_loss) |
| 最佳 Loss | $($metrics.best_loss) |
| 最佳 Epoch | $($metrics.best_epoch) |
| 训练轮次 | $($metrics.total_epochs) |

## 输出文件

$(Get-ChildItem $outputs_dir | ForEach-Object { "- $($_.Name)" })

## 结论

<自动生成的结论>

---
生成时间: $(Get-Date -Format "o")
"@

$report | Out-File $report_file
Write-Output "报告已保存: $report_file"
```

### 8. 对比分析（多实验）

如果指定对比：

```powershell
$experiments = @(
    ".claude/runs/exp1",
    ".claude/runs/exp2",
    ".claude/runs/exp3"
)

Write-Output "=== 实验对比 ==="

$comparison = $experiments | ForEach-Object {
    $m = Get-Content "$_/outputs/metrics.json" | ConvertFrom-Json
    [PSCustomObject]@{
        Experiment = Split-Path $_ -Leaf
        BestLoss = $m.best_loss
        BestAccuracy = $m.best_accuracy
        Epochs = $m.total_epochs
    }
}

$comparison | Format-Table -AutoSize
```

## 输出格式

```
========================================
实验分析报告
========================================

实验名称: <name>
实验目录: <experiment_dir>

--- 基本信息 ---
命令: <command>
开始时间: <start_time>
结束时间: <end_time>
运行时长: <duration>

--- 关键指标 ---
最终 Loss: <final_loss>
最佳 Loss: <best_loss>
最佳 Epoch: <best_epoch>
训练轮次: <total_epochs>

--- 输出文件 ---
checkpoint: <size> MB
metrics: <size> KB

--- 训练曲线 ---
[可视化或数值摘要]

--- 结论 ---
<自动结论>

分析报告已保存: <experiment_dir>/analysis_report.md
========================================
```

## 参数

| 参数 | 说明 |
|------|------|
| `<experiment_dir>` | 指定实验目录 |
| `--compare` | 对比多个实验 |
| `--export-csv` | 导出指标为 CSV |
| `--plot` | 生成训练曲线图 |

## 导出功能

### CSV 导出

```powershell
$csv_file = "$experiment_dir/metrics_export.csv"
$metrics | ConvertTo-Csv -NoTypeInformation | Out-File $csv_file
```

### 训练曲线

需要 Python + matplotlib：

```powershell
python -c "
import json
import matplotlib.pyplot as plt

with open('$experiment_dir/outputs/metrics.json') as f:
    data = json.load(f)

plt.figure(figsize=(10, 6))
plt.plot(data['losses'])
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss')
plt.savefig('$experiment_dir/loss_curve.png')
"
```