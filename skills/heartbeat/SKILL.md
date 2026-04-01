# Heartbeat — Session Lifecycle Manager

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
