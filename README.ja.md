[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/RAM-25MB-orange)

<p align="center">
<strong>你終究要用 Claude Code 的 — 為什麼不一開始就選最好的體驗？</strong><br>
<strong>You'll end up using Claude Code anyway — why not start with the best experience?</strong><br>
<strong>どうせ最後は Claude Code を使うことになる — なら最初から最高の体験を選びませんか？</strong>
</p>

---

## 問題

AI エージェントフレームワーク、見たことありますよね。いくつか試したかもしれません。実際に何が起こるか：

**問題 1：Claude Code は強力。でもあなたがベビーシッターをしている。**
毎セッションがゼロから始まる。昨日学んだことを忘れる。コンテキストをコピペし、アーキテクチャを再説明し、規約を繰り返す。あなたがメモリ。あなたがマネージャー。あなたがボトルネック。

**問題 2：AI エージェントフレームワーク — デモは華やか、体験は最悪。**
30万行のコード。カスタムアダプター。プロジェクト本体より長い設定ファイル。モデルが更新されるたびに壊れる。フレームワークのメンテに費やす時間の方がプロダクト開発より長い。

**問題 3：グレーゾーン。**
安全機構を迂回するセルフホスト型エージェントループ。上限なしのトークン従量課金 API。ツールを使っているのか、ツールに使われているのか分からないフランケンシュタインスタック。

## 答え

Clawd-Lobster は Claude Code を置き換えません。Claude Code に**記憶し、計画し、レビューし、構築し、進化する力**を与えます — 公式 Anthropic ツールだけで。

- **100% Claude Code CLI + Agent SDK。** ラッパーなし、カスタムエージェントループなし、グレーゾーンなし。既存の Claude サブスクリプションで動作。追加 API コストなし。
- **約9,000行。** 30万行ではない。一人で全部読める規模。Claude Code がアップデートされれば、新機能はそのまま使える。書き直し不要。壊れない。
- **5分で開始。** ブラウザを開く。2回クリック。終わり。API キー不要、Docker 不要、YAML の博士号不要。

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

## クイックスタート

### 全員向け（Web UI）

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
```

ブラウザが開きます。セットアップウィザードがすべてガイドします。

### ターミナル派の方へ

```bash
clawd-lobster setup        # terminal onboarding
clawd-lobster squad start  # run Spec Squad in terminal
```

### クラシックインストール（パワーユーザー向け）

```powershell
# Windows
.\install.ps1

# macOS / Linux
chmod +x install.sh && ./install.sh
```

---

## 手に入るもの

### 1. Spec Squad — あなたの AI 開発チーム

やりたいことを説明するだけ。4つの Claude セッションが残りをやります。

**Architect** がテスト可能な要件を含む完全な仕様を書きます。**Reviewer** — Architect の指示を一切見たことがない完全に独立した Claude セッション — がそれを徹底的に叩きます。Reviewer が承認するまでループします。その後 **Coder** が仕様通りに構築し、**Tester** がすべての要件を検証します。

ギミックではありません。テストでは、Reviewer が最初の仕様で実際のバグを11個発見しました — セルフバリデーションチェックリストでは絶対に見つからない問題です。戻り値の型の矛盾、API の不整合、実現不可能な Gherkin シナリオ、ライブラリの互換性問題。

**なぜ機能するのか：** 各エージェントは隔離されたコンテキストで実行されます。Reviewer は Architect の推論に影響されません。Tester は Coder がどんなショートカットを使ったか知りません。独立した頭脳が独立した問題を見つけます。

2つのインターフェース、同じエンジン：
- **Web：** ブラウザで Claude とチャットし、ライブダッシュボードでエージェントの作業を監視
- **Terminal：** ターミナルで Claude が質問し、エージェント実行中に進捗を表示

### 2. 忘れない頭脳

即時からグローバルまで、4層のメモリ：

| Layer | Speed | What |
|-------|-------|------|
| L1.5 | Instant | Claude Code's native auto-memory |
| L2 | ~1ms | SQLite + MCP — per-workspace, salience-weighted |
| L3 | ~10ms | Markdown + Git — synced across machines |
| L4 | ~100ms | Cloud DB (optional) — cross-workspace search |

重要なアイデアは浮上し、ノイズは沈む。うまくいったスキルは強化され、古い知識は減衰する。あなたが管理する必要はありません — すべて自動です。

### 3. 常に生きている

ノートパソコンを閉じても、Clawd-Lobster は動き続けます。

heartbeat は OS のスケジューラ（Task Scheduler / cron / launchd）を使います — カスタムデーモンでも、ポーリングループでも、トークンを燃やすプロセスでもありません。セッションが落ちたら、フルコンテキストで復活。ベビーシッター不要。

### 4. すべてのマシン、1つの頭脳

GitHub がコントロールプレーン。Git がプロトコル。

マシン A がパターンを学習。プライベート Hub に同期。マシン B が即座に継承。新しいマシン？`install.ps1`、「Join Hub」、URL を貼り付け、2分で完全稼働。

### 5. 自己進化

複雑な作業の完了後、システムは再利用可能なパターンを抽出し、学習済みスキルとして保存します。次に同様のタスクが来たとき、前回どう解決したかを覚えています。

スキルには有効性スコアがあります。実績のあるパターンは強化され、古いスキルは減衰します。使えば使うほど賢くなる — 魔法ではなく、うまくいったことを書き留めているだけです。

---

## ダッシュボード

`clawd-lobster serve` で `localhost:3333` に常駐 Web ダッシュボードが開きます。

**オンボーディング** — 初回ウィザードが前提条件をチェックし、セットアップをガイドし、最初のワークスペースを作成します。

**ワークスペース** — すべてのプロジェクトを一覧表示。ステータス、仕様の進捗、メモリサイズ、最終アクティビティ。

**Spec Squad** — ブラウザで Claude とチャットして要件を発見。フェーズタイムラインとターン履歴を備えたライブダッシュボードで、4つのエージェントの作業をリアルタイムで監視。

---

## Skills

厳選された9つの Skills。それぞれが1つのことを確実にこなします。

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

すべての Skill にはトリガー説明（Claude が起動タイミングを判断）、Gotchas セクション（よくある間違いの回避策）、動的 `!command` インジェクション（ロード時のランタイムコンテキスト）があります。

---

## アーキテクチャ

```
Skills (the what)     ->  9 skills with manifests, instructions, gotchas
Tools (the how)       ->  32 MCP tools + Claude Code native tools
Hooks (the when)      ->  OS scheduler, git hooks, PostToolUse, Stop hooks
```

**巨人の肩の上に立つ。** Clawd-Lobster は Claude Code を再構築しません。Claude Code のネイティブ拡張ポイント（MCP サーバー、CLAUDE.md、hooks、settings.json）を Anthropic が設計した通りに使います。Claude Code が新機能をリリースすれば、そのまま使える。モデルが改善されれば、あなたのエージェントも改善される。アダプターコードはゼロ。

```
Disk: ~830 KB    (code + configs)
RAM:  ~25 MB    (MCP server only)
CPU:  0% idle   (OS scheduler, not polling)
LOC:  ~9,000    (not 300,000)
```

ファイルツリーとランタイムの詳細は [ARCHITECTURE.md](ARCHITECTURE.md) を参照。

---

## CLI リファレンス

| Command | What It Does |
|---------|-------------|
| `clawd-lobster serve` | Start web dashboard (localhost:3333) |
| `clawd-lobster setup` | Terminal onboarding wizard |
| `clawd-lobster workspace create <name>` | Create a new workspace |
| `clawd-lobster squad start` | Run Spec Squad in terminal |
| `clawd-lobster status` | Show system health |

---

## マルチマシンセットアップ

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

最初のマシンが Hub を作成。以降のマシンは2分で参加できます。

---

## 必要条件

- Python 3.10+
- Claude Code CLI ([install](https://claude.ai/code))
- Git 2.x+
- Node.js 18+（オプション、Codex Bridge 用）
- GitHub アカウント（Hub sync 用）

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

## フィロソフィー

**1. 増幅する。再構築しない。**
Claude Code は世界で最も優秀なコーディングエージェントです。私たちはそこに神経系を加えます。脳を作り直すのではありません。

**2. 巨人が高くなれば、あなたも高くなる。**
Claude Code がアップデートされるたびに、あなたの Clawd-Lobster も良くなります。マイグレーションゼロ、書き直しゼロ。

**3. 計画こそがプロダクト。**
Spec Squad はまずコードを書きません。仕様を書き、それを敵対的にレビューし、仕様通りに構築します。計画が契約です。

---

## コントリビュート

PR 歓迎です。コントリビュートの前に [ARCHITECTURE.md](ARCHITECTURE.md) をお読みください。

## ライセンス

MIT — [LICENSE](LICENSE) を参照。
