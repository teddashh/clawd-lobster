# Codex Bridge

> Delegate parallelizable work and security audits to OpenAI Codex.

## What It Does

Codex Bridge connects Claude Code to an OpenAI Codex subprocess, enabling two
distinct roles: **worker** (parallel tasks, boilerplate generation) and
**critic** (security audits, code review). This lets you offload grunt work
while keeping Claude as the decision-maker.

## How It Works

The skill exposes plugin commands and a direct CLI mode:

| Command | Purpose |
|---------|---------|
| `/codex:review` | Standard code review against local git state |
| `/codex:adversarial-review` | Challenge implementation approach and design |
| `/codex:rescue` | Delegate investigation or fix to Codex |
| `/codex:status` | Check running Codex task status |
| `/codex:result` | Retrieve completed task output |
| `/codex:cancel` | Cancel a running Codex task |

Direct CLI usage is also supported:

```bash
codex exec "your prompt here"
```

## Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `auto_delegate` | boolean | `false` | Auto-delegate eligible tasks to Codex |
| `preferred_model` | string | `gpt-5.3-codex` | Model used for Codex tasks |
| `default_effort` | string | `none` | Effort level: `none`, `low`, `medium`, `high`, `xhigh` |

## Dependencies

- `node >= 18`
- Codex CLI installed and on PATH

## Credentials

| Credential | Type | Notes |
|------------|------|-------|
| `codex-auth` | `chatgpt-plus` or `api-key` | ChatGPT Plus subscription or OpenAI API key |

## Health Check

`codex --version` is executed every 3600 seconds to verify availability.

## Maintenance

**Plugin patch required after updates.** The Codex plugin
(`openai/codex-plugin-cc`) marks `/codex:review` and
`/codex:adversarial-review` with `disable-model-invocation: true` by default,
which prevents Claude from using them proactively. Clawd-lobster patches this
automatically via `scripts/patch-codex-plugin.py`.

After any plugin update (`claude plugin update`), run:

```bash
python scripts/patch-codex-plugin.py
```

Alternatively, let `skill-manager.py reconcile` handle it automatically. The
patch is idempotent and safe to run multiple times.

---

**Version:** 0.1.0 | **Kind:** prompt-pattern | **Default:** disabled (optional)
