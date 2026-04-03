#!/usr/bin/env python3
"""
skill-manager.py — CLI tool for managing clawd-lobster skills.

Commands:
  list                     Table of all skills: id, name, category, enabled, status
  status [skill-id]        Detailed status for one or all skills
  enable <skill-id>        Enable a skill (updates .mcp.json + settings.json)
  disable <skill-id>       Disable a skill (updates .mcp.json + settings.json)
  config <skill-id>        Show/edit skill config
  credentials <skill-id>   Manage credentials for a skill
  health                   Run health checks on all enabled skills
  reconcile                Re-derive .mcp.json + settings.json from registry

No external dependencies — stdlib only, cross-platform (Windows + Unix).
"""

import argparse
import copy
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

HOME = Path.home()
CLAWD_DIR = HOME / ".clawd-lobster"
SKILLS_REGISTRY_DIR = CLAWD_DIR / "skills"
REGISTRY_FILE = SKILLS_REGISTRY_DIR / "registry.json"
CREDENTIALS_DIR = CLAWD_DIR / "credentials"
CLAUDE_DIR = HOME / ".claude"
MCP_FILE = CLAUDE_DIR / ".mcp.json"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"

# Where the clawd-lobster repo lives — derive from this script's location
REPO_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_DIR / "skills"

IS_WINDOWS = platform.system() == "Windows"

# ── ANSI Colors (graceful fallback) ──────────────────────────────────────────

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, text: str) -> str:
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t: str) -> str:
    return _c("32", t)


def red(t: str) -> str:
    return _c("31", t)


def yellow(t: str) -> str:
    return _c("33", t)


def cyan(t: str) -> str:
    return _c("36", t)


def bold(t: str) -> str:
    return _c("1", t)


def dim(t: str) -> str:
    return _c("2", t)


# ── Utility ──────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_read_json(path: Path, default=None):
    """Read a JSON file, returning *default* on any error."""
    if default is None:
        default = {}
    if not path.exists():
        return copy.deepcopy(default)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(yellow(f"  Warning: could not parse {path}: {exc}"))
        return copy.deepcopy(default)


def safe_write_json(path: Path, data: dict, restricted: bool = False) -> None:
    """Write JSON atomically (write tmp then rename). Optionally chmod 600."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        # Atomic-ish rename
        if IS_WINDOWS:
            # Windows can't rename over existing; remove first
            if path.exists():
                path.unlink()
        tmp.rename(path)
    except OSError as exc:
        # Clean up tmp on failure
        if tmp.exists():
            tmp.unlink()
        raise SystemExit(red(f"Error writing {path}: {exc}"))

    if restricted and not IS_WINDOWS:
        try:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Pretty-print a table with column alignment."""
    if not rows:
        print(dim("  (no entries)"))
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            # Strip ANSI for width calc
            clean = cell
            for code in ("\033[32m", "\033[31m", "\033[33m", "\033[36m",
                         "\033[1m", "\033[2m", "\033[0m"):
                clean = clean.replace(code, "")
            widths[i] = max(widths[i], len(clean))

    hdr = "  ".join(bold(h.ljust(widths[i])) for i, h in enumerate(headers))
    sep = "  ".join("-" * w for w in widths)
    print(hdr)
    print(dim(sep))
    for row in rows:
        parts = []
        for i, cell in enumerate(row):
            clean = cell
            for code in ("\033[32m", "\033[31m", "\033[33m", "\033[36m",
                         "\033[1m", "\033[2m", "\033[0m"):
                clean = clean.replace(code, "")
            padding = widths[i] - len(clean)
            parts.append(cell + " " * padding)
        print("  ".join(parts))


def state_color(state: str) -> str:
    m = {"running": green, "stopped": dim, "error": red, "degraded": yellow,
         "unknown": dim}
    fn = m.get(state, dim)
    return fn(state)


def enabled_color(enabled: bool) -> str:
    return green("yes") if enabled else dim("no")


# ── Registry ─────────────────────────────────────────────────────────────────

_EMPTY_REGISTRY = {
    "version": 1,
    "updatedAt": "",
    "skills": {},
}

_EMPTY_SKILL_ENTRY = {
    "source": "repo",
    "manifestPath": "",
    "installedVersion": "",
    "enabled": False,
    "locked": False,
    "status": {
        "state": "stopped",
        "lastHealthCheck": None,
        "lastError": None,
    },
    "config": {},
    "credentialRefs": [],
}


def load_registry() -> dict:
    reg = safe_read_json(REGISTRY_FILE, _EMPTY_REGISTRY)
    # Ensure shape
    reg.setdefault("version", 1)
    reg.setdefault("updatedAt", "")
    reg.setdefault("skills", {})
    return reg


def save_registry(reg: dict) -> None:
    reg["updatedAt"] = now_iso()
    safe_write_json(REGISTRY_FILE, reg)


# ── Skill manifest discovery ─────────────────────────────────────────────────

def discover_manifests() -> dict[str, dict]:
    """Scan skills/*/skill.json and return {skill_id: manifest_dict}."""
    found: dict[str, dict] = {}
    if not SKILLS_DIR.is_dir():
        return found
    for child in sorted(SKILLS_DIR.iterdir()):
        if not child.is_dir():
            continue
        manifest_path = child / "skill.json"
        if not manifest_path.exists():
            continue
        manifest = safe_read_json(manifest_path)
        skill_id = manifest.get("id", child.name)
        manifest["_dir"] = str(child)
        manifest["_manifest_path"] = str(manifest_path.relative_to(REPO_DIR))
        found[skill_id] = manifest
    return found


def sync_registry_with_manifests(reg: dict) -> bool:
    """Ensure registry entries exist for every discovered manifest.
    Returns True if anything changed."""
    manifests = discover_manifests()
    changed = False
    for sid, manifest in manifests.items():
        if sid not in reg["skills"]:
            entry = copy.deepcopy(_EMPTY_SKILL_ENTRY)
            entry["manifestPath"] = manifest["_manifest_path"]
            entry["installedVersion"] = manifest.get("version", "")
            reg["skills"][sid] = entry
            changed = True
        else:
            # Update manifest path / version if changed
            e = reg["skills"][sid]
            if e["manifestPath"] != manifest["_manifest_path"]:
                e["manifestPath"] = manifest["_manifest_path"]
                changed = True
            ver = manifest.get("version", "")
            if e["installedVersion"] != ver:
                e["installedVersion"] = ver
                changed = True
    return changed


def get_manifest(skill_id: str) -> dict | None:
    """Load a single skill manifest by ID."""
    manifests = discover_manifests()
    return manifests.get(skill_id)


def require_skill(reg: dict, skill_id: str) -> dict:
    """Return registry entry for skill_id, or exit with error."""
    if skill_id not in reg["skills"]:
        # Maybe it exists on disk but not in registry yet
        sync_registry_with_manifests(reg)
        save_registry(reg)
    if skill_id not in reg["skills"]:
        print(red(f"Error: skill '{skill_id}' not found."))
        print(f"  Known skills: {', '.join(sorted(reg['skills'])) or '(none)'}")
        raise SystemExit(1)
    return reg["skills"][skill_id]


# ── MCP / Settings manipulation ─────────────────────────────────────────────

def _managed_tag(skill_id: str) -> str:
    """Convention: MCP server keys managed by us are prefixed with skill id."""
    return skill_id


def _resolve_template_vars(obj, wrapper_dir: str):
    """Recursively replace {{WRAPPER_DIR}} in strings."""
    if isinstance(obj, str):
        return obj.replace("{{WRAPPER_DIR}}", wrapper_dir)
    if isinstance(obj, list):
        return [_resolve_template_vars(v, wrapper_dir) for v in obj]
    if isinstance(obj, dict):
        return {k: _resolve_template_vars(v, wrapper_dir) for k, v in obj.items()}
    return obj


def get_wrapper_dir() -> str:
    """Resolve the wrapper directory (repo root)."""
    # Check config first
    config_file = CLAWD_DIR / "config.json"
    if config_file.exists():
        cfg = safe_read_json(config_file)
        wd = cfg.get("wrapper_dir", "")
        if wd:
            return wd
    # Env override
    env = os.environ.get("CLAWD_WRAPPER_DIR", "")
    if env:
        return env
    # Fallback: derive from script location
    return str(REPO_DIR)


def _build_mcp_server_entry(mcp: dict, skill_dir: str, wrapper_dir: str) -> dict:
    """Build a single MCP server entry from manifest mcp block."""
    entry = {}
    if "command" in mcp:
        entry["command"] = mcp["command"]
    if "args" in mcp:
        entry["args"] = list(mcp["args"])
    # Resolve cwd: "." means the skill directory
    cwd = mcp.get("cwd", "")
    if cwd == ".":
        entry["cwd"] = skill_dir
    elif cwd:
        resolved = cwd.replace("{{WRAPPER_DIR}}", wrapper_dir)
        entry["cwd"] = resolved
    # Pass through env if present
    if "env" in mcp:
        entry["env"] = dict(mcp["env"])
    return entry


def build_mcp_entries(reg: dict) -> dict[str, dict]:
    """Build the MCP server entries for all enabled skills."""
    wrapper_dir = get_wrapper_dir()
    entries: dict[str, dict] = {}
    for sid, entry in reg["skills"].items():
        if not entry.get("enabled"):
            continue
        manifest = get_manifest(sid)
        if not manifest:
            continue
        mcp = manifest.get("mcp", {})
        if not mcp:
            continue
        skill_dir = manifest.get("_dir", "")
        # Determine the server key: use serverName if present, else skill id
        server_name = mcp.get("serverName", sid)
        # Support multi-server via "servers" key, or single-server shorthand
        servers = mcp.get("servers", {})
        if not servers and "command" in mcp:
            server_entry = _build_mcp_server_entry(mcp, skill_dir, wrapper_dir)
            entries[server_name] = server_entry
        else:
            for key, server_def in servers.items():
                server_entry = _build_mcp_server_entry(server_def, skill_dir, wrapper_dir)
                entries[key] = server_entry
    return entries


def build_settings_entries(reg: dict) -> list[str]:
    """Build the settings.json permission entries for all enabled skills."""
    permissions: list[str] = []
    for sid, entry in reg["skills"].items():
        if not entry.get("enabled"):
            continue
        manifest = get_manifest(sid)
        if not manifest:
            continue
        # Permissions live at manifest.permissions.allow
        perms = manifest.get("permissions", {}).get("allow", [])
        permissions.extend(perms)
    return permissions


def get_managed_mcp_keys(reg: dict) -> set[str]:
    """Return the set of MCP server keys that are managed by skills."""
    all_keys: set[str] = set()
    for sid in reg["skills"]:
        manifest = get_manifest(sid)
        if not manifest:
            continue
        mcp = manifest.get("mcp", {})
        servers = mcp.get("servers", {})
        if not servers and "command" in mcp:
            # Single-server: key is serverName or skill id
            server_name = mcp.get("serverName", sid)
            all_keys.add(server_name)
        else:
            all_keys.update(servers.keys())
    return all_keys


def get_managed_permissions(reg: dict) -> set[str]:
    """Return all permissions managed by skills (for safe removal)."""
    all_perms: set[str] = set()
    for sid in reg["skills"]:
        manifest = get_manifest(sid)
        if not manifest:
            continue
        perms = manifest.get("permissions", {}).get("allow", [])
        all_perms.update(perms)
    return all_perms


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_list(args):
    """List all skills in a table."""
    reg = load_registry()
    sync_registry_with_manifests(reg)
    save_registry(reg)

    manifests = discover_manifests()
    rows = []
    for sid in sorted(reg["skills"]):
        entry = reg["skills"][sid]
        manifest = manifests.get(sid, {})
        name = manifest.get("name", sid)
        category = manifest.get("category", "-")
        enabled = enabled_color(entry.get("enabled", False))
        state = state_color(entry.get("status", {}).get("state", "unknown"))
        rows.append([sid, name, category, enabled, state])

    print(bold("\nRegistered Skills"))
    print_table(["ID", "Name", "Category", "Enabled", "Status"], rows)
    print()


def cmd_status(args):
    """Detailed status for a skill (or all)."""
    reg = load_registry()
    sync_registry_with_manifests(reg)
    save_registry(reg)

    skill_ids = [args.skill_id] if args.skill_id else sorted(reg["skills"])
    if args.skill_id:
        require_skill(reg, args.skill_id)

    manifests = discover_manifests()
    for sid in skill_ids:
        entry = reg["skills"][sid]
        manifest = manifests.get(sid, {})
        st = entry.get("status", {})
        print(bold(f"\n{'=' * 50}"))
        print(bold(f"  Skill: {sid}"))
        print(f"{'=' * 50}")
        print(f"  Name:          {manifest.get('name', sid)}")
        print(f"  Version:       {entry.get('installedVersion', '-')}")
        print(f"  Category:      {manifest.get('category', '-')}")
        print(f"  Source:         {entry.get('source', '-')}")
        print(f"  Manifest:      {entry.get('manifestPath', '-')}")
        print(f"  Enabled:       {enabled_color(entry.get('enabled', False))}")
        print(f"  Locked:        {'yes' if entry.get('locked') else 'no'}")
        print(f"  State:         {state_color(st.get('state', 'unknown'))}")
        print(f"  Last Check:    {st.get('lastHealthCheck') or '-'}")
        print(f"  Last Error:    {st.get('lastError') or '-'}")
        print(f"  Credentials:   {', '.join(entry.get('credentialRefs', [])) or '-'}")
        cfg = entry.get("config", {})
        if cfg:
            print(f"  Config:        {json.dumps(cfg, indent=2)}")
        else:
            print(f"  Config:        (none)")
        desc = manifest.get("description", "")
        if desc:
            print(f"  Description:   {desc}")
    print()


def cmd_enable(args):
    """Enable a skill and update .mcp.json + settings.json."""
    reg = load_registry()
    sync_registry_with_manifests(reg)
    entry = require_skill(reg, args.skill_id)

    if entry.get("locked"):
        print(red(f"Error: skill '{args.skill_id}' is locked. Unlock it first."))
        raise SystemExit(1)

    if entry.get("enabled"):
        print(yellow(f"Skill '{args.skill_id}' is already enabled."))
        return

    manifest = get_manifest(args.skill_id)
    if not manifest:
        print(red(f"Error: no skill.json manifest found for '{args.skill_id}'."))
        raise SystemExit(1)

    entry["enabled"] = True
    entry["status"]["state"] = "running"
    save_registry(reg)

    _reconcile_files(reg)
    print(green(f"Skill '{args.skill_id}' enabled."))


def cmd_disable(args):
    """Disable a skill and update .mcp.json + settings.json."""
    reg = load_registry()
    sync_registry_with_manifests(reg)
    entry = require_skill(reg, args.skill_id)

    if entry.get("locked"):
        print(red(f"Error: skill '{args.skill_id}' is locked. Unlock it first."))
        raise SystemExit(1)

    if not entry.get("enabled"):
        print(yellow(f"Skill '{args.skill_id}' is already disabled."))
        return

    entry["enabled"] = False
    entry["status"]["state"] = "stopped"
    save_registry(reg)

    _reconcile_files(reg)
    print(green(f"Skill '{args.skill_id}' disabled."))


def cmd_config(args):
    """Show or edit a skill's config."""
    reg = load_registry()
    sync_registry_with_manifests(reg)
    entry = require_skill(reg, args.skill_id)
    manifest = get_manifest(args.skill_id)

    # Show current config
    cfg = entry.get("config", {})
    schema = (manifest or {}).get("configSchema", {})
    defaults = (manifest or {}).get("configDefaults", {})
    # Extract properties from JSON Schema format
    properties = schema.get("properties", {}) if isinstance(schema, dict) else {}

    print(bold(f"\nConfig for '{args.skill_id}'"))
    if not cfg and not properties:
        print(dim("  This skill has no configurable options."))
        print()
        return

    if properties:
        print(dim("  Schema (from skill.json):"))
        for key, spec in properties.items():
            default_val = defaults.get(key, spec.get("default", ""))
            current = cfg.get(key, default_val)
            desc = spec.get("description", "")
            type_hint = spec.get("type", "")
            extra = []
            if desc:
                extra.append(desc)
            if type_hint:
                extra.append(f"type: {type_hint}")
            hint = "; ".join(extra)
            print(f"    {bold(key)}: {current}  {dim(f'({hint})') if hint else ''}")
    elif cfg:
        print(json.dumps(cfg, indent=2))

    print(dim("\n  To set a value: skill-manager.py config <skill-id> --set key=value"))

    # Handle --set
    if args.set_values:
        for kv in args.set_values:
            if "=" not in kv:
                print(red(f"  Invalid format: {kv} (expected key=value)"))
                continue
            k, v = kv.split("=", 1)
            # Try to parse as JSON for booleans/numbers
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                pass  # keep as string
            cfg[k] = v
            print(green(f"  Set {k} = {v!r}"))
        entry["config"] = cfg
        save_registry(reg)
    print()


def cmd_credentials(args):
    """Manage credentials for a skill."""
    reg = load_registry()
    sync_registry_with_manifests(reg)
    entry = require_skill(reg, args.skill_id)
    manifest = get_manifest(args.skill_id)

    required_creds = (manifest or {}).get("credentials", [])
    current_refs = entry.get("credentialRefs", [])

    print(bold(f"\nCredentials for '{args.skill_id}'"))
    if not required_creds:
        print(dim("  This skill does not declare any credential requirements."))
        print()
        return

    for cred_spec in required_creds:
        cred_id = cred_spec.get("id", "unknown")
        label = cred_spec.get("label", "")
        required = cred_spec.get("required", False)
        cred_file = CREDENTIALS_DIR / f"{cred_id}.json"
        exists = cred_file.exists()

        status = green("configured") if exists else (red("MISSING") if required else yellow("not set"))
        req_label = red("required") if required else dim("optional")
        print(f"  {bold(cred_id)}: {status}  [{req_label}]")
        if label:
            print(f"    {dim(label)}")
        # Show expected fields
        fields = cred_spec.get("fields", [])
        if fields:
            field_names = [f.get("key", "?") for f in fields]
            print(f"    {dim('Fields: ' + ', '.join(field_names))}")

    if args.set_credential:
        cred_id, cred_value = args.set_credential
        cred_file = CREDENTIALS_DIR / f"{cred_id}.json"
        # Try parsing as JSON; if it fails, wrap as {"value": ...}
        try:
            cred_data = json.loads(cred_value)
        except (json.JSONDecodeError, ValueError):
            cred_data = {"value": cred_value}
        safe_write_json(cred_file, cred_data, restricted=True)
        if cred_id not in current_refs:
            entry["credentialRefs"].append(cred_id)
            save_registry(reg)
        print(green(f"  Credential '{cred_id}' saved to {cred_file}"))

    print(dim(f"\n  Credentials stored in: {CREDENTIALS_DIR}"))
    print(dim("  To set: skill-manager.py credentials <skill-id> --set <cred-id> <json-or-value>"))
    print()


def cmd_health(args):
    """Run health checks on all enabled skills."""
    reg = load_registry()
    sync_registry_with_manifests(reg)
    save_registry(reg)

    manifests = discover_manifests()
    any_checked = False

    print(bold("\nSkill Health Checks"))
    print("-" * 50)

    for sid in sorted(reg["skills"]):
        entry = reg["skills"][sid]
        if not entry.get("enabled"):
            continue
        manifest = manifests.get(sid, {})
        health = manifest.get("healthCheck", {})
        name = manifest.get("name", sid)
        any_checked = True

        # Default health check: verify manifest exists and MCP command is valid
        state = "running"
        error = None

        # Check 1: manifest exists
        if not manifest:
            state = "error"
            error = "skill.json manifest not found"
        else:
            # Check 2: if MCP, verify command exists
            mcp = manifest.get("mcp", {})
            cmd = mcp.get("command", "")
            if cmd and not shutil.which(cmd):
                state = "degraded"
                error = f"command '{cmd}' not found in PATH"

            # Check 3: custom health check command (type=command uses "target")
            hc_cmd = health.get("target", health.get("command", ""))
            if hc_cmd and state != "error" and health.get("type") == "command":
                hc_cwd = health.get("cwd", manifest.get("_dir", "."))
                hc_cwd = hc_cwd.replace("{{WRAPPER_DIR}}", get_wrapper_dir())
                try:
                    result = subprocess.run(
                        hc_cmd, shell=True, cwd=hc_cwd,
                        capture_output=True, text=True, timeout=30
                    )
                    if result.returncode != 0:
                        state = "degraded"
                        error = result.stderr.strip() or f"exit code {result.returncode}"
                except subprocess.TimeoutExpired:
                    state = "degraded"
                    error = "health check timed out (30s)"
                except OSError as exc:
                    state = "degraded"
                    error = str(exc)

            # Check 4: credential requirements met
            for cred_spec in manifest.get("credentials", []):
                if cred_spec.get("required"):
                    cred_file = CREDENTIALS_DIR / f"{cred_spec['id']}.json"
                    if not cred_file.exists():
                        state = "degraded"
                        error = f"required credential '{cred_spec['id']}' missing"
                        break

        entry["status"]["state"] = state
        entry["status"]["lastHealthCheck"] = now_iso()
        entry["status"]["lastError"] = error

        icon = green("[OK]") if state == "running" else (
            yellow("[WARN]") if state == "degraded" else red("[FAIL]"))
        print(f"  {icon} {bold(name)} ({sid})")
        if error:
            print(f"       {dim(error)}")

    if not any_checked:
        print(dim("  No enabled skills to check."))

    save_registry(reg)
    print()


def cmd_reconcile(args):
    """Re-derive .mcp.json and settings.json from registry + manifests."""
    reg = load_registry()
    sync_registry_with_manifests(reg)
    save_registry(reg)

    _reconcile_files(reg)
    print(green("Reconcile complete."))
    print(f"  .mcp.json:     {MCP_FILE}")
    print(f"  settings.json: {SETTINGS_FILE}")
    print()


def _reconcile_files(reg: dict) -> None:
    """Core reconcile logic: merge skill-managed entries into config files,
    preserving manual/external entries."""

    managed_mcp_keys = get_managed_mcp_keys(reg)
    managed_permissions = get_managed_permissions(reg)

    # ── .mcp.json ────────────────────────────────────────────────────────
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    current_mcp = safe_read_json(MCP_FILE, {"mcpServers": {}})
    current_mcp.setdefault("mcpServers", {})

    # Remove managed entries (we'll re-add the enabled ones)
    for key in list(current_mcp["mcpServers"]):
        if key in managed_mcp_keys:
            del current_mcp["mcpServers"][key]

    # Add enabled skill MCP entries
    new_entries = build_mcp_entries(reg)
    current_mcp["mcpServers"].update(new_entries)

    safe_write_json(MCP_FILE, current_mcp)

    # ── settings.json ────────────────────────────────────────────────────
    current_settings = safe_read_json(SETTINGS_FILE, {"permissions": {"allow": []}})
    current_settings.setdefault("permissions", {})
    current_settings["permissions"].setdefault("allow", [])

    current_perms = current_settings["permissions"]["allow"]

    # Remove managed permissions (we'll re-add the enabled ones)
    preserved = [p for p in current_perms if p not in managed_permissions]

    # Add enabled skill permissions
    new_perms = build_settings_entries(reg)
    # De-duplicate while preserving order
    seen = set(preserved)
    merged = list(preserved)
    for p in new_perms:
        if p not in seen:
            merged.append(p)
            seen.add(p)

    current_settings["permissions"]["allow"] = merged
    safe_write_json(SETTINGS_FILE, current_settings)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="skill-manager",
        description="Manage clawd-lobster skills — enable, disable, configure, and reconcile.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python skill-manager.py list
              python skill-manager.py enable memory
              python skill-manager.py disable memory
              python skill-manager.py config memory --set provider=openai
              python skill-manager.py credentials memory --set openai-key sk-xxx
              python skill-manager.py health
              python skill-manager.py reconcile
        """),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List all skills")

    # status
    p_status = sub.add_parser("status", help="Detailed status for a skill")
    p_status.add_argument("skill_id", nargs="?", default=None, help="Skill ID (omit for all)")

    # enable
    p_enable = sub.add_parser("enable", help="Enable a skill")
    p_enable.add_argument("skill_id", help="Skill ID to enable")

    # disable
    p_disable = sub.add_parser("disable", help="Disable a skill")
    p_disable.add_argument("skill_id", help="Skill ID to disable")

    # config
    p_config = sub.add_parser("config", help="Show/edit skill config")
    p_config.add_argument("skill_id", help="Skill ID")
    p_config.add_argument("--set", dest="set_values", nargs="*", metavar="key=value",
                          help="Set config values (key=value pairs)")

    # credentials
    p_creds = sub.add_parser("credentials", help="Manage skill credentials")
    p_creds.add_argument("skill_id", help="Skill ID")
    p_creds.add_argument("--set", dest="set_credential", nargs=2,
                          metavar=("CRED_ID", "VALUE"),
                          help="Set a credential value")

    # health
    sub.add_parser("health", help="Run health checks on all enabled skills")

    # reconcile
    sub.add_parser("reconcile", help="Re-derive .mcp.json + settings.json from registry")

    args = parser.parse_args()

    dispatch = {
        "list": cmd_list,
        "status": cmd_status,
        "enable": cmd_enable,
        "disable": cmd_disable,
        "config": cmd_config,
        "credentials": cmd_credentials,
        "health": cmd_health,
        "reconcile": cmd_reconcile,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
