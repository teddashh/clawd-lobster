[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/RAM-25MB-orange)

<p align="center">
<strong>你終究要用 Claude Code 的 — 為什麼不一開始就選最好的體驗？</strong><br>
<strong>反正你遲早會用 Claude Code — 何不從最好的體驗開始？</strong>
</p>

---

## 問題在哪

你看過那些 AI agent 框架。可能也試過幾個。以下是實際會發生的事：

**問題一：Claude Code 很強，但你得一直盯著它。**
每次 session 都從零開始。它忘了昨天學到什麼。你複製貼上前後文，重新解釋架構，重新描述慣例。你就是記憶體。你就是管理者。你就是瓶頸。

**問題二：AI Agent 框架 demo 很炫，實際體驗很痛。**
三十萬行程式碼。自訂 adapter。設定檔比你的專案還長。底層模型一更新就壞掉。你花在維護框架的時間比開發產品還多。

**問題三：灰色地帶。**
自架的 agent 迴圈繞過安全機制。API 按 token 計費毫無上限。東拼西湊的 Frankenstein 技術棧，你搞不清楚到底是你在用工具，還是工具在用你。

## 解答

Clawd-Lobster 不是要取代 Claude Code。它讓 Claude Code 學會**記憶、規劃、審查、建構、進化** — 而且只用 Anthropic 官方工具。

- **100% Claude Code CLI + Agent SDK。** 沒有包裝層，沒有自訂 agent 迴圈，沒有灰色地帶。跑在你現有的 Claude 訂閱上。不用額外 API 費用。
- **約 9,000 行程式碼。** 不是 300,000 行。Claude Code 更新時，新功能直接到手。不用改寫，不會壞掉。
- **5 分鐘上手。** 開瀏覽器。點兩下。搞定。不用 API key，不用 Docker，不用 YAML 博士學位。

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

## 快速開始

### 所有人適用（Web UI）

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
```

瀏覽器打開。安裝精靈帶你走完一切。

### 給終端機控

```bash
clawd-lobster setup        # 終端機導引安裝
clawd-lobster squad start  # 在終端機裡跑 Spec Squad
```

### 傳統安裝（進階使用者）

```powershell
# Windows
.\install.ps1

# macOS / Linux
chmod +x install.sh && ./install.sh
```

---

## 你會得到什麼

### 1. Spec Squad — 你的 AI 開發團隊

你描述你要什麼。四個 Claude session 搞定剩下的。

**Architect** 寫出一份包含可測試需求的完整規格書。**Reviewer** — 一個完全獨立、從未看過 Architect 指令的 Claude session — 把它拆開來挑毛病。他們反覆來回直到 Reviewer 核可。然後 **Coder** 嚴格按規格書來蓋。**Tester** 驗證每一條需求。

這不是噱頭。測試中，Reviewer 在第一份規格書就找到 11 個真實 bug — 那些自我驗證清單永遠抓不到的問題。回傳型別衝突、API 不一致、不可能的 Gherkin 場景、套件不相容。

**為什麼有效：** 每個 agent 跑在隔離的上下文裡。Reviewer 不會受 Architect 的推理影響。Tester 不知道 Coder 走了什麼捷徑。獨立的腦袋找出獨立的問題。

兩種介面，同一個引擎：
- **Web：** 在瀏覽器跟 Claude 聊，然後在即時 dashboard 上看 agent 幹活
- **終端機：** Claude 在終端機問你問題，agent 跑起來時即時顯示進度

### 2. 不會忘記的腦袋 — Thin Ledger

兩層協作。不用向量資料庫。不需要雲端。

| 層 | 內容 | 角色 |
|-----|------|------|
| **SQLite (The Ledger)** | 決策、TODO、稽核日誌、顯著性分數、provenance | 營運真相 — 快速、結構化、可查詢 |
| **Git Wiki (The Library)** | 交叉引用的 markdown 頁面、索引、日誌、來源 | 編譯後的知識庫 — 人類可讀、Git 同步 |
| **Cloud DB (optional)** | Oracle or other cloud DB for cross-machine search | Global sync — only if you need multi-machine recall |

每筆知識記錄都帶 **provenance** — 誰寫的、哪個 agent、信心分數、生命週期狀態（raw → synthesized → accepted → superseded）。沒有匿名事實。

**三個操作保持它的健康：**
- **INGEST** — 新資訊變成帶引用的 wiki 頁面
- **QUERY** — 搜尋兩層、引用來源。有價值的答案會寫回 wiki。
- **LINT** — 定期健康檢查，找出矛盾、過時聲明、孤立頁面、壞連結

**修正工作流：** Agent 不能直接編輯 wiki 頁面。它們透過 `memory_propose_correction` 提出修正，建立審查佇列。有爭議的聲明會被解決，不會被靜默覆蓋。

重要的想法浮上來。雜訊沉下去。有用的技能被強化。過時的知識自然衰減。你完全不用管 — 全部自動。

*架構吸收自 [MemPalace](https://github.com/milla-jovovich/mempalace)（空間結構）和 [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)（INGEST/QUERY/LINT）。不安裝任何相依套件 — 只用概念。*

### 3. 永遠在線

闔上筆電。Clawd-Lobster 繼續幹活。

heartbeat 用的是你作業系統的排程器（Task Scheduler / cron / launchd）— 不是自訂 daemon，不是 polling 迴圈，不是燒 token 的背景程序。Session 掛了就帶著完整上下文自動復活。不用盯。

### 4. 所有機器，一個腦袋

GitHub 是控制平面。Git 是協定。

機器 A 學到一個模式。它同步到你的私有 Hub。機器 B 立刻繼承。新機器？`install.ps1`，「Join Hub」，貼上網址，2 分鐘，完全上線。

### 5. 自我進化

完成複雜工作後，系統會萃取可重用的模式，存成學到的技能。下次遇到類似任務，它記得上次怎麼解決的。

技能有效能分數。驗證過的模式被強化。過時的技能自然衰減。系統越用越聰明 — 不是魔法，是因為它把有效的方法寫下來了。

---

## Dashboard

`clawd-lobster serve` 在 `localhost:3333` 開啟常駐 web dashboard。

**新手引導** — 首次啟動的精靈會檢查前置需求、帶你設定、建立第一個 workspace。

**Workspaces** — 所有專案一目了然。狀態、規格書進度、記憶體大小、最後活動時間。

**Spec Squad** — 跟 Claude 聊天釐清需求。在即時 dashboard 上看四個 agent 工作，有階段時間軸和對話歷程。

---

## Skills

9 個精選 skill。每個只做好一件事。點名稱看完整文件。

### [memory-server](skills/memory-server/README.md) — 根基
26 個 MCP 工具，跨 session 持久記憶。4 層架構，從即時本地快取到雲端同步。顯著性引擎自動浮現重要知識、讓雜訊沉澱。支援 CJK token 估算。這就是讓 Claude Code 不再失憶的 skill。

### [spec](skills/spec/README.md) — 從想法到程式碼
引導式 workspace 建立、OpenSpec 文件產出（3W1H）、Spec Squad 多 agent 流水線。Discovery 訪談萃取你的需求。Architect 撰寫含 Gherkin 場景的可測試規格書。Reviewer 把它拆開來挑。Coder 按契約實作。Tester 逐條驗證。終端機或 Web 皆可。

### [evolve](skills/evolve/README.md) — 自我精進
每 2 小時自動執行。掃描已完成的工作，萃取可重用模式，存成學到的技能。技能有效能分數 — 驗證過的模式被強化，過時的自然衰減。你的 agent 越用越犀利。不需任何設定。

### [absorb](skills/absorb/README.md) — 知識吸收
指向一個 GitHub repo、本地資料夾或網址。它讀完整份 codebase，萃取架構決策、慣例和模式，然後存成可搜尋的知識。適合加入既有專案或研究參考實作時使用。

### [heartbeat](skills/heartbeat/README.md) — 永遠在線
作業系統原生保活（Task Scheduler / cron / launchd）。每 30 分鐘檢查一次。掛掉的 session 透過 `claude --resume` 帶著完整上下文復活。沒有自訂 daemon，沒有 polling 迴圈，不燒 token。闔上筆電 — 你的 agent 繼續幹活。

### [migrate](skills/migrate/README.md) — 一次性匯入
偵測現有的 AI 設定（`~/.claude/`、`~/.openclaw/`、`~/.hermes/`、`~/Documents/claude-setup/`）並匯入記憶、設定和知識。上線時跑一次，之後不用再跑。

### [codex-bridge](skills/codex-bridge/README.md) — 第二大腦
把大量工作委派給 OpenAI Codex（跑在你的 ChatGPT Plus 上）。當**工人**用（平行任務、樣板程式碼、測試產出）或當**評審**用（對抗式安全審查、架構辯論、code review）。Claude 自行判斷何時委派。也能透過 AGENTS.md 把 Claude 的知識同步給 Codex。

### [connect-odoo](skills/connect-odoo/README.md) — ERP 整合
透過 XML-RPC + MCP 雙向連接 Odoo ERP。6 個專用工具讀寫 Odoo 資料。即時 polling 偵測變更。適合 AI 工作流需要與業務流程互動時使用。

### [notebooklm-bridge](skills/notebooklm-bridge/README.md) — 文件產出
自動將 workspace 文件同步到 Google NotebookLM。從你的 codebase 文件產出簡報、資訊圖表、podcast 和報告。內建浮水印移除：多頁用頁碼蓋印、單頁用日期蓋印。全頁面風格一致。

---

每個 skill 都有**觸發描述**（Claude 知道何時啟動）、**Gotchas 區塊**（常見錯誤要避免）、和**動態 `!command` 注入**（載入時的即時上下文）。

---

## 架構

```
Skills (the what)      ->  10 skills with manifests, instructions, gotchas
Tools (the how)        ->  32 MCP tools + Claude Code native tools
Hooks (the when)       ->  OS scheduler, git hooks, PostToolUse, Stop hooks
Memory (the brain)     ->  SQLite Ledger + Git Wiki (Thin Ledger pattern)
Operations (the cycle) ->  INGEST / QUERY / LINT (continuous knowledge lifecycle)
```

**站在巨人肩膀上。** Clawd-Lobster 不重建 Claude Code。它用 Claude Code 原生的擴充點（MCP servers、CLAUDE.md、hooks、settings.json），完全照 Anthropic 的設計走。Claude Code 出新功能，你直接受益。模型進步，你的 agent 跟著進步。零 adapter 程式碼。

```
Disk: ~830 KB    (code + configs)
RAM:  ~25 MB    (MCP server only)
CPU:  0% idle   (OS scheduler, not polling)
LOC:  ~9,000    (not 300,000)
```

完整檔案樹和執行時期細節，請見 [ARCHITECTURE.md](ARCHITECTURE.md)。

---

## CLI 參考

| Command | What It Does |
|---------|-------------|
| `clawd-lobster serve` | Start web dashboard (localhost:3333) |
| `clawd-lobster setup` | Terminal onboarding wizard |
| `clawd-lobster workspace create <name>` | Create a new workspace |
| `clawd-lobster squad start` | Run Spec Squad in terminal |
| `clawd-lobster status` | Show system health |

---

## 多機器設定

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

第一台機器建立 Hub。之後每台 2 分鐘加入。

---

## 環境需求

- Python 3.10+
- Claude Code CLI ([install](https://claude.ai/code))
- Git 2.x+
- Node.js 18+ (optional, for Codex Bridge)
- GitHub account (for Hub sync)

---

## 比較

|  | Heavyweight Frameworks | Raw Claude Code | Clawd-Lobster |
|--|----------------------|----------------|---------------|
| Codebase | 300K+ lines | 0 (built-in) | ~9,000 lines |
| Setup | Hours/days | 0 | 5 minutes |
| Memory | Session-only | Session-only | 4-layer persistent |
| Multi-machine | Usually none | None | Git sync + Hub |
| Model updates | Breaks adapters | Automatic | Automatic |
| Token cost | API per-token | Subscription | Subscription |
| Multi-agent review | Some | None | Spec Squad (adversarial) |
| Self-evolution | None | None | Learned skills + salience |

---

## 設計哲學

**1. 放大，不是重建。**
Claude Code 是世上最強的 coding agent。我們給它裝上神經系統。我們不重建大腦。

**2. 巨人長高，你也長高。**
每次 Claude Code 更新都讓你的 Clawd-Lobster 更強。零遷移，零改寫。

**3. 計畫就是產品。**
Spec Squad 不是先寫程式碼。它先寫規格書，讓對手來挑戰，然後按規格書建構。計畫就是契約。

---

## 貢獻

歡迎 PR。貢獻前請先讀 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 授權

MIT — 詳見 [LICENSE](LICENSE)。
