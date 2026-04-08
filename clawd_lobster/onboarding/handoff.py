"""Claude Code handoff — generates the staged environment for Claude.

When a user runs `claude` in the onboarding workspace, Claude Code reads
the CLAUDE.md we generate. This file tells Claude:
  1. The onboarding session ID and API base URL
  2. How to acquire the controller lease
  3. How to advance the Skill Parade via intent API
  4. The current state (which items are pending/done/failed)

The web dashboard and Claude are co-pilots. Claude doesn't need
hardcoded scripts — it reads the live state and acts accordingly.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import state_store, manifest


def generate_handoff(
    session_id: str,
    port: int = 3333,
    workspace_dir: str | None = None,
) -> dict:
    """Generate the Claude Code handoff package.

    Creates CLAUDE.md in the workspace with onboarding instructions.

    Returns:
        {"ok": True, "claude_md_path": ..., "session_id": ...}
    """
    state = state_store.get_state(session_id)
    if state is None:
        return {"ok": False, "error": "Session not found"}

    # Determine workspace directory
    if workspace_dir is None:
        # Use the first workspace root from config
        config_path = Path.home() / ".clawd-lobster" / "config.json"
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
                workspace_dir = config.get("workspace_root", "")
            except (json.JSONDecodeError, OSError):
                pass
        if not workspace_dir:
            workspace_dir = str(Path.home() / "Documents" / "Workspace")

    ws_path = Path(workspace_dir)
    ws_path.mkdir(parents=True, exist_ok=True)

    # Build state summary for Claude
    items_summary = _build_items_summary(state)
    api_reference = _build_api_reference(port)

    claude_md = f"""# Clawd-Lobster Onboarding — Agent Guide

You are helping the user set up their AI development environment.
The web dashboard at http://localhost:{port}/onboarding shows the visual progress.
You are the conversational guide. Together you and the web are co-pilots.

## Session Info

- **Session ID:** `{session_id}`
- **API Base:** `http://localhost:{port}`
- **Current Phase:** `{state.get('phase', 'unknown')}`
- **Language:** `{state.get('lang', 'en')}`

## How to Work

1. **Acquire the controller lease** before making any changes:
   ```bash
   curl -s -X POST http://localhost:{port}/api/controller/acquire \\
     -H 'Content-Type: application/json' \\
     -d '{{"session_id":"{session_id}","holder":"claude"}}'
   ```
   Save the `lease_id` from the response. Renew every 25 seconds.

2. **Read current state** to know what's pending:
   ```bash
   curl -s http://localhost:{port}/api/onboarding/state?session_id={session_id}
   ```

3. **Run skill setup** for the next pending item:
   ```bash
   curl -s -X POST http://localhost:{port}/api/skills/SKILL_ID/install \\
     -H 'Content-Type: application/json' \\
     -d '{{"session_id":"{session_id}","lease_id":"YOUR_LEASE_ID","skill_id":"SKILL_ID"}}'
   ```

4. **Set foundations** (language, auth, hub, workspace):
   ```bash
   curl -s -X POST http://localhost:{port}/api/onboarding/intent \\
     -H 'Content-Type: application/json' \\
     -d '{{"session_id":"{session_id}","lease_id":"YOUR_LEASE_ID","intent":"set_foundation","item_id":"foundation.language","payload":{{"value":"en"}}}}'
   ```

5. **Register cron jobs** for cron-type skills:
   ```bash
   curl -s -X POST http://localhost:{port}/api/jobs/register \\
     -H 'Content-Type: application/json' \\
     -d '{{"skill_id":"evolve"}}'
   ```

6. **Release lease** when done or handing back to web:
   ```bash
   curl -s -X POST http://localhost:{port}/api/controller/release \\
     -H 'Content-Type: application/json' \\
     -d '{{"session_id":"{session_id}","holder":"claude"}}'
   ```

## Current Status

{items_summary}

## Behavior Guidelines

- **Explain each skill** before setting it up — what it does, why it matters
- **Ask permission** before installing anything (pip install, npm install, etc.)
- **Show progress** — tell the user which step you're on
- **If a step fails**, explain the error and suggest a fix
- **Don't skip required skills** — foundations and required skills must complete
- **Optional skills** — explain what they do, let the user decide to skip or install
- **The web dashboard updates live** — the user can see your progress there

{api_reference}
"""

    # Write CLAUDE.md
    claude_md_path = ws_path / "CLAUDE.md"

    # Don't overwrite if onboarding section already exists — append
    if claude_md_path.exists():
        existing = claude_md_path.read_text(encoding="utf-8")
        if "Clawd-Lobster Onboarding" not in existing:
            claude_md = existing + "\n\n" + claude_md
        else:
            # Update existing onboarding section
            pass  # Keep the new version

    claude_md_path.write_text(claude_md, encoding="utf-8")

    # Also write a state snapshot for quick reference
    state_snapshot_path = ws_path / ".clawd-onboarding.json"
    state_snapshot_path.write_text(
        json.dumps({
            "session_id": session_id,
            "api_base": f"http://localhost:{port}",
            "phase": state.get("phase"),
            "lang": state.get("lang"),
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    state_store.log_event(session_id, {
        "type": "handoff_generated",
        "actor": "backend",
        "controller": None,
        "item_id": None,
        "ok": True,
        "message": f"CLAUDE.md written to {claude_md_path}",
    })

    return {
        "ok": True,
        "claude_md_path": str(claude_md_path),
        "state_snapshot_path": str(state_snapshot_path),
        "session_id": session_id,
    }


def detect_handoff(workspace_dir: str) -> dict | None:
    """Detect if a workspace has an active onboarding handoff.

    Called by Claude Code on startup to check if it should enter
    onboarding mode.

    Returns:
        {"session_id": ..., "api_base": ..., "phase": ...} or None
    """
    snapshot_path = Path(workspace_dir) / ".clawd-onboarding.json"
    if not snapshot_path.exists():
        return None

    try:
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        session_id = data.get("session_id")
        if not session_id:
            return None

        # Verify session still exists
        state = state_store.get_state(session_id)
        if state is None:
            return None

        # If onboarding is complete, clean up
        if state.get("phase") == "complete":
            snapshot_path.unlink(missing_ok=True)
            return None

        return {
            "session_id": session_id,
            "api_base": data.get("api_base", "http://localhost:3333"),
            "phase": state.get("phase"),
            "lang": state.get("lang", "en"),
            "pending_items": [
                i["id"] for i in state.get("items", [])
                if i.get("status") == "pending"
            ],
        }
    except (json.JSONDecodeError, OSError):
        return None


def cleanup_handoff(workspace_dir: str) -> None:
    """Remove onboarding artifacts after completion."""
    snapshot = Path(workspace_dir) / ".clawd-onboarding.json"
    snapshot.unlink(missing_ok=True)

    # Remove onboarding section from CLAUDE.md
    claude_md = Path(workspace_dir) / "CLAUDE.md"
    if claude_md.exists():
        try:
            content = claude_md.read_text(encoding="utf-8")
            if "Clawd-Lobster Onboarding — Agent Guide" in content:
                # Find and remove the onboarding block
                start = content.find("# Clawd-Lobster Onboarding — Agent Guide")
                if start >= 0:
                    content = content[:start].rstrip()
                    if content:
                        claude_md.write_text(content + "\n", encoding="utf-8")
                    else:
                        claude_md.unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_items_summary(state: dict) -> str:
    """Build a markdown summary of current items for CLAUDE.md."""
    lines = []
    tier_names = {
        "foundation": "Foundations",
        "required": "Required Skills",
        "optional": "Power Skills (Optional)",
        "onetime": "One-Time Actions",
    }
    icons = {
        "succeeded": "✅", "failed": "❌", "running": "🔄",
        "pending": "⬜", "skipped": "⏭️", "blocked": "🚫",
    }

    # Group by tier
    tiers: dict[str, list] = {}
    for item in state.get("items", []):
        t = item.get("tier", "other")
        tiers.setdefault(t, []).append(item)

    for tier in ["foundation", "required", "optional", "onetime"]:
        items = tiers.get(tier, [])
        if not items:
            continue
        lines.append(f"\n### {tier_names.get(tier, tier)}")
        for item in items:
            icon = icons.get(item.get("status", "pending"), "⬜")
            name = item.get("title") or item.get("id")
            status = item.get("status", "pending")
            error = f" — {item['error']}" if item.get("error") else ""
            lines.append(f"- {icon} **{name}** ({status}){error}")

    return "\n".join(lines)


def _build_api_reference(port: int) -> str:
    """Build concise API reference for CLAUDE.md."""
    return f"""## Quick API Reference

| Action | Method | Endpoint |
|--------|--------|----------|
| Read state | GET | `http://localhost:{port}/api/onboarding/state?session_id=SID` |
| Read manifest | GET | `http://localhost:{port}/api/onboarding/manifest` |
| Acquire lease | POST | `http://localhost:{port}/api/controller/acquire` |
| Renew lease | POST | `http://localhost:{port}/api/controller/renew` |
| Release lease | POST | `http://localhost:{port}/api/controller/release` |
| Set foundation | POST | `http://localhost:{port}/api/onboarding/intent` |
| Install skill | POST | `http://localhost:{port}/api/skills/SKILL_ID/install` |
| Verify skill | POST | `http://localhost:{port}/api/skills/SKILL_ID/verify` |
| Register job | POST | `http://localhost:{port}/api/jobs/register` |
| Check jobs | GET | `http://localhost:{port}/api/jobs/status` |
| Health check | GET | `http://localhost:{port}/api/onboarding/health` |
| Reconcile | POST | `http://localhost:{port}/api/onboarding/reconcile` |
"""
