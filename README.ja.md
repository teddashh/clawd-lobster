[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/footprint-25MB_RAM-orange)

<p align="center">
<strong>アイデアから動くコードへ。一回の会話で。</strong><br>
<em>Spec Squad があなたの説明をレビュー済み・テスト済みのコードベースに変換します -- Claude Agent SDK を活用。</em>
</p>

<p align="center">
<sub>Web ダッシュボード + CLI。マルチエージェント開発。永続メモリ。マルチマシン同期。</sub>
</p>

---

## Clawd-Lobster とは？

Claude Code は脳。Clawd-Lobster は神経系統です。

Claude Code は現在利用可能な最も高性能なコーディングエージェントですが、セッション間で全てを忘れ、1台のマシンでしか動作せず、スキル管理機能もありません。Clawd-Lobster はまさに足りない部分を補います：コードの設計・レビュー・実装・テストを敵対的マルチエージェント協調で行う **Spec Squad** に加え、永続メモリ、マルチマシンオーケストレーション、厳選されたスキル、自己進化機能を提供します。

**Clawd-Lobster はジェネレーターです。** 一度実行すると、あなた専用の **Hub** が作成されます -- Hub はプライベート GitHub リポジトリで、あなたのコマンドセンターになります。Hub が全マシン、ワークスペース、メモリ、スキルを管理します。

```
  clawd-lobster (このリポジトリ -- ジェネレーター)
       |
       |  pip install -e . && clawd-lobster setup
       |
       v
  clawd-yourname (あなた専用のプライベート Hub -- 自動生成)
       |
       |  日常的に使うのはこちら
       |
       +-- Machine A -- Claude Code + skills + memory
       +-- Machine B -- Claude Code + skills + memory
       +-- Machine C -- Claude Code + skills + memory
            |
            全て接続済み。全てのナレッジを共有。
            ハートビートで常時稼働。
```

GitHub がコントロールプレーンです。Git がプロトコルです。すべてのステート -- スキル、ナレッジ、ワークスペースレジストリ、ハートビートステータス -- は git に格納され、自動的に同期されます。

**ランタイムフットプリント: 25 MB RAM、672 KB ディスク。** Python プロセス 1つ (MCP Memory Server) と SQLite のみ。その他は OS スケジューラ経由で実行・終了するか、ブラウザ上で動作します。ポーリングなし、デーモンなし、肥大化なし。

---

## クイックスタート

スタイルに合わせて3つの方法から選べます。

### Web UI (初心者におすすめ)

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
# ブラウザが http://localhost:3333 で開きます
# オンボーディングウィザードが全てガイドします
```

### Terminal (上級者向け)

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# 4ステップのインタラクティブウィザード: 前提条件確認 -> ペルソナ選択 -> ワークスペースルート設定 -> 最初のワークスペース作成
```

### Classic (インストールスクリプト)

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

### セットアップの仕組み

インストーラーは前提条件を確認し、Claude Code + GitHub の認証を行い、Hub を作成し、MCP Memory Server (32 ツール) をインストールし、ワークスペースを構成し、スケジューラとハートビートを登録します。必要な認証情報: OAuth クリック 2回のみ。API キーは不要です。

| プラットフォーム | 同期 | ハートビート |
|----------|------|-----------|
| Windows | Task Scheduler (30分) | Task Scheduler (30分) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | コンテナライフサイクル | コンテナライフサイクル |

---

## Web ダッシュボード

`clawd-lobster serve` で起動します (デフォルトポート 3333)。ダッシュボードには3つのメインビューがあります:

### /onboarding -- セットアップウィザード

初回訪問時は自動的にここに遷移します。ウィザードが前提条件 (Python, Claude CLI, Git, pip) をチェックし、ペルソナの選択 (Guided / Expert / Tech)、ワークスペースルートの設定、最初のワークスペースの作成まで、すべてブラウザ上で完結します。

### /workspaces -- ワークスペースマネージャー

登録済みの全ワークスペースをリアルタイムステータス付きで一覧表示します。各ワークスペースカードにはパス、メモリデータベースサイズ、git 同期ステータス、Spec Squad のフェーズが表示されます。ダッシュボードから直接新しいワークスペースを作成したり、同期のオン・オフを切り替えたりできます。

### /squad -- Spec Squad

マルチエージェント開発インターフェースです。ディスカバリー会話を開始し、Architect が仕様を書き、Reviewer がそれに異議を唱え、Coder がビルドし、Tester が検証する様子を、SSE によるライブプログレス更新で追跡できます。

---

## Spec Squad -- マルチエージェント開発

Spec Squad は v1.0 のコア機能です。4つの専門エージェントが協調して、あなたのアイデアをレビュー済み・テスト済みのコードに変換します -- Claude Agent SDK を使用。

### パイプライン

```
あなたがプロジェクトを説明する
  | clawd-lobster squad start (ターミナル)
  | または /squad ページ (Web)
  v
Discovery Interview
  | シニアコンサルタントが3-6個のスマートな質問 (3W1H: Why, What, Who, How)
  | 十分なコンテキストが集まったら: DISCOVERY_COMPLETE
  v
Architect
  | 完全な OpenSpec を作成: project.md -> proposal.md -> design.md
  | -> specs/ (SHALL/MUST + Gherkin) -> tasks.md (フェーズ分け、各5-30分)
  v
Reviewer (敵対的)
  | 仕様を徹底的に精査。ギャップ、曖昧さ、弱い判断を発見。
  | 判定: REVISE (問題点付き) または APPROVED (信頼度スコア付き)
  | 最大5ラウンドのレビュー -- Architect は全ての問題を修正必須
  v
Coder
  | 承認された仕様をタスクごと、フェーズごとに実行
  | フェーズ完了ごとにコミット。tasks.md のタスクを完了マーク
  v
Tester
  | 全ての SHALL/MUST 要件をコードに照らして検証
  | Gherkin シナリオを実行。判定: PASSED または ISSUES (パス率付き)
  v
完了 -- レビュー済み・テスト済みのコードベースが完成
```

### 敵対的レビューの仕組み

Reviewer は「容赦なく、しかし公正に」指示されています。`openspec/` 内の全ファイルを読み、アーキテクチャ、要件、タスク分割に異議を唱えます。問題が見つかれば、Architect は修正しなければなりません。このループは Reviewer が信頼度スコア付きの APPROVED 判定を出すまで最大5ラウンド実行されます。結果として、コードを1行も書く前にストレステスト済みの仕様が得られます。

### Web モード vs ターミナルモード

| | Web (`/squad`) | Terminal (`clawd-lobster squad start`) |
|---|---|---|
| Discovery | ブラウザ上のチャットインターフェース | stdin/stdout |
| 進捗表示 | ライブ SSE イベント、ビジュアルフェーズ | フェーズラベルをターミナルに出力 |
| ビルド承認 | ブラウザ上でプロンプト | `Build now? (y/n)` |
| 状態管理 | `.spec-squad.json` に永続化 | 同じファイル |
| 基盤エンジン | 同じ `squad.py` 非同期コア | 同じ `squad.py` 非同期コア |

両モードとも同じパイプライン、同じ Agent SDK 呼び出し、同じステートファイルを使用します。ワークフローに合う方をお選びください。

---

## スキル

9つのスキルモジュール。それぞれ `skill.json` マニフェスト付き。合計 32 MCP ツール。

### Core Skills (固定)

| スキル | タイプ | 機能 |
|---|---|---|
| **Memory Server** | mcp-server | 26ツールの MCP メモリ。SQLite、重要度エンジン、CJK 対応コンパクション |
| **Heartbeat** | cron | OS スケジューラによるセッション維持 -- 停止したセッションを自動復活 |
| **Evolve** | prompt-pattern | パターン抽出、改善提案、重要度減衰 |
| **Absorb** | prompt-pattern | フォルダ、GitHub リポジトリ、URL からのナレッジ取り込み |
| **Spec** | prompt-pattern | OpenSpec 手法によるガイド付き設計 + blitz 実行 |

### Optional Skills

| スキル | タイプ | 機能 | デフォルト |
|---|---|---|---|
| **Migrate** | prompt-pattern | 既存 AI セットアップからのインポート (フォーマット自動検出) | 有効 |
| **Connect-Odoo** | mcp-server | Odoo ERP 連携 -- XML-RPC + ポーラー経由の 6 MCP ツール | 無効 |
| **Codex Bridge** | prompt-pattern | OpenAI Codex に worker + critic ロールでタスク委任 | 無効 |
| **NotebookLM Bridge** | prompt-pattern | Google NotebookLM 経由の無料 RAG + コンテンツエンジン | 無効 |

### スキル管理

各スキルは `skill.json` マニフェストを持つ独立したモジュールです。**Web UI** または **CLI** で管理できます:

```bash
clawd-lobster serve                                      # トグル付き Web ダッシュボード
python scripts/skill-manager.py list                     # 全スキルの一覧表示
python scripts/skill-manager.py enable connect-odoo      # スキルを有効化
python scripts/skill-manager.py disable connect-odoo     # スキルを無効化
python scripts/skill-manager.py health                   # 全ヘルスチェックを実行
python scripts/skill-manager.py reconcile                # .mcp.json + settings.json を再生成
```

### 独自スキルの追加

`skills/my-skill/skill.json` にマニフェストを作成し、スキルを実装 (MCP server、スクリプト、または SKILL.md) して、`skill-manager.py reconcile` を実行するだけです。スキルは設定エントリ3つで完結 -- SDK 不要、プラグイン API 不要、フレームワークロックイン不要。

---

## アーキテクチャ

### 3層設計

```
+----------------------------------------------+
|        Skills Layer (Clawd-Lobster)           |
|                                               |
|  Memory System    Workspace Manager           |
|  Spec Squad       Scheduler                   |
|  Self-Evolution   (カスタムスキル)             |
|                                               |
|  インストール方法: .mcp.json + settings.json  |
|                    + CLAUDE.md                 |
+----------------------+------------------------+
                       |
+----------------------v------------------------+
|            Claude Code (ブレイン)               |
|                                                |
|  Agent Loop - Streaming - Tools - Permissions  |
|  Anthropic がメンテナンス。自動アップグレード。 |
+------------------------------------------------+
```

### 4層メモリ

| レイヤー | 内容 | 速度 | スコープ |
|-------|------|-------|-------|
| **L1.5** | Claude Code auto-memory (ネイティブ) | 即時 | 現在のプロジェクト |
| **L2** | SQLite + 26 MCP ツール | ~1ms | ワークスペース単位 |
| **L3** | Markdown ナレッジベース | ~10ms | git 経由で共有 |
| **L4** | Cloud DB (オプション) | ~100ms | ワークスペース横断 |

重要度エンジンが重要なメモリへのアクセスを維持します: アクセスごとに重要度が 5% 上昇、手動強化で 20% 上昇 (上限 2.0x)、30日以上アクセスのないアイテムは 1日 5% 減衰 (下限 0.01 -- 削除はされません)。

### 実際に動いているもの

| レイヤー | 内容 | 行数 | RAM | タイミング |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (26ツール + SQLite) | ~1,400 | ~25 MB | 常時稼働 |
| **Runtime** | Odoo Connector (有効時) | ~280 | ~22 MB | 有効時のみ |
| **Runtime** | Web Dashboard (stdlib HTTP) | ~800 | ~15 MB | サーブ時 |
| **Cron** | evolve-tick (提案生成) | ~465 | ~20 MB ピーク | 2時間ごと、実行後終了 |
| **Cron** | heartbeat + sync | ~300 | ~5 MB ピーク | 30分ごと、実行後終了 |
| **Setup** | CLI + オンボーディング + squad オーケストレーター | ~1,200 | 0 | オンデマンド |
| **Config** | skill.json マニフェスト、テンプレート | ~900 | 0 | 起動時に読み込み |

**常駐フットプリント: Python プロセス 1つ (~25 MB) + SQLite。** Web ダッシュボードは stdlib `http.server` を使用 -- Flask なし、FastAPI なし、外部依存なし。

### 設計思想

1. **巨人の肩に立つ。** Claude Code の背後には何百万時間ものエンジニアリングがあります。私たちは足りないものを追加し (~3K 行)、最高のエンジンを活かします。

2. **コードが少なければ、故障も少ない。** 設定エントリ3つ = スキル1つ。SDK ゼロ。OS スケジューラは 1970年代から信頼されてきました -- カスタムデーモンの代わりに `cron` + `claude --resume` を使います。

3. **巨人が成長すれば、あなたも成長する。** Anthropic がネイティブメモリ、24/7 エージェント、マルチエージェント連携を提供したとき -- 私たちは書き直すのではなく、コードを引退させます。**私たちのコードベースは時間とともに縮小します。彼らのは成長します。**

詳細は [ARCHITECTURE.md](ARCHITECTURE.md) をご覧ください。

---

## CLI リファレンス

| コマンド | 機能 |
|---|---|
| `clawd-lobster serve` | Web ダッシュボードを localhost:3333 で起動 |
| `clawd-lobster serve --port 8080` | カスタムポートを使用 |
| `clawd-lobster serve --daemon` | サーバーをバックグラウンドで実行 |
| `clawd-lobster setup` | ターミナルオンボーディングウィザードを実行 |
| `clawd-lobster workspace create <name>` | 新しいワークスペースを作成 |
| `clawd-lobster workspace create <name> --repo` | ワークスペース + プライベート GitHub リポジトリを作成 |
| `clawd-lobster workspace create <name> --dry-run` | 変更を加えずプレビュー |
| `clawd-lobster squad start` | Spec Squad をターミナルモードで起動 |
| `clawd-lobster squad start --workspace <path>` | 対象ワークスペースを指定 |
| `clawd-lobster status` | システムヘルス、ワークスペース、バージョンを表示 |
| `clawd-lobster --version` | バージョンを表示 |

---

## マルチマシンセットアップ

### Hub パターン

Hub はプライベート GitHub リポジトリで、コマンドセンターとして機能します。すべてのマシンが Hub をクローンし、自動的に同期します。

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
              |  2分で参加可能       |
              +---------------------+
```

### 別のマシンを追加する

```bash
git clone https://github.com/you/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# "Join existing Hub" を選択 -> Hub URL を貼り付け -> このマシンに名前を付ける -> 完了
```

新しいマシンは蓄積された全ナレッジを即座に引き継ぎます。L2 (SQLite) はワークスペースごとにローカル、L3 (markdown) は git 経由で同期、L4 (オプションの Cloud DB) は全てを統合します。

### Always Alive -- ハートビート

エージェントは決して停止しません。OS スケジューラが 30分ごとに確認します: 各ワークスペースのセッションは稼働中か？停止していれば `claude --resume` で復活 -- コンテキスト完全復元。カスタムデーモン不要。Claude Code が常に稼働し続けます。

---

## ワークスペース

ワークスペースはメモリ、スキル、仕様サポートを備えたプロジェクトディレクトリです。

### ワークスペース構造

```
my-project/
+-- CLAUDE.md              <- プロジェクト固有の指示
+-- .claude-memory/
|   +-- memory.db          <- L2 メモリ (SQLite)
+-- knowledge/             <- L3 ナレッジ (git同期)
+-- skills/learned/        <- 自動生成されたスキル
+-- openspec/              <- 仕様成果物 (/spec または squad 使用時)
|   +-- project.md
|   +-- changes/
|   +-- specs/
+-- .spec-squad.json       <- squad 状態 (squad 使用時)
+-- .blitz-active          <- blitz 実行中に存在
```

### スケジュール自動化

OS レベルのスケジューラ (Windows Task Scheduler / cron / launchd) は Claude Code が起動していなくても動作します:

- **Heartbeat** -- 全ワークスペースセッションの稼働を確認 (停止していれば復活)
- **Git sync** -- 30分ごとに全リポジトリを pull・push
- **Salience decay** -- 毎日のメモリ重要度調整
- **evolve-tick** -- 2時間ごとのパターン抽出 + 改善提案

---

## メモリシステム

### 26 MCP ツール

| カテゴリ | ツール |
|---|---|
| **Write** | `memory_store`, `memory_record_decision`, `memory_record_resolved`, `memory_record_question`, `memory_record_knowledge` |
| **Read** | `memory_list`, `memory_get`, `memory_get_summary` |
| **Delete** | `memory_delete` |
| **Search** | `memory_search` (ベクトル + テキスト、重要度加重、全テーブル) |
| **Salience** | `memory_reinforce` |
| **Evolve** | `memory_learn_skill`, `memory_list_skills`, `memory_improve_skill` |
| **TODO** | `memory_todo_add`, `memory_todo_list`, `memory_todo_update`, `memory_todo_search` |
| **Audit Trail** | `memory_log_action`, `memory_audit_search`, `memory_audit_stats`, `memory_daily_report`, `memory_activity_log` |
| **Admin** | `memory_compact`, `memory_status`, `memory_oracle_summary` |

メモリは受動的なストアではありません -- エージェントの動作を能動的に形作ります。すべての軌跡が記録されます。すべてのワークスペースが git 経由でナレッジを共有します。エージェントたちは共に成長します。

---

## 進化システム

v1 が構築された後も、エージェントは自動的に改善し続けます。

### ループ

```
/absorb (入力)
  +-- フォルダをスキャン -> ナレッジ、決定事項、TODO を抽出
  +-- GitHub リポジトリを読み取り -> パターン + スキルを学習
  +-- URL を取得 -> インサイトを保存
       |
evolve-tick (2時間ごと)
  +-- 完了した作業からパターンを抽出
  +-- 改善提案を生成 (git 同期される markdown ファイル)
  +-- 古くなったナレッジに重要度減衰を適用
  +-- マシン間でナレッジを同期
       |
Review (あなたが判断)
  +-- openspec/proposals/ 内の提案をレビュー
  +-- 承認 -> 次の blitz の TODO になる
  +-- 却下 -> 学びを記録してアーカイブ
```

Evolve は直接変更ではなく**提案**を生成します。すべての提案は `openspec/proposals/` に保存され、人間のレビューを待ちます。学習されたスキルは git sync を通じてセッション間・マシン間で永続します。

---

## 要件

- **Python** 3.10+ および **Git** 2.x+
- **Claude Code** CLI ([インストールガイド](https://docs.anthropic.com/en/docs/claude-code/getting-started))
- **GitHub** アカウント (プライベート Hub リポジトリ用)
- **Node.js** 18+ (オプション -- MCP server が必要とする場合のみ)

---

## インストール (詳細)

### 1. クローンとインストール

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
```

これで `clawd-lobster` CLI コマンドがグローバルに登録されます。

### 2. セットアップの実行

いずれかを選択:

```bash
clawd-lobster serve    # Web ウィザード (http://localhost:3333)
clawd-lobster setup    # ターミナルウィザード
./install.ps1          # Windows クラシックインストーラー
./install.sh           # macOS/Linux クラシックインストーラー
```

### 3. 確認

```bash
clawd-lobster status
# 表示内容: Python バージョン、Claude CLI、Git、ワークスペース、サーバーステータス
```

### 4. 構築開始

```bash
clawd-lobster squad start                    # プロジェクトを説明 -> 仕様作成 -> ビルド
clawd-lobster workspace create my-app --repo # またはワークスペースを手動で作成
```

---

## FAQ

### 「これは Claude Code のラッパーにすぎないのでは？」

はい。それが狙いです。

Claude Code は現在利用可能な最も高性能なコーディングエージェントであり、Anthropic の何百万時間ものエンジニアリングに支えられています。他のフレームワークはエンジンをゼロから再構築します (5万-30万行)。私たちは足りないものを追加し (~3K 行)、最高のエンジンを活かします。

Anthropic が次のブレークスルーを提供したとき、私たちは即座にそれを享受できます。他のフレームワークはアダプターを書き直す必要があります。

### 「Spec Squad は Claude にコードを頼むのとどう違うの？」

Spec Squad はコーディング開始前に**敵対的レビュー**を追加します。Architect が完全な仕様を書き、Reviewer がそれを徹底的に精査 -- ギャップ、曖昧さ、弱い判断を見つけます。Coder が何かに触れる前に最大5ラウンドの修正が行われます。つまり、カジュアルなプロンプトからではなく、ストレステスト済みの設計図からコードが構築されます。

### 「でも他のエージェントは 24/7 稼働して学習し続けるでしょ」

私たちもそうです。スケジューラが 30分ごとにナレッジを同期します。メモリは重要度減衰によって毎日進化します。学習されたスキルは git を通じて全マシンに伝播します。ハートビートがセッションの稼働を保証します: ターミナルが閉じれば、OS スケジューラが `claude --resume` で復活させます -- コンテキスト完全復元。

### 「Claude Code にはすでに組み込みスキルと MCP があるけど、なぜもっと必要？」

Claude Code の組み込みスキルはクローズドです -- 追加、変更、共有ができません。MCP はプロトコルを提供しますが、ライフサイクル管理はありません。スキルのインストールは 3つの JSON ファイルを手動で編集する必要があります。2台目のマシン？全部やり直しです。

**MCP はプロトコルです。私たちはパッケージマネージャーです。** 私たちが追加するもの: `skill.json` マニフェスト、ワンコマンドでの有効化/無効化、認証情報の一元管理、ヘルスチェック、Web ダッシュボード、git 経由のクロスマシンレジストリ同期。

### 「Anthropic はこれをブロックしない？」

私たちは OS cron 経由で `claude` CLI コマンドをスケジュールしています -- `git pull` をスケジュールするのと同じ方法です。`claude --resume`、`--allowedTools`、MCP server を使用しています -- すべて Anthropic が自身の CLI で提供しているフラグです。API キーの自動化なし。OAuth トークンのスクレイピングなし。リバースエンジニアリングなし。

### 「コストはどうなの？」

Pro サブスクリプション ($20/月) では、トークンごとの課金はありません。サブスクリプション1つ。エンジン1つ。予測可能なコストは機能です。

---

## 比較

| | Claude Code (素) | 重量級フレームワーク | **Clawd-Lobster** |
|---|---|---|---|
| エージェントエンジン | Anthropic | カスタム (5万-30万 LOC) | **Anthropic (ネイティブ)** |
| マルチエージェント開発 | なし | 一部あり | **あり (Spec Squad: 4エージェント)** |
| 敵対的レビュー | なし | なし | **あり (最大5ラウンド)** |
| 永続メモリ | なし | 様々 | **4層 + 重要度エンジン** |
| マルチマシン | なし | なし | **あり (Hub + git sync)** |
| 常時稼働 | なし | カスタムデーモン | **OS ハートビート + 自動復活** |
| スキル管理 | N/A | CLI/SDK | **Web UI + CLI + マニフェスト** |
| 自己進化 | なし | 様々 | **あり (提案 + 学習スキル)** |
| オンボーディング | 手動 | 複雑 | **Web ウィザードまたはターミナル、5言語対応** |
| Web ダッシュボード | なし | 様々 | **あり (localhost:3333)** |
| コードベース | 0 | 5万-30万 LOC | **~3K LOC** |
| コストモデル | サブスクリプション | トークン課金 API | **サブスクリプション (定額)** |
| Anthropic アップグレード | 透過的 | 破壊的 | **透過的** |

---

## ロードマップ

**v1.0 で完了**
- [x] 統一 CLI エントリポイント (`clawd-lobster serve/setup/squad/workspace/status`)
- [x] Web Dashboard -- オンボーディングウィザード、ワークスペースマネージャー、Spec Squad UI
- [x] Spec Squad -- Claude Agent SDK によるマルチエージェント開発
- [x] 3つのユーザーペルソナ (Guided / Expert / Tech)
- [x] 9 スキル、32 MCP ツール、`skill.json` マニフェストシステム
- [x] 重要度エンジン付き 4層メモリ
- [x] git sync によるマルチマシン Hub パターン
- [x] OS スケジューラによるハートビート自動復活
- [x] git 同期提案による進化ループ
- [x] Docker サポート

**次のステップ**
- [ ] Supabase L4 -- ワンクリック Cloud Database (Oracle wallet 不要)
- [ ] SearXNG -- プライベートセルフホスト Web 検索
- [ ] Docker Sandbox -- 信頼できない操作のための隔離されたコード実行
- [ ] Skill marketplace -- コミュニティ提供スキル、ワンクリックインストール
- [ ] Team mode -- ロールベースアクセスによるマルチユーザー共有ワークスペース
- [ ] Agent-to-agent delegation -- エージェント間でのタスク割り当て

---

## プロジェクト構造

```
clawd-lobster/
+-- clawd_lobster/       CLI + Web サーバー + squad オーケストレーター + オンボーディング
+-- skills/              9つのスキルモジュール (各 skill.json マニフェスト付き)
+-- scripts/             Heartbeat、sync、evolve-tick、skill-manager など
+-- templates/           設定テンプレート (シークレットなし)
+-- knowledge/           共有ナレッジベース (git同期)
+-- install.ps1/sh       クラシックインストーラー (Windows / macOS / Linux)
+-- pyproject.toml       パッケージ定義 (pip install -e .)
+-- Dockerfile           Docker サポート
+-- docker-compose.yml   Docker Compose 設定
```

---

## コントリビューション

コントリビューションを歓迎します！最も簡単な貢献方法:

1. **スキルを追加** -- `skills/` にフォルダを作成し、`skill.json` マニフェストを配置
2. **テンプレートを改善** -- `templates/` のデフォルト値を改善
3. **プラットフォームサポート** -- Linux/macOS テストへの協力
4. **バグ報告** -- Issue を開く

---

## ライセンス

MIT -- お好きなようにお使いください。

---

<p align="center">
<sub>Anthropic とは無関係です。<a href="https://claude.ai/code">Claude Code</a> の上に構築されています。</sub>
</p>
