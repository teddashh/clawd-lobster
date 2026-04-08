"""Intent-based state transitions.

All state mutations flow through apply_intent(). This is the sole
mutation path — web, TUI, and Claude all call this via the API.
"""
from __future__ import annotations

from typing import Any

from . import state_store, lease

# Valid status transitions
_VALID_TRANSITIONS = {
    "pending": {"running", "skipped"},
    "running": {"succeeded", "failed"},
    "failed": {"running", "skipped"},  # retry or skip
    "blocked": {"pending", "skipped"},
    "skipped": {"pending"},  # un-skip
    "succeeded": set(),  # terminal
}

# Items that can be skipped
_SKIPPABLE_TIERS = {"optional", "onetime"}


def apply_intent(
    session_id: str,
    lease_id: str,
    intent: str,
    item_id: str | None = None,
    payload: dict[str, Any] | None = None,
    expected_revision: int | None = None,
) -> dict:
    """Apply a state transition intent.

    Args:
        session_id: onboarding session
        lease_id: must hold a valid lease
        intent: one of set_status, set_facts, set_foundation, skip_item, complete
        item_id: target item (required for most intents)
        payload: intent-specific data
        expected_revision: optimistic concurrency check

    Returns:
        {"ok": True, "state": updated_state} on success
        {"ok": False, "error": ...} on failure
    """
    if payload is None:
        payload = {}

    # Validate lease
    if not lease.validate_lease(session_id, lease_id):
        return {"ok": False, "error": "Invalid or expired lease"}

    # Load state
    state = state_store.get_state(session_id)
    if state is None:
        return {"ok": False, "error": "Session not found"}

    # Optimistic concurrency
    if expected_revision is not None and state.get("revision") != expected_revision:
        return {
            "ok": False,
            "error": "Revision mismatch",
            "expected": expected_revision,
            "actual": state.get("revision"),
        }

    # Get controller info for actor attribution
    controller = state_store.get_controller(session_id)
    actor = controller.get("holder", "unknown") if controller else "unknown"

    # Dispatch intent
    handlers = {
        "set_status": _intent_set_status,
        "set_facts": _intent_set_facts,
        "set_foundation": _intent_set_foundation,
        "skip_item": _intent_skip_item,
        "complete": _intent_complete,
        "add_items": _intent_add_items,
    }

    handler = handlers.get(intent)
    if handler is None:
        return {"ok": False, "error": f"Unknown intent: {intent}"}

    result = handler(state, item_id, payload, actor)
    if not result.get("ok"):
        # Log failed intent
        state_store.log_event(session_id, {
            "type": "intent_rejected",
            "actor": actor,
            "controller": actor,
            "item_id": item_id,
            "intent": intent,
            "ok": False,
            "message": result.get("error", ""),
        })
        return result

    # Recompute phase
    state["phase"] = state_store.compute_phase(state)

    # Save
    state_store.save_state(session_id, state)

    # Log success
    state_store.log_event(session_id, {
        "type": "intent_applied",
        "actor": actor,
        "controller": actor,
        "item_id": item_id,
        "intent": intent,
        "ok": True,
        "revision": state["revision"],
        "message": result.get("message", ""),
    })

    return {"ok": True, "state": state}


# ---------------------------------------------------------------------------
# Intent handlers
# ---------------------------------------------------------------------------

def _intent_set_status(
    state: dict, item_id: str | None, payload: dict, actor: str,
) -> dict:
    """Change an item's status."""
    if not item_id:
        return {"ok": False, "error": "item_id required"}

    new_status = payload.get("status")
    if not new_status:
        return {"ok": False, "error": "payload.status required"}

    item = state_store.find_item(state, item_id)
    if item is None:
        return {"ok": False, "error": f"Item not found: {item_id}"}

    current = item.get("status", "pending")
    valid_next = _VALID_TRANSITIONS.get(current, set())
    if new_status not in valid_next:
        return {"ok": False, "error": f"Invalid transition: {current} → {new_status}"}

    # Check dependencies for "running"
    if new_status == "running":
        for dep_id in item.get("depends_on", []):
            dep = state_store.find_item(state, dep_id)
            if dep and dep.get("status") not in ("succeeded", "skipped"):
                return {"ok": False, "error": f"Dependency not met: {dep_id}"}

    item["status"] = new_status
    item["last_actor"] = actor

    if new_status == "running":
        item["started_at"] = state_store._now_iso()
    elif new_status in ("succeeded", "failed", "skipped"):
        item["completed_at"] = state_store._now_iso()

    if new_status == "failed":
        item["retry_count"] = item.get("retry_count", 0) + 1
        item["error"] = payload.get("error")

    if new_status == "succeeded":
        item["error"] = None

    return {"ok": True, "message": f"{item_id}: {current} → {new_status}"}


def _intent_set_facts(
    state: dict, item_id: str | None, payload: dict, actor: str,
) -> dict:
    """Update facts on an item (e.g., package_installed=True)."""
    if not item_id:
        return {"ok": False, "error": "item_id required"}

    facts = payload.get("facts")
    if not facts or not isinstance(facts, dict):
        return {"ok": False, "error": "payload.facts required (dict)"}

    item = state_store.find_item(state, item_id)
    if item is None:
        return {"ok": False, "error": f"Item not found: {item_id}"}

    item.setdefault("facts", {}).update(facts)
    item["last_actor"] = actor
    return {"ok": True, "message": f"{item_id}: facts updated"}


def _intent_set_foundation(
    state: dict, item_id: str | None, payload: dict, actor: str,
) -> dict:
    """Set a foundation value (language, workspace_root, etc.)."""
    if not item_id:
        return {"ok": False, "error": "item_id required"}

    item = state_store.find_item(state, item_id)
    if item is None:
        return {"ok": False, "error": f"Item not found: {item_id}"}

    if item.get("tier") != "foundation":
        return {"ok": False, "error": f"{item_id} is not a foundation item"}

    value = payload.get("value")
    item["facts"] = {"value": value}
    item["status"] = "succeeded"
    item["completed_at"] = state_store._now_iso()
    item["last_actor"] = actor
    return {"ok": True, "message": f"{item_id}: set to {value}"}


def _intent_skip_item(
    state: dict, item_id: str | None, payload: dict, actor: str,
) -> dict:
    """Skip an optional item."""
    if not item_id:
        return {"ok": False, "error": "item_id required"}

    item = state_store.find_item(state, item_id)
    if item is None:
        return {"ok": False, "error": f"Item not found: {item_id}"}

    if item.get("tier") not in _SKIPPABLE_TIERS:
        return {"ok": False, "error": f"Cannot skip required item: {item_id}"}

    item["status"] = "skipped"
    item["completed_at"] = state_store._now_iso()
    item["last_actor"] = actor
    item["facts"]["skip_reason"] = payload.get("reason", "user choice")
    return {"ok": True, "message": f"{item_id}: skipped"}


def _intent_complete(
    state: dict, item_id: str | None, payload: dict, actor: str,
) -> dict:
    """Mark onboarding complete."""
    # Check all required items are done
    for item in state.get("items", []):
        if item.get("tier") in ("foundation", "required"):
            if item.get("status") not in ("succeeded", "skipped"):
                return {
                    "ok": False,
                    "error": f"Required item not complete: {item['id']} ({item.get('status')})",
                }

    state["phase"] = "complete"
    return {"ok": True, "message": "Onboarding complete"}


def _intent_add_items(
    state: dict, item_id: str | None, payload: dict, actor: str,
) -> dict:
    """Add new items (e.g., skill items loaded from manifests)."""
    items = payload.get("items")
    if not items or not isinstance(items, list):
        return {"ok": False, "error": "payload.items required (list)"}

    state_store.add_items(state, items)
    return {"ok": True, "message": f"Added {len(items)} items"}
