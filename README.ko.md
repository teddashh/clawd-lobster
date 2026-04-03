🌐 [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [**한국어**](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-0.5.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Runtime](https://img.shields.io/badge/footprint-25MB_RAM-orange)

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

## 요구 사항

- **Node.js** 18+ 및 **Python** 3.11+ 및 **Git** 2.x+
- **Claude Code** CLI（[설치 가이드](https://docs.anthropic.com/en/docs/claude-code/getting-started)）
- **GitHub** 계정（프라이빗 Hub 저장소용）

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
             ▼
  그 후 9개의 자동화된 단계가 실행됩니다:
```

### 9개 단계의 내용

| 단계 | 동작 | 소요 시간 |
|------|--------|------|
| 1 | 사전 요구사항 확인 (Node, Python, Git) | 5초 |
| 2 | Claude Code + GitHub 인증 (OAuth 클릭 2회) | 30초 |
| 3 | **Hub 생성** (프라이빗 저장소) 또는 기존 것 클론 | 10초 |
| 4 | 설정 작성 | 5초 |
| 5 | MCP Memory Server 설치 (32개 도구) | 10초 |
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
| **L2** | SQLite + 32개 MCP 도구 | ~1ms | 워크스페이스별 |
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
| Memory Server | 32 도구 MCP 메모리 + SQLite | 메모리 없음 = 에이전트 없음 |
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
| **Runtime** | MCP Memory Server (32 tools + SQLite) | ~1,400 | ~25 MB | 상시 |
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

### 설계 철학

**1. 거인의 어깨 위에 서라.** Claude Code 뒤에는 수백만 시간의 엔지니어링이 있다. 처음부터 다시 만드는 것은 야망이 아니라 낭비다. 부족한 부분만 추가하고(~2K 줄), 최고의 엔진을 유지한다.

**2. 적은 코드, 적은 장애.** 3개 설정 = 1개 스킬. SDK 불필요. OS 스케줄러는 1970년대부터 안정적이다 — 커스텀 데몬 대신 `cron` + `claude --resume`을 사용한다. 작성하지 않은 코드는 깨지지 않는 코드다.

**3. 거인이 자라면, 당신도 자란다.** Anthropic이 네이티브 메모리, 24/7 에이전트, 멀티 에이전트 조율을 출시하면 — 다시 작성하지 않고 코드를 은퇴시킨다. 다른 프레임워크는 Claude Code와 경쟁한다. 우리는 보완한다. **우리의 코드베이스는 시간이 지나면 줄어든다. 그들의 것은 늘어난다.**

### 프로젝트 구조

```
clawd-lobster/
├── skills/          9개 스킬 모듈 (각 skill.json 매니페스트 포함)
├── scripts/         CLI 도구: skill-manager, heartbeat, sync, evolve-tick 등
├── templates/       설정 템플릿 (시크릿 미포함)
├── webapp/          스킬 관리 대시보드 (3탭 Web UI)
├── knowledge/       공유 지식 베이스 (git 동기화)
├── install.ps1/sh   설치 프로그램 (Windows / macOS / Linux)
└── Dockerfile       Docker 지원
```

전체 파일 트리는 [ARCHITECTURE.md](ARCHITECTURE.md)를 참조하세요.

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
| 에이전트 진화 | 없음 | 없음 | 자기 개선 스킬 | **있음 (제안 + 학습된 스킬)** |
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

### "heartbeat, 스킬, MCP — 이미 있는 거 아니에요?"

Heartbeat: OS 스케줄러 (Task Scheduler / launchd / cron) 가 30분마다 확인합니다 — 커스텀 데몬 없이. 세션이 죽으면 `claude --resume`으로 복활. Claude Code가 네이티브 24/7 (KAIROS)를 출시하면, 코드 변경 없이 무료로 받습니다.

스킬: Claude Code 내장 스킬은 Anthropic이 결정합니다. 직접 추가/수정/공유가 불가능합니다. Clawd-Lobster는 `skill.json` 매니페스트 하나로 커스텀 스킬의 전체 수명주기를 관리합니다 — 도메인 특화, 자격 증명, 헬스 체크 포함.

**MCP는 프로토콜이다. 우리는 패키지 매니저다.** Claude Code의 `.mcp.json`은 평면적인 서버 목록이고, 메타데이터/수명주기/UI가 없습니다. 우리의 스킬 레이어가 설치, 비활성화, 자격 증명, 헬스 모니터링, 멀티 머신 동기화를 추가합니다. `npm`이 Node.js를 대체하지 않는 것처럼 — 대규모로 사용 가능하게 만듭니다.

### "Anthropic이 이것을 차단하지 않을까?"

우리는 CLI 도구를 자동화합니다 — 사용자를 사칭하는 것이 아닙니다. 사용자가 `claude login`을 한 번 실행하고, OS 스케줄러가 Anthropic이 자사 CLI에 제공한 플래그 (`--resume`, `-p`)를 사용합니다. OAuth 자동화, API 키 관리, 리버스 엔지니어링은 하지 않습니다. cron으로 `git pull`을 스케줄링하는 것과 같습니다.

### "무거운 작업의 API 비용은?"

Pro 구독 ($20/월)은 토큰당 과금이 없습니다 — 한계 비용 $0. 모델 라우터, 로컬 추론 스택, 토큰 예산 관리가 불필요합니다. Rate limit에 도달하면 skill-manager가 우아하게 큐잉합니다. **예측 가능한 비용 자체가 기능입니다.**

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
