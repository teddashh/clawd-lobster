"""HTTP API handlers for onboarding.

These are called by the main server.py router. Each function takes
a parsed request body (dict) and returns a response dict + status code.
"""
from __future__ import annotations

from typing import Any

from . import state_store, lease, intents, manifest, probes, executor, handoff


# ---------------------------------------------------------------------------
# Onboarding session
# ---------------------------------------------------------------------------

def create_session(body: dict) -> tuple[dict, int]:
    """POST /api/onboarding/session — Create new onboarding session."""
    lang = body.get("lang", "en")
    state, token = state_store.create_session(lang)

    # Load skill manifests and add items
    manifests = manifest.load_skill_manifests()
    if manifests:
        items = manifest.manifests_to_items(manifests)
        state_store.add_items(state, items)
        state_store.save_state(state["session_id"], state)

    return {
        "ok": True,
        "session_id": state["session_id"],
        "token": token,  # returned ONCE, never stored
        "state": state,
    }, 200


def get_state(query: dict) -> tuple[dict, int]:
    """GET /api/onboarding/state — Read current state."""
    session_id = query.get("session_id", [""])[0] if isinstance(query.get("session_id"), list) else query.get("session_id", "")

    if not session_id:
        state = state_store.get_latest_session()
        if state:
            return {"ok": True, "state": state}, 200
        return {"ok": False, "error": "No active session"}, 404

    state = state_store.get_state(session_id)
    if state is None:
        return {"ok": False, "error": "Session not found"}, 404
    return {"ok": True, "state": state}, 200


def get_manifest(query: dict) -> tuple[dict, int]:
    """GET /api/onboarding/manifest — Return resolved onboarding plan."""
    manifests = manifest.load_skill_manifests()
    catalog = manifest.get_skill_display(manifests)
    items = manifest.manifests_to_items(manifests)

    return {
        "ok": True,
        "skills": catalog,
        "items": items,
        "tiers": {
            "foundation": [i for i in items if i.get("tier") == "foundation"],
            "required": [i for i in items if i.get("tier") == "required"],
            "optional": [i for i in items if i.get("tier") == "optional"],
            "onetime": [i for i in items if i.get("tier") == "onetime"],
        },
    }, 200


def apply_intent(body: dict) -> tuple[dict, int]:
    """POST /api/onboarding/intent — Apply a state transition."""
    session_id = body.get("session_id", "")
    lease_id = body.get("lease_id", "")
    intent_name = body.get("intent", "")
    item_id = body.get("item_id")
    payload = body.get("payload", {})
    expected_revision = body.get("expected_revision")

    if not session_id or not lease_id or not intent_name:
        return {"ok": False, "error": "session_id, lease_id, and intent required"}, 400

    result = intents.apply_intent(
        session_id, lease_id, intent_name,
        item_id=item_id, payload=payload,
        expected_revision=expected_revision,
    )

    status = 200 if result.get("ok") else 409
    return result, status


def run_reconcile(body: dict) -> tuple[dict, int]:
    """POST /api/onboarding/reconcile — Run full reconciliation."""
    session_id = body.get("session_id", "")
    if not session_id:
        return {"ok": False, "error": "session_id required"}, 400

    result = probes.reconcile(session_id)
    status = 200 if result.get("ok") else 500
    return result, status


# mark_complete removed — completion goes through intent("complete") via /api/onboarding/intent


def get_events(query: dict) -> tuple[dict, int]:
    """GET /api/onboarding/events — Incremental event feed."""
    session_id = query.get("session_id", [""])[0] if isinstance(query.get("session_id"), list) else query.get("session_id", "")
    after = int(query.get("after", [0])[0]) if isinstance(query.get("after"), list) else int(query.get("after", 0))

    if not session_id:
        return {"ok": False, "error": "session_id required"}, 400

    events = state_store.get_events(session_id, after=after)
    return {"ok": True, "events": events}, 200


def get_health(query: dict) -> tuple[dict, int]:
    """GET /api/onboarding/health — Aggregate health summary."""
    results = probes.run_all_probes()
    return {"ok": True, "probes": results}, 200


def get_item_health(item_id: str) -> tuple[dict, int]:
    """GET /api/onboarding/health/<item_id> — Per-item probe."""
    result = probes.run_probe(item_id)
    return {"ok": True, "item_id": item_id, "probe": result}, 200


# ---------------------------------------------------------------------------
# Controller lease
# ---------------------------------------------------------------------------

def acquire_lease(body: dict) -> tuple[dict, int]:
    """POST /api/controller/acquire — Request controller lease."""
    session_id = body.get("session_id", "")
    holder = body.get("holder", "")

    if not session_id or not holder:
        return {"ok": False, "error": "session_id and holder required"}, 400

    result = lease.acquire(session_id, holder)
    status = 200 if result.get("ok") else 409
    return result, status


def renew_lease(body: dict) -> tuple[dict, int]:
    """POST /api/controller/renew — Renew active lease."""
    session_id = body.get("session_id", "")
    lease_id = body.get("lease_id", "")

    if not session_id or not lease_id:
        return {"ok": False, "error": "session_id and lease_id required"}, 400

    result = lease.renew(session_id, lease_id)
    status = 200 if result.get("ok") else 409
    return result, status


def release_lease(body: dict) -> tuple[dict, int]:
    """POST /api/controller/release — Release lease. Requires lease_id."""
    session_id = body.get("session_id", "")
    holder = body.get("holder", "")
    lease_id = body.get("lease_id", "")

    if not session_id or not holder or not lease_id:
        return {"ok": False, "error": "session_id, holder, and lease_id required"}, 400

    result = lease.release(session_id, holder, lease_id=lease_id)
    return result, 200 if result.get("ok") else 409


def handoff_lease(body: dict) -> tuple[dict, int]:
    """POST /api/controller/handoff — Transfer lease. Requires lease_id."""
    session_id = body.get("session_id", "")
    from_holder = body.get("from", "")
    to_holder = body.get("to", "")
    lease_id = body.get("lease_id", "")

    if not session_id or not from_holder or not to_holder or not lease_id:
        return {"ok": False, "error": "session_id, from, to, and lease_id required"}, 400

    result = lease.handoff(session_id, from_holder, to_holder, lease_id=lease_id)
    status = 200 if result.get("ok") else 409
    return result, status


def get_controller(query: dict) -> tuple[dict, int]:
    """GET /api/controller — Current lease holder."""
    session_id = query.get("session_id", [""])[0] if isinstance(query.get("session_id"), list) else query.get("session_id", "")

    if not session_id:
        return {"ok": False, "error": "session_id required"}, 400

    result = lease.get_current(session_id)
    return result, 200


# ---------------------------------------------------------------------------
# Skills catalog
# ---------------------------------------------------------------------------

def get_skills_catalog(query: dict) -> tuple[dict, int]:
    """GET /api/skills/catalog — All skills with onboarding metadata."""
    manifests = manifest.load_skill_manifests()
    catalog = manifest.get_skill_display(manifests)
    return {"ok": True, "skills": catalog}, 200


def verify_skill(skill_id: str) -> tuple[dict, int]:
    """POST /api/skills/<skill_id>/verify — Run probe."""
    result = probes.run_probe(skill_id)
    return {"ok": True, "skill_id": skill_id, "probe": result}, 200


def install_skill(body: dict) -> tuple[dict, int]:
    """POST /api/skills/<skill_id>/install — Execute full skill setup."""
    session_id = body.get("session_id", "")
    skill_id = body.get("skill_id", "")
    lease_id = body.get("lease_id", "")
    config_values = body.get("config", {})

    if not session_id or not skill_id or not lease_id:
        return {"ok": False, "error": "session_id, skill_id, and lease_id required"}, 400

    result = executor.execute_skill_setup(
        session_id, skill_id, lease_id, config_values=config_values,
    )
    status = 200 if result.get("ok") else 500
    return result, status


def register_jobs(body: dict) -> tuple[dict, int]:
    """POST /api/jobs/register — Register OS scheduler for a skill."""
    skill_id = body.get("skill_id", "")
    if not skill_id:
        return {"ok": False, "error": "skill_id required"}, 400

    results = executor.register_skill_jobs(skill_id)
    if not results:
        return {"ok": True, "message": f"No scheduled jobs for {skill_id}", "results": []}, 200

    all_ok = all(r.get("ok") for r in results)
    return {"ok": all_ok, "results": results}, 200 if all_ok else 500


def get_jobs_status(query: dict) -> tuple[dict, int]:
    """GET /api/jobs/status — Check all scheduler registrations."""
    skill_ids = ["evolve", "heartbeat"]
    statuses = {}
    for sid in skill_ids:
        statuses[sid] = executor.check_scheduler(sid)
    return {"ok": True, "jobs": statuses}, 200


# ---------------------------------------------------------------------------
# Handoff
# ---------------------------------------------------------------------------

def generate_handoff(body: dict) -> tuple[dict, int]:
    """POST /api/onboarding/handoff — Generate Claude Code handoff package."""
    session_id = body.get("session_id", "")
    port = body.get("port", 3333)
    workspace_dir = body.get("workspace_dir")

    if not session_id:
        return {"ok": False, "error": "session_id required"}, 400

    token = body.get("token")  # pass token so curl examples include auth
    result = handoff.generate_handoff(session_id, port=port, workspace_dir=workspace_dir, token=token)
    status = 200 if result.get("ok") else 500
    return result, status


def detect_handoff_state(body: dict) -> tuple[dict, int]:
    """POST /api/onboarding/detect — Detect active handoff in a workspace."""
    workspace_dir = body.get("workspace_dir", "")
    if not workspace_dir:
        return {"ok": False, "error": "workspace_dir required"}, 400

    result = handoff.detect_handoff(workspace_dir)
    if result:
        return {"ok": True, "handoff": result}, 200
    return {"ok": False, "message": "No active handoff"}, 404
