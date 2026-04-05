[English](README.md) | [**繁體中文**](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/footprint-25MB_RAM-orange)

<p align="center">
<strong>從想法到可用的程式碼，只需一場對話。</strong><br>
<em>Spec Squad 將你的描述轉化為經過審查、測試的程式碼庫 — 由 Claude Agent SDK 驅動。</em>
</p>

<p align="center">
<sub>Web 儀表板 + CLI。多 Agent 開發。持久記憶體。多機同步。</sub>
</p>

---

## 什麼是 Clawd-Lobster？

Claude Code 是大腦，Clawd-Lobster 是神經系統。

Claude Code 是目前最強大的程式寫作 Agent，但它在 session 之間會遺忘所有記憶、只能在單機執行、也沒有技能管理。Clawd-Lobster 正好補足這些缺口：一個 **Spec Squad** 透過對抗式多 Agent 協作來規劃、審查、建構和測試你的程式碼 — 加上持久記憶體、多機編排、精選技能和自我進化。

**Clawd-Lobster 是一個產生器。** 你只需執行一次，它就會建立你的專屬 **Hub** — 一個私人 GitHub 儲存庫，作為你的指揮中心。你的 Hub 管理所有機器、工作區、記憶體和技能。

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

GitHub 是控制平面，Git 是通訊協定。所有狀態 — 技能、知識、工作區註冊表、心跳狀態 — 都存放在 git 中並自動同步。

**執行足跡：25 MB 記憶體、672 KB 磁碟空間。** 一個 Python 程序（MCP Memory Server）加上 SQLite。其餘一切透過作業系統排程器執行後退出，或在瀏覽器中運作。零輪詢、零常駐程序、零臃腫。

---

## 快速開始

三種上手方式，依你的風格選擇。

### Web UI（推薦新手使用）

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
# Browser opens at http://localhost:3333
# Onboarding wizard walks you through everything
```

### 終端機（適合進階使用者）

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# 4-step interactive wizard: prerequisites -> persona -> workspace root -> first workspace
```

### 傳統方式（安裝腳本）

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

### 安裝流程說明

安裝程式會檢查先決條件、驗證 Claude Code + GitHub、建立你的 Hub、安裝 MCP Memory Server（32 個工具）、設定工作區，以及註冊排程器 + 心跳。全程只需 2 次 OAuth 點擊，不需要 API 金鑰。

| 平台 | 同步 | 心跳 |
|----------|------|-----------|
| Windows | Task Scheduler (30 min) | Task Scheduler (30 min) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | Container lifecycle | Container lifecycle |

---

## Web 儀表板

使用 `clawd-lobster serve` 啟動（預設埠 3333）。儀表板提供三個主要畫面：

### /onboarding — 設定精靈

首次造訪者會自動導向此頁。精靈會檢查先決條件（Python、Claude CLI、Git、pip），讓你選擇角色（引導 / 專家 / 技術），設定工作區根目錄，並建立第一個工作區 — 全部在瀏覽器中完成。

### /workspaces — 工作區管理

列出所有已註冊的工作區及即時狀態。每個工作區卡片顯示路徑、記憶體資料庫大小、git 同步狀態和 Spec Squad 階段。可直接從儀表板建立新工作區或切換同步開關。

### /squad — Spec Squad

多 Agent 開發介面。開始探索對話、觀看 Architect 撰寫規格、看 Reviewer 提出挑戰、追蹤 Coder 的建構過程，並監控 Tester 的驗證結果 — 全部透過 SSE 即時更新進度。

---

## Spec Squad — 多 Agent 開發

Spec Squad 是 v1.0 的核心功能。四個專業 Agent 協作，將你的想法轉化為經過審查、測試的程式碼 — 使用 Claude Agent SDK。

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

### 對抗式審查的運作方式

Reviewer 被指示要「嚴厲但公正」。它會閱讀 `openspec/` 中的每個檔案，挑戰架構、需求和任務拆分。如果發現問題，Architect 必須修改。這個迴圈最多執行 5 輪，直到 Reviewer 給出 APPROVED 判定並附上信心分數。結果是在寫下任何一行程式碼之前，規格就已經過壓力測試。

### Web 模式 vs 終端機模式

| | Web (`/squad`) | Terminal (`clawd-lobster squad start`) |
|---|---|---|
| Discovery | 瀏覽器中的聊天介面 | stdin/stdout |
| 進度 | 即時 SSE 事件，視覺化階段 | 終端機印出階段標籤 |
| 建構確認 | 在瀏覽器中提示 | `Build now? (y/n)` |
| 狀態 | 保存於 `.spec-squad.json` | 同一檔案 |
| 底層引擎 | 相同的 `squad.py` async 核心 | 相同的 `squad.py` async 核心 |

兩種模式使用相同的流程、相同的 Agent SDK 呼叫、相同的狀態檔。選擇適合你工作流程的即可。

---

## 技能

9 個技能模組，每個都有 `skill.json` 清單。共 32 個 MCP 工具。

### 核心技能（鎖定）

| 技能 | 類型 | 功能 |
|---|---|---|
| **Memory Server** | mcp-server | 26 個 MCP 工具的記憶體系統，含 SQLite、顯著性引擎、CJK 感知壓縮 |
| **Heartbeat** | cron | 透過作業系統排程器維持 session 存活 — 自動復活已停止的 session |
| **Evolve** | prompt-pattern | 模式萃取、改進提案、顯著性衰減 |
| **Absorb** | prompt-pattern | 從資料夾、GitHub 儲存庫、URL 匯入知識 |
| **Spec** | prompt-pattern | 使用 OpenSpec 方法論進行引導式規劃 + 閃電執行 |

### 選用技能

| 技能 | 類型 | 功能 | 預設 |
|---|---|---|---|
| **Migrate** | prompt-pattern | 從現有 AI 設定匯入（自動偵測格式） | 啟用 |
| **Connect-Odoo** | mcp-server | Odoo ERP 整合 — 透過 XML-RPC + poller 提供 6 個 MCP 工具 | 停用 |
| **Codex Bridge** | prompt-pattern | 將工作委派給 OpenAI Codex，含 worker + critic 角色 | 停用 |
| **NotebookLM Bridge** | prompt-pattern | 透過 Google NotebookLM 提供免費 RAG + 內容引擎 | 停用 |

### 技能管理

每個技能都是自包含的模組，帶有 `skill.json` 清單。透過 **Web UI** 或 **CLI** 管理：

```bash
clawd-lobster serve                                      # Web dashboard with toggles
python scripts/skill-manager.py list                     # Table of all skills
python scripts/skill-manager.py enable connect-odoo      # Enable a skill
python scripts/skill-manager.py disable connect-odoo     # Disable a skill
python scripts/skill-manager.py health                   # Run all health checks
python scripts/skill-manager.py reconcile                # Regenerate .mcp.json + settings.json
```

### 新增自訂技能

在 `skills/my-skill/skill.json` 建立清單，實作技能（MCP server、script 或 SKILL.md），然後執行 `skill-manager.py reconcile`。一個技能只需 3 個設定項 — 不需要 SDK、不需要 plugin API、沒有框架綁定。

---

## 架構

### 3 層設計

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

### 4 層記憶體

| 層級 | 內容 | 速度 | 範圍 |
|-------|------|-------|-------|
| **L1.5** | Claude Code 自動記憶（原生） | 即時 | 目前專案 |
| **L2** | SQLite + 26 個 MCP 工具 | ~1ms | 每個工作區 |
| **L3** | Markdown 知識庫 | ~10ms | 透過 git 共享 |
| **L4** | 雲端資料庫（選用） | ~100ms | 跨工作區 |

顯著性引擎讓重要記憶保持可存取：每次存取提升 5% 顯著性，手動強化提升 20%（上限 2.0x），未被存取的項目在 30 天後每天衰減 5%（下限 0.01 — 永不刪除）。

### 實際在執行什麼？

| 層級 | 內容 | 行數 | 記憶體 | 執行時機 |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (26 tools + SQLite) | ~1,400 | ~25 MB | 持續運行 |
| **Runtime** | Odoo Connector (if enabled) | ~280 | ~22 MB | 啟用時 |
| **Runtime** | Web Dashboard (stdlib HTTP) | ~800 | ~15 MB | 提供服務時 |
| **Cron** | evolve-tick (proposal generator) | ~465 | ~20 MB peak | 每 2 小時，執行後退出 |
| **Cron** | heartbeat + sync | ~300 | ~5 MB peak | 每 30 分鐘，執行後退出 |
| **Setup** | CLI + onboarding + squad orchestrator | ~1,200 | 0 | 隨需執行 |
| **Config** | skill.json manifests, templates | ~900 | 0 | 啟動時讀取 |

**常駐足跡：一個 Python 程序（約 25 MB）+ SQLite。** Web 儀表板使用標準函式庫 `http.server` — 沒有 Flask、沒有 FastAPI、沒有外部相依套件。

### 設計哲學

1. **站在巨人的肩膀上。** Claude Code 背後有數百萬工程小時。我們補足缺少的部分（約 3K 行），保留最好的引擎。

2. **程式碼越少，問題越少。** 三個設定項 = 一個技能。零 SDK。作業系統排程器從 1970 年代就穩定至今 — 我們使用 `cron` + `claude --resume` 而非自建常駐程序。

3. **巨人成長，你也成長。** 當 Anthropic 推出原生記憶體、24/7 Agent 或多 Agent 協調時 — 我們不需要重寫，我們退役程式碼。**我們的程式碼庫隨時間縮小，他們的則持續成長。**

完整檔案樹和內部結構請參閱 [ARCHITECTURE.md](ARCHITECTURE.md)。

---

## CLI 參考

| 指令 | 功能 |
|---|---|
| `clawd-lobster serve` | 在 localhost:3333 啟動 Web 儀表板 |
| `clawd-lobster serve --port 8080` | 使用自訂埠 |
| `clawd-lobster serve --daemon` | 在背景執行伺服器 |
| `clawd-lobster setup` | 執行終端機設定精靈 |
| `clawd-lobster workspace create <name>` | 建立新工作區 |
| `clawd-lobster workspace create <name> --repo` | 建立工作區 + 私人 GitHub 儲存庫 |
| `clawd-lobster workspace create <name> --dry-run` | 預覽而不實際變更 |
| `clawd-lobster squad start` | 以終端機模式啟動 Spec Squad |
| `clawd-lobster squad start --workspace <path>` | 指定目標工作區 |
| `clawd-lobster status` | 顯示系統健康狀態、工作區、版本 |
| `clawd-lobster --version` | 顯示版本 |

---

## 多機設定

### Hub 模式

你的 Hub 是一個私人 GitHub 儲存庫，作為你的指揮中心。每台機器都 clone Hub 並自動同步。

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

### 新增另一台機器

```bash
git clone https://github.com/you/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# Choose "Join existing Hub" -> paste your Hub URL -> name this machine -> done
```

新機器會立即繼承所有累積的知識。L2（SQLite）在每個工作區保持本地，L3（markdown）透過 git 同步，L4（選用的雲端資料庫）統合一切。

### 永不停機 — 心跳機制

你的 Agent 永遠不會停止。作業系統排程器每 30 分鐘檢查一次：每個工作區的 session 是否存活？如果沒有，就用 `claude --resume` 復活 — 完整的上下文恢復。不需要自建常駐程序。只有 Claude Code，永遠在線。

---

## 工作區

工作區是一個帶有記憶體、技能和規格支援的專案目錄。

### 工作區結構

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

### 排程自動化

作業系統層級的排程器（Windows Task Scheduler / cron / launchd）在 Claude Code 未啟動時也能執行：

- **Heartbeat** — 確保所有工作區 session 保持存活（停止時自動復活）
- **Git sync** — 每 30 分鐘拉取和推送所有儲存庫
- **Salience decay** — 每日記憶體重要性調整
- **evolve-tick** — 每 2 小時進行模式萃取 + 改進提案

---

## 記憶體系統

### 26 個 MCP 工具

| 分類 | 工具 |
|---|---|
| **寫入** | `memory_store`, `memory_record_decision`, `memory_record_resolved`, `memory_record_question`, `memory_record_knowledge` |
| **讀取** | `memory_list`, `memory_get`, `memory_get_summary` |
| **刪除** | `memory_delete` |
| **搜尋** | `memory_search` (vector + text, salience-weighted, all tables) |
| **顯著性** | `memory_reinforce` |
| **進化** | `memory_learn_skill`, `memory_list_skills`, `memory_improve_skill` |
| **TODO** | `memory_todo_add`, `memory_todo_list`, `memory_todo_update`, `memory_todo_search` |
| **稽核追蹤** | `memory_log_action`, `memory_audit_search`, `memory_audit_stats`, `memory_daily_report`, `memory_activity_log` |
| **管理** | `memory_compact`, `memory_status`, `memory_oracle_summary` |

記憶體不是被動的儲存空間 — 它主動塑造你的 Agent 的運作方式。每條軌跡都被記錄。每個工作區透過 git 共享知識。你的 Agent 一起成長。

---

## 進化系統

v1 建構完成後，你的 Agent 會自動持續進步。

### 循環

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

Evolve 產生的是**提案**，而非直接變更。所有提案保存在 `openspec/proposals/` 供人工審查。學到的技能透過 git sync 在 session 和機器間持久保存。

---

## 系統需求

- **Python** 3.10+ 和 **Git** 2.x+
- **Claude Code** CLI ([安裝指南](https://docs.anthropic.com/en/docs/claude-code/getting-started))
- **GitHub** 帳號（用於你的私人 Hub 儲存庫）
- **Node.js** 18+（選用 — 僅在使用需要它的 MCP server 時才需要）

---

## 安裝（詳細）

### 1. 複製並安裝

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
```

這會全域註冊 `clawd-lobster` CLI 指令。

### 2. 執行設定

選擇其一：

```bash
clawd-lobster serve    # Web wizard at http://localhost:3333
clawd-lobster setup    # Terminal wizard
./install.ps1          # Windows classic installer
./install.sh           # macOS/Linux classic installer
```

### 3. 驗證

```bash
clawd-lobster status
# Shows: Python version, Claude CLI, Git, workspaces, server status
```

### 4. 開始建構

```bash
clawd-lobster squad start                    # Describe your project -> spec -> build
clawd-lobster workspace create my-app --repo # Or create a workspace manually
```

---

## 常見問題

### 「這不就是 Claude Code 加個外殼嗎？」

是的。這正是重點。

Claude Code 是目前最強大的程式寫作 Agent — 背後有 Anthropic 數百萬工程小時的支撐。其他框架從零開始重建引擎（50K-300K 行）。我們補足缺少的部分（約 3K 行），保留最好的引擎。

當 Anthropic 推出下一個突破時，我們立即受惠。其他框架則必須重寫適配層。

### 「Spec Squad 跟直接叫 Claude 寫程式有什麼不同？」

Spec Squad 在撰寫程式碼前加入了**對抗式審查**。Architect 撰寫完整規格，然後 Reviewer 嚴格挑剔 — 找出漏洞、模糊之處和薄弱的決策。在 Coder 動手之前，最多會進行 5 輪修改。這意味著程式碼是根據經過壓力測試的藍圖來建構，而非根據隨意的提示。

### 「但其他 Agent 能 24/7 執行且持續學習」

我們的也是。排程器每 30 分鐘同步知識。記憶體透過顯著性衰減每日進化。學到的技能透過 git 傳播到所有機器。心跳確保 session 保持存活：如果終端機關閉，作業系統排程器會用 `claude --resume` 復活 — 完整的上下文恢復。

### 「Claude Code 已經有內建技能和 MCP 了，為什麼還需要這個？」

Claude Code 的內建技能是封閉的 — 你無法新增、修改或分享。MCP 提供協定，但沒有生命週期管理。安裝一個技能意味著手動編輯 3 個 JSON 檔案。第二台機器？全部重來。

**MCP 是協定，我們是套件管理器。** 我們新增的：`skill.json` 清單、一鍵啟用/停用、集中式憑證管理、健康檢查、Web 儀表板，以及透過 git 的跨機器註冊表同步。

### 「Anthropic 不會封鎖這個嗎？」

我們透過作業系統 cron 排程 `claude` CLI 指令 — 就像排程 `git pull` 一樣。我們使用 `claude --resume`、`--allowedTools` 和 MCP server — 全是 Anthropic 在自家 CLI 中提供的旗標。沒有 API 金鑰自動化、沒有 OAuth token 抓取、沒有逆向工程。

### 「費用怎麼算？」

使用 Pro 訂閱（$20/月），沒有按 token 計費。一個訂閱、一個引擎。可預測的費用本身就是一個優勢。

---

## 比較

| | Claude Code (原生) | 重量級框架 | **Clawd-Lobster** |
|---|---|---|---|
| Agent 引擎 | Anthropic | 自建（50K-300K LOC） | **Anthropic（原生）** |
| 多 Agent 開發 | 無 | 部分支援 | **有（Spec Squad：4 個 Agent）** |
| 對抗式審查 | 無 | 無 | **有（最多 5 輪）** |
| 持久記憶體 | 無 | 各異 | **4 層 + 顯著性** |
| 多機支援 | 無 | 無 | **有（Hub + git sync）** |
| 永不停機 | 無 | 自建常駐程序 | **作業系統心跳 + 自動復活** |
| 技能管理 | 無 | CLI/SDK | **Web UI + CLI + manifest** |
| 自我進化 | 無 | 各異 | **有（提案 + 學習技能）** |
| 新手引導 | 手動 | 複雜 | **Web 精靈或終端機，5 種語言** |
| Web 儀表板 | 無 | 各異 | **有（localhost:3333）** |
| 程式碼量 | 0 | 50K-300K LOC | **約 3K LOC** |
| 費用模式 | 訂閱制 | 按 token API | **訂閱制（固定）** |
| Anthropic 升級 | 透明 | 中斷 | **透明** |

---

## 路線圖

**v1.0 已完成**
- [x] 統一 CLI 入口（`clawd-lobster serve/setup/squad/workspace/status`）
- [x] Web 儀表板，含設定精靈、工作區管理、Spec Squad UI
- [x] Spec Squad — 透過 Claude Agent SDK 的多 Agent 開發
- [x] 三種使用者角色（引導 / 專家 / 技術）
- [x] 9 個技能、32 個 MCP 工具、`skill.json` 清單系統
- [x] 4 層記憶體 + 顯著性引擎
- [x] 多機 Hub 模式 + git sync
- [x] 透過作業系統排程器的心跳自動復活
- [x] 進化循環 + git 同步提案
- [x] Docker 支援

**下一步**
- [ ] Supabase L4 — 一鍵雲端資料庫（不需要 Oracle wallet）
- [ ] SearXNG — 私人自架網路搜尋
- [ ] Docker Sandbox — 隔離的程式碼執行環境，用於不受信任的操作
- [ ] Skill marketplace — 社群貢獻的技能，一鍵安裝
- [ ] 團隊模式 — 多使用者共享工作區，含角色存取控制
- [ ] Agent 間委派 — Agent 互相分派任務

---

## 專案結構

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

## 貢獻

歡迎貢獻！最簡單的參與方式：

1. **新增技能** — 在 `skills/` 中建立資料夾並附上 `skill.json` 清單
2. **改進範本** — 在 `templates/` 中提供更好的預設值
3. **平台支援** — 協助 Linux/macOS 測試
4. **回報問題** — 開一個 issue

---

## 授權

MIT — 隨你怎麼用。

---

<p align="center">
<sub>與 Anthropic 無關。建構於 <a href="https://claude.ai/code">Claude Code</a> 之上。</sub>
</p>
