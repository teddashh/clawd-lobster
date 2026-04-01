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

### このプロジェクトがやることは一つです。

ゼロからフル装備のClaude Codeエージェントを — 高速で — Webインターフェースを通じてセットアップします。

**Step 1.** WebウィザードがClaude Codeのインストールと認証を数分でガイドします。

**Step 2.** Webウィザードが多層メモリシステムと必須ツールをセットアップします — クリックするだけで、次々とグリーンライトが点灯します。

**Step 3.** 必要なものだけをインストールできるスキルマーケットプレイスです。不要なものは一切ありません。

**Step 4.** エージェントは自由に進化します。すべてのメモリは永続化されます。すべてのアクションは追跡されます。すべてのインサイトは共有されます。

---

### 使わないものをなぜインストールするのですか？

他のフレームワークは、AIエージェントをゼロからすべて再構築します — 30万行のコード、独自のエージェントループ、独自のツールシステム、独自のすべて。そしてAnthropicがより優れたモデルをリリースすると、慌ててアダプターを書き直すことになります。

**Clawd-LobsterはClaude Codeと競合しません。Claude Codeを補完します。**

私たちはClaude Code — 世界で最も先進的なコーディングエージェント — から始め、不足しているものだけを追加します：永続メモリ、マルチエージェントオーケストレーション、そして厳選されたスキル。それ以上でも以下でもありません。

> **すべてのメモリは永続化されます。** すべてのトラジェクトリは記録されます。すべてのワークスペースは共有されます。
>
> エージェントたちは共に成長します。知識は蓄積されます。作業は決して失われません。

> *ゼロの肥大化。ゼロの書き直し。純粋なClaude Codeを、増幅する。*

---

## 違い

| | ヘビーウェイトフレームワーク | 素のClaude Code | **Clawd-Lobster** |
|---|---|---|---|
| **エージェントエンジン** | 独自（自社メンテナンス） | Anthropic | **Anthropic** |
| **コードベース** | 30万行以上 | N/A | **約2,000行** |
| **Opus 4.7リリース時** | アダプター書き直し | 自動アップグレード | **自動アップグレード** |
| **永続メモリ** | 単層またはなし | なし | **4層 + salience** |
| **マルチマシン** | 複雑または不可能 | 不可 | **組み込み（MDMスタイル）** |
| **オンボーディング** | 半日 | 手動 | **5分** |
| **パフォーマンス** | 独自エンジンのオーバーヘッド | ネイティブ | **ネイティブ** |

### コアアイデア

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

**スキルはたった3つの設定エントリです。** SDKなし。プラグインAPIなし。フレームワークのロックインなし。

---

## 機能

### 4層メモリシステム

ほとんどのAIエージェントはセッション間ですべてを忘れてしまいます。Clawd-LobsterはClaude Codeに永続的で、検索可能で、重み付けされたメモリを提供します。

| レイヤー | 内容 | 速度 | スコープ |
|-------|------|-------|-------|
| **L1.5** | CC auto-memory（ネイティブ） | 即時 | 現在のプロジェクト |
| **L2** | SQLite + 21のMCPツール | ~1ms | ワークスペースごと |
| **L3** | Markdownナレッジベース | ~10ms | gitで共有 |
| **L4** | Cloud DB（オプション） | ~100ms | ワークスペース横断 |

**Salienceエンジン** — 重要なメモリは浮上し、古くなったメモリは沈みます：
- アクセスごと：+5% salienceブースト
- 手動強化：+20%ブースト（上限2.0x）
- 30日間未アクセス：-5%/日の減衰（下限0.01、削除はされません）

**CJK対応トークン推定** — 多言語ワークロード向けの正確なコンパクション・タイミング。

### マルチエージェント共有ナレッジ

これは単なる一つのエージェントではありません。フリートです — そしてすべてが同じ頭脳を共有しています。

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

### 進化するエージェント

エージェントは実行するだけではありません — 学習します。3つの専用MCPツールによるセルフエボリューション機能が組み込まれています：

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

- **学習したスキルは永続化** — データベースとgit同期されたスキルファイルの両方に保存されます
- **有効性の追跡** — 使用ごとに+2%、改善ごとに+10%、実証済みスキルのスコアは2.0x以上
- **エージェント間共有** — Agent Aで学習したスキルはgit同期を通じてAgent Bでも利用可能です
- **自然な引退** — 90日以上使用されていないスキルは、潜在的に陳腐化したものとしてフラグが立てられます
- **知識の複利効果** — あるワークスペースでの判断が別のワークスペースの作業に活かされ、解決済みの問題は二度と解き直す必要がありません

### スマートマイグレーション

すでに別のセットアップを使用していますか？Claude Codeが既存のファイルを読み取り、インテリジェントにインポートします：

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

パーサースクリプトは不要です。Claude Code**がそのまま**パーサーです — どんなフォーマットでも読み取り、セマンティクスを理解し、重要なものを保存します。

### シンプルなワークスペース管理

1つのコマンドでワークスペースを作成できます。スケジューラがワークスペースルート配下のすべてのgitリポジトリを自動同期します：

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

### スケジュール自動化

OSレベルのスケジューラ（Windows Task Scheduler / cron / launchd）— Claude Codeが起動していなくても実行されます：

- **Git同期** — 30分ごとにすべてのリポジトリをpullおよびpush
- **Salience減衰** — 日次のメモリ重要度調整

---

## クイックスタート

### オプションA：Webセットアップウィザード

ブラウザで `webapp/index.html` を開き、6ステップのガイド付きウィザードに従ってください。

### オプションB：コマンドライン

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

### インストーラーの動作

| ステップ | アクション | 時間 |
|------|--------|------|
| 1 | 前提条件のチェック（Node, Python, Git） | 5秒 |
| 2 | Claude Code + GitHubの認証（OAuth） | 30秒 |
| 3 | MCP Memory Serverのインストール（21ツール） | 10秒 |
| 4 | Claude Codeの設定（.mcp.json, settings.json, CLAUDE.md） | 5秒 |
| 5 | スケジュールタスクの登録（OS固有） | 5秒 |
| 6 | 完了 | --- |

| プラットフォーム | スケジューラ | 方法 |
|----------|-----------|--------|
| Windows | Task Scheduler | `install.ps1` が自動登録 |
| macOS | launchd | `install.sh` がLaunchAgentを作成 |
| Linux | cron | `install.sh` がcrontabエントリを追加 |
| Docker | コンテナ再起動 | `docker compose` がライフサイクルを管理 |

**必要な認証情報はOAuthクリック2回だけです。** APIキーのペーストは不要です（Oracle L4を使用する場合を除く）。

---

## スキルの追加

スキル = 3つの設定エントリ。それだけです。

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

学ぶべきSDKなし。プラグインインターフェースなし。ビルドステップなし。設定だけです。

---

## プロジェクト構成

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

## フィロソフィー

### 1. 最高のエージェントはすでに存在しています。それを使いましょう。

Claude Codeは世界最大のAI安全性研究機関が支えています。エージェントループ、ストリーミング、パーミッション、ツールシステムには数百万時間のエンジニアリングが注ぎ込まれています。それをゼロから再構築するのは野心ではありません — 無駄です。**巨人の肩の上に立ちましょう。**

### 2. 少ないほど良い。はるかに良い。

フレームワークのコードの一行一行が、メンテナンスが必要な一行です。Clawd-Lobsterが約2,000行なのは、Claude Codeのネイティブ拡張ポイント（MCP, hooks, CLAUDE.md）がすでに誰もが設計できる最高のプラグインシステムだからです。**3つの設定エントリ = 1つのスキル。SDKゼロ。**

### 3. 忘れるエージェントは失敗するエージェントです。

ほとんどのAIエージェントは毎回ゼロからセッションを始めます。同じミスを繰り返し、コンテキストを学び直し、あなたの時間を無駄にします。Clawd-Lobsterの4層メモリとsalience追跡により、**重要なものは浮上し、ノイズは消え、クリティカルなものは決して失われません。**

### 4. エージェントはどこへでも付いてくるべきです。

1台のコンピュータ？問題ありません。3台のマシン？すべてが同じ頭脳を共有すべきです。GitHubをコントロールプレーンに、git同期をプロトコルに。**2分でマシンを追加。インフラゼロ。**

### 5. 常に最新の波に乗りましょう。

AnthropicがOpus 4.7、1Mコンテキスト、新しいツールをリリースしたら — 即座に手に入ります。アダプターの書き直しなし。バージョン固定なし。コミュニティパッチ待ちなし。**Claude Codeを使う最高のタイミングは昨日でした。次に良いタイミングは今です。**

---

## 比較

| | Claude Code（素） | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| エージェントエンジン | Anthropic | 独自（Pi Agent） | 独自（Python） | **Anthropic（ネイティブ）** |
| 永続メモリ | なし | ハイブリッド検索 | FTS5 + LLM | **4層 + salience** |
| マルチエージェント共有メモリ | 不可 | 不可 | 不可 | **対応** |
| エージェント進化 | 不可 | 不可 | セルフインプルービングスキル | **対応（メモリ + スキル）** |
| マルチマシン | 不可 | 不可 | 不可 | **対応（MDMスタイル）** |
| オンボーディング | 手動 | 複雑 | 中程度 | **Webウィザード、5分** |
| 自動アップグレード | 対応 | 不可 | 不可 | **対応** |
| コードベースサイズ | N/A | 約30万行 | 約5万行 | **約2,000行** |
| 監査証跡 | なし | セキュリティ監査 | なし | **完全（すべてのアクション）** |
| スキルインストール | — | Plugin SDK | 3ファイル変更 | **3つの設定エントリ** |

---

## ロードマップ

**スキル**
- [ ] Codex Bridge — 重いタスクをバックグラウンドでOpenAI Codexに委任
- [ ] SearXNG — プライベートなセルフホスト型Web検索、データがネットワーク外に出ません
- [ ] Docker Sandbox — 信頼できないオペレーション用の隔離されたコード実行環境
- [ ] Browser Automation — Playwrightを活用したWebインタラクション

**プラットフォーム**
- [ ] Linuxインストーラー（bash）+ macOSインストーラー（zsh/launchd）
- [ ] Supabase L4 — ワンクリックのクラウドデータベース（Oracle walletは不要）
- [ ] Dashboard — すべてのエージェント、メモリ、同期状況のリアルタイムビュー

**進化**
- [ ] スキルマーケットプレイス — コミュニティ貢献のスキル、ワンクリックインストール
- [ ] 自動スキル生成 — エージェントが成功パターンから学習し、再利用可能なスキルを作成
- [ ] チームモード — ロールベースアクセス制御付きのマルチユーザー共有ワークスペース
- [ ] エージェント間委任 — エージェントが互いにタスクを割り当て

---

## コントリビューション

コントリビューションを歓迎します！最も簡単な貢献方法：

1. **スキルを追加** — `skills/` にフォルダを作成し、`SKILL.md` またはMCPサーバーを追加してください
2. **テンプレートを改善** — `templates/` のデフォルトをより良いものに
3. **プラットフォームサポート** — Linux/macOSインストーラーの開発にご協力ください

---

## ライセンス

MIT — お好きなようにお使いください。

---

<p align="center">
<sub>Anthropicとは無関係です。<a href="https://claude.ai/code">Claude Code</a>の上に構築されています。</sub>
</p>
