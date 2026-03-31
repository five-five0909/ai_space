# Windows PowerShell 项目级科研实验代理

> 本文件定义当前项目的实验协议、命令系统与运行规范。

## 项目结构

```
.claude/
├── CLAUDE.md              # 本文件：总规则
├── commands/              # 项目级命令定义
│   ├── long-run-log.md
│   ├── stage-run.md
│   ├── check-run.md
│   ├── analyze-run.md
│   └── install-psmux.md
├── templates/             # 脚本模板
│   ├── run_experiment.ps1
│   ├── wrapper_train.py
│   ├── test_30s.ps1
│   ├── test_30s.py
│   └── experiment_status.example.json
└── runs/                  # 实验运行目录
```

## 核心原则

### 1. 实验隔离

每次实验必须创建唯一目录：

```
.claude/runs/<YYYYMMDD_HHMMSS>_<experiment_name>/
```

标准实验目录结构：

```
<experiment_dir>/
├── experiment_status.json   # 状态文件（唯一状态源）
├── metadata.json            # 实验元数据
├── command.txt              # 原始命令记录
├── run_experiment.ps1       # 运行脚本
├── wrapper_train.py         # Python 包装器（如需要）
├── logs/
│   └── train.log           # 训练日志
└── outputs/
    ├── metrics.json        # 指标文件
    └── best.pt             # 最佳检查点
```

### 2. 状态协议

`experiment_status.json` 必须包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | pending / running / completed / failed |
| experiment_name | string | 实验名称 |
| experiment_dir | string | 实验目录绝对路径 |
| platform | string | windows |
| launcher_type | string | psmux / start-process |
| pid | number | 进程 ID |
| psmux_session | string | psmux 会话名 |
| host | string | 主机名 |
| workdir | string | 工作目录 |
| start_time | string | ISO8601 开始时间 |
| end_time | string | ISO8601 结束时间 |
| progress | number | 进度百分比 |
| current_epoch | number | 当前轮次 |
| total_epochs | number | 总轮次 |
| best_metric | number | 最佳指标 |
| result_files | object | 结果文件路径 |
| error | string | 错误信息 |
| traceback | string | 错误堆栈 |
| last_update_time | string | ISO8601 最后更新时间 |

### 3. 工具优先级

后台运行：
1. **psmux**（首选）
2. Start-Process（降级）

包管理器：
1. **scoop**（首选）
2. winget
3. choco

### 4. 命令系统

| 命令 | 用途 |
|------|------|
| `/long-run-log` | 启动长时间实验 |
| `/stage-run` | 执行多阶段任务 |
| `/check-run` | 检查实验状态 |
| `/analyze-run` | 分析实验结果 |
| `/install-psmux` | 安装 psmux |

## 使用方式

在 Claude Code 中直接输入命令名：

```
/long-run-log python train.py --epochs 100
```

或描述任务需求，代理将自动选择合适的命令执行。

## 状态流转

```
pending → running → completed
                 ↘ failed
```

- **pending**：已初始化，主任务未启动
- **running**：任务运行中，状态有更新
- **completed**：成功结束
- **failed**：异常结束

## 错误处理

失败时必须汇总：
1. `experiment_status.json` 中的 error / traceback
2. `logs/train.log` 最后 100 行
3. 给出最可能原因和修复建议

## 注意事项

1. 严禁多个实验共享日志、状态、输出文件
2. Windows 工具安装前必须先检测是否已存在
3. psmux 命令必须先查 help/README，不可臆造
4. 所有路径必须使用绝对路径