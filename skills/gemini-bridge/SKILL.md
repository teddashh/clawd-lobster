# Gemini Bridge — Cross-Model Second Opinion

!gemini --version 2>/dev/null || echo "Gemini CLI not installed"

Claude is the lead. Gemini is a consultant. You call Gemini when you need a
different brain — not a faster one, not a cheaper one, a **different** one.

---

## Setup (first time)

1. **Install Gemini CLI:**
   ```bash
   npm install -g @anthropic-ai/gemini  # or follow Google's install guide
   ```

2. **Authenticate:**
   ```bash
   gemini  # interactive login via OAuth
   ```

3. **Verify:**
   ```bash
   gemini --version && gemini -p "hello"
   ```

---

## When to Consult Gemini

### Scenario 1: Uncertainty
You're not confident in your answer. You used words like "I think", "probably",
"might be", "I believe". Stop guessing — get a second opinion.

```bash
gemini -m gemini-2.5-pro -p "I'm working on [context]. My current approach is [X].
Am I missing anything? What would you do differently?"
```

### Scenario 2: Research / Fact-Checking
You need to validate technical facts, API behavior, or library capabilities
that might be outside your training data or might have changed.

```bash
gemini -m gemini-2.5-pro -p "Verify: does [library X] support [feature Y]
as of 2026? Cite sources if possible."
```

### Scenario 3: Complex Decisions
You're choosing between multiple approaches and need a devil's advocate.
Architecture choices, tech stack decisions, trade-off analysis.

```bash
gemini -m gemini-2.5-pro -p "I'm choosing between approach A and approach B
for [problem]. Here's my analysis: [context].
Argue against my preferred choice. What am I not seeing?"
```

### Scenario 4: Security Review
Before shipping auth, encryption, or access control code, get an independent
security review from a brain that hasn't been marinating in the same codebase.

```bash
gemini -m gemini-2.5-pro -p "Security review this code. Act as a penetration
tester. Find vulnerabilities, not style issues.
Code: [paste code]"
```

---

## How to Call Gemini

**Non-interactive (use this in automation):**
```bash
gemini -m gemini-2.5-pro -p "Your prompt here"
```

**With specific model:**
```bash
gemini -m gemini-2.5-flash -p "Quick question: ..."   # fast, cheap
gemini -m gemini-2.5-pro -p "Deep analysis: ..."       # thorough
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
3. Ask Gemini: gemini -m gemini-2.5-pro -p "Given [context], what's your take on [question]?"
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
gemini -m gemini-2.5-pro -p "
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
