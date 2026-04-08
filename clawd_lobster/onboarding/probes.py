"""Health probes for onboarding reconciliation.

Probes are SIDE-EFFECT FREE. They detect and verify — never install,
deploy, or mutate system state.

Each probe returns: {"detected": bool, "verified": bool, "repair_hint": str}
"""
from __future__ import annotations

import importlib
import json
import platform
import subprocess
import sys
from pathlib import Path


def _run_quiet(args: list[str], timeout: int = 10) -> subprocess.CompletedProcess:
    """Run a command quietly, returning result."""
    try:
        return subprocess.run(
            args, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(args, -1, "", f"{args[0]} not found")
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, -1, "", "timeout")


def _config_dir() -> Path:
    return Path.home() / ".clawd-lobster"


def _claude_dir() -> Path:
    return Path.home() / ".claude"


# ---------------------------------------------------------------------------
# Foundation probes
# ---------------------------------------------------------------------------

def probe_claude_auth() -> dict:
    """Check if Claude Code CLI is authenticated."""
    result = _run_quiet(["claude", "--version"])
    detected = result.returncode == 0

    verified = False
    if detected:
        creds = _claude_dir() / ".credentials.json"
        if creds.exists():
            try:
                data = json.loads(creds.read_text(encoding="utf-8"))
                verified = bool(data.get("accessToken") or data.get("oauthToken"))
            except (json.JSONDecodeError, OSError):
                pass

    return {
        "detected": detected,
        "verified": verified,
        "repair_hint": "Run: claude login" if not verified else "",
    }


def probe_hub() -> dict:
    """Check if GitHub Hub repo is configured."""
    config = _config_dir() / "config.json"
    if not config.exists():
        return {"detected": False, "verified": False, "repair_hint": "Run clawd-lobster setup"}

    try:
        data = json.loads(config.read_text(encoding="utf-8"))
        hub_dir = data.get("wrapper_dir") or data.get("hub_dir", "")
        if not hub_dir:
            return {"detected": False, "verified": False, "repair_hint": "Hub not configured"}

        hub_path = Path(hub_dir)
        detected = hub_path.exists()
        verified = (hub_path / ".git").exists() if detected else False

        return {
            "detected": detected,
            "verified": verified,
            "repair_hint": "" if verified else f"Hub directory missing or not a git repo: {hub_dir}",
        }
    except (json.JSONDecodeError, OSError):
        return {"detected": False, "verified": False, "repair_hint": "Config file corrupt"}


# ---------------------------------------------------------------------------
# Skill probes
# ---------------------------------------------------------------------------

def probe_memory_server() -> dict:
    """Check if memory MCP server is installed and configured."""
    # Detect: can import the package
    detected = False
    try:
        importlib.import_module("mcp_memory")
        detected = True
    except ImportError:
        pass

    if not detected:
        return {
            "detected": False,
            "verified": False,
            "repair_hint": "Run: pip install -e skills/memory-server",
        }

    # Verify: MCP config exists
    mcp_config = _claude_dir() / ".mcp.json"
    verified = False
    if mcp_config.exists():
        try:
            data = json.loads(mcp_config.read_text(encoding="utf-8"))
            servers = data.get("mcpServers", {})
            verified = "clawd-memory" in servers
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "detected": True,
        "verified": verified,
        "repair_hint": "" if verified else "Memory server not registered in .mcp.json",
    }


def probe_spec() -> dict:
    """Check if spec skill files exist."""
    skills_dir = Path(__file__).resolve().parent.parent.parent / "skills" / "spec"
    manifest = skills_dir / "skill.json"
    skill_md = skills_dir / "SKILL.md"

    detected = manifest.exists()
    verified = detected and skill_md.exists()

    return {
        "detected": detected,
        "verified": verified,
        "repair_hint": "" if verified else "Spec skill files missing",
    }


def probe_absorb() -> dict:
    """Check if absorb skill is available. Oracle is checked separately."""
    skills_dir = Path(__file__).resolve().parent.parent.parent / "skills" / "absorb"
    detected = (skills_dir / "skill.json").exists()
    return {
        "detected": detected,
        "verified": detected,
        "repair_hint": "" if detected else "Absorb skill files missing",
    }


def probe_evolve() -> dict:
    """Check if evolve cron job is registered."""
    detected = True  # Script always exists
    script = Path(__file__).resolve().parent.parent.parent / "scripts" / "evolve-tick.py"
    if not script.exists():
        return {"detected": False, "verified": False, "repair_hint": "evolve-tick.py missing"}

    # Verify: check if scheduler entry exists
    verified = _check_scheduler("evolve")

    return {
        "detected": True,
        "verified": verified,
        "repair_hint": "" if verified else "Evolve cron job not registered",
    }


def probe_heartbeat() -> dict:
    """Check if heartbeat cron job is registered."""
    script_name = "heartbeat.ps1" if platform.system() == "Windows" else "heartbeat.sh"
    script = Path(__file__).resolve().parent.parent.parent / "scripts" / script_name
    detected = script.exists()

    verified = _check_scheduler("heartbeat") if detected else False

    return {
        "detected": detected,
        "verified": verified,
        "repair_hint": "" if verified else "Heartbeat scheduler not registered",
    }


def probe_deploy() -> dict:
    """Check if Docker is available (optional)."""
    result = _run_quiet(["docker", "--version"])
    detected = result.returncode == 0

    return {
        "detected": detected,
        "verified": detected,
        "repair_hint": "" if detected else "Docker not installed (optional for deploy skill)",
    }


# ---------------------------------------------------------------------------
# Scheduler check helpers
# ---------------------------------------------------------------------------

def _check_scheduler(job_name: str) -> bool:
    """Check if a scheduler entry exists for the given job."""
    if platform.system() == "Windows":
        result = _run_quiet([
            "schtasks", "/Query", "/TN", f"clawd-lobster-{job_name}",
        ])
        return result.returncode == 0
    else:
        # Unix: check crontab
        result = _run_quiet(["crontab", "-l"])
        if result.returncode != 0:
            return False
        return job_name in (result.stdout or "")


# ---------------------------------------------------------------------------
# Probe registry
# ---------------------------------------------------------------------------

PROBE_REGISTRY: dict[str, callable] = {
    "foundation.claude_auth": probe_claude_auth,
    "foundation.hub": probe_hub,
    "memory-server": probe_memory_server,
    "spec": probe_spec,
    "absorb": probe_absorb,
    "evolve": probe_evolve,
    "heartbeat": probe_heartbeat,
    "deploy": probe_deploy,
}


def run_probe(item_id: str) -> dict:
    """Run a probe for a specific item."""
    probe_fn = PROBE_REGISTRY.get(item_id)
    if probe_fn is None:
        return {"detected": False, "verified": False, "repair_hint": f"No probe for {item_id}"}
    try:
        return probe_fn()
    except Exception as e:
        return {"detected": False, "verified": False, "repair_hint": f"Probe error: {e}"}


def run_all_probes() -> dict[str, dict]:
    """Run all registered probes. Returns {item_id: probe_result}."""
    results = {}
    for item_id in PROBE_REGISTRY:
        results[item_id] = run_probe(item_id)
    return results


def reconcile(session_id: str) -> dict:
    """Reconcile persisted state against real machine facts.

    Returns updated state with any drift detected.
    """
    from . import state_store

    state = state_store.get_state(session_id)
    if state is None:
        return {"ok": False, "error": "Session not found"}

    probe_results = run_all_probes()
    drift_count = 0

    for item in state.get("items", []):
        item_id = item["id"]
        if item_id not in probe_results:
            continue

        probe = probe_results[item_id]

        # If state says succeeded but probe says not verified → drift
        if item.get("status") == "succeeded" and not probe.get("verified"):
            item["status"] = "failed"
            item["error"] = f"Reconciliation: {probe.get('repair_hint', 'verification failed')}"
            drift_count += 1

        # Update facts from probe
        item.setdefault("facts", {})
        item["facts"]["_probe_detected"] = probe.get("detected", False)
        item["facts"]["_probe_verified"] = probe.get("verified", False)
        if probe.get("repair_hint"):
            item["facts"]["_repair_hint"] = probe["repair_hint"]

    if drift_count > 0:
        state["phase"] = state_store.compute_phase(state)
        state_store.save_state(session_id, state)
        state_store.log_event(session_id, {
            "type": "reconciliation",
            "actor": "backend",
            "controller": None,
            "item_id": None,
            "ok": True,
            "message": f"Reconciliation found {drift_count} drift(s)",
        })

    return {"ok": True, "drift_count": drift_count, "probes": probe_results}
