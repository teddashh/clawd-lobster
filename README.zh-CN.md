[English](README.md) | [繁體中文](README.zh-TW.md) | [**简体中文**](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/footprint-25MB_RAM-orange)

<p align="center">
<strong>从想法到可用的代码，只需一场对话。</strong><br>
<em>Spec Squad 将你的描述转化为经过审查、测试的代码库 — 由 Claude Agent SDK 驱动。</em>
</p>

<p align="center">
<sub>Web 仪表盘 + CLI。多 Agent 开发。持久内存。多机同步。</sub>
</p>

---

## 什么是 Clawd-Lobster？

Claude Code 是大脑，Clawd-Lobster 是神经系统。

Claude Code 是目前最强大的编程 Agent，但它在 session 之间会遗忘所有记忆、只能在单机运行、也没有技能管理。Clawd-Lobster 正好补上这些缺口：一个 **Spec Squad** 通过对抗式多 Agent 协作来规划、审查、构建和测试你的代码 — 加上持久内存、多机编排、精选技能和自我进化。

**Clawd-Lobster 是一个生成器。** 你只需运行一次，它就会创建你的专属 **Hub** — 一个私有 GitHub 仓库，作为你的指挥中心。你的 Hub 管理所有机器、工作区、内存和技能。

```
  clawd-lobster (this repo -- the generator)
       |
       |  pip install -e . && clawd-lobster setup
       |
       v
  clawd-yourname (YOUR private Hub -- generated for you)
       |
       |  this is what you actually use day-to-day
       |
       +-- Machine A -- Claude Code + skills + memory
       +-- Machine B -- Claude Code + skills + memory
       +-- Machine C -- Claude Code + skills + memory
            |
            All connected. All sharing knowledge.
            All always alive via heartbeat.
```

GitHub 是控制平面，Git 是通信协议。所有状态 — 技能、知识、工作区注册表、心跳状态 — 都存放在 git 中并自动同步。

**运行足迹：25 MB 内存、672 KB 磁盘空间。** 一个 Python 进程（MCP Memory Server）加上 SQLite。其余一切通过操作系统调度器运行后退出，或在浏览器中运行。零轮询、零守护进程、零臃肿。

---

## 快速开始

三种上手方式，根据你的风格选择。

### Web UI（推荐新手使用）

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
# Browser opens at http://localhost:3333
# Onboarding wizard walks you through everything
```

### 终端（适合进阶用户）

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# 4-step interactive wizard: prerequisites -> persona -> workspace root -> first workspace
```

### 传统方式（安装脚本）

**Windows**
```powershell
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
.\install.ps1
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

### 安装流程说明

安装程序会检查前置条件、验证 Claude Code + GitHub、创建你的 Hub、安装 MCP Memory Server（32 个工具）、配置工作区，以及注册调度器 + 心跳。全程只需 2 次 OAuth 点击，不需要 API 密钥。

| 平台 | 同步 | 心跳 |
|----------|------|-----------|
| Windows | Task Scheduler (30 min) | Task Scheduler (30 min) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | Container lifecycle | Container lifecycle |

---

## Web 仪表盘

使用 `clawd-lobster serve` 启动（默认端口 3333）。仪表盘提供三个主要视图：

### /onboarding — 设置向导

首次访问者会自动跳转到此页。向导会检查前置条件（Python、Claude CLI、Git、pip），让你选择角色（引导 / 专家 / 技术），设置工作区根目录，并创建第一个工作区 — 全部在浏览器中完成。

### /workspaces — 工作区管理

列出所有已注册的工作区及实时状态。每个工作区卡片显示路径、内存数据库大小、git 同步状态和 Spec Squad 阶段。可直接从仪表盘创建新工作区或切换同步开关。

### /squad — Spec Squad

多 Agent 开发界面。开始探索对话、观看 Architect 编写规格、看 Reviewer 提出挑战、跟踪 Coder 的构建过程，并监控 Tester 的验证结果 — 全部通过 SSE 实时更新进度。

---

## Spec Squad — 多 Agent 开发

Spec Squad 是 v1.0 的核心功能。四个专业 Agent 协作，将你的想法转化为经过审查、测试的代码 — 使用 Claude Agent SDK。

### 流程

```
You describe your project
  | clawd-lobster squad start (terminal)
  | or /squad page (web)
  v
Discovery Interview
  | Senior consultant asks 3-6 smart questions (3W1H: Why, What, Who, How)
  | When enough context is gathered: DISCOVERY_COMPLETE
  v
Architect
  | Writes complete OpenSpec: project.md -> proposal.md -> design.md
  | -> specs/ (SHALL/MUST + Gherkin) -> tasks.md (phased, 5-30 min each)
  v
Reviewer (adversarial)
  | Tears apart the spec. Finds gaps, ambiguities, weak decisions.
  | Verdict: REVISE (with issues) or APPROVED (with confidence score)
  | Up to 5 review rounds -- Architect must fix every issue
  v
Coder
  | Executes the approved spec task by task, phase by phase
  | Commits after each phase. Marks tasks done in tasks.md
  v
Tester
  | Verifies every SHALL/MUST requirement against the code
  | Runs Gherkin scenarios. Verdict: PASSED or ISSUES (with pass rate)
  v
Done -- reviewed, tested codebase ready
```

### 对抗式审查的工作方式

Reviewer 被要求"严厉但公正"。它会阅读 `openspec/` 中的每个文件，挑战架构、需求和任务拆分。如果发现问题，Architect 必须修改。这个循环最多执行 5 轮，直到 Reviewer 给出 APPROVED 裁定并附上置信分数。结果是在写下任何一行代码之前，规格就已经过压力测试。

### Web 模式 vs 终端模式

| | Web (`/squad`) | Terminal (`clawd-lobster squad start`) |
|---|---|---|
| Discovery | 浏览器中的聊天界面 | stdin/stdout |
| 进度 | 实时 SSE 事件，可视化阶段 | 终端打印阶段标签 |
| 构建确认 | 在浏览器中提示 | `Build now? (y/n)` |
| 状态 | 保存于 `.spec-squad.json` | 同一文件 |
| 底层引擎 | 相同的 `squad.py` async 核心 | 相同的 `squad.py` async 核心 |

两种模式使用相同的流程、相同的 Agent SDK 调用、相同的状态文件。选择适合你工作流程的即可。

---

## 技能

9 个技能模块，每个都有 `skill.json` 清单。共 32 个 MCP 工具。

### 核心技能（锁定）

| 技能 | 类型 | 功能 |
|---|---|---|
| **Memory Server** | mcp-server | 26 个 MCP 工具的内存系统，含 SQLite、显著性引擎、CJK 感知压缩 |
| **Heartbeat** | cron | 通过操作系统调度器维持 session 存活 — 自动复活已停止的 session |
| **Evolve** | prompt-pattern | 模式提取、改进提案、显著性衰减 |
| **Absorb** | prompt-pattern | 从文件夹、GitHub 仓库、URL 导入知识 |
| **Spec** | prompt-pattern | 使用 OpenSpec 方法论进行引导式规划 + 闪电执行 |

### 可选技能

| 技能 | 类型 | 功能 | 默认 |
|---|---|---|---|
| **Migrate** | prompt-pattern | 从现有 AI 设置导入（自动检测格式） | 启用 |
| **Connect-Odoo** | mcp-server | Odoo ERP 集成 — 通过 XML-RPC + poller 提供 6 个 MCP 工具 | 禁用 |
| **Codex Bridge** | prompt-pattern | 将工作委派给 OpenAI Codex，含 worker + critic 角色 | 禁用 |
| **NotebookLM Bridge** | prompt-pattern | 通过 Google NotebookLM 提供免费 RAG + 内容引擎 | 禁用 |

### 技能管理

每个技能都是自包含的模块，带有 `skill.json` 清单。通过 **Web UI** 或 **CLI** 管理：

```bash
clawd-lobster serve                                      # Web dashboard with toggles
python scripts/skill-manager.py list                     # Table of all skills
python scripts/skill-manager.py enable connect-odoo      # Enable a skill
python scripts/skill-manager.py disable connect-odoo     # Disable a skill
python scripts/skill-manager.py health                   # Run all health checks
python scripts/skill-manager.py reconcile                # Regenerate .mcp.json + settings.json
```

### 添加自定义技能

在 `skills/my-skill/skill.json` 创建清单，实现技能（MCP server、script 或 SKILL.md），然后运行 `skill-manager.py reconcile`。一个技能只需 3 个配置项 — 不需要 SDK、不需要 plugin API、没有框架锁定。

---

## 架构

### 3 层设计

```
+----------------------------------------------+
|          Skills Layer (Clawd-Lobster)         |
|                                               |
|  Memory System    Workspace Manager           |
|  Spec Squad       Scheduler                   |
|  Self-Evolution   (your custom skills)        |
|                                               |
|  Installed via: .mcp.json + settings.json     |
|                 + CLAUDE.md                    |
+----------------------+------------------------+
                       |
+----------------------v------------------------+
|            Claude Code (The Brain)             |
|                                                |
|  Agent Loop - Streaming - Tools - Permissions  |
|  Maintained by Anthropic. Auto-upgrades.       |
+------------------------------------------------+
```

### 4 层内存

| 层级 | 内容 | 速度 | 范围 |
|-------|------|-------|-------|
| **L1.5** | Claude Code 自动记忆（原生） | 即时 | 当前项目 |
| **L2** | SQLite + 26 个 MCP 工具 | ~1ms | 每个工作区 |
| **L3** | Markdown 知识库 | ~10ms | 通过 git 共享 |
| **L4** | 云数据库（可选） | ~100ms | 跨工作区 |

显著性引擎让重要记忆保持可访问：每次访问提升 5% 显著性，手动强化提升 20%（上限 2.0x），未被访问的项目在 30 天后每天衰减 5%（下限 0.01 — 永不删除）。

### 实际在运行什么？

| 层级 | 内容 | 行数 | 内存 | 运行时机 |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (26 tools + SQLite) | ~1,400 | ~25 MB | 持续运行 |
| **Runtime** | Odoo Connector (if enabled) | ~280 | ~22 MB | 启用时 |
| **Runtime** | Web Dashboard (stdlib HTTP) | ~800 | ~15 MB | 提供服务时 |
| **Cron** | evolve-tick (proposal generator) | ~465 | ~20 MB peak | 每 2 小时，运行后退出 |
| **Cron** | heartbeat + sync | ~300 | ~5 MB peak | 每 30 分钟，运行后退出 |
| **Setup** | CLI + onboarding + squad orchestrator | ~1,200 | 0 | 按需运行 |
| **Config** | skill.json manifests, templates | ~900 | 0 | 启动时读取 |

**常驻足迹：一个 Python 进程（约 25 MB）+ SQLite。** Web 仪表盘使用标准库 `http.server` — 没有 Flask、没有 FastAPI、没有外部依赖。

### 设计哲学

1. **站在巨人的肩膀上。** Claude Code 背后有数百万工程小时。我们补上缺少的部分（约 3K 行），保留最好的引擎。

2. **代码越少，问题越少。** 三个配置项 = 一个技能。零 SDK。操作系统调度器从 1970 年代就稳定至今 — 我们使用 `cron` + `claude --resume` 而非自建守护进程。

3. **巨人成长，你也成长。** 当 Anthropic 推出原生内存、24/7 Agent 或多 Agent 协调时 — 我们不需要重写，我们退役代码。**我们的代码库随时间缩小，他们的则持续增长。**

完整文件树和内部结构请参阅 [ARCHITECTURE.md](ARCHITECTURE.md)。

---

## CLI 参考

| 命令 | 功能 |
|---|---|
| `clawd-lobster serve` | 在 localhost:3333 启动 Web 仪表盘 |
| `clawd-lobster serve --port 8080` | 使用自定义端口 |
| `clawd-lobster serve --daemon` | 在后台运行服务器 |
| `clawd-lobster setup` | 运行终端设置向导 |
| `clawd-lobster workspace create <name>` | 创建新工作区 |
| `clawd-lobster workspace create <name> --repo` | 创建工作区 + 私有 GitHub 仓库 |
| `clawd-lobster workspace create <name> --dry-run` | 预览而不实际更改 |
| `clawd-lobster squad start` | 以终端模式启动 Spec Squad |
| `clawd-lobster squad start --workspace <path>` | 指定目标工作区 |
| `clawd-lobster status` | 显示系统健康状态、工作区、版本 |
| `clawd-lobster --version` | 显示版本 |

---

## 多机设置

### Hub 模式

你的 Hub 是一个私有 GitHub 仓库，作为你的指挥中心。每台机器都 clone Hub 并自动同步。

```
        +------- GitHub (Control Plane) -------+
        |  skills, knowledge, workspace registry|
        +----------+------------+--------------+
                   |            |
     +-------------v--+  +-----v-------------+
     |  Agent A        |  |  Agent B           |
     |  (office)       |  |  (cloud VM)        |
     |  Claude Code    |  |  Claude Code       |
     |  + local L2 ----+--+---> shared L3/L4   |
     +----------------+  +-------------------+
                   |            |
              +----v------------v----+
              |  Agent C (laptop)    |
              |  joins in 2 minutes  |
              +---------------------+
```

### 添加另一台机器

```bash
git clone https://github.com/you/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# Choose "Join existing Hub" -> paste your Hub URL -> name this machine -> done
```

新机器会立即继承所有积累的知识。L2（SQLite）在每个工作区保持本地，L3（markdown）通过 git 同步，L4（可选的云数据库）统一一切。

### 永不停机 — 心跳机制

你的 Agent 永远不会停止。操作系统调度器每 30 分钟检查一次：每个工作区的 session 是否存活？如果没有，就用 `claude --resume` 复活 — 完整的上下文恢复。不需要自建守护进程。只有 Claude Code，永远在线。

---

## 工作区

工作区是一个带有内存、技能和规格支持的项目目录。

### 工作区结构

```
my-project/
+-- CLAUDE.md              <- project-specific instructions
+-- .claude-memory/
|   +-- memory.db          <- L2 memory (SQLite)
+-- knowledge/             <- L3 knowledge (git-synced)
+-- skills/learned/        <- auto-generated skills
+-- openspec/              <- spec artifacts (if using /spec or squad)
|   +-- project.md
|   +-- changes/
|   +-- specs/
+-- .spec-squad.json       <- squad state (if using squad)
+-- .blitz-active          <- present during blitz execution
```

### 调度自动化

操作系统级别的调度器（Windows Task Scheduler / cron / launchd）在 Claude Code 未启动时也能运行：

- **Heartbeat** — 确保所有工作区 session 保持存活（停止时自动复活）
- **Git sync** — 每 30 分钟拉取和推送所有仓库
- **Salience decay** — 每日内存重要性调整
- **evolve-tick** — 每 2 小时进行模式提取 + 改进提案

---

## 内存系统

### 26 个 MCP 工具

| 分类 | 工具 |
|---|---|
| **写入** | `memory_store`, `memory_record_decision`, `memory_record_resolved`, `memory_record_question`, `memory_record_knowledge` |
| **读取** | `memory_list`, `memory_get`, `memory_get_summary` |
| **删除** | `memory_delete` |
| **搜索** | `memory_search` (vector + text, salience-weighted, all tables) |
| **显著性** | `memory_reinforce` |
| **进化** | `memory_learn_skill`, `memory_list_skills`, `memory_improve_skill` |
| **TODO** | `memory_todo_add`, `memory_todo_list`, `memory_todo_update`, `memory_todo_search` |
| **审计追踪** | `memory_log_action`, `memory_audit_search`, `memory_audit_stats`, `memory_daily_report`, `memory_activity_log` |
| **管理** | `memory_compact`, `memory_status`, `memory_oracle_summary` |

内存不是被动的存储空间 — 它主动塑造你的 Agent 的工作方式。每条轨迹都被记录。每个工作区通过 git 共享知识。你的 Agent 一起成长。

---

## 进化系统

v1 构建完成后，你的 Agent 会自动持续进步。

### 循环

```
/absorb (input)
  +-- Scan folder -> extract knowledge, decisions, TODOs
  +-- Read GitHub repo -> learn patterns + skills
  +-- Fetch URL -> store insights
       |
evolve-tick (every 2 hours)
  +-- Extract patterns from completed work
  +-- Generate improvement proposals (git-synced markdown files)
  +-- Apply salience decay to stale knowledge
  +-- Sync knowledge across machines
       |
Review (you decide)
  +-- Review proposals in openspec/proposals/
  +-- Approve -> becomes TODO for next blitz
  +-- Reject -> archived with learning captured
```

Evolve 生成的是**提案**，而非直接更改。所有提案保存在 `openspec/proposals/` 供人工审查。学到的技能通过 git sync 在 session 和机器间持久保存。

---

## 系统要求

- **Python** 3.10+ 和 **Git** 2.x+
- **Claude Code** CLI ([安装指南](https://docs.anthropic.com/en/docs/claude-code/getting-started))
- **GitHub** 账号（用于你的私有 Hub 仓库）
- **Node.js** 18+（可选 — 仅在使用需要它的 MCP server 时才需要）

---

## 安装（详细）

### 1. 克隆并安装

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
```

这会全局注册 `clawd-lobster` CLI 命令。

### 2. 运行设置

选择其一：

```bash
clawd-lobster serve    # Web wizard at http://localhost:3333
clawd-lobster setup    # Terminal wizard
./install.ps1          # Windows classic installer
./install.sh           # macOS/Linux classic installer
```

### 3. 验证

```bash
clawd-lobster status
# Shows: Python version, Claude CLI, Git, workspaces, server status
```

### 4. 开始构建

```bash
clawd-lobster squad start                    # Describe your project -> spec -> build
clawd-lobster workspace create my-app --repo # Or create a workspace manually
```

---

## 常见问题

### "这不就是 Claude Code 加个壳吗？"

是的。这正是重点。

Claude Code 是目前最强大的编程 Agent — 背后有 Anthropic 数百万工程小时的支撑。其他框架从零开始重建引擎（50K-300K 行）。我们补上缺少的部分（约 3K 行），保留最好的引擎。

当 Anthropic 推出下一个突破时，我们立即受益。其他框架则必须重写适配层。

### "Spec Squad 跟直接让 Claude 写代码有什么不同？"

Spec Squad 在编写代码前加入了**对抗式审查**。Architect 编写完整规格，然后 Reviewer 严格挑剔 — 找出漏洞、模糊之处和薄弱的决策。在 Coder 动手之前，最多会进行 5 轮修改。这意味着代码是根据经过压力测试的蓝图来构建，而非根据随意的提示。

### "但其他 Agent 能 24/7 运行且持续学习"

我们的也是。调度器每 30 分钟同步知识。内存通过显著性衰减每日进化。学到的技能通过 git 传播到所有机器。心跳确保 session 保持存活：如果终端关闭，操作系统调度器会用 `claude --resume` 复活 — 完整的上下文恢复。

### "Claude Code 已经有内置技能和 MCP 了，为什么还需要这个？"

Claude Code 的内置技能是封闭的 — 你无法添加、修改或共享。MCP 提供协议，但没有生命周期管理。安装一个技能意味着手动编辑 3 个 JSON 文件。第二台机器？全部重来。

**MCP 是协议，我们是包管理器。** 我们添加的：`skill.json` 清单、一键启用/禁用、集中式凭证管理、健康检查、Web 仪表盘，以及通过 git 的跨机器注册表同步。

### "Anthropic 不会封锁这个吗？"

我们通过操作系统 cron 调度 `claude` CLI 命令 — 就像调度 `git pull` 一样。我们使用 `claude --resume`、`--allowedTools` 和 MCP server — 全是 Anthropic 在自家 CLI 中提供的标志。没有 API 密钥自动化、没有 OAuth token 抓取、没有逆向工程。

### "费用怎么算？"

使用 Pro 订阅（$20/月），没有按 token 计费。一个订阅、一个引擎。可预测的费用本身就是一个优势。

---

## 比较

| | Claude Code (原生) | 重量级框架 | **Clawd-Lobster** |
|---|---|---|---|
| Agent 引擎 | Anthropic | 自建（50K-300K LOC） | **Anthropic（原生）** |
| 多 Agent 开发 | 无 | 部分支持 | **有（Spec Squad：4 个 Agent）** |
| 对抗式审查 | 无 | 无 | **有（最多 5 轮）** |
| 持久内存 | 无 | 各异 | **4 层 + 显著性** |
| 多机支持 | 无 | 无 | **有（Hub + git sync）** |
| 永不停机 | 无 | 自建守护进程 | **操作系统心跳 + 自动复活** |
| 技能管理 | 无 | CLI/SDK | **Web UI + CLI + manifest** |
| 自我进化 | 无 | 各异 | **有（提案 + 学习技能）** |
| 新手引导 | 手动 | 复杂 | **Web 向导或终端，5 种语言** |
| Web 仪表盘 | 无 | 各异 | **有（localhost:3333）** |
| 代码量 | 0 | 50K-300K LOC | **约 3K LOC** |
| 费用模式 | 订阅制 | 按 token API | **订阅制（固定）** |
| Anthropic 升级 | 透明 | 中断 | **透明** |

---

## 路线图

**v1.0 已完成**
- [x] 统一 CLI 入口（`clawd-lobster serve/setup/squad/workspace/status`）
- [x] Web 仪表盘，含设置向导、工作区管理、Spec Squad UI
- [x] Spec Squad — 通过 Claude Agent SDK 的多 Agent 开发
- [x] 三种用户角色（引导 / 专家 / 技术）
- [x] 9 个技能、32 个 MCP 工具、`skill.json` 清单系统
- [x] 4 层内存 + 显著性引擎
- [x] 多机 Hub 模式 + git sync
- [x] 通过操作系统调度器的心跳自动复活
- [x] 进化循环 + git 同步提案
- [x] Docker 支持

**下一步**
- [ ] Supabase L4 — 一键云数据库（不需要 Oracle wallet）
- [ ] SearXNG — 私有自托管网络搜索
- [ ] Docker Sandbox — 隔离的代码执行环境，用于不受信任的操作
- [ ] Skill marketplace — 社区贡献的技能，一键安装
- [ ] 团队模式 — 多用户共享工作区，含角色访问控制
- [ ] Agent 间委派 — Agent 互相分派任务

---

## 项目结构

```
clawd-lobster/
+-- clawd_lobster/       CLI + web server + squad orchestrator + onboarding
+-- skills/              9 skill modules (each with skill.json manifest)
+-- scripts/             Heartbeat, sync, evolve-tick, skill-manager, etc.
+-- templates/           Config templates (no secrets)
+-- knowledge/           Shared knowledge base (git-synced)
+-- install.ps1/sh       Classic installers (Windows / macOS / Linux)
+-- pyproject.toml       Package definition (pip install -e .)
+-- Dockerfile           Docker support
+-- docker-compose.yml   Docker Compose config
```

---

## 贡献

欢迎贡献！最简单的参与方式：

1. **添加技能** — 在 `skills/` 中创建文件夹并附上 `skill.json` 清单
2. **改进模板** — 在 `templates/` 中提供更好的默认值
3. **平台支持** — 协助 Linux/macOS 测试
4. **报告问题** — 开一个 issue

---

## 许可证

MIT — 随你怎么用。

---

<p align="center">
<sub>与 Anthropic 无关。构建于 <a href="https://claude.ai/code">Claude Code</a> 之上。</sub>
</p>
