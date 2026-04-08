"""Skill setup executor — runs install, configure, and verify steps.

Each skill.json onboarding section defines steps with kinds:
  command  — run a shell command
  config   — write config fields
  probe    — run health probe
  link     — open a URL (user action)

The executor runs steps sequentially, updates facts after each,
and marks the skill succeeded or failed.
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import state_store, manifest, probes

_IS_WINDOWS = platform.system() == "Windows"


def execute_skill_setup(
    session_id: str,
    skill_id: str,
    lease_id: str,
    config_values: dict[str, Any] | None = None,
) -> dict:
    """Execute all setup steps for a skill.

    Args:
        session_id: onboarding session
        skill_id: skill to set up
        lease_id: must hold valid lease
        config_values: user-provided config for 'config' steps

    Returns:
        {"ok": True/False, "steps_run": N, "steps_passed": N, "error": ...}
    """
    from . import lease as lease_mod

    if not lease_mod.validate_lease(session_id, lease_id):
        return {"ok": False, "error": "Invalid or expired lease"}

    state = state_store.get_state(session_id)
    if state is None:
        return {"ok": False, "error": "Session not found"}

    item = state_store.find_item(state, skill_id)
    if item is None:
        return {"ok": False, "error": f"Skill not found: {skill_id}"}

    # Validate dependencies before execution
    for dep_id in item.get("depends_on", []):
        dep = state_store.find_item(state, dep_id)
        if dep is None:
            return {"ok": False, "error": f"Unknown dependency: {dep_id}"}
        if dep.get("status") not in ("succeeded", "skipped"):
            return {"ok": False, "error": f"Dependency not met: {dep_id}"}

    # Validate current status allows execution
    if item.get("status") not in ("pending", "failed"):
        return {"ok": False, "error": f"Cannot execute: item is {item.get('status')}"}

    # Load manifest for step definitions
    manifests = manifest.load_skill_manifests()
    skill_manifest = None
    for m in manifests:
        if m.get("id") == skill_id:
            skill_manifest = m
            break

    if skill_manifest is None:
        # No manifest with onboarding — just run probe
        return _probe_only(session_id, state, item, skill_id)

    ob = skill_manifest.get("onboarding", {})
    steps = ob.get("steps", [])
    if not steps:
        return _probe_only(session_id, state, item, skill_id)

    # Mark running
    item["status"] = "running"
    item["started_at"] = state_store._now_iso()
    item["last_actor"] = "backend"
    state_store.save_state(session_id, state)

    steps_run = 0
    steps_passed = 0
    last_error = None

    for step in steps:
        step_id = step.get("id", "unknown")
        kind = step.get("kind", "command")
        required = step.get("required", True)

        state_store.log_event(session_id, {
            "type": "step_start",
            "actor": "backend",
            "controller": "backend",
            "item_id": skill_id,
            "ok": True,
            "message": f"Running step: {step.get('label', step_id)}",
        })

        steps_run += 1
        success = False

        if kind == "command":
            success, error = _run_command_step(step)
            if not success:
                last_error = error

        elif kind == "config":
            success, error = _run_config_step(step, config_values or {})
            if not success:
                last_error = error

        elif kind == "probe":
            probe_id = step.get("probe", skill_id)
            result = probes.run_probe(probe_id)
            success = result.get("verified", False)
            if not success:
                last_error = result.get("repair_hint", "Probe failed")

        elif kind == "link":
            # Link steps are user actions — auto-pass
            success = True

        # Update facts
        if success:
            steps_passed += 1
            for fact_key in step.get("success_sets", []):
                item.setdefault("facts", {})[fact_key] = True

        state_store.log_event(session_id, {
            "type": "step_complete",
            "actor": "backend",
            "controller": "backend",
            "item_id": skill_id,
            "ok": success,
            "message": f"Step {step_id}: {'passed' if success else 'failed'}",
        })

        # Stop on required step failure
        if not success and required:
            item["status"] = "failed"
            item["error"] = last_error
            item["completed_at"] = state_store._now_iso()
            item["retry_count"] = item.get("retry_count", 0) + 1
            state_store.save_state(session_id, state)
            return {
                "ok": False,
                "steps_run": steps_run,
                "steps_passed": steps_passed,
                "error": last_error,
                "failed_step": step_id,
            }

    # All steps passed (or optional ones failed)
    item["status"] = "succeeded"
    item["error"] = None
    item["completed_at"] = state_store._now_iso()
    state["phase"] = state_store.compute_phase(state)
    state_store.save_state(session_id, state)

    state_store.log_event(session_id, {
        "type": "skill_setup_complete",
        "actor": "backend",
        "controller": "backend",
        "item_id": skill_id,
        "ok": True,
        "message": f"{skill_id}: {steps_passed}/{steps_run} steps passed",
    })

    return {"ok": True, "steps_run": steps_run, "steps_passed": steps_passed}


def _probe_only(session_id: str, state: dict, item: dict, skill_id: str) -> dict:
    """Fallback: just run probe for skills without setup steps."""
    item["status"] = "running"
    state_store.save_state(session_id, state)

    result = probes.run_probe(skill_id)
    if result.get("verified"):
        item["status"] = "succeeded"
        item["error"] = None
    else:
        item["status"] = "failed"
        item["error"] = result.get("repair_hint", "Verification failed")
        item["retry_count"] = item.get("retry_count", 0) + 1

    item["completed_at"] = state_store._now_iso()
    item.setdefault("facts", {}).update({
        "_probe_detected": result.get("detected", False),
        "_probe_verified": result.get("verified", False),
    })
    state["phase"] = state_store.compute_phase(state)
    state_store.save_state(session_id, state)

    return {
        "ok": result.get("verified", False),
        "steps_run": 1,
        "steps_passed": 1 if result.get("verified") else 0,
        "error": None if result.get("verified") else result.get("repair_hint"),
    }


# ---------------------------------------------------------------------------
# Step runners
# ---------------------------------------------------------------------------

def _run_command_step(step: dict) -> tuple[bool, str | None]:
    """Run a command step. Returns (success, error_message)."""
    cmd_spec = step.get("command", {})

    # Resolve platform-specific command
    if isinstance(cmd_spec, str):
        cmd = cmd_spec
    elif isinstance(cmd_spec, dict):
        if _IS_WINDOWS:
            cmd = cmd_spec.get("windows") or cmd_spec.get("all", "")
        else:
            cmd = cmd_spec.get("unix") or cmd_spec.get("macos") or cmd_spec.get("linux") or cmd_spec.get("all", "")
    else:
        return False, "Invalid command spec"

    if not cmd:
        return False, "No command for this platform"

    # Resolve {{WRAPPER_DIR}} placeholder
    wrapper_dir = str(Path(__file__).resolve().parent.parent.parent)
    cmd = cmd.replace("{{WRAPPER_DIR}}", wrapper_dir)

    # Security: use shlex.split instead of shell=True to prevent injection.
    # Commands come from skill.json manifests (we control), but defense-in-depth.
    import shlex
    try:
        if _IS_WINDOWS:
            # shlex.split doesn't handle Windows quoting well; use cmd list manually
            cmd_list = cmd.split()
        else:
            cmd_list = shlex.split(cmd)
    except ValueError as e:
        return False, f"Command parse error: {e}"

    try:
        result = subprocess.run(
            cmd_list, capture_output=True, text=True,
            timeout=120, encoding="utf-8", errors="replace",
            cwd=wrapper_dir,
        )
        if result.returncode == 0:
            return True, None
        else:
            error = (result.stderr or result.stdout or "").strip()[:200]
            return False, f"Command failed (exit {result.returncode}): {error}"
    except subprocess.TimeoutExpired:
        return False, "Command timed out (120s)"
    except Exception as e:
        return False, str(e)


def _run_config_step(step: dict, values: dict) -> tuple[bool, str | None]:
    """Run a config step — validate and save fields."""
    fields = step.get("fields", [])
    for field in fields:
        name = field.get("name", "")
        required = field.get("required", False)
        if required and name not in values:
            return False, f"Missing required config: {name}"

    # Config steps are considered successful if all required fields provided
    # Actual config writing happens via the credential/config system
    return True, None


# ---------------------------------------------------------------------------
# Scheduler registration
# ---------------------------------------------------------------------------

def register_scheduler(
    skill_id: str,
    schedule: str,
    command: str,
    task_name: str | None = None,
) -> dict:
    """Register an OS-level scheduled task.

    Args:
        skill_id: which skill this job belongs to
        schedule: cron expression (e.g., "*/30 * * * *")
        command: command to run
        task_name: override task name (default: clawd-lobster-{skill_id})

    Returns:
        {"ok": True/False, "method": "cron|schtasks|launchd", "error": ...}
    """
    if task_name is None:
        task_name = f"clawd-lobster-{skill_id}"

    # Sanitize task_name to prevent injection (alphanumeric + hyphen only)
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', task_name):
        return {"ok": False, "error": f"Invalid task name: {task_name}", "method": "unknown"}

    wrapper_dir = str(Path(__file__).resolve().parent.parent.parent)
    full_command = command.replace("{{WRAPPER_DIR}}", wrapper_dir)

    if _IS_WINDOWS:
        return _register_windows(task_name, schedule, full_command, wrapper_dir)
    elif platform.system() == "Darwin":
        return _register_cron(task_name, schedule, full_command, wrapper_dir)
    else:
        return _register_cron(task_name, schedule, full_command, wrapper_dir)


def _register_windows(task_name: str, schedule: str, command: str, cwd: str) -> dict:
    """Register Windows Task Scheduler entry."""
    # Parse cron to schtasks params
    parts = schedule.split()
    if len(parts) != 5:
        return {"ok": False, "error": f"Invalid cron expression: {schedule}", "method": "schtasks"}

    minute, hour, dom, month, dow = parts

    # Simple patterns
    if minute.startswith("*/"):
        interval = minute[2:]
        sc_args = f"/SC MINUTE /MO {interval}"
    elif hour.startswith("*/"):
        interval = hour[2:]
        sc_args = f"/SC HOURLY /MO {interval}"
    elif minute == "0" and hour.startswith("*/"):
        interval = hour[2:]
        sc_args = f"/SC HOURLY /MO {interval}"
    else:
        # Default: daily at specific time
        h = hour if hour != "*" else "0"
        m = minute if minute != "*" else "0"
        sc_args = f"/SC DAILY /ST {h.zfill(2)}:{m.zfill(2)}"

    cmd = f'schtasks /Create /TN "{task_name}" /TR "{command}" {sc_args} /F'

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=30, encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            return {"ok": True, "method": "schtasks", "task_name": task_name}
        return {"ok": False, "method": "schtasks", "error": result.stderr.strip()[:200]}
    except Exception as e:
        return {"ok": False, "method": "schtasks", "error": str(e)}


def _register_cron(task_name: str, schedule: str, command: str, cwd: str) -> dict:
    """Register Unix cron entry."""
    marker = f"# {task_name}"
    cron_line = f"{schedule} cd {cwd} && {command} {marker}"

    try:
        # Read existing crontab
        result = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True,
            timeout=10, encoding="utf-8", errors="replace",
        )
        existing = result.stdout or ""

        # Check if already registered
        if task_name in existing:
            # Update existing entry
            lines = [l for l in existing.splitlines() if task_name not in l]
            lines.append(cron_line)
        else:
            lines = existing.splitlines()
            lines.append(cron_line)

        new_crontab = "\n".join(lines) + "\n"

        # Write new crontab
        proc = subprocess.Popen(
            ["crontab", "-"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8",
        )
        stdout, stderr = proc.communicate(input=new_crontab, timeout=10)

        if proc.returncode == 0:
            return {"ok": True, "method": "cron", "task_name": task_name}
        return {"ok": False, "method": "cron", "error": stderr.strip()[:200]}
    except Exception as e:
        return {"ok": False, "method": "cron", "error": str(e)}


def check_scheduler(skill_id: str) -> dict:
    """Check if a scheduler entry exists for a skill."""
    task_name = f"clawd-lobster-{skill_id}"

    if _IS_WINDOWS:
        result = subprocess.run(
            f'schtasks /Query /TN "{task_name}"',
            shell=True, capture_output=True, text=True,
            timeout=10, encoding="utf-8", errors="replace",
        )
        return {
            "registered": result.returncode == 0,
            "method": "schtasks",
            "task_name": task_name,
        }
    else:
        try:
            result = subprocess.run(
                ["crontab", "-l"], capture_output=True, text=True,
                timeout=10, encoding="utf-8", errors="replace",
            )
            registered = task_name in (result.stdout or "")
            return {"registered": registered, "method": "cron", "task_name": task_name}
        except Exception:
            return {"registered": False, "method": "cron", "task_name": task_name}


def register_skill_jobs(skill_id: str) -> list[dict]:
    """Register all scheduled jobs for a skill based on its manifest.

    Returns list of registration results.
    """
    manifests = manifest.load_skill_manifests()
    skill_manifest = None
    for m in manifests:
        if m.get("id") == skill_id:
            skill_manifest = m
            break

    if skill_manifest is None:
        return []

    runtime = skill_manifest.get("runtime", {})
    schedule_expr = runtime.get("schedule")
    entrypoint = runtime.get("entrypoint")

    if not schedule_expr or not entrypoint:
        return []

    # Build command
    wrapper_dir = str(Path(__file__).resolve().parent.parent.parent)
    if entrypoint.endswith(".py"):
        command = f"{sys.executable} {wrapper_dir}/{entrypoint}"
    elif entrypoint.endswith(".sh"):
        command = f"bash {wrapper_dir}/{entrypoint}"
    elif entrypoint.endswith(".ps1"):
        command = f"powershell {wrapper_dir}/{entrypoint}"
    else:
        command = f"{wrapper_dir}/{entrypoint}"

    result = register_scheduler(skill_id, schedule_expr, command)
    return [result]
