# Heartbeat

> OS-level watchdog that keeps Claude Code sessions alive by reviving dead ones every 30 minutes.

## What It Does

Heartbeat monitors Claude Code session health and automatically revives sessions that have gone silent. It reads `workspaces.json` to find tracked sessions, checks their status, and uses `claude --resume` to bring dead ones back. No custom daemon -- the OS scheduler is the watchdog.

## How It Works

The OS scheduler (Task Scheduler on Windows, launchd on macOS, cron on Linux) runs the entrypoint script on a fixed interval.

Each tick:
1. Reads `workspaces.json` for all registered sessions.
2. Checks each session's last heartbeat timestamp.
3. If a session is dead and `auto_revive` is enabled, runs `claude --resume <session-id>`.
4. Logs results.

**Entrypoints:**
- Unix/macOS: `scripts/heartbeat.sh`
- Windows: `scripts/heartbeat.ps1`

**Cron expression:** `*/30 * * * *` (every 30 minutes)

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `interval_minutes` | integer | `30` | Heartbeat check interval in minutes |
| `auto_revive` | boolean | `true` | Automatically revive dead sessions |

## Dependencies

| Type | Requirement |
|------|-------------|
| System | `claude` CLI installed and on PATH |
| Skills | None |

## Credentials

None required.

## Maintenance

- No Python dependencies to update -- pure shell scripts.
- If Claude Code changes the `--resume` flag or session ID format, the entrypoint scripts will need updating.
- Health check runs every 1800 seconds (30 minutes) via command execution.
- To adjust frequency, change both `interval_minutes` in config and the OS scheduler entry.
- On Windows, verify the Task Scheduler entry points to the correct `heartbeat.ps1` path.

**Version:** 0.3.0 | **Kind:** cron | **Category:** core
