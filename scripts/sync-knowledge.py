#!/usr/bin/env python3
"""
sync-knowledge.py — Unified knowledge sync for all agents.

Generates knowledge files that any agent (Claude -p, Codex, Gemini) reads
before starting work. Designed so agents know:
  1. WHERE to find things (skill directory, not full content)
  2. WHAT the project is doing (CLAUDE.md context + global config)
  3. WHAT to do when done (exit protocol: write audit JSON)

Outputs:
  AGENTS.md  → Codex reads on startup
  GEMINI.md  → Gemini reads on startup
  .claude-agent-context.md → claude -p reads via --system-prompt-file

Usage:
    python sync-knowledge.py                         # sync current workspace
    python sync-knowledge.py -w <workspace>          # specific workspace
    python sync-knowledge.py --target codex          # codex only
    python sync-knowledge.py --dry-run               # preview

Run via cron every 30 minutes, or before each agent invocation.
No external dependencies — stdlib only.
"""

import argparse
import json
import os
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
    try:
        return path.read_text(encoding="utf-8") if path.exists() else ""
    except OSError:
        return ""


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


# ── Knowledge Sections ───────────────────────────────────────────────────────

def build_skill_directory() -> str:
    """Skill DIRECTORY — not full content. Just what exists and where to look."""
    skills_dir = REPO_DIR / "skills"
    if not skills_dir.exists():
        return ""

    lines = ["## Skill Library (directory)\n"]
    lines.append(f"Clawd-Lobster is installed at: `{REPO_DIR}`\n")
    lines.append("These skills are available. Read the SKILL.md in each directory for full docs.\n")
    lines.append("| Skill | Type | What It Does | Full Docs |")
    lines.append("|-------|------|-------------|-----------|")

    for sd in sorted(skills_dir.iterdir()):
        sj = sd / "skill.json"
        if not sj.exists():
            continue
        try:
            data = json.loads(sj.read_text(encoding="utf-8"))
            name = data.get("id", sd.name)
            kind = data.get("kind", "unknown")
            # First sentence of description only
            desc = data.get("description", "")
            first_sentence = desc.split(".")[0].split("—")[0].strip()
            if len(first_sentence) > 80:
                first_sentence = first_sentence[:77] + "..."
            full_path = REPO_DIR / "skills" / name / "SKILL.md"
            lines.append(f"| {name} | {kind} | {first_sentence} | `{full_path}` |")
        except (json.JSONDecodeError, OSError):
            continue

    return "\n".join(lines)


def build_memory_guide() -> str:
    """What agents need to know about memory — just the write-back part."""
    return """## Memory System (what you need to know)

This project uses a 4-layer memory system. You do NOT need to operate it.
Claude (the lead agent) manages memory. Your job:

**At the very end of your response, output your findings as a JSON code block:**

```json
{
  "agent": "codex|gemini|claude-p",
  "role": "reviewer|consultant|worker",
  "task": "what you were asked to do",
  "findings": [
    {"type": "blocker|risk|suggestion|decision", "description": "...", "file": "path or null"}
  ],
  "summary": "one paragraph summary of your work",
  "disagreements": ["anything you disagree with in the current approach"]
}
```

Claude (the lead agent) will parse this JSON from your stdout and store
important items in the project's persistent memory. Your session state
disappears when you exit — this JSON block is your ONLY way to persist.

**DO NOT skip the JSON block.** If you found nothing, output empty findings.
The block itself proves you completed your review.
"""


def build_project_context(workspace: Path) -> str:
    """Current project context from CLAUDE.md — stripped of internal sections."""
    claude_md = read_file(workspace / "CLAUDE.md")
    if not claude_md:
        return ""

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

    return "\n## Project Context\n\n" + "\n".join(output)


def build_global_config() -> str:
    """Global conventions that all agents should follow."""
    return """## Global Conventions

- Never commit secrets, API keys, tokens, or credentials
- Never include personal names, hardcoded user paths, or machine-specific info
- Learnings = mistakes to avoid. Skills = patterns to follow. Don't confuse them.
- Spec-driven development: 3W1H framework, DAG order (project → proposal → design → specs → tasks)
- Action logging: TASK_START → SPEC → REVIEW → COMMIT → TASK_DONE
- Always review diffs before committing
"""


def build_recent_context(workspace: Path) -> str:
    """Recent decisions from Claude memory (top 10 only)."""
    projects_dir = CLAUDE_DIR / "projects"
    if not projects_dir.exists():
        return ""

    for proj_dir in projects_dir.iterdir():
        if not proj_dir.is_dir():
            continue
        ws_parts = [p for p in workspace.parts[-2:] if len(p) > 2]
        if all(p.lower() in proj_dir.name.lower() for p in ws_parts):
            memory_dir = proj_dir / "memory"
            index = read_file(memory_dir / "MEMORY.md") if memory_dir.exists() else ""
            if not index:
                continue

            items = []
            for line in index.split("\n"):
                if line.strip().startswith("- [") and "—" in line:
                    desc = line.split("—", 1)[1].strip()
                    items.append(f"- {desc}")
            if items:
                return "\n## Recent Decisions & Learnings\n\n" + "\n".join(items[:10])
    return ""


def build_spec_state(workspace: Path) -> str:
    """Current spec progress if any."""
    changes_dir = workspace / "openspec" / "changes"
    if not changes_dir.exists():
        return ""

    for change_dir in sorted(changes_dir.iterdir(), reverse=True):
        tf = change_dir / "tasks.md"
        if tf.exists():
            content = read_file(tf)
            total = content.count("- [ ]") + content.count("- [x]")
            done = content.count("- [x]")
            if total == 0:
                continue
            blitz = (workspace / ".blitz-active").exists()
            status = "BLITZ IN PROGRESS" if blitz else f"{done}/{total} tasks ({done*100//total}%)"
            return f"\n## Current Spec: {status}\n"
    return ""


# ── Exit Protocol (hardcoded in every agent call) ────────────────────────────

EXIT_PROTOCOL = """## EXIT PROTOCOL (MANDATORY)

At the very end of your response, output your findings as a JSON code block:

```json
{
  "agent": "codex|gemini|claude-p",
  "role": "reviewer|consultant|worker",
  "task": "what you were asked to do",
  "findings": [
    {"type": "blocker|risk|suggestion", "description": "...", "file": "path or null"}
  ],
  "summary": "one paragraph summary",
  "disagreements": ["anything you disagree with"]
}
```

Claude (the lead) will parse this JSON from your stdout and store it.
Your session state disappears when you exit — this JSON is your ONLY persistence.
DO NOT SKIP. If no findings, use empty array.
"""


# ── Format-specific output ───────────────────────────────────────────────────

def build_knowledge(workspace: Path | None) -> str:
    """Build the unified knowledge package."""
    parts = [build_skill_directory(), build_memory_guide(), build_global_config()]
    if workspace:
        ctx = build_project_context(workspace)
        if ctx:
            parts.append(ctx)
        recent = build_recent_context(workspace)
        if recent:
            parts.append(recent)
        spec = build_spec_state(workspace)
        if spec:
            parts.append(spec)
    parts.append(EXIT_PROTOCOL)
    return "\n".join(parts)


def format_for_codex(knowledge: str, timestamp: str) -> str:
    header = f"""# Agent Briefing — Codex

> Synced: {timestamp} | Source: Claude Code + clawd-lobster
> **Role: Reviewer / Worker / Critic.** Challenge assumptions. Find bugs.
> **Do not edit** — auto-generated by sync-knowledge.py
>
> **Context for your role:** You get task briefs + relevant wiki pages + TODOs.
> You do NOT get full decision history — focus on implementation quality.
> If you disagree with a wiki page, report it as a finding, don't rewrite it.

---

"""
    content = header + knowledge
    if len(content.encode("utf-8")) > 32 * 1024:
        content = content[:32 * 1024 - 200] + "\n\n> Truncated (32 KiB limit)\n"
    return content


def format_for_gemini(knowledge: str, timestamp: str) -> str:
    return f"""# Agent Briefing — Gemini

> Synced: {timestamp} | Source: Claude Code + clawd-lobster
> **Role: Consultant / Validator / Researcher.** Provide independent perspective.
> You are part of a three-agent system: Claude (lead), Codex (worker/critic), Gemini (you).
> **Do not edit** — auto-generated by sync-knowledge.py
>
> **Context for your role:** You get the wiki + open disputes + assumptions.
> You do NOT get implementation TODOs — focus on strategy and validation.
> If you find a contradiction in the wiki, report it as a finding with evidence.

---

{knowledge}
"""


def format_for_claude_p(knowledge: str, timestamp: str) -> str:
    return f"""# Agent Briefing — Claude (subprocess)

> Synced: {timestamp} | Source: parent Claude session
> **Role: Delegated task executor.** You are a claude -p subprocess.
> Write findings as JSON block in stdout before exiting.
>
> **Context for your role:** You get full L1 + L2 context.
> Use knowledge/wiki/ for reference. Cite wiki pages in your work.
> If your work produces durable knowledge, note it in findings for the lead to store.

---

{knowledge}
"""


# ── Sync logic ───────────────────────────────────────────────────────────────

def sync_workspace(workspace: Path, targets: list[str], dry_run: bool = False) -> dict:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = {"files_written": []}
    knowledge = build_knowledge(workspace)

    if "codex" in targets:
        path = workspace / "AGENTS.md"
        if write_file(path, format_for_codex(knowledge, timestamp), dry_run):
            summary["files_written"].append(str(path))

    if "gemini" in targets:
        path = workspace / "GEMINI.md"
        if write_file(path, format_for_gemini(knowledge, timestamp), dry_run):
            summary["files_written"].append(str(path))

    if "claude-p" in targets:
        path = workspace / ".claude-agent-context.md"
        if write_file(path, format_for_claude_p(knowledge, timestamp), dry_run):
            summary["files_written"].append(str(path))

    # Ensure .agent-audit directory exists
    audit_dir = workspace / ".agent-audit"
    if not dry_run:
        audit_dir.mkdir(exist_ok=True)
        gitignore = audit_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n!.gitignore\n", encoding="utf-8")

    return summary


def sync_global(targets: list[str], dry_run: bool = False) -> dict:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = {"files_written": []}
    knowledge = build_knowledge(None)

    if "codex" in targets:
        path = CODEX_DIR / "AGENTS.md"
        if write_file(path, format_for_codex(knowledge, timestamp), dry_run):
            summary["files_written"].append(str(path))

    if "gemini" in targets:
        path = GEMINI_DIR / "GEMINI.md"
        if write_file(path, format_for_gemini(knowledge, timestamp), dry_run):
            summary["files_written"].append(str(path))

    return summary


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Sync knowledge to Codex (AGENTS.md), Gemini (GEMINI.md), claude -p",
    )
    parser.add_argument("-w", "--workspace", help="Workspace path")
    parser.add_argument("-g", "--global-only", dest="global_only", action="store_true")
    parser.add_argument("--target", choices=["codex", "gemini", "claude-p", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    targets = ["codex", "gemini", "claude-p"] if args.target == "all" else [args.target]
    results = []

    if args.global_only or not args.workspace:
        result = sync_global(targets, dry_run=args.dry_run)
        results.append(("global", result))

    if args.workspace:
        ws = Path(args.workspace).resolve()
        if not ws.exists():
            print(f"Error: {ws}", file=sys.stderr)
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
