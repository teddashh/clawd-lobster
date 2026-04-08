# Onboarding Redesign Spec — Clawd-Lobster v2.0

## Vision

Transform the onboarding from a developer-focused 5-step wizard into a product-grade,
baby-sit experience that guides completely new users from zero to working Claude Code setup.
The key innovation: after prerequisites are verified, the web UI hands off control to
Claude Code CLI, which drives the remaining setup interactively in the terminal while
the web page shows live progress.

## Review History

- v1: Initial spec (蕾姐)
- v2: Codex adversarial review (2 HIGH, 3 MED) + 蕾姐 CIO synthesis
- Pending: QWEN/Gemini independent review

## Resolved Decisions (from Codex Adversarial Review)

### D1: Bootstrap Paradox → Dual-Track Entry
**Problem:** Web server needs Python, but target user may have nothing installed.
**Resolution:** Two entry paths:
- **Path A (has Python):** `pip install -e . && clawd-lobster serve` → Web onboarding
- **Path B (has nothing):** One-liner bootstrap script in README:
  - Windows: `irm https://raw.githubusercontent.com/teddashh/clawd-lobster/master/bootstrap.ps1 | iex`
  - macOS/Linux: `curl -fsSL https://raw.githubusercontent.com/teddashh/clawd-lobster/master/bootstrap.sh | bash`
  - Script installs Python + Node + Git → pip install → launches `clawd-lobster serve`
- **Node.js is REQUIRED** (not optional) — Claude Code installs via `npm install -g @anthropic-ai/claude-code`
- Page 1 Welcome page includes pre-requisite notice for Path B users

### D2: Handoff Session Token → Nonce-Based Trust
**Problem:** Any local process can POST fake progress to the handoff API.
**Resolution:**
- Server generates a random `session_id` (UUID4) when entering handoff phase
- `CLAUDE.md` includes `session_id` in the instructions
- `POST /api/onboarding/update` requires `session_id` header/field, rejects mismatches
- State stored under `~/.clawd-lobster/onboarding/{session_id}/state.json`

### D3: Auth Check → Active Verification
**Problem:** Checking `~/.claude/.credentials.json` exists ≠ working auth.
**Resolution:**
- Run `claude --version` (CLI exists) + check credentials file (auth attempted)
- If possible, run `claude doctor` or a lightweight auth probe
- On failure: show specific remediation steps, block Page 3
- Auth failure AFTER handoff: CLAUDE.md includes "if auth fails, tell user to re-auth and POST error to /api/onboarding/update"

### D4: State Management → Session-Scoped + Atomic
**Problem:** Multiple tabs/reruns/stale terminals can corrupt state.
**Resolution:**
- Each onboarding run gets a UUID `run_id`
- State file: `~/.clawd-lobster/onboarding/{run_id}/state.json`
- Atomic writes (tmp + rename)
- Sessions older than 24h marked stale
- `/api/onboarding/state` returns `run_id` for cross-referencing
- Re-run: `clawd-lobster setup --force` creates new run_id

### D5: i18n → Key Inventory First, Then Implementation
**Problem:** Estimated ~60 keys, actual surface area much larger.
**Resolution:**
- Create full key manifest BEFORE implementation
- Shell commands stay in English (not translated)
- Only translate: titles, descriptions, button labels, error messages, purpose explanations
- Add missing-key fallback: if key not found, show English + log warning
- Key naming convention: `{page}_{section}_{item}` (e.g. `prereq_python_purpose`)

---

## New Flow: 3 Pages

### Page 1: Welcome + Language

**What the user sees:**
- Beautiful welcome hero with "Welcome to Clawd-Lobster" title
- Product tagline in ALL 5 languages simultaneously (stacked, each dimmed):
  - EN: "You'll end up using Claude Code anyway — why not start with the best experience?"
  - 繁中: "你終究要用 Claude Code 的 — 為什麼不一開始就選最好的體驗？"
  - 簡中: "你终究要用 Claude Code 的 — 为什么不一开始就选最好的体验？"
  - 日: "どうせ Claude Code を使うことになる — 最初から最高の体験を選びませんか？"
  - 韓: "결국 Claude Code를 쓰게 될 텐데 — 처음부터 최고의 경험을 선택하지 않겠습니까？"
- Instruction (all 5 langs): "Let's get started. Please select your language."
- 5 language cards (2-column grid)
- No API calls (pure static page)
- Progress bar: 3 dots

**CSS:** `.welcome-hero` centered, h1 32-36px. Taglines `opacity:0.6`, selected language `opacity:1`.

**JS:** `pickLang()` → `applyI18n()` → enables Next.

### Page 2: Prerequisites + Claude Code Setup (Babysit Mode)

**Title:** "Let's check your system" (localized)

**Prerequisites (in order, all REQUIRED except noted):**

| # | Name | Purpose Key | Install Guide |
|---|------|-------------|---------------|
| 1 | Python 3.10+ | Runs memory server and skills | python.org (Win), brew (Mac), apt (Linux) |
| 2 | Node.js 18+ | **REQUIRED** for Claude Code | nodejs.org (Win), brew (Mac), apt (Linux) |
| 3 | Git 2.x+ | Syncs knowledge across machines | git-scm.com (Win), brew (Mac), apt (Linux) |
| 4 | pip | Python package manager | Usually included with Python |
| 5 | Claude Code CLI | The AI coding assistant | `npm install -g @anthropic-ai/claude-code` |
| 6 | Claude Code Auth | Authentication | `claude login` walkthrough |

**Each prerequisite card shows:**
- Icon: spinner → checkmark (green) / X (red)
- Name + detected version
- Purpose (localized)
- Status: Checking... → OK / MISSING
- If MISSING: expandable inline guide with platform tabs (Win/Mac/Linux)
- Platform detection: server returns `platform` field, JS uses as authoritative

**Enhanced API: `POST /api/onboarding/check`**
```json
{
  "checks": [
    {"name": "python", "ok": true, "version": "3.14.3", "optional": false, "purpose_key": "prereq_python_purpose"},
    {"name": "node", "ok": true, "version": "24.14.0", "optional": false, "purpose_key": "prereq_node_purpose"},
    {"name": "git", "ok": true, "version": "2.53.0", "optional": false, "purpose_key": "prereq_git_purpose"},
    {"name": "pip", "ok": true, "version": "25.3", "optional": false, "purpose_key": "prereq_pip_purpose"},
    {"name": "claude", "ok": true, "version": "2.1.92", "optional": false, "purpose_key": "prereq_claude_purpose"},
    {"name": "claude_auth", "ok": true, "version": "", "optional": false, "purpose_key": "prereq_auth_purpose"}
  ],
  "all_required_ok": true,
  "platform": "windows",
  "default_root": "C:\\Users\\detna\\Documents\\Workspace"
}
```

**Buttons:** Re-check (re-fires check) + Next (disabled until all_required_ok)

### Page 3: Handoff to Claude Code CLI

**Title:** "Let Claude Code take it from here" (localized)

**What the user sees:**
1. Terminal-style card with command to run:
   ```
   $ cd ~/.clawd-lobster/onboarding
   $ claude
   ```
2. Copy button
3. Live progress panel:
   - [ ] Persona selection — Waiting...
   - [ ] Workspace root — Waiting...
   - [ ] First workspace — Waiting...
   - [ ] Configuration — Waiting...
4. Fallback: "I want to do it manually" → expands old Persona + Workspace UI

**Handoff Mechanism (session-secured):**
1. Server generates `session_id` (UUID4)
2. Creates `~/.clawd-lobster/onboarding/{session_id}/CLAUDE.md` with instructions + session_id
3. User runs `claude` in that directory
4. Claude Code reads CLAUDE.md, guides user interactively
5. After each step: `curl -X POST http://localhost:3333/api/onboarding/update -d '{"session_id":"...","step":"persona","value":"tech"}'`
6. Web polls `GET /api/onboarding/state?session_id=...` every 2s
7. All complete → celebration screen

**New API Endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/onboarding/state` | Current onboarding state (requires session_id param) |
| POST | `/api/onboarding/update` | CLI reports step completion (requires session_id in body) |
| GET | `/api/onboarding/instructions` | Returns CLAUDE.md content for CLI |
| POST | `/api/onboarding/handoff` | Creates session, writes CLAUDE.md, returns session_id |

**State Persistence:** `~/.clawd-lobster/onboarding/{session_id}/state.json`
```json
{
  "session_id": "a1b2c3d4-...",
  "phase": "handoff",
  "lang": "zh-TW",
  "platform": "windows",
  "created_at": "2026-04-07T22:00:00Z",
  "persona": null,
  "workspace_root": null,
  "workspace_created": false,
  "config_saved": false
}
```

---

## File Changes

| File | Change | Est. Lines |
|------|--------|-----------|
| `pages.py` | Complete rewrite of `ONBOARDING_PAGE` (3-page wizard + expanded I18N) | ~500 |
| `onboarding.py` | Add auth check, state management, handoff file generation, session logic | ~120 |
| `server.py` | Add 4 new API routes + handoff POST | ~80 |
| `cli.py` | Add `handoff` subcommand (optional, for `clawd-lobster handoff`) | ~40 |

## Implementation Phases

1. **Backend:** State management + session + 4 new API endpoints (test with curl)
2. **Page 1:** Welcome + Language (visible, independent)
3. **Page 2:** Prerequisites babysit (depends on Phase 1 backend)
4. **Page 3:** Handoff + CLAUDE.md generation (depends on Phases 1-3)
5. **Polish:** Fallback, animations, cross-platform test, i18n coverage check

## i18n Key Inventory

See `docs/i18n-keys.md` (to be created before Phase 2).
