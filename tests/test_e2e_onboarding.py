#!/usr/bin/env python3
"""E2E integration test for the onboarding system.

Written by Codex GPT-5.4 — tests the full HTTP flow end-to-end,
simulating a real user clicking through the web UI.

Run: python tests/test_e2e_onboarding.py
"""
import json
import os
import sys
import tempfile
import threading
import time
from http.client import HTTPConnection
from http.server import HTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TEMP_HOME = tempfile.TemporaryDirectory(prefix="clawd-lobster-e2e-home-")
os.environ["HOME"] = TEMP_HOME.name
os.environ["USERPROFILE"] = TEMP_HOME.name

from clawd_lobster import server as cl_server  # noqa: E402


HOST = "127.0.0.1"


def run_step(label, fn):
    try:
        value = fn()
        print(f"PASS: {label}")
        return value
    except Exception as exc:
        print(f"FAIL: {label}: {exc}")
        raise


def request_json(port, method, path, body=None, token=None):
    headers = {}
    payload = None

    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if token:
        headers["Authorization"] = f"Bearer {token}"

    for attempt in range(3):
        conn = HTTPConnection(HOST, port, timeout=10)
        try:
            conn.request(method, path, body=payload, headers=headers)
            response = conn.getresponse()
            raw = response.read().decode("utf-8")
            status = response.status
            conn.close()
            try:
                data = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                data = {"raw": raw}
            return status, data
        except (ConnectionAbortedError, ConnectionResetError, OSError):
            conn.close()
            if attempt < 2:
                time.sleep(0.2)
                continue
            raise


def assert_status(actual, expected, context):
    if actual != expected:
        raise AssertionError(f"{context}: expected HTTP {expected}, got {actual}")


def expect_json(port, method, path, expected_status, body=None, token=None, context=None):
    status, data = request_json(port, method, path, body=body, token=token)
    assert_status(status, expected_status, context or f"{method} {path}")
    return data


def expect_ok(port, method, path, body=None, token=None, expected_status=200, context=None):
    data = expect_json(
        port, method, path,
        expected_status=expected_status,
        body=body, token=token,
        context=context,
    )
    if not data.get("ok"):
        raise AssertionError(f"{context or f'{method} {path}'} returned ok=false: {data}")
    return data


def get_item(state, item_id):
    for item in state.get("items", []):
        if item.get("id") == item_id:
            return item
    raise AssertionError(f"Missing item: {item_id}")


def wait_for_server(port, timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            data = expect_json(port, "GET", "/api/status", 200, context="GET /api/status")
            if data.get("ok"):
                return
        except Exception:
            pass
        time.sleep(0.05)
    raise RuntimeError("Server did not become ready in time")


def assert_unauthorized(port, session_id):
    checks = [
        ("GET", f"/api/onboarding/state?session_id={session_id}", None),
        ("POST", "/api/controller/acquire", {"session_id": session_id, "holder": "web"}),
        ("POST", "/api/onboarding/intent", {
            "session_id": session_id, "lease_id": "lease_wrong",
            "intent": "set_foundation", "item_id": "foundation.language",
            "payload": {"value": "zh-TW"},
        }),
        ("GET", f"/api/controller?session_id={session_id}", None),
        ("POST", "/api/skills/spec/install", {"session_id": session_id, "lease_id": "lease_wrong"}),
        ("POST", "/api/controller/renew", {"session_id": session_id, "lease_id": "lease_wrong"}),
        ("POST", "/api/controller/handoff", {
            "session_id": session_id, "from": "web", "to": "claude", "lease_id": "lease_wrong",
        }),
        ("POST", "/api/controller/release", {
            "session_id": session_id, "holder": "claude", "lease_id": "lease_wrong",
        }),
        ("GET", "/api/onboarding/health", None),
        ("GET", "/api/skills/catalog", None),
        ("GET", f"/api/onboarding/events?session_id={session_id}", None),
        ("POST", "/api/onboarding/reconcile", {"session_id": session_id}),
    ]

    for method, path, body in checks:
        status, data = request_json(port, method, path, body=body, token=None)
        assert_status(status, 401, f"{method} {path} without token")
        if "Authentication required" not in data.get("error", ""):
            raise AssertionError(f"{method} {path} missing auth error payload: {data}")


def main():
    from http.server import ThreadingHTTPServer
    httpd = ThreadingHTTPServer((HOST, 0), cl_server._Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)

    try:
        run_step("start server on random port", thread.start)
        run_step("wait for server readiness", lambda: wait_for_server(port))

        # Step 1: Create session
        session = run_step(
            "create onboarding session",
            lambda: expect_ok(port, "POST", "/api/onboarding/session",
                              body={"lang": "en"}, context="POST /api/onboarding/session"),
        )
        token = session["token"]
        session_id = session["session_id"]

        # Step 2: Auth enforcement
        run_step("protected endpoints reject missing token",
                 lambda: assert_unauthorized(port, session_id))

        # Step 3: Acquire lease
        acquire = run_step(
            "acquire web controller lease",
            lambda: expect_ok(port, "POST", "/api/controller/acquire",
                              body={"session_id": session_id, "holder": "web"},
                              token=token, context="POST /api/controller/acquire"),
        )
        lease_id = acquire["lease_id"]

        # Step 4: Wrong lease rejected
        wrong_lease = run_step(
            "reject wrong lease id",
            lambda: expect_json(port, "POST", "/api/controller/renew", 409,
                                body={"session_id": session_id, "lease_id": "lease_wrong"},
                                token=token, context="POST /api/controller/renew with wrong lease"),
        )
        if "Lease ID mismatch" not in wrong_lease.get("error", ""):
            raise AssertionError(f"unexpected wrong lease response: {wrong_lease}")

        # Step 5: Set language
        run_step(
            "set foundation.language to zh-TW",
            lambda: expect_ok(port, "POST", "/api/onboarding/intent",
                              body={"session_id": session_id, "lease_id": lease_id,
                                    "intent": "set_foundation", "item_id": "foundation.language",
                                    "payload": {"value": "zh-TW"}},
                              token=token, context="POST intent foundation.language"),
        )

        # Step 6: Verify language
        state_after_language = run_step(
            "verify language as succeeded",
            lambda: expect_ok(port, "GET",
                              f"/api/onboarding/state?session_id={session_id}",
                              token=token, context="GET state after language"),
        )
        language_item = get_item(state_after_language["state"], "foundation.language")
        if language_item.get("status") != "succeeded":
            raise AssertionError(f"foundation.language not succeeded: {language_item}")
        if language_item.get("facts", {}).get("value") != "zh-TW":
            raise AssertionError(f"foundation.language value mismatch: {language_item}")

        # Step 7: Set remaining foundations
        foundation_values = [
            ("foundation.claude_auth", "authenticated"),
            ("foundation.hub", "https://github.com/example/private-hub.git"),
            ("foundation.workspace_root", str(Path(TEMP_HOME.name) / "Workspace")),
        ]
        for item_id, value in foundation_values:
            run_step(
                f"set {item_id}",
                lambda item_id=item_id, value=value: expect_ok(
                    port, "POST", "/api/onboarding/intent",
                    body={"session_id": session_id, "lease_id": lease_id,
                          "intent": "set_foundation", "item_id": item_id,
                          "payload": {"value": value}},
                    token=token, context=f"POST intent {item_id}"),
            )

        # Step 8: Verify phase transition
        state_after_foundations = run_step(
            "verify phase changed to skills_required",
            lambda: expect_ok(port, "GET",
                              f"/api/onboarding/state?session_id={session_id}",
                              token=token, context="GET state after foundations"),
        )
        if state_after_foundations["state"].get("phase") != "skills_required":
            raise AssertionError(
                f"expected skills_required, got {state_after_foundations['state'].get('phase')}")

        # Step 9: Satisfy memory-server dependency for spec
        run_step(
            "mark memory-server running",
            lambda: expect_ok(port, "POST", "/api/onboarding/intent",
                              body={"session_id": session_id, "lease_id": lease_id,
                                    "intent": "set_status", "item_id": "memory-server",
                                    "payload": {"status": "running"}},
                              token=token, context="POST intent memory-server running"),
        )
        run_step(
            "mark memory-server succeeded",
            lambda: expect_ok(port, "POST", "/api/onboarding/intent",
                              body={"session_id": session_id, "lease_id": lease_id,
                                    "intent": "set_status", "item_id": "memory-server",
                                    "payload": {"status": "succeeded"}},
                              token=token, context="POST intent memory-server succeeded"),
        )

        # Step 10: Install spec skill
        run_step(
            "install spec skill",
            lambda: expect_ok(port, "POST", "/api/skills/spec/install",
                              body={"session_id": session_id, "lease_id": lease_id, "skill_id": "spec"},
                              token=token, context="POST /api/skills/spec/install"),
        )

        # Step 11: Verify spec succeeded
        spec_state = run_step(
            "verify spec skill succeeded",
            lambda: expect_ok(port, "GET",
                              f"/api/onboarding/state?session_id={session_id}",
                              token=token, context="GET state after spec"),
        )
        spec_item = get_item(spec_state["state"], "spec")
        if spec_item.get("status") != "succeeded":
            raise AssertionError(f"spec did not succeed: {spec_item}")

        # Step 12: Renew lease
        run_step(
            "renew controller lease",
            lambda: expect_ok(port, "POST", "/api/controller/renew",
                              body={"session_id": session_id, "lease_id": lease_id},
                              token=token, context="POST /api/controller/renew"),
        )

        # Step 13: Handoff web to claude
        handoff = run_step(
            "handoff lease web to claude",
            lambda: expect_ok(port, "POST", "/api/controller/handoff",
                              body={"session_id": session_id, "from": "web", "to": "claude",
                                    "lease_id": lease_id},
                              token=token, context="POST /api/controller/handoff"),
        )
        claude_lease_id = handoff["lease_id"]

        # Step 14: Verify claude holds lease
        controller = run_step(
            "verify claude is holder",
            lambda: expect_ok(port, "GET",
                              f"/api/controller?session_id={session_id}",
                              token=token, context="GET /api/controller"),
        )
        if controller.get("holder") != "claude":
            raise AssertionError(f"expected holder claude, got {controller}")

        # Step 15: Claude releases
        run_step(
            "release lease from claude",
            lambda: expect_ok(port, "POST", "/api/controller/release",
                              body={"session_id": session_id, "holder": "claude",
                                    "lease_id": claude_lease_id},
                              token=token, context="POST /api/controller/release"),
        )

        # Step 16: Health check
        run_step(
            "call onboarding health",
            lambda: expect_ok(port, "GET", "/api/onboarding/health",
                              token=token, context="GET /api/onboarding/health"),
        )

        # Step 17: Skills catalog
        catalog = run_step(
            "call skills catalog",
            lambda: expect_ok(port, "GET", "/api/skills/catalog",
                              token=token, context="GET /api/skills/catalog"),
        )
        if not isinstance(catalog.get("skills"), list):
            raise AssertionError(f"skills catalog invalid: {catalog}")

        # Step 18: Events
        events_before = run_step(
            "call onboarding events",
            lambda: expect_ok(port, "GET",
                              f"/api/onboarding/events?session_id={session_id}",
                              token=token, context="GET events before reconcile"),
        )
        if not isinstance(events_before.get("events"), list):
            raise AssertionError(f"events invalid: {events_before}")

        # Step 19: Reconcile
        reconcile = run_step(
            "run onboarding reconcile",
            lambda: expect_ok(port, "POST", "/api/onboarding/reconcile",
                              body={"session_id": session_id},
                              token=token, context="POST /api/onboarding/reconcile"),
        )
        if "drift_count" not in reconcile:
            raise AssertionError(f"reconcile missing drift_count: {reconcile}")

        # Step 20: Verify event trail integrity
        events_after = run_step(
            "verify event trail integrity",
            lambda: expect_ok(port, "GET",
                              f"/api/onboarding/events?session_id={session_id}",
                              token=token, context="GET events after reconcile"),
        )
        events = events_after["events"]
        seqs = [e.get("seq") for e in events]
        if seqs != list(range(1, len(events) + 1)):
            raise AssertionError(f"event seq not contiguous: {seqs}")

        event_types = [e.get("type") for e in events]
        required_types = [
            "session_created", "lease_acquired", "intent_applied",
            "step_start", "step_complete", "skill_setup_complete",
            "lease_handoff", "lease_released", "reconciliation",
        ]
        for et in required_types:
            if et not in event_types:
                raise AssertionError(f"missing event type {et}: {event_types}")

        print(f"\nPASS: completed full E2E onboarding flow ({len(events)} events, {len(seqs)} steps)")
        print(f"Server: http://{HOST}:{port}")

    finally:
        httpd.shutdown()
        httpd.server_close()
        TEMP_HOME.cleanup()


if __name__ == "__main__":
    main()
