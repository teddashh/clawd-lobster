"""Skill setup executor: runs install, configure, and verify steps.

Each skill.json onboarding section defines steps with kinds:
  command:  run a command (split into arguments, never through a shell)
  config:   write config fields
  probe:    run health probe
  link:     open a URL (user action)
  schedule: register the skill's "runtime" job with cron or Task Scheduler

The executor runs steps sequentially, updates facts after each,
and marks the skill succeeded or failed.
"""
from __future__ import annotations

import json
import os
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path
from shutil import which
from typing import Any

IS_WINDOWS = platform.system() == "Windows"


def _resolve_bash() -> str:
    """Find Git Bash on Windows, avoiding WSL bash."""
    if IS_WINDOWS:
        candidates = [
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git" / "bin" / "bash.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Git" / "bin" / "bash.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Git" / "bin" / "bash.exe",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
        found = which("bash")
        if found and "WindowsApps" not in found and "WSL" not in found.upper():
            return found
    return "bash"

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
        # No manifest with onboarding; just run probe
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
            # Link steps are user actions; auto-pass
            success = True

        elif kind == "schedule":
            success, error = _run_schedule_step(skill_id)
            if not success:
                last_error = error

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

# Tokens that only mean something to a shell. Command steps run without one,
# so a step using them would silently do something else (for example
# "echo ... | crontab -" just echoes and exits 0). Refuse them instead.
_SHELL_OPERATORS = {"|", "||", "&", "&&", ";", ">", ">>", "<", "2>", "2>>", "2>&1"}


def _split_command(cmd: str) -> list[str]:
    """Split a manifest command into an argument list, without a shell.

    Unix uses POSIX quoting rules. Windows keeps backslashes (posix=False)
    and then drops the surrounding double quotes, so "a b" stays a single
    argument; subprocess quotes it again when it builds the command line.
    """
    if not _IS_WINDOWS:
        return shlex.split(cmd)
    args = []
    for tok in shlex.split(cmd, posix=False):
        if len(tok) >= 2 and tok[0] == tok[-1] == '"':
            tok = tok[1:-1]
        args.append(tok)
    return args


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

    wrapper_dir = str(Path(__file__).resolve().parent.parent.parent)

    # Security: no shell=True. The command is split into arguments first and
    # the {{WRAPPER_DIR}} placeholder is filled in per argument afterwards,
    # so a path with spaces stays one argument.
    try:
        cmd_list = [arg.replace("{{WRAPPER_DIR}}", wrapper_dir)
                    for arg in _split_command(cmd)]
    except ValueError as e:
        return False, f"Command parse error: {e}"
    if not cmd_list:
        return False, "No command for this platform"
    if any(arg in _SHELL_OPERATORS for arg in cmd_list):
        return False, ("Command steps run without a shell, so pipes, redirects and "
                       "'&&' are not supported. Use a 'schedule' step for cron jobs.")

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


def _run_schedule_step(skill_id: str) -> tuple[bool, str | None]:
    """Register the skill's runtime job. Returns (success, error_message)."""
    results = register_skill_jobs(skill_id)
    if not results:
        return False, f"No runtime schedule in the {skill_id} manifest"
    for result in results:
        if not result.get("ok"):
            return False, result.get("error") or "Scheduler registration failed"
    return True, None


def _run_config_step(step: dict, values: dict) -> tuple[bool, str | None]:
    """Run a config step: validate and save fields."""
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
    command: list[str] | str,
    task_name: str | None = None,
) -> dict:
    """Register an OS-level scheduled task.

    Args:
        skill_id: which skill this job belongs to
        schedule: cron expression (e.g., "*/30 * * * *")
        command: argument list to run (preferred; quoted for cron or for
            schtasks as needed), or a ready-made command string
        task_name: override task name (default: clawd-lobster-{skill_id})

    Returns:
        {"ok": True/False, "method": "cron|schtasks", "error": ...}
    """
    if task_name is None:
        task_name = f"clawd-lobster-{skill_id}"

    # Sanitize task_name to prevent injection (alphanumeric + hyphen only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', task_name):
        return {"ok": False, "error": f"Invalid task name: {task_name}", "method": "unknown"}

    wrapper_dir = str(Path(__file__).resolve().parent.parent.parent)
    if isinstance(command, str):
        command = command.replace("{{WRAPPER_DIR}}", wrapper_dir)
    else:
        command = [arg.replace("{{WRAPPER_DIR}}", wrapper_dir) for arg in command]

    if _IS_WINDOWS:
        return _register_windows(task_name, schedule, command, wrapper_dir)
    # Linux and macOS both use cron
    return _register_cron(task_name, schedule, command, wrapper_dir)


def _schtasks_schedule_args(schedule: str) -> list[str] | None:
    """Translate a simple cron expression into schtasks /SC arguments."""
    parts = schedule.split()
    if len(parts) != 5:
        return None
    minute, hour, _dom, _month, _dow = parts

    if minute.startswith("*/") and minute[2:].isdigit():
        return ["/SC", "MINUTE", "/MO", minute[2:]]
    if hour.startswith("*/") and hour[2:].isdigit():
        return ["/SC", "HOURLY", "/MO", hour[2:]]
    h = hour if hour != "*" else "0"
    m = minute if minute != "*" else "0"
    if not (h.isdigit() and m.isdigit()):
        return None
    # Otherwise: daily at a specific time
    return ["/SC", "DAILY", "/ST", f"{h.zfill(2)}:{m.zfill(2)}"]


def _register_windows(task_name: str, schedule: str, command: list[str] | str,
                      cwd: str) -> dict:
    """Register a Windows Task Scheduler entry.

    The schtasks argument list is built explicitly (no shell, no splitting).
    The /TR value is one argument: the task command line, with each part
    quoted by subprocess.list2cmdline, so paths with spaces survive.
    """
    sc_args = _schtasks_schedule_args(schedule)
    if sc_args is None:
        return {"ok": False, "method": "schtasks",
                "error": f"Unsupported cron expression for schtasks: {schedule}"}

    task_command = command if isinstance(command, str) else subprocess.list2cmdline(command)
    args = ["schtasks", "/Create", "/TN", task_name, "/TR", task_command, *sc_args, "/F"]
    try:
        result = subprocess.run(
            args, capture_output=True, text=True,
            timeout=30, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "method": "schtasks", "error": f"schtasks failed: {e}"}
    if result.returncode == 0:
        return {"ok": True, "method": "schtasks", "task_name": task_name}
    error = (result.stderr or result.stdout or "").strip()[:200]
    return {"ok": False, "method": "schtasks",
            "error": f"schtasks failed (exit {result.returncode}): {error}"}


def _read_crontab() -> tuple[bool, str, str]:
    """Read the user's crontab. Returns (ok, text, error).

    "no crontab for <user>" is not an error: it means an empty crontab.
    """
    try:
        result = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True,
            timeout=10, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, "", f"crontab -l failed: {e}"
    if result.returncode == 0:
        return True, result.stdout or "", ""
    stderr = (result.stderr or "").strip()
    if "no crontab" in stderr.lower():
        return True, "", ""
    return False, "", f"crontab -l failed (exit {result.returncode}): {stderr[:200]}"


def _register_cron(task_name: str, schedule: str, command: list[str] | str,
                   cwd: str) -> dict:
    """Add a cron entry without disturbing the rest of the user's crontab.

    Reads `crontab -l` (no crontab counts as empty), leaves it alone when the
    exact line is already there, replaces our own line for this task (the
    one ending in "# <task_name>") if its command or schedule changed, and
    otherwise appends. The result is written back through stdin of
    `crontab -` (no shell), every return code is checked, and the line is
    read back before success is reported.
    """
    marker = f"# {task_name}"
    command_text = command if isinstance(command, str) else shlex.join(command)
    # cron runs the line with /bin/sh, so arguments are shell-quoted; a bare
    # "%" would end the command in a crontab, so it is escaped
    job = f"cd {shlex.quote(cwd)} && {command_text}".replace("%", "\\%")
    cron_line = f"{schedule} {job} {marker}"

    ok, existing, error = _read_crontab()
    if not ok:
        return {"ok": False, "method": "cron", "error": error}

    lines = existing.splitlines()
    if cron_line in lines:
        return {"ok": True, "method": "cron", "task_name": task_name, "changed": False}

    ours = [i for i, line in enumerate(lines) if line.rstrip().endswith(marker)]
    if ours:
        new_lines = []
        for i, line in enumerate(lines):
            if i == ours[0]:
                new_lines.append(cron_line)
            elif i not in ours:
                new_lines.append(line)
    else:
        new_lines = lines + [cron_line]
    new_crontab = "\n".join(new_lines) + "\n"

    try:
        result = subprocess.run(
            ["crontab", "-"], input=new_crontab, capture_output=True, text=True,
            timeout=10, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "method": "cron", "error": f"crontab - failed: {e}"}
    if result.returncode != 0:
        error = (result.stderr or result.stdout or "").strip()[:200]
        return {"ok": False, "method": "cron",
                "error": f"crontab - failed (exit {result.returncode}): {error}"}

    ok, written, error = _read_crontab()
    if not ok:
        return {"ok": False, "method": "cron", "error": error}
    if cron_line not in written.splitlines():
        return {"ok": False, "method": "cron",
                "error": "crontab was written but the new line is not in it"}
    return {"ok": True, "method": "cron", "task_name": task_name, "changed": True}


def check_scheduler(skill_id: str) -> dict:
    """Check if a scheduler entry exists for a skill."""
    task_name = f"clawd-lobster-{skill_id}"

    if _IS_WINDOWS:
        try:
            result = subprocess.run(
                ["schtasks", "/Query", "/TN", task_name],
                capture_output=True, text=True,
                timeout=10, encoding="utf-8", errors="replace",
            )
            registered = result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            registered = False
        return {"registered": registered, "method": "schtasks", "task_name": task_name}

    ok, text, _error = _read_crontab()
    registered = ok and any(line.rstrip().endswith(f"# {task_name}")
                            for line in text.splitlines())
    return {"registered": registered, "method": "cron", "task_name": task_name}


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

    command = _job_command(Path(__file__).resolve().parent.parent.parent, entrypoint)
    if command is None:
        return [{"ok": False, "method": "schtasks" if _IS_WINDOWS else "cron",
                 "error": f"Entrypoint not found: {entrypoint}"}]

    result = register_scheduler(skill_id, schedule_expr, command)
    return [result]


def _job_command(wrapper_dir: Path, entrypoint: str) -> list[str] | None:
    """Argument list that runs a skill's runtime entrypoint, or None if missing."""
    script = wrapper_dir / entrypoint
    if not script.exists():
        return None
    powershell = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"]
    if entrypoint.endswith(".py"):
        return [sys.executable, str(script)]
    if entrypoint.endswith(".sh"):
        # On Windows prefer the PowerShell twin of a shell script (heartbeat.ps1)
        twin = script.with_suffix(".ps1")
        if _IS_WINDOWS and twin.exists():
            return powershell + [str(twin)]
        return [_resolve_bash(), str(script)]
    if entrypoint.endswith(".ps1"):
        return powershell + [str(script)]
    return [str(script)]
