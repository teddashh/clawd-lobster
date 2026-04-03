🌐 [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [**日本語**](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-0.5.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Runtime](https://img.shields.io/badge/footprint-25MB_RAM-orange)

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

## 必要条件

- **Node.js** 18+ と **Python** 3.11+ と **Git** 2.x+
- **Claude Code** CLI（[インストールガイド](https://docs.anthropic.com/en/docs/claude-code/getting-started)）
- **GitHub** アカウント（プライベート Hub リポジトリ用）

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
             ▼
```

その後、9つのステップが自動実行されます：

### 9つのステップの内容

| ステップ | アクション | 時間 |
|------|--------|------|
| 1 | 前提条件のチェック（Node、Python、Git） | 5秒 |
| 2 | Claude Code + GitHubの認証（OAuthクリック2回） | 30秒 |
| 3 | **Hubを作成**（プライベートリポジトリ）または既存をクローン | 10秒 |
| 4 | 設定の書き込み | 5秒 |
| 5 | MCP Memory Serverのインストール（32ツール） | 10秒 |
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
| **L2** | SQLite + 32のMCPツール | ~1ms | ワークスペースごと |
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
| Memory Server | 32ツールMCPメモリ + SQLite | メモリなし = エージェントなし |
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
| **Runtime** | MCP Memory Server (32 tools + SQLite) | ~1,400 | ~25 MB | 常時 |
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

### 設計哲学

#### 1. 巨人の肩に立つ。

Claude Codeの背後には数百万時間のエンジニアリングがある。ゼロから再構築するのは野心ではない — 無駄だ。足りない部分だけを追加し（〜2K行）、最高のエンジンを維持する。

#### 2. 少ないコード、少ない障害。

3つの設定 = 1つのスキル。SDK不要。OSスケジューラは1970年代から信頼性が高い — カスタムデーモンの代わりに `cron` + `claude --resume` を使用。書かなかったコードは壊れないコード。

#### 3. 巨人が成長すれば、あなたも成長する。

Anthropicがネイティブメモリ、24/7エージェント、マルチエージェント連携を出荷した時 — 書き直すのではなく、コードを引退させる。他のフレームワークはClaude Codeと競合する。我々は補完する。**我々のコードベースは時間とともに縮小する。彼らのは膨張する。**

### プロジェクト構成

```
clawd-lobster/
├── skills/          9つのスキルモジュール（各skill.jsonマニフェスト付き）
├── scripts/         CLIツール：skill-manager、heartbeat、sync、evolve-tick等
├── templates/       設定テンプレート（シークレットなし）
├── webapp/          スキル管理ダッシュボード（3タブWeb UI）
├── knowledge/       共有ナレッジベース（git同期）
├── install.ps1/sh   インストーラ（Windows / macOS / Linux）
└── Dockerfile       Dockerサポート
```

完全なファイルツリーは [ARCHITECTURE.md](ARCHITECTURE.md) を参照。

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
| エージェント進化 | なし | なし | セルフインプルービングスキル | **あり（提案 + 学習済みスキル）** |
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

### 「Heartbeat / スキル / MCPは他でもあるのでは？」

OSスケジューラ（Task Scheduler / launchd / cron）がheartbeatとして30分ごとにチェック — セッション生存、git同期、salience減衰、すべて処理。カスタムデーモン不要、アイドル時トークン消費ゼロ。Anthropicがネイティブ24/7モードを出荷すれば、無料で移行。

Claude Codeのビルトインスキルはクローズドです — 追加・変更・共有不可。Clawd-Lobsterはあなた独自のスキル（ERP連携、コンプライアンスチェック等）を`skill.json`マニフェスト1つで追加可能にします。

**MCPはプロトコル。我々はパッケージマネージャー。** MCPの`.mcp.json`は手動編集のフラット設定。我々のスキル層がマニフェスト、ヘルスチェック、認証情報管理、Web UI、マシン間同期を追加します。`npm`がNode.jsを置き換えないのと同じ — スケールで使えるようにするものです。

### 「Anthropicがこれをブロックしない？」

ユーザーが`claude login`を1回実行 — 人間が、ブラウザで。その後OSスケジューラがAnthropicのCLI（`--resume`、`-p`）でセッションを維持。cronで`git pull`をスケジュールするのと同じです。OAuthトークン管理なし、APIキー自動化なし、リバースエンジニアリングなし。**CLIツールの自動化であり、ユーザーのなりすましではありません。**

### 「ヘビーなワークロードのAPI費用は？」

Proサブスクリプション（$20/月）= トークン課金なし。最初のタスクも480番目のタスクも限界費用$0。モデルルーター不要、推論スタック2つ不要。レートリミット時はskill-managerが優雅にキューイング。**予測可能なコストは機能です。**

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
