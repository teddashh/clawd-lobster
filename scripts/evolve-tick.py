"""
Evolve Tick — cron entrypoint for system-level learning and knowledge consolidation.

NOT for building features (that's /spec:blitz). Evolve is about getting SMARTER:
  1. Reviews recently completed work across all workspaces
  2. Extracts reusable patterns → learned skills
  3. Consolidates knowledge (salience decay, pruning)
  4. Syncs learnings to Hub via git push

Usage:
  python scripts/evolve-tick.py                  # normal run
  python scripts/evolve-tick.py --dry-run        # scan only, don't write
  python scripts/evolve-tick.py --force          # ignore blitz gate
"""
import json
import os
import platform
import re
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Architecture Note:
#
# Building (workspace scope) = /spec → blitz → execute TODOs → push code
#   One machine does it. Spec coordinates.
#
# Evolving (system scope) = review completed work → learn patterns → share
#   Every machine does it. Knowledge syncs via git.
#
# Blitz Gate: If a workspace is mid-blitz, skip it entirely.
# ---------------------------------------------------------------------------

CLAUDE_TIMEOUT = 120  # seconds for pattern extraction (shorter than blitz)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_workspaces() -> list:
    ws_file = _repo_root() / "workspaces.json"
    if not ws_file.exists():
        return []
    try:
        data = json.loads(ws_file.read_text(encoding="utf-8"))
        return data.get("workspaces", [])
    except (json.JSONDecodeError, KeyError):
        return []


def _find_memory_dbs(workspaces: list) -> list:
    """Returns list of (workspace_name, db_path, workspace_path) tuples."""
    results = []
    for ws in workspaces:
        if isinstance(ws, str):
            ws_path = Path(ws)
            ws_name = ws_path.name
        elif isinstance(ws, dict):
            ws_path = Path(ws.get("path", ""))
            ws_name = ws.get("id", ws.get("name", ws_path.name))
        else:
            continue
        if not ws_path.is_absolute():
            continue
        db_path = ws_path / ".claude-memory" / "memory.db"
        if db_path.exists():
            results.append((ws_name, db_path, ws_path))
    return results


def _get_machine_id() -> str:
    return platform.node() or "unknown"


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_blitzing(workspace_path: str) -> bool:
    """Check if workspace is in blitz mode (/spec is executing tasks)."""
    return (Path(workspace_path) / ".blitz-active").exists()


# ---------------------------------------------------------------------------
# Phase 1: Scan recently completed work
# ---------------------------------------------------------------------------

def scan_completed_tasks(db_list: list) -> list:
    """Find tasks completed since last evolve run, across all workspaces."""
    completed = []
    for ws_name, db_path, ws_path in db_list:
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row

            # Check for todo_items table
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]

            if "todo_items" in tables:
                rows = conn.execute(
                    "SELECT * FROM todo_items WHERE status = 'approved' "
                    "ORDER BY updated_at DESC LIMIT 20"
                ).fetchall()
                for row in rows:
                    item = dict(row)
                    item["_ws_name"] = ws_name
                    item["_ws_path"] = str(ws_path)
                    item["_db_path"] = str(db_path)
                    completed.append(item)

            conn.close()
        except sqlite3.Error:
            continue
    return completed


def scan_recent_actions(db_list: list) -> list:
    """Find recent significant actions (commits, reviews, task completions)."""
    actions = []
    for ws_name, db_path, ws_path in db_list:
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row

            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]

            if "action_log" in tables:
                rows = conn.execute(
                    "SELECT * FROM action_log "
                    "WHERE action IN ('TASK_DONE', 'COMMIT', 'REVIEW_OK', 'BLITZ_COMPLETE') "
                    "ORDER BY timestamp DESC LIMIT 20"
                ).fetchall()
                for row in rows:
                    item = dict(row)
                    item["_ws_name"] = ws_name
                    actions.append(item)

            conn.close()
        except sqlite3.Error:
            continue
    return actions


def scan_existing_skills(db_list: list) -> list:
    """Get current learned skills to avoid duplicates."""
    skills = []
    for ws_name, db_path, ws_path in db_list:
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row

            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]

            if "learned_skills" in tables:
                rows = conn.execute(
                    "SELECT name, trigger_condition, category FROM learned_skills"
                ).fetchall()
                for row in rows:
                    skills.append(dict(row))

            conn.close()
        except sqlite3.Error:
            continue
    return skills


# ---------------------------------------------------------------------------
# Phase 2: Extract learnable patterns via Claude
# ---------------------------------------------------------------------------

def extract_patterns(completed_tasks: list, recent_actions: list,
                     existing_skills: list, db_list: list, dry_run: bool = False) -> int:
    """
    Use Claude to review completed work and extract reusable patterns.
    Returns number of patterns learned.
    """
    if not completed_tasks and not recent_actions:
        print("[evolve] No recent completed work to learn from.")
        return 0

    # Build context for Claude
    task_summary = "\n".join(
        f"- [{t.get('_ws_name')}] {t.get('title', '?')}: {t.get('description', '')[:100]}"
        for t in completed_tasks[:10]
    )

    action_summary = "\n".join(
        f"- [{a.get('_ws_name', '?')}] {a.get('action')}: {a.get('target', '')} — {a.get('note', '')[:80]}"
        for a in recent_actions[:10]
    )

    existing_names = ", ".join(s.get("name", "?") for s in existing_skills[:20]) or "(none)"

    prompt = (
        "You are reviewing recently completed work to extract reusable patterns.\n\n"
        "## Recently Completed Tasks\n"
        f"{task_summary or '(none)'}\n\n"
        "## Recent Actions\n"
        f"{action_summary or '(none)'}\n\n"
        "## Already Known Skills\n"
        f"{existing_names}\n\n"
        "## Instructions\n"
        "1. Review the completed tasks and actions above.\n"
        "2. Identify any REUSABLE patterns that could help in future work.\n"
        "3. For each pattern found, call memory_learn_skill() with:\n"
        "   - name: short descriptive name\n"
        "   - trigger_condition: when to use this pattern\n"
        "   - approach: step-by-step how to apply it\n"
        "   - tools_used: which tools are involved\n"
        "   - category: general category\n"
        "4. Skip patterns that duplicate already known skills.\n"
        "5. Also call memory_record_knowledge() for any non-obvious insights.\n"
        "6. If nothing worth learning, just say 'No new patterns found.'\n\n"
        "Be selective — only extract patterns that are genuinely reusable, not one-off fixes."
    )

    if dry_run:
        print(f"[evolve] Would ask Claude to review {len(completed_tasks)} tasks "
              f"and {len(recent_actions)} actions")
        print(f"[evolve] Prompt preview:\n{prompt[:300]}...")
        return 0

    # Find a workspace to run Claude in (prefer one with completed tasks)
    cwd = None
    if completed_tasks:
        cwd = completed_tasks[0].get("_ws_path")
    elif db_list:
        cwd = str(db_list[0][2])

    if not cwd:
        print("[evolve] No workspace available to run Claude in.")
        return 0

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True,
            timeout=CLAUDE_TIMEOUT,
            cwd=cwd,
        )
        output = result.stdout.strip() if result.stdout else ""

        if result.returncode != 0:
            print(f"[evolve] Claude returned error: {result.stderr[:200]}")
            return 0

        # Count how many skills were learned (heuristic: count memory_learn_skill mentions)
        learned = output.lower().count("memory_learn_skill")
        knowledge = output.lower().count("memory_record_knowledge")

        if learned > 0 or knowledge > 0:
            print(f"[evolve] Learned {learned} skill(s), recorded {knowledge} knowledge item(s)")
        else:
            print("[evolve] No new patterns found this cycle.")

        return learned

    except subprocess.TimeoutExpired:
        print("[evolve] Claude timed out during pattern extraction.")
        return 0
    except FileNotFoundError:
        print("[evolve] claude CLI not found in PATH.")
        return 0


# ---------------------------------------------------------------------------
# Phase 3: Consolidate knowledge (salience decay)
# ---------------------------------------------------------------------------

def run_salience_decay(db_list: list, dry_run: bool = False) -> int:
    """
    Apply salience decay to old, untouched memories.
    -5% per day for items not accessed in 30+ days.
    Returns number of items decayed.
    """
    decayed_total = 0
    for ws_name, db_path, ws_path in db_list:
        try:
            conn = sqlite3.connect(str(db_path))

            # Check which tables have salience column
            for table in ["decisions", "resolved", "open_questions", "knowledge_items"]:
                try:
                    cursor = conn.execute(
                        f"SELECT COUNT(*) FROM {table} WHERE salience > 0.01 "
                        f"AND access_count = 0 "
                        f"AND date(created_at) < date('now', '-30 days')"
                    )
                    count = cursor.fetchone()[0]
                    if count > 0:
                        if not dry_run:
                            conn.execute(
                                f"UPDATE {table} SET salience = MAX(0.01, salience * 0.95) "
                                f"WHERE salience > 0.01 "
                                f"AND access_count = 0 "
                                f"AND date(created_at) < date('now', '-30 days')"
                            )
                        decayed_total += count
                except sqlite3.OperationalError:
                    continue  # table or column doesn't exist

            if not dry_run:
                conn.commit()
            conn.close()
        except sqlite3.Error:
            continue

    if decayed_total > 0:
        action = "Would decay" if dry_run else "Decayed"
        print(f"[evolve] {action} salience on {decayed_total} stale item(s)")
    return decayed_total


# ---------------------------------------------------------------------------
# Phase 4: Sync learnings to Hub
# ---------------------------------------------------------------------------

def sync_to_hub(dry_run: bool = False):
    """Push knowledge changes to Hub via git."""
    repo = _repo_root()
    knowledge_dir = repo / "knowledge"

    if not knowledge_dir.exists():
        return

    try:
        # Check for changes in knowledge/
        result = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain", "knowledge/"],
            capture_output=True, text=True, timeout=10,
        )
        if not result.stdout.strip():
            return  # nothing to push

        if dry_run:
            print(f"[evolve] Would sync {len(result.stdout.strip().splitlines())} knowledge changes to Hub")
            return

        subprocess.run(
            ["git", "-C", str(repo), "add", "knowledge/"],
            capture_output=True, timeout=30,
        )
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-m",
             f"evolve: knowledge sync from {_get_machine_id()} ({_now()[:10]})"],
            capture_output=True, timeout=30,
        )
        result = subprocess.run(
            ["git", "-C", str(repo), "push"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            print("[evolve] Knowledge synced to Hub.")
        else:
            print(f"[evolve] Push failed (non-fatal): {result.stderr[:100]}")

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # non-fatal


# ---------------------------------------------------------------------------
# Phase 5: Log evolve cycle
# ---------------------------------------------------------------------------

def log_evolve_cycle(db_list: list, patterns_learned: int, items_decayed: int):
    """Record this evolve cycle in action_log."""
    for ws_name, db_path, ws_path in db_list[:1]:  # log to first workspace
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute(
                "INSERT INTO action_log (id, timestamp, machine_id, action, target, note, tokens, workspace) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (_new_id(), _now(), _get_machine_id(), "EVOLVE_CYCLE",
                 "system", f"learned={patterns_learned}, decayed={items_decayed}",
                 0, ws_name),
            )
            conn.commit()
            conn.close()
        except sqlite3.Error:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    print(f"[evolve] {_now()} — starting evolution cycle")

    # 1. Load workspaces
    workspaces = _load_workspaces()
    if not workspaces:
        print("[evolve] No workspaces configured.")
        return

    # 2. Find memory databases
    db_list = _find_memory_dbs(workspaces)
    if not db_list:
        print("[evolve] No memory.db files found.")
        return

    # 3. Blitz gate — skip workspaces in blitz mode
    if not force:
        filtered = []
        for ws_name, db_path, ws_path in db_list:
            if is_blitzing(str(ws_path)):
                print(f"  [skip] {ws_name}: blitz mode active")
            else:
                filtered.append((ws_name, db_path, ws_path))
        db_list = filtered
        if not db_list:
            print("[evolve] All workspaces in blitz mode. Skipping.")
            return

    print(f"[evolve] Scanning {len(db_list)} workspace(s)...")

    # 4. Scan completed work
    completed = scan_completed_tasks(db_list)
    actions = scan_recent_actions(db_list)
    existing = scan_existing_skills(db_list)

    print(f"[evolve] Found: {len(completed)} completed tasks, "
          f"{len(actions)} recent actions, {len(existing)} existing skills")

    # 5. Extract patterns (Claude reviews completed work)
    patterns = extract_patterns(completed, actions, existing, db_list, dry_run)

    # 6. Salience decay
    decayed = run_salience_decay(db_list, dry_run)

    # 7. Sync to Hub
    sync_to_hub(dry_run)

    # 8. Log the cycle
    if not dry_run:
        log_evolve_cycle(db_list, patterns, decayed)

    print(f"[evolve] Cycle complete: {patterns} patterns learned, {decayed} items decayed")


if __name__ == "__main__":
    main()
