[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/RAM-25MB-orange)

<p align="center">
<strong>你终究要用 Claude Code 的 — 为什么不一开始就选最好的体验？</strong><br>
<strong>反正你迟早要用 Claude Code — 何不从最好的体验开始？</strong>
</p>

---

## 问题在哪

你看过那些 AI agent 框架。可能也试过几个。以下是实际会发生的事：

**问题一：Claude Code 很强，但你得一直盯着它。**
每次 session 都从零开始。它忘了昨天学到什么。你复制粘贴上下文，重新解释架构，重新描述规范。你就是内存。你就是管理者。你就是瓶颈。

**问题二：AI Agent 框架 demo 很炫，实际体验很痛。**
三十万行代码。自定义 adapter。配置文件比你的项目还长。底层模型一更新就挂。你花在维护框架的时间比开发产品还多。

**问题三：灰色地带。**
自建的 agent 循环绕过安全机制。API 按 token 计费毫无上限。东拼西凑的 Frankenstein 技术栈，你搞不清楚到底是你在用工具，还是工具在用你。

## 答案

Clawd-Lobster 不是要取代 Claude Code。它让 Claude Code 学会**记忆、规划、审查、构建、进化** — 而且只用 Anthropic 官方工具。

- **100% Claude Code CLI + Agent SDK。** 没有包装层，没有自定义 agent 循环，没有灰色地带。跑在你现有的 Claude 订阅上。不用额外 API 费用。
- **约 2,000 行代码。** 不是 300,000 行。Claude Code 更新时，新功能直接到手。不用改写，不会挂掉。
- **5 分钟上手。** 开浏览器。点两下。搞定。不用 API key，不用 Docker，不用 YAML 博士学位。

```
  You describe what you want
       |
       v
  Claude asks smart questions (Discovery)
       |
       v
  +-------------------------------------+
  |         SPEC SQUAD                   |
  |                                      |
  |  [A] Architect    writes the spec    |
  |  [R] Reviewer     challenges it      |
  |  [C] Coder        builds it          |
  |  [T] Tester       verifies it        |
  |                                      |
  |  Each is a separate Claude session.  |
  |  The Reviewer has never seen the     |
  |  Architect's prompt.                 |
  |  That's why it catches real bugs.    |
  +-------------------------------------+
       |
       v
  Reviewed, tested, working code.
```

---

## 快速开始

### 所有人适用（Web UI）

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
```

浏览器打开。安装向导带你走完一切。

### 给终端控

```bash
clawd-lobster setup        # 终端引导安装
clawd-lobster squad start  # 在终端里跑 Spec Squad
```

### 传统安装（高级用户）

```powershell
# Windows
.\install.ps1

# macOS / Linux
chmod +x install.sh && ./install.sh
```

---

## 你会得到什么

### 1. Spec Squad — 你的 AI 开发团队

你描述你要什么。四个 Claude session 搞定剩下的。

**Architect** 写出一份包含可测试需求的完整规格书。**Reviewer** — 一个完全独立、从未看过 Architect 指令的 Claude session — 把它拆开来挑毛病。他们反复来回直到 Reviewer 批准。然后 **Coder** 严格按规格书来盖。**Tester** 验证每一条需求。

这不是花架子。测试中，Reviewer 在第一份规格书就找到 11 个真实 bug — 那些自我验证清单永远抓不到的问题。返回类型冲突、API 不一致、不可能的 Gherkin 场景、包不兼容。

**为什么有效：** 每个 agent 跑在隔离的上下文里。Reviewer 不会受 Architect 的推理影响。Tester 不知道 Coder 走了什么捷径。独立的脑子找出独立的问题。

两种界面，同一个引擎：
- **Web：** 在浏览器跟 Claude 聊，然后在实时 dashboard 上看 agent 干活
- **终端：** Claude 在终端问你问题，agent 跑起来时实时显示进度

### 2. 会记东西的脑子

四层内存，从即时到全局：

| Layer | Speed | What |
|-------|-------|------|
| L1.5 | Instant | Claude Code's native auto-memory |
| L2 | ~1ms | SQLite + MCP — per-workspace, salience-weighted |
| L3 | ~10ms | Markdown + Git — synced across machines |
| L4 | ~100ms | Cloud DB (optional) — cross-workspace search |

重要的想法浮上来。噪音沉下去。有用的技能被强化。过时的知识自然衰减。你完全不用管 — 全部自动。

### 3. 永远在线

合上笔记本。Clawd-Lobster 继续干活。

heartbeat 用的是你操作系统的调度器（Task Scheduler / cron / launchd）— 不是自定义 daemon，不是 polling 循环，不是烧 token 的后台进程。Session 挂了就带着完整上下文自动复活。不用盯。

### 4. 所有机器，一个脑子

GitHub 是控制面。Git 是协议。

机器 A 学到一个模式。它同步到你的私有 Hub。机器 B 立刻继承。新机器？`install.ps1`，「Join Hub」，粘贴网址，2 分钟，完全上线。

### 5. 自我进化

完成复杂工作后，系统会提取可重用的模式，存成学到的技能。下次遇到类似任务，它记得上次怎么解决的。

技能有效能分数。验证过的模式被强化。过时的技能自然衰减。系统越用越聪明 — 不是魔法，是因为它把有效的方法写下来了。

---

## Dashboard

`clawd-lobster serve` 在 `localhost:3333` 打开常驻 web dashboard。

**新手引导** — 首次启动的向导会检查前置需求、带你设置、创建第一个 workspace。

**Workspaces** — 所有项目一目了然。状态、规格书进度、内存大小、最后活动时间。

**Spec Squad** — 跟 Claude 聊天厘清需求。在实时 dashboard 上看四个 agent 工作，有阶段时间轴和对话历程。

---

## Skills

9 个精选 skill。每个只做好一件事。

| Skill | What It Does |
|-------|-------------|
| **memory-server** | 4-layer persistent memory via MCP (SQLite + Git + Cloud) |
| **spec** | Guided workspace creation + spec-driven development + Spec Squad |
| **evolve** | Extract reusable patterns from completed work (auto, every 2h) |
| **absorb** | Learn from existing repos, URLs, or folders |
| **heartbeat** | Keep sessions alive via OS scheduler |
| **migrate** | Import from other AI setups (one-time) |
| **codex-bridge** | Delegate to OpenAI Codex for review, bulk work, second opinions |
| **connect-odoo** | Bidirectional Odoo ERP integration via XML-RPC |
| **notebooklm-bridge** | Auto-sync to Google NotebookLM + watermark removal |

每个 skill 都有触发描述（Claude 知道何时启动）、Gotchas 区块（常见错误要避免）、和动态 `!command` 注入（加载时的即时上下文）。

---

## 架构

```
Skills (the what)     ->  9 skills with manifests, instructions, gotchas
Tools (the how)       ->  32 MCP tools + Claude Code native tools
Hooks (the when)      ->  OS scheduler, git hooks, PostToolUse, Stop hooks
```

**站在巨人肩膀上。** Clawd-Lobster 不重建 Claude Code。它用 Claude Code 原生的扩展点（MCP servers、CLAUDE.md、hooks、settings.json），完全照 Anthropic 的设计走。Claude Code 出新功能，你直接受益。模型进步，你的 agent 跟着进步。零 adapter 代码。

```
Disk: 672 KB    (code + configs)
RAM:  ~25 MB    (MCP server only)
CPU:  0% idle   (OS scheduler, not polling)
LOC:  ~2,000    (not 300,000)
```

完整文件树和运行时细节，请见 [ARCHITECTURE.md](ARCHITECTURE.md)。

---

## CLI 参考

| Command | What It Does |
|---------|-------------|
| `clawd-lobster serve` | Start web dashboard (localhost:3333) |
| `clawd-lobster setup` | Terminal onboarding wizard |
| `clawd-lobster workspace create <name>` | Create a new workspace |
| `clawd-lobster squad start` | Run Spec Squad in terminal |
| `clawd-lobster status` | Show system health |

---

## 多机器设置

```
  clawd-lobster (this repo -- the generator)
       |
       |  install once
       v
  clawd-yourname (your private Hub on GitHub)
       |
       +-- Machine A -- skills + memory + heartbeat
       +-- Machine B -- skills + memory + heartbeat
       +-- Machine C -- skills + memory + heartbeat
            |
            All connected. All sharing knowledge.
```

第一台机器创建 Hub。之后每台 2 分钟加入。

---

## 环境需求

- Python 3.10+
- Claude Code CLI ([install](https://claude.ai/code))
- Git 2.x+
- Node.js 18+ (optional, for Codex Bridge)
- GitHub account (for Hub sync)

---

## 比较

|  | Heavyweight Frameworks | Raw Claude Code | Clawd-Lobster |
|--|----------------------|----------------|---------------|
| Codebase | 300K+ lines | 0 (built-in) | ~2,000 lines |
| Setup | Hours/days | 0 | 5 minutes |
| Memory | Session-only | Session-only | 4-layer persistent |
| Multi-machine | Usually none | None | Git sync + Hub |
| Model updates | Breaks adapters | Automatic | Automatic |
| Token cost | API per-token | Subscription | Subscription |
| Multi-agent review | Some | None | Spec Squad (adversarial) |
| Self-evolution | None | None | Learned skills + salience |

---

## 设计哲学

**1. 放大，不是重建。**
Claude Code 是世上最强的 coding agent。我们给它装上神经系统。我们不重建大脑。

**2. 巨人长高，你也长高。**
每次 Claude Code 更新都让你的 Clawd-Lobster 更强。零迁移，零改写。

**3. 计划就是产品。**
Spec Squad 不是先写代码。它先写规格书，让对手来挑战，然后按规格书构建。计划就是契约。

---

## 贡献

欢迎 PR。贡献前请先读 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 许可

MIT — 详见 [LICENSE](LICENSE)。
