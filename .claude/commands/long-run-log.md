# /long-run-log

启动长时间后台实验任务。

## 适用场景

- 训练深度学习模型
- 长时间数据处理
- 批量计算任务
- 任何需要后台运行并追踪状态的任务

## 执行步骤

### 1. 平台检测

```powershell
# 确认平台
$PSVersionTable.Platform
```

### 2. 工具检测

```powershell
# 检测必要工具
Get-Command psmux -ErrorAction SilentlyContinue
Get-Command git -ErrorAction SilentlyContinue
Get-Command python -ErrorAction SilentlyContinue
Get-Command py -ErrorAction SilentlyContinue
```

若缺失，按优先级安装：scoop → winget → choco

### 3. 生成实验目录

格式：`<YYYYMMDD_HHMMSS>_<experiment_name>`

```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$experiment_name = "train_model"  # 从任务推断或用户提供
$experiment_dir = ".claude/runs/${timestamp}_${experiment_name}"
```

### 4. 创建目录结构

```powershell
New-Item -ItemType Directory -Force -Path $experiment_dir
New-Item -ItemType Directory -Force -Path "$experiment_dir/logs"
New-Item -ItemType Directory -Force -Path "$experiment_dir/outputs"
```

### 5. 初始化状态文件

创建 `experiment_status.json`：

```json
{
  "status": "pending",
  "experiment_name": "<name>",
  "experiment_dir": "<absolute_path>",
  "platform": "windows",
  "launcher_type": "psmux",
  "pid": null,
  "psmux_session": "exp_<timestamp>_<name>",
  "host": "<hostname>",
  "workdir": "<workdir>",
  "start_time": null,
  "end_time": null,
  "progress": 0,
  "current_epoch": 0,
  "total_epochs": null,
  "best_metric": null,
  "result_files": {
    "logs": "<experiment_dir>/logs/train.log",
    "metrics": "<experiment_dir>/outputs/metrics.json",
    "checkpoint": "<experiment_dir>/outputs/best.pt"
  },
  "error": null,
  "traceback": null,
  "last_update_time": "<ISO8601>"
}
```

### 6. 创建元数据文件

创建 `metadata.json`：

```json
{
  "experiment_name": "<name>",
  "created_at": "<ISO8601>",
  "command": "<original_command>",
  "description": "<user_description>",
  "tags": []
}
```

### 7. 记录原始命令

创建 `command.txt`：

```
<original_command>
```

### 8. 生成运行脚本

基于 `.claude/templates/run_experiment.ps1` 生成当前实验专属脚本：

- 设置工作目录
- 重定向日志到 `logs/train.log`
- 运行中更新状态
- 完成时写 `completed`
- 失败时写 `failed` 并记录错误

### 9. 启动任务

**优先 psmux（必须加 -d 后台运行）：**

```powershell
$sessionName = "exp_${timestamp}_${experiment_name}"
psmux new -d -s $sessionName -n $experiment_name -- powershell -NoProfile -File "$experiment_dir/run_experiment.ps1" -ExperimentDir "$experiment_dir"
```

**重要参数：**
- `-d`：后台运行，**必须加**，否则会阻塞当前终端
- `-s`：会话名称，用于后续 attach/kill
- `-n`：窗口名称，可选

**验证启动：**

```powershell
# 检查会话是否创建成功
psmux ls

# 应看到类似输出：
# exp_xxx: 1 windows (created ...)
```

**降级 Start-Process（psmux 不可用时）：**

```powershell
Start-Process powershell -ArgumentList "-NoProfile", "-File", "$experiment_dir/run_experiment.ps1", "-ExperimentDir", "$experiment_dir" -WindowStyle Hidden
```

### 10. 更新状态

启动后立即更新 `experiment_status.json`：

- status → running
- pid → 实际 PID
- start_time → 当前时间
- last_update_time → 当前时间

### 11. 返回结果

输出必须包含：

```
实验名称：<name>
实验目录：<experiment_dir>
状态文件：<experiment_dir>/experiment_status.json
日志文件：<experiment_dir>/logs/train.log
输出目录：<experiment_dir>/outputs/
会话/PID：<psmux_session> 或 <pid>
检查命令：/check-run <experiment_dir>
```

## 缺少信息时

按顺序询问：

1. "实验名称是什么？"（若无法从命令推断）
2. "预计运行多少轮/多长时间？"（可选）
3. "是否有特殊参数需要传递？"

## psmux 详细用法

### 常用命令

```powershell
# 后台启动新会话（必须 -d 才能后台运行）
psmux new -d -s <session_name> -n <window_name> -- <command>

# 查看所有会话
psmux ls

# 检查服务器状态
psmux info

# 附加到会话（查看实时输出）
psmux attach -t <session_name>

# 杀死会话
psmux kill-session -t <session_name>

# 杀死所有会话
psmux kill-server
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `-s <name>` | 会话名称（session name） |
| `-n <name>` | 窗口名称（window name），可选 |
| `-d` | 后台运行（detached），**必须加**否则会阻塞 |
| `-t <name>` | 目标会话名，用于 attach/kill 等操作 |
| `-- <cmd>` | 要执行的命令，`--` 后跟完整命令 |

### 工作流程

```
1. psmux info          # 检查服务器是否运行
2. psmux new -d -s exp_xxx -- <cmd>  # 创建后台会话
3. psmux ls            # 确认会话已创建
4. psmux attach -t exp_xxx  # 可选：查看实时输出
5. 任务完成后会话自动退出
```

## 已知问题与踩坑记录

### 1. 服务器未启动

**问题**：`psmux: no server running on session 'default'`

**原因**：psmux 服务器未启动

**解决**：
```powershell
# 方法1：直接创建会话（会自动启动服务器）
psmux new -d -s test -- echo hello

# 方法2：显式启动服务器
psmux start-server  # 如果有此命令
```

### 2. 忘记 -d 参数

**问题**：命令阻塞，无法继续操作

**原因**：不加 `-d` 会前台运行，占用当前终端

**解决**：始终使用 `-d` 参数后台运行
```powershell
# 正确
psmux new -d -s exp_xxx -- powershell -File script.ps1

# 错误（会阻塞）
psmux new -s exp_xxx -- powershell -File script.ps1
```

### 3. 混淆 -s 和 -n 参数

**问题**：会话名和窗口名混淆

**说明**：
- `-s` = session name（会话名，用于 attach/kill/ls）
- `-n` = window name（窗口名，仅显示用）

```powershell
# 正确：创建名为 "exp_001" 的会话
psmux new -d -s exp_001 -n train -- python train.py

# 查看会话
psmux ls              # 显示 exp_001
psmux attach -t exp_001  # 附加到会话
```

### 4. PowerShell 脚本编码问题

**问题**：`TermininatorExpectedAtEndOfString` 或乱码错误

**原因**：PowerShell 5.1 对 UTF-8 编码支持不佳，中文注释可能导致解析错误

**解决**：
1. 脚本文件保存为 UTF-8 with BOM
2. 或使用纯 ASCII/英文注释
3. 在脚本中显式指定编码：
```powershell
Get-Content $file -Encoding UTF8
Out-File $file -Encoding UTF8
```

### 5. 会话命名冲突

**问题**：同名会话已存在

**解决**：使用时间戳生成唯一名称
```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$sessionName = "exp_${timestamp}"
```

### 6. 进程退出后会话消失

**问题**：`psmux ls` 看不到刚创建的会话

**原因**：
- 命令执行完毕后会话自动退出
- 命令启动失败（路径错误、脚本错误等）

**排查**：
```powershell
# 附加到会话查看输出
psmux attach -t <session_name>

# 检查脚本是否可执行
powershell -File script.ps1  # 先前台测试
```

## 输出要求

1. 必须输出可执行的 PowerShell 命令
2. 必须输出完整文件路径
3. 必须明确区分"已执行"和"建议执行"
4. 必须提供后续检查方式