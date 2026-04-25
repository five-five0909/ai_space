# Claude Code 命令大全

> 导出时间：2026-04-17（完整版）

---

## 一、项目级命令（当前项目）

**路径**：`E:\company_place\ai_space\.claude\commands\`

| 命令 | 说明 |
|------|------|
| `/long-run-log` | 启动长时间实验，支持后台运行和状态追踪 |
| `/stage-run` | 执行多阶段任务，管理复杂流程 |
| `/check-run` | 检查实验/任务运行状态 |
| `/analyze-run` | 分析实验结果，生成报告 |
| `/install-psmux` | 安装 psmux 进程管理工具 |

---

## 二、全局命令（用户级）

**路径**：`C:\Users\Administrator\.claude\commands\`

### 🔧 开发工具命令

| 命令 | 说明 |
|------|------|
| `/build-fix` | 构建并修复错误 |
| `/tdd` | 测试驱动开发（TDD）工作流 |
| `/test-coverage` | 测试覆盖率分析 |
| `/e2e` | 端到端测试生成与运行 |
| `/code-review` | 代码审查 |
| `/verify` | 验证命令 |
| `/checkpoint` | 检查点命令 |
| `/eval` | 评估命令 |

### 📚 语言/框架专用命令

| 命令 | 说明 |
|------|------|
| `/python-review` | Python 代码审查 |
| `/cpp-build` | C++ 构建修复 |
| `/cpp-review` | C++ 代码审查 |
| `/cpp-test` | C++ TDD 工作流 |
| `/go-build` | Go 构建修复 |
| `/go-review` | Go 代码审查 |
| `/go-test` | Go TDD 工作流 |
| `/rust-build` | Rust 构建修复 |
| `/rust-review` | Rust 代码审查 |
| `/rust-test` | Rust TDD 工作流 |
| `/kotlin-build` | Kotlin/Gradle 构建修复 |
| `/kotlin-review` | Kotlin 代码审查 |
| `/kotlin-test` | Kotlin TDD 工作流 |
| `/gradle-build` | Gradle 构建修复 |

### 🤖 多代理/团队命令

| 命令 | 说明 |
|------|------|
| `/multi-workflow` | 多模型协作工作流 |
| `/multi-plan` | 多模型协作规划 |
| `/multi-execute` | 多模型协作执行 |
| `/multi-frontend` | 前端专注开发 |
| `/multi-backend` | 后端专注开发 |
| `/orchestrate` | 顺序和 tmux/worktree 编排 |
| `/devfleet` | 并行 Claude Code 代理编排 |
| `/parallel` | 多代理管道编排 |

### 📖 文档/知识命令

| 命令 | 说明 |
|------|------|
| `/docs` | 查找当前文档（Context7） |
| `/update-docs` | 更新文档 |
| `/learn` | 提取可复用模式 |
| `/learn-eval` | 从评估中学习模式 |
| `/evolve` | 分析本能并建议改进 |

### 🔄 循环/状态命令

| 命令 | 说明 |
|------|------|
| `/loop` | 定期运行提示/命令 |
| `/loop-start` | 启动循环 |
| `/loop-status` | 循环状态检查 |

### 🎯 技能/本能命令

| 命令 | 说明 |
|------|------|
| `/skill-create` | 创建新技能 |
| `/skill-health` | 技能组合健康检查 |
| `/instinct-status` | 显示学习到的本能 |
| `/instinct-import` | 导入本能 |
| `/instinct-export` | 导出本能 |
| `/promote` | 提升项目级本能 |
| `/prune` | 删除过期的待定本能 |
| `/rules-distill` | 从技能中提取跨领域规则 |

### 🗂️ 项目/会话管理

| 命令 | 说明 |
|------|------|
| `/projects` | 列出已知项目 |
| `/sessions` | 管理 Claude Code 会话历史 |
| `/save-session` | 保存当前会话状态 |
| `/setup-pm` | 设置项目管理 |
| `/pm2` | PM2 初始化 |

### 🔍 分析/优化命令

| 命令 | 说明 |
|------|------|
| `/context-budget` | 分析上下文窗口使用 |
| `/model-route` | 模型路由命令 |
| `/prompt-optimize` | 分析并优化提示词 |
| `/quality-gate` | 质量门检查 |
| `/refactor-clean` | 清理重构 |
| `/harness-audit` | Harness 审计 |

### 🛠️ 其他工具命令

| 命令 | 说明 |
|------|------|
| `/aside` | 回答快速旁注问题 |
| `/claw` | NanoClaw v2 启动 |
| `/update-codemaps` | 更新代码地图 |
| `/plan` | 重述需求、评估风险、规划步骤 |

---

## 三、OMC 插件技能（oh-my-claudecode）

通过 `/oh-my-claudecode:<name>` 或关键词触发。

### 🔄 工作流技能

| 技能 | 关键词触发 | 说明 |
|------|-----------|------|
| `autopilot` | "autopilot" | 全自主执行模式 |
| `ralph` | "ralph" | 自引用循环直到任务完成 |
| `ultrawork` | "ulw" | 并行执行引擎 |
| `team` | - | N 个协调代理共享任务列表 |
| `ccg` | "ccg" | Claude-Codex-Gemini 三模型协作 |
| `ultraqa` | - | QA 循环工作流 |
| `omc-plan` | - | 战略规划 |
| `ralplan` | "ralplan" | 共识规划（别名） |
| `sciomc` | - | 并行科学家编排 |
| `external-context` | - | 并行文档专家调用 |
| `deepinit` | - | 深度代码库初始化 |
| `deep-interview` | "deep interview" | 苏格拉底深度访谈 |
| `ai-slop-cleaner` | "deslop"/"anti-slop" | AI 生成代码清理 |

### 🔧 工具技能

| 技能 | 说明 |
|------|------|
| `ask-codex` | 通过 Codex 查询 |
| `ask-gemini` | 通过 Gemini 查询 |
| `cancel` | 取消活动的 OMC 模式 |
| `learner` | 从任务中提取学习技能 |
| `omc-setup` | OMC 设置和配置 |
| `mcp-setup` | 配置热门 MCP 服务器 |
| `hud` | 配置 HUD 显示选项 |
| `omc-doctor` | OMC 诊断和修复 |
| `omc-help` | OMC 帮助 |
| `trace` | 证据驱动追踪通道 |
| `release` | 自动发布工作流 |
| `project-session-manager` | 管理隔离开发环境 |
| `skill` | 管理本地技能 |
| `writer-memory` | 写作者记忆系统 |
| `ralph-init` | Ralph 初始化 |
| `configure-notifications` | 配置通知集成 |
| `learn-about-omc` | 学习 OMC 相关 |

---

## 四、Claude-mem 插件技能

| 技能 | 说明 |
|------|------|
| `do` | 执行分阶段实现 |
| `knowledge-agent` | 构建和查询知识代理 |
| `mem-search` | 搜索 claude-mem 持久记忆 |
| `make-plan` | 创建详细分阶段实现计划 |
| `timeline-report` | 生成项目旅程报告 |
| `version-bump` | 自动语义版本管理 |
| `smart-explore` | Token 优化结构化代码探索 |

---

## 五、Superpowers 插件技能

| 技能 | 说明 |
|------|------|
| `brainstorming` | 必须在任何复杂任务前使用 |
| `writing-plans` | 有规格/需求时创建实现计划 |
| `executing-plans` | 执行已写好的实现计划 |
| `dispatching-parallel-agents` | 面对 2+ 独立任务时派发并行代理 |
| `requesting-code-review` | 完成任务后请求代码审查 |
| `receiving-code-review` | 接收代码审查反馈 |
| `finishing-a-development-branch` | 实现完成后结束开发分支 |
| `subagent-driven-development` | 执行实现工作时使用子代理 |
| `using-git-worktrees` | 开始特性工作时使用 Git worktree |
| `systematic-debugging` | 遇到 Bug 时系统化调试 |
| `test-driven-development` | 实现功能时使用 TDD |
| `verification-before-completion` | 完成前验证工作 |

---

## 六、内置 CLI 命令

| 命令 | 说明 |
|------|------|
| `/help` | 获取帮助 |
| `/compact` | 压缩上下文 |
| `/clear` | 清除会话 |
| `/resume` | 恢复会话 |
| `/model` | 切换模型 |
| `/thinking` | 切换思考模式 |
| `/fast` | 切换快速模式 |
| `/hooks` | 查看和管理钩子 |
| `/permissions` | 查看和管理权限 |
| `/mcp` | 查看 MCP 服务器 |
| `/cost` | 查看成本统计 |
| `/status` | 查看状态 |
| `/doctor` | 诊断问题 |
| `/init` | 初始化项目 |
| `/git` | Git 操作 |
| `/pr` | PR 操作 |
| `/issue` | Issue 操作 |
| `/review-pr` | 审查 PR |
| `/commit` | 创建提交 |
| `/reload-plugins` | 重新加载插件 |

---

## 七、插件安装指南

### 当前已安装插件

| 插件 | Marketplace | 说明 |
|------|-------------|------|
| `context7` | claude-plugins-official | 实时文档查询 |
| `oh-my-claudecode` | omc | 多代理编排层 |
| `claude-mem` | thedotmack | 持久记忆系统 |
| `superpowers` | claude-plugins-official | 开发工作流技能 |

### 插件安装步骤

#### 1. oh-my-claudecode (OMC)

**GitHub 源**：`https://github.com/Yeachan-Heo/oh-my-claudecode.git`

```bash
# NPM 安装
npm install -g oh-my-claudecode

# 插件安装
/plugin install oh-my-claudecode

# 更新
omc update
```

**配置 settings.json**：

```json
{
  "enabledPlugins": {
    "oh-my-claudecode@omc": true
  },
  "extraKnownMarketplaces": {
    "omc": {
      "source": {
        "source": "git",
        "url": "https://github.com/Yeachan-Heo/oh-my-claudecode.git"
      }
    }
  }
}
```

**初始化**：`/oh-my-claudecode:omc-setup`

---

#### 2. superpowers

**Marketplace**：`claude-plugins-official`

```bash
/plugin install superpowers
```

---

#### 3. context7

**Marketplace**：`claude-plugins-official`

```bash
/plugin install context7
```

**使用**：`/docs <库名>`

---

#### 4. claude-mem

**GitHub 源**：`thedotmack/claude-mem`

```bash
/plugin install claude-mem
```

---

### 插件管理命令

| 命令 | 说明 |
|------|------|
| `/plugin install <name>` | 安装插件 |
| `/plugin uninstall <name>` | 卸载插件 |
| `/plugin list` | 列出已安装插件 |
| `/plugin update <name>` | 更新插件 |
| `/reload-plugins` | 重新加载所有插件 |

---

## 八、Trellis 工作流框架

> **官方文档**：https://docs.trytrellis.app/zh/guide

Trellis 是一个 **AI Agent 工作流管理框架**，用统一的 Markdown 文件结构管理项目规范、任务上下文和会话记忆，自动为 13+ 个 AI 编码平台生成接入文件。

### 8.1 核心目录结构

```
.trellis/
├── spec/           # 项目规范、编码标准、架构指南
├── tasks/          # 任务 PRD、上下文文件、任务状态
├── workspace/      # 开发者个人日志（journal）和会话连续性
├── workflow.md     # 共享工作流规则
├── config.yaml     # 项目配置
├── worktree.yaml   # Git worktree 配置
└── scripts/        # 驱动整个流程的脚本
```

### 8.2 平台接入文件

| 平台 | 生成的文件 |
|------|-----------|
| Claude Code | `.claude/` 目录（hooks、commands、agents、settings.json） |
| Cursor | `.cursor/commands/` |
| Codex | `.agents/skills/` + `.codex/` |
| GitHub Copilot | `.github/copilot/` + `.github/hooks/` |
| 其他 | `AGENTS.md`、`.kilocode/`、`.kiro/` 等 |

### 8.3 安装与初始化

```bash
# 安装 Trellis CLI
npm install -g @mindfoldhq/trellis@latest

# 进入项目目录初始化
cd your-project
trellis init -u fifine

# 同时启用 Claude Code + Cursor
trellis init --cursor -u fifine
```

> **Windows/WSL2 支持**：Trellis v0.3.0+ 支持 Windows，Node.js >= 18

### 8.4 Trellis 命令

| 命令 | 说明 |
|------|------|
| `/trellis:start` | 开始任务，加载相关 spec 和 task 上下文 |
| `/trellis:parallel` | 启动并行任务（git worktree 隔离） |
| `/trellis:finish-work` | 完成任务，更新状态和 journal |
| `/trellis:brainstorm` | 头脑风暴模式，讨论需求和设计 |

### 8.5 三大核心概念

| 概念 | 目录 | 作用 |
|------|------|------|
| **Spec** | `.trellis/spec/` | 沉淀项目规范（编码规范、技术栈、架构） |
| **Task** | `.trellis/tasks/` | 管理开发任务（PRD、目标、检查清单） |
| **Journal** | `.trellis/workspace/<user>/` | 保持会话连续性（决策、踩坑、进度） |

### 8.6 典型工作流示例

#### 论文写作场景

```
.trellis/
├── spec/
│   ├── thesis-conventions.md      # 论文格式规范
│   ├── drawio-standards.md        # draw.io 图表标准
│   └── academic-writing.md        # 学术写作规范
├── tasks/
│   ├── thesis-ch1-introduction.md
│   ├── thesis-ch4-design.md       # 每章一个任务文件
│   └── ...
└── workspace/
    └── fifine/
        └── journal.md             # 论文进度日志
```

#### 接单项目场景

```
.trellis/
├── spec/
│   └── springboot-conventions.md  # 技术栈、代码规范
├── tasks/
│   ├── client-order-module.md     # 订单模块任务
│   ├── client-user-module.md      # 用户模块任务
└── workspace/
    └── fifine/
        └── journal.md             # 项目进度
```

### 8.7 与现有工具链结合

| 工具 | 结合方式 |
|------|---------|
| **Obsidian** | 软链接 `.trellis/` 到 vault，用 Kanban 可视化 |
| **Superpowers** | Trellis 管结构 + Superpowers 管方法论 |
| **OMC** | Trellis 管项目 + OMC 管多代理编排 |

### 8.8 Trellis vs CLAUDE.md

| 方式 | 特点 |
|------|------|
| **CLAUDE.md** | 单文件，越写越大，一次性加载全部上下文 |
| **Trellis** | 分层结构，按需加载：spec（项目级）+ task（任务级）+ journal（个人） |

### 8.9 快速上手清单

1. **安装**：`npm install -g @mindfoldhq/trellis@latest`
2. **初始化**：`trellis init -u fifine`
3. **写 Spec**：把项目规范写进 `.trellis/spec/`
4. **建 Task**：把待办拆成任务文件放进 `.trellis/tasks/`
5. **开始工作**：`/trellis:start <task-name>`
6. **记录进度**：`/trellis:finish-work`
7. **持续迭代**：每次踩坑、规律都写进 spec

---

## 使用方式

1. **斜杠命令**：直接输入 `/命令名`，如 `/code-review`
2. **技能触发**：通过关键词自动触发，如说 "autopilot" 会触发 autopilot 技能
3. **插件技能**：输入 `/插件名:技能名`，如 `/oh-my-claudecode:autopilot`

---

## 文件来源

- 项目命令：`.claude/commands/*.md`
- 全局命令：`~/.claude/commands/*.md`
- 插件技能：各插件的 `skills/` 目录
- 配置文件：`~/.claude/settings.json`
- Trellis 核心：`.trellis/` 目录