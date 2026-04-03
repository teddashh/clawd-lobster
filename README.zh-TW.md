🌐 [English](README.md) | [**繁體中文**](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

<p align="center">
<strong>你終究要用 Claude Code 的，何必在那邊一直試其他 Agent？</strong><br>
<em>終極 agent 體驗 — 最輕量、精選功能、極致效能。</em>
</p>

<p align="center">
<sub>網頁引導設定。多層記憶。多 agent 共享知識。自由進化。</sub>
</p>

---

## Clawd-Lobster 是什麼？

Claude Code 是大腦。Clawd-Lobster 是神經系統。

Claude Code 是目前最強的 coding agent，但它每次 session 結束就全忘了、只能在一台機器上跑、也沒有技能管理。Clawd-Lobster 精準補上這些缺口：持久記憶、多機器協作、精選技能、自我進化。不多不少，剛剛好。

**Clawd-Lobster 是一個產生器。** 你只要跑一次，它會幫你建立一個專屬的 **Hub** — 一個私人 GitHub repo，成為你的指揮中心。Hub 管理你所有的機器、workspace、記憶和技能。

```
  clawd-lobster (這個 repo — 產生器)
       │
       │  跑一次 install.ps1
       │
       ▼
  clawd-yourname (你的私人 Hub — 專為你產生)
       │
       │  這才是你每天實際在用的東西
       │
       ├── Machine A ── Claude Code + skills + memory
       ├── Machine B ── Claude Code + skills + memory
       └── Machine C ── Claude Code + skills + memory
            │
            全部連線。全部共享知識。
            全部透過 heartbeat 保持存活。
```

GitHub 是控制平面。Git 是通訊協定。所有狀態 — 技能、知識、workspace 註冊、heartbeat 狀態 — 都活在 git 裡，自動同步。

**運行佔用：25 MB RAM，672 KB 磁碟空間。** 一個 Python process（MCP Memory Server）加上 SQLite。其他東西不是跑完就結束（透過 OS 排程器），就是在瀏覽器裡。零輪詢、零 daemon、零贅肉。

```
Disk: 672 KB (程式碼 + 設定，不含 .git 和圖片)
RAM:  ~25 MB (MCP server，唯一常駐 process)
CPU:  0% 閒置 (無輪詢、無 daemon — OS 排程器負責喚醒)
```

---

## 快速開始

### 第一台機器（建立你的 Hub）

**Windows**
```powershell
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
.\install.ps1
# 回答 4 個問題 → 你的私人 Hub 建好了 → 一切就緒
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

### 安裝流程怎麼運作

安裝程式問你 4 個問題，就這樣。其他一切都是自動的。

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
             ▼  接著 9 個自動化步驟
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

### 9 個步驟各做了什麼

| 步驟 | 動作 | 時間 |
|------|--------|------|
| 1 | 檢查前置需求（Node、Python、Git） | 5 秒 |
| 2 | 驗證 Claude Code + GitHub（2 次 OAuth 點擊） | 30 秒 |
| 3 | **建立你的 Hub**（私人 repo）或 clone 已有的 | 10 秒 |
| 4 | 寫入設定 | 5 秒 |
| 5 | 安裝 MCP Memory Server（21 個工具） | 10 秒 |
| 6 | 設定 Claude Code（CLAUDE.md + .mcp.json） | 5 秒 |
| 7 | 部署 workspace（clone repo、初始化 memory.db） | 視情況 |
| 8 | 註冊排程器 + heartbeat | 5 秒 |
| 9 | 吸收既有系統（如果有選） | 視情況 |

| 平台 | 同步 | Heartbeat |
|----------|------|-----------|
| Windows | Task Scheduler (30 分鐘) | Task Scheduler (30 分鐘) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | Container lifecycle | Container lifecycle |

**總共只需要：2 次 OAuth 點擊。** 不用 API key，除非你要用 Oracle L4。

### 之後再加機器

只要你的 Hub 已經在 GitHub 上了，加機器更簡單：

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

## Chapter 1：記憶 — 你的 Agent 會記住

為什麼這很重要：大多數 AI agent 每次 session 都從零開始。它們重複犯錯、重新學習 context、浪費你的時間。

### 4 層記憶系統

| 層級 | 內容 | 速度 | 範圍 |
|-------|------|-------|-------|
| **L1.5** | CC 自動記憶（原生） | 即時 | 當前專案 |
| **L2** | SQLite + 24 個 MCP 工具 | ~1ms | 每個 workspace |
| **L3** | Markdown 知識庫 | ~10ms | 透過 git 共享 |
| **L4** | 雲端資料庫（選用） | ~100ms | 跨 workspace |

### 重要度引擎（Salience Engine）

重要的記憶自動浮上來，過時的慢慢沉下去：
- 每次存取：重要度 +5%
- 手動強化：+20%（上限 2.0 倍）
- 30 天沒碰：每天 -5%（底線 0.01，永不刪除）

**CJK 感知的 token 估算** — 多語言工作量下也能精準計算壓縮時機。

### 實際運作方式

記憶不只是被動的儲存 — 它會主動影響你的 agent 行為。

```
你做了一個決定
  → memory_record_decision("chose SQLite over Postgres", "local-first, no server needed")

下一次 session 開始
  → 開機流程載入重要的決定 + 知識
  → Claude 記得那個決定和原因

30 天之後
  → 重要的決定仍然高重要度（經常被存取 → 加分）
  → 瑣碎的 context 已自然衰減（但永遠不會被刪除）
```

每條軌跡都記錄。每個 workspace 都共享。你的 agent 一起成長。知識持續累積。你的成果永遠不會消失。

---

## Chapter 2：Workspace — 你的 Agent 的工作場所

為什麼這很重要：如果沒有結構化的工作空間，agent 會搞混 context、弄亂專案，也無法跨機器共享知識。

Workspace 是一個有記憶、技能和 spec 支援的專案目錄。每個 workspace 都是一個 git repo（通常是 GitHub 上的私人 repo）。

### 建立 Workspace

兩種方式：

1. **`/spec new`** — 引導式建立，附完整 spec（推薦）。詳見 [Chapter 4](#chapter-4spec--你的-agent-怎麼做計畫)。
2. **`workspace-create.py`** — 快速建立，不附 spec：

```powershell
.\scripts\new-workspace.ps1 -name "my-api"
# 建立資料夾、memory.db、CLAUDE.md、GitHub repo — 搞定。
```

### Workspace 結構

```
my-project/
├── CLAUDE.md              ← 專案專屬指令
├── .claude-memory/
│   └── memory.db          ← L2 記憶 (SQLite)
├── knowledge/             ← L3 知識 (git 同步)
├── skills/learned/        ← 自動產生的技能
├── openspec/              ← spec 產物 (如果使用 /spec)
│   ├── project.md
│   ├── changes/
│   └── specs/
└── .blitz-active          ← blitz 執行期間會出現
```

### 啟用與同步 Workspace

```
~/Documents/Workspace/
├── my-api/          ← 已註冊，每 30 分鐘同步
├── data-pipeline/   ← 已註冊，每 30 分鐘同步
└── random-notes/    ← 不是 git repo，同步會忽略
```

- 每個啟用的 workspace 每 30 分鐘透過 git 同步
- 在 Web UI 的 Workspace 分頁切換 workspace 開關
- 停用的 workspace 停止同步但資料保留
- 排程器自動同步你 workspace 根目錄下的所有 git repo

### 多機器共享

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

### 永不斷線 — Heartbeat

你的 agent 永遠不會死掉。OS 排程器每 30 分鐘檢查一次：每個 workspace session 還活著嗎？如果不是，就用 `claude --resume` 復活它 — 完整 context 還原。

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

- **終端機開著** — session 存活，agent 擁有完整 context，24/7 運行
- **終端機關了** — heartbeat 偵測到，自動復活
- **所有 session** — 都能透過 Claude Code Remote 在任何裝置上看到
- **沒有自訂 daemon** — OS 排程器就是看門狗。從不當機。零維護。

### 排程自動化

OS 層級排程器（Windows Task Scheduler / cron / launchd）— 就算 Claude Code 沒在跑也會執行：

- **Heartbeat** — 確保所有 workspace session 持續存活（死了就復活）
- **Git 同步** — 每 30 分鐘 pull 和 push 所有 repo
- **重要度衰減** — 每天自動調整記憶重要度
- **用戶端狀態** — 追蹤每台機器的 session、最後 heartbeat、已部署的 workspace

---

## Chapter 3：技能 — 你的 Agent 能做什麼

為什麼這很重要：Claude Code 內建了一些技能，但你不能新增、修改、或跟團隊分享。技能是你的競爭優勢。

技能是獨立的模組，就像 Chrome 擴充功能，只是給你的 AI agent 用的。

### 三個技能來源

| 分頁 | 內容 | 可切換？ |
|---|---|---|
| **Claude Native** | 內建：`/batch`、`/loop`、`/simplify`、`/compact` 等 | 技能：可以（透過權限）。指令：唯讀。 |
| **Clawd-Lobster** | 受管理的：memory、heartbeat、evolve、absorb、spec、connect-odoo | 可以 — 完整生命週期 |
| **Custom / Hub** | 你自己的 + 從 ClawHub 下載的社群技能 | 可以 — 完整生命週期 |

一個統一的畫面。三個來源。你系統上的每個技能 — 不管是來自 Anthropic、Clawd-Lobster、還是你自己 — 都能在同一個地方看到和管理。

### 核心技能（鎖定 — 無法停用）

| 技能 | 功能 | 為什麼鎖定 |
|---|---|---|
| Memory Server | 28 工具 MCP memory + SQLite | 沒有記憶 = 沒有 agent |
| Heartbeat | 透過 OS 排程器的 session 保活 | 沒有 heartbeat = session 會死 |
| Evolve | 自我進化 + TODO 處理 | 核心差異化功能 |
| Absorb | 從任何來源吸收知識 | 核心學習能力 |
| Spec | 引導式規劃 + blitz 執行 | 核心開發工作流程 |

### 選用技能

| 技能 | 功能 | 預設 |
|---|---|---|
| Migrate | 從其他 AI 設定匯入 | 啟用 |
| Connect-Odoo | Odoo ERP 整合（XML-RPC） | 停用 |
| Codex Bridge | 將工作委派給 OpenAI Codex（worker + critic） | 停用 |
| NotebookLM Bridge | 透過 Google NotebookLM 實現免費 RAG + 內容引擎 | 停用 |

### 技能管理

每個技能都是一個獨立模組，附有 `skill.json` manifest。透過 **Web UI** 或 **CLI** 管理。

**Web Dashboard** — 打開 `webapp/index.html`：
- 卡片式介面，ON/OFF 開關、狀態指示、分類篩選、搜尋
- 內嵌設定 — 每個技能可獨立編輯設定和憑證
- 健康檢查 — 每個啟用的技能都有綠/黃/紅狀態燈號

**CLI 管理工具：**

```bash
python scripts/skill-manager.py list                     # 列出所有技能
python scripts/skill-manager.py enable connect-odoo      # 啟用技能
python scripts/skill-manager.py disable connect-odoo     # 停用技能
python scripts/skill-manager.py status                   # 詳細狀態
python scripts/skill-manager.py config connect-odoo      # 查看/編輯設定
python scripts/skill-manager.py credentials connect-odoo # 管理憑證
python scripts/skill-manager.py health                   # 執行所有健康檢查
python scripts/skill-manager.py reconcile                # 重新產生 .mcp.json + settings.json
```

### 新增你自己的技能

1. 建立 `skills/my-skill/skill.json` — manifest 宣告一切：

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

2. 實作技能（MCP server、腳本、或 SKILL.md）
3. 執行 `skill-manager.py reconcile` — 它會自動註冊並更新 `.mcp.json` + `settings.json`

**一個技能只要 3 筆設定。** 不用 SDK。不用 plugin API。不被框架綁死。manifest **就是**合約。

---

## Chapter 4：Spec — 你的 Agent 怎麼做計畫

為什麼這很重要：沒有計畫的自主執行，只是隨機產生程式碼。Spec 驅動開發讓 Claude 有藍圖可以遵循。

基於 OpenSpec 方法論。Claude 引導你做規劃，然後自主執行。

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

### 3W1H 標準

每個產物都遵循 Why、What、Who、How — 在各自適當的層級：

| 產物 | 層級 |
|---|---|
| project.md | 廣泛的 context 擷取 |
| proposal.md | 範圍定義 |
| design.md | 架構藍圖 |
| specs/ | 可測試的需求（SHALL/MUST + Gherkin） |
| tasks.md | 執行計畫（分階段，有檔案參照） |

從規劃到決策到日誌到歸檔，一致適用同一套標準。

### Blitz 模式

全速自主執行。Spec 就是計畫 — 不問問題，直接做。

- **分支隔離** — 所有工作在 `blitz/v1`，main 在驗證前保持乾淨
- **階段提交** — 每個階段完成後 `git commit`
- **暫停進化** — `.blitz-active` 標記告訴 evolve-tick 跳過這個 workspace
- **委派標記** — 前綴為 `[codex]` 的任務會跳過，留給外部執行
- **Blitz 結束後** — 合併到 main、將 spec 存為知識、建議下一步

### 驗證

- 每個產物完成後執行自我驗證（proposal、design、specs、tasks）
- 需求必須使用 SHALL 或 MUST — 絕不用 "should"、"could" 或 "might"
- 每條需求都至少有一個 Gherkin scenario
- 每個 task 都包含檔案路徑，且能在 5-30 分鐘內完成
- 產物 DAG 是嚴格的：project → proposal → design → specs → tasks

### 指令

| 指令 | 功能 |
|---|---|
| `/spec new` | 引導式 workspace + spec 建立 |
| `/spec:status` | 顯示進度（逐階段附進度條） |
| `/spec:add "feature"` | 新增到既有 spec（差異操作） |
| `/spec:blitz` | 啟動/續接 blitz 執行 |
| `/spec:archive` | 歸檔完成的變更 + 存為知識 |

---

## Chapter 5：進化 — 你的 Agent 如何進步

為什麼這很重要：v1 只是起點。一個無法從自身工作中學習的 agent，就是一個會停滯的 agent。

v1 做好之後，你的 agent 會持續自動變得更好。

### 進化循環

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

### 三階段內容產線

源自 Claude、Codex 與 Gemini 的三方 AI 辯論，建立了一套內容產生流程：

1. **研究** — 收集來源、吸收脈絡、萃取關鍵洞察
2. **辯論** — 多個 AI 觀點互相挑戰與精煉內容
3. **產出** — 透過 NotebookLM 輸出最終成品（簡報、資訊圖表、Podcast、影片、測驗）

### 吸收（Absorb）

餵它任何東西 — 資料夾、GitHub repo、URL。Claude 會自動分類所有找到的內容：

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

不需要寫解析腳本。Claude Code **本身就是**解析器 — 它能讀任何格式、理解語意、然後存下重要的東西。三種掃描深度：

| 深度 | 內容 |
|---|---|
| `shallow` | README、CLAUDE.md、頂層設定檔 |
| `normal` | shallow 的全部 + 關鍵原始碼、技能定義、重要文件 |
| `deep` | 完整程式碼分析 — 所有原始碼、測試、CI 設定、腳本 |

項目會被分類為知識（事實、架構）、決策（經驗、陷阱）、技能（可重複使用的模式）和 TODO（待辦事項）。

### 進化（自動）

每 2 小時，`evolve-tick.py` 會挑選一個待處理的 TODO，在隔離的 git worktree 中工作。關鍵特性：

- **每次一個 TODO** — 保持簡單和安全
- **永不自動合併** — 所有工作留在 `evolve/<id>` 分支等待審查
- **學到的技能會保留** — 同時存在資料庫和 git 同步的技能檔案中
- **效能追蹤** — 每次使用 +2%，每次改進 +10%，實戰驗證的技能分數 > 2.0x
- **跨 agent 共享** — Agent A 學到的技能，Agent B 透過 git sync 也能用
- **自然淘汰** — 超過 90 天沒用的技能會被標記為可能過時
- **知識持續累積** — 一個 workspace 裡的決策會影響另一個 workspace 的工作，解決過的問題不會再解決第二次

### Blitz vs 進化

| | Blitz | 進化 |
|---|---|---|
| 何時用 | 從 spec 建構 v1 | v1 之後持續改進 |
| 速度 | 所有 task 不間斷 | 每 2 小時一個 TODO |
| 範圍 | 整個專案 | 單一改進 |
| 分支 | `blitz/v1`（結束時合併） | `evolve/<id>`（逐一審查） |
| 自動合併 | 是（在 blitz 分支內） | 絕不 — 人工審查 |

---

## 架構

給想了解內部運作的工程師。

### 底層是怎麼運作的

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

### 實際在跑什麼？

整個 repo 大約 ~13K 行，但大部分是安裝檔、文件和給 Claude 讀的指令。當你的 agent 在工作時，實際佔用記憶體的是：

| 層級 | 內容 | 行數 | RAM | 何時 |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (28 tools + SQLite) | ~1,400 | ~25 MB | 常駐 |
| **Runtime** | Odoo Connector (if enabled) | ~280 | ~22 MB | 啟用時 |
| **Cron** | evolve-tick (TODO processor) | ~465 | ~20 MB peak | 每 2 小時，跑完就結束 |
| **Cron** | heartbeat + sync | ~300 | ~5 MB peak | 每 30 分鐘，跑完就結束 |
| **Static** | Web UI (browser renders it) | ~1,900 | 0 on server | 隨需 |
| **Setup** | Installers, workspace-create, skill-manager | ~2,800 | 0 | 只跑一次 |
| **Docs** | SKILL.md files, README, CHANGELOG | ~3,500 | 0 | Claude 需要時讀取 |
| **Config** | skill.json manifests, templates | ~900 | 0 | 啟動時讀取 |

**常駐佔用：一個 Python process (~25 MB) + SQLite。** 其他東西不是跑完就結束（cron 腳本），就是在瀏覽器裡（Web UI），或只是 Claude 需要 context 時才讀的檔案。

### 跟 Claude Code 的關係

其他框架從頭重建 Claude — 然後呼叫 Claude 的 API 來做實際的思考：

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

我們不呼叫 Claude 的 API。我們不管理 OAuth token。我們不處理 rate limit。我們排程的是 **Claude Code 本身** — 一個 Anthropic 自己做的、自己發佈的、自己維護的工具。當他們改進 Claude Code，我們就跟著變快。當他們改 API，我們完全不受影響。

其他框架在幫**別人的車**做遙控器。我們坐**在車裡**。

### 跟 GitHub 的關係

GitHub 是一切的控制平面：

- **Hub repo** — 你的私人指揮中心
- **Workspace repos** — 每個專案都是私人 repo
- **Git 同步** — 知識、技能和狀態每 30 分鐘同步
- **Heartbeat 狀態** — 機器健康度推送到 git
- **Spec 產物** — 提交到 workspace repo

### 為什麼不自己做引擎？

其他框架從頭重建整個 AI agent — 30 萬行程式碼、自訂 agent loop、自訂工具系統、什麼都自己來。等 Anthropic 出了更好的模型，他們就得忙著改寫 adapter。

**Clawd-Lobster 不跟 Claude Code 競爭，而是讓它更完整。**

我們從 Claude Code 出發 — 世界上最強的 coding agent — 然後只加上它缺的東西：持久記憶、多 agent 協作、精選技能。不多不少，剛剛好。

> *零贅肉。零重寫。純粹的 Claude Code，放大再放大。*

### 設計哲學

#### 1. 最好的 agent 已經存在了，直接用就好。

Claude Code 背後是世界上最大的 AI 安全實驗室。上百萬工程小時打造了它的 agent loop、串流、權限和工具系統。從頭重寫不是雄心壯志 — 是浪費。**站在巨人的肩膀上吧。**

#### 2. 少即是多，而且多很多。

框架的每一行程式碼都是你要維護的。Clawd-Lobster 只有大約 2 千行，因為 Claude Code 原生的擴充點（MCP、hooks、CLAUDE.md）本身就是最好的 plugin 系統。**三筆設定 = 一個技能。零 SDK。**

#### 3. 會忘記的 agent 就是會失敗的 agent。

大部分 AI agent 每次開始都從零開始。它們重複犯錯、重新學習 context、浪費你的時間。Clawd-Lobster 的 4 層記憶加上重要度追蹤，確保**重要的東西浮上來、雜訊慢慢消失、關鍵資訊永遠不會搞丟。**

#### 4. 你的 agent 應該跟你走到哪都能用。

一台電腦？沒問題。三台機器？它們應該共用同一個大腦。GitHub 當控制平面，git sync 當協定。**2 分鐘加入一台新機器。零基礎設施。**

#### 5. 永遠站在最新的浪頭上。

當 Anthropic 推出 Opus 4.7、1M context、新工具 — 你立刻就能用。不用改寫 adapter。不用釘死版本。不用等社群補丁。**用 Claude Code 最好的時間是昨天，第二好的時間是現在。**

#### 6. 能排程的就不要自己寫。

其他框架寫自訂 daemon 讓 agent 24/7 跑。我們用 `cron` + `claude --resume`。其他框架管理 OAuth token 來呼叫 Claude 的 API。我們讓使用者打一次 `claude login` 就好。**你寫的每一行 auth 程式碼，都是 provider 改版時可能壞掉的一行。你沒寫的每一行，就是壞不了的一行。** OS 排程器從 1970 年代就穩定運行到現在。你的自訂 daemon 上禮拜二才寫的。

#### 7. 巨人長高了，你也跟著長高。

Claude Code 內部有記憶整合（autoDream）、常駐 agent（KAIROS）、多 agent 協調（Coordinator Mode）和複雜規劃（ULTRAPLAN）等系統。有些已上線，有些還在 feature flag 後面。我們已經用 2K 行程式碼建了大部分等價功能。

但重點是：**當 Anthropic 原生推出這些功能，我們不用重寫 — 我們退役。** KAIROS 上線了？我們的 heartbeat 優雅讓位。autoDream 改進了？它跟我們的重要度引擎共存。Coordinator Mode 出了？我們的 evolve-tick 直接用。

其他框架跟 Claude Code 競爭。我們跟它互補。他們在 Claude Code 加功能時得重寫。我們得到的是刪程式碼的機會。**我們的程式碼隨時間縮小，他們的則不斷膨脹。**

### 專案結構

```
clawd-lobster/
├── skills/                          技能模組（每個都有 skill.json manifest）
│   ├── memory-server/               24 工具 MCP 記憶 + 重要度 + 進化
│   │   ├── mcp_memory/              Python package (pip install -e .)
│   │   └── skill.json               Manifest
│   ├── connect-odoo/                Odoo ERP 整合 (XML-RPC + poller)
│   │   ├── connect_odoo/            MCP server + poller
│   │   └── skill.json               Manifest
│   ├── evolve/                      自我進化 prompt pattern
│   │   └── skill.json               Manifest
│   ├── heartbeat/                   Session 保活 (cron)
│   │   └── skill.json               Manifest
│   ├── absorb/                      從任何來源吸收知識
│   │   └── skill.json               Manifest
│   ├── spec/                        引導式規劃 + blitz 執行
│   │   └── skill.json               Manifest
│   ├── codex-bridge/                將工作委派給 OpenAI Codex
│   │   └── skill.json               Manifest
│   ├── notebooklm-bridge/           透過 NotebookLM 實現免費 RAG + 內容引擎
│   │   └── skill.json               Manifest
│   ├── migrate/                     從既有設定匯入
│   │   └── skill.json               Manifest
│   └── learned/                     從經驗自動產生的技能
│
├── scripts/
│   ├── skill-manager.py             技能管理 CLI
│   ├── sync-all.ps1                 Windows: 自動 git 同步 + 衰減
│   ├── sync-all.sh                  Linux/macOS: 自動 git 同步 + 衰減
│   ├── heartbeat.ps1                Windows: session 保活
│   ├── heartbeat.sh                 Linux/macOS: session 保活
│   ├── new-workspace.ps1            建立 workspace + GitHub repo
│   ├── workspace-create.py          自動化 workspace 建立
│   ├── validate-spec.py             Spec 產物硬性驗證
│   ├── setup-hooks.sh               安裝 git pre-commit hooks (Unix)
│   ├── setup-hooks.ps1              安裝 git pre-commit hooks (Windows)
│   ├── evolve-tick.py               模式萃取 + 提案 + 重要度衰減
│   ├── notebooklm-sync.py           自動推送 workspace 文件至 NotebookLM
│   ├── init_db.py                   初始化記憶資料庫
│   └── security-scan.py             5 工具安全掃描器
│
├── templates/                       設定範本（不含密鑰）
│   ├── global-CLAUDE.md
│   ├── workspace-CLAUDE.md
│   ├── mcp.json.template
│   └── settings.json.template
│
├── webapp/                          技能管理 Dashboard
│   └── index.html                   3 分頁 UI：Skills + Setup + Settings
│
├── knowledge/                       共享知識庫（git 同步）
├── soul/                            Agent 個性（選用）
├── workspaces.json                  Workspace 註冊表
├── install.ps1                      Windows 安裝程式（4 階段）
├── install.sh                       Linux/macOS 安裝程式（4 階段）
├── Dockerfile                       Docker build
├── docker-compose.yml               Docker Compose 設定
├── LICENSE                          MIT
└── README.md
```

---

## 完整比較

| | Claude Code（原生） | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| Agent 引擎 | Anthropic | 自訂（300K LOC） | 自訂（50K LOC） | **Anthropic（原生）** |
| 認證模式 | 人工登入 | OAuth/API key | API key | **人工登入一次** |
| 費用模式 | 訂閱制 | 按 token 計費 API | 按 token 計費 API | **訂閱制（吃到飽）** |
| 永不斷線 | 沒有 | 自訂 daemon | 自訂 daemon | **OS heartbeat + 自動復活** |
| 持久記憶 | 沒有 | 混合搜尋 | FTS5 + LLM | **4 層 + 重要度引擎** |
| 多 agent 共享記憶 | 沒有 | 沒有 | 沒有 | **有（git 同步）** |
| 技能管理 | 不適用 | 僅 CLI | 手動 | **Web UI + CLI + manifest** |
| Agent 進化 | 沒有 | 沒有 | 自我改進技能 | **有（24 MCP 工具）** |
| 多機器 | 沒有 | 沒有 | 沒有 | **有（MDM 風格）** |
| Session 管理 | 手動 | Gateway process | 手動 | **自動復活所有 session** |
| 上手時間 | 手動設定 | 複雜 | 中等 | **網頁精靈，5 種語言** |
| 自動升級 | 有 | 沒有 | 沒有 | **有** |
| 程式碼量 | 0 | ~300K LOC | ~50K LOC | **~2K LOC** |
| Anthropic API 改版 | 透明 | 破壞性 | 破壞性 | **透明** |
| 稽核軌跡 | 沒有 | 安全稽核 | 沒有 | **完整（每個動作）** |
| 技能安裝 | — | Plugin SDK | 改 3 個檔案 | **1 個 manifest + reconcile** |

---

## 路線圖

**技能**
- [x] Odoo ERP Connector — XML-RPC 整合 + poller (v0.4.0)
- [x] Codex Bridge — 將工作委派給 OpenAI Codex，worker + critic 角色 (v0.5.0)
- [x] NotebookLM Bridge — 透過 Google NotebookLM 實現免費 RAG + 內容引擎 (v0.5.0)
- [x] Spec 驅動開發 — 使用 OpenSpec 方法論的引導式規劃 (v0.5.0)
- [ ] SearXNG — 私有自架網頁搜尋，資料不會離開你的網路
- [ ] Docker Sandbox — 隔離的程式碼執行環境，給不信任的操作用
- [ ] Browser Automation — 用 Playwright 驅動的網頁互動

**平台**
- [x] Linux 安裝程式（bash）+ macOS 安裝程式 (v0.3.0)
- [x] 技能管理 Dashboard — Web UI + CLI 完整技能生命週期 (v0.4.0)
- [x] 技能 manifest 系統 — `skill.json` 含設定、憑證、健康檢查 (v0.4.0)
- [ ] Supabase L4 — 一鍵雲端資料庫（不需要 Oracle wallet）

**進化**
- [x] 進化迴圈 + 提案 — evolve 產生 git 同步的提案，而非直接 TODO (v0.5.0)
- [ ] 技能市集 — 社群貢獻的技能，一鍵安裝
- [x] 自動產生技能 — agent 從成功模式中學習 (v0.3.0 evolve skill)
- [ ] 團隊模式 — 多人共享 workspace，角色式權限控制
- [ ] Agent 間委派 — agent 互相指派任務

---

## FAQ

### 「這不就是 Claude Code 加個殼嗎？」

對，這就是重點。

Claude Code 是目前最強的 coding agent — 背後是 Anthropic 數百萬工程小時的心血。OpenClaw 從頭重建引擎（30 萬行）。Hermes 再重建一次（5 萬行）。我們只加上缺的部分（2 千行），然後保留最好的引擎。

當 Anthropic 推出下一個突破，我們立刻就能用。他們得忙著改寫 adapter。

### 「但其他 agent 可以 24/7 跑而且持續學習」

我們的也可以。排程器每 30 分鐘同步知識。記憶每天透過重要度衰減自然進化。學到的技能透過 git 傳播到所有機器。**agent 不需要一直跑，知識也會持續成長。**

heartbeat 確保 session 持續存活：如果終端機關了，OS 排程器偵測到就用 `claude --resume` 復活 — 完整 context 還原。不需要自訂 daemon。就是 Claude Code，永遠在線。參見[架構](#跟-claude-code-的關係)章節了解我們如何與按 token 計費的 API 框架不同地處理 24/7。

### 「其他 agent 也有 heartbeat 和時間感知」

我們也有 — 但更聰明。我們不跑自訂 daemon process，而是用 OS 排程器（Task Scheduler / launchd / cron）做 heartbeat。它每 30 分鐘檢查：session 還活著嗎？需要 git 同步嗎？重要度衰減到了嗎？用戶端狀態？全部搞定。OS 排程器從不當機、從不需要除錯、閒置時也不燒 token。當 Claude Code 推出原生 24/7 模式（KAIROS — 已經在程式碼裡了），我們免費直接用。零程式碼改動。詳見 [Chapter 2](#永不斷線--heartbeat)。

### 「Claude Code 已經有內建技能了，為什麼還需要更多？」

Claude Code 內建了 `/commit`、`/review-pr`、`/init` 等技能。它們很好用，但也是**封閉的** — Anthropic 決定它們做什麼、怎麼運作、何時改變。你不能新增自己的。你不能修改它們。你不能跟團隊分享。

那就像你手機上的內建 app。Clawd-Lobster 是 App Store。

| | Claude Code 內建 | **Clawd-Lobster 技能** |
|---|---|---|
| 誰建立 | Anthropic | 你、你的團隊、社群 |
| 誰控制 | Anthropic | 你 |
| 可以修改嗎 | 不行 | 可以 — 那是你的程式碼 |
| 可以新增嗎 | 不行 | 可以 — `skill.json` + 實作 |
| 可以分享嗎 | 不行 | 可以 — 推到 GitHub / ClawHub |
| 領域專屬 | 不行（通用開發工具） | 可以 — 你的 ERP、CRM、工作流程 |
| 憑證管理 | 不適用 | 內建每技能憑證系統 |
| 啟用/停用 | 不適用 | 一個開關，Web UI 或 CLI |

你的公司需要一個部署前跑合規檢查的技能？一個每 5 分鐘從 Odoo 同步 CRM 資料的技能？一個用你特定格式產生雙語 PDF 報告的技能？Claude Code 永遠不會出這些。**你的技能就是你的競爭優勢。它們應該在你的系統裡，不是別人的。**

### 「Claude Code 已經有 MCP 和技能了，為什麼還要再做一層？」

Claude Code 給你 MCP — 一個註冊工具伺服器的協定。這就像說 Chrome 讓你安裝擴充功能。沒錯。但 Chrome 還有 **Chrome 線上應用程式商店** — 因為手動安裝 `.crx` 檔案不叫管理擴充功能。

Claude Code 給你的：
- `.mcp.json` — 一個扁平的伺服器指令列表。沒有 metadata。沒有生命週期。
- `settings.json` — 一個扁平的允許工具列表。沒有分組。沒有開關。
- `CLAUDE.md` — 自由格式文字。沒有 schema。沒有驗證。

實際上這代表：
- **安裝技能？** 手動改 3 個 JSON 檔案然後跑 `pip install`。
- **停用技能？** 手動從 2 個檔案刪除項目，希望你沒漏掉。
- **憑證？** 每個技能存在不同地方。有的用環境變數、有的用檔案、有的寫死。
- **有在跑嗎？** 不知道。打開終端機隨緣。
- **第二台機器？** 全部從頭再來一次。
- **10 個技能？** 你的 `.mcp.json` 變成一面看不懂的 JSON 牆。祝你好運。

Clawd-Lobster 的技能層加上了 MCP 沒有的東西：

| MCP（原生） | 技能管理（我們的） |
|---|---|
| 扁平 JSON 設定 | `skill.json` manifest 含 schema、憑證、健康檢查、相依性 |
| 手動編輯安裝 | `skill-manager.py enable <id>` — 一個指令 |
| 手動編輯移除 | `skill-manager.py disable <id>` — 一個指令，乾淨移除 |
| 沒有憑證標準 | 集中式 `~/.clawd-lobster/credentials/`，每技能欄位定義 |
| 沒有健康監控 | 內建健康檢查（mcp-ping、command、HTTP） |
| 沒有 UI | Web dashboard 含卡片、開關、搜尋、分類篩選 |
| 每台機器各自設定 | 透過 git 跨機器同步註冊表 |
| 沒有相依性追蹤 | 技能宣告所需 — 其他技能、系統工具、Python 套件 |

**MCP 是協定。我們是套件管理器。**

就像 `npm` 不是要取代 Node.js — 它讓 Node.js 在規模化時能用。我們的技能層不是要取代 MCP — 它讓 MCP 在你有 5、10 或 50 個技能分散在多台機器上時能管理。詳見 [Chapter 3](#chapter-3技能--你的-agent-能做什麼) 完整的技能管理系統。

### 「Anthropic 會封鎖這個嗎？」

我們沒做任何 Anthropic 禁止的事。精確地說：

- **我們做的事：** 透過 OS cron/Task Scheduler 排程 `claude` CLI 指令。用 `claude --resume` 恢復既有 session。使用 Anthropic 自己定義的 MCP 協定。
- **我們不做的事：** 程式化 OAuth 登入。API key 自動化。Token 擷取。認證繞過。逆向工程。

使用者跑一次 `claude login` — 一個人，在瀏覽器裡，用他們的 Pro 訂閱。之後，OS 排程器用 Anthropic 自己在 CLI 裡提供的 flag（`--resume`、`-p`、`--allowedTools`）保持 session 存活。這跟用 cron 排程 `git pull` 沒什麼不同。**我們是自動化一個 CLI 工具，不是冒充使用者。**

其他框架直接呼叫 Claude 的 API — 他們需要 API key、管理 OAuth refresh token、處理 rate limit、然後祈禱定價不要變。每次 API 改版對他們來說都是破壞性的改動。對我們來說，是透明的 — Claude Code 自己處理自己的認證。

### 「重度工作量的 API 費用呢？」

「昂貴的 API」這個論點，是基於按 token 計費的假設。有了 Pro 訂閱（$20/月），**沒有按 token 的費用。** 你的第 1 個任務和第 480 個任務花的都一樣：邊際成本 $0。

這直接消除了其他框架需要的「思考用貴模型，苦力用便宜模型」的架構。你不需要在本機跑 Ollama 7B 處理便宜任務。你不需要兩套推論架構。你不需要一個模型路由器來決定用哪個大腦。

一個訂閱。一個引擎。一個大腦。無限任務。

當 rate limit 打到了（遲早的），Clawd-Lobster 的 skill-manager 會優雅地排隊工作。沒有 token 預算恐慌。沒有帳單驚喜。**可預測的費用本身就是功能。**

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
