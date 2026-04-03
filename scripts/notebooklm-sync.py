#!/usr/bin/env python3
"""
notebooklm-sync.py — Push all valuable content from a workspace to NotebookLM.

Scans the workspace for markdown files, specs, knowledge docs, and pushes
them as sources to the workspace's linked NotebookLM notebook.

Usage:
  python notebooklm-sync.py <workspace-path> <notebook-id>
  python notebooklm-sync.py <workspace-path> <notebook-id> --dry-run
  python notebooklm-sync.py <workspace-path> <notebook-id> --full   # include code files too
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Files/dirs to SKIP (not valuable as NotebookLM sources)
SKIP_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv',
    'staging', '.claude-memory', '.codex-jobs', 'dist', 'build',
    '.next', '.nuxt', 'coverage', '.pytest_cache', '.mypy_cache',
}

SKIP_FILES = {
    '.env', '.env.local', '.env.production',
    'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock',
    'poetry.lock', 'Pipfile.lock',
}

# File patterns that ARE valuable
VALUABLE_EXTENSIONS = {
    '.md', '.txt', '.rst',           # documentation
    '.json',                          # configs (small ones)
    '.yaml', '.yml', '.toml',         # configs
}

# Extra extensions for --full mode
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx',
    '.go', '.rs', '.java', '.rb', '.php',
    '.sh', '.ps1', '.bash',
}

# Max file size to push (500KB — NotebookLM has limits)
MAX_FILE_SIZE = 500 * 1024


def scan_workspace(workspace: Path, full: bool = False) -> list[Path]:
    """Scan workspace for valuable files to push as sources."""
    extensions = VALUABLE_EXTENSIONS.copy()
    if full:
        extensions.update(CODE_EXTENSIONS)

    files = []
    for root, dirs, filenames in os.walk(workspace):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in sorted(filenames):
            if fname in SKIP_FILES:
                continue
            fpath = Path(root) / fname
            if fpath.suffix not in extensions:
                continue
            if fpath.stat().st_size > MAX_FILE_SIZE:
                continue
            if fpath.stat().st_size == 0:
                continue
            files.append(fpath)

    return files


def get_existing_sources(notebook_id: str) -> set[str]:
    """Get titles of already-added sources to avoid duplicates."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "notebooklm", "source", "list", "-n", notebook_id, "--json"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.returncode == 0 and result.stdout.strip():
            sources = json.loads(result.stdout)
            return {s.get("title", "") for s in sources if isinstance(s, dict)}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return set()


def push_source(notebook_id: str, filepath: Path, title: str) -> bool:
    """Push a file as a source to NotebookLM. Returns True on success."""
    # Non-markdown files (json/yaml/toml) fail as file uploads.
    # Wrap them in markdown so NotebookLM accepts them as text.
    if filepath.suffix in {'.json', '.yaml', '.yml', '.toml'}:
        return _push_as_markdown(notebook_id, filepath, title)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "notebooklm", "source", "add",
             str(filepath), "-n", notebook_id, "--title", title],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _push_as_markdown(notebook_id: str, filepath: Path, title: str) -> bool:
    """Wrap a config file in markdown code block and push as text."""
    import tempfile
    try:
        content = filepath.read_text(encoding="utf-8")
        md_content = f"# {title}\n\n```{filepath.suffix.lstrip('.')}\n{content}\n```\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False,
                                         encoding='utf-8') as tmp:
            tmp.write(md_content)
            tmp_path = tmp.name

        result = subprocess.run(
            [sys.executable, "-m", "notebooklm", "source", "add",
             tmp_path, "-n", notebook_id, "--title", title],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        os.unlink(tmp_path)
        return result.returncode == 0
    except Exception:
        return False


def make_title(filepath: Path, workspace: Path) -> str:
    """Generate a descriptive title from the file path."""
    rel = filepath.relative_to(workspace)
    parts = list(rel.parts)

    # Special naming for known paths
    if parts[0] == "openspec" and len(parts) > 1:
        return f"[spec] {'/'.join(parts[1:])}"
    if parts[0] == "knowledge" and len(parts) > 1:
        return f"[knowledge] {'/'.join(parts[1:])}"
    if parts[0] == "skills" and len(parts) > 1:
        return f"[skill] {'/'.join(parts[1:])}"
    if parts[-1] == "CLAUDE.md":
        return "Project Instructions (CLAUDE.md)"
    if parts[-1] == "README.md":
        return "README"
    if parts[-1] == "CHANGELOG.md":
        return "CHANGELOG"

    return str(rel)


def save_notebook_id(workspace: Path, notebook_id: str):
    """Save notebook ID to workspace for future use."""
    id_file = workspace / ".notebooklm-id"
    id_file.write_text(notebook_id.strip(), encoding="utf-8")


def load_notebook_id(workspace: Path) -> str | None:
    """Load saved notebook ID from workspace."""
    id_file = workspace / ".notebooklm-id"
    if id_file.exists():
        return id_file.read_text(encoding="utf-8").strip()
    return None


def create_notebook(workspace_name: str) -> str | None:
    """Create a new NotebookLM notebook and return its ID."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "notebooklm", "create", workspace_name],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.returncode == 0 and result.stdout.strip():
            # Parse: "Created notebook: <id> - <name>"
            line = result.stdout.strip()
            if ":" in line:
                parts = line.split(":", 1)[1].strip()
                nb_id = parts.split(" - ")[0].strip() if " - " in parts else parts.strip()
                return nb_id
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def main():
    dry_run = "--dry-run" in sys.argv
    full = "--full" in sys.argv

    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        print("Usage: python notebooklm-sync.py <workspace-path> [notebook-id] [--dry-run] [--full]")
        print("  If notebook-id is omitted, uses saved ID or creates a new notebook.")
        sys.exit(1)

    workspace = Path(sys.argv[1]).resolve()

    # Get notebook ID: from arg, from saved file, or create new
    notebook_id = None
    args_without_flags = [a for a in sys.argv[2:] if not a.startswith("--")]
    if args_without_flags:
        notebook_id = args_without_flags[0]
    else:
        notebook_id = load_notebook_id(workspace)

    if not notebook_id:
        print(f"No notebook ID found. Creating new notebook...")
        notebook_id = create_notebook(workspace.name)
        if not notebook_id:
            print("Error: Failed to create notebook. Is notebooklm-py authenticated?")
            sys.exit(1)
        print(f"Created notebook: {notebook_id}")

    # Always save the ID for next time
    if not dry_run:
        save_notebook_id(workspace, notebook_id)

    if not workspace.is_dir():
        print(f"Error: {workspace} is not a directory")
        sys.exit(1)

    print(f"Scanning: {workspace}")
    print(f"Notebook: {notebook_id}")
    print(f"Mode: {'full (includes code)' if full else 'docs only'}")
    print(f"{'DRY RUN' if dry_run else ''}")
    print()

    # Scan for files
    files = scan_workspace(workspace, full)
    print(f"Found {len(files)} valuable files:")
    for f in files:
        rel = f.relative_to(workspace)
        size = f.stat().st_size
        print(f"  {rel} ({size:,} bytes)")
    print()

    if not files:
        print("Nothing to push.")
        return

    # Check existing sources
    if not dry_run:
        existing = get_existing_sources(notebook_id)
        print(f"Already in notebook: {len(existing)} sources")
    else:
        existing = set()

    # Push each file
    pushed = 0
    skipped = 0
    failed = 0

    for filepath in files:
        title = make_title(filepath, workspace)

        if title in existing:
            print(f"  [skip] {title} (already exists)")
            skipped += 1
            continue

        if dry_run:
            print(f"  [would push] {title}")
            pushed += 1
            continue

        print(f"  [push] {title}...", end=" ", flush=True)
        if push_source(notebook_id, filepath, title):
            print("ok")
            pushed += 1
        else:
            print("FAILED")
            failed += 1

    print(f"\nDone: {pushed} pushed, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
