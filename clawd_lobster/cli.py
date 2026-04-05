"""
clawd_lobster.cli — Main entry point for the clawd-lobster CLI.

Usage:
    clawd-lobster serve            Start the web UI server
    clawd-lobster setup            Run the terminal onboarding wizard
    clawd-lobster workspace create Create a new workspace
    clawd-lobster squad start      Run spec squad in terminal
    clawd-lobster status           Show system health
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from clawd_lobster import __version__


# ── Path helpers ────────────────────────────────────────────────────────────

def _home() -> Path:
    return Path.home()


def _config_dir() -> Path:
    return _home() / ".clawd-lobster"


def _config_file() -> Path:
    return _config_dir() / "config.json"


def _repo_dir() -> Path:
    """Root of the clawd-lobster repository (parent of this package)."""
    return Path(__file__).resolve().parent.parent


def _read_json(path: Path, default=None):
    """Read a JSON file, returning *default* on any error."""
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


# ── ANSI helpers ────────────────────────────────────────────────────────────

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


# ── Subcommand: serve ──────────────────────────────────────────────────────

def cmd_serve(args: argparse.Namespace) -> int:
    """Start the clawd-lobster web server."""
    from clawd_lobster.server import start_server

    port = args.port
    open_browser = not args.no_open

    if args.daemon:
        # Background mode: re-launch self as a detached process
        cmd = [sys.executable, "-m", "clawd_lobster.cli", "serve",
               "--port", str(port), "--no-open"]
        if platform.system() == "Windows":
            # Windows: CREATE_NO_WINDOW flag
            CREATE_NO_WINDOW = 0x08000000
            proc = subprocess.Popen(
                cmd,
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        pid_file = _config_dir() / "server.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(proc.pid), encoding="utf-8")
        print(f"Server started in background (PID {proc.pid})")
        print(f"  URL: http://localhost:{port}")
        print(f"  PID file: {pid_file}")
        return 0

    print(f"{bold('clawd-lobster')} v{__version__}")
    print(f"Starting server on http://localhost:{port}")
    start_server(port=port, open_browser=open_browser)
    return 0


# ── Subcommand: setup ──────────────────────────────────────────────────────

def cmd_setup(_args: argparse.Namespace) -> int:
    """Run the terminal onboarding wizard."""
    from clawd_lobster.onboarding import run_terminal_setup

    print(f"{bold('clawd-lobster setup')} v{__version__}")
    print(dim("-" * 40))
    run_terminal_setup()
    return 0


# ── Subcommand: workspace ──────────────────────────────────────────────────

def cmd_workspace(args: argparse.Namespace) -> int:
    """Handle workspace subcommands."""
    if args.workspace_action == "create":
        return _workspace_create(args)
    else:
        # Shouldn't reach here due to argparse required=True
        print(red("Unknown workspace action. Use: clawd-lobster workspace create <name>"))
        return 1


def _workspace_create(args: argparse.Namespace) -> int:
    """Create a new workspace using workspace-create.py logic."""
    scripts_dir = _repo_dir() / "scripts"
    ws_script = scripts_dir / "workspace-create.py"

    if not ws_script.exists():
        print(red(f"Error: workspace-create.py not found at {ws_script}"))
        return 1

    # Dynamic import of workspace-create.py (hyphen in filename)
    import importlib.util
    spec = importlib.util.spec_from_file_location("workspace_create", str(ws_script))
    if spec is None or spec.loader is None:
        print(red("Error: could not load workspace-create.py"))
        return 1

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    try:
        summary = mod.create_workspace(
            name=args.name,
            domain=args.domain or "personal",
            description=args.description or "",
            create_repo=args.repo,
            dry_run=args.dry_run,
        )
        mod.print_summary(summary)
        return 0
    except FileExistsError as exc:
        print(red(f"Error: {exc}"))
        return 1
    except ValueError as exc:
        print(red(f"Error: {exc}"))
        return 1


# ── Subcommand: squad ──────────────────────────────────────────────────────

def cmd_squad(args: argparse.Namespace) -> int:
    """Handle squad subcommands."""
    if args.squad_action == "start":
        return _squad_start(args)
    else:
        print(red("Unknown squad action. Use: clawd-lobster squad start"))
        return 1


def _squad_start(args: argparse.Namespace) -> int:
    """Run spec squad in terminal mode."""
    from clawd_lobster.squad import run_squad_terminal

    workspace = getattr(args, "workspace", None)
    print(f"{bold('clawd-lobster squad')} v{__version__}")
    print(dim("-" * 40))
    run_squad_terminal(workspace=workspace)
    return 0


# ── Subcommand: status ─────────────────────────────────────────────────────

def cmd_status(_args: argparse.Namespace) -> int:
    """Show system health information."""
    print(f"{bold('clawd-lobster')} v{__version__}")
    print(dim("=" * 50))

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  Python:       {green(py_ver)}")

    # Platform
    print(f"  Platform:     {platform.system()} {platform.release()}")

    # Claude CLI version
    claude_ver = _get_tool_version("claude", ["--version"])
    if claude_ver:
        print(f"  Claude CLI:   {green(claude_ver)}")
    else:
        print(f"  Claude CLI:   {red('not found')}")

    # Git version
    git_ver = _get_tool_version("git", ["--version"])
    if git_ver:
        print(f"  Git:          {green(git_ver)}")
    else:
        print(f"  Git:          {red('not found')}")

    print()

    # Config
    config = _read_json(_config_file())
    config_exists = _config_file().exists()
    if config_exists:
        print(f"  Config:       {green(str(_config_file()))}")
        ws_root = config.get("workspace_root", "")
        if ws_root:
            print(f"  Workspace root: {ws_root}")
    else:
        print(f"  Config:       {yellow('not found (run clawd-lobster setup)')}")

    # Workspaces
    print()
    ws_json_path = _find_workspaces_json()
    ws_data = _read_json(ws_json_path, {"workspaces": []})
    workspaces = ws_data.get("workspaces", [])
    ws_count = len(workspaces)

    if ws_count == 0:
        print(f"  Workspaces:   {yellow('none')}")
    else:
        print(f"  Workspaces:   {green(str(ws_count))}")
        for ws in workspaces:
            ws_id = ws.get("id", "?")
            ws_path = Path(ws.get("path", ""))
            exists = ws_path.exists()
            status = green("ok") if exists else red("missing")

            # Memory size
            mem_db = ws_path / ".claude-memory" / "memory.db"
            if mem_db.exists():
                size_kb = mem_db.stat().st_size / 1024
                mem_info = f"{size_kb:.0f} KB"
            else:
                mem_info = "no db"

            print(f"    {bold(ws_id):30s}  {status}  mem: {dim(mem_info)}")

    # Heartbeat / PID
    print()
    pid_file = _config_dir() / "server.pid"
    if pid_file.exists():
        pid = pid_file.read_text(encoding="utf-8").strip()
        print(f"  Server PID:   {pid} {dim('(' + str(pid_file) + ')')}")
    else:
        print(f"  Server:       {dim('not running')}")

    print()
    return 0


def _get_tool_version(tool: str, args: list[str]) -> str:
    """Get version string for a CLI tool, or empty string if not found."""
    exe = shutil.which(tool)
    if exe is None:
        return ""
    try:
        result = subprocess.run(
            [exe] + args,
            capture_output=True, text=True, timeout=10,
        )
        output = result.stdout.strip() or result.stderr.strip()
        # Clean up — take first line, strip common prefixes
        if output:
            return output.splitlines()[0].strip()
        return ""
    except (subprocess.TimeoutExpired, OSError):
        return ""


def _find_workspaces_json() -> Path:
    """Locate workspaces.json — config.data_dir, config.wrapper_dir, or repo dir."""
    config = _read_json(_config_file())
    data_dir = config.get("data_dir", "")
    if data_dir:
        candidate = Path(data_dir) / "workspaces.json"
        if candidate.exists():
            return candidate
    wrapper_dir = config.get("wrapper_dir", "")
    if wrapper_dir:
        candidate = Path(wrapper_dir) / "workspaces.json"
        if candidate.exists():
            return candidate
    return _repo_dir() / "workspaces.json"


# ── Parser ──────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="clawd-lobster",
        description="AI-native spec-to-code framework — from idea to working code.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Quick start:
  clawd-lobster setup                      First-time setup wizard
  clawd-lobster serve                      Start the web UI
  clawd-lobster workspace create my-app    Create a new workspace
  clawd-lobster squad start                Run spec squad
  clawd-lobster status                     Show system health
""",
    )
    parser.add_argument(
        "--version", "-V", action="version",
        version=f"clawd-lobster {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── serve ───────────────────────────────────────────────────────────
    p_serve = subparsers.add_parser(
        "serve",
        help="Start the web UI server",
        description="Start the clawd-lobster web server on localhost.",
    )
    p_serve.add_argument(
        "--port", "-p", type=int, default=3333,
        help="Port to bind (default: 3333)",
    )
    p_serve.add_argument(
        "--no-open", action="store_true",
        help="Don't open the browser automatically",
    )
    p_serve.add_argument(
        "--daemon", "-d", action="store_true",
        help="Run in background (daemon mode)",
    )
    p_serve.set_defaults(func=cmd_serve)

    # ── setup ──────────────────────────────────────────────────────────
    p_setup = subparsers.add_parser(
        "setup",
        help="Run the terminal onboarding wizard",
        description="Interactive setup wizard for first-time configuration.",
    )
    p_setup.set_defaults(func=cmd_setup)

    # ── workspace ──────────────────────────────────────────────────────
    p_workspace = subparsers.add_parser(
        "workspace",
        help="Manage workspaces",
        description="Create and manage clawd-lobster workspaces.",
    )
    ws_sub = p_workspace.add_subparsers(dest="workspace_action")

    p_ws_create = ws_sub.add_parser(
        "create",
        help="Create a new workspace",
        description="Create a new workspace with memory, git, and optional GitHub repo.",
    )
    p_ws_create.add_argument(
        "name",
        help="Workspace name (kebab-case, e.g. my-app)",
    )
    p_ws_create.add_argument(
        "--domain", choices=("work", "personal", "hybrid"),
        help="Domain: work, personal, or hybrid (default: personal)",
    )
    p_ws_create.add_argument(
        "--description", help="Short project description",
    )
    p_ws_create.add_argument(
        "--repo", action="store_true",
        help="Create a private GitHub repo",
    )
    p_ws_create.add_argument(
        "--dry-run", action="store_true",
        help="Preview without making changes",
    )
    p_ws_create.set_defaults(func=cmd_workspace)

    # ── squad ──────────────────────────────────────────────────────────
    p_squad = subparsers.add_parser(
        "squad",
        help="Run the spec squad",
        description="Launch spec squad agents for discovery and code generation.",
    )
    sq_sub = p_squad.add_subparsers(dest="squad_action")

    p_sq_start = sq_sub.add_parser(
        "start",
        help="Start the spec squad in terminal mode",
    )
    p_sq_start.add_argument(
        "--workspace", "-w",
        help="Workspace name or path (default: current directory)",
    )
    p_sq_start.set_defaults(func=cmd_squad)

    # ── status ─────────────────────────────────────────────────────────
    p_status = subparsers.add_parser(
        "status",
        help="Show system health",
        description="Display system info, workspace status, and health checks.",
    )
    p_status.set_defaults(func=cmd_status)

    return parser


# ── Entry point ─────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print(f"\n{yellow('Interrupted.')}")
        return 130


if __name__ == "__main__":
    sys.exit(main())
