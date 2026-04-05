[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

# Clawd-Lobster

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/github/license/teddashh/clawd-lobster)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Runtime](https://img.shields.io/badge/RAM-25MB-orange)

<p align="center">
<strong>你終究要用 Claude Code 的 — 為什麼不一開始就選最好的體驗？</strong><br>
<strong>You'll end up using Claude Code anyway — why not start with the best experience?</strong><br>
<strong>어차피 결국 Claude Code를 쓰게 됩니다 — 처음부터 최고의 경험을 선택하지 않을 이유가 있나요?</strong>
</p>

---

## 문제

AI 에이전트 프레임워크, 본 적 있으시죠. 몇 개 써봤을 수도 있습니다. 실제로 무슨 일이 벌어지는지:

**문제 1: Claude Code는 강력합니다. 하지만 당신이 보모 노릇을 하고 있습니다.**
매 세션이 제로에서 시작합니다. 어제 배운 걸 잊어버립니다. 컨텍스트를 복붙하고, 아키텍처를 다시 설명하고, 규칙을 또 알려줍니다. 당신이 메모리입니다. 당신이 매니저입니다. 당신이 병목입니다.

**문제 2: AI 에이전트 프레임워크 — 데모는 화려하고, 경험은 최악입니다.**
30만 줄의 코드. 커스텀 어댑터. 실제 프로젝트보다 긴 설정 파일. 모델이 업데이트될 때마다 깨집니다. 프레임워크 유지보수에 쓰는 시간이 제품 개발보다 깁니다.

**문제 3: 그레이 존.**
안전 장치를 우회하는 셀프 호스팅 에이전트 루프. 상한선 없는 토큰 종량제 API. 도구를 쓰고 있는 건지, 도구에 쓰이고 있는 건지 구분 안 되는 프랑켄슈타인 스택.

## 답

Clawd-Lobster는 Claude Code를 대체하지 않습니다. Claude Code가 **기억하고, 계획하고, 리뷰하고, 구축하고, 진화하게** 만듭니다 — 공식 Anthropic 도구만으로.

- **100% Claude Code CLI + Agent SDK.** 래퍼 없음, 커스텀 에이전트 루프 없음, 그레이 존 없음. 기존 Claude 구독으로 동작합니다. 추가 API 비용 없음.
- **약 9,000줄.** 30만 줄이 아닙니다. Claude Code가 업데이트되면 새 기능을 그대로 사용할 수 있습니다. 다시 작성할 필요 없음, 깨지지 않음.
- **5분이면 시작.** 브라우저를 열고, 두 번 클릭하면, 끝. API 키 불필요, Docker 불필요, YAML 박사학위 불필요.

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

## 빠른 시작

### 모든 사용자 (Web UI)

```bash
git clone https://github.com/teddashh/clawd-lobster
cd clawd-lobster
pip install -e .
clawd-lobster serve
```

브라우저가 열립니다. 설정 마법사가 모든 것을 안내합니다.

### 터미널을 좋아하는 분들

```bash
clawd-lobster setup        # terminal onboarding
clawd-lobster squad start  # run Spec Squad in terminal
```

### 클래식 설치 (파워 유저용)

```powershell
# Windows
.\install.ps1

# macOS / Linux
chmod +x install.sh && ./install.sh
```

---

## 무엇을 얻는가

### 1. Spec Squad — 당신의 AI 개발 팀

원하는 것을 설명하세요. 4개의 Claude 세션이 나머지를 합니다.

**Architect**가 테스트 가능한 요구사항이 포함된 완전한 사양을 작성합니다. **Reviewer** — Architect의 지시를 한 번도 본 적 없는 완전히 독립된 Claude 세션 — 가 그것을 철저히 뜯어봅니다. Reviewer가 승인할 때까지 반복합니다. 그 후 **Coder**가 사양대로 구축하고, **Tester**가 모든 요구사항을 검증합니다.

기믹이 아닙니다. 테스트에서 Reviewer는 첫 사양에서 실제 버그 11개를 잡아냈습니다 — 셀프 밸리데이션 체크리스트로는 절대 찾을 수 없는 문제들입니다. 반환 타입 충돌, API 불일치, 불가능한 Gherkin 시나리오, 라이브러리 호환성 문제.

**왜 효과가 있는가:** 각 에이전트가 격리된 컨텍스트에서 실행됩니다. Reviewer는 Architect의 추론에 영향받지 않습니다. Tester는 Coder가 어떤 지름길을 썼는지 모릅니다. 독립적인 두뇌가 독립적인 문제를 찾습니다.

두 가지 인터페이스, 같은 엔진:
- **Web:** 브라우저에서 Claude와 채팅하고, 라이브 대시보드에서 에이전트 작업을 감시
- **Terminal:** 터미널에서 Claude가 질문하고, 에이전트 실행 중 진행 상황 출력

### 2. 잊지 않는 두뇌

즉시부터 글로벌까지, 4계층 메모리:

| Layer | Speed | What |
|-------|-------|------|
| L1.5 | Instant | Claude Code's native auto-memory |
| L2 | ~1ms | SQLite + MCP — per-workspace, salience-weighted |
| L3 | ~10ms | Markdown + Git — synced across machines |
| L4 | ~100ms | Cloud DB (optional) — cross-workspace search |

중요한 아이디어는 떠오르고, 노이즈는 가라앉습니다. 효과 있는 스킬은 강화되고, 오래된 지식은 감쇠됩니다. 관리할 필요 없습니다 — 전부 자동입니다.

### 3. 항상 살아 있음

노트북을 닫아도 Clawd-Lobster는 계속 작동합니다.

heartbeat는 OS 스케줄러(Task Scheduler / cron / launchd)를 사용합니다 — 커스텀 데몬도, 폴링 루프도, 토큰을 태우는 프로세스도 아닙니다. 세션이 죽으면 풀 컨텍스트로 부활합니다. 보모 노릇 불필요.

### 4. 모든 머신, 하나의 두뇌

GitHub이 컨트롤 플레인. Git이 프로토콜.

머신 A가 패턴을 학습합니다. 프라이빗 Hub에 동기화됩니다. 머신 B가 즉시 계승합니다. 새 머신? `install.ps1`, "Join Hub", URL 붙여넣기, 2분이면 완전 가동.

### 5. 자기 진화

복잡한 작업 완료 후, 시스템이 재사용 가능한 패턴을 추출하고 학습된 스킬로 저장합니다. 다음에 비슷한 태스크가 오면, 지난번에 어떻게 해결했는지 기억합니다.

스킬에는 유효성 점수가 있습니다. 입증된 패턴은 강화되고, 오래된 스킬은 감쇠됩니다. 쓸수록 시스템이 똑똑해집니다 — 마법이 아니라, 잘된 것을 기록해두기 때문입니다.

---

## 대시보드

`clawd-lobster serve`가 `localhost:3333`에서 상주 Web 대시보드를 엽니다.

**온보딩** — 첫 실행 마법사가 사전 요구사항을 체크하고, 설정을 안내하고, 첫 워크스페이스를 생성합니다.

**워크스페이스** — 모든 프로젝트를 한 화면에. 상태, 사양 진행률, 메모리 크기, 마지막 활동.

**Spec Squad** — 브라우저에서 Claude와 대화하며 요구사항을 발견. 페이즈 타임라인과 턴 히스토리가 있는 라이브 대시보드에서 4개 에이전트의 작업을 실시간 감시.

---

## Skills

엄선된 9개 Skills. 각각 하나를 확실하게 합니다.

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

모든 Skill에는 트리거 설명(Claude가 활성화 시점을 판단), Gotchas 섹션(흔한 실수 방지책), 동적 `!command` 인젝션(로드 시 런타임 컨텍스트)이 있습니다.

---

## 아키텍처

```
Skills (the what)     ->  9 skills with manifests, instructions, gotchas
Tools (the how)       ->  32 MCP tools + Claude Code native tools
Hooks (the when)      ->  OS scheduler, git hooks, PostToolUse, Stop hooks
```

**거인의 어깨 위에 서다.** Clawd-Lobster는 Claude Code를 재구축하지 않습니다. Claude Code의 네이티브 확장 포인트(MCP 서버, CLAUDE.md, hooks, settings.json)를 Anthropic이 설계한 그대로 사용합니다. Claude Code가 새 기능을 출시하면 그대로 사용 가능. 모델이 개선되면 에이전트도 개선됩니다. 어댑터 코드 제로.

```
Disk: ~830 KB    (code + configs)
RAM:  ~25 MB    (MCP server only)
CPU:  0% idle   (OS scheduler, not polling)
LOC:  ~9,000    (not 300,000)
```

파일 트리와 런타임 상세 정보는 [ARCHITECTURE.md](ARCHITECTURE.md)를 참조하세요.

---

## CLI 레퍼런스

| Command | What It Does |
|---------|-------------|
| `clawd-lobster serve` | Start web dashboard (localhost:3333) |
| `clawd-lobster setup` | Terminal onboarding wizard |
| `clawd-lobster workspace create <name>` | Create a new workspace |
| `clawd-lobster squad start` | Run Spec Squad in terminal |
| `clawd-lobster status` | Show system health |

---

## 멀티 머신 설정

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

첫 번째 머신이 Hub를 생성합니다. 이후 머신은 2분이면 합류 가능합니다.

---

## 요구사항

- Python 3.10+
- Claude Code CLI ([install](https://claude.ai/code))
- Git 2.x+
- Node.js 18+ (선택사항, Codex Bridge용)
- GitHub 계정 (Hub sync용)

---

## 비교

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

## 철학

**1. 증폭한다. 재구축하지 않는다.**
Claude Code는 세계에서 가장 유능한 코딩 에이전트입니다. 우리는 거기에 신경계를 추가합니다. 뇌를 다시 만들지 않습니다.

**2. 거인이 높아지면, 당신도 높아진다.**
Claude Code가 업데이트될 때마다 Clawd-Lobster도 좋아집니다. 마이그레이션 제로, 재작성 제로.

**3. 계획이 곧 제품이다.**
Spec Squad는 코드부터 쓰지 않습니다. 사양을 쓰고, 적대적으로 리뷰하고, 사양대로 구축합니다. 계획이 계약입니다.

---

## 기여

PR 환영합니다. 기여하기 전에 [ARCHITECTURE.md](ARCHITECTURE.md)를 읽어주세요.

## 라이선스

MIT — [LICENSE](LICENSE) 참조.
