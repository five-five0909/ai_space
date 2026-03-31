# AI 终端工具配置指南

> Claude Code & OpenCode · Windows 环境适用

---

## 目录

1. [工具介绍与对比](#1-工具介绍与对比)
2. [Claude Code 完整配置](#2-claude-code-完整配置)
   - [2.2.1 权限系统详解](#221-权限系统详解)
   - [2.10 CLI 启动参数完整说明](#210-cli-启动参数完整说明)
   - [2.11 环境变量速查表](#211-环境变量速查表)
3. [OpenCode 完整配置](#3-opencode-完整配置)
   - [3.2.1 权限系统详解](#321-权限系统详解)
   - [3.8 CLI 启动参数](#38-cli-启动参数)
4. [Oh My OpenCode 插件](#4-oh-my-opencode-插件)
   - [4.5 工作模式详解](#45-工作模式详解)
   - [4.6 内置 Skills 详解](#46-内置-skills-详解)
   - [4.7 内置 MCP 服务器](#47-内置-mcp-服务器)
5. [Oh My ClaudeCode 插件](#5-oh-my-claudecode-插件)
   - [5.3 执行模式详解](#53-执行模式详解)
   - [5.5 内置 Agent 详解](#55-内置-agent-详解)
   - [5.7 自定义技能系统](#57-自定义技能系统)
6. [Everything Claude Code 插件](#6-everything-claude-code-插件)
7. [常见问题与排错](#7-常见问题与排错)
8. [OpenSpec + Superpowers 协同实战指南](#8-openspec--superpowers-协同实战指南)
   - [8.4 OpenSpec 工作流命令](#84-openspec-工作流命令)
   - [8.7 OpenSpec + Superpowers 协同工作流](#87-openspec--superpowers-协同工作流)
9. [权限系统对比速查](#9-权限系统对比速查)

---

## 1. 工具介绍与对比

### Claude Code 是什么？

Anthropic 官方出的 AI 编程助手，在终端里用 Claude 帮你写代码、改代码、调试。

### OpenCode 是什么？

开源的 AI 终端工具，支持多模型（Claude、GPT、MiniMax 等），支持多 Agent 协作。

### 该选哪个？

| 对比项 | Claude Code | OpenCode |
|--------|-------------|----------|
| **维护方** | Anthropic 官方 | 开源社区 |
| **模型支持** | 仅 Claude 系列 | 多模型（Claude/GPT/MiniMax/本地模型） |
| **Agent 系统** | 有，基础 | 强，支持多 Agent 协作 |
| **Hooks 系统** | 有 | 有 |
| **MCP 支持** | 有 | 有 |
| **记忆系统** | 有 | 有 |
| **适合场景** | 日常开发、单模型足够 | 多模型协作、成本敏感、需要 Agent 分工 |

**简单说**：
- 只用 Claude → 选 Claude Code
- 要用多个模型、要 Agent 协作降成本 → 选 OpenCode
- 两个都装不冲突

---

## 2. Claude Code 完整配置

### 2.1 配置文件位置

```
全局配置（所有项目共享）
C:\Users\<你的用户名>\.claude\
├── settings.json       # 主配置文件
├── CLAUDE.md           # 全局指令（每次启动加载）
├── agents\             # 自定义 Agent 定义
├── hooks\              # Hook 脚本
└── memory\             # 记忆存储

项目配置（只对当前项目生效）
你的项目目录\.claude\
├── settings.json       # 项目配置（覆盖全局）
└── CLAUDE.md           # 项目指令

优先级：项目配置 > 全局配置 > 默认值
```

### 2.2 settings.json 主配置

**最简配置**：

```json
{
  "model": "claude-sonnet-4-6"
}
```

**常用完整配置**：

```json
{
  "model": "claude-sonnet-4-6",
  "fallbackModel": "claude-haiku-4-5",

  "permissions": {
    "allow": [
      "Bash(npm *)",
      "Bash(git *)",
      "Bash(node *)",
      "Edit(**)",
      "Read(**)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Read(**/.env)",
      "Read(**/secrets.*)"
    ]
  },

  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "85",
    "MAX_THINKING_TOKENS": "10000"
  },

  "statusLine": {
    "type": "command",
    "command": "node ~/.claude/statusline.mjs"
  }
}
```

**配置项说明**：

| 配置项 | 作用 |
|--------|------|
| `model` | 默认使用的模型 |
| `fallbackModel` | 模型不可用时的备选 |
| `permissions.allow` | 自动允许的操作 |
| `permissions.deny` | 自动拒绝的操作 |
| `env.CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 上下文使用率达多少自动压缩（推荐 85） |
| `statusLine` | 状态栏配置 |

### 2.2.1 权限系统详解

Claude Code 默认会对可能修改系统的操作（文件写入、Bash 命令、MCP 工具）请求权限确认。

#### 权限配置语法

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Bash(git commit *)",
      "Bash(git * main)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl *)",
      "Bash(rm -rf *)",
      "Bash(git push *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

**匹配规则**：

| 模式 | 匹配内容 |
|------|----------|
| `Bash(npm *)` | 所有 npm 开头的命令 |
| `Bash(git * main)` | 对 main 分支的 git 操作 |
| `Read(./.env)` | 特定文件 |
| `Read(./secrets/**)` | secrets 目录下所有文件 |
| `Edit(**)` | 所有文件编辑 |

**优先级**：`deny` > `allow` > 默认询问

#### 自动授权模式（危险）

> ⚠️ **安全警告**：自动授权模式会跳过所有权限检查，可能导致数据丢失、系统损坏或数据泄露。仅限在沙箱环境（无网络访问的容器/虚拟机）中使用。

**方式一：CLI 启动参数**

```bash
# 跳过所有权限检查
claude --dangerously-skip-permissions

# 示例：自动化脚本中运行
claude --dangerously-skip-permissions --print "修复所有 lint 错误"
```

**方式二：Desktop 设置**

1. 打开 Settings → Claude Code
2. 启用 "Allow bypass permissions mode"
3. 重启 Claude Code

**方式三：环境变量**

```json
// settings.json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  }
}
```

> 💡 企业管理员可通过 `disableBypassPermissionsMode` 禁用此功能。

#### 权限模式对比

| 模式 | 触发方式 | 说明 |
|------|----------|------|
| **默认** | 无配置 | 所有敏感操作询问用户 |
| **允许列表** | `permissions.allow` | 匹配的操作自动执行 |
| **拒绝列表** | `permissions.deny` | 匹配的操作自动拒绝 |
| **跳过权限** | `--dangerously-skip-permissions` | 所有操作自动执行（危险） |

#### 安全建议

| 场景 | 推荐配置 |
|------|----------|
| 日常开发 | 使用 `allow` 列表信任常用命令 |
| CI/CD 自动化 | 在隔离环境中使用 `--dangerously-skip-permissions` |
| 团队协作 | 将 `settings.json` 提交到仓库，统一权限规则 |
| 处理敏感数据 | 配置 `deny` 列表保护 `.env`、密钥文件 |

### 2.3 CLAUDE.md 全局指令

每次启动都会加载，用于定义你的编码规范和工作流程。

**示例**：

```markdown
# 全局指令

## 编码规范
- TypeScript 严格模式
- 函数式组件优先
- 错误必须显式处理
- 禁止硬编码密钥

## 工作流程
1. 改代码前先列计划
2. 每改一个文件跑相关测试
3. 提交前做安全检查

## 上下文压缩指令

压缩时必须保留：
- 正在修改的文件路径
- 未完成的任务列表
- 架构决策及原因
- 报错信息原文

可以丢弃：
- 已完成任务的详细过程
- 重复的工具输出
```

> ⚠️ 建议控制在 200 行以内，太长会消耗 token。

### 2.4 Hooks 自动化触发器

**Hook 是什么？** 当某事发生时，自动执行脚本。

**可用 Hook 类型**：

| Hook | 触发时机 | 常见用途 |
|------|----------|----------|
| `SessionStart` | 会话启动时 | 加载配置 |
| `PreToolUse` | 工具执行前 | 参数验证 |
| `PostToolUse` | 工具执行后 | 自动格式化 |
| `PreCompact` | 压缩前 | 备份上下文 |
| `Stop` | 会话结束时 | 保存会话摘要 |

**配置方式**（在 settings.json）：

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "node ~/.claude/hooks/auto-format.mjs",
        "timeout": 5000
      }]
    }],
    "PreCompact": [{
      "matcher": "auto",
      "hooks": [{
        "type": "command",
        "command": "node ~/.claude/hooks/pre-compact-backup.mjs",
        "async": true
      }]
    }],
    "Stop": [{
      "matcher": "auto",
      "hooks": [{
        "type": "command",
        "command": "node ~/.claude/hooks/stop-save-session.mjs",
        "timeout": 10000
      }]
    }]
  }
}
```

**matcher 匹配规则**：

| matcher | 匹配 |
|---------|------|
| `"always"` | 所有工具 |
| `"Bash"` | 所有 Bash 命令 |
| `"Write\|Edit"` | Write 或 Edit 工具 |
| `"Bash(npm *)"` | npm 开头的命令 |

**自动格式化脚本** (`~/.claude/hooks/auto-format.mjs`)：

```javascript
import { execSync } from 'child_process';

let inputData = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => inputData += chunk);
process.stdin.on('end', () => {
  try {
    const input = JSON.parse(inputData || '{}');
    const filePath = input?.tool_input?.file_path || '';

    if (filePath.endsWith('.ts') || filePath.endsWith('.tsx')) {
      execSync(`npx prettier --write "${filePath}"`, { timeout: 5000 });
    } else if (filePath.endsWith('.py')) {
      execSync(`python -m black "${filePath}"`, { timeout: 5000 });
    }
    process.exit(0);
  } catch {
    process.exit(0);
  }
});
```

**压缩前备份脚本** (`~/.claude/hooks/pre-compact-backup.mjs`)：

```javascript
import { readFileSync, mkdirSync, writeFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

let inputData = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => inputData += chunk);
process.stdin.on('end', () => {
  try {
    const input = JSON.parse(inputData || '{}');
    const transcriptPath = input.transcript_path || '';
    if (!transcriptPath) process.exit(0);

    const backupDir = join(homedir(), '.claude', 'backups');
    mkdirSync(backupDir, { recursive: true });

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupFile = join(backupDir, `session-${timestamp}.md`);

    const lines = readFileSync(transcriptPath, 'utf8').split('\n');
    let content = `# 会话备份 ${new Date().toLocaleString('zh-CN')}\n\n`;

    for (const line of lines.slice(-50)) {
      if (!line.trim()) continue;
      try {
        const entry = JSON.parse(line);
        if (entry.type === 'message') {
          content += `### ${entry.role === 'user' ? '用户' : 'Claude'}\n`;
          const text = Array.isArray(entry.content)
            ? entry.content.filter(c => c.type === 'text').map(c => c.text).join('\n')
            : (entry.content || '');
          content += text.slice(0, 500) + '\n\n';
        }
      } catch {}
    }

    writeFileSync(backupFile, content, 'utf8');
    process.stdout.write(`✓ 已备份: ${backupFile}\n`);
    process.exit(0);
  } catch {
    process.exit(0);
  }
});
```

**会话结束保存脚本** (`~/.claude/hooks/stop-save-session.mjs`)：

```javascript
// 会话结束时自动保存摘要，供下次恢复使用
import { readFileSync, mkdirSync, writeFileSync, readdirSync, unlinkSync } from 'fs';
import { join, basename } from 'path';
import { homedir } from 'os';

let inputData = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => inputData += chunk);
process.stdin.on('end', () => {
  try {
    const input = JSON.parse(inputData || '{}');
    const transcriptPath = input.transcript_path || '';
    const cwd = input.cwd || process.cwd();
    const sessionId = input.session_id || 'unknown';

    // 创建 sessions 目录
    const sessionsDir = join(homedir(), '.claude', 'sessions');
    mkdirSync(sessionsDir, { recursive: true });

    // 生成文件名：YYYY-MM-DD-<short-id>-session.tmp
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 10);
    const shortId = sessionId.slice(0, 8).toLowerCase().replace(/[^a-z0-9-]/g, 'a');
    const sessionFile = join(sessionsDir, `${dateStr}-${shortId}-session.tmp`);

    // 构建会话摘要
    let content = `# Session: ${dateStr}\n\n`;
    content += `**Started:** ${input.start_time || 'unknown'}\n`;
    content += `**Last Updated:** ${now.toLocaleString('zh-CN')}\n`;
    content += `**Project:** ${basename(cwd)}\n`;
    content += `**Topic:** ${input.topic || 'Claude Code 会话'}\n\n`;
    content += `---\n\n`;

    // 解析会话记录
    if (transcriptPath) {
      try {
        const lines = readFileSync(transcriptPath, 'utf8').split('\n');
        content += `## 会话摘要\n\n`;

        let userMessages = [];
        let assistantMessages = [];
        let filesModified = new Set();

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const entry = JSON.parse(line);
            if (entry.type === 'message') {
              const text = Array.isArray(entry.content)
                ? entry.content.filter(c => c.type === 'text').map(c => c.text).join('\n')
                : (entry.content || '');

              // 提取修改的文件
              const fileMatches = text.match(/(?:修改|编辑|写入|读取).*?[:：]\s*`?([^\s`]+\.(ts|tsx|js|jsx|py|go|rs|md|json))`?/gi);
              if (fileMatches) {
                fileMatches.forEach(m => {
                  const file = m.match(/[:：]\s*`?([^\s`]+)`?$/);
                  if (file) filesModified.add(file[1]);
                });
              }

              if (entry.role === 'user' && text.trim()) {
                userMessages.push(text.slice(0, 300));
              } else if (entry.role === 'assistant' && text.trim()) {
                assistantMessages.push(text.slice(0, 300));
              }
            }
          } catch {}
        }

        // 用户主要任务
        content += `## 主要任务\n\n`;
        userMessages.slice(-5).forEach((msg, i) => {
          content += `${i + 1}. ${msg}\n`;
        });
        content += '\n';

        // 修改的文件
        if (filesModified.size > 0) {
          content += `## 修改的文件\n\n`;
          filesModified.forEach(f => {
            content += `- \`${f}\`\n`;
          });
          content += '\n';
        }

        // 最近对话
        content += `## 最近对话\n\n`;
        const recentUser = userMessages.slice(-3);
        const recentAssistant = assistantMessages.slice(-3);
        for (let i = 0; i < Math.max(recentUser.length, recentAssistant.length); i++) {
          if (recentUser[i]) content += `**用户:** ${recentUser[i]}\n\n`;
          if (recentAssistant[i]) content += `**Claude:** ${recentAssistant[i]}\n\n`;
        }

      } catch (e) {
        content += `*无法读取会话记录: ${e.message}*\n`;
      }
    }

    content += `---\n\n`;
    content += `> 下次启动时使用 \`/resume-session\` 恢复此会话\n`;

    writeFileSync(sessionFile, content, 'utf8');
    process.stdout.write(`✓ 会话已保存: ${sessionFile}\n`);

    // 只保留最近 10 个会话文件
    try {
      const files = readdirSync(sessionsDir)
        .filter(f => f.endsWith('-session.tmp'))
        .map(f => ({ name: f, path: join(sessionsDir, f) }))
        .sort((a, b) => b.name.localeCompare(a.name));
      files.slice(10).forEach(f => {
        try { unlinkSync(f.path); } catch {}
      });
    } catch {}

    process.exit(0);
  } catch (e) {
    process.stderr.write(`保存失败: ${e.message}\n`);
    process.exit(0);
  }
});
```

**Stop Hook 说明**：

| 触发场景 | 说明 |
|----------|------|
| 用户输入 `/exit` | 主动退出 |
| 用户按 `Ctrl+D` | EOF 退出 |
| 会话超时 | 长时间无操作 |
| 上下文满了强制结束 | 达到上限 |

### 2.5 Agent AI助手分工

**Agent 是什么？** 把不同任务分给不同"角色"的 AI。

**定义方式**：在 `~/.claude/agents/` 目录创建 `.md` 文件。

**示例 - Coder Agent** (`~/.claude/agents/coder.md`)：

```markdown
---
description: 代码执行 Agent，精确修改文件
mode: subagent
model: claude-sonnet-4-6
---

# Coder Agent

你是精确执行代码任务的工程师。

## 原则
1. 严格按指令 - 不添加未要求的修改
2. 最小化改动 - 只改必要的部分
3. 保持风格 - 与现有代码一致

## 禁止
- 不修改测试文件（除非明确要求）
- 不删除未提及的代码
```

**mode 说明**：

| mode | 说明 |
|------|------|
| `primary` | 主 Agent，用户直接交互 |
| `subagent` | 子 Agent，被其他 Agent 调用 |

### 2.6 记忆系统

**三层记忆**：

| 层级 | 文件 | 作用 |
|------|------|------|
| 全局记忆 | `~/.claude/CLAUDE.md` | 编码规范、常用命令 |
| 项目记忆 | `项目/.claude/CLAUDE.md` | 技术栈、目录结构 |
| 会话记忆 | 运行时 `/memory` 命令 | 临时发现、API 用法 |

**记忆管理命令**：

| 命令 | 作用 |
|------|------|
| `/memory` | 查看当前记忆 |
| `/memory add "内容"` | 添加记忆 |
| `/memory list` | 列出所有记忆 |
| `/memory forget ID` | 删除记忆 |

**使用示例**：

```bash
# 添加记忆
Remember: 数据库连接字符串在 .env 文件里

# 或用命令
/memory add "API 速率限制是 100 req/min"
```

### 2.7 上下文压缩

**为什么需要？** 上下文有限（~200K token），长任务会消耗完。

**自动压缩配置**：

```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "85"
  },
  "hooks": {
    "PreCompact": [{
      "matcher": "auto",
      "hooks": [{
        "type": "command",
        "command": "node C:/Users/Administrator/.claude/hooks/pre-compact-backup.mjs",
        "async": true
      }]
    }]
  }
}
```

| 阈值 | 策略 |
|------|------|
| `75` | 保守 |
| `85` | 平衡（推荐） |
| `90` | 激进 |

**压缩前自动备份脚本** (`~/.claude/hooks/pre-compact-backup.mjs`)：

```javascript
// Windows 兼容的压缩前自动备份脚本
import { readFileSync, mkdirSync, writeFileSync, readdirSync, unlinkSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

let inputData = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => inputData += chunk);
process.stdin.on('end', () => {
  try {
    const input = JSON.parse(inputData || '{}');
    const trigger = input.trigger || 'unknown';
    const sessionId = input.session_id || 'unknown';
    const transcriptPath = input.transcript_path || '';

    // 创建备份目录
    const backupDir = join(homedir(), '.claude', 'backups');
    mkdirSync(backupDir, { recursive: true });

    // 生成时间戳文件名
    const now = new Date();
    const timestamp = now.toISOString()
      .replace(/:/g, '-')
      .replace(/\..+/, '')
      .replace('T', '_');
    const backupFile = join(backupDir, `session-${timestamp}-${trigger}.md`);

    // 写入备份头信息
    let content = `# Claude Code 会话备份\n`;
    content += `- 时间：${now.toLocaleString('zh-CN')}\n`;
    content += `- 触发方式：${trigger}\n`;
    content += `- 会话 ID：${sessionId}\n\n`;

    // 解析 transcript 文件（如果存在）
    if (transcriptPath) {
      try {
        const rawLines = readFileSync(transcriptPath, 'utf8').split('\n');
        content += `## 会话摘要\n\n`;
        let count = 0;
        for (const line of rawLines) {
          if (!line.trim()) continue;
          try {
            const entry = JSON.parse(line);
            if (entry.type === 'message') {
              if (entry.role === 'user') {
                const text = Array.isArray(entry.content)
                  ? entry.content.filter(c => c.type === 'text').map(c => c.text).join('\n')
                  : (entry.content || '');
                if (text.trim()) {
                  content += `### 用户\n${text.slice(0, 500)}\n\n`;
                  count++;
                }
              } else if (entry.role === 'assistant') {
                const text = Array.isArray(entry.content)
                  ? entry.content.filter(c => c.type === 'text').map(c => c.text).join('\n')
                  : '';
                if (text.trim()) {
                  content += `### Claude\n${text.slice(0, 500)}\n\n`;
                  count++;
                }
              }
            }
            if (count >= 40) break; // 只保留前 40 条消息
          } catch {}
        }
      } catch (e) {
        content += `*（无法读取会话记录：${e.message}）*\n`;
      }
    }

    writeFileSync(backupFile, content, 'utf8');

    // 记录日志
    const logFile = join(homedir(), '.claude', 'compact-log.txt');
    const logEntry = `[${now.toISOString()}] 备份完成: ${backupFile}\n`;
    try {
      const existing = readFileSync(logFile, 'utf8');
      writeFileSync(logFile, existing + logEntry, 'utf8');
    } catch {
      writeFileSync(logFile, logEntry, 'utf8');
    }

    // 只保留最近 20 个备份
    try {
      const files = readdirSync(backupDir)
        .filter(f => f.startsWith('session-') && f.endsWith('.md'))
        .map(f => ({ name: f, path: join(backupDir, f) }))
        .sort((a, b) => b.name.localeCompare(a.name));
      files.slice(20).forEach(f => {
        try { unlinkSync(f.path); } catch {}
      });
    } catch {}

    process.exit(0);
  } catch (e) {
    process.stderr.write(`备份失败: ${e.message}\n`);
    process.exit(0); // 即使失败也不阻断压缩
  }
});
```

**备份功能说明**：
- 压缩前自动保存会话摘要到 `~/.claude/backups/` 目录
- 记录压缩日志到 `~/.claude/compact-log.txt`
- 自动清理旧备份，只保留最近 20 个
- 即使备份失败也不会阻断压缩流程

**手动压缩**：

```bash
/compact                    # 压缩
/compact 保留当前任务       # 带保留指令
/clear                      # 清空重来
```

### 2.8 Statusline 状态栏

**效果示例**：

```
GLM-5 | 📁python学习 | 🟢▓▓▓▓░░░░░░45% | 💰$0.042 | ⏱️30m
GLM-5 | 📁python学习 | 🟡▓▓▓▓▓▓░░░░67%
GLM-5 | 📁python学习 | 🟠▓▓▓▓▓▓▓▓░░80%
GLM-5 | 📁python学习 | 🔴▓▓▓▓▓▓▓▓▓░92%
   💡 建议: 考虑执行 /compact 或 /clear
```

**显示说明**：

| 内容 | 说明 |
|------|------|
| 模型名 | 当前使用的模型 |
| 🟢🟡🟠🔴 | 上下文状态（绿<50%、黄50-74%、橙75-84%、红≥85%） |
| ▓░ 进度条 | 10格电池图，▓已用 ░剩余 |
| 📁目录 | 当前项目文件夹名 |
| 🌿分支 | Git 分支 + ✓干净/✗有更改 |
| 💰费用 | 本次会话花费 |
| ⏱️时长 | 会话时间 |

**完整配置脚本** (`~/.claude/statusline.mjs`)：

```javascript
// Claude Code 高级状态栏脚本
// 功能：模型、上下文进度条、费用、Git、会话时间、模式检测

import { execSync } from 'child_process';
import { basename } from 'path';

let inputData = '';
process.stdin.setEncoding('utf8');

process.stdin.on('data', (chunk) => {
  inputData += chunk;
});

process.stdin.on('end', () => {
  try {
    const input = JSON.parse(inputData || '{}');

    // ============ 基础信息提取 ============
    const model = input?.model?.display_name || 'Unknown';
    const modelId = input?.model?.id || '';
    const usedPct = input?.context_window?.used_percentage || 0;
    const usedTokens = input?.context_window?.used_tokens || 0;
    const maxTokens = input?.context_window?.max_tokens || 200000;
    const cost = input?.cost?.total_cost_usd || 0;
    const cwd = input?.workspace?.current_dir || process.cwd();
    const dirName = basename(cwd);

    // ============ 计算派生值 ============
    const usedInt = Math.floor(usedPct);
    const remainingTokens = maxTokens - usedTokens;

    // Token 格式化（K/M）
    const formatTokens = (tokens) => {
      if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`;
      if (tokens >= 1000) return `${Math.floor(tokens / 1000)}K`;
      return tokens.toString();
    };

    // ============ 模型名称简化 ============
    let modelShort = modelId
      .replace('claude-sonnet-4-6', 'Sonnet-4.6')
      .replace('claude-opus-4-6', 'Opus-4.6')
      .replace('claude-haiku-4-5', 'Haiku-4.5')
      .replace('claude-sonnet-4-5', 'Sonnet-4.5')
      .replace('claude-opus-4-5', 'Opus-4.5')
      .replace('anthropic/', '')
      .replace('glm-5', 'GLM-5');

    if (!modelShort || modelShort === modelId) {
      modelShort = model || 'Unknown';
    }

    // ============ 上下文电池图 ============
    const filledBlocks = Math.floor(usedInt / 10);
    const emptyBlocks = 10 - filledBlocks;

    let statusIcon;
    if (usedInt < 50) {
      statusIcon = '🟢';
    } else if (usedInt < 75) {
      statusIcon = '🟡';
    } else if (usedInt < 85) {
      statusIcon = '🟠';
    } else {
      statusIcon = '🔴';
    }

    const bar = '▓'.repeat(filledBlocks) + '░'.repeat(emptyBlocks);

    // ============ Git 信息 ============
    let gitInfo = '';
    try {
      const branch = execSync('git branch --show-current 2>NUL', {
        cwd, encoding: 'utf8', timeout: 800, stdio: ['pipe', 'pipe', 'pipe']
      }).trim();

      if (branch) {
        const status = execSync('git status --porcelain 2>NUL', {
          cwd, encoding: 'utf8', timeout: 800, stdio: ['pipe', 'pipe', 'pipe']
        }).trim();
        gitInfo = ` 🌿${branch}${status.length > 0 ? '✗' : '✓'}`;
      }
    } catch {}

    // ============ 会话时间 ============
    let sessionInfo = '';
    const duration = input?.session?.duration_seconds || 0;
    if (duration > 60) {
      const mins = Math.floor(duration / 60);
      sessionInfo = mins >= 60
        ? ` ⏱️${Math.floor(mins/60)}h${mins%60}m`
        : ` ⏱️${mins}m`;
    }

    // ============ 模式检测 ============
    let modeInfo = '';
    if (input?.thinking?.enabled) modeInfo = ' 🧠';
    if (input?.plan_mode) modeInfo += ' 📋';

    // ============ 费用格式化 ============
    const formatCost = (c) => {
      if (c >= 1) return `$${c.toFixed(2)}`;
      if (c >= 0.01) return `$${c.toFixed(3)}`;
      return `¢${Math.floor(c * 100)}`;
    };
    const costStr = formatCost(cost);

    // ============ 构建输出 ============
    const parts = [];
    parts.push(`${modelShort}${modeInfo}`);
    parts.push(`📁${dirName}${gitInfo}`);
    parts.push(`${statusIcon}${bar}${usedInt}%`);
    if (cost > 0) parts.push(`💰${costStr}`);
    if (sessionInfo) parts.push(sessionInfo.trim());

    const line1 = parts.join(' | ');

    // 第二行提示
    let line2 = '';
    if (usedInt >= 85) {
      line2 = `\n   💡 建议: ${usedInt >= 95 ? '立即执行 /compact' : '考虑执行 /compact 或 /clear'}`;
    } else if (usedInt >= 70) {
      line2 = `\n   📌 剩余上下文: ${formatTokens(remainingTokens)} tokens`;
    }

    process.stdout.write(line1 + line2 + '\n');

  } catch {
    process.stdout.write('⚪ Claude Code | 状态读取失败 | 检查配置\n');
  }
});
```

**在 settings.json 启用**：

```json
{
  "statusLine": {
    "type": "command",
    "command": "node ~/.claude/statusline.mjs"
  }
}
```

### 2.9 命令速查表

| 命令 | 作用 |
|------|------|
| `/compact` | 压缩上下文 |
| `/clear` | 清空对话 |
| `/context` | 查看上下文使用情况 |
| `/cost` | 查看花费 |
| `/model` | 切换模型 |
| `/plan` | 进入规划模式 |
| `/diff` | 查看文件变动 |
| `/doctor` | 检查配置 |
| `/hooks` | 管理 Hooks |
| `/memory` | 管理记忆 |
| `/agents` | 查看 Agent |

| 快捷键 | 作用 |
|--------|------|
| `Ctrl+C` | 取消当前操作 |
| `Ctrl+F` (x2) | 杀掉所有后台 Agent |
| `Esc` (x2) | 撤回上一条消息 |

### 2.10 CLI 启动参数完整说明

```bash
claude [选项] [提示词]
```

**核心参数**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--model, -m` | 指定模型 | `claude --model sonnet` |
| `--name, -n` | 会话名称 | `claude -n "重构任务"` |
| `--print, -p` | 非交互模式，输出结果 | `claude -p "解释这段代码"` |
| `--output-format` | 输出格式 | `--output-format json` |
| `--dangerously-skip-permissions` | 跳过所有权限检查（危险） | 见上方说明 |

**权限相关参数**：

| 参数 | 说明 |
|------|------|
| `--permission-mode` | 设置初始权限模式 |
| `--permission-prompt-tool` | 指定 MCP 工具处理权限提示 |

**会话管理参数**：

| 参数 | 说明 |
|------|------|
| `--no-session-persistence` | 禁用会话持久化 |
| `--remote` | 在 claude.ai 创建 Web 会话 |
| `--remote-control, --rc` | 启用远程控制模式 |
| `--worktree` | 在独立 worktree 中运行 |

**调试参数**：

| 参数 | 说明 |
|------|------|
| `--debug` | 启用调试模式 | `--debug "api,mcp"` |
| `--no-chrome` | 禁用 Chrome 集成 |
| `--plugin-dir` | 指定插件目录 |

**使用示例**：

```bash
# 指定模型运行
claude --model opus "设计一个微服务架构"

# 非交互模式（适合脚本）
claude --print "生成 README.md" --output-format json > result.json

# 自动化修复 lint 错误（CI 场景）
claude --dangerously-skip-permissions --print "修复所有 lint 错误"

# 远程控制模式
claude --remote-control "我的项目"
```

### 2.11 环境变量速查表

在 `settings.json` 的 `env` 字段配置，或直接在 shell 中设置。

**上下文与压缩**：

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 95 | 自动压缩阈值（推荐 50-85） |
| `MAX_THINKING_TOKENS` | 31999 | 扩展思考 token 上限 |

**模型与子 Agent**：

| 环境变量 | 说明 |
|----------|------|
| `CLAUDE_CODE_SUBAGENT_MODEL` | 子 Agent 使用的模型（推荐 haiku） |

**实验性功能**：

| 环境变量 | 说明 |
|----------|------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | 启用 Agent Teams 功能 |

**Git 与工具**：

| 环境变量 | 说明 |
|----------|------|
| `CLAUDE_CODE_GIT_BASH_PATH` | Git Bash 路径（Windows） |
| `USE_BUILTIN_RIPGREP` | 是否使用内置 ripgrep |

**遥测**：

| 环境变量 | 说明 |
|----------|------|
| `CLAUDE_CODE_ENABLE_TELEMETRY` | 启用遥测 |

**配置示例**：

```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_CODE_SUBAGENT_MODEL": "claude-haiku-4-5"
  }
}
```

### 2.12 项目规范目录 .spec

**用途**：在项目中定义 `.spec` 目录存放开发规范，让 Claude 每次编程时自动遵守。

**目录结构示例**：

```
你的项目/
├── .spec/
│   ├── README.md              # 规范目录说明
│   ├── coding-standards.md    # 编码规范（代码风格、命名约定）
│   ├── project-conventions.md # 项目约定（目录结构、技术栈）
│   └── templates/             # 代码模板
└── .claude/
    └── CLAUDE.md              # 引用 .spec 规范
```

**配置方法**：

**Step 1** - 创建规范文件（`.spec/coding-standards.md`）：

```markdown
# 编码规范

## Python 规范
- 遵循 PEP 8
- 使用类型注解
- 函数必须有文档字符串

## 命名约定
| 类型 | 风格 | 示例 |
|------|------|------|
| 类 | PascalCase | `DataProcessor` |
| 函数 | snake_case | `process_data()` |
| 常量 | UPPER_SNAKE | `MAX_SIZE` |

## 禁止事项
- ❌ 硬编码密钥
- ❌ 裸 `except:`
```

**Step 2** - 在项目 `.claude/CLAUDE.md` 中引用：

```markdown
# 项目指令

## 规范加载

Claude 编程时必须遵守以下规范：
- **编码规范**：[.spec/coding-standards.md](.spec/coding-standards.md)
- **项目约定**：[.spec/project-conventions.md](.spec/project-conventions.md)

## 核心原则
- ✅ 遵循规范文件中的代码风格
- ✅ 使用类型注解
- ❌ 禁止硬编码敏感信息
```

**工作原理**：

| 步骤 | 说明 |
|------|------|
| 1 | Claude 启动时加载项目 `.claude/CLAUDE.md` |
| 2 | 读取其中的规范文件引用 |
| 3 | 编程时自动遵守这些规范 |

**规范文件编写建议**：

| 建议 | 原因 |
|------|------|
| 每个文件 < 200 行 | 避免消耗过多 token |
| 使用表格和列表 | 结构清晰，易于 Claude 理解 |
| 提供正反示例 | 明确什么是推荐/禁止的 |
| 按主题拆分文件 | 便于维护和按需加载 |

**高级用法 - 条件加载**：

```markdown
# 在 .claude/CLAUDE.md 中

## 条件规范

当修改 `src/api/` 目录时，遵守：
- [.spec/api-design.md](.spec/api-design.md)

当修改 `tests/` 目录时，遵守：
- [.spec/testing-standards.md](.spec/testing-standards.md)
```

**与全局配置的关系**：

```
优先级：项目规范 > 全局规范 > 默认行为

~/.claude/CLAUDE.md        # 全局规范（所有项目共享）
项目/.claude/CLAUDE.md     # 项目规范（覆盖全局）
项目/.spec/                # 具体规范文件
```

---

## 3. OpenCode 完整配置

### 3.1 配置文件位置

```
全局配置
C:\Users\<你的用户名>\.config\opencode\
├── opencode.json       # 主配置
├── AGENTS.md           # 全局指令
├── agents\             # Agent 定义
└── commands\           # 自定义命令

项目配置
你的项目目录\.opencode\
├── opencode.json       # 项目配置
└── AGENTS.md           # 项目指令

优先级：项目配置 > 全局配置 > 默认值
```

### 3.2 opencode.json 主配置

```json
{
  "$schema": "https://opencode.ai/config.json",

  "model": "anthropic/claude-sonnet-4-6",
  "small_model": "minimax/MiniMax-M2",
  "default_agent": "architect",

  "provider": {
    "anthropic": {
      "apiKey": "${ANTHROPIC_API_KEY}"
    },
    "minimax": {
      "apiKey": "${MINIMAX_API_KEY}",
      "baseURL": "https://api.minimax.io/v1"
    }
  },

  "agent": {
    "architect": {
      "description": "主控规划 Agent",
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-6",
      "temperature": 0.2
    },
    "coder": {
      "description": "代码执行 Agent",
      "mode": "subagent",
      "model": "minimax/MiniMax-M2",
      "temperature": 0.1
    },
    "tester": {
      "description": "测试 Agent",
      "mode": "subagent",
      "model": "minimax/MiniMax-M2"
    }
  },

  "instructions": ["AGENTS.md"],

  "permission": {
    "edit": "allow",
    "bash": {
      "npm *": "allow",
      "git *": "allow",
      "*": "ask"
    }
  }
}
```

**配置项说明**：

| 配置项 | 作用 |
|--------|------|
| `model` | 默认主模型 |
| `small_model` | 轻量任务用的便宜模型 |
| `default_agent` | 默认启动的 Agent |
| `provider` | 各模型提供商的 API 配置 |
| `agent` | Agent 定义（也可用 .md 文件） |
| `instructions` | 加载的指令文件 |
| `permission` | 权限设置 |

### 3.2.1 权限系统详解

OpenCode 默认允许大部分操作，可通过 `permission` 配置调整。

#### 权限值说明

| 值 | 行为 |
|----|------|
| `"allow"` | 自动执行，不询问 |
| `"ask"` | 执行前询问用户 |
| `"deny"` | 拒绝执行 |

#### 全局权限配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "bash": "allow",
    "edit": "deny"
  }
}
```

#### 命令级权限配置

```json
{
  "permission": {
    "bash": {
      "*": "ask",
      "git *": "allow",
      "npm *": "allow",
      "rm *": "deny",
      "curl *": "deny"
    },
    "edit": {
      "*": "deny",
      "src/**/*.ts": "allow"
    }
  }
}
```

**匹配规则**：最后匹配的规则生效，越具体的规则优先级越高。

#### Agent 级权限覆盖

为特定 Agent 设置不同的权限：

```json
{
  "agent": {
    "coder": {
      "permission": {
        "edit": "allow",
        "bash": {
          "*": "ask",
          "npm *": "allow"
        }
      }
    },
    "reviewer": {
      "permission": {
        "edit": "deny",
        "bash": {
          "git diff": "allow",
          "grep *": "allow"
        }
      }
    }
  }
}
```

#### Markdown Agent 权限定义

```markdown
---
description: 代码审查 Agent
mode: subagent
permission:
  edit: deny
  bash:
    "*": ask
    "git diff": allow
    "git log*": allow
---

只分析代码，不修改文件。
```

#### 默认权限表

| 工具 | 默认值 | 说明 |
|------|--------|------|
| `read` | `allow` | 读取文件 |
| `edit` | `allow` | 编辑文件 |
| `glob` | `allow` | 文件搜索 |
| `grep` | `allow` | 内容搜索 |
| `list` | `allow` | 列出目录 |
| `bash` | `allow` | 执行命令 |
| `doom_loop` | `ask` | 循环操作 |
| `external_directory` | `ask` | 外部目录访问 |

> ⚠️ 敏感文件（`.env`、`*.env.*`）默认拒绝读取，但 `*.env.example` 允许。

#### 自动授权全部（危险）

```json
{
  "permission": "allow"
}
```

> ⚠️ 此配置允许所有操作自动执行，无任何安全检查。仅在隔离环境中使用。

### 3.3 AGENTS.md 项目指令

```markdown
# 项目规则

## 技术栈
- React 18 + TypeScript
- Node.js + Express
- PostgreSQL + Prisma

## 目录结构
- src/api/ - API 路由
- src/services/ - 业务逻辑

## 开发命令
- 开发：npm run dev
- 测试：npm test
- 构建：npm run build

## Agent 协作规则

### Architect
- 先生成 execution_plan.md
- 每次派发一个任务
- 迭代不超过 5 次

### Coder
- 严格按指令执行
- 不做未要求的修改

### Tester
- 报告包含完整错误输出
- 不修改任何文件
```

### 3.4 Agent 配置

**两种方式**：

1. **JSON 配置**（在 opencode.json 里）
2. **Markdown 文件**（在 `agents/` 目录）

**Markdown 方式** (`~/.config/opencode/agents/architect.md`)：

```markdown
---
description: 主控规划 Agent，分析需求、生成计划
mode: primary
model: anthropic/claude-sonnet-4-6
temperature: 0.2
---

# Architect Agent

你是项目的首席架构师。负责规划和决策，不直接写代码。

## 工作流程

1. 理解需求，识别歧义
2. 生成 execution_plan.md
3. 派发任务给 @coder
4. 验证结果

## 约束
- 不直接修改代码
- 每次只派发一个任务
```

**Agent 协作流程**：

```
用户需求
    │
    ▼
┌─────────────────┐
│  Architect      │  分析需求、生成计划
│  (Claude)       │  协调子 Agent
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌─────────┐
│ Coder │  │ Reviewer│
│(便宜) │  │ (Claude)│
└───┬───┘  └─────────┘
    │
    ▼
┌───────┐
│Tester │
│(便宜) │
└───────┘
```

**模型选择建议**：

| Agent | 推荐模型 | 原因 |
|-------|----------|------|
| Architect | Claude Sonnet/Opus | 需要深度推理 |
| Coder | MiniMax / DeepSeek | 执行指令稳定、便宜 |
| Tester | MiniMax / Haiku | 简单任务够用 |
| Reviewer | Claude Sonnet | 需要理解代码语义 |

### 3.5 自定义命令

在 `~/.config/opencode/commands/` 目录创建 `.md` 文件。

**示例** (`commands/plan.md`)：

```markdown
---
description: 生成执行计划
agent: architect
---

分析需求并生成 execution_plan.md：

需求：$ARGUMENTS

要求：
1. 扫描项目结构
2. 搜索相关代码
3. 生成计划（含文件列表、步骤、验收标准）
```

**使用**：`/plan 给用户系统添加 OAuth2 登录`

### 3.6 命令速查表

| 命令 | 作用 |
|------|------|
| `/compact` | 压缩会话 |
| `/models` | 查看可用模型 |
| `/agents` | 查看 Agent |
| `/sessions` | 历史会话 |
| `/undo` | 撤销 |
| `/redo` | 重做 |
| `/thinking` | 显示/隐藏推理过程 |

| 快捷键 | 作用 |
|--------|------|
| `Ctrl+X, C` | 压缩会话 |
| `Ctrl+X, N` | 新建会话 |
| `Ctrl+X, M` | 模型列表 |
| `Ctrl+X, A` | Agent 列表 |
| `F2` | 快速切换模型 |

### 3.8 CLI 启动参数

```bash
opencode [选项]
```

| 参数 | 说明 |
|------|------|
| `--model, -m` | 指定模型 |
| `--agent, -a` | 指定默认 Agent |
| `--config, -c` | 指定配置文件路径 |
| `--no-tui` | 禁用 TUI 界面 |
| `--print` | 非交互模式 |
| `--debug` | 启用调试模式 |
| `--help, -h` | 显示帮助 |
| `--version, -v` | 显示版本 |

**使用示例**：

```bash
# 指定模型启动
opencode --model anthropic/claude-sonnet-4-6

# 指定 Agent 启动
opencode --agent coder

# 使用自定义配置
opencode --config ./custom-opencode.json
```

### 3.9 特殊语法

```bash
# 引用文件
帮我优化 @src/utils/auth.ts

# 执行命令
!git log -10 --oneline
!npm test

# 调用 Agent
@coder 修改 src/auth.ts
@reviewer 审查这段代码
```

---

## 4. Oh My OpenCode 插件

> **重要**：Oh My OpenCode 是 OpenCode 的官方增强插件，提供多 Agent 协作、自动工作流、内置 MCP 等强大功能。

### 4.1 插件简介

**Oh My OpenCode (OMO)** 是一个"开箱即用"的 AI Agent Harness 系统，为 OpenCode 提供生产级增强功能。

**核心特点**：
- 🔥 **Ultrawork 模式** - 输入 `ulw` 自动完成整个任务
- 🤖 **多 Agent 协作** - 5 个专业化 Agent 并行工作
- 🔧 **内置 MCP 服务器** - Web 搜索、文档查询、代码搜索
- 📚 **内置 Skills** - TDD、Git、重构、调试等
- ⚡ **后台并行任务** - 多 Provider 并发控制
- 🔄 **Ralph Loop** - 自主循环直到任务完成

**工作原理**：

```
用户输入 "ulw 实现用户认证"
         │
         ▼
┌─────────────────┐
│   Sisyphus      │  主控 Agent（协调器）
│   (主 Agent)    │  分解任务、派发给子 Agent
└────────┬────────┘
         │
    ┌────┼────┬────────┬────────┐
    ▼    ▼    ▼        ▼        ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│Oracle││Librar││Explore││Prometh││其他 │
│(架构)││ian   ││(搜索) ││eus    ││Agent│
│      ││(文档)││       ││(执行) ││     │
└──────┘└──────┘└──────┘└──────┘└──────┘
    │       │       │       │
    └───────┴───────┴───────┘
            │
            ▼
      任务完成
```

### 4.2 安装方式

**方式一：交互式安装（推荐）**

```bash
# 使用 bun（推荐）
bunx oh-my-opencode install

# 或使用 npx
npx oh-my-opencode install
```

安装过程中会提示配置 AI 订阅：
- Claude (Anthropic)
- Gemini (Google)
- ChatGPT/OpenAI
- Copilot (GitHub)
- 其他 Provider

**方式二：非交互式安装（自动化）**

```bash
# 适用于 CI/CD 或 LLM Agent 自动配置
bunx oh-my-openagent install --no-tui \
  --claude=yes \
  --gemini=yes \
  --copilot=no \
  --openai=yes
```

**方式三：手动安装**

```bash
# 1. 克隆到 OpenCode 插件目录
git clone https://github.com/code-yeongyu/oh-my-openagent.git
cd oh-my-openagent

# 2. 安装依赖
bun install

# 3. 复制配置模板
cp templates/oh-my-opencode.jsonc ~/.config/opencode/
```

### 4.3 配置文件详解

配置文件位置：
- **用户级**：`~/.config/opencode/oh-my-opencode.jsonc`
- **项目级**：`.opencode/oh-my-opencode.jsonc`

**完整配置示例**：

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-opencode.schema.json",

  // ============ Agent 配置 ============
  "agents": {
    // 主控 Agent
    "sisyphus": {
      "model": "anthropic/claude-sonnet-4-6",
      "ultrawork": {
        "model": "anthropic/claude-opus-4-6",
        "variant": "max"
      }
    },
    // 文档查询 Agent
    "librarian": {
      "model": "google/gemini-2.5-flash"
    },
    // 代码探索 Agent
    "explore": {
      "model": "anthropic/claude-haiku-4-5"
    },
    // 架构决策 Agent
    "oracle": {
      "model": "anthropic/claude-opus-4-6",
      "variant": "high"
    },
    // 执行 Agent
    "prometheus": {
      "prompt_append": "Leverage deep & quick agents heavily, always in parallel."
    }
  },

  // ============ 任务分类路由 ============
  "categories": {
    // 快速任务
    "quick": {
      "model": "anthropic/claude-haiku-4-5"
    },
    // 深度推理
    "unspecified-high": {
      "model": "anthropic/claude-opus-4-6",
      "variant": "max"
    },
    // 普通任务
    "unspecified-low": {
      "model": "anthropic/claude-sonnet-4-6"
    },
    // 可视化工程
    "visual-engineering": {
      "model": "google/gemini-2.5-pro",
      "variant": "high"
    },
    // 文档写作
    "writing": {
      "model": "google/gemini-2.5-flash"
    }
  },

  // ============ 并发控制 ============
  "background_task": {
    "providerConcurrency": {
      "anthropic": 3,
      "openai": 3,
      "google": 5
    },
    "modelConcurrency": {
      "anthropic/claude-opus-4-6": 2
    }
  },

  // ============ 实验性功能 ============
  "experimental": {
    "aggressive_truncation": true,
    "task_system": true
  },

  // ============ 其他设置 ============
  "tmux": { "enabled": false },
  "hashline_edit": false,
  "runtime_fallback": true
}
```

### 4.4 内置 Agent 详解

| Agent | 角色 | 默认模型 | 用途 |
|-------|------|----------|------|
| **Sisyphus** | 主控 Agent | Claude Sonnet | 分解任务、协调子 Agent、汇总结果 |
| **Oracle** | 架构师 | Claude Opus | 深度推理、架构设计、技术决策 |
| **Librarian** | 文档专家 | Gemini Flash | 查阅文档、API 参考、最佳实践 |
| **Explore** | 探索者 | Claude Haiku | 快速扫描代码库、定位文件、理解结构 |
| **Prometheus** | 执行者 | 继承主模型 | 实现代码、运行测试、执行操作 |

**调用方式**：

```bash
# 直接调用特定 Agent
Ask @oracle to review this architecture design
Ask @librarian how to implement rate limiting in Express.js
Ask @explore to find all API endpoints in this project

# 或者让主 Agent 自动分配
ulw implement user authentication
```

**禁用特定 Agent**：

```json
{
  "disabled_agents": ["oracle", "multimodal-looker"]
}
```

### 4.5 工作模式详解

#### Ultrawork 模式（全自动）

**激活方式**：在提示词中加入 `ulw` 或 `ultrawork`

```bash
# 示例
ulw fix all failing tests
ultrawork implement JWT authentication following our patterns
```

**工作流程**：
1. 主 Agent 分析任务，分解为子任务
2. 并行派发给多个子 Agent
3. 后台执行，持续直到完成
4. 自动验证、修复问题

**特点**：
- 完全自主，无需人工干预
- 并行执行，效率最高
- 适合复杂、多步骤任务

#### Ralph Loop 模式（循环执行）

**激活方式**：使用 `/ralph-loop` 命令

```bash
# 基本用法
/ralph-loop "Build a REST API with authentication"

# 指定最大迭代次数
/ralph-loop "Refactor the payment module" --max-iterations=50

# 结合 ultrawork
/ralph-loop "Implement full test coverage" --ultrawork
```

**工作原理**：
- 自动检测 `<promise>DONE</promise>` 标记判断完成
- 如果 Agent 停止但未完成，自动注入续接提示
- 可设置最大迭代次数防止无限循环

**取消循环**：

```bash
/cancel-ralph
```

**状态文件**：`.sisyphus/ralph-loop.local.md`（自动 gitignore）

#### 模式对比

| 模式 | 触发方式 | 适用场景 | 特点 |
|------|----------|----------|------|
| **默认** | 无关键词 | 简单任务、需要确认 | 交互式，逐步确认 |
| **Ultrawork** | `ulw` | 复杂任务、自动化 | 全自主、并行执行 |
| **Ralph Loop** | `/ralph-loop` | 长时间任务、持续迭代 | 循环直到完成 |

### 4.6 内置 Skills 详解

#### /refactor - 智能重构

```bash
# 基本用法
/refactor <target> [--scope=<file|module|project>] [--strategy=<safe|aggressive>]

# 示例
/refactor src/auth --scope=module --strategy=safe
/refactor UserService --scope=file
```

**功能**：
- LSP 驱动的重命名和导航
- AST-grep 模式匹配
- 架构分析前置
- TDD 验证后置
- 自动生成 codemap

#### /git-master - Git 专家

```bash
# 提交管理
/git-master commit these changes

# Rebase 操作
/git-master rebase onto main

# 历史分析
/git-master who wrote this authentication code?

# Git bisect 调试
/git-master find the commit that broke the build
```

**核心原则**：
- 原子提交（3+ 文件 = 2+ commits）
- 自动检测提交风格（分析最近 30 条提交）
- 智能拆分大型变更

#### /tdd - 测试驱动开发

```bash
/tdd implement user registration
/tdd fix the login bug
```

**工作流程**：
1. 先写失败测试
2. 实现最小代码
3. 验证测试通过
4. 重构优化

#### /dev-browser - 浏览器自动化

```bash
# 安装 skill
git clone https://github.com/sawyerhood/dev-browser /tmp/dev-browser-skill
mkdir -p ~/.config/opencode/skills
cp -r /tmp/dev-browser-skill/skills/dev-browser ~/.config/opencode/skills/
cd ~/.config/opencode/skills/dev-browser && npm install

# 使用
Use dev-browser to navigate to example.com and extract the main heading
```

### 4.7 内置 MCP 服务器

| MCP 服务器 | 功能 | 调用示例 |
|-----------|------|----------|
| **websearch** | Web 搜索 (Exa/Tavily) | `websearch_web_search_exa({ query: "React 19 features" })` |
| **context7** | 官方文档查询 | `context7_resolve_library_id({ libraryName: "express" })` |
| **grep_app** | GitHub 代码搜索 | `grep_app_search({ query: "JWT middleware", language: "typescript" })` |

**禁用内置 MCP**：

```json
{
  "disabled_mcps": ["websearch", "context7"]
}
```

### 4.8 自定义 Skill 创建

在 `.opencode/skills/` 目录创建 `SKILL.md` 文件：

```markdown
---
name: my-custom-skill
description: My specialized workflow
mcp:
  my-mcp:
    command: npx
    args: ["-y", "my-mcp-server"]
---

# My Skill Instructions

This content is injected into the agent's system prompt when the skill is loaded.

## Workflow
1. Step one
2. Step two
3. Step three
```

**Skill 目录结构**：

```
.opencode/skills/
├── my-skill/
│   ├── SKILL.md           # Skill 定义
│   ├── prompts/           # 提示词模板
│   └── scripts/           # 辅助脚本
└── another-skill/
    └── SKILL.md
```

### 4.9 CLI 命令速查

```bash
# 安装
bunx oh-my-opencode install

# 运行任务（带完成检测）
bunx oh-my-opencode run "Refactor the auth module"

# 查看配置
bunx oh-my-opencode config show

# 验证配置
bunx oh-my-opencode config validate
```

### 4.10 配置选项完整参考

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `agents` | object | Agent 配置覆盖 |
| `agents.<name>.model` | string | 指定模型 |
| `agents.<name>.variant` | string | 模型变体（high/max/medium） |
| `agents.<name>.temperature` | number | 温度参数 |
| `agents.<name>.prompt` | string | 系统提示词（file:// URI） |
| `agents.<name>.prompt_append` | string | 追加提示词 |
| `agents.<name>.disable` | boolean | 禁用 Agent |
| `disabled_agents` | array | 禁用的 Agent 列表 |
| `categories` | object | 任务分类路由 |
| `background_task` | object | 后台任务并发配置 |
| `background_task.providerConcurrency` | object | 各 Provider 并发数 |
| `background_task.modelConcurrency` | object | 各模型并发数 |
| `experimental` | object | 实验性功能开关 |
| `experimental.aggressive_truncation` | boolean | 激进截断 |
| `experimental.task_system` | boolean | 任务系统 |
| `tmux.enabled` | boolean | 启用 tmux 集成 |
| `hashline_edit` | boolean | Hash-anchored 编辑 |
| `runtime_fallback` | boolean | 运行时回退 |
| `disabled_mcps` | array | 禁用的 MCP 服务器 |

### 4.11 与 Everything Claude Code 对比

| 功能 | Oh My OpenCode | Everything Claude Code |
|------|----------------|------------------------|
| **目标平台** | OpenCode | Claude Code |
| **Agent 数量** | 5 核心 | 21+ |
| **Skills 数量** | 内置 + 自定义 | 102+ |
| **Ultrawork 模式** | ✅ | ❌ |
| **Ralph Loop** | ✅ | ❌ |
| **内置 MCP** | 3 个 | 14 个 |
| **持续学习** | ❌ | ✅ |
| **安全扫描** | ❌ | ✅ AgentShield |
| **配置复杂度** | 中等 | 较高 |
| **学习曲线** | 平缓 | 较陡 |

---

## 5. Oh My ClaudeCode 插件

> **重要**：Oh My ClaudeCode (OMC) 是 Claude Code 的官方增强插件，与 Oh My OpenCode 功能对应，提供多 Agent 协作、自动工作流等强大功能。

### 5.1 插件简介

**Oh My ClaudeCode (OMC)** 是 Claude Code 的多智能体编排系统，零学习曲线，开箱即用。

**核心特点**：
- 🚀 **Team 模式** - 标准的多 Agent 编排方式
- 🔥 **Autopilot** - 全自动执行，从想法到代码
- 🔄 **Ralph 模式** - 持久执行，必须完整完成
- ⚡ **Ultrawork** - 最大并行化执行
- 🤖 **32 个专业 Agent** - 架构、研究、设计、测试等
- 🧠 **技能学习** - 从会话中自动提取可复用模式
- 📊 **HUD 状态栏** - 实时显示编排指标
- 🔗 **OpenClaw 集成** - 自动化响应和工作流程

**工作原理**：

```
用户输入 "team 3:executor fix all TypeScript errors"
         │
         ▼
┌─────────────────┐
│   Team 编排     │  阶段化流水线
│   (协调器)      │
└────────┬────────┘
         │
    team-plan → team-prd → team-exec → team-verify → team-fix
         │
         ▼
┌─────────────────────────────────────────────────┐
│              专业 Agent 池                       │
├──────────┬──────────┬──────────┬────────────────┤
│ architect│ executor │ debugger │ test-engineer │
│ planner  │ reviewer │ designer │  git-master   │
└──────────┴──────────┴──────────┴────────────────┘
```

### 5.2 安装方式

**方式一：插件安装（推荐）**

```bash
# 添加 marketplace
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode

# 安装插件
/plugin install oh-my-claudecode

# 配置
/omc-setup
```

**方式二：NPM 全局安装**

```bash
# 注意：npm 包名是 oh-my-claude-sisyphus
npm install -g oh-my-claude-sisyphus

# 或使用 bun
bun install -g oh-my-claude-sisyphus
```

**启用 Claude Code 原生团队**：

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 5.3 执行模式详解

| 模式 | 触发方式 | 特点 | 适用场景 |
|------|----------|------|----------|
| **Team** | `/team N:agent "task"` | 阶段化流水线 | 标准多 Agent 协作 |
| **Autopilot** | `autopilot:` | 全自主执行 | 端到端功能开发 |
| **Ralph** | `ralph:` | 持久执行 | 必须完整完成的任务 |
| **Ultrawork** | `ulw:` | 最大并行 | 并行修复/重构 |
| **Pipeline** | - | 顺序处理 | 多阶段转换 |
| **omc-teams** | `/omc-teams N:codex` | tmux CLI 工作者 | Codex/Gemini 任务 |

#### Team 模式（推荐）

```bash
# 标准 Team 编排
/team 3:executor "fix all TypeScript errors"

# Team 流水线
team-plan → team-prd → team-exec → team-verify → team-fix (loop)
```

#### tmux CLI 工作者（v4.4.0+）

```bash
# Codex CLI 窗格
/omc-teams 2:codex "review auth module for security issues"

# Gemini CLI 窗格
/omc-teams 2:gemini "redesign UI components for accessibility"

# Claude CLI 窗格
/omc-teams 1:claude "implement the payment flow"

# 三模型并行编排
/ccg Review this PR — architecture (Codex) and UI components (Gemini)
```

| 技能 | 工作者 | 最适合 |
|------|--------|--------|
| `/omc-teams N:codex` | N 个 Codex CLI 窗格 | 代码审查、安全分析、架构 |
| `/omc-teams N:gemini` | N 个 Gemini CLI 窗格 | UI/UX 设计、文档、大上下文 |
| `/omc-teams N:claude` | N 个 Claude CLI 窗格 | 通用任务 |
| `/ccg` | 1 Codex + 1 Gemini | 并行三模型编排 |

### 5.4 魔法关键词速查

| 关键词 | 效果 | 示例 |
|--------|------|------|
| `team` | 标准 Team 编排 | `/team 3:executor "fix errors"` |
| `omc-teams` | tmux CLI 工作者 | `/omc-teams 2:codex "review"` |
| `ccg` | 三模型编排 | `/ccg review this PR` |
| `autopilot` | 全自动执行 | `autopilot: build a todo app` |
| `ralph` | 持久模式 | `ralph: refactor auth` |
| `ulw` | 最大并行 | `ulw fix all errors` |
| `plan` | 规划访谈 | `plan the API` |
| `ralplan` | 迭代规划 | `ralplan this feature` |
| `deep-interview` | 需求澄清 | `deep-interview "vague idea"` |
| `swarm` | **已弃用** | 使用 `team` 替代 |
| `ultrapilot` | **已弃用** | 使用 `team` 替代 |

**注意**：
- `ralph` 包含 `ultrawork` 的并行执行，无需组合关键词
- `swarm` 和 `ultrapilot` 在 v4.1.7+ 中路由到 Team

### 5.5 内置 Agent 详解

| Agent | 角色 | 用途 |
|-------|------|------|
| **analyst** | 需求分析师 | 需求清晰度、验收标准、隐藏约束 |
| **architect** | 架构师 | 系统设计、边界、接口、权衡 |
| **planner** | 规划师 | 任务排序、执行计划、风险标记 |
| **executor** | 执行者 | 代码实现、重构、功能开发 |
| **debugger** | 调试专家 | 根因分析、回归隔离、故障诊断 |
| **test-engineer** | 测试工程师 | 测试策略、覆盖率、防抖 |
| **code-reviewer** | 代码审查员 | 逻辑缺陷、可维护性、反模式 |
| **security-reviewer** | 安全审查员 | 漏洞、信任边界、认证授权 |
| **designer** | 设计师 | UX/UI 架构、交互设计 |
| **git-master** | Git 专家 | 提交策略、历史整洁 |
| **writer** | 文档专家 | 文档、迁移说明、用户指南 |
| **verifier** | 验证专家 | 完成证据、声明验证、测试充分性 |

### 5.6 内置 Skills 详解

| Skill | 用途 | 触发方式 |
|-------|------|----------|
| `autopilot` | 全自主执行 | `/autopilot` 或 `autopilot:` |
| `ralph` | 持久执行循环 | `/ralph` 或 `ralph:` |
| `ultrawork` | 最大并行化 | `/ultrawork` 或 `ulw:` |
| `team` | Team 编排 | `/team N:agent` |
| `plan` | 规划工作流 | `/plan` |
| `ralplan` | 迭代规划共识 | `/ralplan` |
| `deep-interview` | 苏格拉底式需求澄清 | `/deep-interview` |
| `learner` | 从会话提取模式 | `/learner` |
| `hud` | HUD 状态栏配置 | `/hud` |
| `omc-doctor` | 诊断和修复问题 | `/omc-doctor` |
| `omc-setup` | 初始配置 | `/omc-setup` |
| `cancel` | 取消活动模式 | `/cancel` |

### 5.7 自定义技能系统

**一次学习，永久复用**：OMC 自动从调试过程中提取实战知识为可移植的技能文件。

**技能目录结构**：

```
~/.omc/skills/           # 用户作用域（所有项目共享）
.omc/skills/             # 项目作用域（团队共享，受版本控制）
```

**技能文件格式**：

```yaml
# .omc/skills/fix-proxy-crash.md
---
name: Fix Proxy Crash
description: aiohttp proxy crashes on ClientDisconnectedError
triggers: ["proxy", "aiohttp", "disconnected"]
source: extracted
---

在 server.py:42 的处理程序外包裹 try/except ClientDisconnectedError...
```

**技能管理命令**：

```bash
/skill list              # 列出所有技能
/skill add               # 添加新技能
/skill remove <name>     # 删除技能
/skill edit <name>       # 编辑技能
/skill search <query>    # 搜索技能
/learner                 # 自动提取可复用模式
```

### 5.8 OpenClaw 集成

将 Claude Code 会话事件转发到 OpenClaw 网关。

**快速设置**：

```bash
/oh-my-claudecode:configure-notifications
# → 选择 "OpenClaw Gateway"
```

**手动配置** (`~/.claude/omc_config.openclaw.json`)：

```json
{
  "enabled": true,
  "gateways": {
    "my-gateway": {
      "url": "https://your-gateway.example.com/wake",
      "headers": { "Authorization": "Bearer YOUR_TOKEN" },
      "method": "POST",
      "timeout": 10000
    }
  },
  "hooks": {
    "session-start": { "gateway": "my-gateway", "enabled": true },
    "stop": { "gateway": "my-gateway", "enabled": true }
  }
}
```

**环境变量**：

| 变量 | 说明 |
|------|------|
| `OMC_OPENCLAW=1` | 启用 OpenClaw |
| `OMC_OPENCLAW_DEBUG=1` | 启用调试日志 |

### 5.9 通知配置

**Telegram/Discord/Slack 通知**：

```bash
# Telegram
omc config-stop-callback telegram --enable --token <bot_token> --chat <chat_id> --tag-list "@alice,bob"

# Discord
omc config-stop-callback discord --enable --webhook <url> --tag-list "@here,123456789012345678"

# Slack
omc config-stop-callback slack --enable --webhook <url> --tag-list "<!here>,<@U1234567890>"
```

### 5.10 速率限制等待

自动恢复速率限制的会话：

```bash
omc wait          # 检查状态
omc wait --start  # 启用自动恢复守护进程
omc wait --stop   # 禁用守护进程
```

### 5.11 CLI 命令速查

```bash
# 安装和配置
/omc-setup                    # 初始配置
/omc-doctor                   # 诊断问题

# 执行模式
/team 3:executor "task"       # Team 编排
/autopilot                    # Autopilot 模式
/ralph                        # Ralph 模式
/ultrawork                    # Ultrawork 模式

# tmux CLI 工作者
/omc-teams 2:codex "task"     # Codex CLI
/omc-teams 2:gemini "task"    # Gemini CLI
/ccg                          # 三模型并行

# 技能管理
/skill list                   # 列出技能
/learner                      # 学习模式

# 其他
/hud                          # HUD 配置
/cancel                       # 取消模式
/trace                        # 追踪分析
```

### 5.12 与 Oh My OpenCode 对比

| 功能 | Oh My ClaudeCode | Oh My OpenCode |
|------|------------------|----------------|
| **目标平台** | Claude Code | OpenCode |
| **Agent 数量** | 32 | 5 核心 |
| **Skills 数量** | 28 | 内置 + 自定义 |
| **Team 模式** | ✅ 阶段化流水线 | ❌ |
| **Ultrawork 模式** | ✅ | ✅ |
| **Ralph Loop** | ✅ | ✅ |
| **tmux CLI 工作者** | ✅ Codex/Gemini | ❌ |
| **三模型编排** | ✅ /ccg | ❌ |
| **OpenClaw 集成** | ✅ | ❌ |
| **通知系统** | ✅ Telegram/Discord/Slack | ❌ |
| **技能学习** | ✅ 自动提取 | ❌ |
| **HUD 状态栏** | ✅ | ❌ |

---

## 6. Everything Claude Code 插件

### 4.1 插件简介

**Everything Claude Code (ECC)** 是一个 AI Agent Harness 性能优化系统，由 Anthropic Hackathon 获胜者开发。

**核心特点**：
- 50K+ GitHub Stars，30+ 贡献者
- 支持 Claude Code、Cursor、OpenCode、Codex 等多个平台
- 包含 21 个 Agent、102 个 Skill、52 个命令
- 生产级别的 Hooks、Rules、MCP 配置

**主要功能**：
- Token 优化与上下文管理
- 记忆持久化（跨会话保存/加载上下文）
- 持续学习（自动从会话中提取模式）
- 验证循环与安全扫描
- 多 Agent 协作编排

### 4.2 安装方式

**方式一：作为插件安装（推荐）**

```bash
# 添加 marketplace
/plugin marketplace add affaan-m/everything-claude-code

# 安装插件
/plugin install everything-claude-code@everything-claude-code
```

**方式二：手动安装**

```bash
# 克隆仓库
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code

# 安装依赖
npm install

# 安装 rules（必须手动安装）
# Windows PowerShell
.\install.ps1 typescript    # 或 python、golang、swift、php

# macOS/Linux
./install.sh typescript
```

**安装 Rules（插件无法自动分发）**：

```bash
# 用户级（所有项目共享）
mkdir -p ~/.claude/rules
cp -r everything-claude-code/rules/common/* ~/.claude/rules/
cp -r everything-claude-code/rules/typescript/* ~/.claude/rules/

# 项目级（仅当前项目）
mkdir -p .claude/rules
cp -r everything-claude-code/rules/common/* .claude/rules/
```

### 4.3 核心组件

| 组件 | 数量 | 说明 |
|------|------|------|
| **Agents** | 21 | 专业子 Agent，可委托执行特定任务 |
| **Skills** | 102 | 工作流定义和领域知识 |
| **Commands** | 52 | 斜杠命令快速执行 |
| **Rules** | 34 | 始终遵循的编码规范 |
| **Hooks** | 20+ | 触发式自动化脚本 |
| **MCP Servers** | 14 | 预配置的 MCP 服务器 |

### 4.4 常用 Agent 速查

| Agent | 用途 | 调用方式 |
|-------|------|----------|
| `planner` | 功能实现规划 | `/plan "添加用户认证"` |
| `architect` | 系统设计决策 | 自动委托 |
| `tdd-guide` | 测试驱动开发 | `/tdd` |
| `code-reviewer` | 代码质量审查 | `/code-review` |
| `security-reviewer` | 安全漏洞检测 | `/security-scan` |
| `build-error-resolver` | 构建错误修复 | `/build-fix` |
| `e2e-runner` | E2E 测试运行 | `/e2e` |
| `refactor-cleaner` | 死代码清理 | `/refactor-clean` |
| `go-reviewer` | Go 代码审查 | `/go-review` |
| `python-reviewer` | Python 代码审查 | `/python-review` |

### 4.5 常用命令速查

| 命令 | 说明 |
|------|------|
| `/plan` | 创建实现计划 |
| `/tdd` | 强制 TDD 工作流 |
| `/code-review` | 审查代码变更 |
| `/build-fix` | 修复构建错误 |
| `/e2e` | 生成 E2E 测试 |
| `/refactor-clean` | 移除死代码 |
| `/security-scan` | 运行安全扫描 |
| `/learn` | 从会话中提取模式 |
| `/checkpoint` | 保存验证状态 |
| `/verify` | 运行验证循环 |
| `/test-coverage` | 分析测试覆盖率 |
| `/update-docs` | 更新文档 |
| `/sessions` | 管理会话历史 |
| `/instinct-status` | 查看学习到的直觉 |
| `/instinct-import` | 导入直觉 |
| `/instinct-export` | 导出直觉 |
| `/evolve` | 将直觉聚类为技能 |
| `/harness-audit` | 审计 Harness 可靠性 |
| `/quality-gate` | 运行质量门检查 |
| `/model-route` | 按复杂度路由到不同模型 |

### 4.6 持续学习系统

ECC 的直觉学习系统自动从你的编码模式中学习：

```bash
# 查看学习到的直觉（含置信度）
/instinct-status

# 导出直觉供分享
/instinct-export

# 导入他人的直觉
/instinct-import <file>

# 将相关直觉聚类为技能
/evolve

# 提取并评估模式后保存
/learn-eval
```

### 4.7 AgentShield 安全扫描

内置安全审计工具，包含 1282 个测试、102 条静态分析规则：

```bash
# 快速扫描（无需安装）
npx ecc-agentshield scan

# 自动修复安全的问题
npx ecc-agentshield scan --fix

# 深度分析（使用三个 Opus 4.6 Agent）
npx ecc-agentshield scan --opus --stream

# 生成安全配置
npx ecc-agentshield init
```

**扫描范围**：
- 密钥检测（14 种模式）
- 权限审计
- Hook 注入分析
- MCP 服务器风险分析
- Agent 配置审查

### 4.8 Token 优化建议

ECC 提供经过验证的 Token 优化设置：

```json
// ~/.claude/settings.json
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```

| 设置 | 默认值 | 推荐值 | 效果 |
|------|--------|--------|------|
| `model` | opus | **sonnet** | 成本降低 ~60%，可处理 80%+ 编码任务 |
| `MAX_THINKING_TOKENS` | 31,999 | **10,000** | 隐藏思考成本降低 ~70% |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 95 | **50** | 更早压缩，长会话质量更好 |

### 4.9 Hook 运行时控制

```bash
# 设置 Hook 严格度（默认：standard）
export ECC_HOOK_PROFILE=standard   # minimal | standard | strict

# 临时禁用特定 Hook
export ECC_DISABLED_HOOKS="pre:bash:tmux-reminder,post:edit:typecheck"
```

### 4.10 跨平台支持

| 平台 | Agents | Commands | Skills | Hooks | Rules |
|------|--------|----------|--------|-------|-------|
| **Claude Code** | 21 | 52 | 102 | 8 类型 | 34 |
| **Cursor IDE** | 共享 | 共享 | 共享 | 15 类型 | 34 |
| **OpenCode** | 12 | 31 | 37 | 11 类型 | 13 |
| **Codex** | 共享 | 指令式 | 10 | 暂无 | 指令式 |

### 4.11 常见工作流

**开发新功能**：
```
/plan "添加 OAuth 登录"    → planner 创建实现蓝图
/tdd                       → tdd-guide 强制测试先行
/code-review               → code-reviewer 审查代码
```

**修复 Bug**：
```
/tdd                       → 写一个复现问题的失败测试
                           → 实现修复，验证测试通过
/code-review               → 检查回归问题
```

**生产准备**：
```
/security-scan             → 安全审查（OWASP Top 10）
/e2e                       → 关键用户流程测试
/test-coverage             → 验证 80%+ 覆盖率
```

---

## 7. 常见问题与排错

### Hook 不生效

```powershell
# 检查 Node.js
node --version

# 检查配置
Get-Content ~/.claude/settings.json | Select-String "hooks"

# 手动测试
echo '{}' | node ~/.claude/hooks/auto-format.mjs
```

### 模型连接失败

```powershell
# 检查 API Key
$env:ANTHROPIC_API_KEY

# 测试连接
curl https://api.anthropic.com/v1/models
```

### 上下文满了

```bash
# 手动压缩
/compact 保留当前任务

# 清空重来
/clear

# 查看使用情况
/context
```

### Git 信息不显示

- 确认当前目录是 git 仓库
- 确认 git 在 PATH 中：`git --version`
- 脚本超时设置太小（建议 1000ms）

### Statusline 不显示

```powershell
# 手动测试
echo '{"model":{"display_name":"Test"}}' | node ~/.claude/statusline.mjs

# 检查配置
Get-Content ~/.claude/settings.json | Select-String "statusLine"
```

### OpenCode Agent 调用失败

```bash
# 查看可用 Agent
/agents

# 检查模型配置
/models
```

---

## 8. OpenSpec + Superpowers 协同实战指南

> **后端开发的黄金搭档**：OpenSpec 提供规范驱动开发流程，Superpowers 提供工作流自动化技能，两者结合实现从需求到交付的完整闭环。

### 8.1 OpenSpec 简介

**OpenSpec** 是一个规范驱动开发工具，确保在编写代码之前，人类和 AI 对"构建什么"达成一致。

**核心理念**：
```
需求 → 规范 → 设计 → 任务 → 实现 → 归档
```

**核心价值**：
- 📋 **对齐预期** - 先规划后编码，避免返工
- 🔄 **可追溯性** - 每个变更都有完整文档
- 🤖 **AI 友好** - 自动生成规划工件
- 📁 **规范持久化** - 项目知识沉淀

### 8.2 OpenSpec 安装

**前置条件**：Node.js 20.19.0+

```bash
# 全局安装
npm install -g @fission-ai/openspec@latest

# 验证安装
openspec --version
```

**在 Claude Code 中安装**：

```bash
# 进入项目目录
cd your-project

# 初始化 OpenSpec（交互式）
openspec init

# 或指定工具
openspec init --tools claude

# 或配置所有支持的 AI 工具
openspec init --tools all
```

**在 OpenCode 中安装**：

```bash
# 初始化时指定 opencode
openspec init --tools opencode

# 或同时配置多个工具
openspec init --tools claude,opencode
```

**初始化后的目录结构**：

```
your-project/
├── openspec/
│   ├── specs/           # 项目规范（持久化）
│   ├── changes/         # 进行中的变更
│   │   └── archive/     # 已完成的变更
│   └── config.yaml      # OpenSpec 配置
├── .claude/
│   └── skills/
│       └── opsx/        # OpenSpec skills
└── .opencode/
    └── skills/
        └── opsx/
```

### 8.3 OpenSpec 配置文件

**config.yaml 完整配置**：

```yaml
# 必填：默认 schema
schema: spec-driven

# 可选：项目上下文（注入到所有工件）
context: |
  技术栈：Spring Boot 3.2 + Java 17
  数据库：PostgreSQL 15
  构建工具：Maven
  编码规范：Google Java Style

  架构约定：
  - Controller → Service → Repository 分层
  - 使用 DTO 进行数据传输
  - 统一异常处理
  - RESTful API 设计

# 可选：每个工件的规则
rules:
  proposal:
    - 包含回滚计划
    - 评估性能影响
  specs:
    - 使用 Given/When/Then 格式
    - 包含边界条件
  design:
    - 绘制时序图
    - 标注关键接口
  tasks:
    - 每个任务不超过 4 小时
    - 标注依赖关系
```

### 8.4 OpenSpec 工作流命令

#### 核心命令速查

| 命令 | 阶段 | 说明 |
|------|------|------|
| `/opsx:propose` | 规划 | 创建变更 + 生成所有规划工件 |
| `/opsx:new` | 规划 | 仅创建变更目录骨架 |
| `/opsx:continue` | 规划 | 逐个创建工件 |
| `/opsx:ff` | 规划 | 快速生成所有规划工件 |
| `/opsx:apply` | 实现 | 执行任务清单 |
| `/opsx:archive` | 归档 | 归档已完成的变更 |
| `/opsx:review` | 审查 | 审查实现结果 |
| `/opsx:status` | 状态 | 查看当前进度 |

#### 完整工作流示例

```bash
# ============ 阶段 1：规划 ============

# 提出变更（最常用）
/opsx:propose "添加用户认证功能"

# AI 自动生成：
# openspec/changes/add-user-auth/
# ├── proposal.md    # 为什么做、做什么
# ├── specs/         # 需求规格
# │   └── auth/
# │       └── spec.md
# ├── design.md      # 技术设计
# └── tasks.md       # 任务清单

# ============ 阶段 2：实现 ============

# 执行任务
/opsx:apply

# AI 会逐个执行 tasks.md 中的任务：
# - [x] 1.1 创建 User 实体
# - [x] 1.2 实现 UserRepository
# - [x] 1.3 创建 AuthService
# - [ ] 1.4 实现 JWT 生成
# ...

# 中断后继续
/opsx:apply add-user-auth

# ============ 阶段 3：归档 ============

# 归档完成的变更
/opsx:archive

# 变更移动到：
# openspec/changes/archive/2026-03-30-add-user-auth/

# Delta specs 合并到主 specs
```

#### 任务清单格式

```markdown
# tasks.md

## 1. 数据层
- [ ] 1.1 创建 User 实体类
- [ ] 1.2 实现 UserRepository 接口
- [ ] 1.3 添加数据库迁移脚本

## 2. 服务层
- [ ] 2.1 实现 AuthService
- [ ] 2.2 实现 JWT 工具类
- [ ] 2.3 实现密码加密

## 3. 控制层
- [ ] 3.1 创建 AuthController
- [ ] 3.2 实现 /login 端点
- [ ] 3.3 实现 /register 端点

## 4. 测试
- [ ] 4.1 单元测试
- [ ] 4.2 集成测试
```

### 8.5 Superpowers 简介

**Superpowers** 是一套工作流自动化 Skills，为 Claude Code 和 OpenCode 提供结构化的开发流程。

**核心 Skills**：

| Skill | 用途 | 触发时机 |
|-------|------|----------|
| `brainstorming` | 头脑风暴 | 复杂任务开始前 |
| `planning` | 规划 | 需要制定计划时 |
| `tdd` | 测试驱动 | 写新功能/修复 bug |
| `code-review` | 代码审查 | 完成代码后 |
| `debugging` | 调试 | 遇到 bug 时 |
| `verification` | 验证 | 任务完成前 |

**安装方式**：

Superpowers 通常作为 Everything Claude Code 或 Oh My OpenCode 的一部分安装，也可以手动配置：

```bash
# 克隆 skills
git clone https://github.com/nickvdyck/superpowers.git

# 复制到 Claude Code
cp -r superpowers/skills/* ~/.claude/skills/

# 复制到 OpenCode
cp -r superpowers/skills/* ~/.config/opencode/skills/
```

### 8.6 Superpowers Skills 详解

#### brainstorming - 头脑风暴

**触发**：`/brainstorm` 或复杂任务开始前自动触发

```
用途：生成多个方案、评估利弊、选择最优解

示例：
/brainstorm 如何实现分布式缓存
```

**输出结构**：
- 方案列表
- 每个方案的优缺点
- 推荐方案及理由

#### planning - 规划

**触发**：`/plan` 或用户请求规划时

```
用途：生成详细的实现计划

示例：
/plan 实现用户认证模块
```

**输出结构**：
- 任务分解
- 文件列表
- 实现步骤
- 验收标准

#### tdd - 测试驱动开发

**触发**：`/tdd` 或开始新功能时

```
用途：强制测试先行工作流

示例：
/tdd 实现用户注册功能
```

**工作流程**：
1. 写失败测试（RED）
2. 实现最小代码（GREEN）
3. 重构优化（REFACTOR）
4. 验证覆盖率（80%+）

#### code-review - 代码审查

**触发**：`/code-review` 或代码完成后自动触发

```
用途：审查代码质量、安全性、性能

示例：
/code-review
```

**审查维度**：
- 代码质量（可读性、可维护性）
- 安全漏洞（OWASP Top 10）
- 性能问题
- 最佳实践

### 8.7 OpenSpec + Superpowers 协同工作流

#### SpringBoot 项目最佳实践

**项目结构**：

```
springboot-project/
├── openspec/
│   ├── specs/
│   │   ├── api/
│   │   │   └── spec.md        # API 规范
│   │   ├── auth/
│   │   │   └── spec.md        # 认证规范
│   │   └── database/
│   │       └── spec.md        # 数据库规范
│   ├── changes/
│   └── config.yaml
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/
│   │   │       ├── controller/
│   │   │       ├── service/
│   │   │       ├── repository/
│   │   │       ├── entity/
│   │   │       └── dto/
│   │   └── resources/
│   │       └── application.yml
│   └── test/
└── .claude/
    └── skills/
```

**完整工作流**：

```bash
# 1. 初始化项目
openspec init --tools claude

# 2. 配置 SpringBoot 上下文
# 编辑 openspec/config.yaml

# 3. 使用 brainstorm 探索方案
/brainstorm 如何实现 RESTful 用户管理 API

# 4. 创建变更规范
/opsx:propose "实现用户 CRUD API"

# 5. TDD 实现
/tdd
/opsx:apply

# 6. 代码审查
/code-review

# 7. 归档
/opsx:archive
```

**config.yaml 示例（SpringBoot）**：

```yaml
schema: spec-driven

context: |
  Spring Boot 3.2 项目

  技术栈：
  - Java 17
  - Spring Data JPA
  - PostgreSQL
  - Maven
  - Lombok

  架构约定：
  - 三层架构：Controller → Service → Repository
  - DTO 模式：使用 MapStruct 转换
  - 异常处理：@ControllerAdvice + 自定义异常
  - API 文档：SpringDoc OpenAPI
  - 安全：Spring Security + JWT

rules:
  proposal:
    - 评估对现有 API 的影响
    - 考虑数据库迁移
  design:
    - 绘制类图和时序图
    - 标注事务边界
  tasks:
    - 按层分组：Controller → Service → Repository
    - 每个任务包含测试
```

#### PyTorch 项目最佳实践

**项目结构**：

```
pytorch-project/
├── openspec/
│   ├── specs/
│   │   ├── model/
│   │   │   └── spec.md        # 模型架构规范
│   │   ├── data/
│   │   │   └── spec.md        # 数据处理规范
│   │   └── training/
│   │       └── spec.md        # 训练流程规范
│   ├── changes/
│   └── config.yaml
├── src/
│   ├── models/
│   │   └── model.py
│   ├── data/
│   │   ├── dataset.py
│   │   └── transforms.py
│   ├── training/
│   │   ├── trainer.py
│   │   └── losses.py
│   └── utils/
├── experiments/
├── configs/
└── tests/
```

**config.yaml 示例（PyTorch）**：

```yaml
schema: spec-driven

context: |
  PyTorch 深度学习项目

  技术栈：
  - Python 3.11
  - PyTorch 2.2
  - PyTorch Lightning
  - Weights & Biases
  - Hydra

  项目约定：
  - 模型继承 LightningModule
  - 数据集继承 Dataset
  - 配置使用 Hydra YAML
  - 实验跟踪使用 W&B
  - 代码风格：Black + isort

rules:
  proposal:
    - 评估计算资源需求
    - 考虑 GPU 内存限制
  specs:
    - 包含模型输入输出形状
    - 标注可训练参数数量
  design:
    - 绘制模型架构图
    - 标注数据流向
  tasks:
    - 先实现数据管道
    - 后实现模型
    - 最后实现训练循环
```

**PyTorch 工作流示例**：

```bash
# 1. 初始化
openspec init --tools claude

# 2. 探索模型架构
/brainstorm 图像分类模型选型

# 3. 创建实验规范
/opsx:propose "实现 ResNet-50 迁移学习"

# 4. TDD 实现
/tdd
/opsx:apply

# 5. 验证模型
/verify

# 6. 归档实验记录
/opsx:archive
```

### 8.8 CLI 命令速查

#### OpenSpec CLI

```bash
# 初始化
openspec init [path] --tools <tools>

# 配置
openspec config profile core
openspec config list
openspec config set <key> <value>

# 更新
openspec update

# 状态
openspec status
openspec status --json

# 归档
openspec archive <change-name> --yes

# 模板
openspec templates
```

#### Superpowers Skills

```bash
# 头脑风暴
/brainstorm <topic>

# 规划
/plan <feature>

# TDD
/tdd <feature>

# 代码审查
/code-review

# 调试
/debugging <issue>

# 验证
/verify

# 测试覆盖率
/test-coverage
```

### 8.9 常见问题

**Q: OpenSpec 和 Superpowers 有什么区别？**

| 对比项 | OpenSpec | Superpowers |
|--------|----------|-------------|
| **核心功能** | 规范驱动开发 | 工作流自动化 |
| **主要输出** | 规范文档 | 执行技能 |
| **适用阶段** | 需求→设计→任务 | 实现全过程 |
| **是否持久化** | 是（openspec/目录） | 否（运行时） |
| **可定制性** | 高（config.yaml） | 中（skills配置） |

**Q: 如何在现有项目中引入 OpenSpec？**

```bash
# 1. 安装并初始化
npm install -g @fission-ai/openspec@latest
cd your-project
openspec init

# 2. 创建初始规范
/opsx:propose "项目初始规范"

# 3. 将现有代码规范写入 config.yaml
```

**Q: Superpowers 技能如何自动触发？**

在 Everything Claude Code 或 Oh My OpenCode 中，技能会根据上下文自动触发：
- 开始新功能 → 自动触发 `planning`
- 完成代码 → 自动触发 `code-review`
- 遇到 bug → 自动触发 `debugging`

---

## 9. 权限系统对比速查

### Claude Code vs OpenCode 权限对比

| 功能 | Claude Code | OpenCode |
|------|-------------|----------|
| **配置文件** | `settings.json` | `opencode.json` |
| **自动允许** | `permissions.allow: [...]` | `permission: "allow"` 或 `permission: { bash: "allow" }` |
| **自动拒绝** | `permissions.deny: [...]` | `permission: "deny"` |
| **询问用户** | 默认行为 | `permission: "ask"` |
| **命令模式匹配** | `Bash(npm *)` | `bash: { "npm *": "allow" }` |
| **Agent 级覆盖** | 不支持 | `agent.xxx.permission` |
| **CLI 跳过权限** | `--dangerously-skip-permissions` | 不支持 |
| **Desktop 跳过权限** | Settings → Bypass permissions | 无 Desktop 版 |
| **企业禁用跳过** | `disableBypassPermissionsMode` | 不适用 |
| **默认行为** | 所有敏感操作询问 | 大部分操作允许 |

### 快速配置模板

**Claude Code 信任常用命令**：

```json
{
  "permissions": {
    "allow": [
      "Bash(npm *)",
      "Bash(git *)",
      "Bash(node *)",
      "Edit(**)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(curl *)",
      "Read(**/.env)"
    ]
  }
}
```

**OpenCode 限制危险操作**：

```json
{
  "permission": {
    "*": "allow",
    "bash": {
      "rm *": "deny",
      "curl *": "deny",
      "*": "ask"
    },
    "edit": {
      ".env": "deny",
      "*.env.*": "deny"
    }
  }
}
```

---

> **更新日期**：2026-03-30
> **适用版本**：Claude Code 2.1.x / OpenCode 1.x / Oh My OpenCode latest / OpenSpec latest