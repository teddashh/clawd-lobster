#!/usr/bin/env python3
"""Full onboarding demo — runs the complete flow via HTTP API."""
import json
import sys
from http.client import HTTPConnection

sys.stdout.reconfigure(encoding="utf-8")

HOST = "127.0.0.1"
PORT = 3333


def api(method, path, body=None, token=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    conn = HTTPConnection(HOST, PORT, timeout=10)
    payload = json.dumps(body).encode() if body else None
    conn.request(method, path, body=payload, headers=h)
    r = conn.getresponse()
    data = json.loads(r.read().decode())
    conn.close()
    return data


def main():
    print("=" * 60)
    print("  CLAWD-LOBSTER ONBOARDING — FULL E2E FLOW")
    print("=" * 60)

    # Step 1
    print("\n--- Step 1: Create Session ---")
    r = api("POST", "/api/onboarding/session", {"lang": "zh-TW"})
    token = r["token"]
    sid = r["session_id"]
    print(f"  Session: {sid}")
    print(f"  Token: {token[:8]}...")
    print(f"  Items: {len(r['state']['items'])}")
    print(f"  Phase: {r['state']['phase']}")

    # Step 2
    print("\n--- Step 2: Take Control (Web) ---")
    r = api("POST", "/api/controller/acquire", {"session_id": sid, "holder": "web"}, token)
    lid = r["lease_id"]
    print(f"  Lease: {lid}")

    # Step 3-6: Foundations
    foundations = [
        ("foundation.language", "zh-TW", "Language"),
        ("foundation.claude_auth", "authenticated", "Claude Auth"),
        ("foundation.hub", "https://github.com/user/my-hub.git", "GitHub Hub"),
        ("foundation.workspace_root", "~/Documents/Workspace", "Workspace Root"),
    ]
    for i, (item_id, value, label) in enumerate(foundations, 3):
        print(f"\n--- Step {i}: {label} ---")
        r = api("POST", "/api/onboarding/intent", {
            "session_id": sid, "lease_id": lid,
            "intent": "set_foundation", "item_id": item_id,
            "payload": {"value": value},
        }, token)
        ok = "OK" if r.get("ok") else f"FAIL: {r.get('error', '')}"
        print(f"  {item_id}: {value}")
        print(f"  Result: {ok}")

    # Check phase
    r = api("GET", f"/api/onboarding/state?session_id={sid}", token=token)
    phase = r["state"]["phase"]
    print(f"\n  Phase after foundations: {phase}")

    # Step 7: Install skills
    print("\n--- Step 7: Install Required Skills ---")
    skills = ["memory-server", "spec", "absorb", "evolve", "heartbeat", "deploy"]
    for skill_id in skills:
        # Mark running then succeeded via intent API
        # (In real onboarding, /install runs actual commands — here we simulate)
        r1 = api("POST", "/api/onboarding/intent", {
            "session_id": sid, "lease_id": lid,
            "intent": "set_status", "item_id": skill_id,
            "payload": {"status": "running"},
        }, token)
        if not r1.get("ok"):
            print(f"  {skill_id:20s} -> running FAIL: {r1.get('error', '')[:40]}")
            continue
        r2 = api("POST", "/api/onboarding/intent", {
            "session_id": sid, "lease_id": lid,
            "intent": "set_status", "item_id": skill_id,
            "payload": {"status": "succeeded"},
        }, token)
        ok = "OK" if r2.get("ok") else r2.get("error", "fail")[:40]
        print(f"  {skill_id:20s} {ok}")

    # Step 8: Cron jobs
    print("\n--- Step 8: Register Cron Jobs ---")
    for job in ["evolve", "heartbeat"]:
        r = api("POST", "/api/jobs/register", {"skill_id": job}, token)
        results = r.get("results", [])
        if results:
            print(f"  {job:20s} method={results[0].get('method')} ok={results[0].get('ok')}")
        else:
            print(f"  {job:20s} no scheduled jobs")

    # Step 9: Health
    print("\n--- Step 9: Health Check ---")
    r = api("GET", "/api/onboarding/health", token=token)
    for pid, result in r.get("probes", {}).items():
        d = "Y" if result.get("detected") else "N"
        v = "Y" if result.get("verified") else "N"
        print(f"  {pid:25s} detected={d} verified={v}")

    # Step 10: Handoff
    print("\n--- Step 10: Handoff Web -> Claude ---")
    r = api("POST", "/api/controller/handoff", {
        "session_id": sid, "from": "web", "to": "claude", "lease_id": lid,
    }, token)
    claude_lid = r.get("lease_id", "")
    print(f"  Holder: claude")
    print(f"  Lease: {claude_lid}")

    # Step 11: State check
    print("\n--- Step 11: Claude Reads State ---")
    r = api("GET", f"/api/onboarding/state?session_id={sid}", token=token)
    state = r["state"]
    done = sum(1 for i in state["items"] if i["status"] in ("succeeded", "skipped"))
    total = len(state["items"])
    print(f"  Phase: {state['phase']}")
    print(f"  Progress: {done}/{total}")

    # Step 12: Release
    print("\n--- Step 12: Claude Releases ---")
    r = api("POST", "/api/controller/release", {
        "session_id": sid, "holder": "claude", "lease_id": claude_lid,
    }, token)
    print(f"  Released: {'OK' if r.get('ok') else 'FAIL'}")

    # Step 13: Handoff file
    print("\n--- Step 13: Generate CLAUDE.md ---")
    r = api("POST", "/api/onboarding/handoff-gen", {
        "session_id": sid, "port": PORT, "token": token,
    }, token)
    path = r.get("claude_md_path", "N/A")
    print(f"  Path: {path}")

    # Step 14: Reconcile
    print("\n--- Step 14: Reconcile ---")
    r = api("POST", "/api/onboarding/reconcile", {"session_id": sid}, token)
    print(f"  Drift: {r.get('drift_count', 0)}")

    # Step 15: Events
    print("\n--- Step 15: Audit Trail ---")
    r = api("GET", f"/api/onboarding/events?session_id={sid}", token=token)
    events = r.get("events", [])
    types = {}
    for e in events:
        t = e.get("type", "unknown")
        types[t] = types.get(t, 0) + 1
    print(f"  Events: {len(events)}")
    for t in sorted(types):
        print(f"    {t}: {types[t]}")

    # Summary
    print("\n" + "=" * 60)
    print("  ONBOARDING COMPLETE")
    print(f"  Session: {sid}")
    print(f"  Progress: {done}/{total} items")
    print(f"  Events: {len(events)}")
    print(f"  Phase: {state['phase']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
