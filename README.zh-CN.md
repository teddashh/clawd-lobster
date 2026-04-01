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

### 这个项目只做一件事。

帮你从零开始，快速拥有一个装备齐全的 Claude Code 智能体 — 通过网页界面完成。

**第 1 步。** 网页向导引导你安装 Claude Code 并完成身份验证，只需几分钟。

**第 2 步。** 网页向导帮你搭建多层记忆系统和核心工具 — 一步步点击，逐项亮绿灯。

**第 3 步。** 技能商城，按需安装。不需要的一概不装。

**第 4 步。** 你的智能体自由进化。每段记忆都会保留。每个操作都可追溯。每个洞察都能共享。

---

### 为什么要装一堆用不上的东西？

其他框架从头重造整个 AI 智能体 — 30 万行代码、自研智能体循环、自研工具系统、什么都自己造。等 Anthropic 发布更强的模型，他们又得手忙脚乱地重写适配层。

**Clawd-Lobster 不是要取代 Claude Code，而是让它更完整。**

我们以 Claude Code — 世界上最先进的编程智能体 — 为基础，精准补足它所缺少的：持久化记忆、多智能体协同和精选技能。不多也不少。

> **每段记忆都会保留。** 每条轨迹都有记录。每个工作区都能共享。
>
> 你的智能体共同成长。你的知识不断积累。你的成果永不丢失。

> *零冗余。零重写。纯粹的 Claude Code，增强版。*

---

## 核心差异

| | 重量级框架 | 原生 Claude Code | **Clawd-Lobster** |
|---|---|---|---|
| **智能体引擎** | 自研（自行维护） | Anthropic | **Anthropic** |
| **代码量** | 30 万行以上 | 不适用 | **约 2000 行** |
| **Opus 4.7 发布时** | 重写适配层 | 自动升级 | **自动升级** |
| **持久化记忆** | 单层或无 | 无 | **4 层 + 重要性权重** |
| **多设备协同** | 复杂或不可能 | 不支持 | **内置（MDM 风格）** |
| **上手时间** | 半天 | 手动配置 | **5 分钟** |
| **性能** | 自研引擎带来额外开销 | 原生 | **原生** |

### 核心理念

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

**一个技能只需 3 条配置。** 无需 SDK。无需插件接口。无框架绑定。

---

## 功能特性

### 4 层记忆系统

大多数 AI 智能体在会话之间会遗忘一切。Clawd-Lobster 为 Claude Code 提供持久化、可搜索、带权重的记忆。

| 层级 | 内容 | 速度 | 范围 |
|-------|------|-------|-------|
| **L1.5** | CC 自动记忆（原生） | 即时 | 当前项目 |
| **L2** | SQLite + 21 个 MCP 工具 | 约 1ms | 每个工作区 |
| **L3** | Markdown 知识库 | 约 10ms | 通过 git 共享 |
| **L4** | 云数据库（可选） | 约 100ms | 跨工作区 |

**重要性引擎** — 重要的记忆自动上浮，过时的自动下沉：
- 每次访问：重要性 +5%
- 手动强化：+20%（上限 2.0 倍）
- 30 天未访问：每天 -5% 衰减（下限 0.01，永不删除）

**CJK 感知的 token 估算** — 为多语言工作负载提供精准的压缩时机判断。

### 多智能体共享知识

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

### 自我进化的智能体

你的智能体不只是执行 — 它们会学习。内置自我进化功能，提供 3 个专用 MCP 工具：

```
Task completed (complex, multi-step)
    │
    ▼ memory_learn_skill()
    │ Extracts the reusable pattern
    │ Saves to L2 (SQLite) + skills/learned/ (file)
    │
    ▼ Next similar task arrives
    │ memory_list_skills() finds the pattern
    │ Agent follows the proven approach
    │
    ▼ Better approach discovered?
      memory_improve_skill() updates it
      Effectiveness score increases (+10%)
```

- **学到的技能持久保存** — 同时存储在数据库和 git 同步的技能文件中
- **有效性追踪** — 每次使用 +2%，每次改进 +10%，经过验证的技能评分 > 2.0 倍
- **跨智能体共享** — Agent A 学到的技能通过 git 同步供 Agent B 使用
- **自然淘汰** — 超过 90 天未使用的技能会被标记为可能过时
- **知识复利** — 一个工作区的决策能指导另一个工作区的工作，解决过的问题不需要再解决第二次

### 智能迁移

已经在用其他方案？Claude Code 会读取你现有的文件并智能导入：

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

无需解析脚本。Claude Code **本身就是**解析器 — 它能读取任何格式、理解语义，并保存有价值的内容。

### 简洁的工作区管理

一条命令创建工作区。调度器自动同步工作区根目录下的所有 git 仓库：

```powershell
.\scripts\new-workspace.ps1 -name "my-api"
# Creates folder, memory.db, CLAUDE.md, GitHub repo — done.
```

```
~/Documents/Workspace/
├── my-api/          ← registered, synced every 30 min
├── data-pipeline/   ← registered, synced every 30 min
└── random-notes/    ← not a git repo, ignored by sync
```

### 定时自动化

系统级调度器（Windows Task Scheduler / cron / launchd）— 即使 Claude Code 未运行也照常执行：

- **Git 同步** — 每 30 分钟自动拉取和推送所有仓库
- **重要性衰减** — 每日记忆重要性调整

---

## 快速开始

### 方案 A：网页安装向导

在浏览器中打开 `webapp/index.html`，按照 6 步引导完成配置。

### 方案 B：命令行

**Windows (PowerShell)**
```powershell
git clone https://github.com/YOUR_USERNAME/clawd-lobster
cd clawd-lobster
.\install.ps1
```

**macOS / Linux (Bash)**
```bash
git clone https://github.com/YOUR_USERNAME/clawd-lobster
cd clawd-lobster
chmod +x install.sh && ./install.sh
```

**Docker**
```bash
git clone https://github.com/YOUR_USERNAME/clawd-lobster
cd clawd-lobster
docker compose up -d
docker compose exec clawd bash
# Then inside container: claude auth login
```

### 安装器做了什么

| 步骤 | 操作 | 耗时 |
|------|--------|------|
| 1 | 检查前置依赖（Node、Python、Git） | 5 秒 |
| 2 | 认证 Claude Code + GitHub（OAuth） | 30 秒 |
| 3 | 安装 MCP Memory Server（21 个工具） | 10 秒 |
| 4 | 配置 Claude Code（.mcp.json、settings.json、CLAUDE.md） | 5 秒 |
| 5 | 注册定时任务（系统原生） | 5 秒 |
| 6 | 完成 | --- |

| 平台 | 调度器 | 方式 |
|----------|-----------|--------|
| Windows | Task Scheduler | `install.ps1` 自动注册 |
| macOS | launchd | `install.sh` 创建 LaunchAgent |
| Linux | cron | `install.sh` 添加 crontab 条目 |
| Docker | 容器重启 | `docker compose` 管理生命周期 |

**总共只需：2 次 OAuth 点击。** 无需粘贴 API 密钥（除非你需要 Oracle L4）。

---

## 添加技能

一个技能 = 3 条配置。就这么简单。

```jsonc
// 1. .mcp.json — register the MCP server
{ "mcpServers": { "my-skill": { "command": "python", "args": ["-m", "my_skill"] } } }

// 2. settings.json — auto-allow read tools
{ "permissions": { "allow": ["mcp__my-skill__my_tool"] } }
```

```markdown
<!-- 3. CLAUDE.md — teach the agent when to use it -->
## My Skill
Use my_tool when the user asks about X. Prefer it over Y for Z tasks.
```

无需学习 SDK。无需插件接口。无需构建步骤。只是配置而已。

---

## 项目结构

```
clawd-lobster/
├── skills/
│   ├── memory-server/        21-tool MCP memory with salience + evolution
│   │   └── mcp_memory/       Python package (pip install -e .)
│   ├── evolve/               Self-evolution skill specification
│   ├── learned/              Auto-generated skills from experience
│   └── migrate/              Import from existing setups
│
├── scripts/
│   ├── sync-all.ps1          Windows: auto git sync + decay
│   ├── sync-all.sh           Linux/macOS: auto git sync + decay
│   ├── new-workspace.ps1     Create workspace + GitHub repo
│   └── init_db.py            Initialize memory database
│
├── templates/                Config templates (no secrets)
│   ├── global-CLAUDE.md
│   ├── workspace-CLAUDE.md
│   ├── mcp.json.template
│   └── settings.json.template
│
├── webapp/                   Web-based setup wizard
│   └── index.html            6-step dark-theme onboarding
│
├── knowledge/                Shared knowledge base (git-synced)
├── soul/                     Agent personality (optional)
├── workspaces.json           Workspace registry
├── install.ps1               Windows installer
├── install.sh                Linux/macOS installer
├── Dockerfile                Docker build
├── docker-compose.yml        Docker Compose config
├── LICENSE                   MIT
└── README.md
```

---

## 设计哲学

### 1. 最好的智能体已经存在，直接用就好。

Claude Code 背后是世界上最大的 AI 安全实验室。数百万工程小时投入到它的智能体循环、流式传输、权限和工具系统中。从零开始重造这些不是雄心壮志 — 而是浪费。**站在巨人的肩膀上。**

### 2. 少即是多，而且多得多。

框架的每一行代码都是你需要维护的。Clawd-Lobster 只有约 2000 行代码，因为 Claude Code 的原生扩展点（MCP、hooks、CLAUDE.md）本身就是最好的插件系统。**三条配置 = 一个技能。零 SDK。**

### 3. 会遗忘的智能体注定失败。

大多数 AI 智能体每次会话都从零开始。它们重复犯错、重新学习上下文、浪费你的时间。Clawd-Lobster 的 4 层记忆加重要性追踪确保**重要的内容上浮、噪音逐渐消退、关键信息永不丢失。**

### 4. 你的智能体应该跟你走到哪里。

一台电脑？没问题。三台设备？它们应该共享同一个大脑。GitHub 作为控制平面，git 同步作为协议。**2 分钟加入一台新设备。零基础设施。**

### 5. 永远踩在最新的浪尖上。

当 Anthropic 发布 Opus 4.7、1M context、新工具时 — 你即刻获得。无需重写适配层。无需锁定版本。无需等待社区补丁。**用 Claude Code 最好的时间是昨天，其次是现在。**

---

## 横向对比

| | Claude Code（原生） | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| 智能体引擎 | Anthropic | 自研（Pi Agent） | 自研（Python） | **Anthropic（原生）** |
| 持久化记忆 | 无 | 混合搜索 | FTS5 + LLM | **4 层 + 重要性权重** |
| 多智能体共享记忆 | 否 | 否 | 否 | **是** |
| 智能体进化 | 否 | 否 | 自改进技能 | **是（记忆 + 技能）** |
| 多设备协同 | 否 | 否 | 否 | **是（MDM 风格）** |
| 上手门槛 | 手动配置 | 复杂 | 中等 | **网页向导，5 分钟** |
| 自动升级 | 是 | 否 | 否 | **是** |
| 代码量 | 不适用 | 约 30 万行 | 约 5 万行 | **约 2000 行** |
| 审计追踪 | 否 | 安全审计 | 否 | **完整（每个操作）** |
| 技能安装 | — | 插件 SDK | 修改 3 个文件 | **3 条配置** |

---

## 路线图

**技能**
- [ ] Codex Bridge — 将重型任务委托给 OpenAI Codex 在后台执行
- [ ] SearXNG — 私有自托管网页搜索，数据不出内网
- [ ] Docker Sandbox — 隔离的代码执行环境，用于不受信任的操作
- [ ] Browser Automation — 基于 Playwright 的网页交互

**平台**
- [ ] Linux 安装器（bash）+ macOS 安装器（zsh/launchd）
- [ ] Supabase L4 — 一键部署云数据库（无需 Oracle wallet）
- [ ] Dashboard — 实时查看所有智能体、记忆和同步状态

**进化**
- [ ] 技能商城 — 社区贡献的技能，一键安装
- [ ] 自动技能生成 — 智能体从成功模式中学习，创建可复用技能
- [ ] 团队模式 — 多用户共享工作区，基于角色的访问控制
- [ ] 智能体间委托 — 智能体之间互相分配任务

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
