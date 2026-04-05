# Heartbeat — Session Lifecycle Manager

!uname -a 2>/dev/null || systeminfo | findstr /B /C:"OS Name" /C:"OS Version" 2>/dev/null || echo "Unknown OS"
!claude --version 2>/dev/null || echo "Claude CLI not found"

Clawd-Lobster agents are **always alive**. The OS scheduler runs a heartbeat every 30 minutes that ensures every registered workspace has a running Claude Code session. Dead sessions are automatically revived.

## How it works

```
OS Scheduler (every 30 min)
    │
    ▼ heartbeat.ps1 / heartbeat.sh
    │
    ▼ Scan workspaces.json
    │
    For each workspace:
    ├─ Session alive? → skip
    └─ Session dead?  → claude --resume (revive)
    │
    ▼ Update client status (sessions_alive, last_heartbeat)
    ▼ Push status to git (next sync cycle)
```

## What this means

- **Terminal open → session alive → agent has full context**
- **Terminal closed → heartbeat detects → revives with --resume**
- **All sessions visible via Claude Code Remote / App**
- **Client status tracked: which machines are alive, how many sessions running**

## This is NOT a daemon

We don't run a custom 24/7 process. The OS scheduler is the heartbeat. Claude Code sessions are the agents. `--resume` restores full context. This gives us:

- Zero custom daemon code to maintain
- OS-level reliability (Task Scheduler / launchd / cron never crash)
- Each session runs the real Claude Code (not a knockoff engine)
- Automatic upgrades when Anthropic ships new features

## Inside each session

Once a session is alive, the agent can use `/loop` or `/schedule` for in-session tasks:
- Periodic memory compaction
- P1 question review
- Knowledge consolidation
- Learned skill improvement

These in-session tasks only run when the terminal is open. The heartbeat ensures terminals stay open.

## Configuration

The heartbeat respects:
- `workspaces.json` — which workspaces to monitor
- `config.json` — domain filter (work/personal/hybrid)
- Machine ID — only manages sessions for this machine's workspaces

## Gotchas

1. **Reviving a session that crashed for a reason.** If a Claude Code session crashed due to a config error, bad MCP server, or corrupted state, heartbeat will revive it every 30 minutes in an infinite crash loop. Check session logs before assuming "session died randomly" — the root cause may need fixing first.

2. **`--resume` without a valid session to resume.** If the session file is corrupted or deleted, `claude --resume` fails silently or starts a fresh session without the previous context. Heartbeat should verify the session file exists before attempting resume.

3. **Task Scheduler vs cron path differences.** On Windows, Task Scheduler requires absolute paths and the correct Python/Node environment. On Linux/macOS, cron inherits a minimal PATH. The heartbeat script must work across both — never assume shell aliases or virtualenvs are available.

4. **Multiple heartbeats racing on the same workspace.** If the OS scheduler fires twice quickly (e.g., after sleep/wake), two heartbeat instances may try to revive the same session simultaneously, creating duplicate processes. The script should use a lock file or PID check.

5. **Heartbeat reports "all alive" but sessions are zombies.** A Claude Code process may exist but be hung (consuming no CPU, responding to nothing). Checking process existence is not enough — heartbeat should verify the session is responsive, not just running.
