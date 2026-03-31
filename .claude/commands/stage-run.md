# /stage-run

执行多阶段实验任务。

## 适用场景

- 数据预处理 → 训练 → 评估
- 特征工程 → 模型训练 → 超参调优
- 多步骤流水线
- 需要按顺序执行的多个独立任务

## 执行步骤

### 1. 解析阶段

将任务分解为独立阶段：

```
阶段1: 数据预处理
阶段2: 模型训练
阶段3: 模型评估
```

每个阶段包含：
- 名称
- 命令/脚本
- 预计时长
- 输入文件
- 输出文件
- 成功条件

### 2. 生成实验目录

格式：`<YYYYMMDD_HHMMSS>_<experiment_name>`

### 3. 创建目录结构

```
<experiment_dir>/
├── experiment_status.json
├── metadata.json
├── stages.json           # 阶段定义
├── stage_01_preprocess/
│   ├── run.ps1
│   └── logs/
├── stage_02_train/
│   ├── run.ps1
│   └── logs/
├── stage_03_evaluate/
│   ├── run.ps1
│   └── logs/
├── logs/
│   └── pipeline.log
└── outputs/
    └── final/
```

### 4. 创建阶段定义文件

`stages.json`：

```json
{
  "stages": [
    {
      "index": 1,
      "name": "preprocess",
      "command": "python preprocess.py",
      "status": "pending",
      "input_files": ["data/raw.csv"],
      "output_files": ["data/processed.csv"],
      "start_time": null,
      "end_time": null,
      "duration_seconds": null
    },
    {
      "index": 2,
      "name": "train",
      "command": "python train.py",
      "status": "pending",
      "depends_on": [1],
      "input_files": ["data/processed.csv"],
      "output_files": ["outputs/model.pt"],
      "start_time": null,
      "end_time": null,
      "duration_seconds": null
    }
  ],
  "current_stage": 0,
  "total_stages": 3
}
```

### 5. 初始化状态文件

`experiment_status.json`：

```json
{
  "status": "pending",
  "experiment_name": "<name>",
  "experiment_dir": "<path>",
  "stage_status": {
    "current_stage": 0,
    "total_stages": 3,
    "stage_names": ["preprocess", "train", "evaluate"],
    "completed_stages": [],
    "failed_stage": null
  },
  ...
}
```

### 6. 为每个阶段生成脚本

`stage_XX_<name>/run.ps1`：

```powershell
# 阶段运行脚本
param(
    [string]$ExperimentDir
)

$StageName = "<stage_name>"
$LogFile = "$ExperimentDir/logs/pipeline.log"
$StatusFile = "$ExperimentDir/experiment_status.json"

# 记录开始
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] [$StageName] $Message" | Out-File -FilePath $LogFile -Append
}

Write-Log "Stage started"

try {
    # 执行阶段命令
    <stage_command> 2>&1 | Tee-Object -FilePath "$ExperimentDir/stage_XX_$StageName/logs/output.log" -Append

    # 更新阶段状态
    Write-Log "Stage completed"
    exit 0
} catch {
    Write-Log "Stage failed: $_"
    exit 1
}
```

### 7. 创建主控脚本

`run_experiment.ps1`：

```powershell
# 多阶段主控脚本
$ExperimentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$StagesFile = "$ExperimentDir/stages.json"
$StatusFile = "$ExperimentDir/experiment_status.json"

# 读取阶段定义
$stages = Get-Content $StagesFile | ConvertFrom-Json

# 更新状态函数
function Update-Status {
    param([string]$Status, [int]$CurrentStage)
    $status = Get-Content $StatusFile | ConvertFrom-Json
    $status.status = $Status
    $status.stage_status.current_stage = $CurrentStage
    $status.last_update_time = (Get-Date -Format "o")
    $status | ConvertTo-Json -Depth 10 | Out-File $StatusFile
}

# 执行各阶段
Update-Status "running" 0

for ($i = 0; $i -lt $stages.stages.Count; $i++) {
    $stage = $stages.stages[$i]
    $stageDir = "$ExperimentDir/stage_$($stage.index.ToString('00'))_$($stage.name)"

    # 更新当前阶段
    Update-Status "running" ($i + 1)

    # 执行阶段脚本
    $result = & powershell -File "$stageDir/run.ps1" -ExperimentDir $ExperimentDir

    if ($LASTEXITCODE -ne 0) {
        # 阶段失败
        Update-Status "failed" ($i + 1)
        exit 1
    }
}

# 全部完成
Update-Status "completed" $stages.stages.Count
```

### 8. 启动流水线

使用 psmux 或 Start-Process 启动主控脚本。

### 9. 返回结果

输出必须包含：

```
实验名称：<name>
实验目录：<experiment_dir>
总阶段数：<n>
阶段列表：
  1. <stage_1_name>
  2. <stage_2_name>
  3. <stage_3_name>
状态文件：<experiment_dir>/experiment_status.json
日志文件：<experiment_dir>/logs/pipeline.log
检查命令：/check-run <experiment_dir>
```

## 缺少信息时

询问：

1. "请描述各阶段任务（命令、输入、输出）"
2. "各阶段之间是否有依赖关系？"
3. "哪个阶段预计最耗时？"

## 阶段依赖

支持依赖声明：

```json
{
  "index": 3,
  "name": "evaluate",
  "depends_on": [2],
  ...
}
```

- 依赖阶段必须成功完成
- 失败则跳过依赖此阶段的所有后续阶段

## 失败恢复

如果中间阶段失败：

1. 状态记录失败阶段
2. 后续阶段不执行
3. 可手动修复后从失败阶段继续
4. 命令：`/stage-run --resume <experiment_dir>`