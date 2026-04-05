# Codex Bridge — Intelligent Work Delegation

!codex --version 2>/dev/null || echo "Codex CLI not installed"
!codex whoami 2>/dev/null || echo "Codex not authenticated"

Claude is the brain. Codex is an extra pair of hands. You decide when to use them.

---

## Setup (first time)

When a user enables this skill or enters the Codex Bridge settings:

1. **Check if Codex CLI is installed:**
   ```bash
   codex --version
   ```
   If not found, guide the user:
   ```
   To install Codex CLI:
     npm install -g @openai/codex

   Then authenticate:
     codex login

   This will open a browser for ChatGPT Plus login (or you can use an API key).
   ```

2. **Check if authenticated:**
   ```bash
   codex whoami
   ```
   If not authenticated, guide through `codex login`.

3. **Install the official plugin:**
   ```bash
   claude plugin install openai/codex-plugin-cc
   ```

4. **Verify everything works:**
   ```bash
   codex --version && codex whoami
   ```
   Report status to user. If all good, mark credential as verified.

---

## When to Delegate (your judgment, not rules)

You are a senior architect managing a capable assistant. Use your judgment.
Here are patterns to inform your decisions, not rules to follow blindly:

### Good candidates for delegation

- **Parallelizable work** — 10 similar React components, 20 API endpoint stubs,
  database migration scripts for multiple tables. Work that's independent and
  can be done without seeing each other's results.

- **Well-specified implementation** — When the spec, design, and tests are
  already defined. Codex follows instructions well when the instructions are clear.

- **Boilerplate and scaffolding** — Project setup, config files, CI pipelines,
  linter configs. Stuff that follows well-known patterns.

- **Test generation** — Given existing code + Gherkin specs, generate test files.
  You write the code, Codex writes the tests (or vice versa).

- **Bulk refactoring** — Rename across 50 files, update import paths, migrate
  API versions. Tedious but straightforward.

### Use Codex as a second brain (critic, not worker)

Not every delegation is about getting work done. Sometimes you need a
**different perspective** — a second opinion from a brain that hasn't
been marinating in the same codebase as you.

- **Security audit** — You wrote the auth code. Ask Codex to *attack* it:
  ```
  /codex:adversarial-review
  ```
  Codex reviews as an adversary — looking for vulnerabilities, edge cases,
  and design flaws you're too close to see. Read-only. No auto-fix.

- **Architecture debate** — You're choosing between two approaches. Ask Codex
  to argue against your preferred option:
  ```
  /codex:rescue "I'm choosing approach A over B for [reason]. Play devil's
  advocate — argue why B is better. Don't implement anything, just debate."
  ```

- **Code review** — You finished a feature. Get a cold-eye review before merge:
  ```
  /codex:review
  ```
  Fresh perspective, no emotional attachment to the code.

- **Spec challenge** — Before blitz, ask Codex to poke holes in your spec:
  ```
  /codex:rescue "Read openspec/changes/v1/proposal.md and design.md.
  Find 3 things that will break in production. Don't fix them, just list them."
  ```

**The key: Codex critiques, YOU decide.** Codex never auto-applies changes
in review mode. It gives opinions. You evaluate them with your full context.

This is actually MORE valuable for security than doing it yourself — you
can't objectively audit code you just wrote. A different brain can.

### Keep for yourself (write the code)

- **Architecture decisions** — System design, data model choices, trade-offs.
  These need your full context and judgment. (But ask Codex to *challenge*
  your decision afterward.)

- **Security-critical implementation** — Write auth, encryption, and validation
  yourself. Then ask Codex to *review* it adversarially.

- **Code that depends on recent context** — If you just made a decision that
  affects this code, do it yourself. Codex won't have that context.

- **Novel problem-solving** — Debugging weird issues, investigating unknown
  behavior, designing new patterns. This is where your reasoning shines.

- **User-facing communication** — Explaining changes, asking questions,
  presenting options. Stay in the conversation.

### Context-aware delegation

You have awareness of your own state. Use it:

- **Context window filling up?** Delegate the next batch of independent tasks
  to Codex to free your context for judgment calls.

- **Rate limits approaching?** Shift repetitive work to Codex. Preserve your
  throughput for tasks that need deep reasoning.

- **Blitz mode with 200 tasks?** Look for clusters of similar tasks. Delegate
  the cluster, keep the unique ones.

- **Multiple workspaces need attention?** Handle the one that needs judgment,
  delegate the routine work in the other.

---

## How to Call Codex (exact commands)

There are TWO ways to delegate. Choose based on context:

### Method 1: Via Claude Code Plugin Commands (if plugin installed)

These work inside a Claude Code session:
```
/codex:rescue "<task>"                    # general delegation
/codex:rescue --background "<task>"       # background (returns immediately)
/codex:review                             # code review (read-only)
/codex:adversarial-review                 # adversarial review (find flaws)
/codex:status                             # check background jobs
/codex:status <job-id>                    # detailed job status
/codex:result <job-id>                    # retrieve completed output
/codex:cancel <job-id>                    # cancel background job
```

Plugin: `claude plugin install codex` (from openai-codex marketplace).

### Method 2: Via Codex CLI Directly (always works)

Use Bash tool to run Codex directly:

```bash
# Non-interactive execution (run and return result)
codex exec "Your prompt here"

# Non-interactive execution in a specific directory
codex exec --cwd /path/to/workspace "Your prompt here"

# Code review of current repo
codex exec review

# Interactive mode (if you need back-and-forth)
codex "Your prompt here"
```

**IMPORTANT syntax notes:**
- `codex exec "prompt"` — non-interactive, returns result (USE THIS)
- `codex "prompt"` — interactive mode (avoid in automation)
- Do NOT use `codex -p` — that flag does not exist
- The prompt goes AFTER the `exec` subcommand, not as a flag

### Practical Examples

**Ask for a second opinion on architecture:**
```bash
codex exec "Read README.md and design.md in this repo. 
What are the 3 biggest architectural risks? Don't fix anything, just analyze."
```

**Delegate boilerplate generation:**
```bash
codex exec "Create unit test files for all modules in src/services/. 
Follow the existing test patterns in tests/. Use pytest."
```

**Adversarial security review:**
```bash
codex exec "Review src/auth/ for security vulnerabilities.
Act as a penetration tester. Report findings with severity ratings.
Do NOT modify any files."
```

**Spec challenge before blitz:**
```bash
codex exec "Read openspec/changes/v1/proposal.md and design.md.
Find 3 things that will break in production. Just list them with reasoning."
```

### During Blitz (/spec:blitz)

Tasks in tasks.md can have a `[codex]` marker:
```markdown
- [ ] Generate API route stubs (`src/api/routes/`)
- [ ] [codex] Create database migration for users table (`migrations/001_users.sql`)
- [ ] [codex] Generate React components for settings pages (`src/components/settings/`)
- [ ] Implement authentication middleware (`src/middleware/auth.ts`)
```

When you encounter a `[codex]` task during blitz:
```bash
codex exec "Complete this task in the current repo:
Task: <task description>
File: <target file path>
Rules: Make minimal changes. Follow existing code style. Commit when done."
```

### Review Codex Output

**Always review Codex's output before applying.** Codex is capable but not
infallible. Check:
- Does it match the spec?
- Does it follow the project's conventions?
- Are there security concerns?
- Does it integrate with recent changes?

If Codex made commits (during `exec`), review the diff:
```bash
git log --oneline -5    # see what Codex committed
git diff HEAD~1         # review the last commit
```

If the output is good, keep it. If not, `git revert` or do it yourself.

---

## During Evolution

When evolve-tick generates proposals, it can also suggest tasks suitable
for Codex delegation. These proposals will be tagged with
`effort: small` and `tags: ["codex-candidate"]` to indicate they're
good candidates for delegation.

The final decision is always yours. Tags are hints, not orders.

---

## Cost Model

Codex runs on the user's own account:
- **ChatGPT Plus** — included in subscription
- **API key** — pay-per-token

This skill does not track costs. Codex CLI handles its own billing.
The `effort` config option controls compute intensity:
- `none` / `minimal` — fastest, cheapest
- `medium` — balanced (default)
- `high` / `xhigh` — thorough, more expensive

---

## Context Sync: Claude → Codex

By default, Codex doesn't know what Claude knows. The sync bridge fixes this
by converting Claude's project state into Codex's `AGENTS.md` format.

### What gets synced (one-way: Claude → Codex)

| Claude Source | Codex Destination | Content |
|--------------|-------------------|---------|
| `CLAUDE.md` | `AGENTS.md` | Project instructions, conventions, key files |
| Auto-memory | `AGENTS.md` appendix | Key decisions, constraints, architecture |
| Learned skills | `AGENTS.md` appendix | Skills the agent has learned |
| `settings.json` | `~/.codex/config.toml` | Global defaults (first sync only) |

### Setup (automatic on skill enable)

When this skill is enabled, run the sync once:
```bash
python scripts/sync-claude-to-codex.py --workspace <current-workspace>
```

Then set up a cron job to keep it fresh:
```bash
# crontab -e (Unix)
*/30 * * * * cd /path/to/clawd-lobster && python scripts/sync-claude-to-codex.py -q

# Task Scheduler (Windows) — run every 30 min:
# python C:\path\to\clawd-lobster\scripts\sync-claude-to-codex.py -q
```

### Manual sync

```bash
python scripts/sync-claude-to-codex.py                    # current workspace
python scripts/sync-claude-to-codex.py -w /path/to/ws     # specific workspace
python scripts/sync-claude-to-codex.py --global            # global only
python scripts/sync-claude-to-codex.py --dry-run           # preview
```

### Why one-way only?

Claude → Codex, never Codex → Claude. Because:
- Claude has a full memory system (MCP, auto-memory, knowledge base)
- Codex is a task worker — it doesn't accumulate project knowledge
- Claude is the brain; Codex reads Claude's notes before each task

---

## Limitations

- Codex must be installed locally (`npm install -g @openai/codex`)
- Codex must be authenticated (`codex login`)
- One task at a time per session (no parallel Codex jobs)
- Review output is read-only (no auto-apply)
- AGENTS.md has a 32 KiB limit — large memory sets are truncated
- Sync is periodic (not real-time) — Codex sees Claude's state as of last sync

## Gotchas

1. **Using `codex -p` instead of `codex exec`.** The `-p` flag does not exist in Codex CLI. Always use `codex exec "prompt"` for non-interactive execution. This is the single most common invocation error.

2. **Delegating context-dependent work.** Codex does not share Claude's conversation context or recent decisions. If you just made an architectural choice that affects the delegated task, Codex will not know about it and will produce inconsistent code. Only delegate tasks that are self-contained.

3. **Auto-applying Codex review output.** Review mode (`/codex:review`, `/codex:adversarial-review`) is read-only by design. Claude sometimes tries to auto-apply suggested fixes from review output. Always present review findings to the user and let them decide.

4. **Forgetting to sync AGENTS.md before delegation.** Codex reads AGENTS.md for project context. If the sync script hasn't run recently, Codex operates with stale or missing context. Run `sync-claude-to-codex.py` before delegating if the project has changed significantly.

5. **Parallel Codex jobs.** Only one Codex task runs at a time per session. Attempting to launch a second task while one is running will fail or queue unpredictably. Wait for the first to complete before starting another.
