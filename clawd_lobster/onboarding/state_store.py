"""Atomic state persistence for onboarding workflow.

All state mutations go through this module. No other code should write
state.json, controller.json, or events.jsonl directly.
"""
from __future__ import annotations

import json
import os
import platform
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_IS_WINDOWS = platform.system() == "Windows"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _base_dir() -> Path:
    return Path.home() / ".clawd-lobster"


def _onboarding_dir(session_id: str) -> Path:
    return _base_dir() / "onboarding" / session_id


# ---------------------------------------------------------------------------
# Atomic JSON I/O
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, data: dict) -> None:
    """Write JSON atomically via temp file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if _IS_WINDOWS and path.exists():
        path.unlink()
    tmp.rename(path)


def _read_json(path: Path) -> dict | None:
    """Read JSON file, returning None if missing or corrupt."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _append_event(path: Path, event: dict) -> None:
    """Append a single JSON line to events.jsonl."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, ensure_ascii=False) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


# ---------------------------------------------------------------------------
# Session creation
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_token() -> str:
    return uuid.uuid4().hex


def _hash_token(token: str) -> str:
    import hashlib
    return "sha256:" + hashlib.sha256(token.encode()).hexdigest()[:32]


# Default items for onboarding
_FOUNDATION_ITEMS = [
    {"id": "foundation.language", "tier": "foundation", "kind": "config",
     "status": "pending", "depends_on": [], "facts": {}},
    {"id": "foundation.claude_auth", "tier": "foundation", "kind": "probe",
     "status": "pending", "depends_on": [], "facts": {}},
    {"id": "foundation.hub", "tier": "foundation", "kind": "config",
     "status": "pending", "depends_on": ["foundation.claude_auth"], "facts": {}},
    {"id": "foundation.workspace_root", "tier": "foundation", "kind": "config",
     "status": "pending", "depends_on": [], "facts": {}},
]


def create_session(lang: str = "en") -> tuple[dict, str]:
    """Create a new onboarding session.

    Returns (state_dict, raw_token).
    The raw token is returned once and never stored — only the hash is persisted.
    """
    session_id = "ob_" + uuid.uuid4().hex[:12]
    token = _new_token()
    now = _now_iso()

    state = {
        "version": 1,
        "session_id": session_id,
        "created_at": now,
        "updated_at": now,
        "revision": 0,
        "token_hash": _hash_token(token),
        "lang": lang,
        "phase": "foundations",
        "items": list(_FOUNDATION_ITEMS),  # deep copy via list()
    }

    # Persist
    d = _onboarding_dir(session_id)
    _atomic_write(d / "state.json", state)

    # Init empty controller
    _atomic_write(d / "controller.json", {
        "lease_id": None,
        "holder": None,
        "session_id": session_id,
        "acquired_at": None,
        "expires_at": None,
        "revision": 0,
    })

    # Log creation event
    _append_event(d / "events.jsonl", {
        "ts": now, "seq": 1, "session_id": session_id,
        "revision": 0, "type": "session_created",
        "actor": "backend", "controller": None,
        "item_id": None, "ok": True,
        "message": f"onboarding session created (lang={lang})",
    })

    return state, token


# ---------------------------------------------------------------------------
# State read/write
# ---------------------------------------------------------------------------

def get_state(session_id: str) -> dict | None:
    """Read current onboarding state."""
    return _read_json(_onboarding_dir(session_id) / "state.json")


def get_controller(session_id: str) -> dict | None:
    """Read current controller lease."""
    return _read_json(_onboarding_dir(session_id) / "controller.json")


def save_state(session_id: str, state: dict) -> None:
    """Persist state atomically. Bumps revision and updated_at."""
    state["revision"] = state.get("revision", 0) + 1
    state["updated_at"] = _now_iso()
    _atomic_write(_onboarding_dir(session_id) / "state.json", state)


def save_controller(session_id: str, controller: dict) -> None:
    """Persist controller lease atomically."""
    controller["revision"] = controller.get("revision", 0) + 1
    _atomic_write(_onboarding_dir(session_id) / "controller.json", controller)


def log_event(session_id: str, event: dict) -> None:
    """Append an event to the audit trail."""
    path = _onboarding_dir(session_id) / "events.jsonl"

    # Auto-assign seq from file line count
    seq = 1
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                seq = sum(1 for _ in f) + 1
        except OSError:
            pass

    event.setdefault("ts", _now_iso())
    event.setdefault("seq", seq)
    event.setdefault("session_id", session_id)
    _append_event(path, event)


def get_events(session_id: str, after: int = 0) -> list[dict]:
    """Read events after a given seq number."""
    path = _onboarding_dir(session_id) / "events.jsonl"
    if not path.exists():
        return []
    events = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                    if evt.get("seq", 0) > after:
                        events.append(evt)
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return events


# ---------------------------------------------------------------------------
# Item helpers
# ---------------------------------------------------------------------------

def find_item(state: dict, item_id: str) -> dict | None:
    """Find an item by ID in the state."""
    for item in state.get("items", []):
        if item["id"] == item_id:
            return item
    return None


def update_item(state: dict, item_id: str, **kwargs: Any) -> bool:
    """Update fields on an item. Returns True if found."""
    item = find_item(state, item_id)
    if item is None:
        return False
    item.update(kwargs)
    return True


def add_items(state: dict, items: list[dict]) -> None:
    """Add items to the state (e.g., when loading skill manifests)."""
    existing_ids = {i["id"] for i in state.get("items", [])}
    for item in items:
        if item["id"] not in existing_ids:
            state["items"].append(item)


def compute_phase(state: dict) -> str:
    """Recompute the current phase based on item statuses."""
    items = state.get("items", [])

    foundations = [i for i in items if i.get("tier") == "foundation"]
    required = [i for i in items if i.get("tier") == "required"]
    optional = [i for i in items if i.get("tier") == "optional"]

    def all_done(group: list) -> bool:
        return all(i.get("status") in ("succeeded", "skipped") for i in group)

    if not all_done(foundations):
        return "foundations"
    if not all_done(required):
        return "skills_required"
    if optional and not all_done(optional):
        return "skills_optional"
    return "complete"


# ---------------------------------------------------------------------------
# Session discovery
# ---------------------------------------------------------------------------

def list_sessions() -> list[str]:
    """List all session IDs."""
    base = _base_dir() / "onboarding"
    if not base.exists():
        return []
    return [
        d.name for d in sorted(base.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        if d.is_dir() and d.name.startswith("ob_")
    ]


def get_latest_session() -> dict | None:
    """Get the most recent session state."""
    sessions = list_sessions()
    if not sessions:
        return None
    return get_state(sessions[0])


def verify_token(session_id: str, token: str) -> bool:
    """Verify a raw token against the stored hash."""
    state = get_state(session_id)
    if state is None:
        return False
    return state.get("token_hash") == _hash_token(token)
