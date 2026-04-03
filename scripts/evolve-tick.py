"""
Evolve Tick — cron entrypoint for auto-processing TODO items.

Runs periodically (default: every 2 hours). Each tick:
  1. Scans workspace memory.db files for pending TODOs
  2. Picks the highest-priority pending TODO (priority ASC, oldest first)
  3. Opens a git worktree for isolated work
  4. Runs Claude Code in print mode to complete the TODO
  5. Updates TODO status based on result

Usage:
  python scripts/evolve-tick.py                  # normal run
  python scripts/evolve-tick.py --dry-run        # scan only, don't execute
  python scripts/evolve-tick.py --force          # ignore blitz gate
"""
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TIMEOUT_SECONDS = 300  # 5 minutes per TODO
WORKTREE_PREFIX = "evolve-"

# ---------------------------------------------------------------------------
# Blitz Gate: When /spec is running a blitz (full-speed task execution),
# evolve-tick must not interfere. The .blitz-active marker file is created
# by /spec:blitz and removed when blitz completes. This prevents style
# inconsistency from evolve modifying code mid-build.
# ---------------------------------------------------------------------------


def is_blitzing(workspace_path: str) -> bool:
    """Check if workspace is in blitz mode (spec is executing tasks)."""
    marker = Path(workspace_path) / ".blitz-active"
    return marker.exists()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _repo_root() -> Path:
    """Find the clawd-lobster repo root (where this script lives under scripts/)."""
    return Path(__file__).resolve().parent.parent


def _load_workspaces() -> list:
    """Load workspace list from workspaces.json at repo root."""
    ws_file = _repo_root() / "workspaces.json"
    if not ws_file.exists():
        print(f"[WARN] workspaces.json not found at {ws_file}")
        return []
    try:
        data = json.loads(ws_file.read_text(encoding="utf-8"))
        return data.get("workspaces", [])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[WARN] Failed to parse workspaces.json: {e}")
        return []


def _find_memory_dbs(workspaces: list) -> list:
    """
    Find all memory.db files across workspaces.
    Each workspace entry may have a 'path' key pointing to the workspace root.
    Returns list of (workspace_name, db_path, workspace_path) tuples.
    """
    results = []
    for ws in workspaces:
        if isinstance(ws, str):
            ws_path = Path(ws)
            ws_name = ws_path.name
        elif isinstance(ws, dict):
            ws_path = Path(ws.get("path", ""))
            ws_name = ws.get("name", ws_path.name)
        else:
            continue

        if not ws_path.is_absolute():
            continue

        db_path = ws_path / ".claude-memory" / "memory.db"
        if db_path.exists():
            results.append((ws_name, db_path, ws_path))
        else:
            print(f"[SKIP] No memory.db for workspace '{ws_name}' at {db_path}")

    return results


def _slugify(text: str, max_len: int = 40) -> str:
    """Convert text to a URL/branch-safe slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len].rstrip("-")


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _get_machine_id() -> str:
    """Get a stable machine identifier."""
    return platform.node() or "unknown"


def _worktree_dir(todo_id: str) -> Path:
    """
    Return the worktree directory path.
    Uses temp directory for cross-platform compatibility.
    """
    return Path(tempfile.gettempdir()) / f"{WORKTREE_PREFIX}{todo_id}"


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def scan_pending_todos(db_list: list) -> list:
    """
    Scan all memory.db files for pending TODOs.
    Returns list of dicts sorted by priority ASC, created_at ASC.
    """
    todos = []
    for ws_name, db_path, ws_path in db_list:
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            # Check if todos table exists
            tables = [
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='todos'"
                ).fetchall()
            ]
            if "todos" not in tables:
                conn.close()
                continue

            rows = conn.execute(
                "SELECT * FROM todos WHERE status = 'pending' "
                "ORDER BY priority ASC, created_at ASC"
            ).fetchall()
            for row in rows:
                item = dict(row)
                item["_ws_name"] = ws_name
                item["_ws_path"] = str(ws_path)
                item["_db_path"] = str(db_path)
                todos.append(item)
            conn.close()
        except sqlite3.Error as e:
            print(f"[WARN] Error reading {db_path}: {e}")
            continue

    # Global sort: priority ASC, created_at ASC
    todos.sort(key=lambda t: (t.get("priority", 2), t.get("created_at", "")))
    return todos


def create_worktree(ws_path: str, todo_id: str, slug: str) -> tuple:
    """
    Create a git worktree for the TODO.
    Returns (worktree_path, branch_name) or (None, error_msg).
    """
    branch_name = f"evolve/{todo_id}-{slug}"
    wt_path = _worktree_dir(todo_id)

    # Clean up stale worktree if it exists
    if wt_path.exists():
        try:
            subprocess.run(
                ["git", "-C", ws_path, "worktree", "remove", str(wt_path), "--force"],
                capture_output=True,
                timeout=30,
            )
        except Exception:
            # Try manual cleanup
            try:
                shutil.rmtree(str(wt_path), ignore_errors=True)
            except Exception:
                pass

    # Check if branch already exists
    result = subprocess.run(
        ["git", "-C", ws_path, "branch", "--list", branch_name],
        capture_output=True,
        text=True,
        timeout=30,
    )
    branch_exists = bool(result.stdout.strip())

    try:
        if branch_exists:
            # Use existing branch
            subprocess.run(
                [
                    "git",
                    "-C",
                    ws_path,
                    "worktree",
                    "add",
                    str(wt_path),
                    branch_name,
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
        else:
            # Create new branch
            subprocess.run(
                [
                    "git",
                    "-C",
                    ws_path,
                    "worktree",
                    "add",
                    str(wt_path),
                    "-b",
                    branch_name,
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
        return (str(wt_path), branch_name)
    except subprocess.CalledProcessError as e:
        return (None, f"git worktree failed: {e.stderr.strip()}")
    except subprocess.TimeoutExpired:
        return (None, "git worktree timed out")


def run_claude(worktree_path: str, todo: dict) -> tuple:
    """
    Run Claude Code in print mode to complete the TODO.
    Returns (made_commits: bool, output: str).
    """
    title = todo.get("title", "")
    description = todo.get("description", "")

    prompt = (
        "Complete this TODO item. Read the codebase first, understand the context, "
        "then implement.\n\n"
        f"TODO: {title}\n"
        f"Description: {description}\n\n"
        "Rules:\n"
        "- Make minimal, focused changes\n"
        "- Write tests if applicable\n"
        "- Commit your changes with a clear message"
    )

    # Get commit count before
    try:
        before = subprocess.run(
            ["git", "-C", worktree_path, "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        count_before = int(before.stdout.strip()) if before.returncode == 0 else 0
    except Exception:
        count_before = 0

    # Run Claude Code
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--cwd", worktree_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        output = result.stdout[:2000] if result.stdout else ""
        if result.returncode != 0:
            error = result.stderr[:500] if result.stderr else "unknown error"
            return (False, f"Claude exited with code {result.returncode}: {error}")
    except subprocess.TimeoutExpired:
        return (False, "Claude Code timed out after 5 minutes")
    except FileNotFoundError:
        return (False, "claude CLI not found in PATH")

    # Get commit count after
    try:
        after = subprocess.run(
            ["git", "-C", worktree_path, "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        count_after = int(after.stdout.strip()) if after.returncode == 0 else 0
    except Exception:
        count_after = 0

    made_commits = count_after > count_before
    return (made_commits, output)


def update_todo_status(db_path: str, todo_id: str, status: str, branch: str = "", note: str = ""):
    """Update a TODO's status in the database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            "UPDATE todos SET status = ?, branch = ?, note = ?, updated_at = ? WHERE id = ?",
            (status, branch, note[:1000], datetime.utcnow().isoformat(), todo_id),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to update todo {todo_id}: {e}")


def log_action(db_path: str, action: str, target: str = "", note: str = "", workspace: str = ""):
    """Log an action to the action_log table."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO action_log (id, machine_id, action, target, note, tokens, workspace) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (_new_id(), _get_machine_id(), action, target, note[:1000], 0, workspace),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[WARN] Failed to log action: {e}")


def cleanup_worktree(ws_path: str, todo_id: str):
    """Remove worktree (best-effort, non-fatal)."""
    wt_path = _worktree_dir(todo_id)
    if not wt_path.exists():
        return
    try:
        subprocess.run(
            ["git", "-C", ws_path, "worktree", "remove", str(wt_path), "--force"],
            capture_output=True,
            timeout=30,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    print(f"[evolve-tick] {datetime.utcnow().isoformat()} — scanning for pending TODOs")

    # 1. Load workspaces
    workspaces = _load_workspaces()
    if not workspaces:
        print("[evolve-tick] No workspaces configured. Nothing to do.")
        return

    # 2. Find memory.db files
    db_list = _find_memory_dbs(workspaces)
    if not db_list:
        print("[evolve-tick] No memory.db files found. Nothing to do.")
        return

    # 3. Scan for pending TODOs
    todos = scan_pending_todos(db_list)
    if not todos:
        print("[evolve-tick] No pending TODOs found. All clear.")
        return

    # 3.5. Blitz gate — skip workspaces where /spec:blitz is active
    if not force:
        filtered = []
        skipped_ws = set()
        for t in todos:
            ws_p = t["_ws_path"]
            if is_blitzing(ws_p):
                if ws_p not in skipped_ws:
                    print(f"\u23ed Skipping {t['_ws_name']}: blitz mode active")
                    skipped_ws.add(ws_p)
            else:
                filtered.append(t)
        todos = filtered
        if not todos:
            print("[evolve-tick] All workspaces in blitz mode. Nothing to do.")
            return

    print(f"[evolve-tick] Found {len(todos)} pending TODO(s)")
    for i, t in enumerate(todos[:5]):
        print(f"  [{i+1}] P{t.get('priority', '?')} — {t.get('title', '?')} ({t['_ws_name']})")

    if dry_run:
        print("[evolve-tick] Dry run — not processing.")
        return

    # 4. Pick the top one
    todo = todos[0]
    todo_id = todo["id"]
    title = todo.get("title", "untitled")
    ws_path = todo["_ws_path"]
    ws_name = todo["_ws_name"]
    db_path = todo["_db_path"]

    print(f"\n[evolve-tick] Processing: {title} (id={todo_id}, workspace={ws_name})")

    # 5. Create worktree
    slug = _slugify(title)
    wt_result = create_worktree(ws_path, todo_id, slug)
    worktree_path, branch_or_error = wt_result

    if worktree_path is None:
        print(f"[evolve-tick] Worktree failed: {branch_or_error}")
        update_todo_status(db_path, todo_id, "in_progress", note=f"worktree error: {branch_or_error}")
        log_action(db_path, "EVOLVE_FAIL", target=todo_id, note=branch_or_error, workspace=ws_name)
        return

    branch_name = branch_or_error
    print(f"[evolve-tick] Worktree ready: {worktree_path} (branch: {branch_name})")

    # 6. Run Claude
    log_action(db_path, "EVOLVE_START", target=todo_id, note=title, workspace=ws_name)
    made_commits, output = run_claude(worktree_path, todo)

    # 7. Update status
    if made_commits:
        print(f"[evolve-tick] Claude made commits. Staging TODO as complete.")
        update_todo_status(db_path, todo_id, "staged", branch=branch_name, note=output[:500])
        log_action(
            db_path,
            "EVOLVE_STAGED",
            target=todo_id,
            note=f"branch={branch_name}",
            workspace=ws_name,
        )
    else:
        print(f"[evolve-tick] No commits made. Marking as in_progress.")
        update_todo_status(db_path, todo_id, "in_progress", note=output[:500])
        log_action(
            db_path,
            "EVOLVE_NOCOMMIT",
            target=todo_id,
            note=output[:200],
            workspace=ws_name,
        )
        # Clean up worktree on failure (no commits to keep)
        cleanup_worktree(ws_path, todo_id)

    print(f"[evolve-tick] Done.")


if __name__ == "__main__":
    main()
