# Codex Bridge — Intelligent Work Delegation

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

## How to Delegate

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
node codex-companion.mjs task --background "Complete this task: <task description>. Working directory context: <relevant info>"
```

Or use the Claude Code command directly:
```
/codex:rescue --background "<task description>"
```

Check status periodically:
```
/codex:status
```

Retrieve results:
```
/codex:result <job-id>
```

### Ad-hoc Delegation

Outside of blitz, you can delegate anytime:
```
/codex:rescue "investigate why the auth tests are failing"
/codex:review --background
/codex:adversarial-review
```

### Review Codex Output

**Always review Codex's output before applying.** Codex is capable but not
infallible. Check:
- Does it match the spec?
- Does it follow the project's conventions?
- Are there security concerns?
- Does it integrate with recent changes?

If the output is good, apply it. If not, do it yourself or give Codex
clearer instructions.

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

## Limitations

- Codex must be installed locally (`npm install -g @openai/codex`)
- Codex must be authenticated (`codex login`)
- One task at a time per session (no parallel Codex jobs)
- Review output is read-only (no auto-apply)
- Codex doesn't have access to your MCP memory tools
- Codex doesn't know about your learned skills or decisions

**This is by design.** Codex is a worker, not a partner. It does what
you tell it, well. It doesn't need your full context to write a
database migration or generate test stubs.
