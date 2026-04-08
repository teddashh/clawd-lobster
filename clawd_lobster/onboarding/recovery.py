"""Startup recovery and session reconciliation.

On every server start (or page load), reconcile persisted state
against the real machine. Observed facts win over stored state.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import state_store, probes, lease


def recover_on_startup() -> dict:
    """Run full recovery sequence on server startup.

    1. Find latest active session
    2. Clean up expired leases
    3. Reconcile state against machine facts
    4. Resume from first incomplete required item

    Returns:
        {"ok": True, "session_id": ..., "drift_count": ..., "lease_cleaned": bool}
        or {"ok": False, "reason": "no_session"} if nothing to recover
    """
    sessions = state_store.list_sessions()
    if not sessions:
        return {"ok": False, "reason": "no_session"}

    # Find the most recent non-complete session
    session_id = None
    for sid in sessions:
        st = state_store.get_state(sid)
        if st and st.get("phase") != "complete":
            session_id = sid
            break

    if session_id is None:
        return {"ok": False, "reason": "all_complete"}

    state = state_store.get_state(session_id)
    results = {"ok": True, "session_id": session_id, "drift_count": 0, "lease_cleaned": False}

    # 1. Clean stale lease
    controller = state_store.get_controller(session_id)
    if controller and controller.get("lease_id"):
        current = lease.get_current(session_id)
        if current.get("ok") and current.get("lease_id") is None:
            results["lease_cleaned"] = True

    # 2. Reconcile state against real facts
    probe_results = probes.run_all_probes()
    drift = 0

    for item in state.get("items", []):
        item_id = item["id"]
        if item_id not in probe_results:
            continue

        probe = probe_results[item_id]

        # Drift: state says succeeded but machine disagrees
        if item.get("status") == "succeeded" and not probe.get("verified"):
            item["status"] = "failed"
            item["error"] = f"Recovery: {probe.get('repair_hint', 'verification failed after restart')}"
            drift += 1

        # Drift: state says pending but machine shows it's done
        if item.get("status") in ("pending", "failed") and probe.get("verified"):
            item["status"] = "succeeded"
            item["error"] = None
            drift += 1

        # Update probe facts
        item.setdefault("facts", {})
        item["facts"]["_probe_detected"] = probe.get("detected", False)
        item["facts"]["_probe_verified"] = probe.get("verified", False)

    if drift > 0:
        state["phase"] = state_store.compute_phase(state)
        state_store.save_state(session_id, state)
        state_store.log_event(session_id, {
            "type": "recovery",
            "actor": "backend",
            "controller": None,
            "item_id": None,
            "ok": True,
            "message": f"Startup recovery: {drift} drift(s) found and corrected",
        })

    results["drift_count"] = drift
    results["phase"] = state.get("phase")

    # Find resume point
    resume_item = None
    for item in state.get("items", []):
        if item.get("tier") in ("foundation", "required"):
            if item.get("status") in ("pending", "failed"):
                resume_item = item["id"]
                break

    results["resume_from"] = resume_item
    return results


def validate_state_integrity(session_id: str) -> dict:
    """Check state file for corruption or inconsistency.

    Returns:
        {"valid": True/False, "issues": [...]}
    """
    state = state_store.get_state(session_id)
    if state is None:
        return {"valid": False, "issues": ["State file missing or unreadable"]}

    issues = []

    # Check required fields
    for field in ("version", "session_id", "revision", "phase", "items"):
        if field not in state:
            issues.append(f"Missing field: {field}")

    # Check items structure
    items = state.get("items", [])
    if not isinstance(items, list):
        issues.append("items is not a list")
    else:
        seen_ids = set()
        for item in items:
            item_id = item.get("id")
            if not item_id:
                issues.append("Item missing id")
                continue
            if item_id in seen_ids:
                issues.append(f"Duplicate item id: {item_id}")
            seen_ids.add(item_id)

            status = item.get("status")
            if status not in ("pending", "running", "succeeded", "failed", "skipped", "blocked", None):
                issues.append(f"Invalid status for {item_id}: {status}")

            # Running items without started_at
            if status == "running" and not item.get("started_at"):
                issues.append(f"{item_id} is running but has no started_at")

            # Check dependency references exist
            for dep in item.get("depends_on", []):
                if dep not in seen_ids and not any(i.get("id") == dep for i in items):
                    issues.append(f"{item_id} depends on unknown item: {dep}")

    # Check controller
    controller = state_store.get_controller(session_id)
    if controller is not None:
        holder = controller.get("holder")
        if holder and holder not in ("web", "claude", "tui", None):
            issues.append(f"Invalid controller holder: {holder}")

    # Check events file
    events_path = Path.home() / ".clawd-lobster" / "onboarding" / session_id / "events.jsonl"
    if events_path.exists():
        try:
            lines = events_path.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines):
                if line.strip():
                    try:
                        json.loads(line)
                    except json.JSONDecodeError:
                        issues.append(f"Corrupt event at line {i+1}")
        except OSError:
            issues.append("Events file unreadable")

    return {"valid": len(issues) == 0, "issues": issues}
