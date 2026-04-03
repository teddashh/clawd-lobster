🌐 [English](README.md) | [繁體中文](README.zh-TW.md) | [**简体中文**](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

<p align="center">
<strong>最好的终究是最好的，何必舍近求远？</strong><br>
<em>终极智能体体验 — 最轻量、精选功能、极致性能。</em>
</p>

<p align="center">
<sub>网页引导安装。多层记忆。多智能体共享知识。自由进化。</sub>
</p>

---

## Clawd-Lobster 是什么？

Claude Code 是大脑。Clawd-Lobster 是神经系统。

Claude Code 是目前最强的编程智能体，但它每次 session 结束就全部遗忘、只能跑在一台机器上、也没有技能管理。Clawd-Lobster 精准补足这些缺口：持久记忆、多机协同、精选技能、自我进化。不多不少，刚刚好。

**Clawd-Lobster 是一个生成器。** 你只需运行一次，它会帮你创建一个专属 **Hub** — 一个私有 GitHub 仓库，作为你的指挥中心。Hub 管理你所有的机器、工作区、记忆和技能。

```
  clawd-lobster (这个仓库 — 生成器)
       │
       │  运行一次 install.ps1
       │
       ▼
  clawd-yourname (你的私有 Hub — 为你生成)
       │
       │  这才是你每天实际使用的东西
       │
       ├── Machine A ── Claude Code + skills + memory
       ├── Machine B ── Claude Code + skills + memory
       └── Machine C ── Claude Code + skills + memory
            │
            全部连接。全部共享知识。
            全部通过 heartbeat 保持存活。
```

GitHub 是控制平面。Git 是通信协议。所有状态 — 技能、知识、工作区注册、heartbeat 状态 — 都存储在 git 中，自动同步。

**运行开销：25 MB RAM，672 KB 磁盘。** 一个 Python 进程（MCP Memory Server）加 SQLite。其余的要么运行即退出（通过 OS 调度器），要么在浏览器中呈现。零轮询、零守护进程、零臃肿。

```
Disk: 672 KB (代码 + 配置，不含 .git 和图片资源)
RAM:  ~25 MB (MCP server，唯一常驻进程)
CPU:  0% 空闲 (无轮询、无守护进程 — OS 调度器负责唤醒)
```

---

## 快速开始

### 第一台机器（创建你的 Hub）

**Windows**
```powershell
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
.\install.ps1
# 回答 4 个问题 → 你的私有 Hub 创建完成 → 一切就绪
```

**macOS / Linux**
```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
chmod +x install.sh && ./install.sh
```

**Docker**
```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
docker compose up -d && docker compose exec clawd bash
```

### 安装流程如何运作

安装程序会问你 4 个问题，仅此而已。其余一切全自动。

```
  ┌──────────────────────────────────────────────────┐
  │  1. Language?                                     │
  │     English / 繁體中文 / 简体中文 / 日本語 / 한국어   │
  │                                                   │
  │  2. First machine or joining?                     │
  │     → New Hub (I'm the first)                     │
  │     → Join Hub (I have the URL)                   │
  │                                                   │
  │  3. Fresh or importing?                           │
  │     → Fresh start                                 │
  │     → Absorb existing system                      │
  │                                                   │
  │  4. Name your Hub / Machine                       │
  │     → Hub: clawd-yourname (becomes private repo)  │
  │     → Machine: home-pc / office-vm / laptop       │
  │     → Domain: work / personal / hybrid            │
  └──────────────────────────────────────────────────┘
             │
             ▼  然后 9 个自动化步骤
  [1] Prerequisites   — Node, Python, Git, Claude Code
  [2] Authentication  — Claude + GitHub (OAuth clicks)
  [3] Create Hub      — copies template → private GitHub repo
  [4] Config          — writes ~/.clawd-lobster/config.json
  [5] Memory Server   — installs 24-tool MCP server
  [6] Claude Code     — configures CLAUDE.md + .mcp.json + skill registry
  [7] Workspaces      — clones repos, inits memory.db each
  [8] Scheduler       — registers sync + heartbeat tasks
  [9] Migration       — absorbs OpenClaw/Hermes/etc (if chosen)
```

### 9 个步骤各做了什么

| 步骤 | 操作 | 耗时 |
|------|--------|------|
| 1 | 检查前置依赖（Node、Python、Git） | 5 秒 |
| 2 | 认证 Claude Code + GitHub（2 次 OAuth 点击） | 30 秒 |
| 3 | **创建你的 Hub**（私有仓库）或克隆已有的 | 10 秒 |
| 4 | 写入配置 | 5 秒 |
| 5 | 安装 MCP Memory Server（21 个工具） | 10 秒 |
| 6 | 配置 Claude Code（CLAUDE.md + .mcp.json） | 5 秒 |
| 7 | 部署工作区（克隆仓库、初始化 memory.db） | 视情况 |
| 8 | 注册调度器 + heartbeat | 5 秒 |
| 9 | 吸收现有系统（如果选择了） | 视情况 |

| 平台 | 同步 | Heartbeat |
|----------|------|-----------|
| Windows | Task Scheduler (30 分钟) | Task Scheduler (30 分钟) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | Container lifecycle | Container lifecycle |

**总共只需：2 次 OAuth 点击。** 无需 API key，除非你要用 Oracle L4。

### 之后添加机器

只要你的 Hub 已在 GitHub 上，添加机器更简单：

```bash
git clone https://github.com/you/clawd-lobster
cd clawd-lobster
./install.ps1   # or ./install.sh

  → Join existing Hub
  → paste your Hub URL
  → name this machine
  → done (clones Hub, deploys workspaces, starts heartbeat)
```

---

## Chapter 1：记忆 — 你的智能体会记住

为什么这很重要：大多数 AI 智能体每次 session 都从零开始。它们重复犯错、重新学习上下文、浪费你的时间。

### 4 层记忆系统

| 层级 | 内容 | 速度 | 范围 |
|-------|------|-------|-------|
| **L1.5** | CC 自动记忆（原生） | 即时 | 当前项目 |
| **L2** | SQLite + 24 个 MCP 工具 | ~1ms | 每个工作区 |
| **L3** | Markdown 知识库 | ~10ms | 通过 git 共享 |
| **L4** | 云数据库（可选） | ~100ms | 跨工作区 |

### 重要性引擎（Salience Engine）

重要的记忆自动上浮，过时的自动下沉：
- 每次访问：重要性 +5%
- 手动强化：+20%（上限 2.0 倍）
- 30 天未访问：每天 -5%（下限 0.01，永不删除）

**CJK 感知的 token 估算** — 为多语言工作负载提供精准的压缩时机判断。

### 实际运作方式

记忆不仅仅是被动存储 — 它会主动影响你的智能体行为。

```
你做了一个决定
  → memory_record_decision("chose SQLite over Postgres", "local-first, no server needed")

下一次 session 开始
  → 启动协议加载重要的决定 + 知识
  → Claude 记得那个决定及其理由

30 天之后
  → 重要的决定依然高重要性（经常被访问 → 加分）
  → 琐碎的上下文已自然衰减（但永远不会被删除）
```

每条轨迹都有记录。每个工作区都能共享。你的智能体共同成长。知识持续积累。你的成果永不丢失。

---

## Chapter 2：工作区 — 你的智能体的工作场所

为什么这很重要：如果没有结构化的工作空间，智能体会混淆上下文、搞乱项目，也无法跨机器共享知识。

工作区是一个拥有记忆、技能和 spec 支持的项目目录。每个工作区都是一个 git 仓库（通常是 GitHub 上的私有仓库）。

### 创建工作区

两种方式：

1. **`/spec new`** — 引导式创建，附完整 spec（推荐）。详见 [Chapter 4](#chapter-4spec--你的智能体如何做计划)。
2. **`workspace-create.py`** — 快速创建，不附 spec：

```powershell
.\scripts\new-workspace.ps1 -name "my-api"
# 创建文件夹、memory.db、CLAUDE.md、GitHub 仓库 — 搞定。
```

### 工作区结构

```
my-project/
├── CLAUDE.md              ← 项目专属指令
├── .claude-memory/
│   └── memory.db          ← L2 记忆 (SQLite)
├── knowledge/             ← L3 知识 (git 同步)
├── skills/learned/        ← 自动生成的技能
├── openspec/              ← spec 产物 (如果使用 /spec)
│   ├── project.md
│   ├── changes/
│   └── specs/
└── .blitz-active          ← blitz 执行期间出现
```

### 激活与同步工作区

```
~/Documents/Workspace/
├── my-api/          ← 已注册，每 30 分钟同步
├── data-pipeline/   ← 已注册，每 30 分钟同步
└── random-notes/    ← 不是 git 仓库，同步会忽略
```

- 每个激活的工作区每 30 分钟通过 git 同步
- 在 Web UI 的工作区选项卡中切换工作区开关
- 停用的工作区停止同步但数据保留
- 调度器自动同步你工作区根目录下的所有 git 仓库

### 多机共享

这不只是一个智能体，而是一支舰队 — 它们共享同一个大脑。

```
        ┌─────── GitHub (Control Plane) ───────┐
        │  skills, knowledge, workspace registry │
        └──────────┬────────────┬───────────────┘
                   │            │
     ┌─────────────▼──┐  ┌─────▼─────────────┐
     │  Agent A        │  │  Agent B           │
     │  (office)       │  │  (cloud VM)        │
     │  Claude Code    │  │  Claude Code       │
     │  + local L2 ────┼──┼──► shared L3/L4    │
     └────────────────┘  └───────────────────┘
                   │            │
              ┌────▼────────────▼────┐
              │  Agent C (laptop)    │
              │  joins in 2 minutes  │
              └──────────────────────┘

Every agent contributes memories → shared knowledge grows
Any agent retrieves memories → collective intelligence available
```

- **L2** 保持本地（快速、按工作区隔离）— 每个智能体有自己的缓存
- **L3** 通过 git 同步 — 所有智能体读写同一个知识库
- **L4** 统一一切 — 跨工作区搜索、审计追踪、完整历史
- **新智能体加入？** `git clone + install.ps1` — 即刻继承所有积累的知识

### 永不掉线 — Heartbeat

你的智能体永远不会死掉。OS 调度器每 30 分钟检查一次：每个工作区 session 还活着吗？如果不是，就用 `claude --resume` 复活 — 完整上下文恢复。

```
OS Scheduler (every 30 min)
    │
    ▼ heartbeat.ps1 / heartbeat.sh
    │
    For each workspace in workspaces.json:
    ├─ Session alive? → skip
    └─ Session dead?  → claude --resume → context restored
    │
    ▼ All sessions visible via Claude Code Remote / App
```

- **终端开着** — session 存活，智能体拥有完整上下文，24/7 运行
- **终端关了** — heartbeat 检测到，自动复活
- **所有 session** — 都能通过 Claude Code Remote 在任意设备上查看
- **没有自定义守护进程** — OS 调度器就是看门狗。从不崩溃。零维护。

### 定时自动化

OS 级调度器（Windows Task Scheduler / cron / launchd）— 即使 Claude Code 未运行也照常执行：

- **Heartbeat** — 确保所有工作区 session 持续存活（断了就复活）
- **Git 同步** — 每 30 分钟拉取和推送所有仓库
- **重要性衰减** — 每日记忆重要性调整
- **客户端状态** — 追踪每台机器的 session、最后 heartbeat、已部署的工作区

---

## Chapter 3：技能 — 你的智能体能做什么

为什么这很重要：Claude Code 内置了一些技能，但你无法新增、修改或与团队分享。技能是你的竞争优势。

技能是独立的模块，就像 Chrome 扩展，只不过是给你的 AI 智能体用的。

### 三个技能来源

| 选项卡 | 内容 | 可切换？ |
|---|---|---|
| **Claude Native** | 内置：`/batch`、`/loop`、`/simplify`、`/compact` 等 | 技能：可以（通过权限）。命令：只读。 |
| **Clawd-Lobster** | 受管理的：memory、heartbeat、evolve、absorb、spec、connect-odoo | 可以 — 完整生命周期 |
| **Custom / Hub** | 你自己的 + 从 ClawHub 下载的社区技能 | 可以 — 完整生命周期 |

一个统一视图。三个来源。你系统上的每个技能 — 无论来自 Anthropic、Clawd-Lobster 还是你自己 — 都在同一个地方可见和管理。

### 核心技能（锁定 — 不可禁用）

| 技能 | 功能 | 为什么锁定 |
|---|---|---|
| Memory Server | 28 工具 MCP memory + SQLite | 没有记忆 = 没有智能体 |
| Heartbeat | 通过 OS 调度器的 session 保活 | 没有 heartbeat = session 会断 |
| Evolve | 自我进化 + TODO 处理 | 核心差异化功能 |
| Absorb | 从任何来源吸收知识 | 核心学习能力 |
| Spec | 引导式规划 + blitz 执行 | 核心开发工作流 |

### 可选技能

| 技能 | 功能 | 默认 |
|---|---|---|
| Migrate | 从其他 AI 方案导入 | 启用 |
| Connect-Odoo | Odoo ERP 集成（XML-RPC） | 禁用 |
| Codex Bridge | 将工作委派给 OpenAI Codex（worker + critic） | 禁用 |
| NotebookLM Bridge | 通过 Google NotebookLM 实现免费 RAG + 内容引擎 | 禁用 |

### 技能管理

每个技能都是独立模块，附有 `skill.json` manifest。通过 **Web UI** 或 **CLI** 管理。

**Web Dashboard** — 打开 `webapp/index.html`：
- 卡片式界面，ON/OFF 开关、状态指示器、分类筛选、搜索
- 内联配置 — 每个技能可独立编辑设置和凭据
- 健康检查 — 每个启用的技能都有绿/黄/红状态指示

**CLI 管理工具：**

```bash
python scripts/skill-manager.py list                     # 列出所有技能
python scripts/skill-manager.py enable connect-odoo      # 启用技能
python scripts/skill-manager.py disable connect-odoo     # 禁用技能
python scripts/skill-manager.py status                   # 详细状态
python scripts/skill-manager.py config connect-odoo      # 查看/编辑配置
python scripts/skill-manager.py credentials connect-odoo # 管理凭据
python scripts/skill-manager.py health                   # 运行所有健康检查
python scripts/skill-manager.py reconcile                # 重新生成 .mcp.json + settings.json
```

### 添加你自己的技能

1. 创建 `skills/my-skill/skill.json` — manifest 声明一切：

```jsonc
{
  "id": "my-skill",
  "name": "My Skill",
  "description": "What it does",
  "version": "0.1.0",
  "category": "utility",       // core | integration | automation | intelligence | utility
  "kind": "mcp-server",        // mcp-server | prompt-pattern | cron | poller
  "alwaysOn": false,
  "defaultEnabled": true,
  "mcp": {
    "serverName": "my-skill",
    "command": "python",
    "args": ["-m", "my_skill.server"],
    "cwd": "."
  },
  "permissions": { "allow": ["mcp__my-skill__my_tool"] },
  "credentials": [],
  "configSchema": { ... },
  "healthCheck": { "type": "mcp-ping", "intervalSeconds": 300 },
  "dependencies": { "skills": [], "system": ["python>=3.11"], "python": ["fastmcp>=3.0"] }
}
```

2. 实现技能（MCP server、脚本或 SKILL.md）
3. 运行 `skill-manager.py reconcile` — 它会自动注册并更新 `.mcp.json` + `settings.json`

**一个技能只需 3 条配置。** 无需 SDK。无需插件 API。无框架绑定。manifest **就是**合约。

---

## Chapter 4：Spec — 你的智能体如何做计划

为什么这很重要：没有计划的自主执行，只是随机生成代码。Spec 驱动开发给 Claude 一份蓝图来遵循。

基于 OpenSpec 方法论。Claude 引导你做规划，然后自主执行。

### 流程

```
You: "I want to build a membership site"
  ↓ /spec new
Claude asks questions (3W1H: Why, What, Who, How)
  ↓ you answer (typically 3-6 exchanges)
Claude creates:
  ├── GitHub repo + workspace
  ├── project.md (context capture)
  ├── proposal.md (Why + What + scope)
  ├── design.md (Architecture + data model)
  ├── specs/ (Gherkin scenarios with SHALL/MUST requirements)
  └── tasks.md (100-300 phased tasks, each 5-30 min)
  ↓ you review
"Ready to blitz?"
  ↓ yes
Claude executes all tasks autonomously
  ↓ blitz complete
V1 is ready. Evolution begins.
```

### 3W1H 标准

每个产物都遵循 Why、What、Who、How — 在各自适当的层级：

| 产物 | 层级 |
|---|---|
| project.md | 广泛的上下文捕获 |
| proposal.md | 范围界定 |
| design.md | 架构蓝图 |
| specs/ | 可测试的需求（SHALL/MUST + Gherkin） |
| tasks.md | 执行计划（分阶段，有文件引用） |

从规划到决策到日志到归档，一致适用同一套标准。

### Blitz 模式

全速自主执行。Spec 就是计划 — 不问问题，直接执行。

- **分支隔离** — 所有工作在 `blitz/v1`，main 在验证前保持干净
- **阶段提交** — 每个阶段完成后 `git commit`
- **暂停进化** — `.blitz-active` 标记告诉 evolve-tick 跳过该工作区
- **委派标记** — 前缀为 `[codex]` 的任务会跳过，留给外部执行
- **Blitz 结束后** — 合并到 main、将 spec 存为知识、建议下一步

### 验证

- 每个产物完成后运行自我验证（proposal、design、specs、tasks）
- 需求必须使用 SHALL 或 MUST — 绝不用 "should"、"could" 或 "might"
- 每条需求至少有一个 Gherkin scenario
- 每个 task 包含文件路径，且可在 5-30 分钟内完成
- 产物 DAG 是严格的：project → proposal → design → specs → tasks

### 命令

| 命令 | 功能 |
|---|---|
| `/spec new` | 引导式工作区 + spec 创建 |
| `/spec:status` | 显示进度（逐阶段附进度条） |
| `/spec:add "feature"` | 添加到现有 spec（增量操作） |
| `/spec:blitz` | 启动/恢复 blitz 执行 |
| `/spec:archive` | 归档已完成的变更 + 存为知识 |

---

## Chapter 5：进化 — 你的智能体如何进步

为什么这很重要：v1 只是起点。一个无法从自身工作中学习的智能体，就是一个会停滞的智能体。

v1 做好之后，你的智能体会持续自动变得更好。

### 进化循环

```
/absorb (input)
  ├── Scan folder → extract knowledge, decisions, TODOs
  ├── Read GitHub repo → learn patterns + skills
  └── Fetch URL → store insights
       ↓
evolve-tick (every 2 hours)
  ├── Pick highest-priority pending TODO
  ├── Create git worktree (isolated branch)
  ├── Run Claude to complete it (5 min timeout)
  └── Stage for review (never auto-merge)
       ↓
Review (you decide)
  ├── Web UI: see staged changes
  ├── Claude explains what changed and why
  └── Approve (merge) or Reject (archive + learn)
```

### 三阶段内容管线

源自 Claude、Codex 与 Gemini 的三方 AI 辩论，建立了一套内容生成流程：

1. **研究** — 收集来源、吸收上下文、提取关键洞察
2. **辩论** — 多个 AI 视角互相挑战和精炼内容
3. **生成** — 通过 NotebookLM 输出最终成品（幻灯片、信息图、播客、视频、测验）

### 吸收（Absorb）

喂它任何东西 — 文件夹、GitHub 仓库、URL。Claude 会自动分类所有发现的内容：

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

无需编写解析脚本。Claude Code **本身就是**解析器 — 它能读取任何格式、理解语义、保存有价值的内容。三种扫描深度：

| 深度 | 内容 |
|---|---|
| `shallow` | README、CLAUDE.md、顶层配置文件 |
| `normal` | shallow 全部 + 关键源码、技能定义、重要文档 |
| `deep` | 完整代码分析 — 所有源文件、测试、CI 配置、脚本 |

条目被分类为知识（事实、架构）、决策（经验、陷阱）、技能（可复用模式）和 TODO（待办事项）。

### 进化（自动）

每 2 小时，`evolve-tick.py` 会挑选一个待处理的 TODO，在隔离的 git worktree 中工作。关键特性：

- **每次一个 TODO** — 保持简单和安全
- **永不自动合并** — 所有工作留在 `evolve/<id>` 分支等待审查
- **学到的技能会保留** — 同时存储在数据库和 git 同步的技能文件中
- **有效性追踪** — 每次使用 +2%，每次改进 +10%，经过验证的技能分数 > 2.0x
- **跨智能体共享** — Agent A 学到的技能，Agent B 通过 git 同步也能用
- **自然淘汰** — 超过 90 天未使用的技能会被标记为可能过时
- **知识复利** — 一个工作区的决策会指导另一个工作区的工作，解决过的问题不需要再解决第二次

### Blitz vs 进化

| | Blitz | 进化 |
|---|---|---|
| 何时用 | 从 spec 构建 v1 | v1 之后持续改进 |
| 速度 | 所有 task 不间断 | 每 2 小时一个 TODO |
| 范围 | 整个项目 | 单一改进 |
| 分支 | `blitz/v1`（结束时合并） | `evolve/<id>`（逐一审查） |
| 自动合并 | 是（在 blitz 分支内） | 绝不 — 人工审查 |

---

## 架构

面向想了解内部实现的工程师。

### 底层是怎么运作的

```
┌──────────────────────────────────────────────┐
│          Clawd-Lobster (Skills Layer)         │
│                                              │
│  Memory System    Workspace Manager          │
│  Scheduler        Migration Tool             │
│  Self-Evolution   (your custom skills)       │
│                                              │
│  Installed via: .mcp.json + settings.json    │
│                 + CLAUDE.md                  │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│            Claude Code (The Brain)            │
│                                              │
│  Agent Loop · Streaming · Tools · Permissions │
│  Maintained by Anthropic. Auto-upgrades.     │
└──────────────────────────────────────────────┘
```

### 实际在运行什么？

整个仓库约 ~13K 行，但大部分是安装文件、文档和给 Claude 读的指令。当你的智能体工作时，实际占用内存的是：

| 层级 | 内容 | 行数 | RAM | 何时 |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (28 tools + SQLite) | ~1,400 | ~25 MB | 常驻 |
| **Runtime** | Odoo Connector (if enabled) | ~280 | ~22 MB | 启用时 |
| **Cron** | evolve-tick (TODO processor) | ~465 | ~20 MB peak | 每 2 小时，运行即退出 |
| **Cron** | heartbeat + sync | ~300 | ~5 MB peak | 每 30 分钟，运行即退出 |
| **Static** | Web UI (browser renders it) | ~1,900 | 0 on server | 按需 |
| **Setup** | Installers, workspace-create, skill-manager | ~2,800 | 0 | 只运行一次 |
| **Docs** | SKILL.md files, README, CHANGELOG | ~3,500 | 0 | Claude 按需读取 |
| **Config** | skill.json manifests, templates | ~900 | 0 | 启动时读取 |

**常驻开销：一个 Python 进程 (~25 MB) + SQLite。** 其余的要么运行即退出（cron 脚本），要么在浏览器中（Web UI），或者只是 Claude 需要上下文时才读取的文件。

### 与 Claude Code 的关系

其他框架从头重建 Claude — 然后调用 Claude 的 API 来进行实际的思考：

```
Heavyweight framework approach:
  Custom Engine (300K LOC) ──API call──→ Claude Model
                                ↑
                    Anthropic can change pricing,
                    revoke OAuth, rate-limit,
                    or deprecate endpoints — at any time.
                    Your 300K lines are at their mercy.

Clawd-Lobster approach:
  User runs: claude login          ← human authenticates once
  OS scheduler runs: claude --resume  ← Anthropic's own CLI, their own flag
  Clawd-Lobster just keeps the session alive and manages skills.
```

我们不调用 Claude 的 API。我们不管理 OAuth token。我们不处理 rate limit。我们调度的是 **Claude Code 本身** — 一个 Anthropic 自己构建、自己发布、自己维护的工具。当他们改进 Claude Code，我们就跟着变快。当他们改 API，我们完全不受影响。

其他框架在给**别人的车**做遥控器。我们坐**在车里**。

### 与 GitHub 的关系

GitHub 是一切的控制平面：

- **Hub 仓库** — 你的私有指挥中心
- **工作区仓库** — 每个项目都是私有仓库
- **Git 同步** — 知识、技能和状态每 30 分钟同步
- **Heartbeat 状态** — 机器健康度推送到 git
- **Spec 产物** — 提交到工作区仓库

### 为什么不自己做引擎？

其他框架从头重建整个 AI 智能体 — 30 万行代码、自定义 agent loop、自定义工具系统、什么都自己做。等 Anthropic 发布更好的模型，他们就得忙着重写适配层。

**Clawd-Lobster 不跟 Claude Code 竞争，而是让它更完整。**

我们以 Claude Code — 世界上最先进的编程智能体 — 为基础，精准补足它所缺少的：持久记忆、多智能体协同、精选技能。不多不少，刚刚好。

> *零冗余。零重写。纯粹的 Claude Code，增强版。*

### 设计哲学

#### 1. 最好的智能体已经存在，直接用就好。

Claude Code 背后是世界上最大的 AI 安全实验室。数百万工程小时投入到它的 agent loop、流式传输、权限和工具系统中。从零开始重造这些不是雄心壮志 — 而是浪费。**站在巨人的肩膀上。**

#### 2. 少即是多，而且多得多。

框架的每一行代码都需要维护。Clawd-Lobster 只有约 2 千行，因为 Claude Code 原生的扩展点（MCP、hooks、CLAUDE.md）本身就是最好的插件系统。**三条配置 = 一个技能。零 SDK。**

#### 3. 会遗忘的智能体注定失败。

大多数 AI 智能体每次会话都从零开始。它们重复犯错、重新学习上下文、浪费你的时间。Clawd-Lobster 的 4 层记忆加重要性追踪确保**重要的内容上浮、噪音逐渐消退、关键信息永不丢失。**

#### 4. 你的智能体应该跟你走到哪里。

一台电脑？没问题。三台设备？它们应该共享同一个大脑。GitHub 作为控制平面，git 同步作为协议。**2 分钟加入一台新设备。零基础设施。**

#### 5. 永远踩在最新的浪尖上。

当 Anthropic 发布 Opus 4.7、1M context、新工具时 — 你即刻获得。无需重写适配层。无需锁定版本。无需等待社区补丁。**用 Claude Code 最好的时间是昨天，其次是现在。**

#### 6. 能调度的就不要自己写。

其他框架写自定义守护进程让智能体 24/7 运行。我们用 `cron` + `claude --resume`。其他框架管理 OAuth token 来调用 Claude 的 API。我们让用户输入一次 `claude login` 就行。**你写的每一行认证代码，都是供应商改版时可能出错的一行。你没写的每一行，就是出不了错的一行。** OS 调度器从 1970 年代就稳定运行至今。你的自定义守护进程上周二才写好。

#### 7. 巨人长高了，你也跟着长高。

Claude Code 内部有记忆整合（autoDream）、常驻智能体（KAIROS）、多智能体协调（Coordinator Mode）和复杂规划（ULTRAPLAN）等系统。有些已上线，有些还在 feature flag 后面。我们已经用 2K 行代码构建了大部分等价功能。

但关键在于：**当 Anthropic 原生推出这些功能，我们不用重写 — 我们退役。** KAIROS 上线了？我们的 heartbeat 优雅让位。autoDream 改进了？它与我们的重要性引擎共存。Coordinator Mode 发布了？我们的 evolve-tick 直接用。

其他框架与 Claude Code 竞争。我们与它互补。他们在 Claude Code 增加功能时得重写。我们得到的是删代码的机会。**我们的代码随时间缩小，他们的则不断膨胀。**

### 项目结构

```
clawd-lobster/
├── skills/                          技能模块（每个都有 skill.json manifest）
│   ├── memory-server/               24 工具 MCP 记忆 + 重要性 + 进化
│   │   ├── mcp_memory/              Python package (pip install -e .)
│   │   └── skill.json               Manifest
│   ├── connect-odoo/                Odoo ERP 集成 (XML-RPC + poller)
│   │   ├── connect_odoo/            MCP server + poller
│   │   └── skill.json               Manifest
│   ├── evolve/                      自我进化 prompt pattern
│   │   └── skill.json               Manifest
│   ├── heartbeat/                   Session 保活 (cron)
│   │   └── skill.json               Manifest
│   ├── absorb/                      从任何来源吸收知识
│   │   └── skill.json               Manifest
│   ├── spec/                        引导式规划 + blitz 执行
│   │   └── skill.json               Manifest
│   ├── codex-bridge/                将工作委派给 OpenAI Codex
│   │   └── skill.json               Manifest
│   ├── notebooklm-bridge/           通过 NotebookLM 实现免费 RAG + 内容引擎
│   │   └── skill.json               Manifest
│   ├── migrate/                     从现有方案导入
│   │   └── skill.json               Manifest
│   └── learned/                     从经验自动生成的技能
│
├── scripts/
│   ├── skill-manager.py             技能管理 CLI
│   ├── sync-all.ps1                 Windows: 自动 git 同步 + 衰减
│   ├── sync-all.sh                  Linux/macOS: 自动 git 同步 + 衰减
│   ├── heartbeat.ps1                Windows: session 保活
│   ├── heartbeat.sh                 Linux/macOS: session 保活
│   ├── new-workspace.ps1            创建工作区 + GitHub 仓库
│   ├── workspace-create.py          自动化工作区创建
│   ├── validate-spec.py             Spec 产物硬性验证
│   ├── setup-hooks.sh               安装 git pre-commit hooks (Unix)
│   ├── setup-hooks.ps1              安装 git pre-commit hooks (Windows)
│   ├── evolve-tick.py               模式提取 + 提案 + 重要性衰减
│   ├── notebooklm-sync.py           自动推送工作区文档至 NotebookLM
│   ├── init_db.py                   初始化记忆数据库
│   └── security-scan.py             5 工具安全扫描器
│
├── templates/                       配置模板（不含密钥）
│   ├── global-CLAUDE.md
│   ├── workspace-CLAUDE.md
│   ├── mcp.json.template
│   └── settings.json.template
│
├── webapp/                          技能管理 Dashboard
│   └── index.html                   3 选项卡 UI：Skills + Setup + Settings
│
├── knowledge/                       共享知识库（git 同步）
├── soul/                            智能体个性（可选）
├── workspaces.json                  工作区注册表
├── install.ps1                      Windows 安装器（4 阶段）
├── install.sh                       Linux/macOS 安装器（4 阶段）
├── Dockerfile                       Docker build
├── docker-compose.yml               Docker Compose 配置
├── LICENSE                          MIT
└── README.md
```

---

## 横向对比

| | Claude Code（原生） | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| 智能体引擎 | Anthropic | 自研（300K LOC） | 自研（50K LOC） | **Anthropic（原生）** |
| 认证模式 | 人工登录 | OAuth/API key | API key | **人工登录一次** |
| 费用模式 | 订阅制 | 按 token 计费 API | 按 token 计费 API | **订阅制（包月）** |
| 永不掉线 | 无 | 自定义守护进程 | 自定义守护进程 | **OS heartbeat + 自动复活** |
| 持久记忆 | 无 | 混合搜索 | FTS5 + LLM | **4 层 + 重要性引擎** |
| 多智能体共享记忆 | 无 | 无 | 无 | **有（git 同步）** |
| 技能管理 | 不适用 | 仅 CLI | 手动 | **Web UI + CLI + manifest** |
| 智能体进化 | 无 | 无 | 自改进技能 | **有（24 MCP 工具）** |
| 多设备协同 | 无 | 无 | 无 | **有（MDM 风格）** |
| Session 管理 | 手动 | Gateway 进程 | 手动 | **自动复活所有 session** |
| 上手门槛 | 手动配置 | 复杂 | 中等 | **网页向导，5 种语言** |
| 自动升级 | 有 | 无 | 无 | **有** |
| 代码量 | 0 | ~300K LOC | ~50K LOC | **~2K LOC** |
| Anthropic API 变更 | 透明 | 破坏性 | 破坏性 | **透明** |
| 审计追踪 | 无 | 安全审计 | 无 | **完整（每个操作）** |
| 技能安装 | — | Plugin SDK | 改 3 个文件 | **1 个 manifest + reconcile** |

---

## 路线图

**技能**
- [x] Odoo ERP Connector — XML-RPC 集成 + poller (v0.4.0)
- [x] Codex Bridge — 将工作委派给 OpenAI Codex，worker + critic 角色 (v0.5.0)
- [x] NotebookLM Bridge — 通过 Google NotebookLM 实现免费 RAG + 内容引擎 (v0.5.0)
- [x] Spec 驱动开发 — 使用 OpenSpec 方法论的引导式规划 (v0.5.0)
- [ ] SearXNG — 私有自托管网页搜索，数据不出内网
- [ ] Docker Sandbox — 隔离的代码执行环境，用于不受信任的操作
- [ ] Browser Automation — 基于 Playwright 的网页交互

**平台**
- [x] Linux 安装器（bash）+ macOS 安装器 (v0.3.0)
- [x] 技能管理 Dashboard — Web UI + CLI 完整技能生命周期 (v0.4.0)
- [x] 技能 manifest 系统 — `skill.json` 含配置、凭据、健康检查 (v0.4.0)
- [ ] Supabase L4 — 一键部署云数据库（无需 Oracle wallet）

**进化**
- [x] 进化循环 + 提案 — evolve 生成 git 同步的提案，而非直接 TODO (v0.5.0)
- [ ] 技能商城 — 社区贡献的技能，一键安装
- [x] 自动技能生成 — 智能体从成功模式中学习 (v0.3.0 evolve skill)
- [ ] 团队模式 — 多用户共享工作区，基于角色的访问控制
- [ ] 智能体间委托 — 智能体之间互相分配任务

---

## FAQ

### 「这不就是 Claude Code 套个壳吗？」

对，这就是重点。

Claude Code 是目前最强的编程智能体 — 背后是 Anthropic 数百万工程小时。OpenClaw 从头重建引擎（30 万行）。Hermes 再重建一次（5 万行）。我们只加上缺的部分（2 千行），保留最好的引擎。

当 Anthropic 推出下一个突破，我们即刻获得。他们得忙着重写适配层。

### 「但其他智能体可以 24/7 运行并持续学习」

我们的也可以。调度器每 30 分钟同步知识。记忆通过重要性衰减每天自然进化。学到的技能通过 git 传播到所有机器。**智能体不需要一直运行，知识也会持续增长。**

heartbeat 确保 session 持续存活：如果终端关了，OS 调度器检测到就用 `claude --resume` 复活 — 完整上下文恢复。不需要自定义守护进程。就是 Claude Code，永远在线。参见[架构](#与-claude-code-的关系)章节了解我们如何与按 token 计费的 API 框架不同地处理 24/7。

### 「其他智能体也有 heartbeat 和时间感知」

我们也有 — 但更聪明。我们不跑自定义守护进程，而是用 OS 调度器（Task Scheduler / launchd / cron）做 heartbeat。它每 30 分钟检查：session 还活着吗？需要 git 同步吗？重要性衰减到了吗？客户端状态？全部搞定。OS 调度器从不崩溃、从不需要调试、空闲时也不消耗 token。当 Claude Code 推出原生 24/7 模式（KAIROS — 已经在代码里了），我们免费直接用。零代码变更。详见 [Chapter 2](#永不掉线--heartbeat)。

### 「Claude Code 已经有内置技能了，为什么还需要更多？」

Claude Code 内置了 `/commit`、`/review-pr`、`/init` 等技能。它们不错，但也是**封闭的** — Anthropic 决定它们做什么、怎么运作、何时变更。你无法新增自己的。你无法修改它们。你无法与团队分享。

这就像手机上的内置应用。Clawd-Lobster 是应用商店。

| | Claude Code 内置 | **Clawd-Lobster 技能** |
|---|---|---|
| 谁创建 | Anthropic | 你、你的团队、社区 |
| 谁控制 | Anthropic | 你 |
| 可以修改吗 | 不能 | 可以 — 那是你的代码 |
| 可以新增吗 | 不能 | 可以 — `skill.json` + 实现 |
| 可以分享吗 | 不能 | 可以 — 推送到 GitHub / ClawHub |
| 领域专属 | 不行（通用开发工具） | 可以 — 你的 ERP、CRM、工作流 |
| 凭据管理 | 不适用 | 内置每技能凭据系统 |
| 启用/禁用 | 不适用 | 一个开关，Web UI 或 CLI |

你的公司需要一个部署前运行合规检查的技能？一个每 5 分钟从 Odoo 同步 CRM 数据的技能？一个用你特定格式生成双语 PDF 报告的技能？Claude Code 永远不会推出这些。**你的技能就是你的竞争优势。它们应该在你的系统里，不是别人的。**

### 「Claude Code 已经有 MCP 和技能了，为什么还要再做一层？」

Claude Code 给你 MCP — 一个注册工具服务器的协议。这就像说 Chrome 让你安装扩展。没错。但 Chrome 还有 **Chrome 网上应用店** — 因为手动安装 `.crx` 文件不叫管理扩展。

Claude Code 给你的：
- `.mcp.json` — 一个扁平的服务器命令列表。没有元数据。没有生命周期。
- `settings.json` — 一个扁平的允许工具列表。没有分组。没有开关。
- `CLAUDE.md` — 自由格式文本。没有 schema。没有验证。

实际上这意味着：
- **安装技能？** 手动编辑 3 个 JSON 文件然后运行 `pip install`。
- **禁用技能？** 手动从 2 个文件删除条目，希望没遗漏。
- **凭据？** 每个技能存储方式不同。有的用环境变量、有的用文件、有的硬编码。
- **运行正常吗？** 不知道。打开终端碰运气。
- **第二台机器？** 全部从头再来一遍。
- **10 个技能？** 你的 `.mcp.json` 变成一堵看不懂的 JSON 墙。祝你好运。

Clawd-Lobster 的技能层补上了 MCP 没有的东西：

| MCP（原生） | 技能管理（我们的） |
|---|---|
| 扁平 JSON 配置 | `skill.json` manifest 含 schema、凭据、健康检查、依赖项 |
| 手动编辑安装 | `skill-manager.py enable <id>` — 一条命令 |
| 手动编辑移除 | `skill-manager.py disable <id>` — 一条命令，干净移除 |
| 没有凭据标准 | 集中式 `~/.clawd-lobster/credentials/`，每技能字段定义 |
| 没有健康监控 | 内置健康检查（mcp-ping、command、HTTP） |
| 没有 UI | Web dashboard 含卡片、开关、搜索、分类筛选 |
| 每台机器各自配置 | 通过 git 跨机器同步注册表 |
| 没有依赖追踪 | 技能声明所需 — 其他技能、系统工具、Python 包 |

**MCP 是协议。我们是包管理器。**

就像 `npm` 不是要取代 Node.js — 它让 Node.js 在规模化时变得可用。我们的技能层不是要取代 MCP — 它让 MCP 在你有 5、10 或 50 个技能分布在多台机器上时变得可管理。详见 [Chapter 3](#chapter-3技能--你的智能体能做什么) 完整的技能管理系统。

### 「Anthropic 会封杀这个吗？」

我们没做任何 Anthropic 禁止的事。精确地说：

- **我们做的事：** 通过 OS cron/Task Scheduler 调度 `claude` CLI 命令。用 `claude --resume` 恢复现有 session。使用 Anthropic 自己定义的 MCP 协议。
- **我们不做的事：** 程序化 OAuth 登录。API key 自动化。Token 抓取。认证绕过。逆向工程。

用户运行一次 `claude login` — 一个人，在浏览器中，用他们的 Pro 订阅。之后，OS 调度器用 Anthropic 自己在 CLI 中提供的 flag（`--resume`、`-p`、`--allowedTools`）保持 session 存活。这跟用 cron 调度 `git pull` 没什么区别。**我们是自动化一个 CLI 工具，不是冒充用户。**

其他框架直接调用 Claude 的 API — 他们需要 API key、管理 OAuth refresh token、处理 rate limit、然后祈祷定价不要变。每次 API 变更对他们来说都是破坏性的。对我们来说，是透明的 — Claude Code 自己处理自己的认证。

### 「重度工作量的 API 费用呢？」

「昂贵的 API」这个论点，基于按 token 计费的假设。有了 Pro 订阅（$20/月），**没有按 token 的费用。** 你的第 1 个任务和第 480 个任务花费相同：边际成本 $0。

这直接消除了其他框架需要的「思考用贵模型、苦力用便宜模型」架构。你不需要在本地跑 Ollama 7B 处理廉价任务。你不需要两套推理架构。你不需要一个模型路由器来决定用哪个大脑。

一个订阅。一个引擎。一个大脑。无限任务。

当 rate limit 命中时（迟早的），Clawd-Lobster 的 skill-manager 会优雅地排队工作。没有 token 预算恐慌。没有账单惊喜。**可预测的成本本身就是功能。**

---

## 参与贡献

欢迎贡献！最简单的参与方式：

1. **添加技能** — 在 `skills/` 目录下创建一个文件夹，包含 `SKILL.md` 或 MCP server
2. **改进模板** — 优化 `templates/` 中的默认配置
3. **平台适配** — 协助完善 Linux/macOS 安装器

---

## 许可证

MIT — 随便用。

---

<p align="center">
<sub>本项目与 Anthropic 无关。基于 <a href="https://claude.ai/code">Claude Code</a> 构建。</sub>
</p>
