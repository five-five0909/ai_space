# Claude Code 全局配置汇总

> 导出时间：2026-04-17
> 路径：`C:\Users\Administrator\.claude\`

---

## 1. 主设置文件 (`settings.json`)

**路径**：`C:\Users\Administrator\.claude\settings.json`

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-sp-24086d32f7a84be699442c24d5bb74ea",
    "ANTHROPIC_BASE_URL": "https://coding.dashscope.aliyuncs.com/apps/anthropic",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-5",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "qwen3.6-plus",
    "ANTHROPIC_MODEL": "glm-5",
    "ANTHROPIC_REASONING_MODEL": "glm-5",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80",
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "statusLine": {
    "type": "command",
    "command": "node C:/Users/Administrator/.claude/hud/omc-hud.mjs",
    "padding": 0
  },
  "enabledPlugins": {
    "context7@claude-plugins-official": true,
    "oh-my-claudecode@omc": true,
    "claude-mem@thedotmack": true,
    "superpowers@claude-plugins-official": true
  },
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
  },
  "outputStyle": "engineer-professional",
  "alwaysThinkingEnabled": true,
  "autoCompactWindow": 180000,
  "skipDangerousModePermissionPrompt": true
}
```

### 配置说明

| 字段 | 说明 |
|------|------|
| `env.ANTHROPIC_BASE_URL` | API 代理端点（阿里云 DashScope） |
| `env.ANTHROPIC_MODEL` | 默认模型 `glm-5` |
| `statusLine` | HUD 状态栏显示 |
| `enabledPlugins` | 启用的插件列表 |
| `outputStyle` | 输出风格：专业工程师模式 |
| `alwaysThinkingEnabled` | 始终启用思考模式 |
| `autoCompactWindow` | 自动压缩窗口 180 秒 |

---

## 2. API 配置 (`config.json`)

**路径**：`C:\Users\Administrator\.claude\config.json`

```json
{
  "primaryApiKey": "any"
}
```

> 注：实际 API Key 通过环境变量 `ANTHROPIC_AUTH_TOKEN` 设置

---

## 3. 全局指令文件 (`CLAUDE.md`)

**路径**：`C:\Users\Administrator\.claude\CLAUDE.md`

### oh-my-claudecode (OMC) 配置

```markdown
# oh-my-claudecode - Intelligent Multi-Agent Orchestration

<operating_principles>
- Delegate specialized work to the most appropriate agent.
- Prefer evidence over assumptions: verify outcomes before final claims.
- Choose the lightest-weight path that preserves quality.
- Consult official docs before implementing with SDKs/frameworks/APIs.
</operating_principles>

<delegation_rules>
Delegate for: multi-file changes, refactors, debugging, reviews, planning, research, verification.
Work directly for: trivial ops, small clarifications, single commands.
</delegation_rules>

<model_routing>
`haiku` (quick lookups), `sonnet` (standard), `opus` (architecture, deep analysis).
</model_routing>

<agent_catalog>
Prefix: `oh-my-claudecode:`.
explore, analyst, planner, architect, debugger, executor, verifier, tracer,
security-reviewer, code-reviewer, test-engineer, designer, writer, qa-tester,
scientist, document-specialist, git-master, code-simplifier, critic
</agent_catalog>
```

### 上下文压缩指令

```markdown
## 上下文压缩指令

当上下文达到 85% 或手动执行 /compact 时，压缩摘要必须保留：

**必须精确保留（不可泛化改写）：**
- 正在修改的所有文件完整路径
- 未完成的任务列表和当前进度状态
- 本次会话的架构决策及原因
- 正在调试的报错信息（原文，不改写）
- 已排查并排除的原因
- 重要的函数名、变量名、API 签名

**可以丢弃：**
- 已完成任务的详细操作过程
- 重复的工具输出内容
- 中间的失败尝试（保留结论，丢弃过程）

**压缩完成后立即输出：**
- 当前任务状态：[进行中 / 已完成 / 阻塞]
- 下一步需要执行的操作
- 等待用户确认的决策点
```

---

## 4. MCP 服务器配置模板 (`mcp-servers.json`)

**路径**：`C:\Users\Administrator\.claude\mcp-configs\mcp-servers.json`

### 已配置的 MCP 服务器

| 服务器 | 类型 | 用途 |
|--------|------|------|
| `github` | npx | GitHub PRs、issues、repos |
| `firecrawl` | npx | Web 抓取和爬虫 |
| `supabase` | npx | Supabase 数据库操作 |
| `memory` | npx | 跨会话持久记忆 |
| `sequential-thinking` | npx | 链式思维推理 |
| `vercel` | http | Vercel 部署和项目 |
| `railway` | npx | Railway 部署 |
| `cloudflare-docs` | http | Cloudflare 文档搜索 |
| `cloudflare-workers-*` | http | Cloudflare Workers 构建/绑定/监控 |
| `clickhouse` | http | ClickHouse 分析查询 |
| `exa-web-search` | npx | Exa API 网络搜索 |
| `context7` | npx | 实时文档查询 |
| `magic` | npx | Magic UI 组件 |
| `filesystem` | npx | 文件系统操作 |
| `insaits` | python | AI 安全监控 |
| `playwright` | npx | 浏览器自动化和测试 |
| `fal-ai` | npx | AI 图像/视频/音频生成 |
| `browserbase` | npx | 云端浏览器会话 |
| `browser-use` | http | AI 浏览器代理 |
| `devfleet` | http | 多代理编排 |
| `token-optimizer` | npx | Token 优化压缩 |
| `confluence` | npx | Confluence Cloud 集成 |

### 注意事项

```json
"_comments": {
  "usage": "Copy the servers you need to your ~/.claude.json mcpServers section",
  "env_vars": "Replace YOUR_*_HERE placeholders with actual values",
  "disabling": "Use disabledMcpServers array in project config to disable per-project",
  "context_warning": "Keep under 10 MCPs enabled to preserve context window"
}
```

---

## 5. 启用的插件

| 插件 | Marketplace | 状态 |
|------|-------------|------|
| `context7` | claude-plugins-official | 启用 |
| `oh-my-claudecode` | omc | 启用 |
| `claude-mem` | thedotmack | 启用 |
| `superpowers` | claude-plugins-official | 启用 |

---

## 6. 插件 Marketplace 来源

| Marketplace | 来源 |
|-------------|------|
| `omc` | Git: `https://github.com/Yeachan-Heo/oh-my-claudecode.git` |
| `thedotmack` | GitHub: `thedotmack/claude-mem` |

---

## 配置文件清单

```
C:\Users\Administrator\.claude\
├── CLAUDE.md              # 全局指令文件
├── config.json            # API 配置
├── settings.json          # 主设置文件
├── mcp-configs\
│   └── mcp-servers.json   # MCP 服务器配置模板
├── plugins\
│   ├── cache\             # 插件缓存
│   └── marketplaces\      # Marketplace 源
├── commands\              # 自定义命令
│   └ trellis\             # Trellis 命令集
├── projects\              # 项目级配置
├── tasks\                 # 任务状态
├── skills\                # 本地技能
├── paste-cache\           # 粘贴缓存
└── shell-snapshots\       # Shell 快照
```

---

## 更新提示

当前 OMC 版本：`v4.9.0`
可用更新：`v4.12.0`

更新命令：
```bash
omc update
```