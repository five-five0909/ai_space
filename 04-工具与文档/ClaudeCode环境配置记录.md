# Claude Code 环境配置记录

> 记录当前 Claude Code 的完整配置状态，便于迁移和恢复。

---

## 1. 核心配置 (settings.json)

**路径**: `C:\Users\Administrator\.claude\settings.json`

### API 配置（DashScope 代理）

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-sp-xxx",
    "ANTHROPIC_BASE_URL": "https://coding.dashscope.aliyuncs.com/apps/anthropic",
    "ANTHROPIC_MODEL": "glm-5",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-5",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "qwen3.6-plus",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5",
    "ANTHROPIC_REASONING_MODEL": "glm-5"
  }
}
```

### 行为配置

```json
{
  "outputStyle": "engineer-professional",
  "alwaysThinkingEnabled": true,
  "autoCompactWindow": 180000,
  "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80",
  "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
  "skipDangerousModePermissionPrompt": true
}
```

### 状态栏 HUD

```json
{
  "statusLine": {
    "type": "command",
    "command": "node C:/Users/Administrator/.claude/hud/omc-hud.mjs",
    "padding": 0
  }
}
```

---

## 2. 插件系统 (enabledPlugins)

### 已启用插件

| 插件 | 来源 | 说明 |
|------|------|------|
| `context7` | claude-plugins-official | 实时文档查询 |
| `oh-my-claudecode` | omc | 多智能体编排框架 |
| `claude-mem` | thedotmack | 跨会话持久化记忆 |

### 市场源配置

```json
{
  "extraKnownMarketplaces": {
    "omc": {
      "source": {
        "source": "git",
        "url": "https://github.com/Yeachan-Heo/oh-my-claudecode.git"
      }
    },
    "thedotmack": {
      "source": {
        "source": "github",
        "repo": "thedotmack/claude-mem"
      }
    }
  }
}
```

---

## 3. OMC 配置 (.omc-config.json)

**路径**: `C:\Users\Administrator\.claude\.omc-config.json`

```json
{
  "defaultExecutionMode": "ultrawork",
  "setupVersion": "4.11.5",
  "team": {
    "maxAgents": 3,
    "defaultAgentType": "executor",
    "monitorIntervalMs": 30000,
    "shutdownTimeoutMs": 15000
  },
  "modelRouting": {
    "haiku": "glm-5",
    "sonnet": "qwen3.6-plus",
    "opus": "glm-5"
  },
  "apiConfig": {
    "baseUrl": "https://coding.dashscope.aliyuncs.com/apps/anthropic",
    "provider": "dashscope"
  }
}
```

### OMC 版本

- **当前版本**: v4.9.0
- **最新版本**: v4.12.0
- **更新命令**: `omc update`

---

## 4. MCP 服务器配置

**路径**: `C:\Users\Administrator\.claude\mcp-configs\mcp-servers.json`

### 已配置的 MCP 服务器

| 服务器 | 类型 | 用途 |
|--------|------|------|
| `github` | npx | GitHub PR/Issue/Repo 操作 |
| `firecrawl` | npx | 网页抓取和爬虫 |
| `supabase` | npx | Supabase 数据库操作 |
| `memory` | npx | 跨会话持久记忆 |
| `sequential-thinking` | npx | 链式推理 |
| `vercel` | http | Vercel 部署 |
| `railway` | npx | Railway 部署 |
| `cloudflare-docs` | http | Cloudflare 文档搜索 |
| `cloudflare-workers-builds` | http | Workers 构建 |
| `cloudflare-workers-bindings` | http | Workers 绑定 |
| `cloudflare-observability` | http | Cloudflare 日志监控 |
| `clickhouse` | http | ClickHouse 分析查询 |
| `exa-web-search` | npx | Exa API 网络搜索 |
| `context7` | npx | 实时文档查询 |
| `magic` | npx | Magic UI 组件 |
| `filesystem` | npx | 文件系统操作 |
| `insaits` | python | AI 安全监控 |
| `playwright` | npx | 浏览器自动化 |
| `fal-ai` | npx | AI 图像/视频生成 |
| `browserbase` | npx | 云浏览器会话 |
| `browser-use` | http | AI 浏览器代理 |
| `devfleet` | http | 多智能体编排 |
| `token-optimizer` | npx | Token 优化压缩 |
| `confluence` | npx | Confluence 集成 |

> **注意**: 保持启用的 MCP 数量 < 10，避免上下文窗口膨胀。

---

## 5. 目录结构

```
C:\Users\Administrator\.claude\
├── settings.json           # 主配置
├── .omc-config.json        # OMC 配置
├── CLAUDE.md               # 全局指令
├── .credentials.json       # 凭证
├── .session-stats.json     # 会话统计
├── config.json             # 基础配置
├── hud/                    # HUD 状态栏
│   └── omc-hud.mjs
├── plugins/                # 插件缓存和市场
│   ├── cache/
│   ├── marketplaces/
│   └── install-counts-cache.json
├── skills/                 # 用户自定义技能
│   └── .omc/
├── mcp-configs/            # MCP 配置模板
│   └── mcp-servers.json
├── projects/               # 项目级配置
├── sessions/               # 会话历史
├── plans/                  # 计划文件
├── backups/                # 备份
├── commands/               # 项目级命令
├── debug/                  # 调试日志
├── file-history/           # 文件历史
├── paste-cache/            # 粘贴缓存
├── shell-snapshots/        # Shell 状态快照
└── statusline-pro/         # 状态栏扩展
```

---

## 6. 快速恢复命令

### 重装插件

```bash
claude plugin install context7@claude-plugins-official
claude plugin install oh-my-claudecode@omc
claude plugin install claude-mem@thedotmack
```

### OMC 更新

```bash
omc update
```

### 配置镜像源（如需）

```bash
npm config set registry https://registry.npmmirror.com
```

---

## 7. 环境变量清单

| 变量 | 值 | 说明 |
|------|-----|------|
| `ANTHROPIC_AUTH_TOKEN` | `sk-sp-xxx` | DashScope API Key |
| `ANTHROPIC_BASE_URL` | `https://coding.dashscope.aliyuncs.com/apps/anthropic` | API 代理地址 |
| `ANTHROPIC_MODEL` | `glm-5` | 默认模型 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `glm-5` | Haiku 级模型 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `qwen3.6-plus` | Sonnet 级模型 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `glm-5` | Opus 级模型 |

---

## 8. 待配置项（需要填入真实值）

以下 MCP 需要配置真实的 API Key：

- `GITHUB_PERSONAL_ACCESS_TOKEN`
- `FIRECRAWL_API_KEY`
- `SUPABASE_PROJECT_REF`
- `EXA_API_KEY`
- `FAL_KEY`
- `BROWSERBASE_API_KEY`
- `BROWSER_USE_KEY`
- `CONFLUENCE_BASE_URL` / `EMAIL` / `API_TOKEN`

---

*更新时间: 2026-04-16*