"""
clawd_lobster.onboarding — Setup wizard logic.

Handles prerequisite checking, Claude CLI auth, persona selection,
and first workspace creation -- in both terminal and web modes.

No external dependencies -- stdlib only.
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────

HOME = Path.home()
CONFIG_DIR = HOME / ".clawd-lobster"
CONFIG_FILE = CONFIG_DIR / "config.json"
IS_WINDOWS = platform.system() == "Windows"


# ── ANSI helpers (terminal mode) ───────────────────────────────────────────

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def _green(t: str) -> str:
    return _c("32", t)


def _red(t: str) -> str:
    return _c("31", t)


def _yellow(t: str) -> str:
    return _c("33", t)


def _cyan(t: str) -> str:
    return _c("36", t)


def _bold(t: str) -> str:
    return _c("1", t)


def _dim(t: str) -> str:
    return _c("2", t)


# ── Utility ────────────────────────────────────────────────────────────────

def _run_cmd(args: list[str]) -> subprocess.CompletedProcess:
    """Run a command, capturing output. Returns CompletedProcess."""
    try:
        return subprocess.run(
            args, capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(
            args, returncode=-1, stdout="", stderr=f"{args[0]} not found",
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            args, returncode=-1, stdout="", stderr="timeout",
        )


def _get_version(args: list[str]) -> str:
    """Run a version command and extract the version string."""
    result = _run_cmd(args)
    if result.returncode != 0:
        return ""
    text = result.stdout.strip() or result.stderr.strip()
    # Extract version-like substring (e.g. "3.12.1" from "Python 3.12.1")
    for part in text.split():
        if part and part[0].isdigit():
            return part
    return text[:40] if text else ""


# ── Prerequisite checks ───────────────────────────────────────────────────

def check_prerequisites() -> dict:
    """Check system prerequisites. Returns dict with checks list and metadata.

    Returns:
        {
            "checks": [
                {"name": "python", "ok": True, "version": "3.12.1", "optional": False},
                {"name": "claude", "ok": True, "version": "1.0.0", "optional": False},
                {"name": "git", "ok": True, "version": "2.43.0", "optional": False},
                {"name": "node", "ok": False, "version": "", "optional": True},
                {"name": "pip", "ok": True, "version": "24.0", "optional": False},
            ],
            "all_required_ok": True,
            "default_root": "~/Documents/Workspace"
        }
    """
    checks = []

    # Python
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append({
        "name": "python",
        "ok": sys.version_info >= (3, 10),
        "version": py_version,
        "optional": False,
    })

    # Claude CLI
    claude_version = _get_version(["claude", "--version"])
    checks.append({
        "name": "claude",
        "ok": bool(claude_version),
        "version": claude_version,
        "optional": False,
    })

    # Git
    git_version = _get_version(["git", "--version"])
    checks.append({
        "name": "git",
        "ok": bool(git_version),
        "version": git_version,
        "optional": False,
    })

    # Node (optional)
    node_version = _get_version(["node", "--version"])
    # node --version returns "v20.11.0" — strip leading v
    if node_version.startswith("v"):
        node_version = node_version[1:]
    checks.append({
        "name": "node",
        "ok": bool(node_version),
        "version": node_version,
        "optional": True,
    })

    # pip
    pip_version = _get_version([sys.executable, "-m", "pip", "--version"])
    checks.append({
        "name": "pip",
        "ok": bool(pip_version),
        "version": pip_version,
        "optional": False,
    })

    all_required_ok = all(c["ok"] for c in checks if not c["optional"])

    # Default workspace root
    default_root = str(HOME / "Documents" / "Workspace")
    config = _load_config()
    if config.get("workspace_root"):
        default_root = config["workspace_root"]

    return {
        "checks": checks,
        "all_required_ok": all_required_ok,
        "default_root": default_root,
    }


# ── Config management ─────────────────────────────────────────────────────

def _load_config() -> dict:
    """Load config.json, returning empty dict on failure."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def is_first_time() -> bool:
    """Check if this is a first-time setup (no config.json exists)."""
    return not CONFIG_FILE.exists()


def save_config(persona: str, workspace_root: str) -> None:
    """Write config.json with persona and workspace root.

    Args:
        persona: User persona — "noob", "expert", or "tech".
        workspace_root: Absolute path to workspace root directory.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    config = _load_config()
    config["persona"] = persona
    config["workspace_root"] = workspace_root
    config["setup_complete"] = True

    tmp = CONFIG_FILE.with_suffix(".tmp")
    try:
        tmp.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        if IS_WINDOWS and CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        tmp.rename(CONFIG_FILE)
    except OSError:
        if tmp.exists():
            tmp.unlink()
        raise


# ── Terminal onboarding ────────────────────────────────────────────────────

def run_terminal_setup() -> None:
    """Run the interactive terminal onboarding wizard.

    Walks the user through:
      1. Prerequisite checks (Python, Claude CLI, git)
      2. Persona selection (noob / expert / tech)
      3. Workspace root directory
      4. First workspace creation
    """
    print(f"\n{_bold('clawd-lobster setup')}")
    print(_dim("-" * 40))

    # Step 1: Prerequisites
    print(f"\n{_bold('Step 1: Prerequisites')}\n")
    result = check_prerequisites()

    any_fail = False
    for check in result["checks"]:
        if check["ok"]:
            status = _green("OK")
            ver = f" ({check['version']})" if check["version"] else ""
            print(f"  {_green('+')} {check['name']}{ver} {status}")
        elif check["optional"]:
            print(f"  {_dim('o')} {check['name']} {_dim('optional, not found')}")
        else:
            print(f"  {_red('x')} {check['name']} {_red('MISSING')}")
            any_fail = True

    if any_fail:
        print(f"\n{_red('Some required tools are missing. Install them and retry.')}")
        return

    print(f"\n  {_green('All prerequisites met.')}")

    # Step 2: Persona
    print(f"\n{_bold('Step 2: How do you work?')}\n")
    print("  1. Guided  — New to AI dev. Show me everything.")
    print("  2. Expert  — I know what I'm doing. Less hand-holding.")
    print("  3. Tech    — I want full control and raw output.")

    persona_map = {"1": "noob", "2": "expert", "3": "tech"}
    while True:
        choice = input(f"\n  Choose [1/2/3] (default: 1): ").strip()
        if not choice:
            choice = "1"
        if choice in persona_map:
            persona = persona_map[choice]
            break
        print(_red("  Invalid choice. Enter 1, 2, or 3."))

    # Step 3: Workspace root
    print(f"\n{_bold('Step 3: Workspace root directory')}\n")
    default_root = result["default_root"]
    ws_root = input(f"  Root directory [{default_root}]: ").strip()
    if not ws_root:
        ws_root = default_root

    ws_root_path = Path(ws_root).expanduser().resolve()
    ws_root_path.mkdir(parents=True, exist_ok=True)
    print(f"  Using: {_dim(str(ws_root_path))}")

    # Save config
    save_config(persona, str(ws_root_path))
    print(f"\n  {_green('Config saved to')} {_dim(str(CONFIG_FILE))}")

    # Step 4: First workspace
    print(f"\n{_bold('Step 4: Create your first workspace')}\n")
    ws_name = input("  Workspace name (kebab-case, e.g. my-project): ").strip()

    if ws_name:
        # Try to use workspace-create logic
        try:
            repo_dir = Path(__file__).resolve().parent.parent
            sys.path.insert(0, str(repo_dir / "scripts"))
            from importlib import import_module
            wc = import_module("workspace-create")
            summary = wc.create_workspace(name=ws_name, domain="personal")
            wc.print_summary(summary)
        except Exception as e:
            print(f"  {_yellow('Could not create workspace:')} {e}")
            print(f"  You can create one later with: clawd-lobster workspace create {ws_name}")
    else:
        print(f"  {_dim('Skipped. Create one later with: clawd-lobster workspace create <name>')}")

    # Done
    print(f"\n{_green(_bold('Setup complete!'))}")
    print(f"\n  Next steps:")
    print(f"    clawd-lobster serve      — Open the web UI")
    print(f"    clawd-lobster workspace   — Manage workspaces")
    print(f"    clawd-lobster squad start — Launch Spec Squad\n")
