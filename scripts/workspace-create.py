#!/usr/bin/env python3
"""
workspace-create.py — CLI tool for creating clawd-lobster workspaces.

Usage:
  python workspace-create.py                                    # Interactive
  python workspace-create.py --name "my-api" --domain work      # Non-interactive
  python workspace-create.py --name "my-api" --dry-run           # Dry run
  python workspace-create.py --name "my-api" --repo              # With GitHub repo

No external dependencies — stdlib only, cross-platform (Windows + Unix).
"""

import argparse
import copy
import json
import os
import platform
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

HOME = Path.home()
CLAWD_DIR = HOME / ".clawd-lobster"
CONFIG_FILE = CLAWD_DIR / "config.json"
REPO_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_DIR / "scripts"
TEMPLATES_DIR = REPO_DIR / "templates"
IS_WINDOWS = platform.system() == "Windows"

VALID_DOMAINS = ("work", "personal", "hybrid")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# ── ANSI Colors (graceful fallback) ──────────────────────────────────────────

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

# Safe unicode symbols — fallback to ASCII if encoding can't handle them
try:
    "\u2713".encode(sys.stdout.encoding or "ascii")
    SYM_CHECK = "\u2713"  # ✓
    SYM_CIRCLE = "\u25CB"  # ○
except (UnicodeEncodeError, LookupError):
    SYM_CHECK = "+"
    SYM_CIRCLE = "o"


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


def safe_write_json(path: Path, data, restricted: bool = False) -> None:
    """Write JSON atomically (write tmp then rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        if IS_WINDOWS:
            if path.exists():
                path.unlink()
        tmp.rename(path)
    except OSError as exc:
        if tmp.exists():
            tmp.unlink()
        raise SystemExit(red(f"Error writing {path}: {exc}"))

    if restricted and not IS_WINDOWS:
        try:
            import stat as _stat
            os.chmod(path, _stat.S_IRUSR | _stat.S_IWUSR)
        except OSError:
            pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: list[str], cwd: Path = None, check: bool = False) -> subprocess.CompletedProcess:
    """Run a command, capturing output. Returns CompletedProcess."""
    try:
        return subprocess.run(
            args, cwd=str(cwd) if cwd else None,
            capture_output=True, text=True, check=check,
        )
    except FileNotFoundError:
        # Command not installed
        return subprocess.CompletedProcess(args, returncode=-1, stdout="", stderr=f"{args[0]} not found")
    except subprocess.CalledProcessError as exc:
        return subprocess.CompletedProcess(args, returncode=exc.returncode, stdout=exc.stdout, stderr=exc.stderr)


def tool_available(name: str) -> bool:
    """Check if a CLI tool is available on PATH."""
    from shutil import which
    return which(name) is not None


# ── Validation ───────────────────────────────────────────────────────────────

def validate_name(name: str) -> str:
    """Validate workspace name: kebab-case, no spaces, no special chars."""
    name = name.strip()
    if not name:
        raise ValueError("Workspace name cannot be empty")
    if not KEBAB_RE.match(name):
        raise ValueError(
            f"Invalid name '{name}'. Must be kebab-case "
            "(lowercase letters, numbers, hyphens only, no leading/trailing hyphens)"
        )
    return name


def validate_domain(domain: str) -> str:
    """Validate domain value."""
    domain = domain.strip().lower()
    if domain not in VALID_DOMAINS:
        raise ValueError(f"Invalid domain '{domain}'. Must be one of: {', '.join(VALID_DOMAINS)}")
    return domain


# ── Path Resolution ─────────────────────────────────────────────────────────

def resolve_workspace_root() -> Path:
    """
    Determine workspace root directory, checking in order:
    1. CLAWD_WORKSPACE_ROOT env var
    2. workspace_root from ~/.clawd-lobster/config.json
    3. Default: ~/Documents/Workspace/
    """
    # 1. Environment variable
    env_root = os.environ.get("CLAWD_WORKSPACE_ROOT")
    if env_root:
        return Path(env_root)

    # 2. Config file
    config = safe_read_json(CONFIG_FILE)
    cfg_root = config.get("workspace_root", "")
    if cfg_root:
        return Path(cfg_root)

    # 3. Default
    return HOME / "Documents" / "Workspace"


def resolve_workspaces_json() -> Path:
    """Find workspaces.json — check config.data_dir, then repo dir."""
    config = safe_read_json(CONFIG_FILE)
    data_dir = config.get("data_dir", "")
    if data_dir:
        candidate = Path(data_dir) / "workspaces.json"
        if candidate.exists():
            return candidate

    # Fallback: repo dir (wrapper_dir from config, or script-derived)
    wrapper_dir = config.get("wrapper_dir", "")
    if wrapper_dir:
        candidate = Path(wrapper_dir) / "workspaces.json"
        if candidate.exists():
            return candidate

    return REPO_DIR / "workspaces.json"


# ── Core Functions ───────────────────────────────────────────────────────────

def create_directory_structure(workspace_path: Path, dry_run: bool = False) -> list[str]:
    """Create the workspace directory tree. Returns list of created dirs."""
    dirs = [
        workspace_path,
        workspace_path / ".claude-memory",
        workspace_path / ".claude" / "rules",
        workspace_path / ".claude" / "hooks",
        workspace_path / "knowledge",
        workspace_path / "knowledge" / "raw",
        workspace_path / "knowledge" / "wiki",
        workspace_path / "knowledge" / "wiki" / "architecture",
        workspace_path / "knowledge" / "wiki" / "conventions",
        workspace_path / "knowledge" / "wiki" / "decisions",
        workspace_path / "knowledge" / "wiki" / "learnings",
        workspace_path / "knowledge" / "wiki" / "skills",
        workspace_path / "knowledge" / ".pending",
        workspace_path / "skills",
        workspace_path / "skills" / "learned",
        workspace_path / "openspec",
        workspace_path / "openspec" / "changes",
    ]

    created = []
    for d in dirs:
        if dry_run:
            created.append(str(d))
        else:
            d.mkdir(parents=True, exist_ok=True)
            created.append(str(d))

    return created


def create_knowledge_index(workspace_path: Path, name: str, dry_run: bool = False) -> None:
    """Create knowledge/INDEX.md with starter content."""
    content = f"""# {name} — Knowledge Index

## Wiki
Cross-referenced knowledge pages organized by topic:
- `wiki/architecture/` — system design decisions
- `wiki/conventions/` — coding standards, patterns
- `wiki/decisions/` — why we chose X over Y (with provenance)
- `wiki/learnings/` — mistakes and lessons
- `wiki/skills/` — reusable patterns

## Raw Sources
Immutable source materials in `raw/`.

## Pending Corrections
Proposed wiki edits awaiting review in `.pending/`.

## Log
Append-only journal of knowledge operations in `log.md`.
"""
    index_path = workspace_path / "knowledge" / "INDEX.md"
    if not dry_run:
        index_path.write_text(content, encoding="utf-8")

    # Create log.md (append-only journal, Karpathy pattern)
    log_path = workspace_path / "knowledge" / "log.md"
    if not dry_run and not log_path.exists():
        log_path.write_text(f"# {name} — Knowledge Log\n\nAppend-only journal of knowledge operations.\n", encoding="utf-8")


def create_openspec_project(workspace_path: Path, name: str, description: str = "",
                            dry_run: bool = False) -> None:
    """Create openspec/project.md placeholder."""
    desc_line = description if description else "Describe the project goals and scope here."
    content = f"""# {name} — Project Spec

## Overview
{desc_line}

## Goals
- [ ] Define project goals

## Architecture
- [ ] Define architecture decisions

## Status
Created: {date.today().isoformat()}
"""
    spec_path = workspace_path / "openspec" / "project.md"
    if not dry_run:
        spec_path.write_text(content, encoding="utf-8")


def create_claude_md(workspace_path: Path, name: str, description: str = "",
                     domain: str = "personal", dry_run: bool = False) -> None:
    """Create CLAUDE.md from template or generate default."""
    template_path = TEMPLATES_DIR / "workspace-CLAUDE.md"

    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        content = content.replace("[PROJECT_NAME]", name)
        # Add metadata section
        meta = f"\n## Metadata\n- Domain: {domain}\n- Created: {date.today().isoformat()}\n"
        if description:
            meta += f"- Description: {description}\n"
        content += meta
    else:
        # Generate from scratch
        desc_line = description if description else "Describe the project goals and context here."
        content = f"""# {name} — Workspace

## About
{desc_line}

## Metadata
- Domain: {domain}
- Created: {date.today().isoformat()}

## Conventions
- List coding conventions, naming patterns, or project-specific rules here

## Key Files
- List important files and their purposes here
"""

    claude_path = workspace_path / "CLAUDE.md"
    if not dry_run:
        claude_path.write_text(content, encoding="utf-8")


def create_gitignore(workspace_path: Path, dry_run: bool = False) -> None:
    """Create .gitignore with standard entries."""
    content = """.claude-memory/
__pycache__/
*.pyc
.env
node_modules/
"""
    gitignore_path = workspace_path / ".gitignore"
    if not dry_run:
        gitignore_path.write_text(content, encoding="utf-8")


def init_memory_db(workspace_path: Path, dry_run: bool = False) -> bool:
    """Initialize memory.db via init_db.py. Returns True on success."""
    db_path = workspace_path / ".claude-memory" / "memory.db"
    init_script = SCRIPTS_DIR / "init_db.py"

    if dry_run:
        return True

    if not init_script.exists():
        print(yellow(f"  Warning: init_db.py not found at {init_script}"))
        return False

    # Import and call directly (same process, no subprocess needed)
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from init_db import init_db
        init_db(str(db_path))
        return True
    except Exception as exc:
        print(yellow(f"  Warning: memory.db init failed: {exc}"))
        return False
    finally:
        sys.path.pop(0)


def init_git_repo(workspace_path: Path, name: str, dry_run: bool = False) -> bool:
    """Initialize git repo with initial commit. Returns True on success."""
    if dry_run:
        return True

    if not tool_available("git"):
        print(yellow("  Warning: git not found -- skipping git init"))
        return False

    result = run_cmd(["git", "init"], cwd=workspace_path)
    if result.returncode != 0:
        print(yellow(f"  Warning: git init failed: {result.stderr.strip()}"))
        return False

    run_cmd(["git", "add", "-A"], cwd=workspace_path)
    result = run_cmd(
        ["git", "commit", "-m", f"Initialize workspace: {name}"],
        cwd=workspace_path,
    )
    if result.returncode != 0:
        print(yellow(f"  Warning: git commit failed: {result.stderr.strip()}"))
        return False

    return True


def create_github_repo(workspace_path: Path, name: str, dry_run: bool = False) -> str:
    """Create a private GitHub repo. Returns 'owner/name' or empty string."""
    if dry_run:
        return "<owner>/" + name

    if not tool_available("gh"):
        print(yellow("  Warning: gh CLI not found -- skipping GitHub repo creation"))
        return ""

    # Check authentication
    auth_check = run_cmd(["gh", "auth", "status"])
    if auth_check.returncode != 0:
        print(yellow("  Warning: gh not authenticated -- skipping GitHub repo creation"))
        return ""

    result = run_cmd(
        ["gh", "repo", "create", name, "--private", "--source", ".", "--push"],
        cwd=workspace_path,
    )
    if result.returncode != 0:
        print(yellow(f"  Warning: GitHub repo creation failed: {result.stderr.strip()}"))
        return ""

    # Get owner
    user_result = run_cmd(["gh", "api", "user", "--jq", ".login"])
    owner = user_result.stdout.strip() if user_result.returncode == 0 else ""
    repo_slug = f"{owner}/{name}" if owner else name

    return repo_slug


def register_workspace(name: str, path: Path, domain: str = "personal",
                       repo: str = "", dry_run: bool = False) -> bool:
    """Add workspace entry to workspaces.json. Returns True on success."""
    registry_path = resolve_workspaces_json()

    if dry_run:
        return True

    registry = safe_read_json(registry_path, {"owner": "", "workspace_root": "", "workspaces": []})

    # Check for duplicate
    for ws in registry.get("workspaces", []):
        if ws.get("id") == name:
            print(yellow(f"  Warning: workspace '{name}' already in registry -- skipping"))
            return False

    entry = {
        "id": name,
        "path": str(path),
        "repo": repo,
        "domain": domain,
        "deploy": "all",
        "created": date.today().isoformat(),
    }
    registry.setdefault("workspaces", []).append(entry)
    safe_write_json(registry_path, registry)
    return True


# ── Interactive Prompts ──────────────────────────────────────────────────────

def prompt_name() -> str:
    """Ask for workspace name interactively."""
    while True:
        name = input(f"\n{bold('Workspace name')} (kebab-case): ").strip()
        try:
            return validate_name(name)
        except ValueError as exc:
            print(red(f"  {exc}"))


def prompt_domain() -> str:
    """Ask for domain interactively."""
    while True:
        domain = input(f"{bold('Domain')} [work/personal/hybrid] (default: personal): ").strip()
        if not domain:
            return "personal"
        try:
            return validate_domain(domain)
        except ValueError as exc:
            print(red(f"  {exc}"))


def prompt_description() -> str:
    """Ask for optional description."""
    return input(f"{bold('Description')} (optional): ").strip()


def prompt_github() -> bool:
    """Ask whether to create GitHub repo."""
    answer = input(f"{bold('Create GitHub repo?')} [y/N]: ").strip().lower()
    return answer in ("y", "yes")


# ── Main Orchestration ───────────────────────────────────────────────────────

def create_workspace(
    name: str,
    domain: str = "personal",
    description: str = "",
    create_repo: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Create a complete workspace. Returns a summary dict.

    This function is importable so other tools (e.g. /spec) can call it
    programmatically.
    """
    # Validate inputs
    name = validate_name(name)
    domain = validate_domain(domain)

    workspace_root = resolve_workspace_root()
    workspace_path = workspace_root / name

    # Check if workspace already exists
    if workspace_path.exists() and any(workspace_path.iterdir()):
        raise FileExistsError(f"Workspace directory already exists and is not empty: {workspace_path}")

    summary = {
        "name": name,
        "path": str(workspace_path),
        "domain": domain,
        "description": description,
        "dry_run": dry_run,
        "git_initialized": False,
        "github_repo": "",
        "memory_initialized": False,
        "registered": False,
    }

    action = "Would create" if dry_run else "Creating"
    print(f"\n{cyan(action + ' workspace:')} {bold(name)}")
    print(f"  Path: {dim(str(workspace_path))}")
    if dry_run:
        print(f"  {yellow('[DRY RUN -- no changes will be made]')}")

    # 1. Directory structure
    print(f"\n  {dim('Creating directories...')}")
    create_directory_structure(workspace_path, dry_run)

    # 2. Knowledge INDEX.md
    print(f"  {dim('Creating knowledge index...')}")
    create_knowledge_index(workspace_path, name, dry_run)

    # 3. OpenSpec project.md
    print(f"  {dim('Creating openspec project...')}")
    create_openspec_project(workspace_path, name, description, dry_run)

    # 4. CLAUDE.md from template
    print(f"  {dim('Creating CLAUDE.md...')}")
    create_claude_md(workspace_path, name, description, domain, dry_run)

    # 5. .gitignore
    print(f"  {dim('Creating .gitignore...')}")
    create_gitignore(workspace_path, dry_run)

    # 5b. Copy .claude/rules/ and .claude/hooks/ from templates
    print(f"  {dim('Deploying rules and hooks...')}")
    if not dry_run:
        import shutil
        for subdir in ("rules", "hooks"):
            src = TEMPLATES_DIR / ".claude" / subdir
            dst = workspace_path / ".claude" / subdir
            if src.exists():
                for f in src.iterdir():
                    if f.is_file():
                        shutil.copy2(str(f), str(dst / f.name))

    # 6. Memory DB
    print(f"  {dim('Initializing memory.db...')}")
    summary["memory_initialized"] = init_memory_db(workspace_path, dry_run)

    # 7. Git init
    print(f"  {dim('Initializing git...')}")
    summary["git_initialized"] = init_git_repo(workspace_path, name, dry_run)

    # 8. GitHub repo (optional)
    if create_repo:
        print(f"  {dim('Creating GitHub repo...')}")
        summary["github_repo"] = create_github_repo(workspace_path, name, dry_run)
    else:
        # Check config for auto_create_github
        config = safe_read_json(CONFIG_FILE)
        if config.get("auto_create_github", False):
            print(f"  {dim('Creating GitHub repo (auto_create_github=true)...')}")
            summary["github_repo"] = create_github_repo(workspace_path, name, dry_run)

    # 9. Register in workspaces.json
    print(f"  {dim('Registering workspace...')}")
    summary["registered"] = register_workspace(
        name, workspace_path, domain, summary["github_repo"], dry_run
    )

    return summary


def print_summary(summary: dict) -> None:
    """Print a formatted summary of workspace creation."""
    check = green(SYM_CHECK) if not summary["dry_run"] else yellow(SYM_CIRCLE)

    print(f"\n{check} {bold('Workspace created:')} {summary['name']}")
    print(f"  Path: {summary['path']}")

    if summary["github_repo"]:
        print(f"  GitHub: {summary['github_repo']} (private)")
    elif summary["dry_run"]:
        print(f"  GitHub: {dim('(dry run)')}")

    if summary["memory_initialized"]:
        print(f"  Memory: {green('initialized')}")
    else:
        print(f"  Memory: {yellow('skipped')}")

    if summary["git_initialized"]:
        print(f"  Git: {green('initialized')}")
    else:
        print(f"  Git: {yellow('skipped')}")

    print(f"  Knowledge: {green('ready')}")
    print(f"  OpenSpec: {green('ready')}")

    if summary["registered"]:
        print(f"  Registry: {green('registered')}")

    # Auto-create NotebookLM notebook if skill is available
    nb_status = _try_notebooklm_setup(summary)
    if nb_status:
        print(f"  NotebookLM: {green(nb_status)}")

    print(f"\n  {bold('Next:')} cd \"{summary['path']}\" && claude")
    print(f"  Then: /spec to start planning\n")


def _try_notebooklm_setup(summary: dict) -> str | None:
    """Try to create a NotebookLM notebook and sync workspace. Non-fatal."""
    if summary.get("dry_run"):
        return "would create notebook (dry run)"
    try:
        # Check if notebooklm-py is available
        result = subprocess.run(
            [sys.executable, "-m", "notebooklm", "--version"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return None  # not installed, skip silently

        # Check if authenticated
        result = subprocess.run(
            [sys.executable, "-m", "notebooklm", "auth", "check"],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if not result.stdout or "fail" in result.stdout.lower():
            return None  # not authenticated or unreadable output, skip silently

        # Create notebook
        name = summary.get("name", "workspace")
        result = subprocess.run(
            [sys.executable, "-m", "notebooklm", "create", name],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.returncode == 0 and result.stdout.strip():
            line = result.stdout.strip()
            if ":" in line:
                parts = line.split(":", 1)[1].strip()
                nb_id = parts.split(" - ")[0].strip() if " - " in parts else parts
                # Save notebook ID
                id_file = Path(summary["path"]) / ".notebooklm-id"
                id_file.write_text(nb_id, encoding="utf-8")
                return f"notebook created ({nb_id[:8]}...)"

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


# ── CLI Entry Point ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a new clawd-lobster workspace with memory, git, and optional GitHub repo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s                                        Interactive mode
  %(prog)s --name my-api --domain work             Non-interactive
  %(prog)s --name my-api --repo                    With GitHub repo
  %(prog)s --name my-api --dry-run                 Preview only
""",
    )
    parser.add_argument("--name", "-n", help="Workspace name (kebab-case)")
    parser.add_argument("--domain", "-d", choices=VALID_DOMAINS, help="Domain: work, personal, or hybrid")
    parser.add_argument("--description", help="Short project description")
    parser.add_argument("--repo", action="store_true", help="Create a private GitHub repo")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    print(f"\n{bold('clawd-lobster workspace creator')}")
    print(dim("-" * 40))

    try:
        # Resolve arguments — prompt interactively if not provided
        name = args.name
        if not name:
            name = prompt_name()
        else:
            name = validate_name(name)

        domain = args.domain
        if not domain:
            if args.name:
                # Non-interactive mode with --name but no --domain: default
                domain = "personal"
            else:
                domain = prompt_domain()

        description = args.description or ""
        if not description and not args.name:
            description = prompt_description()

        create_repo = args.repo
        if not create_repo and not args.name:
            create_repo = prompt_github()

        # Create the workspace
        summary = create_workspace(
            name=name,
            domain=domain,
            description=description,
            create_repo=create_repo,
            dry_run=args.dry_run,
        )

        print_summary(summary)
        return 0

    except FileExistsError as exc:
        print(f"\n{red('Error:')} {exc}")
        return 1
    except ValueError as exc:
        print(f"\n{red('Error:')} {exc}")
        return 1
    except KeyboardInterrupt:
        print(f"\n{yellow('Cancelled.')}")
        return 130


if __name__ == "__main__":
    sys.exit(main())
