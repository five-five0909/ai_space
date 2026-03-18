### 核心系统：文档架构
你需要构建两类文档：
1.  **知识库（Knowledge Base）**：定义项目是什么（6个核心 Markdown 文件）。
2.  **持久层（Persistent Layer）**：定义 AI 怎么工作以及项目进度（2-3个管理文件）。

---

### 第一步：启动提示词 (Interrogation)
*在创建文档之前，先发给 AI 这段话，让它帮你生成文档内容：*

> "在写任何代码之前，进入 Planning 模式，对我的想法进行无尽的审问（Interrogation）。不要假设任何问题。问我问题直到没有假设剩下。你需要搞清楚：核心功能、用户流程、数据结构、错误处理、技术栈细节、UI/UX 细节。
>
> 等我回答完所有问题后，请基于我们的对话，生成以下规范文档文件：PRD.md、APP_FLOW.md、TECH_STACK.md、FRONTEND_GUIDELINES.md、BACKEND_STRUCTURE.md、IMPLEMENTATION_PLAN.md。要具体且详尽，消除所有歧义。"

---

### 第二步：必备文档模板 (复制并保存为 .md 文件)

#### 1. `PRD.md` (产品需求文档)
**作用**：项目的合同，定义构建什么、不构建什么。
```markdown
# Product Requirements Document (PRD)

## 项目概述
[一句话描述这个 App 是做什么的，给谁用的]

## 核心功能 (Core Features)
1. [功能名称]: [详细描述，包括用户故事和成功标准]
2. ...

## 用户故事 (User Stories)
- 作为用户，我可以 [行动]，以便于 [结果]。

## 范围 (In Scope / Out of Scope)
- **In Scope**: [明确包含的功能]
- **Out of Scope**: [明确不做的功能，防止 AI 发散]

## 成功标准
- [由什么定义“完成”]
```

#### 2. `APP_FLOW.md` (应用流程)
**作用**：防止 AI 瞎猜页面跳转逻辑。
```markdown
# App Flow & Navigation

## 页面清单
- /home: [描述]
- /login: [描述]

## 用户路径 (User Journeys)
### 1. [流程名称，如：用户注册]
- 步骤 1: 用户点击...
- 步骤 2: 系统验证...
- 决策点: 如果成功 -> 跳转 A；如果失败 -> 显示错误 B。

## 边缘情况 (Edge Cases)
- [网络断开时发生什么]
- [数据为空时显示什么]
```

#### 3. `TECH_STACK.md` (技术栈)
**作用**：锁定版本，防止 AI 幻觉或混用不兼容的库。
```markdown
# Technology Stack

## Core
- Framework: Next.js 14.1.0 (App Router)
- Language: TypeScript 5.3.3
- Styling: Tailwind CSS 3.4.1

## Libraries & Tools
- State Management: [e.g., Zustand, React Context]
- Auth: [e.g., Clerk, Supabase Auth]
- Database: [e.g., Supabase, Postgres]
- UI Components: [e.g., shadcn/ui, Radix UI]
- Icons: Lucide React

## Rules
- 严格使用上述版本。
- 未经允许不得引入新依赖。
```

#### 4. `FRONTEND_GUIDELINES.md` (前端指南)
**作用**：视觉系统的真理来源，确保 UI 一致性。
```markdown
# Frontend Design Guidelines

## 视觉风格
- 风格关键字: [e.g., Glassmorphism, Bento Grid, Neobrutalism]
- 布局策略: Mobile-First (优先适配移动端)

## 颜色系统 (Color Palette)
- Primary: #3B82F6
- Background: #F9FAFB
- Text: #1F2937
- [包含所有具体的 HEX 代码]

## 排版 (Typography)
- Font Family: Inter, sans-serif
- H1: [size/weight]
- Body: [size/weight]

## 组件规范
- Spacing Scale: 4px, 8px, 16px, 32px (Tailwind standard)
- Border Radius: [e.g., 8px for cards, 4px for buttons]
- Shadows: [具体的阴影值]
```

#### 5. `BACKEND_STRUCTURE.md` (后端结构)
**作用**：数据库和 API 的蓝图。
```markdown
# Backend Structure

## Database Schema (Supabase/Postgres)
### Table: users
- id (uuid, pk)
- email (varchar)
- created_at (timestamp)

### Table: [table_name]
- [columns...]

## API Endpoints
- GET /api/products: [返回数据结构]
- POST /api/checkout: [输入参数与返回结果]

## Authentication & Security
- RLS (Row Level Security) 规则描述
```

#### 6. `IMPLEMENTATION_PLAN.md` (实施计划)
**作用**：逐步构建的指令集，AI 只能按步骤执行。
```markdown
# Implementation Plan

## Phase 1: Setup
- [ ] 1.1 初始化 Next.js 项目并安装依赖 (参考 TECH_STACK.md)
- [ ] 1.2 配置 Tailwind 和全局样式 (参考 FRONTEND_GUIDELINES.md)
- [ ] 1.3 设置文件夹结构

## Phase 2: Core Components
- [ ] 2.1 构建导航栏
- [ ] 2.2 构建基础 Layout

## Phase 3: Features
- [ ] 3.1 [具体功能 A]
...
```

---

### 第三步：AI 记忆与规则文件 (放在根目录)

#### 7. `CLAUDE.md` (或 `.cursor/rules`)
**作用**：AI 的操作手册，每次会话自动读取。
```markdown
# Project Rules & Context

## 核心指令
1. 每次会话开始时，必须先读取 `progress.txt`。
2. 编码前必须参考 `FRONTEND_GUIDELINES.md` 和 `TECH_STACK.md`。
3. 完成一个步骤后，必须更新 `progress.txt`。

## 技术约束
- 所有组件放在 `src/components/`。
- 使用 TypeScript 接口定义所有数据类型。
- 永远不要使用内联样式，只使用 Tailwind 类名。
- 错误处理：所有 API 调用必须包含 try/catch 和 UI 反馈。

## 参考文档
- PRD.md, APP_FLOW.md, TECH_STACK.md, FRONTEND_GUIDELINES.md, BACKEND_STRUCTURE.md, IMPLEMENTATION_PLAN.md
```

#### 8. `progress.txt` (进度追踪)
**作用**：AI 的外部记忆，解决“新会话丢失上下文”的问题。
```text
# Project Progress

## Status
当前阶段: Phase 2 - Component Build

## 已完成 (Done)
- [x] 项目初始化
- [x] 数据库 Schema 建立

## 进行中 (In Progress)
- [ ] 正在构建首页 Hero 组件

## 待办 (To Do)
- [ ] 用户登录流程
- [ ] 支付集成

## 已知问题/Bug (Known Issues)
- 移动端导航栏点击后未自动关闭
```

#### 9. `lessons.md` (可选但推荐：自我进化)
**作用**：记录 AI 犯过的错，防止重蹈覆辙。
```markdown
# Lessons Learned

- [日期]: AI 之前使用了错误的 import 路径，正确的路径规则是 @/components/...
- [日期]: 不要在客户端组件直接使用 server-only 的库。
```

---

### 第四步：推荐的文件目录结构

让 AI 按照这个结构来组织代码，不要让它乱放：

```text
my-app/
├── src/
│   ├── app/          (页面和路由)
│   ├── components/   (UI 组件)
│   ├── lib/          (工具函数)
│   └── styles/       (CSS)
├── public/
├── .env              (密钥，绝对不要提交到 git)
├── CLAUDE.md         (AI 规则文件)
├── progress.txt      (进度文件)
├── lessons.md        (经验教训)
├── PRD.md
├── APP_FLOW.md
├── TECH_STACK.md
├── FRONTEND_GUIDELINES.md
├── BACKEND_STRUCTURE.md
├── IMPLEMENTATION_PLAN.md
└── package.json
```

### 总结：如何使用这一套？

1.  **Interrogate**: 先用提示词让 AI 帮你把思路理顺。
2.  **Generate**: 让 AI 生成上述 6 个 Markdown 规范文档。
3.  **Lock**: 人工检查一遍文档，确认无误后保存，这就是你的“法律”。
4.  **Code**: 打开 Cursor 或 Claude Code，输入：“阅读 CLAUDE.md 和 progress.txt，然后开始执行 IMPLEMENTATION_PLAN.md 的步骤 X”。
5.  **Update**: 一个功能做完，要求 AI：“更新 progress.txt”。

这就是“氛围编程”不变成“屎山编程”的秘诀。