# Hooks

Optional hooks that enhance Claude Code behavior. Remove any you don't want.

## auto-format (PostToolUse)

Runs your project's formatter after every file Edit or Write.

**Supported formatters:** black/ruff (Python), prettier (JS/TS/CSS/JSON/MD), rustfmt (Rust), gofmt (Go), rubocop (Ruby)

**To disable:** Remove the PostToolUse entry from `settings.json`, or delete the script.

**To add a formatter:** Edit `auto-format.sh` / `auto-format.ps1` and add a case for your file extension.

## verify-on-stop (Stop)

Quick health check when Claude finishes a turn. Reports uncommitted changes and available test runners.

**What it checks:**
- Uncommitted git changes (modified + staged count)
- Whether a test runner is available (npm test, pytest)

**What it does NOT do:** Run full test suites (too slow for a hook).

**To disable:** Remove the Stop entry from `settings.json`, or delete the script.

## Registration

Hooks are registered in `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{"type": "command", "command": ".claude/hooks/auto-format.sh"}]
    }],
    "Stop": [{
      "matcher": "",
      "hooks": [{"type": "command", "command": ".claude/hooks/verify-on-stop.sh"}]
    }]
  }
}
```

On Windows, change `.sh` to `.ps1` and prefix with `powershell -File`.
