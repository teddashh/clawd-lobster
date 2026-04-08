"""
clawd_lobster.dashboard — Workspace and health data provider.

Reads workspaces.json and per-workspace state to provide data
for both the CLI status command and the web dashboard.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _find_workspaces_json() -> Path:
    """Find workspaces.json from config or repo."""
    config_path = Path.home() / ".clawd-lobster" / "config.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            wrapper = config.get("wrapper_dir", "")
            if wrapper:
                candidate = Path(wrapper) / "workspaces.json"
                if candidate.exists():
                    return candidate
        except (json.JSONDecodeError, OSError):
            pass
    return Path(__file__).resolve().parent.parent / "workspaces.json"


def get_workspaces() -> list[dict[str, Any]]:
    """Return a list of registered workspace entries."""
    ws_path = _find_workspaces_json()
    if not ws_path.exists():
        return []
    try:
        data = json.loads(ws_path.read_text(encoding="utf-8"))
        return data.get("workspaces", [])
    except (json.JSONDecodeError, OSError):
        return []
