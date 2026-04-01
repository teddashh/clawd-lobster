🌐 [English](README.md) | [**繁體中文**](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

<p align="center">
<strong>終究要用最好的，何必繞遠路？</strong><br>
<em>終極 agent 體驗 — 最輕量、精選功能、極致效能。</em>
</p>

<p align="center">
<sub>網頁引導設定。多層記憶。多 agent 共享知識。自由進化。</sub>
</p>

---

### 這個專案只做一件事。

讓你從零開始，透過網頁介面，快速擁有一個裝備齊全的 Claude Code agent。

**第 1 步。** 網頁精靈帶你幾分鐘內裝好 Claude Code 並完成驗證。

**第 2 步。** 網頁精靈幫你設定多層記憶系統和必備工具 — 一步一步點，一個一個綠燈亮。

**第 3 步。** 技能市集讓你只裝需要的東西，不需要的完全不碰。

**第 4 步。** 你的 agent 自由進化。每段記憶都留著。每個動作都追蹤。每個洞察都共享。

---

### 幹嘛裝一堆用不到的東西？

其他框架從頭打造整個 AI agent — 30 萬行程式碼、自己寫 agent loop、自己刻工具系統、什麼都自己來。等 Anthropic 出了更強的模型，他們就得忙著改寫一堆 adapter。

**Clawd-Lobster 不跟 Claude Code 競爭，而是讓它更完整。**

我們從 Claude Code 出發 — 世界上最強的 coding agent — 然後只加上它缺的東西：持久記憶、多 agent 協作、精選技能。不多不少，剛剛好。

> **每段記憶都留著。** 每條軌跡都記錄。每個 workspace 都共享。
>
> 你的 agent 一起成長。知識不斷累積。你的成果永遠不會消失。

> *零贅肉。零重寫。純粹的 Claude Code，放大再放大。*

---

## 差異比較

| | 重量級框架 | 原生 Claude Code | **Clawd-Lobster** |
|---|---|---|---|
| **Agent 引擎** | 自己維護 | Anthropic | **Anthropic** |
| **程式碼量** | 30 萬行以上 | 不適用 | **約 2 千行** |
| **Opus 4.7 出了** | 改寫 adapter | 自動升級 | **自動升級** |
| **持久記憶** | 單層或沒有 | 沒有 | **4 層 + 重要度引擎** |
| **多機器** | 複雜或不可能 | 不行 | **內建（MDM 風格）** |
| **上手時間** | 半天 | 手動設定 | **5 分鐘** |
| **效能** | 自訂引擎的額外開銷 | 原生 | **原生** |

### 核心概念

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

**一個技能只要 3 筆設定。** 不用 SDK。不用 plugin API。不被框架綁死。

---

## 功能特色

### 4 層記憶系統

大部分 AI agent 在每次對話之間什麼都忘光。Clawd-Lobster 給 Claude Code 持久、可搜尋、有權重的記憶。

| 層級 | 內容 | 速度 | 範圍 |
|-------|------|-------|-------|
| **L1.5** | CC 自動記憶（原生） | 即時 | 當前專案 |
| **L2** | SQLite + 21 個 MCP 工具 | 約 1ms | 每個 workspace |
| **L3** | Markdown 知識庫 | 約 10ms | 透過 git 共享 |
| **L4** | 雲端資料庫（選用） | 約 100ms | 跨 workspace |

**重要度引擎（Salience engine）** — 重要的記憶自動浮上來，過時的慢慢沉下去：
- 每次存取：重要度 +5%
- 手動強化：+20%（上限 2.0 倍）
- 30 天沒碰：每天 -5%（底線 0.01，永不刪除）

**CJK 感知的 token 估算** — 多語言工作量下也能精準計算壓縮時機。

### 多 Agent 共享知識

這不只是一個 agent，而是一整個艦隊 — 而且它們共用同一個大腦。

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

- **L2** 留在本機（快，每個 workspace 獨立）— 每個 agent 有自己的快取
- **L3** 透過 git 同步 — 每個 agent 讀寫同一個知識庫
- **L4** 統一一切 — 跨 workspace 搜尋、稽核軌跡、完整歷史
- **新 agent 加入？** `git clone + install.ps1` — 瞬間繼承所有累積的知識

### 會進化的 Agent

你的 agent 不只是執行任務 — 它們會學習。內建自我進化功能，靠 3 個專用 MCP 工具：

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

- **學到的技能會保留** — 同時存在資料庫和 git 同步的技能檔案中
- **效能追蹤** — 每次使用 +2%，每次改進 +10%，實戰驗證的技能分數會超過 2.0 倍
- **跨 agent 共享** — Agent A 學到的技能，Agent B 透過 git sync 也能用
- **自然淘汰** — 超過 90 天沒用的技能會被標記為可能過時
- **知識持續累積** — 一個 workspace 裡的決策會影響另一個 workspace 的工作，解決過的問題不會再解決第二次

### 智慧遷移

已經在用其他設定了？Claude Code 會讀取你現有的檔案，聰明地匯入：

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

不需要寫解析腳本。Claude Code **本身就是**解析器 — 它能讀任何格式、理解語意、然後存下重要的東西。

### 簡單的 Workspace 管理

一個指令就能建立 workspace。排程器會自動同步你 workspace 根目錄下的所有 git repo：

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

### 排程自動化

作業系統層級的排程器（Windows Task Scheduler / cron / launchd）— 就算 Claude Code 沒在跑也會執行：

- **Git 同步** — 每 30 分鐘自動 pull 和 push 所有 repo
- **重要度衰減** — 每天自動調整記憶的重要程度

---

## 快速開始

### 選項 A：網頁設定精靈

用瀏覽器打開 `webapp/index.html`，跟著 6 步驟引導精靈走就好。

### 選項 B：命令列

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

### 安裝程式做了什麼

| 步驟 | 動作 | 時間 |
|------|--------|------|
| 1 | 檢查前置需求（Node、Python、Git） | 5 秒 |
| 2 | 驗證 Claude Code + GitHub（OAuth） | 30 秒 |
| 3 | 安裝 MCP Memory Server（21 個工具） | 10 秒 |
| 4 | 設定 Claude Code（.mcp.json、settings.json、CLAUDE.md） | 5 秒 |
| 5 | 註冊排程任務（OS 原生） | 5 秒 |
| 6 | 完成 | --- |

| 平台 | 排程器 | 方式 |
|----------|-----------|--------|
| Windows | Task Scheduler | `install.ps1` 自動註冊 |
| macOS | launchd | `install.sh` 建立 LaunchAgent |
| Linux | cron | `install.sh` 加入 crontab |
| Docker | 容器重啟 | `docker compose` 處理生命週期 |

**總共只需要：2 次 OAuth 點擊。** 不用貼 API key（除非你要用 Oracle L4）。

---

## 新增技能

一個技能 = 3 筆設定。就這樣。

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

不用學 SDK。不用 plugin 介面。不用 build。只有設定。

---

## 專案結構

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

## 設計哲學

### 1. 最好的 agent 已經存在了，直接用就好。

Claude Code 背後是世界上最大的 AI 安全實驗室。上百萬工程小時打造了它的 agent loop、串流、權限和工具系統。從頭重寫不是雄心壯志 — 是浪費。**站在巨人的肩膀上吧。**

### 2. 少即是多，而且多很多。

框架的每一行程式碼都是你要維護的。Clawd-Lobster 只有大約 2 千行，因為 Claude Code 原生的擴充點（MCP、hooks、CLAUDE.md）本身就是最好的 plugin 系統。**三筆設定 = 一個技能。零 SDK。**

### 3. 會忘記的 agent 就是會失敗的 agent。

大部分 AI agent 每次開始都從零開始。它們重複犯錯、重新學習 context、浪費你的時間。Clawd-Lobster 的 4 層記憶加上重要度追蹤，確保**重要的東西浮上來、雜訊慢慢消失、關鍵資訊永遠不會搞丟。**

### 4. 你的 agent 應該跟你走到哪都能用。

一台電腦？沒問題。三台機器？它們應該共用同一個大腦。GitHub 當控制平面，git sync 當協定。**2 分鐘加入一台新機器。零基礎設施。**

### 5. 永遠站在最新的浪頭上。

當 Anthropic 推出 Opus 4.7、1M context、新工具 — 你立刻就能用。不用改寫 adapter。不用釘死版本。不用等社群補丁。**用 Claude Code 最好的時間是昨天，第二好的時間是現在。**

---

## 完整比較

| | Claude Code（原生） | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| Agent 引擎 | Anthropic | 自訂（Pi Agent） | 自訂（Python） | **Anthropic（原生）** |
| 持久記憶 | 沒有 | 混合搜尋 | FTS5 + LLM | **4 層 + 重要度引擎** |
| 多 agent 共享記憶 | 沒有 | 沒有 | 沒有 | **有** |
| Agent 進化 | 沒有 | 沒有 | 自我改進技能 | **有（記憶 + 技能）** |
| 多機器 | 沒有 | 沒有 | 沒有 | **有（MDM 風格）** |
| 上手時間 | 手動設定 | 複雜 | 中等 | **網頁精靈，5 分鐘** |
| 自動升級 | 有 | 沒有 | 沒有 | **有** |
| 程式碼量 | 不適用 | 約 30 萬行 | 約 5 萬行 | **約 2 千行** |
| 稽核軌跡 | 沒有 | 安全稽核 | 沒有 | **完整（每個動作）** |
| 技能安裝 | — | Plugin SDK | 改 3 個檔案 | **3 筆設定** |

---

## 路線圖

**技能**
- [ ] Codex Bridge — 把重度任務丟給 OpenAI Codex 在背景跑
- [ ] SearXNG — 私有自架網頁搜尋，資料不會離開你的網路
- [ ] Docker Sandbox — 隔離的程式碼執行環境，給不信任的操作用
- [ ] Browser Automation — 用 Playwright 驅動的網頁互動

**平台**
- [ ] Linux 安裝程式（bash）+ macOS 安裝程式（zsh/launchd）
- [ ] Supabase L4 — 一鍵雲端資料庫（不需要 Oracle wallet）
- [ ] Dashboard — 即時查看所有 agent、記憶和同步狀態

**進化**
- [ ] 技能市集 — 社群貢獻的技能，一鍵安裝
- [ ] 自動產生技能 — agent 從成功模式中學習，建立可重複使用的技能
- [ ] 團隊模式 — 多人共享 workspace，角色式權限控制
- [ ] Agent 間委派 — agent 互相指派任務

---

## 貢獻

歡迎貢獻！最簡單的參與方式：

1. **新增技能** — 在 `skills/` 建一個資料夾，放 `SKILL.md` 或 MCP server
2. **改善範本** — 讓 `templates/` 裡的預設值更好用
3. **平台支援** — 幫忙做 Linux/macOS 安裝程式

---

## 授權

MIT — 愛怎麼用就怎麼用。

---

<p align="center">
<sub>與 Anthropic 無關。建立在 <a href="https://claude.ai/code">Claude Code</a> 之上。</sub>
</p>
