# Gemini Bridge — Cross-Model Second Opinion

!gemini --version 2>/dev/null || echo "Gemini CLI not installed"

Claude is the lead. Gemini is a consultant. You call Gemini when you need a
different brain — not a faster one, not a cheaper one, a **different** one.

---

## Setup (first time)

1. **Install Gemini CLI:**
   ```bash
   npm install -g @google/gemini-cli
   ```

2. **Authenticate (OAuth — uses your Google One AI Pro/Ultra subscription):**
   ```bash
   gemini  # opens browser for Google OAuth login
   ```
   After login, Gemini CLI uses your subscription quota. No API keys needed.

3. **Verify:**
   ```bash
   gemini --version && gemini -p "hello"
   ```

**Important:** If you have `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment
variables set, the CLI will use those instead of OAuth. Remove them to use
your subscription:
```powershell
# Windows
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', $null, 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', $null, 'User')
```

---

## Why Three Agents

The problem isn't token cost. The problem is **round trips**.

Every time you build something, the user checks it, finds an issue, and asks
you to redo it — that's 10-20 minutes wasted. If three agents spend 3 minutes
discussing upfront and catch the issue before you code, that's a net win.

Two checkpoints. Each costs 2-3 minutes. Each can save an entire redo cycle.

```
User's request
    |
    v
[Checkpoint 1: PLAN REVIEW]
  You draft the approach
  → Codex challenges: "what about edge case X?"
  → Gemini validates: "library Y doesn't support Z, use W instead"
  → You revise the plan
  → Build with confidence
    |
    v
[Checkpoint 2: CODE REVIEW]
  You finish the code
  → Codex adversarial review: finds integration bugs
  → Gemini logic check: catches assumption errors
  → You fix before delivering
    |
    v
Deliver to user — first time right
```

**When to trigger each checkpoint:**

| Checkpoint | Trigger | What to ask |
|-----------|---------|-------------|
| Plan Review | Before any task that would take > 15 minutes to redo | "Here's my plan. What am I missing? What will break?" |
| Code Review | After completing significant code, before delivering | "Review this for bugs, wrong assumptions, and integration issues." |

**When NOT to bother:**
- Simple file edits, config changes, documentation
- Tasks where the answer is obvious
- Anything that takes < 5 minutes to redo if wrong

## How to Call

### Plan Review (Checkpoint 1)

```bash
# Ask both in parallel — compare their concerns
codex exec "I'm about to [task]. My plan: [plan]. What's wrong with this?"

gemini -m gemini-3.1-pro -p "I'm about to [task]. My plan: [plan].
What am I missing? What assumptions am I making?"
```

Then synthesize: if both say it's fine, go. If either raises a concern,
address it before coding.

### Code Review (Checkpoint 2)

```bash
# Codex: adversarial (find what's broken)
codex exec review

# Gemini: logical (verify the approach is sound)
gemini -m gemini-3.1-pro -p "Review this implementation against its spec.
Does the code actually do what the spec says? Any logic errors?
[paste key code or point to files]"
```

### Quick Research (anytime)

```bash
gemini -p "Verify: does [library X] support [feature Y]
as of 2026? Cite sources if possible."
```

### Security Review (before shipping auth/crypto)

```bash
gemini -p "Security review this code. Act as a penetration
tester. Find vulnerabilities, not style issues.
Code: [paste code]"
```

## Agent Call Template

When calling Gemini, ALWAYS append the exit protocol to the prompt:

```bash
gemini -p "
[your actual task prompt here]

EXIT PROTOCOL (MANDATORY):
Before you finish, create .agent-audit/ directory if needed, then write
your findings to .agent-audit/gemini-TIMESTAMP.json with this schema:
{
  \"agent\": \"gemini\",
  \"role\": \"consultant\",
  \"timestamp\": \"ISO-8601\",
  \"task\": \"what you were asked\",
  \"findings\": [{\"type\": \"blocker|risk|suggestion\", \"description\": \"...\", \"file\": \"...\"}],
  \"summary\": \"one paragraph\",
  \"disagreements\": []
}
If no findings, write empty array. DO NOT SKIP.
"
```

After Gemini finishes, read `.agent-audit/gemini-*.json` and store important
findings via `memory_record_knowledge` or `memory_log_action`.

**Same applies to claude -p calls:** append the exit protocol, read the
audit JSON after the subprocess finishes.

---

## How to Call Gemini

**Non-interactive (use this in automation):**
```bash
gemini -m gemini-3.1-pro -p "Your prompt here"
```

**With specific model:**
```bash
gemini -m gemini-3-flash -p "Quick question: ..."      # fast, simple queries
gemini -m gemini-3.1-pro -p "Deep analysis: ..."       # thorough, complex reasoning
```

**IMPORTANT syntax notes:**
- `gemini -p "prompt"` — non-interactive, returns result
- `gemini` — interactive mode (avoid in automation)
- `-m` flag selects the model
- Response comes on stdout, errors on stderr

---

## Three-Way Debate Pattern

For critical decisions, consult **both** Codex and Gemini, then synthesize:

```
1. Claude forms initial opinion
2. Ask Codex:  codex exec "Given [context], what's your take on [question]?"
3. Ask Gemini: gemini -m gemini-3.1-pro -p "Given [context], what's your take on [question]?"
4. Claude synthesizes all three perspectives
5. Present the consensus (or the disagreement) to the user
```

**When to use three-way debate:**
- Architecture decisions that are hard to reverse
- Security-critical implementations
- Performance trade-offs with significant cost implications
- Technology choices that affect the next 6+ months

**When NOT to:**
- Simple coding tasks
- Well-established patterns
- Anything where the answer is already clear

---

## Cross-Model Memory Sync

Gemini doesn't know what Claude knows. To give Gemini context before a
consultation, prepare a context block:

```bash
# Quick context dump for Gemini
gemini -m gemini-3.1-pro -p "
Project context:
$(cat CLAUDE.md 2>/dev/null | head -50)

Recent decisions:
$(memory_audit_search limit=3 2>/dev/null || echo 'no audit data')

Question: [your actual question]
"
```

For systematic sync (similar to Codex AGENTS.md sync), a future version
will support `sync-claude-to-gemini.py` that generates a context file
Gemini can reference.

---

## Model Quality Gate

**The gate is relative, not absolute.** What matters is the consultant's
capability *relative to the lead model*, not an absolute tier list.

| You (Lead) | Gemini 3.1 Pro | Gemini 3 Flash | GPT-5.4 Codex |
|-----------|---------------|---------------|--------------|
| Opus 4.6 | Peer — different perspective | Quick research only | Peer — different perspective |
| Sonnet 4.6 | **Upgrade** — stronger brain | Peer | **Upgrade** — stronger brain |

**Rules:**
- Always consult models at your level or above
- Never consult models significantly weaker than yourself
- If the top-tier quota is exhausted and only weaker models remain:
  don't silently downgrade — tell the user and decide yourself
- A wrong second opinion from a weak model is worse than no opinion

---

## Cost Model

- **Gemini CLI (Google AI Studio)** — generous free tier, pay-per-token after
- **Gemini API** — standard Google pricing
- This skill does not track costs. The CLI handles its own billing.

---

## Comparison: Codex Bridge vs Gemini Bridge

| | Codex Bridge | Gemini Bridge |
|---|---|---|
| Best for | Bulk work, code review, implementation | Research, validation, architecture debate |
| Strength | Follows specs precisely, parallel tasks | Broad knowledge, fact-checking, creative alternatives |
| CLI | `codex exec "prompt"` | `gemini -m model -p "prompt"` |
| Auth | ChatGPT Plus subscription | Google OAuth (free tier available) |
| Role | Worker + Critic | Consultant + Validator |

**Use both together** for the strongest results. Codex builds, Gemini validates,
Claude decides.

---

## Gotchas

1. **Don't use Gemini for implementation.** Gemini is a consultant, not a coder in this context. It gives opinions. You (Claude) write the code.

2. **Context window differences.** Gemini has different context limits than Claude. Don't dump your entire codebase — summarize the relevant parts.

3. **Gemini CLI auth expires.** If you get auth errors, the user needs to re-run `gemini` interactively. The skill can't fix this automatically.

4. **Don't over-consult.** Asking Gemini on every trivial decision slows everything down. Reserve it for genuine uncertainty, not routine coding.

5. **Gemini may disagree with Claude.** That's the point. When they disagree, present both views to the user — don't silently pick one. The user decides.
