"""
clawd_lobster.dashboard — Workspace and health data provider.

Reads workspaces.json, config.json, and per-workspace state to
provide data for both the CLI status command and the web dashboard.
"""

from typing import Any


def get_workspaces() -> list[dict[str, Any]]:
    """Return a list of registered workspace entries.

    Each entry is a dict with keys: id, path, repo, domain, deploy, created.
    Returns an empty list if no workspaces are registered.
    """
    # TODO: Phase 5 — read from workspaces.json
    return []
