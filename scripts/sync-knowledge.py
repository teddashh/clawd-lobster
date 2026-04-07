#!/usr/bin/env python3
"""
sync-knowledge.py — Unified knowledge sync: Claude → Codex (AGENTS.md) + Gemini (GEMINI.md)

Generates a standardized knowledge package from Claude Code's state and
outputs it in each agent's native format. All agents enter with the same
understanding of the system, the project, and recent decisions.

Knowledge Package:
  1. System capabilities (skills, tools, memory architecture)
  2. Project context (CLAUDE.md)
  3. Recent decisions and learnings (from auto-memory)
  4. Current spec state (if any)
  5. Role definition (per target agent)

Targets:
  AGENTS.md  → Codex (project root + ~/.codex/)
  GEMINI.md  → Gemini (project root + ~/.gemini/)

Usage:
    python sync-knowledge.py                         # sync current workspace
    python sync-knowledge.py -w <workspace>          # specific workspace
    python sync-knowledge.py --target codex          # codex only
    python sync-knowledge.py --target gemini         # gemini only
    python sync-knowledge.py --dry-run               # preview

Designed to run as a cron job (every 30 minutes).
No external dependencies — stdlib only.
"""

import argparse
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

HOME = Path.home()
CLAUDE_DIR = HOME / ".claude"
CODEX_DIR = HOME / ".codex"
GEMINI_DIR = HOME / ".gemini"
REPO_DIR = Path(__file__).resolve().parent.parent

# ── Utilities ────────────────────────────────────────────────────────────────

def read_file(path: Path) -> str:
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""
    return ""


def read_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def write_file(path: Path, content: str, dry_run: bool = False) -> bool:
    existing = read_file(path)
    if existing.strip() == content.strip():
        return False
    if dry_run:
        print(f"  [DRY RUN] Would write: {path}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


# ── Knowledge Package Builder ────────────────────────────────────────────────

def build_system_knowledge() -> str:
    """Build the system capabilities section — same for all agents."""
    return """## System: Clawd-Lobster

Clawd-Lobster is a hardened skill framework for Claude Code.
~9,000 lines of code, 10 skills, 32 MCP tools. Runs on Claude subscription.

### 10 Skills
| Skill | Purpose |
|-------|---------|
| memory-server | 4-layer persistent memory (SQLite + MCP, 26 tools) |
| spec | Spec-driven development: discovery → spec → adversarial review → build → test |
| evolve | Extract reusable patterns from completed work (auto, every 2h) |
| absorb | Learn from repos, URLs, or folders |
| heartbeat | OS-native session keep-alive (Task Scheduler / cron / launchd) |
| migrate | One-time import from other AI setups |
| codex-bridge | Delegate to OpenAI Codex (worker + critic) |
| gemini-bridge | Consult Google Gemini (research + validation + debate) |
| connect-odoo | Bidirectional Odoo ERP integration (XML-RPC + MCP, 6 tools) |
| notebooklm-bridge | Google NotebookLM sync + watermark removal |

### 4-Layer Memory Architecture
| Layer | Speed | Storage | Scope |
|-------|-------|---------|-------|
| L1.5 | Instant | Claude Code native auto-memory | Session |
| L2 | ~1ms | SQLite + MCP (per-workspace) | Workspace |
| L3 | ~10ms | Markdown + Git (synced) | Cross-machine |
| L4 | ~100ms | Cloud DB (optional) | Global |

Salience engine: access +5%, reinforce +20%, 30-day decay -5%/day.
Important knowledge floats up. Noise sinks away. Automatic.

### Key Conventions
- Learnings = mistakes to avoid (memory_store type="learning")
- Skills = patterns to follow (memory_learn_skill)
- Action logging: TASK_START → SPEC → REVIEW → COMMIT → TASK_DONE
- Spec-driven: 3W1H framework, DAG order (project → proposal → design → specs → tasks)
- Never cross-read another workspace's memory
"""


def build_project_context(workspace: Path) -> str:
    """Read CLAUDE.md from workspace."""
    claude_md = read_file(workspace / "CLAUDE.md")
    if not claude_md:
        return ""

    # Strip Claude-internal sections but keep content accurate
    lines = claude_md.split("\n")
    output = []
    skip = False
    for line in lines:
        lower = line.lower().strip()
        if any(x in lower for x in ["## hooks", "## mcp servers", "## permission",
                                      "## session-memory hook", "## command-logger hook"]):
            skip = True
            continue
        if skip and line.startswith("#"):
            skip = False
        if not skip:
            output.append(line)

    return "\n## Project Context (from CLAUDE.md)\n\n" + "\n".join(output)


def build_memory_context(workspace: Path) -> str:
    """Extract key decisions and learnings from Claude auto-memory."""
    projects_dir = CLAUDE_DIR / "projects"
    if not projects_dir.exists():
        return ""

    for proj_dir in projects_dir.iterdir():
        if not proj_dir.is_dir():
            continue
        ws_parts = [p for p in workspace.parts[-2:] if len(p) > 2]
        if all(p.lower() in proj_dir.name.lower() for p in ws_parts):
            memory_dir = proj_dir / "memory"
            if memory_dir.exists():
                return _extract_memory(memory_dir)
    return ""


def _extract_memory(memory_dir: Path) -> str:
    index = read_file(memory_dir / "MEMORY.md")
    if not index:
        return ""

    lines = []
    for line in index.split("\n"):
        if not line.strip().startswith("- ["):
            continue
        lower = line.lower()
        if any(x in lower for x in ["feedback_", "project_claw", "project_agent",
                                      "reference_arp", "project_status"]):
            if "—" in line:
                desc = line.split("—", 1)[1].strip()
                lines.append(f"- {desc}")

    if not lines:
        return ""
    return "\n## Recent Decisions & Context (from Claude Memory)\n\n" + "\n".join(lines[:15])


def build_spec_state(workspace: Path) -> str:
    """Check current spec progress."""
    tasks_file = None
    changes_dir = workspace / "openspec" / "changes"
    if changes_dir.exists():
        for change_dir in sorted(changes_dir.iterdir(), reverse=True):
            tf = change_dir / "tasks.md"
            if tf.exists():
                tasks_file = tf
                break

    if not tasks_file:
        return ""

    content = read_file(tasks_file)
    total = content.count("- [ ]") + content.count("- [x]")
    done = content.count("- [x]")

    if total == 0:
        return ""

    blitz = (workspace / ".blitz-active").exists()
    status = "BLITZ IN PROGRESS" if blitz else f"{done}/{total} tasks ({done*100//total}%)"

    return f"\n## Current Spec State\n\nSpec progress: {status}\n"


def build_learned_skills(workspace: Path) -> str:
    """List learned skills."""
    skills_dir = workspace / "skills" / "learned"
    if not skills_dir.exists():
        return ""

    skills = []
    for f in skills_dir.glob("*.md"):
        content = read_file(f)
        first_line = content.split("\n")[0].strip("# ").strip() if content else f.stem
        skills.append(f"- **{f.stem}**: {first_line}")

    if not skills:
        return ""
    return "\n## Learned Skills\n\n" + "\n".join(skills)


# ── Format-specific output ───────────────────────────────────────────────────

def format_agents_md(knowledge: str, timestamp: str) -> str:
    """Format for Codex AGENTS.md."""
    header = f"""# Project Knowledge (synced from Claude Code)

> Auto-generated by `sync-knowledge.py`. Last sync: {timestamp}
> **Do not edit manually** — changes will be overwritten.
> Your role: Reviewer / Worker / Critic. Challenge assumptions. Find bugs.

---

"""
    footer = f"\n\n---\n*Synced: {timestamp} | Source: Claude Code + clawd-lobster*\n"

    content = header + knowledge + footer
    # Enforce 32 KiB limit
    if len(content.encode("utf-8")) > 32 * 1024:
        content = content[:32 * 1024 - 200] + "\n\n> **Truncated** — exceeded 32 KiB limit.\n"
    return content


def format_gemini_md(knowledge: str, timestamp: str) -> str:
    """Format for Gemini GEMINI.md."""
    header = f"""# Project Knowledge (synced from Claude Code)

> Auto-generated by `sync-knowledge.py`. Last sync: {timestamp}
> **Do not edit manually** — changes will be overwritten.
> Your role: Consultant / Validator / Researcher. Provide independent perspective.
> You are part of a three-agent system: Claude (lead), Codex (worker/critic), Gemini (you — consultant).

---

"""
    footer = f"\n\n---\n*Synced: {timestamp} | Source: Claude Code + clawd-lobster*\n"
    return header + knowledge + footer


# ── Main sync logic ─────────────────────────────────────────────────────────

def sync_workspace(workspace: Path, targets: list[str], dry_run: bool = False) -> dict:
    """Sync a workspace to all target agents."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = {"files_written": []}

    # Build unified knowledge package
    parts = [build_system_knowledge()]
    project_ctx = build_project_context(workspace)
    if project_ctx:
        parts.append(project_ctx)
    memory_ctx = build_memory_context(workspace)
    if memory_ctx:
        parts.append(memory_ctx)
    spec_state = build_spec_state(workspace)
    if spec_state:
        parts.append(spec_state)
    skills_ctx = build_learned_skills(workspace)
    if skills_ctx:
        parts.append(skills_ctx)

    knowledge = "\n".join(parts)

    # Output to each target
    if "codex" in targets:
        agents_md = format_agents_md(knowledge, timestamp)
        path = workspace / "AGENTS.md"
        if write_file(path, agents_md, dry_run):
            summary["files_written"].append(str(path))

    if "gemini" in targets:
        gemini_md = format_gemini_md(knowledge, timestamp)
        path = workspace / "GEMINI.md"
        if write_file(path, gemini_md, dry_run):
            summary["files_written"].append(str(path))

    return summary


def sync_global(targets: list[str], dry_run: bool = False) -> dict:
    """Sync global knowledge to agent config dirs."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = {"files_written": []}
    knowledge = build_system_knowledge()

    if "codex" in targets:
        content = format_agents_md(knowledge, timestamp)
        path = CODEX_DIR / "AGENTS.md"
        if write_file(path, content, dry_run):
            summary["files_written"].append(str(path))

    if "gemini" in targets:
        content = format_gemini_md(knowledge, timestamp)
        path = GEMINI_DIR / "GEMINI.md"
        if write_file(path, content, dry_run):
            summary["files_written"].append(str(path))

    return summary


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Sync Claude Code knowledge → Codex (AGENTS.md) + Gemini (GEMINI.md)",
    )
    parser.add_argument("-w", "--workspace", help="Workspace path to sync")
    parser.add_argument("-g", "--global-only", dest="global_only", action="store_true")
    parser.add_argument("--target", choices=["codex", "gemini", "all"], default="all",
                        help="Which agents to sync to (default: all)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    targets = ["codex", "gemini"] if args.target == "all" else [args.target]
    results = []

    # Global sync
    if args.global_only or not args.workspace:
        result = sync_global(targets, dry_run=args.dry_run)
        results.append(("global", result))

    # Workspace sync
    if args.workspace:
        ws = Path(args.workspace).resolve()
        if not ws.exists():
            print(f"Error: workspace not found: {ws}", file=sys.stderr)
            return 1
        result = sync_workspace(ws, targets, dry_run=args.dry_run)
        results.append((str(ws), result))
    elif not args.global_only:
        cwd = Path.cwd()
        if (cwd / "CLAUDE.md").exists():
            result = sync_workspace(cwd, targets, dry_run=args.dry_run)
            results.append((str(cwd), result))

    if not args.quiet:
        for name, result in results:
            written = result.get("files_written", [])
            if written:
                print(f"Synced ({name}): {len(written)} files")
                for f in written:
                    print(f"  -> {f}")
            else:
                print(f"No changes ({name})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
