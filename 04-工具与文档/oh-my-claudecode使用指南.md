# oh-my-claudecode (OMC) 完整使用指南

> 版本：v4.11.5 | 适配环境：Windows PowerShell + Zellij + WSL2

------

## 目录

1. [安装配置](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#安装配置)
2. [核心原则](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#核心原则)
3. [代理目录](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#代理目录)
4. [技能系统](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#技能系统)
5. [工具集](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#工具集)
6. [团队管道](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#团队管道)
7. [执行协议](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#执行协议)
8. [验证机制](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#验证机制)
9. [提交协议](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#提交协议)
10. [钩子系统](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#钩子系统)
11. [状态管理](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#状态管理)
12. [Zellij 集成方案](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#zellij-集成方案)
13. [典型工作流](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#典型工作流)
14. [快速参考卡片](https://claude.ai/chat/f20ba1aa-717c-4f65-a9c2-21e7aac31efd#快速参考卡片)

------

## 安装配置

### 首次安装

```bash
# 在 Claude Code 里说：
setup omc

# 或直接运行：
/oh-my-claudecode:omc-setup
```

### 更新到最新版

```bash
omc update
```

### 系统诊断

```bash
/oh-my-claudecode:omc-doctor
```

### 禁用开关

```bash
# 禁用整个 OMC
DISABLE_OMC=1

# 跳过指定钩子（逗号分隔）
OMC_SKIP_HOOKS=PreToolUse,PostToolUse
```

### 配置文件位置

| 路径                                         | 内容       |
| -------------------------------------------- | ---------- |
| `~/.claude/CLAUDE.md`                        | 主配置文件 |
| `~/.claude/agents/*.md`                      | 代理定义   |
| `~/.claude/plugins/marketplaces/omc/skills/` | 技能目录   |
| `.omc/state/`                                | 运行状态   |
| `.omc/notepad.md`                            | 便签       |
| `.omc/project-memory.json`                   | 项目记忆   |
| `.omc/plans/`                                | 计划文件   |
| `.omc/research/`                             | 研究文件   |
| `.omc/logs/`                                 | 日志文件   |

------

## 核心原则

| 原则             | 说明                                       |
| ---------------- | ------------------------------------------ |
| **代理委托**     | 专业工作交给最合适的代理，不要什么都自己做 |
| **证据优先**     | 声明完成前必须验证结果                     |
| **轻量路径**     | 选择保证质量的最轻量方案                   |
| **官方文档优先** | 用 SDK/框架/API 前先查官方文档             |

### 什么时候委托，什么时候直接做

```
✅ 委托给代理：
  - 多文件修改、重构
  - 调试、代码审查
  - 规划、研究、验证

✅ 直接处理：
  - 简单操作、小澄清
  - 单个命令执行
```

### 模型路由规则

| 模型     | 适用场景           | 特点     |
| -------- | ------------------ | -------- |
| `haiku`  | 快速查找、轻量代理 | 最快最省 |
| `sonnet` | 标准开发、代理协调 | 均衡     |
| `opus`   | 架构决策、深度分析 | 最强最贵 |

------

## 代理目录

所有代理调用格式：`oh-my-claudecode:<代理名>`

### 探索与分析类

| 代理      | 模型   | 用途                   | 典型场景                     |
| --------- | ------ | ---------------------- | ---------------------------- |
| `explore` | haiku  | 快速代码库搜索         | "帮我找找哪里处理了登录逻辑" |
| `analyst` | opus   | 需求分析、隐藏风险识别 | 新功能上线前评估风险         |
| `tracer`  | sonnet | 证据驱动的因果追踪     | "为什么这个 bug 会出现"      |

### 规划与架构类

| 代理        | 模型 | 用途               | 典型场景         |
| ----------- | ---- | ------------------ | ---------------- |
| `planner`   | opus | 实现计划制定       | 开始编码前先规划 |
| `architect` | opus | 系统设计、架构决策 | 重大架构选型     |

### 实施与调试类

| 代理       | 模型   | 用途               | 典型场景          |
| ---------- | ------ | ------------------ | ----------------- |
| `executor` | sonnet | 代码实现执行       | 执行已规划的任务  |
| `debugger` | sonnet | 根因分析、错误修复 | 线上 bug 快速定位 |

> 复杂实现任务可以指定用 opus：`/team 1:executor(opus) "重构认证模块"`

### 审查与验证类

| 代理                | 模型   | 用途                 | 典型场景           |
| ------------------- | ------ | -------------------- | ------------------ |
| `verifier`          | sonnet | 完成验证             | 任务结束前确认     |
| `code-reviewer`     | opus   | 代码质量审查         | PR 合并前          |
| `security-reviewer` | sonnet | 安全漏洞检测         | 涉及用户数据的功能 |
| `critic`            | opus   | 计划与代码批判性审查 | 重要方案二次确认   |

### 测试与 QA 类

| 代理            | 模型   | 用途         | 典型场景       |
| --------------- | ------ | ------------ | -------------- |
| `test-engineer` | sonnet | 测试策略设计 | 新模块上线前   |
| `qa-tester`     | sonnet | CLI 交互测试 | 命令行工具验证 |

### 专业工具类

| 代理                  | 模型   | 用途           | 典型场景          |
| --------------------- | ------ | -------------- | ----------------- |
| `designer`            | sonnet | UI/UX 设计开发 | 前端页面设计      |
| `writer`              | haiku  | 技术文档撰写   | README、注释      |
| `scientist`           | sonnet | 数据分析研究   | PISFM 实验分析    |
| `document-specialist` | sonnet | 外部文档查询   | 不确定 SDK 用法时 |
| `git-master`          | sonnet | Git 操作专家   | 复杂 git 操作     |
| `code-simplifier`     | opus   | 代码简化重构   | 历史遗留代码清理  |

------

## 技能系统

调用格式：`/oh-my-claudecode:<技能名>`

### 工作流技能

| 技能             | 触发关键词             | 用途           | 说明               |
| ---------------- | ---------------------- | -------------- | ------------------ |
| `autopilot`      | 说 "autopilot"         | 自主端到端执行 | 给任务，全自动跑完 |
| `ralph`          | 说 "ralph"             | RALPH 模式执行 | 结构化执行循环     |
| `ultrawork`      | 说 "ulw"               | 并行任务执行   | 多任务同时跑       |
| `team`           | 显式调用               | 团队编排       | 多代理协作         |
| `plan`           | 说 "plan" 或 "ralplan" | 规划模式       | 执行前先规划       |
| `ultraqa`        | 显式调用               | 快速问答       | 轻量问答场景       |
| `deep-interview` | 说 "deep interview"    | 深度访谈       | 需求深挖           |

### 调度技能

| 技能               | 用途                            |
| ------------------ | ------------------------------- |
| `ccg`              | 跨上下文调度                    |
| `ralplan`          | RALPLAN 结构化规划              |
| `sciomc`           | 科学计算模式（适合 PISFM 实验） |
| `external-context` | 外部上下文注入                  |
| `deepinit`         | 深度初始化                      |

### 工具技能

| 技能                      | 触发关键词             | 用途                        |
| ------------------------- | ---------------------- | --------------------------- |
| `ask`                     | —                      | 询问外部 AI（Codex/Gemini） |
| `cancel`                  | —                      | 取消当前执行模式            |
| `learner`                 | —                      | 学习模式                    |
| `hud`                     | —                      | 状态仪表盘                  |
| `trace`                   | —                      | 追踪分析                    |
| `omc-setup`               | —                      | 安装配置                    |
| `mcp-setup`               | —                      | MCP 服务器配置              |
| `omc-doctor`              | —                      | 系统诊断                    |
| `skill`                   | —                      | 技能管理                    |
| `writer-memory`           | —                      | 记忆写入                    |
| `configure-notifications` | —                      | 通知配置                    |
| `ai-slop-cleaner`         | "deslop" / "anti-slop" | 清理 AI 废话风格代码        |

------

## 工具集

### 外部 AI 调用

```bash
# 团队模式指定代理数量
/team N:executor "任务描述"

# 调用外部 AI
omc team N:codex "任务"
omc team N:gemini "任务"
omc ask claude
omc ask codex
omc ask gemini

# 跨上下文调度
/ccg
```

### 状态管理工具

| 工具                | 用途             |
| ------------------- | ---------------- |
| `state_read`        | 读取当前模式状态 |
| `state_write`       | 写入模式状态     |
| `state_clear`       | 清除模式状态     |
| `state_list_active` | 列出所有活跃模式 |
| `state_get_status`  | 获取详细状态     |

### 团队管理工具

| 工具          | 用途             |
| ------------- | ---------------- |
| `TeamCreate`  | 创建团队         |
| `TeamDelete`  | 删除团队         |
| `SendMessage` | 发消息给指定代理 |
| `TaskCreate`  | 创建任务         |
| `TaskList`    | 列出任务         |
| `TaskGet`     | 获取任务详情     |
| `TaskUpdate`  | 更新任务状态     |

### 记忆与便签工具

| 工具                           | 用途               |
| ------------------------------ | ------------------ |
| `notepad_read`                 | 读取便签           |
| `notepad_write_priority`       | 写入永久优先级便签 |
| `notepad_write_working`        | 写入工作便签       |
| `notepad_write_manual`         | 写入手动便签       |
| `project_memory_read`          | 读取项目记忆       |
| `project_memory_write`         | 写入项目记忆       |
| `project_memory_add_note`      | 添加笔记           |
| `project_memory_add_directive` | 添加指令           |

### 代码智能工具

| 工具                  | 用途            |
| --------------------- | --------------- |
| `lsp_hover`           | 查看符号文档    |
| `lsp_goto_definition` | 跳转定义        |
| `lsp_find_references` | 查找引用        |
| `lsp_diagnostics`     | 查看诊断信息    |
| `ast_grep_search`     | AST 语法搜索    |
| `ast_grep_replace`    | AST 语法替换    |
| `python_repl`         | Python 交互执行 |

------

## 团队管道

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  team-plan  │───▶│  team-prd   │───▶│  team-exec  │───▶│ team-verify │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                              ┌─────────────────┘
                                              ▼
                                         ┌─────────────┐
                                         │  team-fix   │◀── 循环（有最大次数限制）
                                         └─────────────┘
```

### team ralph 模式

`team ralph` 把团队管道和 RALPH 模式连接起来，适合需要持续迭代的复杂任务。

------

## 执行协议

### 广泛请求处理流程

```
1. explore 探索代码库
2. planner 制定计划
3. 并行执行 2+ 个独立任务（ultrawork）
4. 后台运行构建/测试
5. verifier 验证结果
```

### 作者与审查分离原则

```
❌ 禁止：同一上下文中自我批准（写完自己说"没问题"）

✅ 正确做法：
  写作通道 → 创建/修订内容
  审查通道 → 用 code-reviewer 或 verifier 独立评估
```

### 完成前检查清单

```
✓ 无待处理任务
✓ 测试全部通过
✓ verifier 证据收集完成
```

------

## 验证机制

```
时机：声明"完成"之前必须验证

规模匹配：
  小任务   → haiku 验证
  标准任务 → sonnet 验证
  大/安全  → opus 验证

验证失败：继续迭代，不允许强行声明完成
```

------

## 提交协议

### Git Trailers 格式

```
<type>: <描述>

<可选正文>

Constraint: 影响决策的活跃约束
Rejected: 考虑的替代方案 | 拒绝原因
Directive: 未来修改者的警告
Confidence: high | medium | low
Scope-risk: narrow | moderate | broad
Not-tested: 未覆盖的边缘场景
```

### 示例

```
fix(auth): prevent silent session drops during long-running ops

Auth service returns inconsistent status codes on token expiry,
so the interceptor catches all 4xx and triggers inline refresh.

Constraint: Auth service does not support token introspection
Constraint: Must not add latency to non-expired-token paths
Rejected: Extend token TTL to 24h | security policy violation
Rejected: Background refresh on timer | race condition
Confidence: high
Scope-risk: narrow
Directive: Error handling is intentionally broad — do not narrow without verifying upstream
Not-tested: Auth service cold-start latency >500ms
```

------

## 钩子系统

### 钩子类型

| 类型          | 触发时机   | 典型用途             |
| ------------- | ---------- | -------------------- |
| `PreToolUse`  | 工具执行前 | 参数验证、权限检查   |
| `PostToolUse` | 工具执行后 | 自动格式化、结果检查 |
| `Stop`        | 会话结束时 | 最终验证、清理       |

### 钩子注入标签

```xml
<!-- 继续执行信号 -->
<hook success: Success>

<!-- 触发指定技能 -->
<MAGIC KEYWORD: 技能名>

<!-- ralph/ultrawork 活跃标志 -->
The boulder never stops
```

### 持久化记忆标签

```xml
<!-- 7天记忆 -->
<remember>内容</remember>

<!-- 永久记忆 -->
<remember priority>内容</remember>
```

------

## 状态管理

### 状态文件路径

| 路径                               | 内容       |
| ---------------------------------- | ---------- |
| `.omc/state/`                      | 状态根目录 |
| `.omc/state/sessions/{sessionId}/` | 会话级状态 |
| `.omc/notepad.md`                  | 便签内容   |
| `.omc/project-memory.json`         | 项目记忆   |
| `.omc/plans/`                      | 规划文件   |
| `.omc/research/`                   | 研究输出   |
| `.omc/logs/`                       | 运行日志   |

------

## Zellij 集成方案

### 环境说明

| 环境               | Zellij 集成深度      | 推荐度 |
| ------------------ | -------------------- | ------ |
| Windows PowerShell | 手动集成，无原生支持 | ⭐⭐⭐    |
| WSL2 Ubuntu        | 原生完整支持         | ⭐⭐⭐⭐⭐  |

------

### 方案一：PowerShell 侧（当前主力环境）

#### 安装 Zellij

```powershell
scoop bucket add extras
scoop install zellij
```

#### 配置 PowerShell Profile

```powershell
# 打开 profile
notepad $PROFILE
```

加入以下内容：

```powershell
# ===== Zellij + OMC 集成 =====

# 检测是否在 Zellij 会话内
function Test-InZellij {
    return $null -ne $env:ZELLIJ
}

# 启动 Claude Code（自动进入 Zellij）
function Start-Claude {
    param([Parameter(ValueFromRemainingArguments)]$args)
    if (Test-InZellij) {
        claude @args
    } else {
        # 在新 Zellij 会话里启动 claude
        zellij run --name "claude" -- claude @args
    }
}

# OMC 快捷函数
function Invoke-OMC {
    param(
        [string]$Skill,
        [Parameter(ValueFromRemainingArguments)]$Rest
    )
    claude "/oh-my-claudecode:$Skill $Rest"
}

# 常用别名
Set-Alias cc    Start-Claude
Set-Alias omc   Invoke-OMC

# OMC 技能快捷别名
function omc-plan     { claude "/oh-my-claudecode:plan $args" }
function omc-team     { claude "/oh-my-claudecode:team $args" }
function omc-auto     { claude "/oh-my-claudecode:autopilot $args" }
function omc-debug    { claude "/oh-my-claudecode:debugger $args" }
function omc-review   { claude "/oh-my-claudecode:code-reviewer $args" }
function omc-doctor   { claude "/oh-my-claudecode:omc-doctor" }
```

#### Zellij 布局配置（推荐用于 OMC 多代理）

创建 `~/.config/zellij/layouts/omc.kdl`：

```kdl
layout {
    pane split_direction="vertical" {
        // 左侧主窗格：Claude Code 主会话
        pane {
            name "claude-main"
            command "pwsh"
            args "-NoExit" "-Command" "claude"
        }
        // 右侧分为上下两个
        pane split_direction="horizontal" {
            // 右上：代码/文件查看
            pane {
                name "editor"
                command "pwsh"
            }
            // 右下：日志/输出
            pane {
                name "logs"
                command "pwsh"
                args "-NoExit" "-Command" "Get-Content .omc/logs/ -Wait 2>/dev/null"
            }
        }
    }
    // 底部状态栏
    pane size=1 borderless=true {
        plugin location="zellij:status-bar"
    }
}
```

启动 OMC 专属布局：

```powershell
zellij --layout ~/.config/zellij/layouts/omc.kdl
```

或加到 profile 里：

```powershell
function Start-OMCWorkspace {
    zellij --layout "$HOME\.config\zellij\layouts\omc.kdl"
}
Set-Alias omcws Start-OMCWorkspace
```

#### Zellij 常用键位（PowerShell 侧）

| 操作           | 快捷键            |
| -------------- | ----------------- |
| 新建窗格（右） | `Ctrl+p` → `r`    |
| 新建窗格（下） | `Ctrl+p` → `d`    |
| 切换窗格       | `Ctrl+p` → 方向键 |
| 新建标签页     | `Ctrl+t` → `n`    |
| 重命名标签页   | `Ctrl+t` → `r`    |
| 全屏当前窗格   | `Ctrl+p` → `f`    |
| 关闭窗格       | `Ctrl+p` → `x`    |
| 分离会话       | `Ctrl+o` → `d`    |
| 重新连接会话   | `zellij attach`   |

------

### 方案二：WSL2 侧（推荐，OMC 完整支持）

#### 安装 Zellij（WSL2 Ubuntu）

```bash
# 方式一：脚本安装
bash <(curl -L https://zellij.dev/launch)

# 方式二：cargo 安装（如果已有 rust）
cargo install zellij

# 方式三：下载二进制
wget https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz
tar -xvf zellij-*.tar.gz
sudo mv zellij /usr/local/bin/
```

#### 配置 Claude Code 使用 Zellij（WSL2）

```bash
# ~/.bashrc 或 ~/.zshrc 加入
export CLAUDE_CODE_USE_TERMINAL_MULTIPLEXER=1
export CLAUDE_CODE_TERMINAL_MULTIPLEXER=zellij
```

#### WSL2 侧 Zellij 布局

创建 `~/.config/zellij/layouts/omc.kdl`：

```kdl
layout {
    pane split_direction="vertical" {
        pane {
            name "claude-main"
            size "60%"
            command "zsh"
            args "-c" "claude; zsh"
        }
        pane split_direction="horizontal" {
            pane {
                name "workspace"
                command "zsh"
            }
            pane {
                name "omc-logs"
                size "30%"
                command "zsh"
                args "-c" "tail -f .omc/logs/*.log 2>/dev/null || zsh"
            }
        }
    }
    pane size=1 borderless=true {
        plugin location="zellij:status-bar"
    }
}
```

#### 从 PowerShell 直接启动 WSL2 + Zellij + OMC

```powershell
# 在 PowerShell profile 里加入
function Start-WSLOMCWorkspace {
    wsl -e zsh -c "zellij --layout ~/.config/zellij/layouts/omc.kdl"
}
Set-Alias wslomcws Start-WSLOMCWorkspace
```

------

### Zellij 会话管理（通用）

```bash
# 列出所有会话
zellij list-sessions

# 连接到已有会话
zellij attach <会话名>

# 新建命名会话
zellij --session omc-project

# 删除会话
zellij delete-session <会话名>

# 在后台运行命令（新窗格）
zellij run -- claude "/oh-my-claudecode:autopilot"

# 在指定方向新建窗格并运行
zellij run --direction right -- tail -f .omc/logs/latest.log
```

------

## 典型工作流

### 场景一：开发新功能（完整流程）

```bash
# 1. 启动 OMC 工作区
omcws  # 或 wslomcws

# 2. 深度初始化（了解项目）
/oh-my-claudecode:deepinit

# 3. 规划
/oh-my-claudecode:plan

# 4. 团队执行
/oh-my-claudecode:team

# 5. 代码审查
/oh-my-claudecode:code-reviewer

# 6. 安全检查（如涉及用户数据）
/oh-my-claudecode:security-reviewer
```

### 场景二：调试 Bug

```bash
# 快速追踪根因
/oh-my-claudecode:tracer

# 或直接调试
/oh-my-claudecode:debugger

# 修复后验证
/oh-my-claudecode:verifier
```

### 场景三：PISFM 科学实验（BiMamba/hyperspectral）

```bash
# 科学计算模式
/oh-my-claudecode:sciomc

# 数据分析
/oh-my-claudecode:scientist

# 实验结果写入记忆
# 使用 notepad_write_priority 保存实验结论
```

### 场景四：代码重构

```bash
# 1. 分析现状
/oh-my-claudecode:analyst

# 2. 制定重构计划
/oh-my-claudecode:plan

# 3. 批判性审查计划
/oh-my-claudecode:critic

# 4. 执行（复杂用 opus）
/team 1:executor(opus) "按计划重构认证模块"

# 5. 简化清理
/oh-my-claudecode:code-simplifier
```

### 场景五：不确定某个 SDK 用法

```bash
# 先查文档，不要瞎猜
/oh-my-claudecode:document-specialist

# 查完再让 executor 实现
/team 1:executor "按文档实现 XXX"
```

### 场景六：Zellij 多窗格并行监控

```
窗格1（左主）：claude 主会话，运行 OMC autopilot
窗格2（右上）：实时查看被修改的文件
窗格3（右下）：tail -f .omc/logs/latest.log 监控 OMC 状态
# 在 Zellij 内手动分配
# 主窗格：
claude

# 右上新窗格（Ctrl+p → r）：
watch -n2 git diff --stat

# 右下新窗格（Ctrl+p → d）：
tail -f .omc/logs/*.log
```

------

## 快速参考卡片

### 技能一览

```bash
/oh-my-claudecode:autopilot      # 全自动执行
/oh-my-claudecode:plan           # 规划模式
/oh-my-claudecode:ralph          # RALPH 模式
/oh-my-claudecode:ultrawork      # 并行执行（说 "ulw"）
/oh-my-claudecode:team           # 团队编排
/oh-my-claudecode:deep-interview # 深度访谈需求
/oh-my-claudecode:cancel         # 取消当前模式
/oh-my-claudecode:hud            # 查看状态仪表盘
/oh-my-claudecode:trace          # 追踪分析
/oh-my-claudecode:omc-doctor     # 系统诊断
/oh-my-claudecode:ai-slop-cleaner # 清理AI废话（说 "deslop"）
```

### 代理一览

```bash
/oh-my-claudecode:explore         # 搜索代码库
/oh-my-claudecode:analyst         # 需求/风险分析
/oh-my-claudecode:planner         # 制定计划
/oh-my-claudecode:architect       # 架构设计
/oh-my-claudecode:executor        # 执行代码
/oh-my-claudecode:debugger        # 调试
/oh-my-claudecode:verifier        # 验证完成
/oh-my-claudecode:code-reviewer   # 代码审查
/oh-my-claudecode:security-reviewer # 安全审查
/oh-my-claudecode:test-engineer   # 测试策略
/oh-my-claudecode:git-master      # Git 操作
/oh-my-claudecode:writer          # 写文档
/oh-my-claudecode:scientist       # 数据分析
/oh-my-claudecode:document-specialist # 查外部文档
```

### PowerShell 别名速查（配置后）

```powershell
cc              # 启动 Claude（自动进 Zellij）
omcws           # 启动 OMC 工作区（Zellij 布局）
wslomcws        # WSL2 侧启动 OMC 工作区
omc-plan        # 规划模式
omc-team        # 团队模式
omc-auto        # autopilot 模式
omc-debug       # 调试代理
omc-review      # 代码审查
omc-doctor      # 系统诊断
```

### 记忆标签速查

```xml
<remember>临时记住7天</remember>
<remember priority>永久记住</remember>
```

### 钩子信号速查

```xml
<hook success: Success>   <!-- 继续 -->
The boulder never stops   <!-- ralph/ulw 活跃 -->
```

------

## 版本信息

| 项目        | 值                                   |
| ----------- | ------------------------------------ |
| 当前版本    | v4.9.0                               |
| 最新版本    | v4.11.5                              |
| 更新命令    | `omc update`                         |
| Zellij 版本 | 最新稳定版（`scoop install zellij`） |

# OMC 实战场景手册

> 针对：深度学习研究 + SpringBoot接单 + Python学习 + Obsidian知识库

------

## 场景一：PISFM 科研实验（调参 / 分析 / 写报告）

### 典型痛点

- 跑完实验不知道怎么分析结果
- 消融实验结果要写成论文段落
- 调参没有系统性，靠感觉

### 最佳 OMC 流程

#### Step 1：实验前——让 OMC 帮你设计实验方案

```
你说：
"我要做 BiMamba encoder 的消融实验，变量是：
有无预训练权重（wo_pretrain）、有无物理信息嵌入
数据集：LUCAS，seeds: 42/123/2024/31415/2718
帮我设计完整实验方案"

/oh-my-claudecode:scientist
```

OMC 会用 `scientist` 代理输出：实验分组、控制变量表、预期结果假设。

#### Step 2：实验中——挂机跑，不用守着

```bash
# 在 Zellij 里开两个窗格
# 窗格1：跑训练脚本
python train.py --config configs/pisfm_base.yaml --seed 42

# 窗格2：让 OMC 监控日志并分析
# 在 claude 里说：
"监控 ./logs/train.log，每当出现 epoch loss 就记录到便签"

/oh-my-claudecode:autopilot
# 然后加：notepad_write_working 自动记录
```

#### Step 3：实验后——结果分析

```
把结果贴给 claude，说：

"以下是5组seed的RMSE结果：
seed42: 0.312, seed123: 0.298, seed2024: 0.321...
对比 wo_pretrain 变体，分析预训练权重的贡献"

/oh-my-claudecode:scientist
```

输出：均值±标准差、统计显著性分析、结论段落。

#### Step 4：写论文段落

```
"把上面的分析结果写成 IEEE 格式的 Ablation Study 段落，
中英文各一份"

/oh-my-claudecode:writer
```

#### Step 5：把结论永久存入记忆

```
在 claude 里说：
"把这次实验结论存入项目记忆"

# OMC 会用：
project_memory_add_note
```

下次继续实验，直接能读取上次结论。

### 一句话记忆

```
实验设计→scientist  分析结果→scientist  写段落→writer  存结论→project_memory
```

------

## 场景二：SpringBoot + Vue 接单开发

### 典型痛点

- 客户需求描述模糊，怕理解偏
- 一个人写前后端，容易顾此失彼
- 代码写完不知道有没有安全漏洞

### 最佳 OMC 流程

#### Step 1：需求阶段——深度挖掘客户真实需求

```
把客户消息贴进来，说：
"客户在小红书找我做一个xxx系统，需求如下：[粘贴原文]
帮我深度分析需求，找出模糊点和隐藏风险"

/oh-my-claudecode:deep-interview
# 然后：
/oh-my-claudecode:analyst
```

输出：需求清单、模糊点列表、你需要回问客户的问题。

#### Step 2：架构阶段——设计技术方案

```
"基于以上需求，设计 SpringBoot + Vue3 的技术方案
要求：Scoop 环境开发，部署到客户服务器"

/oh-my-claudecode:architect
```

输出：模块划分、接口设计、数据库 ER 图建议、技术选型理由。

#### Step 3：规划阶段——拆分任务

```
/oh-my-claudecode:plan
```

输出：按天的开发计划，哪些可以并行，估时。

#### Step 4：开发阶段——并行跑前后端

```
# ultrawork 并行执行
说 "ulw" 或：
/oh-my-claudecode:ultrawork

# 然后描述两个并行任务：
任务A: "实现用户认证模块 SpringBoot 后端，JWT + Spring Security"
任务B: "实现 Vue3 登录页，对接上面的接口"
```

两个 executor 代理同时跑，比顺序执行快一倍。

#### Step 5：安全审查——交付前必做

```
/oh-my-claudecode:security-reviewer
```

重点检查：SQL注入、越权访问、敏感信息泄露。接单项目必须过这关。

#### Step 6：代码审查

```
/oh-my-claudecode:code-reviewer
```

#### Step 7：Git 提交

```
/oh-my-claudecode:git-master
# 自动生成规范的 commit message + trailers
```

### 一句话记忆

```
需求→deep-interview+analyst  架构→architect  开发→ulw并行  交付→security-reviewer
```

------

## 场景三：Python 学习 / LeetCode 调试

### 典型痛点

- 做 LeetCode 老是忘记 `i += 1`，卡在 while 循环
- 看懂了但说不清楚，笔记不知道怎么记
- 想要 Obsidian 格式的笔记，每次手动整理很烦

### 最佳 OMC 流程

#### Step 1：遇到不会的题——先让 OMC 引导而不是直接给答案

```
"LeetCode 283 移动零，我的思路是双指针，但卡住了
帮我引导，不要直接给答案"

/oh-my-claudecode:deep-interview
# 让它问你问题，引导你想清楚
```

#### Step 2：代码写完有 bug——追踪根因

```
把你的代码贴进来，说：
"这段代码有 bug，帮我找根因，
重点检查 while 循环里有没有漏 i += 1"

/oh-my-claudecode:tracer
```

输出：bug 位置、为什么会犯这个错、如何避免。

#### Step 3：题做完——生成 Obsidian 笔记

```
"把这道题的解题过程整理成 Obsidian 笔记
要求：
- 大白话中文
- 包含数字举例
- LaTeX 公式
- Callout 语法标注易错点
- 标签：#LeetCode #双指针 #Python"

/oh-my-claudecode:writer
```

直接复制进 Obsidian，不用再手动整理。

#### Step 4：学完一个专题——生成总结卡片

```
"把这周学的双指针、滑动窗口整理成对比表格
Obsidian 格式，包含：适用场景、模板代码、经典题目"

/oh-my-claudecode:writer
```

#### Step 5：把易错模式存入记忆

```
<remember priority>
Python while 循环易错：循环体末尾必须有 i += 1，
否则死循环。每次写 while 先把更新语句占位。
</remember>
```

Claude 会永久记住，下次你犯同样错误时主动提醒。

### 一句话记忆

```
引导思路→deep-interview  找bug→tracer  生成笔记→writer  记易错→remember priority
```

------

## 场景四：Obsidian 知识库管理

### 典型痛点

- 学了很多，但笔记散乱，找不到
- 想整理但不知道从哪里开始
- 新学的内容和旧笔记没有关联

### 最佳 OMC 流程

#### Step 1：整理散乱笔记——先探索现状

```
"扫描我的 Obsidian vault，分析笔记结构，
找出：孤立笔记、重复内容、缺少标签的文件"

/oh-my-claudecode:explore
```

#### Step 2：建立知识图谱——规划笔记结构

```
"基于我的 PISFM 研究 + 深度学习学习路径，
设计一套 Obsidian 文件夹结构和 MOC（内容地图）"

/oh-my-claudecode:architect
```

#### Step 3：批量生成笔记模板

```
"为以下场景各生成一个 Obsidian 模板：
1. 深度学习论文笔记
2. LeetCode 题目笔记
3. 实验记录（BiMamba实验）
4. 接单项目记录"

/oh-my-claudecode:writer
```

#### Step 4：把新学内容快速转化为笔记

```
# 把学习材料（PDF/截图/文字）丢给 claude，说：
"把这段内容转化为 Obsidian 笔记
风格：大白话，数字举例，LaTeX，Callout高亮重点
关联已有笔记：[[反向传播]] [[梯度下降]]"

/oh-my-claudecode:writer
```

#### Step 5：每日知识库维护（配合 Daily Note）

```
"今天学了 Mamba 状态空间模型，做了3道LeetCode
帮我生成今天的 Daily Note，包含：
- 今日学习总结
- 明日计划
- 新增知识点的笔记链接"

/oh-my-claudecode:writer
```

### 一句话记忆

```
扫描结构→explore  规划体系→architect  写笔记→writer  每日维护→writer+daily
```

------

## 场景五：挂机自动执行（睡前丢任务，早上看结果）

### 核心思路

> 睡前把任务描述清楚 → autopilot 全自动跑 → 早上看 `.omc/notepad.md` 看结果

### 方案 A：单任务挂机（最简单）

```bash
# 1. 开 Zellij 会话并命名
zellij --session overnight

# 2. 在 claude 里说：
"请用 autopilot 模式完成以下任务，完成后把结果写入便签：
[详细描述任务]
要求：遇到不确定的地方，选择保守方案，不要问我"

/oh-my-claudecode:autopilot
```

然后分离会话直接睡：

```bash
# Ctrl+o → d  分离 Zellij 会话
# 早上重新连接：
zellij attach overnight
# 或看便签：
cat .omc/notepad.md
```

### 方案 B：多任务并行挂机（ultrawork）

```bash
# 睡前在 claude 里说：
"ulw 模式，并行执行以下3个任务，全部完成后写入便签：

任务1：重构 UserService，提取公共方法，保持接口不变
任务2：为所有 Controller 补全 Swagger 注释
任务3：生成完整的单元测试，覆盖率目标80%

遇到冲突选保守方案，不要修改数据库相关代码"

# 自动触发：
/oh-my-claudecode:ultrawork
```

### 方案 C：科研任务挂机（PISFM 专用）

```bash
# 睡前说：
"autopilot 模式，完成以下科研任务：

1. 读取 ./results/ablation_*.csv
2. 计算每组实验的均值和标准差
3. 生成对比表格（Markdown格式）
4. 写出消融实验分析段落（中英文）
5. 把结论存入项目记忆

完成后在便签写：✅完成 + 关键数字"
```

### 挂机任务描述模板（复制使用）

```
autopilot 模式，任务如下：

【目标】：[一句话说清楚要达到什么结果]

【具体步骤】：
1. [步骤1]
2. [步骤2]
3. [步骤3]

【约束条件】：
- 不要修改：[哪些文件/模块不能动]
- 遇到不确定：选择保守方案，不要中断等我
- 不要安装新的依赖（或：可以用 pip install）

【完成标志】：
- 把结果摘要写入便签
- 关键数字/结论用 ✅ 标出
```

### 挂机注意事项

| 注意点                 | 说明                                                   |
| ---------------------- | ------------------------------------------------------ |
| **描述要足够详细**     | 任务描述越清晰，跑偏概率越低                           |
| **明确禁止边界**       | 写清楚哪些文件不能动                                   |
| **让它选保守方案**     | 说"遇到不确定选保守"，不然它会乱改                     |
| **用便签收集结果**     | 说"完成后写入便签"，早上 `cat .omc/notepad.md`         |
| **用 Zellij 保持会话** | 分离会话（Ctrl+o→d），不依赖终端窗口存活               |
| **复杂任务用 team**    | 超复杂任务用 `/oh-my-claudecode:team` 而不是 autopilot |

### 早上检查结果

```bash
# 重连会话
zellij attach overnight

# 看便签（结果摘要）
cat .omc/notepad.md

# 看项目记忆（科研结论）
cat .omc/project-memory.json

# 看运行日志
cat .omc/logs/*.log

# 看 git 记录（有没有提交）
git log --oneline -10
```

------

## 五个场景对比速查

| 场景           | 启动命令         | 核心代理                          | 结果在哪看     |
| -------------- | ---------------- | --------------------------------- | -------------- |
| PISFM实验      | `/omc:scientist` | scientist + writer                | project-memory |
| SpringBoot接单 | 说 "ulw"         | architect + executor×2 + security | git log        |
| LeetCode调试   | `/omc:tracer`    | tracer + writer                   | Obsidian笔记   |
| Obsidian整理   | `/omc:explore`   | explore + writer                  | vault文件      |
| 挂机执行       | `/omc:autopilot` | autopilot（全自动）               | notepad.md     |

------

## 通用开场白模板

每次开始任务前，先告诉 OMC 上下文，效果更好：

```
我是深度学习研究生，当前项目：PISFM（土壤有机碳预测，BiMamba编码器）
开发环境：Windows + Scoop + WSL2 Ubuntu
现在要做的任务：[描述任务]
```

或者让 OMC 读项目记忆：

```
先读取项目记忆，然后开始：[任务]
```