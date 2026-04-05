[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/footprint-25MB_RAM-orange)

<p align="center">
<strong>아이디어에서 작동하는 코드까지. 한 번의 대화로.</strong><br>
<em>Spec Squad가 여러분의 설명을 리뷰 완료, 테스트 완료된 코드베이스로 변환합니다 -- Claude Agent SDK 기반.</em>
</p>

<p align="center">
<sub>Web 대시보드 + CLI. 멀티 에이전트 개발. 영구 메모리. 멀티 머신 동기화.</sub>
</p>

---

## Clawd-Lobster란?

Claude Code는 두뇌입니다. Clawd-Lobster는 신경계입니다.

Claude Code는 현재 사용 가능한 가장 강력한 코딩 에이전트이지만, 세션 간에 모든 것을 잊어버리고, 한 대의 머신에서만 실행되며, 스킬 관리 기능이 없습니다. Clawd-Lobster는 바로 부족한 부분을 채웁니다: 적대적 멀티 에이전트 협업을 통해 코드를 설계, 리뷰, 구현, 테스트하는 **Spec Squad**와 함께 영구 메모리, 멀티 머신 오케스트레이션, 엄선된 스킬, 자기 진화 기능을 제공합니다.

**Clawd-Lobster는 제너레이터입니다.** 한 번 실행하면 여러분만의 **Hub**가 생성됩니다 -- Hub는 프라이빗 GitHub 저장소로, 여러분의 커맨드 센터가 됩니다. Hub가 모든 머신, 워크스페이스, 메모리, 스킬을 관리합니다.

```
  clawd-lobster (이 저장소 -- 제너레이터)
       |
       |  pip install -e . && clawd-lobster setup
       |
       v
  clawd-yourname (여러분의 프라이빗 Hub -- 자동 생성)
       |
       |  실제로 매일 사용하는 것은 이쪽
       |
       +-- Machine A -- Claude Code + skills + memory
       +-- Machine B -- Claude Code + skills + memory
       +-- Machine C -- Claude Code + skills + memory
            |
            모두 연결됨. 모든 지식을 공유.
            하트비트로 항상 활성 상태.
```

GitHub이 컨트롤 플레인입니다. Git이 프로토콜입니다. 모든 상태 -- 스킬, 지식, 워크스페이스 레지스트리, 하트비트 상태 -- 는 git에 저장되고 자동으로 동기화됩니다.

**런타임 풋프린트: 25 MB RAM, 672 KB 디스크.** Python 프로세스 1개 (MCP Memory Server)와 SQLite뿐입니다. 나머지는 OS 스케줄러를 통해 실행 후 종료되거나 브라우저에서 동작합니다. 폴링 없음, 데몬 없음, 비대화 없음.

---

## 빠른 시작

스타일에 맞게 세 가지 방법 중 선택할 수 있습니다.

### Web UI (초보자 추천)

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
# 브라우저가 http://localhost:3333 에서 열립니다
# 온보딩 마법사가 모든 것을 안내합니다
```

### Terminal (전문가용)

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# 4단계 대화형 마법사: 사전 요구사항 확인 -> 페르소나 선택 -> 워크스페이스 루트 설정 -> 첫 번째 워크스페이스 생성
```

### Classic (설치 스크립트)

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

### 설치 과정

인스톨러가 사전 요구사항을 확인하고, Claude Code + GitHub 인증을 수행하고, Hub를 생성하고, MCP Memory Server (32 도구)를 설치하고, 워크스페이스를 구성하고, 스케줄러와 하트비트를 등록합니다. 필요한 인증 정보: OAuth 클릭 2회. API 키는 필요하지 않습니다.

| 플랫폼 | 동기화 | 하트비트 |
|----------|------|-----------|
| Windows | Task Scheduler (30분) | Task Scheduler (30분) |
| macOS | launchd | launchd |
| Linux | cron | cron |
| Docker | 컨테이너 라이프사이클 | 컨테이너 라이프사이클 |

---

## Web 대시보드

`clawd-lobster serve`로 시작합니다 (기본 포트 3333). 대시보드에는 세 가지 주요 뷰가 있습니다:

### /onboarding -- 설치 마법사

처음 방문하면 자동으로 이 페이지로 이동합니다. 마법사가 사전 요구사항 (Python, Claude CLI, Git, pip)을 확인하고, 페르소나 선택 (Guided / Expert / Tech), 워크스페이스 루트 설정, 첫 번째 워크스페이스 생성까지 모든 것을 브라우저에서 완료합니다.

### /workspaces -- 워크스페이스 매니저

등록된 모든 워크스페이스를 실시간 상태와 함께 목록으로 표시합니다. 각 워크스페이스 카드에는 경로, 메모리 데이터베이스 크기, git 동기화 상태, Spec Squad 단계가 표시됩니다. 대시보드에서 직접 새 워크스페이스를 만들거나 동기화를 켜고 끌 수 있습니다.

### /squad -- Spec Squad

멀티 에이전트 개발 인터페이스입니다. 디스커버리 대화를 시작하고, Architect가 사양을 작성하고, Reviewer가 이의를 제기하고, Coder가 빌드하고, Tester가 검증하는 과정을 SSE를 통한 실시간 진행 업데이트로 추적할 수 있습니다.

---

## Spec Squad -- 멀티 에이전트 개발

Spec Squad는 v1.0의 핵심 기능입니다. 4개의 전문 에이전트가 협업하여 여러분의 아이디어를 리뷰 완료, 테스트 완료된 코드로 변환합니다 -- Claude Agent SDK 사용.

### 파이프라인

```
여러분이 프로젝트를 설명합니다
  | clawd-lobster squad start (터미널)
  | 또는 /squad 페이지 (Web)
  v
Discovery Interview
  | 시니어 컨설턴트가 3-6개의 스마트한 질문 (3W1H: Why, What, Who, How)
  | 충분한 컨텍스트가 모이면: DISCOVERY_COMPLETE
  v
Architect
  | 완전한 OpenSpec 작성: project.md -> proposal.md -> design.md
  | -> specs/ (SHALL/MUST + Gherkin) -> tasks.md (단계별, 각 5-30분)
  v
Reviewer (적대적)
  | 사양을 철저히 검토. 갭, 모호함, 약한 결정을 발견.
  | 판정: REVISE (이슈 포함) 또는 APPROVED (신뢰도 점수 포함)
  | 최대 5라운드 리뷰 -- Architect는 모든 이슈를 반드시 수정
  v
Coder
  | 승인된 사양을 태스크별, 단계별로 실행
  | 각 단계 완료 후 커밋. tasks.md에서 태스크를 완료 표시
  v
Tester
  | 모든 SHALL/MUST 요구사항을 코드와 대조 검증
  | Gherkin 시나리오 실행. 판정: PASSED 또는 ISSUES (패스율 포함)
  v
완료 -- 리뷰 완료, 테스트 완료된 코드베이스 준비 완료
```

### 적대적 리뷰의 작동 방식

Reviewer는 "무자비하지만 공정하게"라는 지시를 받습니다. `openspec/` 내의 모든 파일을 읽고 아키텍처, 요구사항, 태스크 분할에 이의를 제기합니다. 문제가 발견되면 Architect가 수정해야 합니다. 이 루프는 Reviewer가 신뢰도 점수와 함께 APPROVED 판정을 내릴 때까지 최대 5라운드 실행됩니다. 그 결과, 코드 한 줄을 작성하기 전에 스트레스 테스트를 거친 사양을 얻게 됩니다.

### Web 모드 vs 터미널 모드

| | Web (`/squad`) | Terminal (`clawd-lobster squad start`) |
|---|---|---|
| Discovery | 브라우저 내 채팅 인터페이스 | stdin/stdout |
| 진행 상황 | 실시간 SSE 이벤트, 시각적 단계 표시 | 단계 라벨을 터미널에 출력 |
| 빌드 승인 | 브라우저에서 프롬프트 | `Build now? (y/n)` |
| 상태 관리 | `.spec-squad.json`에 영구 저장 | 동일 파일 |
| 기반 엔진 | 동일한 `squad.py` 비동기 코어 | 동일한 `squad.py` 비동기 코어 |

두 모드 모두 동일한 파이프라인, 동일한 Agent SDK 호출, 동일한 상태 파일을 사용합니다. 워크플로에 맞는 쪽을 선택하시면 됩니다.

---

## 스킬

9개의 스킬 모듈. 각각 `skill.json` 매니페스트 포함. 총 32개 MCP 도구.

### Core Skills (고정)

| 스킬 | 타입 | 기능 |
|---|---|---|
| **Memory Server** | mcp-server | 26개 도구의 MCP 메모리. SQLite, 중요도 엔진, CJK 대응 압축 |
| **Heartbeat** | cron | OS 스케줄러를 통한 세션 유지 -- 중단된 세션 자동 복구 |
| **Evolve** | prompt-pattern | 패턴 추출, 개선 제안, 중요도 감쇠 |
| **Absorb** | prompt-pattern | 폴더, GitHub 저장소, URL에서 지식 수집 |
| **Spec** | prompt-pattern | OpenSpec 방법론을 통한 가이드 설계 + blitz 실행 |

### Optional Skills

| 스킬 | 타입 | 기능 | 기본값 |
|---|---|---|---|
| **Migrate** | prompt-pattern | 기존 AI 설정에서 가져오기 (포맷 자동 감지) | 활성화 |
| **Connect-Odoo** | mcp-server | Odoo ERP 연동 -- XML-RPC + 폴러를 통한 6개 MCP 도구 | 비활성화 |
| **Codex Bridge** | prompt-pattern | OpenAI Codex에 worker + critic 역할로 작업 위임 | 비활성화 |
| **NotebookLM Bridge** | prompt-pattern | Google NotebookLM을 통한 무료 RAG + 콘텐츠 엔진 | 비활성화 |

### 스킬 관리

각 스킬은 `skill.json` 매니페스트를 가진 독립 모듈입니다. **Web UI** 또는 **CLI**로 관리할 수 있습니다:

```bash
clawd-lobster serve                                      # 토글이 있는 Web 대시보드
python scripts/skill-manager.py list                     # 모든 스킬 목록 표시
python scripts/skill-manager.py enable connect-odoo      # 스킬 활성화
python scripts/skill-manager.py disable connect-odoo     # 스킬 비활성화
python scripts/skill-manager.py health                   # 모든 헬스 체크 실행
python scripts/skill-manager.py reconcile                # .mcp.json + settings.json 재생성
```

### 나만의 스킬 추가하기

`skills/my-skill/skill.json`에 매니페스트를 만들고, 스킬을 구현하고 (MCP server, 스크립트, 또는 SKILL.md), `skill-manager.py reconcile`을 실행하면 됩니다. 스킬은 설정 항목 3개로 완성 -- SDK 불필요, 플러그인 API 불필요, 프레임워크 종속 없음.

---

## 아키텍처

### 3계층 설계

```
+----------------------------------------------+
|        Skills Layer (Clawd-Lobster)           |
|                                               |
|  Memory System    Workspace Manager           |
|  Spec Squad       Scheduler                   |
|  Self-Evolution   (커스텀 스킬)               |
|                                               |
|  설치 방법: .mcp.json + settings.json         |
|             + CLAUDE.md                        |
+----------------------+------------------------+
                       |
+----------------------v------------------------+
|            Claude Code (브레인)                |
|                                                |
|  Agent Loop - Streaming - Tools - Permissions  |
|  Anthropic이 유지보수. 자동 업그레이드.        |
+------------------------------------------------+
```

### 4계층 메모리

| 계층 | 내용 | 속도 | 범위 |
|-------|------|-------|-------|
| **L1.5** | Claude Code auto-memory (네이티브) | 즉시 | 현재 프로젝트 |
| **L2** | SQLite + 26개 MCP 도구 | ~1ms | 워크스페이스별 |
| **L3** | Markdown 지식 베이스 | ~10ms | git을 통해 공유 |
| **L4** | Cloud DB (선택사항) | ~100ms | 워크스페이스 간 |

중요도 엔진이 중요한 메모리에 대한 접근을 유지합니다: 접근할 때마다 중요도가 5% 증가, 수동 강화로 20% 증가 (상한 2.0x), 30일 이상 접근하지 않은 항목은 하루 5% 감쇠 (하한 0.01 -- 삭제되지 않음).

### 실제로 실행되는 것

| 계층 | 내용 | 라인 수 | RAM | 타이밍 |
|-------|------|-------|-----|------|
| **Runtime** | MCP Memory Server (26개 도구 + SQLite) | ~1,400 | ~25 MB | 상시 실행 |
| **Runtime** | Odoo Connector (활성화 시) | ~280 | ~22 MB | 활성화 시에만 |
| **Runtime** | Web Dashboard (stdlib HTTP) | ~800 | ~15 MB | 서빙 시 |
| **Cron** | evolve-tick (제안 생성) | ~465 | ~20 MB 피크 | 2시간마다, 실행 후 종료 |
| **Cron** | heartbeat + sync | ~300 | ~5 MB 피크 | 30분마다, 실행 후 종료 |
| **Setup** | CLI + 온보딩 + squad 오케스트레이터 | ~1,200 | 0 | 요청 시 |
| **Config** | skill.json 매니페스트, 템플릿 | ~900 | 0 | 시작 시 로드 |

**상주 풋프린트: Python 프로세스 1개 (~25 MB) + SQLite.** Web 대시보드는 stdlib `http.server`를 사용합니다 -- Flask 없음, FastAPI 없음, 외부 의존성 없음.

### 설계 철학

1. **거인의 어깨 위에 서다.** Claude Code 뒤에는 수백만 시간의 엔지니어링이 있습니다. 우리는 부족한 부분을 추가하고 (~3K 라인) 최고의 엔진을 살립니다.

2. **코드가 적으면 고장도 적다.** 설정 항목 3개 = 스킬 1개. SDK 제로. OS 스케줄러는 1970년대부터 신뢰받아 왔습니다 -- 커스텀 데몬 대신 `cron` + `claude --resume`을 사용합니다.

3. **거인이 성장하면 여러분도 성장한다.** Anthropic이 네이티브 메모리, 24/7 에이전트, 멀티 에이전트 조정을 제공할 때 -- 우리는 다시 작성하는 것이 아니라 코드를 은퇴시킵니다. **우리의 코드베이스는 시간이 지나면 줄어듭니다. 그들의 것은 늘어납니다.**

자세한 내용은 [ARCHITECTURE.md](ARCHITECTURE.md)를 참조하세요.

---

## CLI 레퍼런스

| 명령어 | 기능 |
|---|---|
| `clawd-lobster serve` | Web 대시보드를 localhost:3333에서 시작 |
| `clawd-lobster serve --port 8080` | 커스텀 포트 사용 |
| `clawd-lobster serve --daemon` | 서버를 백그라운드에서 실행 |
| `clawd-lobster setup` | 터미널 온보딩 마법사 실행 |
| `clawd-lobster workspace create <name>` | 새 워크스페이스 생성 |
| `clawd-lobster workspace create <name> --repo` | 워크스페이스 + 프라이빗 GitHub 저장소 생성 |
| `clawd-lobster workspace create <name> --dry-run` | 변경 없이 미리보기 |
| `clawd-lobster squad start` | Spec Squad를 터미널 모드로 시작 |
| `clawd-lobster squad start --workspace <path>` | 대상 워크스페이스 지정 |
| `clawd-lobster status` | 시스템 상태, 워크스페이스, 버전 표시 |
| `clawd-lobster --version` | 버전 출력 |

---

## 멀티 머신 설정

### Hub 패턴

Hub는 프라이빗 GitHub 저장소로, 커맨드 센터 역할을 합니다. 모든 머신이 Hub를 클론하고 자동으로 동기화합니다.

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
              |  2분이면 참여 가능   |
              +---------------------+
```

### 다른 머신 추가하기

```bash
git clone https://github.com/you/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster setup
# "Join existing Hub" 선택 -> Hub URL 붙여넣기 -> 이 머신 이름 지정 -> 완료
```

새 머신은 축적된 모든 지식을 즉시 물려받습니다. L2 (SQLite)는 워크스페이스별로 로컬, L3 (markdown)는 git을 통해 동기화, L4 (선택적 Cloud DB)는 모든 것을 통합합니다.

### Always Alive -- 하트비트

에이전트는 절대 멈추지 않습니다. OS 스케줄러가 30분마다 확인합니다: 각 워크스페이스의 세션이 살아 있는가? 아니라면 `claude --resume`으로 복구합니다 -- 컨텍스트 완전 복원. 커스텀 데몬 불필요. Claude Code가 항상 실행 상태를 유지합니다.

---

## 워크스페이스

워크스페이스는 메모리, 스킬, 사양 지원을 갖춘 프로젝트 디렉토리입니다.

### 워크스페이스 구조

```
my-project/
+-- CLAUDE.md              <- 프로젝트별 지시사항
+-- .claude-memory/
|   +-- memory.db          <- L2 메모리 (SQLite)
+-- knowledge/             <- L3 지식 (git 동기화)
+-- skills/learned/        <- 자동 생성된 스킬
+-- openspec/              <- 사양 아티팩트 (/spec 또는 squad 사용 시)
|   +-- project.md
|   +-- changes/
|   +-- specs/
+-- .spec-squad.json       <- squad 상태 (squad 사용 시)
+-- .blitz-active          <- blitz 실행 중 존재
```

### 스케줄링 자동화

OS 수준 스케줄러 (Windows Task Scheduler / cron / launchd)는 Claude Code가 활성화되어 있지 않을 때도 동작합니다:

- **Heartbeat** -- 모든 워크스페이스 세션이 활성 상태인지 확인 (중단 시 복구)
- **Git sync** -- 30분마다 모든 저장소를 pull 및 push
- **Salience decay** -- 매일 메모리 중요도 조정
- **evolve-tick** -- 2시간마다 패턴 추출 + 개선 제안

---

## 메모리 시스템

### 26개 MCP 도구

| 카테고리 | 도구 |
|---|---|
| **Write** | `memory_store`, `memory_record_decision`, `memory_record_resolved`, `memory_record_question`, `memory_record_knowledge` |
| **Read** | `memory_list`, `memory_get`, `memory_get_summary` |
| **Delete** | `memory_delete` |
| **Search** | `memory_search` (벡터 + 텍스트, 중요도 가중, 전체 테이블) |
| **Salience** | `memory_reinforce` |
| **Evolve** | `memory_learn_skill`, `memory_list_skills`, `memory_improve_skill` |
| **TODO** | `memory_todo_add`, `memory_todo_list`, `memory_todo_update`, `memory_todo_search` |
| **Audit Trail** | `memory_log_action`, `memory_audit_search`, `memory_audit_stats`, `memory_daily_report`, `memory_activity_log` |
| **Admin** | `memory_compact`, `memory_status`, `memory_oracle_summary` |

메모리는 수동적인 저장소가 아닙니다 -- 에이전트의 동작을 능동적으로 형성합니다. 모든 궤적이 기록됩니다. 모든 워크스페이스가 git을 통해 지식을 공유합니다. 에이전트들은 함께 성장합니다.

---

## 진화 시스템

v1이 구축된 후에도 에이전트는 자동으로 계속 개선됩니다.

### 루프

```
/absorb (입력)
  +-- 폴더 스캔 -> 지식, 결정사항, TODO 추출
  +-- GitHub 저장소 읽기 -> 패턴 + 스킬 학습
  +-- URL 가져오기 -> 인사이트 저장
       |
evolve-tick (2시간마다)
  +-- 완료된 작업에서 패턴 추출
  +-- 개선 제안 생성 (git 동기화되는 markdown 파일)
  +-- 오래된 지식에 중요도 감쇠 적용
  +-- 머신 간 지식 동기화
       |
Review (여러분이 판단)
  +-- openspec/proposals/ 내 제안 검토
  +-- 승인 -> 다음 blitz의 TODO가 됨
  +-- 거부 -> 교훈을 기록하고 아카이브
```

Evolve는 직접 변경이 아닌 **제안**을 생성합니다. 모든 제안은 `openspec/proposals/`에 저장되어 사람의 검토를 기다립니다. 학습된 스킬은 git sync를 통해 세션 간, 머신 간에 영구적으로 유지됩니다.

---

## 요구사항

- **Python** 3.10+ 및 **Git** 2.x+
- **Claude Code** CLI ([설치 가이드](https://docs.anthropic.com/en/docs/claude-code/getting-started))
- **GitHub** 계정 (프라이빗 Hub 저장소용)
- **Node.js** 18+ (선택사항 -- MCP server가 필요로 하는 경우에만)

---

## 설치 (상세)

### 1. 클론 및 설치

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
```

이것으로 `clawd-lobster` CLI 명령이 전역적으로 등록됩니다.

### 2. 설치 실행

하나를 선택하세요:

```bash
clawd-lobster serve    # Web 마법사 (http://localhost:3333)
clawd-lobster setup    # 터미널 마법사
./install.ps1          # Windows 클래식 인스톨러
./install.sh           # macOS/Linux 클래식 인스톨러
```

### 3. 확인

```bash
clawd-lobster status
# 표시 내용: Python 버전, Claude CLI, Git, 워크스페이스, 서버 상태
```

### 4. 빌드 시작

```bash
clawd-lobster squad start                    # 프로젝트 설명 -> 사양 작성 -> 빌드
clawd-lobster workspace create my-app --repo # 또는 워크스페이스를 수동으로 생성
```

---

## FAQ

### "이건 그냥 Claude Code 래퍼 아닌가요?"

네, 그게 핵심입니다.

Claude Code는 현재 사용 가능한 가장 강력한 코딩 에이전트이며, Anthropic의 수백만 시간의 엔지니어링이 뒷받침하고 있습니다. 다른 프레임워크는 엔진을 처음부터 다시 만듭니다 (5만-30만 라인). 우리는 부족한 부분을 추가하고 (~3K 라인) 최고의 엔진을 살립니다.

Anthropic이 다음 획기적 기능을 출시하면, 우리는 즉시 그 혜택을 누립니다. 다른 프레임워크는 어댑터를 다시 작성해야 합니다.

### "Spec Squad는 Claude에게 코딩을 부탁하는 것과 뭐가 다른가요?"

Spec Squad는 코딩 시작 전에 **적대적 리뷰**를 추가합니다. Architect가 완전한 사양을 작성하면 Reviewer가 이를 철저히 검토합니다 -- 갭, 모호함, 약한 결정을 찾아냅니다. Coder가 무엇이든 건드리기 전에 최대 5라운드의 수정이 이루어집니다. 즉, 캐주얼한 프롬프트가 아니라 스트레스 테스트를 거친 설계도를 바탕으로 코드가 만들어집니다.

### "하지만 다른 에이전트는 24/7 돌아가면서 계속 학습하잖아요"

우리도 마찬가지입니다. 스케줄러가 30분마다 지식을 동기화합니다. 메모리는 중요도 감쇠를 통해 매일 진화합니다. 학습된 스킬은 git을 통해 모든 머신으로 전파됩니다. 하트비트가 세션 활성 상태를 보장합니다: 터미널이 닫히면 OS 스케줄러가 `claude --resume`으로 복구합니다 -- 컨텍스트 완전 복원.

### "Claude Code에는 이미 내장 스킬과 MCP가 있는데, 왜 더 필요한가요?"

Claude Code의 내장 스킬은 폐쇄적입니다 -- 추가, 수정, 공유가 불가능합니다. MCP는 프로토콜을 제공하지만 라이프사이클 관리는 없습니다. 스킬을 설치하려면 3개의 JSON 파일을 수동으로 편집해야 합니다. 두 번째 머신? 전부 다시 해야 합니다.

**MCP는 프로토콜입니다. 우리는 패키지 매니저입니다.** 우리가 추가하는 것: `skill.json` 매니페스트, 원 커맨드 활성화/비활성화, 인증 정보 중앙 관리, 헬스 체크, Web 대시보드, git을 통한 크로스 머신 레지스트리 동기화.

### "Anthropic이 이걸 차단하지 않나요?"

우리는 OS cron을 통해 `claude` CLI 명령을 스케줄링합니다 -- `git pull`을 스케줄링하는 것과 같은 방식입니다. `claude --resume`, `--allowedTools`, MCP server를 사용합니다 -- 모두 Anthropic이 자체 CLI에서 제공하는 플래그입니다. API 키 자동화 없음. OAuth 토큰 스크래핑 없음. 리버스 엔지니어링 없음.

### "비용은 어떻게 되나요?"

Pro 구독 ($20/월)에서는 토큰당 과금이 없습니다. 구독 하나. 엔진 하나. 예측 가능한 비용이 곧 기능입니다.

---

## 비교

| | Claude Code (기본) | 대형 프레임워크 | **Clawd-Lobster** |
|---|---|---|---|
| 에이전트 엔진 | Anthropic | 커스텀 (5만-30만 LOC) | **Anthropic (네이티브)** |
| 멀티 에이전트 개발 | 없음 | 일부 있음 | **있음 (Spec Squad: 4 에이전트)** |
| 적대적 리뷰 | 없음 | 없음 | **있음 (최대 5라운드)** |
| 영구 메모리 | 없음 | 다양 | **4계층 + 중요도 엔진** |
| 멀티 머신 | 없음 | 없음 | **있음 (Hub + git sync)** |
| 상시 가동 | 없음 | 커스텀 데몬 | **OS 하트비트 + 자동 복구** |
| 스킬 관리 | N/A | CLI/SDK | **Web UI + CLI + 매니페스트** |
| 자기 진화 | 없음 | 다양 | **있음 (제안 + 학습된 스킬)** |
| 온보딩 | 수동 | 복잡 | **Web 마법사 또는 터미널, 5개 언어 지원** |
| Web 대시보드 | 없음 | 다양 | **있음 (localhost:3333)** |
| 코드베이스 | 0 | 5만-30만 LOC | **~3K LOC** |
| 비용 모델 | 구독 | 토큰 과금 API | **구독 (정액)** |
| Anthropic 업그레이드 | 투명 | 파괴적 | **투명** |

---

## 로드맵

**v1.0에서 완료**
- [x] 통합 CLI 진입점 (`clawd-lobster serve/setup/squad/workspace/status`)
- [x] Web Dashboard -- 온보딩 마법사, 워크스페이스 매니저, Spec Squad UI
- [x] Spec Squad -- Claude Agent SDK를 통한 멀티 에이전트 개발
- [x] 3가지 사용자 페르소나 (Guided / Expert / Tech)
- [x] 9개 스킬, 32개 MCP 도구, `skill.json` 매니페스트 시스템
- [x] 중요도 엔진이 포함된 4계층 메모리
- [x] git sync를 통한 멀티 머신 Hub 패턴
- [x] OS 스케줄러를 통한 하트비트 자동 복구
- [x] git 동기화 제안을 통한 진화 루프
- [x] Docker 지원

**다음 단계**
- [ ] Supabase L4 -- 원클릭 Cloud Database (Oracle wallet 불필요)
- [ ] SearXNG -- 프라이빗 셀프 호스팅 웹 검색
- [ ] Docker Sandbox -- 신뢰할 수 없는 작업을 위한 격리된 코드 실행
- [ ] Skill marketplace -- 커뮤니티 기여 스킬, 원클릭 설치
- [ ] Team mode -- 역할 기반 접근 제어가 있는 다중 사용자 공유 워크스페이스
- [ ] Agent-to-agent delegation -- 에이전트 간 태스크 할당

---

## 프로젝트 구조

```
clawd-lobster/
+-- clawd_lobster/       CLI + Web 서버 + squad 오케스트레이터 + 온보딩
+-- skills/              9개 스킬 모듈 (각각 skill.json 매니페스트 포함)
+-- scripts/             Heartbeat, sync, evolve-tick, skill-manager 등
+-- templates/           설정 템플릿 (시크릿 없음)
+-- knowledge/           공유 지식 베이스 (git 동기화)
+-- install.ps1/sh       클래식 인스톨러 (Windows / macOS / Linux)
+-- pyproject.toml       패키지 정의 (pip install -e .)
+-- Dockerfile           Docker 지원
+-- docker-compose.yml   Docker Compose 설정
```

---

## 기여하기

기여를 환영합니다! 가장 쉬운 기여 방법:

1. **스킬 추가** -- `skills/`에 폴더를 만들고 `skill.json` 매니페스트 배치
2. **템플릿 개선** -- `templates/`의 기본값 개선
3. **플랫폼 지원** -- Linux/macOS 테스트 도움
4. **버그 보고** -- Issue 열기

---

## 라이선스

MIT -- 원하는 대로 사용하세요.

---

<p align="center">
<sub>Anthropic과 무관합니다. <a href="https://claude.ai/code">Claude Code</a> 위에 구축되었습니다.</sub>
</p>
