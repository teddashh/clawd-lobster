🌐 [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [**日本語**](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

<p align="center">
<strong>結局、最高のものを使うことになる。</strong><br>
<em>究極のエージェント体験 — 最軽量、厳選された機能、最大のパフォーマンス。</em>
</p>

<p align="center">
<sub>Webガイド付きセットアップ。多層メモリ。マルチエージェント共有ナレッジ。自由な進化。</sub>
</p>

---

## Clawd-Lobster とは？

Claude Codeは頭脳。Clawd-Lobsterは神経系統。

Claude Codeは現時点で最も優れたコーディングエージェントですが、セッション間ですべてを忘れ、1台のマシンでしか動作せず、スキル管理もありません。Clawd-Lobsterは不足しているものを的確に補います：永続メモリ、マルチマシンオーケストレーション、厳選されたスキル、そして自己進化。それ以上でも以下でもありません。

**Clawd-Lobsterはジェネレーターです。** 一度実行するだけで、あなた専用の**Hub** — プライベートGitHubリポジトリがコマンドセンターになります。Hubがすべてのマシン、ワークスペース、メモリ、スキルを管理します。

```
  clawd-lobster (このリポジトリ — ジェネレーター)
       │
       │  install.ps1 を一度実行
       │
       ▼
  clawd-yourname (あなたのプライベートHub — あなた用に生成)
       │
       │  これが日常的に実際に使うもの
       │
       ├── Machine A ── Claude Code + skills + memory
       ├── Machine B ── Claude Code + skills + memory
       └── Machine C ── Claude Code + skills + memory
            │
            すべて接続。すべて知識を共有。
            すべてheartbeatで常時稼働。
```

GitHubがコントロールプレーン。Gitがプロトコル。すべての状態 — スキル、ナレッジ、ワークスペース登録、heartbeatステータス — がgitに格納され、自動的に同期されます。

**ランタイムフットプリント：25 MB RAM、672 KBディスク。** 1つのPythonプロセス（MCP Memory Server）とSQLite。その他はOSスケジューラで実行→終了するか、ブラウザ上で動作します。ポーリングゼロ、デーモンゼロ、肥大化ゼロ。

```
Disk: 672 KB (コード + 設定、.gitと画像アセットを除く)
RAM:  ~25 MB (MCPサーバー、唯一の常駐プロセス)
CPU:  0% アイドル (ポーリングなし、デーモンなし — OSスケジューラが起動を担当)
```

---

## クイックスタート

### 最初のマシン（Hubを作成）

**Windows**
```powershell
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
.\install.ps1
# 4つの質問に答える → プライベートHubが作成される → すべてセットアップ完了
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

### セットアップの仕組み

インストーラーが4つの質問をします。それだけです。残りはすべて自動です。

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
             ▼  続いて9つの自動化ステップ
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

### 9つのステップの内容

| ステップ | アクション | 時間 |
|------|--------|------|
| 1 | 前提条件のチェック（Node、Python、Git） | 5秒 |
| 2 | Claude Code + GitHubの認証（OAuthクリック2回） | 30秒 |
| 3 | **Hubを作成**（プライベートリポジトリ）または既存をクローン | 10秒 |
| 4 | 設定の書き込み | 5秒 |
| 5 | MCP Memory Serverのインストール（21ツール） | 10秒 |
| 6 | Claude Codeの設定（CLAUDE.md + .mcp.json） | 5秒 |
| 7 | ワークスペースのデプロイ（リポジトリをクローン、memory.dbを初期化） | 場合による |
| 8 | スケジューラ + heartbeatの登録 | 5秒 |
| 9 | 既存システムの吸収（選択した場合） | 場合による |

| プラットフォーム | 同期 | Heartbeat |
|----------|------|-----------|
| Windows | Task Scheduler (30分) | Task Scheduler (30分) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | Container lifecycle | Container lifecycle |

**必要な認証情報はOAuthクリック2回だけ。** Oracle L4を使用する場合を除き、APIキーは不要です。

### 後からマシンを追加

HubがすでにGitHub上にあれば、マシンの追加はさらに簡単です：

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

## Chapter 1：メモリ — エージェントは記憶する

なぜ重要か：ほとんどのAIエージェントは毎回ゼロからセッションを開始します。同じミスを繰り返し、コンテキストを学び直し、時間を無駄にします。

### 4層メモリシステム

| レイヤー | 内容 | 速度 | スコープ |
|-------|------|-------|-------|
| **L1.5** | CC auto-memory（ネイティブ） | 即時 | 現在のプロジェクト |
| **L2** | SQLite + 24のMCPツール | ~1ms | ワークスペースごと |
| **L3** | Markdownナレッジベース | ~10ms | gitで共有 |
| **L4** | Cloud DB（オプション） | ~100ms | ワークスペース横断 |

### Salienceエンジン

重要なメモリは浮上し、古くなったメモリは沈みます：
- アクセスごと：salienceが+5%
- 手動強化：+20%ブースト（上限2.0x）
- 30日間未アクセス：-5%/日の減衰（下限0.01、削除はされません）

**CJK対応トークン推定** — 多言語ワークロード向けの正確なコンパクション・タイミング。

### 実際の動作

メモリは受動的なストアではありません — エージェントの動作に能動的に影響を与えます。

```
あなたが決定を下す
  → memory_record_decision("chose SQLite over Postgres", "local-first, no server needed")

次のセッション開始
  → ブートプロトコルが重要な決定 + ナレッジをロード
  → Claudeがその決定とその理由を覚えている

30日後
  → 重要な決定は依然として高salience（頻繁にアクセスされる → ブースト）
  → 些末なコンテキストは自然に減衰（ただし削除されることはない）
```

すべてのトラジェクトリは記録されます。すべてのワークスペースは共有されます。エージェントたちは共に成長します。知識は蓄積されます。作業は決して失われません。

---

## Chapter 2：ワークスペース — エージェントの作業場

なぜ重要か：構造化された作業場所がなければ、エージェントはコンテキストを混同し、プロジェクトを混乱させ、マシン間でナレッジを共有できません。

ワークスペースはメモリ、スキル、specサポートを備えたプロジェクトディレクトリです。すべてのワークスペースはgitリポジトリです（通常はGitHub上のプライベートリポジトリ）。

### ワークスペースの作成

2つの方法：

1. **`/spec new`** — 完全なspecを伴うガイド付き作成（推奨）。詳細は[Chapter 4](#chapter-4spec--エージェントの計画方法)を参照。
2. **`workspace-create.py`** — specなしのクイック作成：

```powershell
.\scripts\new-workspace.ps1 -name "my-api"
# フォルダ、memory.db、CLAUDE.md、GitHubリポジトリを作成 — 完了。
```

### ワークスペース構造

```
my-project/
├── CLAUDE.md              ← プロジェクト固有の指示
├── .claude-memory/
│   └── memory.db          ← L2メモリ (SQLite)
├── knowledge/             ← L3ナレッジ (git同期)
├── skills/learned/        ← 自動生成されたスキル
├── openspec/              ← specアーティファクト (/spec使用時)
│   ├── project.md
│   ├── changes/
│   └── specs/
└── .blitz-active          ← blitz実行中に存在
```

### ワークスペースの有効化と同期

```
~/Documents/Workspace/
├── my-api/          ← 登録済み、30分ごとに同期
├── data-pipeline/   ← 登録済み、30分ごとに同期
└── random-notes/    ← gitリポジトリではない、同期でスキップ
```

- すべてのアクティブなワークスペースは30分ごとにgitで同期されます
- Web UIのワークスペースタブでワークスペースのON/OFFを切り替えます
- 非アクティブなワークスペースは同期を停止しますがデータは保持されます
- スケジューラがワークスペースルート配下のすべてのgitリポジトリを自動同期します

### マルチマシン共有

これは単なる1つのエージェントではありません。フリートです — そしてすべてが同じ頭脳を共有しています。

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

- **L2** はローカルに保持（高速、ワークスペースごと）— 各エージェントが独自のキャッシュを持ちます
- **L3** はgitで同期 — すべてのエージェントが同じナレッジベースを読み書きします
- **L4** はすべてを統合 — ワークスペース横断検索、監査証跡、完全な履歴
- **新しいエージェントが参加？** `git clone + install.ps1` — 蓄積されたすべての知識を即座に継承します

### 常時稼働 — Heartbeat

エージェントは決して死にません。OSスケジューラが30分ごとにチェック：各ワークスペースセッションは生きているか？そうでなければ、`claude --resume`で復活させます — 完全なコンテキストが復元されます。

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

- **ターミナルが開いている** — セッション稼働中、エージェントは完全なコンテキストを持ち、24/7で動作
- **ターミナルが閉じた** — heartbeatが検知し、自動的に復活
- **すべてのセッション** — Claude Code Remoteで任意のデバイスから閲覧可能
- **カスタムデーモンなし** — OSスケジューラがウォッチドッグ。クラッシュしない。メンテナンスゼロ。

### スケジュール自動化

OSレベルのスケジューラ（Windows Task Scheduler / cron / launchd）— Claude Codeが起動していなくても実行されます：

- **Heartbeat** — すべてのワークスペースセッションが稼働し続けることを保証（停止していれば復活）
- **Git同期** — 30分ごとにすべてのリポジトリをpullおよびpush
- **Salience減衰** — 日次のメモリ重要度調整
- **クライアントステータス** — 各マシンのセッション、最終heartbeat、デプロイ済みワークスペースを追跡

---

## Chapter 3：スキル — エージェントにできること

なぜ重要か：Claude Codeにはビルトインスキルがありますが、独自のスキルを追加したり、変更したり、チームと共有したりすることはできません。スキルはあなたの競争優位性です。

スキルは自己完結型のモジュールです。AIエージェント用のChrome拡張機能のようなものです。

### 3つのスキルソース

| タブ | 内容 | 切り替え可？ |
|---|---|---|
| **Claude Native** | ビルトイン：`/batch`、`/loop`、`/simplify`、`/compact`など | スキル：可（権限経由）。コマンド：読み取り専用。 |
| **Clawd-Lobster** | マネージド：memory、heartbeat、evolve、absorb、spec、connect-odoo | 可 — フルライフサイクル |
| **Custom / Hub** | 独自 + ClawHubからダウンロードしたコミュニティスキル | 可 — フルライフサイクル |

1つの統一ビュー。3つのソース。システム上のすべてのスキル — Anthropicからのものも、Clawd-Lobsterからのものも、あなた自身のものも — 1か所で表示・管理できます。

### コアスキル（ロック — 無効化不可）

| スキル | 機能 | ロックの理由 |
|---|---|---|
| Memory Server | 28ツールMCPメモリ + SQLite | メモリなし = エージェントなし |
| Heartbeat | OSスケジューラによるセッションキープアライブ | heartbeatなし = セッションが死ぬ |
| Evolve | 自己進化 + TODO処理 | コア差別化機能 |
| Absorb | あらゆるソースからのナレッジ取り込み | コア学習能力 |
| Spec | ガイド付きプランニング + blitz実行 | コア開発ワークフロー |

### オプショナルスキル

| スキル | 機能 | デフォルト |
|---|---|---|
| Migrate | 他のAIセットアップからのインポート | 有効 |
| Connect-Odoo | Odoo ERP連携（XML-RPC） | 無効 |
| Codex Bridge | OpenAI Codexに作業を委任（worker + critic） | 無効 |
| NotebookLM Bridge | Google NotebookLMによる無料RAG + コンテンツエンジン | 無効 |

### スキル管理

すべてのスキルは`skill.json`マニフェストを持つ自己完結型モジュールです。**Web UI**または**CLI**で管理します。

**Web Dashboard** — `webapp/index.html`を開く：
- カードグリッドにON/OFFトグル、ステータスインジケーター、カテゴリフィルター、検索
- インライン設定 — スキルごとに設定と認証情報を編集
- ヘルスチェック — 有効なすべてのスキルに緑/黄/赤のステータスを表示

**CLI管理ツール：**

```bash
python scripts/skill-manager.py list                     # すべてのスキルを一覧表示
python scripts/skill-manager.py enable connect-odoo      # スキルを有効化
python scripts/skill-manager.py disable connect-odoo     # スキルを無効化
python scripts/skill-manager.py status                   # 詳細ステータス
python scripts/skill-manager.py config connect-odoo      # 設定の表示/編集
python scripts/skill-manager.py credentials connect-odoo # 認証情報の管理
python scripts/skill-manager.py health                   # すべてのヘルスチェックを実行
python scripts/skill-manager.py reconcile                # .mcp.json + settings.json を再生成
```

### 独自スキルの追加

1. `skills/my-skill/skill.json`を作成 — マニフェストがすべてを宣言：

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

2. スキルを実装（MCPサーバー、スクリプト、またはSKILL.md）
3. `skill-manager.py reconcile`を実行 — 自動的に登録し、`.mcp.json` + `settings.json`を更新

**スキルはたった3つの設定エントリです。** SDKなし。プラグインAPIなし。フレームワークロックインなし。マニフェスト**が**コントラクトです。

---

## Chapter 4：Spec — エージェントの計画方法

なぜ重要か：計画なしの自律実行は、ランダムなコード生成に過ぎません。Spec駆動開発はClaudeに従うべきブループリントを与えます。

OpenSpec方法論に基づいています。Claudeがプランニングをガイドし、その後自律的に実行します。

### フロー

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

### 3W1H標準

すべてのアーティファクトはWhy、What、Who、How — それぞれ適切なレベルで従います：

| アーティファクト | レベル |
|---|---|
| project.md | 広範なコンテキストキャプチャ |
| proposal.md | スコープ定義 |
| design.md | アーキテクチャのブループリント |
| specs/ | テスト可能な要件（SHALL/MUST + Gherkin） |
| tasks.md | 実行計画（フェーズ分け、ファイルパス参照付き） |

プランニングから意思決定、ログ、アーカイブまで、同じ標準が一貫して適用されます。

### Blitzモード

フルスピードの自律実行。Specが計画 — 質問なし、実行あるのみ。

- **ブランチ分離** — すべての作業は`blitz/v1`で行われ、mainは検証まで保護
- **フェーズコミット** — 各フェーズ完了後に`git commit`
- **進化の一時停止** — `.blitz-active`マーカーがevolve-tickにこのワークスペースをスキップするよう通知
- **委任マーカー** — `[codex]`プレフィックスのタスクは外部実行用にスキップ
- **Blitz完了後** — mainにマージ、specをナレッジとして保存、次のステップを提案

### バリデーション

- 各アーティファクト完了後にセルフバリデーションを実行（proposal、design、specs、tasks）
- 要件はSHALLまたはMUSTを使用 — "should"、"could"、"might"は不可
- すべての要件に少なくとも1つのGherkinシナリオ
- すべてのタスクにファイルパスが含まれ、5-30分で完了できる範囲
- アーティファクトDAGは厳格：project → proposal → design → specs → tasks

### コマンド

| コマンド | 機能 |
|---|---|
| `/spec new` | ガイド付きワークスペース + spec作成 |
| `/spec:status` | 進捗表示（フェーズごとにプログレスバー付き） |
| `/spec:add "feature"` | 既存specへの追加（差分操作） |
| `/spec:blitz` | blitz実行の開始/再開 |
| `/spec:archive` | 完了した変更のアーカイブ + ナレッジとして保存 |

---

## Chapter 5：進化 — エージェントの改善方法

なぜ重要か：v1は始まりに過ぎません。自分の作業から学べないエージェントは、成長が止まるエージェントです。

v1が完成した後、エージェントは自動的に改善し続けます。

### 進化ループ

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

### 3段階コンテンツパイプライン

Claude、Codex、Geminiによる3者間AIディベートから、コンテンツ生成パイプラインが確立されました：

1. **リサーチ** — ソースを収集し、コンテキストを吸収し、重要なインサイトを抽出
2. **ディベート** — 複数のAI視点がコンテンツに挑戦し、精製
3. **生成** — NotebookLMを通じて最終アウトプット（スライド、インフォグラフィック、ポッドキャスト、動画、クイズ）

### Absorb（吸収）

何でも投入できます — フォルダ、GitHubリポジトリ、URL。Claudeが見つけたものすべてを自動的に分類します：

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

パーサースクリプトは不要です。Claude Code**がそのまま**パーサーです — どんなフォーマットでも読み取り、セマンティクスを理解し、重要なものを保存します。3つのスキャン深度：

| 深度 | 内容 |
|---|---|
| `shallow` | README、CLAUDE.md、トップレベルの設定ファイル |
| `normal` | shallowの全部 + 主要なソースファイル、スキル定義、重要なドキュメント |
| `deep` | 完全なコードベース分析 — すべてのソースファイル、テスト、CI設定、スクリプト |

項目はナレッジ（事実、アーキテクチャ）、決定（教訓、落とし穴）、スキル（再利用可能なパターン）、TODO（アクションアイテム）に分類されます。

### 進化（自動）

2時間ごとに、`evolve-tick.py`が保留中のTODOを1つ選び、隔離されたgit worktreeで作業します。主要な特性：

- **1回のtickにつき1つのTODO** — シンプルかつ安全に
- **自動マージなし** — すべての作業は`evolve/<id>`ブランチでレビュー待ち
- **学習したスキルは永続化** — データベースとgit同期されたスキルファイルの両方に保存
- **有効性の追跡** — 使用ごとに+2%、改善ごとに+10%、実証済みスキルのスコアは2.0x以上
- **エージェント間共有** — Agent Aで学習したスキルはgit同期を通じてAgent Bでも利用可能
- **自然な引退** — 90日以上使用されていないスキルは潜在的に陳腐化したものとしてフラグ
- **知識の複利効果** — あるワークスペースでの判断が別のワークスペースの作業に活かされ、解決済みの問題は二度と解き直す必要がない

### Blitz vs 進化

| | Blitz | 進化 |
|---|---|---|
| タイミング | specからv1を構築 | v1以降の改善 |
| 速度 | すべてのタスク、ノンストップ | 2時間ごとに1つのTODO |
| スコープ | プロジェクト全体 | 個別の改善 |
| ブランチ | `blitz/v1`（終了時にマージ） | `evolve/<id>`（個別にレビュー） |
| 自動マージ | あり（blitzブランチ内） | なし — 人間がレビュー |

---

## アーキテクチャ

内部構造を理解したいエンジニア向けです。

### 内部の仕組み

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

### 実際に動いているものは？

リポジトリ全体は約~13K行ですが、大部分はセットアップファイル、ドキュメント、Claudeが読むための指示です。エージェントが作業中に実際にメモリを占有しているのは：

| レイヤー | 内容 | 行数 | RAM | タイミング |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (28 tools + SQLite) | ~1,400 | ~25 MB | 常時 |
| **Runtime** | Odoo Connector (if enabled) | ~280 | ~22 MB | 有効時 |
| **Cron** | evolve-tick (TODO processor) | ~465 | ~20 MB peak | 2時間ごと、実行後終了 |
| **Cron** | heartbeat + sync | ~300 | ~5 MB peak | 30分ごと、実行後終了 |
| **Static** | Web UI (browser renders it) | ~1,900 | 0 on server | オンデマンド |
| **Setup** | Installers, workspace-create, skill-manager | ~2,800 | 0 | 一度だけ実行 |
| **Docs** | SKILL.md files, README, CHANGELOG | ~3,500 | 0 | Claudeがオンデマンドで読取 |
| **Config** | skill.json manifests, templates | ~900 | 0 | 起動時に読取 |

**常駐フットプリント：1つのPythonプロセス（~25 MB）+ SQLite。** その他は実行後終了（cronスクリプト）、ブラウザ内（Web UI）、またはClaudeがコンテキストを必要とするときに読むだけのファイルです。

### Claude Codeとの関係

他のフレームワークはClaudeをゼロから再構築し、実際の思考にはClaudeのAPIを呼び出します：

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

私たちはClaudeのAPIを呼び出しません。OAuthトークンを管理しません。レートリミットを処理しません。私たちがスケジュールするのは**Claude Code自体** — Anthropicが構築し、配布し、メンテナンスするツールです。Anthropicが改善すれば、私たちも高速化します。APIが変わっても、影響ありません。

他のフレームワークは**他人の車の**リモコンを作っています。私たちは**車の中に**座っています。

### GitHubとの関係

GitHubはすべてのコントロールプレーンです：

- **Hubリポジトリ** — あなたのプライベートコマンドセンター
- **ワークスペースリポジトリ** — 各プロジェクトはプライベートリポジトリ
- **Git同期** — ナレッジ、スキル、ステートが30分ごとに同期
- **Heartbeatステータス** — マシンの稼働状況をgitにプッシュ
- **Specアーティファクト** — ワークスペースリポジトリにコミット

### なぜ独自のエンジンを作らないのか？

他のフレームワークはAIエージェント全体をゼロから再構築します — 30万行のコード、カスタムエージェントループ、カスタムツールシステム、すべてカスタム。Anthropicがより良いモデルをリリースすると、アダプターの書き直しに奔走します。

**Clawd-LobsterはClaude Codeと競合しません。Claude Codeを補完します。**

私たちはClaude Code — 世界で最も先進的なコーディングエージェント — から始め、不足しているものだけを追加します：永続メモリ、マルチエージェントオーケストレーション、厳選されたスキル。それ以上でも以下でもありません。

> *ゼロの肥大化。ゼロの書き直し。純粋なClaude Codeを、増幅する。*

### 設計哲学

#### 1. 最高のエージェントはすでに存在する。それを使え。

Claude Codeは世界最大のAI安全性研究機関が支えています。エージェントループ、ストリーミング、パーミッション、ツールシステムには数百万時間のエンジニアリングが注ぎ込まれています。それをゼロから再構築するのは野心ではありません — 無駄です。**巨人の肩の上に立ちましょう。**

#### 2. 少ないほど良い。はるかに良い。

フレームワークのコードの一行一行がメンテナンスが必要な一行です。Clawd-Lobsterが約2,000行なのは、Claude Codeのネイティブ拡張ポイント（MCP、hooks、CLAUDE.md）がすでに最高のプラグインシステムだからです。**3つの設定エントリ = 1つのスキル。SDKゼロ。**

#### 3. 忘れるエージェントは失敗するエージェントだ。

ほとんどのAIエージェントは毎回ゼロからセッションを始めます。同じミスを繰り返し、コンテキストを学び直し、時間を無駄にします。Clawd-Lobsterの4層メモリとsalience追跡により、**重要なものは浮上し、ノイズは消え、クリティカルなものは決して失われません。**

#### 4. エージェントはどこへでもついてくるべきだ。

1台のコンピュータ？問題ありません。3台のマシン？すべてが同じ頭脳を共有すべきです。GitHubをコントロールプレーンに、git同期をプロトコルに。**2分でマシンを追加。インフラゼロ。**

#### 5. 常に最新の波に乗れ。

AnthropicがOpus 4.7、1Mコンテキスト、新しいツールをリリースしたら — 即座に手に入ります。アダプターの書き直しなし。バージョン固定なし。コミュニティパッチ待ちなし。**Claude Codeを使う最高のタイミングは昨日でした。次に良いタイミングは今です。**

#### 6. スケジュールできるものは自作しない。

他のフレームワークはカスタムデーモンを書いてエージェントを24/7で実行します。私たちは`cron` + `claude --resume`を使います。他のフレームワークはOAuthトークンを管理してClaudeのAPIを呼び出します。私たちはユーザーに`claude login`を1回打ってもらうだけです。**あなたが書く認証コードの一行一行が、プロバイダーが変更したときに壊れ得る一行です。書かなかった一行は、壊れ得ない一行です。** OSスケジューラは1970年代から安定稼働しています。あなたのカスタムデーモンは先週の火曜日に書かれたものです。

#### 7. 巨人が背を伸ばせば、あなたも伸びる。

Claude Code内部にはメモリ統合（autoDream）、常時稼働エージェント（KAIROS）、マルチエージェント調整（Coordinator Mode）、複雑な計画立案（ULTRAPLAN）のシステムがあります。一部はライブ、一部はfeature flag背後。私たちは2K行で同等の機能のほとんどを構築済みです。

しかし重要なのは：**Anthropicがこれらの機能をネイティブでリリースしたとき、私たちは書き直しません — 引退させます。** KAIROSがライブになったら？heartbeatが優雅に身を引きます。autoDreamが改善されたら？salienceエンジンと共存します。Coordinator Modeがリリースされたら？evolve-tickがそれを使います。

他のフレームワークはClaude Codeと競合します。私たちは補完します。Claude Codeが機能を追加するとき、彼らは書き直す必要があります。私たちはコードを削除する機会を得ます。**私たちのコードベースは時間とともに縮小し、彼らのは膨張します。**

### プロジェクト構成

```
clawd-lobster/
├── skills/                          スキルモジュール（各skill.jsonマニフェスト付き）
│   ├── memory-server/               24ツールMCPメモリ + salience + 進化
│   │   ├── mcp_memory/              Python package (pip install -e .)
│   │   └── skill.json               Manifest
│   ├── connect-odoo/                Odoo ERP連携 (XML-RPC + poller)
│   │   ├── connect_odoo/            MCP server + poller
│   │   └── skill.json               Manifest
│   ├── evolve/                      自己進化prompt pattern
│   │   └── skill.json               Manifest
│   ├── heartbeat/                   セッションキープアライブ (cron)
│   │   └── skill.json               Manifest
│   ├── absorb/                      あらゆるソースからのナレッジ取り込み
│   │   └── skill.json               Manifest
│   ├── spec/                        ガイド付きプランニング + blitz実行
│   │   └── skill.json               Manifest
│   ├── codex-bridge/                OpenAI Codexに作業を委任
│   │   └── skill.json               Manifest
│   ├── notebooklm-bridge/           NotebookLMによる無料RAG + コンテンツエンジン
│   │   └── skill.json               Manifest
│   ├── migrate/                     既存セットアップからのインポート
│   │   └── skill.json               Manifest
│   └── learned/                     経験から自動生成されたスキル
│
├── scripts/
│   ├── skill-manager.py             スキル管理CLI
│   ├── sync-all.ps1                 Windows: 自動git同期 + 減衰
│   ├── sync-all.sh                  Linux/macOS: 自動git同期 + 減衰
│   ├── heartbeat.ps1                Windows: セッションキープアライブ
│   ├── heartbeat.sh                 Linux/macOS: セッションキープアライブ
│   ├── new-workspace.ps1            ワークスペース + GitHubリポジトリ作成
│   ├── workspace-create.py          自動ワークスペース作成
│   ├── validate-spec.py             Specアーティファクトのハードバリデーション
│   ├── setup-hooks.sh               git pre-commit hooksのインストール (Unix)
│   ├── setup-hooks.ps1              git pre-commit hooksのインストール (Windows)
│   ├── evolve-tick.py               パターン抽出 + 提案 + salience減衰
│   ├── notebooklm-sync.py           ワークスペースドキュメントをNotebookLMに自動プッシュ
│   ├── init_db.py                   メモリデータベース初期化
│   └── security-scan.py             5ツールセキュリティスキャナー
│
├── templates/                       設定テンプレート（シークレットなし）
│   ├── global-CLAUDE.md
│   ├── workspace-CLAUDE.md
│   ├── mcp.json.template
│   └── settings.json.template
│
├── webapp/                          スキル管理Dashboard
│   └── index.html                   3タブUI：Skills + Setup + Settings
│
├── knowledge/                       共有ナレッジベース（git同期）
├── soul/                            エージェントのパーソナリティ（オプション）
├── workspaces.json                  ワークスペースレジストリ
├── install.ps1                      Windowsインストーラー（4フェーズ）
├── install.sh                       Linux/macOSインストーラー（4フェーズ）
├── Dockerfile                       Docker build
├── docker-compose.yml               Docker Compose設定
├── LICENSE                          MIT
└── README.md
```

---

## 比較

| | Claude Code（素） | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| エージェントエンジン | Anthropic | カスタム（300K LOC） | カスタム（50K LOC） | **Anthropic（ネイティブ）** |
| 認証モデル | 人間がログイン | OAuth/APIキー | APIキー | **人間が一度ログイン** |
| コストモデル | サブスクリプション | トークン課金API | トークン課金API | **サブスクリプション（定額）** |
| 常時稼働 | なし | カスタムデーモン | カスタムデーモン | **OSハートビート + 自動復活** |
| 永続メモリ | なし | ハイブリッド検索 | FTS5 + LLM | **4層 + salience** |
| マルチエージェント共有メモリ | なし | なし | なし | **あり（git同期）** |
| スキル管理 | N/A | CLIのみ | 手動 | **Web UI + CLI + マニフェスト** |
| エージェント進化 | なし | なし | セルフインプルービングスキル | **あり（24 MCPツール）** |
| マルチマシン | なし | なし | なし | **あり（MDMスタイル）** |
| セッション管理 | 手動 | Gatewayプロセス | 手動 | **全セッション自動復活** |
| オンボーディング | 手動 | 複雑 | 中程度 | **Webウィザード、5言語** |
| 自動アップグレード | あり | なし | なし | **あり** |
| コードベースサイズ | 0 | ~300K LOC | ~50K LOC | **~2K LOC** |
| Anthropic API変更 | 透過的 | 破壊的 | 破壊的 | **透過的** |
| 監査証跡 | なし | セキュリティ監査 | なし | **完全（すべてのアクション）** |
| スキルインストール | — | Plugin SDK | 3ファイル変更 | **1マニフェスト + reconcile** |

---

## ロードマップ

**スキル**
- [x] Odoo ERP Connector — XML-RPC連携 + poller (v0.4.0)
- [x] Codex Bridge — OpenAI Codexに作業を委任、worker + criticロール (v0.5.0)
- [x] NotebookLM Bridge — Google NotebookLMによる無料RAG + コンテンツエンジン (v0.5.0)
- [x] Spec駆動開発 — OpenSpec方法論によるガイド付きプランニング (v0.5.0)
- [ ] SearXNG — プライベートなセルフホスト型Web検索、データがネットワーク外に出ない
- [ ] Docker Sandbox — 信頼できないオペレーション用の隔離されたコード実行環境
- [ ] Browser Automation — Playwrightを活用したWebインタラクション

**プラットフォーム**
- [x] Linuxインストーラー（bash）+ macOSインストーラー (v0.3.0)
- [x] スキル管理Dashboard — Web UI + CLIでスキルのフルライフサイクル管理 (v0.4.0)
- [x] スキルマニフェストシステム — `skill.json`に設定、認証情報、ヘルスチェック (v0.4.0)
- [ ] Supabase L4 — ワンクリックのクラウドデータベース（Oracle wallet不要）

**進化**
- [x] 進化ループ + 提案 — evolveがgit同期された提案を生成、直接TODOではない (v0.5.0)
- [ ] スキルマーケットプレイス — コミュニティ貢献のスキル、ワンクリックインストール
- [x] 自動スキル生成 — エージェントが成功パターンから学習 (v0.3.0 evolve skill)
- [ ] チームモード — ロールベースアクセス制御付きマルチユーザー共有ワークスペース
- [ ] エージェント間委任 — エージェントが互いにタスクを割り当て

---

## FAQ

### 「これってただのClaude Codeのラッパーでは？」

はい。それが狙いです。

Claude Codeは現時点で最も優れたコーディングエージェントです — Anthropicの数百万時間のエンジニアリングに支えられています。OpenClawはエンジンをゼロから再構築します（30万行）。Hermesもまた再構築します（5万行）。私たちは不足分を追加し（2千行）、最高のエンジンを保持します。

Anthropicが次のブレイクスルーをリリースしたとき、私たちは即座に恩恵を受けます。彼らはアダプターの書き直しに追われます。

### 「でも他のエージェントは24/7で動いて学習し続けるのでは？」

私たちもそうです。スケジューラは30分ごとにナレッジを同期します。メモリはsalience減衰で日々自然に進化します。学習されたスキルはgitを通じてすべてのマシンに伝播します。**エージェントが常時稼働していなくても、知識は成長し続けます。**

heartbeatがセッションを常に生かします：ターミナルが閉じたら、OSスケジューラが検知して`claude --resume`で復活 — 完全なコンテキストが復元されます。カスタムデーモンは不要。Claude Codeが常にオン。トークン課金APIフレームワークとの24/7の扱いの違いについては[アーキテクチャ](#claude-codeとの関係)セクションを参照してください。

### 「他のエージェントにもheartbeatと時間認識がある」

私たちにもあります — ただしよりスマートに。カスタムデーモンプロセスを実行する代わりに、OSスケジューラ（Task Scheduler / launchd / cron）をheartbeatとして使用します。30分ごとにチェック：セッションは生きているか？Git同期は必要か？Salience減衰の時間か？クライアントステータスは？すべて処理済み。OSスケジューラはクラッシュせず、デバッグ不要で、アイドル時にトークンを消費しません。Claude Codeがネイティブの24/7モード（KAIROS — コードベースに存在）をリリースすれば、無料で手に入ります。コード変更ゼロ。詳細は[Chapter 2](#常時稼働--heartbeat)を参照。

### 「Claude Codeにはすでにビルトインスキルがある。なぜもっと必要？」

Claude Codeには`/commit`、`/review-pr`、`/init`などのスキルが内蔵されています。良いものです。しかし**クローズド**でもあります — Anthropicが機能、動作、変更のタイミングを決定します。独自のスキルを追加できません。変更もできません。チームと共有もできません。

それはスマートフォンの内蔵アプリ。Clawd-LobsterはApp Storeです。

| | Claude Codeビルトイン | **Clawd-Lobsterスキル** |
|---|---|---|
| 作成者 | Anthropic | あなた、あなたのチーム、コミュニティ |
| 管理者 | Anthropic | あなた |
| 変更可能か | 不可 | 可 — あなたのコード |
| 追加可能か | 不可 | 可 — `skill.json` + 実装 |
| 共有可能か | 不可 | 可 — GitHubやClawHubにプッシュ |
| ドメイン特化 | 不可（汎用開発ツール） | 可 — あなたのERP、CRM、ワークフロー |
| 認証情報管理 | N/A | スキルごとの認証情報システム内蔵 |
| 有効/無効 | N/A | ワントグル、Web UIまたはCLI |

あなたの会社がデプロイ前にコンプライアンスチェックを実行するスキルが必要？OdooのCRMデータを5分ごとに同期するスキル？特定のフォーマットでバイリンガルPDFレポートを生成するスキル？Claude Codeがそれらをリリースすることはありません。**あなたのスキルはあなたの競争優位性です。それは他人のシステムではなく、あなたのシステムにあるべきです。**

### 「Claude CodeにはすでにMCPとスキルがある。なぜもう1つの層が必要？」

Claude CodeはMCPを提供します — ツールサーバーを登録するプロトコルです。これはChromeが拡張機能をインストールできるようにしていると言うのと同じです。確かに。しかしChromeには**Chrome ウェブストア**もあります — `.crx`ファイルを手動でインストールするのは拡張機能の管理ではないからです。

Claude Codeが提供するもの：
- `.mcp.json` — フラットなサーバーコマンドリスト。メタデータなし。ライフサイクルなし。
- `settings.json` — フラットな許可ツールリスト。グルーピングなし。トグルなし。
- `CLAUDE.md` — 自由形式テキスト。スキーマなし。バリデーションなし。

実際にはこういうことです：
- **スキルのインストール？** 3つのJSONファイルを手動で編集して`pip install`を実行。
- **スキルの無効化？** 2つのファイルからエントリを手動で削除。全部消せたことを祈る。
- **認証情報？** スキルごとに保存方法が違う。環境変数だったり、ファイルだったり、ハードコードだったり。
- **動いてる？** わからない。ターミナルを開いて運を天に任せる。
- **2台目のマシン？** 全部最初からやり直し。
- **10個のスキル？** `.mcp.json`が読めないJSONの壁になる。ご健闘をお祈りします。

Clawd-Lobsterのスキル層がMCPにないものを追加：

| MCP（素） | スキル管理（私たちの） |
|---|---|
| フラットJSON設定 | `skill.json`マニフェスト（スキーマ、認証情報、ヘルスチェック、依存関係） |
| 手動編集でインストール | `skill-manager.py enable <id>` — コマンド1つ |
| 手動編集で削除 | `skill-manager.py disable <id>` — コマンド1つ、クリーンな削除 |
| 認証情報標準なし | `~/.clawd-lobster/credentials/`に集約、スキルごとのフィールド定義 |
| ヘルスモニタリングなし | ヘルスチェック内蔵（mcp-ping、command、HTTP） |
| UIなし | Webダッシュボード（カードグリッド、トグル、検索、カテゴリフィルター） |
| マシンごとの設定 | gitによるマシン間のレジストリ同期 |
| 依存関係追跡なし | スキルが必要なもの（他のスキル、システムツール、Pythonパッケージ）を宣言 |

**MCPはプロトコル。私たちはパッケージマネージャーです。**

`npm`がNode.jsを置き換えないのと同じ — Node.jsをスケールで使えるようにするものです。私たちのスキル層はMCPを置き換えません — 5、10、50のスキルを複数マシンにまたがって管理する際にMCPを使えるようにします。完全なスキル管理システムについては[Chapter 3](#chapter-3スキル--エージェントにできること)を参照してください。

### 「Anthropicがこれをブロックしない？」

私たちはAnthropicが禁じていることは一切していません。正確に言うと：

- **やっていること：** OS cron/Task Schedulerで`claude` CLIコマンドをスケジュール。`claude --resume`で既存セッションを再開。Anthropic自身が定義したMCPプロトコルを使用。
- **やっていないこと：** プログラマティックOAuthログイン。APIキーの自動化。トークンスクレイピング。認証バイパス。リバースエンジニアリング。

ユーザーは`claude login`を1回実行します — 人間が、ブラウザで、Proサブスクリプションを使って。その後、OSスケジューラがAnthropicのCLIに自ら用意したフラグ（`--resume`、`-p`、`--allowedTools`）を使ってセッションを維持します。cronで`git pull`をスケジュールするのと何も変わりません。**私たちはCLIツールを自動化しています。ユーザーになりすましているのではありません。**

他のフレームワークはClaudeのAPIを直接呼び出します — APIキーが必要で、OAuthリフレッシュトークンを管理し、レートリミットを処理し、料金が変わらないことを祈ります。すべてのAPI変更が彼らにとって破壊的です。私たちにとっては透過的です — Claude Codeが自身の認証を処理します。

### 「ヘビーなワークロードのAPI費用は？」

「高いAPI」という議論は、トークン課金を前提としています。Proサブスクリプション（$20/月）があれば、**トークン課金はありません。** 最初のタスクも480番目のタスクも同じコスト：限界費用$0。

これにより、他のフレームワークが必要とする「思考には高いモデル、作業には安いモデル」アーキテクチャが丸ごと不要になります。ローカルでOllama 7Bを実行して安いタスクを処理する必要はありません。2つの推論スタックは不要です。どの頭脳を使うか決めるモデルルーターも不要です。

1つのサブスクリプション。1つのエンジン。1つの頭脳。無制限のタスク。

レートリミットに達したら（いずれ達します）、Clawd-Lobsterのskill-managerが優雅に作業をキューイングします。トークン予算パニックなし。驚きの請求なし。**予測可能なコストは機能です。**

---

## コントリビューション

コントリビューションを歓迎します！最も簡単な貢献方法：

1. **スキルを追加** — `skills/`にフォルダを作成し、`SKILL.md`またはMCPサーバーを追加
2. **テンプレートを改善** — `templates/`のデフォルトをより良いものに
3. **プラットフォームサポート** — Linux/macOSインストーラーの開発に協力

---

## ライセンス

MIT — お好きなようにお使いください。

---

<p align="center">
<sub>Anthropicとは無関係です。<a href="https://claude.ai/code">Claude Code</a>の上に構築されています。</sub>
</p>
