# Clawd-Lobster

![Version](https://img.shields.io/badge/version-0.6.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

[English](README.md) · **繁體中文**

Clawd-Lobster 替 Claude Code CLI 加上每個工作區各自的 MCP 記憶伺服器、以 Claude Agent SDK 打造的四角色 Spec Squad、十一份 skill 資訊清單，以及跨機器的定時 git 同步。

**專案介紹頁：** https://teddashh.github.io/clawd-lobster/?lang=zh-TW

> **狀態：實驗性質，已停止維護**。2026 年 4 月 1 日到 9 日之間有 136 個 commit，之後只在 2026 年 10 月做過一次清理與安全性修正。沒有正式的 release，也沒有 PyPI 套件。套件版本是 0.6.0，詳見 [CHANGELOG.md](CHANGELOG.md) 與[現況與限制](#現況與限制)。

---

## 為什麼要做這個

新開的 Claude Code session 不會知道上一個 session 做了哪些決定，除非你把內容貼給它，或寫進 CLAUDE.md，而 CLAUDE.md 每台機器又各有一份。決策、還沒做完的 TODO、從失敗中學到的教訓，最後都散落在各個對話紀錄裡。由同一個 session 撰寫又自己核准的規格，會把漏洞原封不動帶進程式碼。

Clawd-Lobster 不取代 Claude Code。它透過 Claude Code 本來就有的擴充點（MCP 伺服器、CLAUDE.md、settings.json hook 與 Claude Agent SDK），在外圍加上記憶、經過審查的規格、排程與設定精靈。

- **只用 Claude Code CLI 與 Agent SDK**。沒有自己寫的 agent 迴圈，也不修改 Claude Code，所以 Claude Code 大部分的更新都不需要這裡跟著改。
- **小到讀得完**。Python、shell、PowerShell 與 JavaScript 加起來約 25,800 行，其中約 3,000 行是放在 `scripts/legacy/` 的舊版 Spec Squad。
- **在瀏覽器裡設定**。`clawd-lobster serve` 會打開設定精靈，Claude Code session 也能從終端機操作同一個精靈。

```
  You describe the project
       |
       v
  Discovery: Claude asks follow-up questions
       |
       v
  +--------------------------------------+
  |              SPEC SQUAD              |
  |                                      |
  |  [A] Architect   writes the spec     |
  |  [R] Reviewer    challenges it       |
  |  [C] Coder       builds from tasks   |
  |  [T] Tester      checks each item    |
  |                                      |
  |  Every turn is a fresh Agent SDK     |
  |  session. The Reviewer never sees    |
  |  the Architect's prompt and can      |
  |  only read files.                    |
  +--------------------------------------+
       |
       v
  Spec, code, and test results in the workspace
```

---

## 快速開始

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e ".[agent]"
clawd-lobster serve
```

`serve` 會在 127.0.0.1:3333 啟動儀表板，並自動用瀏覽器打開設定精靈（`--no-open` 不開瀏覽器，`--port` 改連接埠）。選好語言（英文、繁體中文、簡體中文、日文或韓文），接著完成四項基礎設定（語言、Claude Code 登入、GitHub Hub、工作區根目錄）和六個必要的 skill。[設定指南](docs/onboarding-guide.html)走的也是同樣的步驟。

Spec Squad 需要 `agent` 這組選用相依套件，也就是 `claude-agent-sdk`；只執行 `pip install -e .` 則會裝好其餘的一切。

### 只用終端機

```bash
clawd-lobster setup        # 終端機版設定
clawd-lobster squad start  # 在目前的資料夾執行 Spec Squad
```

### 安裝腳本

```powershell
# Windows
.\install.ps1
```

```bash
# macOS / Linux
chmod +x install.sh && ./install.sh
```

腳本分九個步驟：檢查必要工具、驗證身分、設定 Hub、寫入設定、安裝記憶伺服器、設定 CLAUDE.md 與 settings（附加內容到 CLAUDE.md 之前會先備份）、部署工作區、排程（每 30 分鐘的同步與 heartbeat）並登記這台機器，最後從舊環境搬移資料。

---

## 你會得到什麼

### 1. Spec Squad

你描述想做什麼，接下來交給四個角色。

**Architect** 寫出 OpenSpec 檔案，需求用 SHALL/MUST 描述並附上 Gherkin 情境。**Reviewer** 是另一個獨立的 session，看不到 Architect 收到的指示，也只能讀取檔案，負責挑戰這份規格。兩邊來回修改，直到 Reviewer 核准為止，最多五輪。第五輪結束後 Reviewer 仍未核准的話，規格還是會被核准，讓流程繼續，但會記錄成強制核准：`.spec-squad.json` 寫的是 `"approval": "round_limit"`，而不是 `"reviewer"`，回合紀錄裡會多一筆 `FORCED_APPROVAL`，終端機和網頁畫面也都會註明這是輪數上限造成的核准。接著 **Coder** 依 `tasks.md` 實作，**Tester** 逐條檢查需求。只有 Coder 和 Tester 能執行 shell 指令。

每個角色都在自己的脈絡裡工作：Reviewer 不會順著 Architect 的推理走，Tester 也不知道 Coder 抄了哪些捷徑。

兩種介面，同一套引擎：
- **網頁**：探索對話會一直追問，直到資訊足夠才開始，之後即時畫面會顯示每個階段與每一輪。
- **終端機**：輸入描述，按兩次 Enter 結束。規格審查完之後，開始實作前會先問你。

### 2. 不會忘記的腦袋：Thin Ledger

| 層 | 內容 | 角色 |
|----|------|------|
| **SQLite（the Ledger）** | 決策、TODO、稽核紀錄、salience 分數、來源資訊 | 營運紀錄，每個工作區一個資料庫 |
| **Git wiki（the Library）** | `knowledge/wiki/` 底下的 Markdown 頁面與索引 | 整理過的知識，人看得懂，透過 git 同步 |
| **Oracle（the Vault）** | embedding 與跨機器的語意搜尋 | 選用，需要 Oracle 資料庫和 embedding 端點 |

記憶伺服器用 FastMCP 寫成，提供 27 個工具（[skills/memory-server](skills/memory-server/README.md)）。每筆知識都帶著來源資訊（provenance）：來源 agent、信心分數，以及生命週期狀態（raw、extracted、synthesized、accepted 或 superseded）。

**三個操作讓它保持健康**：
- **Ingest（吸收）**：absorb skill 會讀取 repo、資料夾、檔案與網頁，把內容存成知識。
- **Query（查詢）**：`memory_search` 依 salience 排序，Oracle 搜尋沒有結果時會改用本機文字搜尋。
- **Lint（健檢）**：evolve-tick 會檢查每個 wiki 有沒有失效的索引連結、沒被索引到的頁面、超過 90 天沒更新的頁面，以及待審的修正。

**修正流程**：agent 不直接修改 wiki 頁面。`memory_propose_correction` 會提出一筆待審的質疑（如果有 `knowledge/.pending/` 資料夾，也會在裡面留一份筆記），所以有爭議的內容會經過處理，而不是被默默覆蓋。

被用到的項目 salience 會上升，閒置的則會衰減，所以重要的決策會留在搜尋結果前面。

*架構概念取自 [MemPalace](https://github.com/MemPalace/mempalace)（空間結構）與 [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)（ingest、query、lint）。只借用概念，兩者都沒有被當成相依套件安裝。*

### 3. Heartbeat

Heartbeat 靠作業系統的排程器（Task Scheduler、cron 或 launchd）每 30 分鐘跑一次，不是常駐的 daemon。它會用程式名稱替每個工作區找正在執行的 `claude`；找不到的話，就在那個工作區開一個終端機執行 `claude --resume`，這會開出 session 選單，而不是接回特定的 session。

### 4. 所有機器，一個腦袋

GitHub 是控制平面，git 是協定。設定流程會建立或加入一個私人 GitHub repo 當作你的 Hub。安裝腳本會排定每 30 分鐘執行一次 `sync-all`，對工作區根目錄底下的每個 git repo 執行 pull、commit 與 push。這樣一台機器學到的做法，其他機器在下次同步時就會拿到。要加入新機器，執行安裝腳本並加入現有的 Hub 即可。

### 5. 自我進化

evolve-tick 每兩小時執行一次（設定 evolve skill 時由儀表板登記排程：在你的 crontab 加上一行，其餘內容不動；Windows 上則是建立一個 Task Scheduler 工作）。它會收集各工作區最近完成的 TODO 與操作紀錄，請 Claude 把可以重複使用的做法存成 learned skill，接著讓沒用到的項目 salience 衰減，並檢查 wiki。改進的想法會寫成 `openspec/proposals/` 底下的提案檔並 commit 進 repo，等人審查。

---

## 儀表板

`clawd-lobster serve` 用 Python 標準函式庫在 127.0.0.1:3333 啟動 HTTP 伺服器。

- **設定精靈（Onboarding）**：每張卡片列出自己的步驟，相依的項目通過之前會保持鎖定。
- **工作區（Workspaces）**：列出每個工作區的路徑、領域、建立日期與目前的 Squad 階段，也可以在這裡建立新的工作區。
- **Skill**：用三個分頁（MCP Servers、Prompt Patterns、Cron Jobs）列出所有 skill，並標示 Always On、Enabled 或 Disabled。
- **憑證（Credentials）**：Claude Code、GitHub、OpenAI Codex、Google Gemini、Oracle Vault 與 Odoo。只有 Claude Code 和 GitHub 有登入檢查，Update 按鈕目前還沒有作用。
- **Spec Squad**：先是探索對話，之後是各階段與每一輪的即時畫面。

### Agent 引導式設定

這不是傳統的安裝程式。網頁儀表板和 Claude Code session 是**共同駕駛**：

```
網頁（視覺層）         +     Claude Code（對話層）
顯示 skill 卡片              解釋每個 skill 的用途
顯示設定進度                 回答你的問題
顯示設定表單                 執行安裝指令
即時更新                     讀取狀態，推進流程
```

兩邊都不是主控。它們透過同一個後端 API 提交意圖，一份控制權租約確保同一時間只有一方在操作。

> **安全提醒**：儀表板只監聽 127.0.0.1，而且每個請求在處理之前都要先通過檢查。Host 標頭必須是 `127.0.0.1:<port>` 或 `localhost:<port>`，用來擋下 DNS rebinding。帶有 Origin 標頭的請求必須來自儀表板本身。每個 POST 都要在 `X-Clawd-Token` 標頭附上這次執行專用的 token，讓其他網頁無法代替你送出請求（CSRF）。伺服器每次啟動都會產生新的隨機 token，放進它提供的頁面，並寫到 `~/.clawd-lobster/server-<port>.token`（只有你能讀取）給本機腳本使用，伺服器停止時會刪除這個檔案。沒通過檢查的請求會收到 403，CORS 預檢請求一律回 403，回應也不會帶任何 `Access-Control-*` 標頭。設定流程的 API 和以前一樣還需要 session token。這個 token 擋的是網頁，擋不了同一台機器上以你的身分執行的其他程式，所以用完還是請關掉 `clawd-lobster serve`。

---

## Skill 一覽

十一份 skill 資訊清單，分成四類，另外還有一個存放 learned skill 的資料夾。其中六個在設定時是必要的，其餘為選用。

| Skill | 類型 | 設定 | 用途 |
|-------|------|------|------|
| [memory-server](skills/memory-server/README.md) | MCP 伺服器 | 必要 | 27 個 MCP 工具，處理決策、知識、TODO、learned skill、稽核與搜尋 |
| [spec](skills/spec/README.md) | Prompt 模式 | 必要 | 建立工作區、產生 OpenSpec 文件，以及 Spec Squad 流程 |
| [absorb](skills/absorb/README.md) | Prompt 模式 | 必要 | 讀取 repo、資料夾、檔案與網頁存進記憶；設定好 Oracle 時改存進 Vault |
| [evolve](skills/evolve/README.md) | cron，每 2 小時 | 必要 | 檢視完成的 TODO 與最近的操作、儲存 learned skill、讓 salience 衰減、檢查 wiki |
| [heartbeat](skills/heartbeat/README.md) | cron，每 30 分鐘 | 必要 | 替沒有執行中 session 的工作區執行 `claude --resume` |
| [deploy](skills/deploy/README.md) | Prompt 模式 | 必要 | `/deploy` 會偵測技術堆疊，產生 dev、staging、prod 用的 Dockerfile、Compose 檔與 nginx 設定 |
| [migrate](skills/migrate/README.md) | Prompt 模式 | 選用 | 從 `~/.claude/`、`~/.openclaw/` 與 `~/.hermes/` 匯入記憶與設定 |
| [codex-bridge](skills/codex-bridge/README.md) | Prompt 模式 | 選用 | 把大量或可平行的工作，或第二輪審查，交給 OpenAI Codex CLI |
| [gemini-bridge](skills/gemini-bridge/README.md) | Prompt 模式 | 選用 | 遇到不確定或複雜的決策時，向 Gemini CLI 徵詢第二意見 |
| [notebooklm-bridge](skills/notebooklm-bridge/README.md) | Prompt 模式 | 選用 | 把工作區文件同步到 Google NotebookLM，產生簡報、資訊圖表、語音摘要與報告 |
| [connect-odoo](skills/connect-odoo/README.md) | 輪詢器 | 選用 | 透過 XML-RPC 連接 Odoo：6 個 MCP 工具，加上監看資料變動的輪詢器 |
| [learned](skills/learned/README.md) | 資料夾 | 自動 | evolve 存下來的做法 |

每個 skill 都有一份資訊清單（`skill.json`），記載說明、所需憑證與健康檢查；必要的 skill 還會列出設定步驟與相依項目。[scripts/skill-manager.py](scripts/skill-manager.py) 負責列出 skill，處理啟用、停用、設定、憑證與健康檢查，也能從登錄資料重建 `.mcp.json` 與 `settings.json`。

---

## 架構

```
Skills (the what)      ->  11 skill manifests (skill.json) with instructions
Tools (the how)        ->  27 MCP tools + Claude Code's own tools + the dashboard API
Hooks (the when)       ->  OS scheduler, git, PostToolUse and Stop hooks
Memory (the brain)     ->  SQLite ledger + git wiki + optional Oracle Vault
Operations (the cycle) ->  ingest, query, lint
Dashboard (the eyes)   ->  web UI at 127.0.0.1:3333
```

**站在巨人的肩膀上**。Clawd-Lobster 不重寫 Claude Code，而是照官方文件使用 Claude Code 自己的擴充點（MCP 伺服器、CLAUDE.md、hook、settings.json），所以 Claude Code 或模型改版時，沒有轉接層需要跟著更新。

- 追蹤的檔案：約 2.6 MB（程式碼、設定、文件）
- 程式碼：約 25,800 行 Python、shell、PowerShell 與 JavaScript
- 記憶伺服器：閒置時常駐記憶體約 90 MB（Python 3.14、FastMCP 3）
- 排程：由作業系統排程器執行，跑完就結束，沒有常駐的 daemon

檔案樹與執行細節請見 [ARCHITECTURE.md](ARCHITECTURE.md)。裡面有些數字沒有跟上程式碼，例如它寫 32 個 MCP 工具，伺服器實際上是 27 個。

---

## 指令參考

| 指令 | 用途 |
|------|------|
| `clawd-lobster serve` | 在 127.0.0.1:3333 啟動儀表板（`--port`、`--no-open`、`--daemon`） |
| `clawd-lobster setup` | 終端機版設定精靈 |
| `clawd-lobster workspace create <name>` | 建立工作區（`--domain`、`--description`、`--repo`、`--dry-run`） |
| `clawd-lobster squad start` | 在終端機執行 Spec Squad（`--workspace` 可以給名稱或路徑，預設是目前的資料夾） |
| `clawd-lobster status` | 顯示系統狀態 |

沒有 `clawd-lobster deploy` 這個指令；部署是 Claude Code 裡的 `/deploy` prompt 模式。

---

## 多機設定

```
  clawd-lobster (this repo, the generator)
       |
       |  install once
       v
  clawd-yourname (your private Hub on GitHub)
       |
       +-- Machine A: skills + memory + heartbeat
       +-- Machine B: skills + memory + heartbeat
       +-- Machine C: skills + memory + heartbeat
            |
            Synced through git every 30 minutes.
```

第一台機器建立 Hub，安裝腳本建議的名稱是 `clawd-` 加上你的使用者名稱。之後的每台機器都加入這個 Hub。

工作區清單 `workspaces.json` 屬於每台機器各自的狀態：這個 repo 不追蹤它，只附上 [workspaces.example.json](workspaces.example.json) 說明格式，你的私人 Hub 則會追蹤自己的那一份。會被推送出去的檔案與 commit 訊息，只會用 `~/.clawd-lobster/config.json` 裡的 `machine_id` 稱呼這台機器（安裝腳本預設建議一個隨機的 `machine-` 名稱），不會寫出它的主機名稱。

---

## 環境需求

- Python 3.10 以上（記憶伺服器需要 3.11 以上）
- 已安裝並登入的 Claude Code CLI（[安裝說明](https://code.claude.com/docs/zh-TW/setup)）
- Git 2.x
- GitHub 帳號與 gh CLI（用於 Hub）
- Node.js 為選用，必要工具檢查會列出它，但不強制安裝
- 選用：Oracle 資料庫與 embedding 端點（Vault 與向量搜尋）、OpenAI Codex CLI、Gemini CLI、可使用 NotebookLM 的 Google 帳號、Odoo 伺服器

---

## 現況與限制

實驗性質。2026 年 4 月 1 日到 9 日之間有 136 個 commit，之後只在 2026 年 10 月做過一次清理與安全性修正。沒有正式的 release。

**目前可用**
- `pip install -e .` 之後就有 `clawd-lobster` 指令，包含 serve、setup、workspace create、squad start 與 status
- 測試可以通過：83 個單元測試（設定流程、排程登記、儀表板的請求檢查與 Spec Squad 的核准紀錄），加上一支透過 HTTP API 跑完整流程的端對端腳本（2026 年 10 月在 Python 3.14 重新驗證過）
- 記憶伺服器只靠 SQLite 就能運作，文字搜尋依 salience 排序
- 提供 Windows（PowerShell）、macOS 與 Linux 的安裝腳本
- 終端機版的 Spec Squad 寫完規格會停下來，問過你才開始寫程式

**限制與尚未完成**
- 2026 年 4 月 9 日之後就沒有新功能，也沒有針對之後的 Claude Code 或 Agent SDK 版本驗證過
- 儀表板的 token 能擋下其他網頁，但同一台機器上以你的身分執行的任何程式都讀得到它
- 審查五輪後若 Reviewer 仍未核准，規格還是會被核准，網頁流程會直接進入實作；狀態檔、回合紀錄與兩種介面都會標明這是輪數上限造成的強制核准
- 每 30 分鐘的同步會對工作區根目錄底下的每個 git repo 自動 commit 並 push，新的 Markdown、JSON、YAML、HTML 與腳本檔也會一起加進去，不想被推上去的東西請放在這個資料夾以外
- Heartbeat 只用程式名稱判斷 session 是否還在執行，重新開啟時也只是執行單純的 `claude --resume`
- Spec Squad 需要 `[agent]` 選用相依套件；向量搜尋與 Vault 需要 Oracle 資料庫；記憶伺服器需要 Python 3.11 以上

---

## 設計理念

**1. 放大，不是重建**。
Claude Code 負責 agent 的工作。這裡只在外圍裝上神經系統，不去動大腦。

**2. 巨人長高，你也跟著長高**。
這裡完全不修改 Claude Code，所以它更新時，這裡很少需要跟著改。

**3. 計畫就是產品**。
Spec Squad 不先寫程式碼。它先寫規格，交給另一個 session 審查，再照著規格實作。規格就是契約。

---

## 貢獻

歡迎 PR。貢獻前請先讀 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 其他語言

[简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)。這些翻譯描述的是較早的版本，最新內容以英文 README、這份中文 README 與[專案介紹頁](https://teddashh.github.io/clawd-lobster/?lang=zh-TW)為準。

## 授權

MIT，詳見 [LICENSE](LICENSE)。
