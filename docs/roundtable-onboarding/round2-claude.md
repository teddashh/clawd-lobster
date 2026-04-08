# Round 2: Claude Opus 4.6 — Cross-Examination & Concessions

## Concessions

I concede on three points:

### 1. Daemon ≠ Scheduler (Codex was right)
I withdraw the single-daemon-as-scheduler proposal. OS schedulers (cron/Task Scheduler/launchd) remain the source of truth for recurring jobs. The web server is a separate, stoppable process. The dashboard inspects and manages OS jobs but does not own them.

### 2. Don't mix skills with non-skills (Codex was right)
GitHub Hub and sync-all are infrastructure, not skills. They don't belong in skill.json manifests or the skills dashboard tab. I accept the separation into:
- **Foundations:** language, auth, workspace root, Hub
- **Skills:** manifest-driven, from skill.json
- **Jobs:** OS scheduler entries tied to specific skills

### 3. Shared rendering is a trap (Gemini was right)
Web and TUI share API + state, not rendering. No Textual-web hybrid.

---

## Synthesis: The Agent-Guided Architecture

Ted's insight + Gemini's "context-aware webpage" + Codex's manifest-driven queue converge into something new. Let me propose the merged architecture.

### The Flow

```
install.ps1 / install.sh
  │
  ├── 1. Install prerequisites (Python, Node, Git)
  ├── 2. npm install -g @anthropic-ai/claude-code  (if not present)
  ├── 3. pip install clawd-lobster
  ├── 4. clawd-lobster init  (create ~/.clawd-lobster/config.json, first workspace)
  ├── 5. clawd-lobster serve --daemon  (web dashboard starts, port 3333)
  │       └── Dashboard renders in ONBOARDING mode
  │           └── Page embeds JSON state: { phase: "foundations", step: 0, ... }
  ├── 6. Open browser → localhost:3333/?token=<generated>
  └── 7. Open terminal in first workspace → launch claude
          └── Claude reads workspace context → sees onboarding state
          └── Claude + Web together guide the user
```

### The "Escape Room" Model

The web dashboard and Claude Code are **co-pilots**, not master-slave:

```
┌─────────────────────────────────────────────────┐
│  WEB (Visual Layer)          │  CLAUDE (Guide)   │
│                              │                   │
│  Shows current skill card    │  Explains what    │
│  Shows setup progress        │  this skill does  │
│  Shows config forms          │  Answers questions│
│  Shows error diagnostics     │  Runs setup cmds  │
│  Embeds state as JSON        │  Reads state JSON │
│                              │  Updates state    │
│  User clicks buttons         │  User talks       │
│  Web calls API               │  Claude calls API │
│                              │                   │
│  Either can advance the flow │                   │
└─────────────────────────────────────────────────┘
```

**Key principle:** The web is NOT a dumb wizard that Claude reads instructions from. The web is a **stateful visual companion**. Claude doesn't need CLAUDE.md to know what to do — the web's embedded state tells Claude exactly where the user is.

### State Machine

```json
{
  "onboarding": {
    "phase": "foundations | skills_required | skills_optional | jobs | complete",
    "current_item": "memory-server",
    "items_done": ["language", "auth", "hub"],
    "items_remaining": ["memory-server", "spec", "absorb", ...],
    "errors": [],
    "token": "abc123..."
  }
}
```

This lives at `~/.clawd-lobster/state.json`. Both web and Claude read/write it.

### Skill Tiers (Merging Codex + Gemini proposals)

I propose merging Codex's 4-category model with Gemini's tiered disclosure:

**Tier 1: Foundations (not skills — must complete)**
1. Language selection
2. Claude Code auth verification
3. GitHub Hub registration
4. Workspace root + first workspace

**Tier 2: Core Skills (required — walk through each)**
5. memory-server — Install + verify MCP
6. spec — Explain + enable
7. absorb — Explain + optional Oracle Vault setup HERE
8. evolve — Explain + register cron
9. heartbeat — Explain + register cron
10. deploy — Explain + check Docker

**Tier 3: Power Skills (optional — explain each, user chooses)**
11. codex-bridge — Install Codex CLI + auth
12. gemini-bridge — Install Gemini CLI + auth
13. notebooklm-bridge — Install + Google auth
14. connect-odoo — Odoo URL + credentials + register poller

**Tier 4: One-time Actions (run once, not revisited)**
15. migrate — Scan legacy systems
16. sync-all — Register 30-min scheduler

**Post-setup verification:**
17. Health check all enabled skills

Each tier is a "chapter" in the Skill Parade. The user sees which chapter they're in, and can't skip Tier 2 before Tier 1 is done.

---

## Remaining Disputes for Round 3

### 1. TUI Timing
Codex says TUI is premature. Gemini says Textual is right if R10 requires full dashboard. I say: **start with `rich` for onboarding (lightweight), plan Textual dashboard for v2.** This gives Ted TUI onboarding NOW without the full dashboard commitment.

### 2. How Claude reads web state
Gemini suggests meta tags / hidden JSON in DOM. I say: **simpler — just read `~/.clawd-lobster/state.json`.** Claude doesn't need to parse HTML. The web writes state.json, Claude reads state.json. Same source of truth, no HTML scraping.

### 3. Token auth implementation
Gemini proposes Jupyter-style `?token=abc123`. I agree, but: **who generates the token?** Proposal: `clawd-lobster init` generates a random token, saves it in config.json, passes it to the web server. First browser open includes the token. Subsequent opens from Claude can use the stored token.

### 4. Credential management v1
Codex says file-based with restrictive permissions. I now agree for v1. But I want a clear abstraction boundary so v2 keyring is a drop-in replacement, not a rewrite.

### Questions for Round 3
1. Should the web dashboard be a SPA (single page app with JS routing) or multi-page?
2. How does the onboarding state machine handle "resume after reboot"?
3. Should we support simultaneous web + TUI sessions viewing the same state?
4. What's the minimum viable onboarding for v1? Can we cut scope?
