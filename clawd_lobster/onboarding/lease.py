"""Controller lease manager.

Only one actor (web or claude) can mutate onboarding state at a time.
The lease has a TTL (90s default). Renew every 30s. Expired leases
are automatically released.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

from . import state_store

LEASE_TTL_SECONDS = 90
LEASE_RENEW_SECONDS = 30


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


def _is_expired(controller: dict) -> bool:
    """Check if current lease is expired."""
    expires = controller.get("expires_at")
    if not expires:
        return True
    try:
        exp_dt = datetime.fromisoformat(expires)
        return _now() > exp_dt
    except (ValueError, TypeError):
        return True


def acquire(session_id: str, holder: str) -> dict:
    """Attempt to acquire the controller lease.

    Args:
        session_id: onboarding session
        holder: "web" | "claude" | "tui"

    Returns:
        {"ok": True, "lease_id": ..., "expires_at": ...} on success
        {"ok": False, "error": ..., "current_holder": ...} on conflict
    """
    if holder not in ("web", "claude", "tui"):
        return {"ok": False, "error": f"Invalid holder: {holder}"}

    controller = state_store.get_controller(session_id)
    if controller is None:
        return {"ok": False, "error": "Session not found"}

    # Check if there's an active non-expired lease
    if controller.get("lease_id") and not _is_expired(controller):
        if controller.get("holder") == holder:
            # Same holder re-acquiring — just renew
            return renew(session_id, controller["lease_id"])
        return {
            "ok": False,
            "error": "Lease held by another controller",
            "current_holder": controller.get("holder"),
            "expires_at": controller.get("expires_at"),
        }

    # Grant new lease
    lease_id = "lease_" + uuid.uuid4().hex[:8]
    now = _now()
    expires = (now + timedelta(seconds=LEASE_TTL_SECONDS)).isoformat()

    controller.update({
        "lease_id": lease_id,
        "holder": holder,
        "session_id": session_id,
        "acquired_at": now.isoformat(),
        "expires_at": expires,
    })
    state_store.save_controller(session_id, controller)

    state_store.log_event(session_id, {
        "type": "lease_acquired",
        "actor": holder,
        "controller": holder,
        "item_id": None,
        "ok": True,
        "message": f"Lease acquired by {holder} (ttl={LEASE_TTL_SECONDS}s)",
    })

    return {"ok": True, "lease_id": lease_id, "expires_at": expires, "holder": holder}


def renew(session_id: str, lease_id: str) -> dict:
    """Renew an active lease. Returns new expiry."""
    controller = state_store.get_controller(session_id)
    if controller is None:
        return {"ok": False, "error": "Session not found"}

    if controller.get("lease_id") != lease_id:
        return {"ok": False, "error": "Lease ID mismatch"}

    if _is_expired(controller):
        return {"ok": False, "error": "Lease expired"}

    expires = (_now() + timedelta(seconds=LEASE_TTL_SECONDS)).isoformat()
    controller["expires_at"] = expires
    state_store.save_controller(session_id, controller)

    return {"ok": True, "lease_id": lease_id, "expires_at": expires}


def release(session_id: str, holder: str) -> dict:
    """Voluntarily release the lease."""
    controller = state_store.get_controller(session_id)
    if controller is None:
        return {"ok": False, "error": "Session not found"}

    if controller.get("holder") != holder:
        return {"ok": False, "error": f"Lease not held by {holder}"}

    controller.update({
        "lease_id": None,
        "holder": None,
        "acquired_at": None,
        "expires_at": None,
    })
    state_store.save_controller(session_id, controller)

    state_store.log_event(session_id, {
        "type": "lease_released",
        "actor": holder,
        "controller": None,
        "item_id": None,
        "ok": True,
        "message": f"Lease released by {holder}",
    })

    return {"ok": True}


def handoff(session_id: str, from_holder: str, to_holder: str) -> dict:
    """Transfer lease from one holder to another."""
    controller = state_store.get_controller(session_id)
    if controller is None:
        return {"ok": False, "error": "Session not found"}

    if controller.get("holder") != from_holder:
        return {"ok": False, "error": f"Lease not held by {from_holder}"}

    if _is_expired(controller):
        return {"ok": False, "error": "Lease expired, cannot handoff"}

    # Transfer
    lease_id = "lease_" + uuid.uuid4().hex[:8]
    expires = (_now() + timedelta(seconds=LEASE_TTL_SECONDS)).isoformat()

    controller.update({
        "lease_id": lease_id,
        "holder": to_holder,
        "acquired_at": _now_iso(),
        "expires_at": expires,
    })
    state_store.save_controller(session_id, controller)

    state_store.log_event(session_id, {
        "type": "lease_handoff",
        "actor": from_holder,
        "controller": to_holder,
        "item_id": None,
        "ok": True,
        "message": f"Lease transferred from {from_holder} to {to_holder}",
    })

    return {"ok": True, "lease_id": lease_id, "expires_at": expires, "holder": to_holder}


def get_current(session_id: str) -> dict:
    """Get current lease info, cleaning up expired leases."""
    controller = state_store.get_controller(session_id)
    if controller is None:
        return {"ok": False, "error": "Session not found"}

    if controller.get("lease_id") and _is_expired(controller):
        # Auto-expire
        old_holder = controller.get("holder")
        controller.update({
            "lease_id": None,
            "holder": None,
            "acquired_at": None,
            "expires_at": None,
        })
        state_store.save_controller(session_id, controller)
        state_store.log_event(session_id, {
            "type": "lease_expired",
            "actor": "backend",
            "controller": None,
            "item_id": None,
            "ok": True,
            "message": f"Lease auto-expired (was held by {old_holder})",
        })

    return {
        "ok": True,
        "lease_id": controller.get("lease_id"),
        "holder": controller.get("holder"),
        "expires_at": controller.get("expires_at"),
        "revision": controller.get("revision", 0),
    }


def validate_lease(session_id: str, lease_id: str) -> bool:
    """Check if a lease_id is currently valid (not expired, matches)."""
    controller = state_store.get_controller(session_id)
    if controller is None:
        return False
    if controller.get("lease_id") != lease_id:
        return False
    return not _is_expired(controller)
