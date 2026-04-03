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

## Clawd-Lobster란?

Claude Code는 두뇌입니다. Clawd-Lobster는 신경계입니다.

Claude Code는 현존하는 가장 강력한 코딩 에이전트이지만, 세션 간에 모든 것을 잊고, 한 대의 머신에서만 동작하며, 스킬 관리 기능이 없습니다. Clawd-Lobster는 부족한 것을 정확히 보완합니다: 영구 메모리, 멀티 머신 오케스트레이션, 엄선된 스킬, 그리고 자기 진화. 그 이상도, 그 이하도 없습니다.

**Clawd-Lobster는 생성기입니다.** 한 번 실행하면, 여러분만의 **Hub** — 커맨드 센터가 되는 프라이빗 GitHub 저장소를 만들어 줍니다. Hub가 모든 머신, 워크스페이스, 메모리, 스킬을 관리합니다.

```
  clawd-lobster (이 저장소 — 생성기)
       │
       │  install.ps1을 한 번 실행
       │
       ▼
  clawd-yourname (여러분의 프라이빗 Hub — 여러분을 위해 생성)
       │
       │  이것이 매일 실제로 사용하는 것
       │
       ├── Machine A ── Claude Code + skills + memory
       ├── Machine B ── Claude Code + skills + memory
       └── Machine C ── Claude Code + skills + memory
            │
            전부 연결. 전부 지식 공유.
            전부 heartbeat로 상시 가동.
```

GitHub가 컨트롤 플레인입니다. Git이 프로토콜입니다. 모든 상태 — 스킬, 지식, 워크스페이스 등록, heartbeat 상태 — 가 git에 저장되고 자동으로 동기화됩니다.

**런타임 풋프린트: 25 MB RAM, 672 KB 디스크.** 하나의 Python 프로세스(MCP Memory Server)와 SQLite. 나머지는 OS 스케줄러로 실행 후 종료되거나, 브라우저에서 렌더링됩니다. 폴링 제로, 데몬 제로, 블로트 제로.

```
Disk: 672 KB (코드 + 설정, .git과 이미지 자산 제외)
RAM:  ~25 MB (MCP 서버, 유일한 상주 프로세스)
CPU:  0% 유휴 (폴링 없음, 데몬 없음 — OS 스케줄러가 깨움 담당)
```

---

## 빠른 시작

### 첫 번째 머신 (Hub 생성)

**Windows**
```powershell
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
.\install.ps1
# 4개 질문에 답하기 → 프라이빗 Hub 생성 완료 → 모든 설정 완료
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

### 설정 과정

설치 프로그램이 4개의 질문을 합니다. 그게 전부입니다. 나머지는 모두 자동입니다.

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
             ▼  이어서 9개의 자동화 단계
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

### 9개 단계의 내용

| 단계 | 동작 | 소요 시간 |
|------|--------|------|
| 1 | 사전 요구사항 확인 (Node, Python, Git) | 5초 |
| 2 | Claude Code + GitHub 인증 (OAuth 클릭 2회) | 30초 |
| 3 | **Hub 생성** (프라이빗 저장소) 또는 기존 것 클론 | 10초 |
| 4 | 설정 작성 | 5초 |
| 5 | MCP Memory Server 설치 (21개 도구) | 10초 |
| 6 | Claude Code 구성 (CLAUDE.md + .mcp.json) | 5초 |
| 7 | 워크스페이스 배포 (저장소 클론, memory.db 초기화) | 상황에 따라 |
| 8 | 스케줄러 + heartbeat 등록 | 5초 |
| 9 | 기존 시스템 흡수 (선택한 경우) | 상황에 따라 |

| 플랫폼 | 동기화 | Heartbeat |
|----------|------|-----------|
| Windows | Task Scheduler (30분) | Task Scheduler (30분) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | Container lifecycle | Container lifecycle |

**필요한 인증: OAuth 클릭 2회.** Oracle L4를 사용하지 않는 한 API 키 불필요.

### 나중에 머신 추가

Hub가 이미 GitHub에 있다면, 머신 추가는 더 간단합니다:

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

## Chapter 1: 메모리 — 에이전트는 기억한다

왜 중요한가: 대부분의 AI 에이전트는 매 세션을 제로에서 시작합니다. 같은 실수를 반복하고, 컨텍스트를 다시 학습하고, 시간을 낭비합니다.

### 4층 메모리 시스템

| 레이어 | 내용 | 속도 | 범위 |
|-------|------|-------|-------|
| **L1.5** | CC 자동 메모리 (네이티브) | 즉시 | 현재 프로젝트 |
| **L2** | SQLite + 24개 MCP 도구 | ~1ms | 워크스페이스별 |
| **L3** | Markdown 지식 베이스 | ~10ms | git 동기화 공유 |
| **L4** | Cloud DB (선택사항) | ~100ms | 워크스페이스 간 |

### Salience 엔진

중요한 기억은 떠오르고, 오래된 기억은 가라앉습니다:
- 각 접근: salience +5%
- 수동 강화: +20% (최대 2.0x 제한)
- 30일 미접근: -5%/일 감쇠 (최저 0.01, 삭제 없음)

**CJK 인식 토큰 추정** — 다국어 작업에 대한 정확한 압축 타이밍.

### 실제 동작 방식

메모리는 수동적인 저장소가 아닙니다 — 에이전트의 동작에 능동적으로 영향을 미칩니다.

```
당신이 결정을 내림
  → memory_record_decision("chose SQLite over Postgres", "local-first, no server needed")

다음 세션 시작
  → 부트 프로토콜이 중요한 결정 + 지식을 로드
  → Claude가 그 결정과 이유를 기억함

30일 후
  → 중요한 결정은 여전히 높은 salience (자주 접근됨 → 부스트)
  → 사소한 컨텍스트는 자연스럽게 감쇠 (하지만 절대 삭제되지 않음)
```

모든 궤적이 기록됩니다. 모든 워크스페이스가 공유됩니다. 에이전트들이 함께 성장합니다. 지식이 축적됩니다. 작업은 절대 소실되지 않습니다.

---

## Chapter 2: 워크스페이스 — 에이전트의 작업 공간

왜 중요한가: 구조화된 작업 장소가 없으면, 에이전트는 컨텍스트를 혼동하고, 프로젝트를 엉망으로 만들고, 머신 간에 지식을 공유할 수 없습니다.

워크스페이스는 메모리, 스킬, spec 지원이 갖춰진 프로젝트 디렉토리입니다. 모든 워크스페이스는 git 저장소입니다 (보통 GitHub의 프라이빗 저장소).

### 워크스페이스 생성

두 가지 방법:

1. **`/spec new`** — 완전한 spec이 포함된 가이드 생성 (권장). 자세한 내용은 [Chapter 4](#chapter-4-spec--에이전트의-계획-방법)를 참조.
2. **`workspace-create.py`** — spec 없이 빠르게 생성:

```powershell
.\scripts\new-workspace.ps1 -name "my-api"
# 폴더, memory.db, CLAUDE.md, GitHub 저장소 생성 — 완료.
```

### 워크스페이스 구조

```
my-project/
├── CLAUDE.md              ← 프로젝트 전용 지시사항
├── .claude-memory/
│   └── memory.db          ← L2 메모리 (SQLite)
├── knowledge/             ← L3 지식 (git 동기화)
├── skills/learned/        ← 자동 생성된 스킬
├── openspec/              ← spec 산출물 (/spec 사용 시)
│   ├── project.md
│   ├── changes/
│   └── specs/
└── .blitz-active          ← blitz 실행 중 존재
```

### 워크스페이스 활성화 및 동기화

```
~/Documents/Workspace/
├── my-api/          ← 등록됨, 30분마다 동기화
├── data-pipeline/   ← 등록됨, 30분마다 동기화
└── random-notes/    ← git 저장소 아님, 동기화에서 제외
```

- 모든 활성 워크스페이스는 30분마다 git으로 동기화됩니다
- Web UI의 워크스페이스 탭에서 워크스페이스 ON/OFF를 전환합니다
- 비활성 워크스페이스는 동기화가 중단되지만 데이터는 유지됩니다
- 스케줄러가 워크스페이스 루트 아래의 모든 git 저장소를 자동 동기화합니다

### 멀티 머신 공유

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

- **L2**는 로컬에 유지 (빠름, 워크스페이스별) — 각 에이전트가 자체 캐시 보유
- **L3**는 git으로 동기화 — 모든 에이전트가 같은 지식 베이스를 읽고 씀
- **L4**는 모든 것을 통합 — 워크스페이스 간 검색, 감사 추적, 전체 이력
- **새 에이전트 합류?** `git clone + install.ps1` — 축적된 모든 지식을 즉시 상속

### 상시 가동 — Heartbeat

에이전트는 절대 죽지 않습니다. OS 스케줄러가 30분마다 확인: 각 워크스페이스 세션이 살아있나? 아니라면 `claude --resume`으로 복활 — 완전한 컨텍스트 복원.

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

- **터미널 열림** — 세션 활성, 에이전트가 완전한 컨텍스트를 가지고 24/7 동작
- **터미널 닫힘** — heartbeat가 감지, 자동으로 복활
- **모든 세션** — Claude Code Remote로 어떤 기기에서든 확인 가능
- **커스텀 데몬 없음** — OS 스케줄러가 워치독. 크래시 없음. 유지보수 제로.

### 예약 자동화

OS 레벨 스케줄러 (Windows Task Scheduler / cron / launchd) — Claude Code가 실행 중이 아니어도 동작:

- **Heartbeat** — 모든 워크스페이스 세션이 살아있도록 보장 (죽으면 복활)
- **Git 동기화** — 30분마다 모든 저장소 Pull 및 Push
- **Salience 감쇠** — 매일 메모리 중요도 조정
- **클라이언트 상태** — 각 머신의 세션, 마지막 heartbeat, 배포된 워크스페이스 추적

---

## Chapter 3: 스킬 — 에이전트가 할 수 있는 것

왜 중요한가: Claude Code에는 내장 스킬이 있지만, 직접 추가하거나, 수정하거나, 팀과 공유할 수 없습니다. 스킬은 여러분의 경쟁 우위입니다.

스킬은 독립적인 모듈입니다. AI 에이전트용 Chrome 확장 프로그램이라고 생각하세요.

### 세 가지 스킬 소스

| 탭 | 내용 | 전환 가능? |
|---|---|---|
| **Claude Native** | 내장: `/batch`, `/loop`, `/simplify`, `/compact` 등 | 스킬: 가능 (권한 통해). 명령: 읽기 전용. |
| **Clawd-Lobster** | 관리형: memory, heartbeat, evolve, absorb, spec, connect-odoo | 가능 — 전체 수명주기 |
| **Custom / Hub** | 직접 만든 것 + ClawHub에서 다운로드한 커뮤니티 스킬 | 가능 — 전체 수명주기 |

하나의 통합 뷰. 세 가지 소스. 여러분 시스템의 모든 스킬 — Anthropic에서 온 것이든, Clawd-Lobster에서 온 것이든, 직접 만든 것이든 — 한 곳에서 확인하고 관리할 수 있습니다.

### 핵심 스킬 (잠금 — 비활성화 불가)

| 스킬 | 기능 | 잠금 이유 |
|---|---|---|
| Memory Server | 28 도구 MCP 메모리 + SQLite | 메모리 없음 = 에이전트 없음 |
| Heartbeat | OS 스케줄러를 통한 세션 유지 | heartbeat 없음 = 세션이 죽음 |
| Evolve | 자기 진화 + TODO 처리 | 핵심 차별화 기능 |
| Absorb | 모든 소스에서 지식 흡수 | 핵심 학습 능력 |
| Spec | 가이드 기반 기획 + blitz 실행 | 핵심 개발 워크플로 |

### 선택 스킬

| 스킬 | 기능 | 기본값 |
|---|---|---|
| Migrate | 다른 AI 설정에서 가져오기 | 활성화 |
| Connect-Odoo | Odoo ERP 연동 (XML-RPC) | 비활성화 |
| Codex Bridge | OpenAI Codex에 작업 위임 (worker + critic) | 비활성화 |
| NotebookLM Bridge | Google NotebookLM을 통한 무료 RAG + 콘텐츠 엔진 | 비활성화 |

### 스킬 관리

모든 스킬은 `skill.json` 매니페스트를 가진 독립 모듈입니다. **Web UI** 또는 **CLI**로 관리합니다.

**Web Dashboard** — `webapp/index.html`을 열기:
- 카드 그리드에 ON/OFF 토글, 상태 표시, 카테고리 필터, 검색
- 인라인 설정 — 스킬별로 설정과 자격 증명 편집
- 헬스 체크 — 활성화된 모든 스킬에 녹색/노란색/빨간색 상태 표시

**CLI 관리 도구:**

```bash
python scripts/skill-manager.py list                     # 모든 스킬 목록
python scripts/skill-manager.py enable connect-odoo      # 스킬 활성화
python scripts/skill-manager.py disable connect-odoo     # 스킬 비활성화
python scripts/skill-manager.py status                   # 상세 상태
python scripts/skill-manager.py config connect-odoo      # 설정 보기/편집
python scripts/skill-manager.py credentials connect-odoo # 자격 증명 관리
python scripts/skill-manager.py health                   # 모든 헬스 체크 실행
python scripts/skill-manager.py reconcile                # .mcp.json + settings.json 재생성
```

### 직접 스킬 추가하기

1. `skills/my-skill/skill.json` 생성 — 매니페스트가 모든 것을 선언:

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

2. 스킬 구현 (MCP 서버, 스크립트, 또는 SKILL.md)
3. `skill-manager.py reconcile` 실행 — 자동으로 등록하고 `.mcp.json` + `settings.json` 업데이트

**스킬은 설정 3개로 끝입니다.** SDK 불필요. 플러그인 API 불필요. 프레임워크 종속 없음. 매니페스트**가** 계약입니다.

---

## Chapter 4: Spec — 에이전트의 계획 방법

왜 중요한가: 계획 없는 자율 실행은 무작위 코드 생성일 뿐입니다. Spec 주도 개발은 Claude에게 따를 청사진을 줍니다.

OpenSpec 방법론에 기반합니다. Claude가 기획을 안내하고, 그 다음 자율적으로 실행합니다.

### 흐름

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

### 3W1H 표준

모든 산출물은 Why, What, Who, How를 적절한 수준에서 따릅니다:

| 산출물 | 수준 |
|---|---|
| project.md | 광범위한 컨텍스트 캡처 |
| proposal.md | 범위 정의 |
| design.md | 아키텍처 청사진 |
| specs/ | 테스트 가능한 요구사항 (SHALL/MUST + Gherkin) |
| tasks.md | 실행 계획 (단계별, 파일 경로 참조) |

기획부터 의사결정, 로그, 아카이브까지 동일한 표준이 일관되게 적용됩니다.

### Blitz 모드

전속력 자율 실행. Spec이 계획 — 질문 없이, 실행만.

- **브랜치 격리** — 모든 작업은 `blitz/v1`에서 진행, main은 검증 전까지 보호
- **단계별 커밋** — 각 단계 완료 후 `git commit`
- **진화 일시 중지** — `.blitz-active` 마커가 evolve-tick에 이 워크스페이스를 건너뛰라고 알림
- **위임 마커** — `[codex]` 접두사가 붙은 태스크는 외부 실행을 위해 건너뜀
- **Blitz 완료 후** — main에 머지, spec을 지식으로 저장, 다음 단계 제안

### 검증

- 각 산출물 완료 후 자체 검증 실행 (proposal, design, specs, tasks)
- 요구사항은 반드시 SHALL 또는 MUST 사용 — "should", "could", "might"는 불가
- 모든 요구사항에 최소 하나의 Gherkin 시나리오
- 모든 태스크에 파일 경로 포함, 5-30분 내 완료 가능한 범위
- 산출물 DAG는 엄격: project → proposal → design → specs → tasks

### 명령어

| 명령어 | 기능 |
|---|---|
| `/spec new` | 가이드 기반 워크스페이스 + spec 생성 |
| `/spec:status` | 진행 상황 표시 (단계별 진행 바 포함) |
| `/spec:add "feature"` | 기존 spec에 추가 (증분 작업) |
| `/spec:blitz` | blitz 실행 시작/재개 |
| `/spec:archive` | 완료된 변경 아카이브 + 지식으로 저장 |

---

## Chapter 5: 진화 — 에이전트의 발전 방법

왜 중요한가: v1은 시작일 뿐입니다. 자신의 작업에서 배우지 못하는 에이전트는 성장이 멈추는 에이전트입니다.

v1을 만든 후, 에이전트는 자동으로 계속 좋아집니다.

### 진화 루프

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

### 3단계 콘텐츠 파이프라인

Claude, Codex, Gemini 간의 3자 AI 토론에서 콘텐츠 생성 파이프라인이 확립되었습니다:

1. **리서치** — 소스 수집, 컨텍스트 흡수, 핵심 인사이트 추출
2. **토론** — 다수의 AI 관점이 콘텐츠를 도전하고 정제
3. **생성** — NotebookLM을 통한 최종 출력 (슬라이드, 인포그래픽, 팟캐스트, 영상, 퀴즈)

### 흡수 (Absorb)

무엇이든 넣을 수 있습니다 — 폴더, GitHub 저장소, URL. Claude가 발견한 모든 것을 자동으로 분류합니다:

```
Detected environments:
  ✓ claude-setup     → 11 workspaces, Oracle config, soul files
  ✓ Raw Claude Code  → CLAUDE.md, auto-memory, sessions
  ✓ OpenClaw         → SOUL.md, MEMORY.md, skills, approvals
  ✓ Hermes Agent     → skills, memory, profiles
```

파서 스크립트가 필요 없습니다. Claude Code **자체가** 파서입니다 — 어떤 형식이든 읽고, 의미를 이해하고, 중요한 것을 저장합니다. 세 가지 스캔 깊이:

| 깊이 | 내용 |
|---|---|
| `shallow` | README, CLAUDE.md, 최상위 설정 파일 |
| `normal` | shallow 전부 + 핵심 소스 파일, 스킬 정의, 중요 문서 |
| `deep` | 전체 코드베이스 분석 — 모든 소스 파일, 테스트, CI 설정, 스크립트 |

항목은 지식 (사실, 아키텍처), 결정 (경험, 함정), 스킬 (재사용 가능한 패턴), TODO (실행 항목)로 분류됩니다.

### 진화 (자동)

2시간마다 `evolve-tick.py`가 대기 중인 TODO 하나를 선택하고, 격리된 git worktree에서 작업합니다. 핵심 특성:

- **tick당 TODO 하나** — 간단하고 안전하게
- **자동 머지 없음** — 모든 작업은 `evolve/<id>` 브랜치에서 리뷰 대기
- **학습된 스킬 영구 보존** — 데이터베이스와 git 동기화 스킬 파일 양쪽에 저장
- **효과성 추적** — 사용할 때마다 +2%, 개선할 때마다 +10%, 검증된 스킬 점수 > 2.0x
- **에이전트 간 공유** — Agent A에서 학습한 스킬은 git 동기화로 Agent B에서 사용 가능
- **자연 은퇴** — 90일 이상 미사용 스킬은 오래된 것으로 표시
- **지식 복리 효과** — 한 워크스페이스의 결정이 다른 워크스페이스의 작업에 반영되며, 해결된 문제는 두 번 해결하지 않음

### Blitz vs 진화

| | Blitz | 진화 |
|---|---|---|
| 시점 | spec에서 v1 구축 | v1 이후 지속 개선 |
| 속도 | 모든 태스크, 논스톱 | 2시간마다 TODO 하나 |
| 범위 | 전체 프로젝트 | 개별 개선 |
| 브랜치 | `blitz/v1` (완료 시 머지) | `evolve/<id>` (개별 리뷰) |
| 자동 머지 | 있음 (blitz 브랜치 내) | 없음 — 사람이 리뷰 |

---

## 아키텍처

내부 동작을 이해하고 싶은 엔지니어를 위한 섹션입니다.

### 내부 구조

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

### 실제로 실행되는 것은?

전체 저장소는 약 ~13K 줄이지만, 대부분은 설치 파일, 문서, Claude가 읽을 지시사항입니다. 에이전트가 작업 중일 때 실제로 메모리를 점유하는 것은:

| 레이어 | 내용 | 줄 수 | RAM | 시점 |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (28 tools + SQLite) | ~1,400 | ~25 MB | 상시 |
| **Runtime** | Odoo Connector (if enabled) | ~280 | ~22 MB | 활성화 시 |
| **Cron** | evolve-tick (TODO processor) | ~465 | ~20 MB peak | 2시간마다, 실행 후 종료 |
| **Cron** | heartbeat + sync | ~300 | ~5 MB peak | 30분마다, 실행 후 종료 |
| **Static** | Web UI (browser renders it) | ~1,900 | 0 on server | 필요 시 |
| **Setup** | Installers, workspace-create, skill-manager | ~2,800 | 0 | 한 번만 실행 |
| **Docs** | SKILL.md files, README, CHANGELOG | ~3,500 | 0 | Claude가 필요 시 읽음 |
| **Config** | skill.json manifests, templates | ~900 | 0 | 시작 시 읽음 |

**상주 풋프린트: Python 프로세스 하나 (~25 MB) + SQLite.** 나머지는 실행 후 종료 (cron 스크립트)되거나, 브라우저 안에 있거나 (Web UI), Claude가 컨텍스트 필요 시 읽는 파일일 뿐입니다.

### Claude Code와의 관계

다른 프레임워크는 Claude를 처음부터 다시 만들고, 실제 사고를 위해 Claude의 API를 호출합니다:

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

우리는 Claude의 API를 호출하지 않습니다. OAuth 토큰을 관리하지 않습니다. Rate limit을 처리하지 않습니다. 우리가 스케줄링하는 것은 **Claude Code 자체** — Anthropic이 직접 만들고, 배포하고, 유지보수하는 도구입니다. Anthropic이 개선하면, 우리도 빨라집니다. API가 바뀌어도, 영향 없습니다.

다른 프레임워크는 **남의 차**의 리모컨을 만들고 있습니다. 우리는 **차 안에** 앉아 있습니다.

### GitHub와의 관계

GitHub가 모든 것의 컨트롤 플레인입니다:

- **Hub 저장소** — 여러분의 프라이빗 커맨드 센터
- **워크스페이스 저장소** — 각 프로젝트는 프라이빗 저장소
- **Git 동기화** — 지식, 스킬, 상태가 30분마다 동기화
- **Heartbeat 상태** — 머신 상태가 git에 푸시
- **Spec 산출물** — 워크스페이스 저장소에 커밋

### 왜 직접 엔진을 만들지 않는가?

다른 프레임워크는 AI 에이전트 전체를 처음부터 다시 만듭니다 — 30만 줄의 코드, 커스텀 에이전트 루프, 커스텀 도구 시스템, 모든 것이 커스텀입니다. Anthropic이 더 좋은 모델을 출시하면, 어댑터를 급히 재작성합니다.

**Clawd-Lobster는 Claude Code와 경쟁하지 않습니다. Claude Code를 완성합니다.**

Claude Code — 세계에서 가장 진보된 코딩 에이전트 — 에서 시작하여, 부족한 것만 정확히 추가합니다: 영구 메모리, 멀티 에이전트 오케스트레이션, 엄선된 스킬. 그 이상도, 그 이하도 없습니다.

> *제로 블로트. 제로 재작성. 순수한 Claude Code, 증폭.*

### 설계 철학

#### 1. 최고의 에이전트는 이미 존재합니다. 그것을 사용하세요.

Claude Code는 세계 최대의 AI 안전 연구소가 지원합니다. 수백만 시간의 엔지니어링이 에이전트 루프, 스트리밍, 권한, 도구 시스템에 투입되었습니다. 처음부터 다시 만드는 것은 야심이 아닙니다 — 낭비입니다. **거인의 어깨 위에 서세요.**

#### 2. 적을수록 좋습니다. 훨씬 더.

프레임워크 코드의 모든 줄은 유지보수해야 할 줄입니다. Clawd-Lobster가 ~2K 줄인 이유는 Claude Code의 네이티브 확장 포인트 (MCP, hooks, CLAUDE.md)가 이미 최고의 플러그인 시스템이기 때문입니다. **설정 3개 = 스킬 하나. SDK 제로.**

#### 3. 잊는 에이전트는 실패하는 에이전트입니다.

대부분의 AI 에이전트는 매 세션을 제로에서 시작합니다. 실수를 반복하고, 컨텍스트를 다시 학습하고, 시간을 낭비합니다. Clawd-Lobster의 salience 추적이 포함된 4층 메모리는 **중요한 것이 떠오르고, 노이즈는 사라지며, 중요한 것은 절대 잃어버리지 않도록** 보장합니다.

#### 4. 에이전트는 어디서든 따라와야 합니다.

컴퓨터 한 대? 좋습니다. 세 대? 모두 같은 두뇌를 공유해야 합니다. GitHub을 컨트롤 플레인으로, git 동기화를 프로토콜로. **2분 만에 머신 추가. 인프라 제로.**

#### 5. 항상 최신 물결을 타세요.

Anthropic이 Opus 4.7, 1M 컨텍스트, 새로운 도구를 출시하면 — 즉시 받을 수 있습니다. 어댑터 재작성 없음. 버전 고정 없음. 커뮤니티 패치 대기 없음. **Claude Code를 사용하기 가장 좋은 때는 어제였습니다. 두 번째로 좋은 때는 지금입니다.**

#### 6. 스케줄링할 수 있으면 직접 만들지 마세요.

다른 프레임워크는 커스텀 데몬을 만들어 에이전트를 24/7로 실행합니다. 우리는 `cron` + `claude --resume`을 사용합니다. 다른 프레임워크는 OAuth 토큰을 관리해 Claude의 API를 호출합니다. 우리는 사용자에게 `claude login`을 한 번만 입력하게 합니다. **여러분이 작성하는 인증 코드의 모든 줄은, 공급자가 변경할 때 깨질 수 있는 줄입니다. 작성하지 않은 모든 줄은, 깨질 수 없는 줄입니다.** OS 스케줄러는 1970년대부터 안정적으로 동작하고 있습니다. 여러분의 커스텀 데몬은 지난 화요일에 작성된 것입니다.

#### 7. 거인이 키가 자라면, 여러분도 함께 자랍니다.

Claude Code 내부에는 메모리 통합 (autoDream), 상시 가동 에이전트 (KAIROS), 멀티 에이전트 조정 (Coordinator Mode), 복잡한 계획 수립 (ULTRAPLAN)의 시스템이 있습니다. 일부는 라이브, 일부는 feature flag 뒤에. 우리는 2K 줄로 대부분의 동등한 기능을 이미 구축했습니다.

하지만 핵심은: **Anthropic이 이 기능들을 네이티브로 출시하면, 우리는 재작성하지 않습니다 — 은퇴시킵니다.** KAIROS가 라이브? heartbeat가 우아하게 물러납니다. autoDream이 개선? salience 엔진과 공존합니다. Coordinator Mode가 출시? evolve-tick이 그것을 사용합니다.

다른 프레임워크는 Claude Code와 경쟁합니다. 우리는 보완합니다. Claude Code가 기능을 추가할 때, 그들은 재작성해야 합니다. 우리는 코드를 삭제할 기회를 얻습니다. **우리의 코드베이스는 시간이 지날수록 줄어들고, 그들의 것은 계속 늘어납니다.**

### 프로젝트 구조

```
clawd-lobster/
├── skills/                          스킬 모듈 (각각 skill.json 매니페스트 포함)
│   ├── memory-server/               24 도구 MCP 메모리 + salience + 진화
│   │   ├── mcp_memory/              Python package (pip install -e .)
│   │   └── skill.json               Manifest
│   ├── connect-odoo/                Odoo ERP 연동 (XML-RPC + poller)
│   │   ├── connect_odoo/            MCP server + poller
│   │   └── skill.json               Manifest
│   ├── evolve/                      자기 진화 prompt pattern
│   │   └── skill.json               Manifest
│   ├── heartbeat/                   세션 유지 (cron)
│   │   └── skill.json               Manifest
│   ├── absorb/                      모든 소스에서 지식 흡수
│   │   └── skill.json               Manifest
│   ├── spec/                        가이드 플래닝 + blitz 실행
│   │   └── skill.json               Manifest
│   ├── codex-bridge/                OpenAI Codex에 작업 위임
│   │   └── skill.json               Manifest
│   ├── notebooklm-bridge/           NotebookLM을 통한 무료 RAG + 콘텐츠 엔진
│   │   └── skill.json               Manifest
│   ├── migrate/                     기존 설정에서 가져오기
│   │   └── skill.json               Manifest
│   └── learned/                     경험에서 자동 생성된 스킬
│
├── scripts/
│   ├── skill-manager.py             스킬 관리 CLI
│   ├── sync-all.ps1                 Windows: 자동 git 동기화 + 감쇠
│   ├── sync-all.sh                  Linux/macOS: 자동 git 동기화 + 감쇠
│   ├── heartbeat.ps1                Windows: 세션 유지
│   ├── heartbeat.sh                 Linux/macOS: 세션 유지
│   ├── new-workspace.ps1            워크스페이스 + GitHub 저장소 생성
│   ├── workspace-create.py          자동 워크스페이스 생성
│   ├── validate-spec.py             Spec 산출물 검증
│   ├── setup-hooks.sh               git pre-commit hooks 설치 (Unix)
│   ├── setup-hooks.ps1              git pre-commit hooks 설치 (Windows)
│   ├── evolve-tick.py               패턴 추출 + 제안 + salience 감쇠
│   ├── notebooklm-sync.py           워크스페이스 문서를 NotebookLM에 자동 푸시
│   ├── init_db.py                   메모리 데이터베이스 초기화
│   └── security-scan.py             5 도구 보안 스캐너
│
├── templates/                       설정 템플릿 (시크릿 없음)
│   ├── global-CLAUDE.md
│   ├── workspace-CLAUDE.md
│   ├── mcp.json.template
│   └── settings.json.template
│
├── webapp/                          스킬 관리 Dashboard
│   └── index.html                   3탭 UI: Skills + Setup + Settings
│
├── knowledge/                       공유 지식 베이스 (git 동기화)
├── soul/                            에이전트 성격 (선택사항)
├── workspaces.json                  워크스페이스 레지스트리
├── install.ps1                      Windows 설치 프로그램 (4단계)
├── install.sh                       Linux/macOS 설치 프로그램 (4단계)
├── Dockerfile                       Docker build
├── docker-compose.yml               Docker Compose 설정
├── LICENSE                          MIT
└── README.md
```

---

## 비교

| | Claude Code (기본) | OpenClaw | Hermes Agent | **Clawd-Lobster** |
|---|---|---|---|---|
| 에이전트 엔진 | Anthropic | 커스텀 (300K LOC) | 커스텀 (50K LOC) | **Anthropic (네이티브)** |
| 인증 모델 | 사람이 로그인 | OAuth/API 키 | API 키 | **사람이 한 번 로그인** |
| 비용 모델 | 구독제 | 토큰당 과금 API | 토큰당 과금 API | **구독제 (정액)** |
| 상시 가동 | 없음 | 커스텀 데몬 | 커스텀 데몬 | **OS heartbeat + 자동 복활** |
| 영구 메모리 | 없음 | 하이브리드 검색 | FTS5 + LLM | **4층 + salience** |
| 멀티 에이전트 공유 메모리 | 없음 | 없음 | 없음 | **있음 (git 동기화)** |
| 스킬 관리 | N/A | CLI만 | 수동 | **Web UI + CLI + 매니페스트** |
| 에이전트 진화 | 없음 | 없음 | 자기 개선 스킬 | **있음 (24 MCP 도구)** |
| 멀티 머신 | 없음 | 없음 | 없음 | **있음 (MDM 방식)** |
| 세션 관리 | 수동 | Gateway 프로세스 | 수동 | **모든 세션 자동 복활** |
| 온보딩 | 수동 | 복잡 | 보통 | **웹 마법사, 5개 언어** |
| 자동 업그레이드 | 있음 | 없음 | 없음 | **있음** |
| 코드베이스 규모 | 0 | ~300K LOC | ~50K LOC | **~2K LOC** |
| Anthropic API 변경 | 투명 | 파괴적 | 파괴적 | **투명** |
| 감사 추적 | 없음 | 보안 감사 | 없음 | **전체 (모든 행동)** |
| 스킬 설치 | — | Plugin SDK | 파일 3개 변경 | **매니페스트 1개 + reconcile** |

---

## 로드맵

**스킬**
- [x] Odoo ERP Connector — XML-RPC 연동 + poller (v0.4.0)
- [x] Codex Bridge — OpenAI Codex에 작업 위임, worker + critic 역할 (v0.5.0)
- [x] NotebookLM Bridge — Google NotebookLM을 통한 무료 RAG + 콘텐츠 엔진 (v0.5.0)
- [x] Spec 기반 개발 — OpenSpec 방법론을 활용한 가이드 플래닝 (v0.5.0)
- [ ] SearXNG — 프라이빗 자체 호스팅 웹 검색, 데이터가 네트워크 밖으로 나가지 않음
- [ ] Docker Sandbox — 신뢰할 수 없는 작업을 위한 격리된 코드 실행
- [ ] Browser Automation — Playwright 기반 웹 상호작용

**플랫폼**
- [x] Linux 설치 프로그램 (bash) + macOS 설치 프로그램 (v0.3.0)
- [x] 스킬 관리 Dashboard — Web UI + CLI로 스킬 전체 수명주기 관리 (v0.4.0)
- [x] 스킬 매니페스트 시스템 — `skill.json`에 설정, 자격 증명, 헬스 체크 (v0.4.0)
- [ ] Supabase L4 — 원클릭 클라우드 데이터베이스 (Oracle wallet 불필요)

**진화**
- [x] 진화 루프 + 제안 — evolve가 git 동기화된 제안을 생성, 직접 TODO가 아님 (v0.5.0)
- [ ] 스킬 마켓플레이스 — 커뮤니티 기여 스킬, 원클릭 설치
- [x] 자동 스킬 생성 — 에이전트가 성공 패턴에서 학습 (v0.3.0 evolve skill)
- [ ] 팀 모드 — 역할 기반 접근 제어가 있는 다중 사용자 공유 워크스페이스
- [ ] 에이전트 간 위임 — 에이전트가 서로에게 작업을 할당

---

## FAQ

### "이게 그냥 Claude Code에 껍데기 씌운 거 아니에요?"

네. 그게 핵심입니다.

Claude Code는 현존하는 가장 강력한 코딩 에이전트입니다 — Anthropic의 수백만 시간 엔지니어링이 뒷받침합니다. OpenClaw는 엔진을 처음부터 다시 만듭니다 (30만 줄). Hermes도 또 만듭니다 (5만 줄). 우리는 부족한 부분만 추가하고 (2천 줄), 최고의 엔진을 유지합니다.

Anthropic이 다음 돌파구를 출시하면, 우리는 즉시 혜택을 받습니다. 그들은 어댑터 재작성에 쫓기게 됩니다.

### "하지만 다른 에이전트는 24/7로 돌면서 계속 학습하는데"

우리도 그렇습니다. 스케줄러가 30분마다 지식을 동기화합니다. 메모리는 salience 감쇠로 매일 자연스럽게 진화합니다. 학습된 스킬은 git을 통해 모든 머신에 전파됩니다. **에이전트가 항상 실행 중이 아니어도, 지식은 계속 성장합니다.**

heartbeat가 세션을 계속 살려둡니다: 터미널이 닫히면, OS 스케줄러가 감지하고 `claude --resume`으로 복활 — 완전한 컨텍스트 복원. 커스텀 데몬 불필요. 그냥 Claude Code가 항상 켜져 있습니다. 토큰당 과금 API 프레임워크와 24/7을 어떻게 다르게 다루는지는 [아키텍처](#claude-code와의-관계) 섹션을 참조하세요.

### "다른 에이전트에도 heartbeat와 시간 인식이 있다"

우리도 있습니다 — 다만 더 똑똑하게. 커스텀 데몬 프로세스를 실행하는 대신, OS 스케줄러 (Task Scheduler / launchd / cron)를 heartbeat로 사용합니다. 30분마다 확인: 세션 살아있나? Git 동기화 필요한가? Salience 감쇠 시간인가? 클라이언트 상태는? 모두 처리 완료. OS 스케줄러는 크래시하지 않고, 디버깅 불필요하고, 유휴 시 토큰을 소모하지 않습니다. Claude Code가 네이티브 24/7 모드 (KAIROS — 코드베이스에 이미 존재)를 출시하면, 무료로 받습니다. 코드 변경 제로. 자세한 내용은 [Chapter 2](#상시-가동--heartbeat)를 참조.

### "Claude Code에 이미 내장 스킬이 있는데, 왜 더 필요해?"

Claude Code에는 `/commit`, `/review-pr`, `/init` 등의 스킬이 내장되어 있습니다. 좋은 것들입니다. 하지만 **폐쇄적**이기도 합니다 — Anthropic이 기능, 동작, 변경 시점을 결정합니다. 직접 추가할 수 없습니다. 수정할 수 없습니다. 팀과 공유할 수 없습니다.

그것은 스마트폰의 내장 앱입니다. Clawd-Lobster는 App Store입니다.

| | Claude Code 내장 | **Clawd-Lobster 스킬** |
|---|---|---|
| 누가 만드나 | Anthropic | 여러분, 여러분의 팀, 커뮤니티 |
| 누가 제어하나 | Anthropic | 여러분 |
| 수정 가능한가 | 불가 | 가능 — 여러분의 코드 |
| 추가 가능한가 | 불가 | 가능 — `skill.json` + 구현 |
| 공유 가능한가 | 불가 | 가능 — GitHub / ClawHub에 푸시 |
| 도메인 특화 | 불가 (범용 개발 도구) | 가능 — 여러분의 ERP, CRM, 워크플로 |
| 자격 증명 관리 | N/A | 스킬별 자격 증명 시스템 내장 |
| 활성화/비활성화 | N/A | 토글 하나, Web UI 또는 CLI |

여러분의 회사가 배포 전 컴플라이언스 체크를 실행하는 스킬이 필요한가요? Odoo에서 5분마다 CRM 데이터를 동기화하는 스킬? 여러분만의 형식으로 이중 언어 PDF 보고서를 생성하는 스킬? Claude Code는 절대 그런 것을 출시하지 않습니다. **여러분의 스킬은 여러분의 경쟁 우위입니다. 그것은 다른 사람의 시스템이 아닌, 여러분의 시스템에 있어야 합니다.**

### "Claude Code에 이미 MCP와 스킬이 있는데, 왜 또 하나의 레이어가 필요해?"

Claude Code는 MCP를 제공합니다 — 도구 서버를 등록하는 프로토콜입니다. Chrome이 확장 프로그램을 설치할 수 있다고 말하는 것과 같습니다. 맞습니다. 하지만 Chrome에는 **Chrome 웹 스토어**도 있습니다 — `.crx` 파일을 수동으로 설치하는 것은 확장 프로그램 관리가 아니기 때문입니다.

Claude Code가 제공하는 것:
- `.mcp.json` — 평면적인 서버 명령 목록. 메타데이터 없음. 수명주기 없음.
- `settings.json` — 평면적인 허용 도구 목록. 그룹핑 없음. 토글 없음.
- `CLAUDE.md` — 자유 형식 텍스트. 스키마 없음. 유효성 검증 없음.

실제로 이것이 의미하는 바:
- **스킬 설치?** JSON 파일 3개를 수동으로 편집하고 `pip install` 실행.
- **스킬 비활성화?** 파일 2개에서 항목을 수동으로 삭제. 다 지웠기를 바라야 함.
- **자격 증명?** 스킬마다 저장 방식이 다름. 환경 변수, 파일, 하드코딩 등.
- **작동 중인가?** 모름. 터미널 열고 행운을 빎.
- **두 번째 머신?** 전부 처음부터 다시.
- **스킬 10개?** `.mcp.json`이 읽을 수 없는 JSON 벽이 됨. 행운을 빕니다.

Clawd-Lobster의 스킬 레이어가 MCP에 없는 것을 추가합니다:

| MCP (기본) | 스킬 관리 (우리 것) |
|---|---|
| 평면 JSON 설정 | `skill.json` 매니페스트 (스키마, 자격 증명, 헬스 체크, 의존성) |
| 수동 편집으로 설치 | `skill-manager.py enable <id>` — 명령어 하나 |
| 수동 편집으로 제거 | `skill-manager.py disable <id>` — 명령어 하나, 깔끔한 제거 |
| 자격 증명 표준 없음 | `~/.clawd-lobster/credentials/`에 집중, 스킬별 필드 정의 |
| 헬스 모니터링 없음 | 헬스 체크 내장 (mcp-ping, command, HTTP) |
| UI 없음 | 웹 대시보드 (카드 그리드, 토글, 검색, 카테고리 필터) |
| 머신별 설정 | git으로 머신 간 레지스트리 동기화 |
| 의존성 추적 없음 | 스킬이 필요한 것 (다른 스킬, 시스템 도구, Python 패키지) 선언 |

**MCP는 프로토콜입니다. 우리는 패키지 매니저입니다.**

`npm`이 Node.js를 대체하지 않는 것처럼 — Node.js를 대규모로 사용 가능하게 만듭니다. 우리의 스킬 레이어는 MCP를 대체하지 않습니다 — 5개, 10개, 50개의 스킬이 여러 머신에 걸쳐 있을 때 MCP를 관리 가능하게 만듭니다. 전체 스킬 관리 시스템은 [Chapter 3](#chapter-3-스킬--에이전트가-할-수-있는-것)을 참조하세요.

### "Anthropic이 이것을 차단하지 않을까?"

우리는 Anthropic이 금지하는 것을 아무것도 하지 않습니다. 정확히 말하면:

- **우리가 하는 것:** OS cron/Task Scheduler로 `claude` CLI 명령어를 스케줄링. `claude --resume`으로 기존 세션 재개. Anthropic 자체가 정의한 MCP 프로토콜 사용.
- **우리가 하지 않는 것:** 프로그래밍 방식 OAuth 로그인. API 키 자동화. 토큰 스크래핑. 인증 우회. 리버스 엔지니어링.

사용자가 `claude login`을 한 번 실행합니다 — 사람이, 브라우저에서, Pro 구독으로. 그 후, OS 스케줄러가 Anthropic이 자사 CLI에 직접 제공한 플래그 (`--resume`, `-p`, `--allowedTools`)를 사용해 세션을 유지합니다. cron으로 `git pull`을 스케줄링하는 것과 다를 바 없습니다. **우리는 CLI 도구를 자동화합니다. 사용자를 사칭하는 것이 아닙니다.**

다른 프레임워크는 Claude의 API를 직접 호출합니다 — API 키가 필요하고, OAuth 리프레시 토큰을 관리하고, rate limit을 처리하고, 가격이 변하지 않기를 기도합니다. 모든 API 변경이 그들에게는 파괴적입니다. 우리에게는 투명합니다 — Claude Code가 자체 인증을 처리합니다.

### "무거운 작업의 API 비용은?"

"비싼 API"라는 주장은 토큰당 과금을 전제합니다. Pro 구독 ($20/월)이 있으면, **토큰당 비용이 없습니다.** 첫 번째 작업과 480번째 작업의 비용이 같습니다: 한계 비용 $0.

이것은 다른 프레임워크가 필요로 하는 "사고에는 비싼 모델, 노동에는 싼 모델" 아키텍처를 완전히 없앱니다. 로컬에서 Ollama 7B를 실행해 저렴한 작업을 처리할 필요가 없습니다. 두 개의 추론 스택이 필요 없습니다. 어떤 두뇌를 쓸지 결정하는 모델 라우터도 필요 없습니다.

하나의 구독. 하나의 엔진. 하나의 두뇌. 무제한 작업.

Rate limit에 도달하면 (언젠가는 그럽니다), Clawd-Lobster의 skill-manager가 우아하게 작업을 큐잉합니다. 토큰 예산 공포 없음. 깜짝 청구서 없음. **예측 가능한 비용 자체가 기능입니다.**

---

## 기여하기

기여를 환영합니다! 가장 쉬운 기여 방법:

1. **스킬 추가** — `skills/` 폴더에 `SKILL.md` 또는 MCP server를 포함한 폴더를 생성
2. **템플릿 개선** — `templates/`의 기본값 개선
3. **플랫폼 지원** — Linux/macOS 설치 프로그램 개발에 도움

---

## 라이선스

MIT — 원하는 대로 사용하세요.

---

<p align="center">
<sub>Anthropic과 제휴 관계가 아닙니다. <a href="https://claude.ai/code">Claude Code</a> 위에 구축되었습니다.</sub>
</p>
