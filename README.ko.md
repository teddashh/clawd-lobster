🌐 [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [**한국어**](README.ko.md)

# Clawd-Lobster

<p align="center">
<strong>결국 최고를 쓰게 됩니다.</strong><br>
<em>궁극의 에이전트 경험 — 가장 가벼운 구조, 엄선된 기능, 최고의 성능.</em>
</p>

<p align="center">
<sub>웹 기반 설정. 다층 메모리. 멀티 에이전트 공유 지식. 자유로운 진화.</sub>
</p>

---

### 이 프로젝트는 한 가지를 합니다.

여러분을 제로 상태에서 완벽하게 갖춰진 Claude Code 에이전트로 — 빠르게 — 웹 인터페이스를 통해 안내합니다.

**Step 1.** 웹 마법사가 Claude Code 설치와 인증을 몇 분 만에 안내합니다.

**Step 2.** 웹 마법사가 다층 메모리 시스템과 필수 도구를 설정합니다 — 클릭 한 번, 초록불 하나씩.

**Step 3.** 필요한 것만 설치하는 스킬 마켓플레이스입니다. 필요 없는 것은 설치하지 않습니다.

**Step 4.** 에이전트가 자유롭게 진화합니다. 모든 기억은 유지됩니다. 모든 행동은 추적됩니다. 모든 인사이트는 공유됩니다.

---

### 필요 없는 것을 왜 설치하나요?

다른 프레임워크는 AI 에이전트 전체를 처음부터 다시 만듭니다 — 30만 줄의 코드, 커스텀 에이전트 루프, 커스텀 도구 시스템, 모든 것이 커스텀입니다. 그리고 Anthropic이 더 좋은 모델을 출시하면, 어댑터를 급히 다시 작성합니다.

**Clawd-Lobster는 Claude Code와 경쟁하지 않습니다. Claude Code를 완성합니다.**

우리는 Claude Code — 세계에서 가장 진보된 코딩 에이전트 — 에서 시작하여, 부족한 것만 정확히 추가합니다: 영구 메모리, 멀티 에이전트 오케스트레이션, 엄선된 스킬. 그 이상도, 그 이하도 없습니다.

> **모든 기억은 유지됩니다.** 모든 궤적이 기록됩니다. 모든 워크스페이스가 공유됩니다.
>
> 에이전트들이 함께 성장합니다. 지식이 축적됩니다. 작업은 절대 소실되지 않습니다.

> *제로 블로트. 제로 재작성. 순수한 Claude Code, 증폭.*

---

## 차이점

| | 무거운 프레임워크 | 기본 Claude Code | **Clawd-Lobster** |
|---|---|---|---|
| **에이전트 엔진** | 커스텀 (자체 유지보수) | Anthropic | **Anthropic** |
| **코드베이스** | 300K+ 줄 | N/A | **~2K 줄** |
| **Opus 4.7 출시 시** | 어댑터 재작성 | 자동 업그레이드 | **자동 업그레이드** |
| **영구 메모리** | 단층 또는 없음 | 없음 | **4층 + salience** |
| **멀티 머신** | 복잡하거나 불가능 | 불가 | **내장 (MDM 방식)** |
| **온보딩** | 반나절 | 수동 | **5분** |
| **성능** | 커스텀 엔진 오버헤드 | 네이티브 | **네이티브** |

### 핵심 아이디어

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

**스킬은 설정 3개로 끝입니다.** SDK 불필요. 플러그인 API 불필요. 프레임워크 종속 없음.

---

## 기능

### 4층 메모리 시스템

대부분의 AI 에이전트는 세션 간에 모든 것을 잊습니다. Clawd-Lobster는 Claude Code에 영구적이고, 검색 가능하며, 가중치가 부여된 메모리를 제공합니다.

| 레이어 | 내용 | 속도 | 범위 |
|-------|------|-------|-------|
| **L1.5** | CC 자동 메모리 (네이티브) | 즉시 | 현재 프로젝트 |
| **L2** | SQLite + 21개 MCP 도구 | ~1ms | 워크스페이스별 |
| **L3** | Markdown 지식 베이스 | ~10ms | git 동기화 공유 |
| **L4** | Cloud DB (선택사항) | ~100ms | 워크스페이스 간 |

**Salience 엔진** — 중요한 기억은 떠오르고, 오래된 기억은 가라앉습니다:
- 각 접근: +5% salience 상승
- 수동 강화: +20% 상승 (최대 2.0x 제한)
- 30일 미접근: -5%/일 감쇠 (최저 0.01, 삭제 없음)

**CJK 인식 토큰 추정** — 다국어 작업에 대한 정확한 압축 타이밍.

### 멀티 에이전트 공유 지식

이것은 단순히 하나의 에이전트가 아닙니다. 하나의 함대이며 — 모두 같은 두뇌를 공유합니다.

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

- **L2**는 로컬에 유지됩니다 (빠름, 워크스페이스별) — 각 에이전트가 자체 캐시를 보유합니다
- **L3**는 git으로 동기화됩니다 — 모든 에이전트가 같은 지식 베이스를 읽고 씁니다
- **L4**는 모든 것을 통합합니다 — 워크스페이스 간 검색, 감사 추적, 전체 이력
- **새 에이전트 합류?** `git clone + install.ps1` — 축적된 모든 지식을 즉시 상속합니다

### 진화하는 에이전트

에이전트는 단순히 실행만 하지 않습니다 — 학습합니다. 3개의 전용 MCP 도구를 통한 내장 자기 진화:

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

- **학습된 스킬은 영구 보존** — 데이터베이스와 git 동기화 스킬 파일 양쪽에 저장됩니다
- **효과성 추적** — 사용할 때마다 +2%, 개선할 때마다 +10%, 검증된 스킬은 점수 > 2.0x
- **에이전트 간 공유** — Agent A에서 학습한 스킬은 git 동기화를 통해 Agent B에서 사용 가능합니다
- **자연 은퇴** — 90일 이상 미사용 스킬은 잠재적으로 오래된 것으로 표시됩니다
- **지식 복리 효과** — 한 워크스페이스의 결정이 다른 워크스페이스의 작업에 반영되며, 해결된 문제는 두 번 해결하지 않습니다

### 스마트 마이그레이션

이미 다른 설정을 사용 중이신가요? Claude Code가 기존 파일을 읽고 지능적으로 가져옵니다:

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

파서 스크립트가 필요 없습니다. Claude Code **자체가** 파서입니다 — 어떤 형식이든 읽고, 의미를 이해하고, 중요한 것을 저장합니다.

### 간편한 워크스페이스 관리

명령어 하나로 워크스페이스를 생성합니다. 스케줄러가 워크스페이스 루트 아래의 모든 git 저장소를 자동 동기화합니다:

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

### 예약 자동화

OS 레벨 스케줄러 (Windows Task Scheduler / cron / launchd) — Claude Code가 활성화되지 않은 상태에서도 실행됩니다:

- **Git 동기화** — 30분마다 모든 저장소를 Pull 및 Push
- **Salience 감쇠** — 매일 메모리 중요도 조정

---

## 빠른 시작

### 옵션 A: 웹 설정 마법사

브라우저에서 `webapp/index.html`을 열고 6단계 가이드 마법사를 따르세요.

### 옵션 B: 커맨드 라인

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

### 설치 프로그램이 수행하는 작업

| 단계 | 동작 | 소요 시간 |
|------|--------|------|
| 1 | 필수 조건 확인 (Node, Python, Git) | 5초 |
| 2 | Claude Code + GitHub 인증 (OAuth) | 30초 |
| 3 | MCP Memory Server 설치 (21개 도구) | 10초 |
| 4 | Claude Code 설정 (.mcp.json, settings.json, CLAUDE.md) | 5초 |
| 5 | 예약 작업 등록 (OS 네이티브) | 5초 |
| 6 | 완료 | --- |

| 플랫폼 | 스케줄러 | 방식 |
|----------|-----------|--------|
| Windows | Task Scheduler | `install.ps1` 자동 등록 |
| macOS | launchd | `install.sh`가 LaunchAgent 생성 |
| Linux | cron | `install.sh`가 crontab 항목 추가 |
| Docker | 컨테이너 재시작 | `docker compose`가 생명주기 관리 |

**필요한 인증: OAuth 클릭 2번.** API 키 붙여넣기 불필요 (Oracle L4를 원하지 않는 한).

---

## 스킬 추가하기

스킬 = 설정 3개. 그게 전부입니다.

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

배울 SDK 없음. 플러그인 인터페이스 없음. 빌드 단계 없음. 설정만으로 완료.

---

## 프로젝트 구조

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

## 철학

### 1. 최고의 에이전트는 이미 존재합니다. 그것을 사용하세요.

Claude Code는 세계 최대의 AI 안전 연구소가 지원합니다. 수백만 시간의 엔지니어링이 에이전트 루프, 스트리밍, 권한, 도구 시스템에 투입되었습니다. 그것을 처음부터 다시 만드는 것은 야심이 아닙니다 — 낭비입니다. **거인의 어깨 위에 서세요.**

### 2. 적을수록 좋습니다. 훨씬 더.

프레임워크 코드의 모든 줄은 유지보수해야 할 줄입니다. Clawd-Lobster가 ~2K 줄인 이유는 Claude Code의 네이티브 확장 포인트(MCP, hooks, CLAUDE.md)가 이미 누구나 설계할 수 있는 최고의 플러그인 시스템이기 때문입니다. **설정 3개 = 스킬 하나. SDK 제로.**

### 3. 잊어버리는 에이전트는 실패하는 에이전트입니다.

대부분의 AI 에이전트는 매 세션을 제로에서 시작합니다. 실수를 반복하고, 컨텍스트를 다시 학습하고, 시간을 낭비합니다. Clawd-Lobster의 salience 추적이 포함된 4층 메모리는 **중요한 것이 떠오르고, 노이즈는 사라지며, 중요한 것은 절대 잃어버리지 않도록** 보장합니다.

### 4. 에이전트는 어디서든 따라와야 합니다.

컴퓨터 한 대? 좋습니다. 세 대? 모두 같은 두뇌를 공유해야 합니다. GitHub을 컨트롤 플레인으로, git 동기화를 프로토콜로. **2분 만에 머신을 추가하세요. 인프라 제로.**

### 5. 항상 최신 물결을 타세요.

Anthropic이 Opus 4.7, 1M 컨텍스트, 새로운 도구를 출시하면 — 즉시 받을 수 있습니다. 어댑터 재작성 없음. 버전 고정 없음. 커뮤니티 패치 대기 없음. **Claude Code를 사용하기 가장 좋은 때는 어제였습니다. 두 번째로 좋은 때는 지금입니다.**

---

## 비교

| | Claude Code (기본) | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| 에이전트 엔진 | Anthropic | 커스텀 (Pi Agent) | 커스텀 (Python) | **Anthropic (네이티브)** |
| 영구 메모리 | 없음 | 하이브리드 검색 | FTS5 + LLM | **4층 + salience** |
| 멀티 에이전트 공유 메모리 | 불가 | 불가 | 불가 | **지원** |
| 에이전트 진화 | 불가 | 불가 | 자기 개선 스킬 | **지원 (메모리 + 스킬)** |
| 멀티 머신 | 불가 | 불가 | 불가 | **지원 (MDM 방식)** |
| 온보딩 | 수동 | 복잡 | 보통 | **웹 마법사, 5분** |
| 자동 업그레이드 | 지원 | 불가 | 불가 | **지원** |
| 코드베이스 규모 | N/A | ~300K LOC | ~50K LOC | **~2K LOC** |
| 감사 추적 | 불가 | 보안 감사 | 불가 | **전체 (모든 행동)** |
| 스킬 설치 | — | Plugin SDK | 파일 3개 변경 | **설정 3개** |

---

## 로드맵

**스킬**
- [ ] Codex Bridge — 무거운 작업을 백그라운드에서 OpenAI Codex에 위임
- [ ] SearXNG — 프라이빗 자체 호스팅 웹 검색, 데이터가 네트워크 밖으로 나가지 않음
- [ ] Docker Sandbox — 신뢰할 수 없는 작업을 위한 격리된 코드 실행
- [ ] Browser Automation — Playwright 기반 웹 상호작용

**플랫폼**
- [ ] Linux 설치 프로그램 (bash) + macOS 설치 프로그램 (zsh/launchd)
- [ ] Supabase L4 — 원클릭 클라우드 데이터베이스 (Oracle wallet 불필요)
- [ ] Dashboard — 모든 에이전트, 메모리, 동기화 상태의 실시간 뷰

**진화**
- [ ] 스킬 마켓플레이스 — 커뮤니티 기여 스킬, 원클릭 설치
- [ ] 자동 스킬 생성 — 에이전트가 성공 패턴에서 학습하여 재사용 가능한 스킬 생성
- [ ] 팀 모드 — 역할 기반 접근 제어가 있는 다중 사용자 공유 워크스페이스
- [ ] 에이전트 간 위임 — 에이전트가 서로에게 작업을 할당

---

## 기여하기

기여를 환영합니다! 가장 쉬운 기여 방법:

1. **스킬 추가** — `skills/` 폴더에 `SKILL.md` 또는 MCP server를 포함한 폴더를 생성하세요
2. **템플릿 개선** — `templates/`의 기본값을 개선하세요
3. **플랫폼 지원** — Linux/macOS 설치 프로그램 개발을 도와주세요

---

## 라이선스

MIT — 원하는 대로 사용하세요.

---

<p align="center">
<sub>Anthropic과 제휴 관계가 아닙니다. <a href="https://claude.ai/code">Claude Code</a> 위에 구축되었습니다.</sub>
</p>
