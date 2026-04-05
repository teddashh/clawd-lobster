#!/usr/bin/env python3
"""
spec-squad.py — Multi-session spec orchestrator for Clawd-Lobster.

Runs the /spec flow with separate Claude sessions acting as specialized roles:
  - Architect:  Writes the spec (project.md → proposal.md → design.md → specs/ → tasks.md)
  - Reviewer:   Challenges the spec, finds gaps, demands fixes
  - Coder:      Executes the approved spec (blitz mode)
  - Tester:     Verifies code against spec requirements

Each role is a separate `claude -p` invocation with a role-specific system prompt.
The orchestrator routes artifacts between them and shows progress in the terminal.

Usage:
    python spec-squad.py <workspace-path>                    # Full flow
    python spec-squad.py <workspace-path> --phase review     # Start from review
    python spec-squad.py <workspace-path> --plan-only        # Spec + review only
    python spec-squad.py <workspace-path> --status           # Show current state

No external dependencies — stdlib only.
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

CLAUDE_TIMEOUT = 300  # 5 min per turn
MAX_REVIEW_ROUNDS = 5
SQUAD_STATE_FILE = ".spec-squad.json"

ROLES = {
    "architect": "A",
    "reviewer": "R",
    "coder": "C",
    "tester": "T",
}

PHASES = ["spec", "review", "code", "test"]

# ── ANSI helpers ─────────────────────────────────────────────────────────────

_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def blue(t): return _c("34", t)
def green(t): return _c("32", t)
def yellow(t): return _c("33", t)
def red(t): return _c("31", t)
def cyan(t): return _c("36", t)
def magenta(t): return _c("35", t)
def bold(t): return _c("1", t)
def dim(t): return _c("2", t)


ROLE_COLORS = {
    "architect": blue,
    "reviewer": magenta,
    "coder": green,
    "tester": yellow,
}


def role_tag(role: str) -> str:
    color = ROLE_COLORS.get(role, dim)
    return color(f"[{ROLES[role]}:{role.upper()}]")


# ── State management ─────────────────────────────────────────────────────────

def load_state(workspace: Path) -> dict:
    state_file = workspace / SQUAD_STATE_FILE
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "phase": "spec",
        "review_round": 0,
        "approved": False,
        "started": None,
        "turns": [],
    }


def save_state(workspace: Path, state: dict):
    state_file = workspace / SQUAD_STATE_FILE
    state_file.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ── Claude session runner ────────────────────────────────────────────────────

def run_claude(prompt: str, cwd: Path, role: str, timeout: int = CLAUDE_TIMEOUT) -> str:
    """Run a claude -p session and return output."""
    tag = role_tag(role)
    print(f"\n{tag} {dim('Thinking...')}")

    start = time.time()
    try:
        result = subprocess.run(
            ["claude", "-p", "--dangerously-skip-permissions", prompt],
            capture_output=True, text=True,
            timeout=timeout,
            cwd=str(cwd),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        elapsed = time.time() - start
        output = result.stdout.strip() if result.stdout else ""

        if result.returncode != 0:
            err = result.stderr[:300] if result.stderr else "unknown error"
            print(f"{tag} {red(f'Error ({elapsed:.0f}s): {err}')}")
            return ""

        # Show first few lines as preview
        lines = output.split("\n")
        preview = "\n".join(lines[:3])
        if len(lines) > 3:
            preview += f"\n{dim(f'  ... ({len(lines)} lines total)')}"
        print(f"{tag} {green(f'Done ({elapsed:.0f}s)')}")
        print(textwrap.indent(preview, "  "))

        return output

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"{tag} {red(f'Timeout after {elapsed:.0f}s')}")
        return ""


# ── Role prompts ─────────────────────────────────────────────────────────────

def architect_prompt(project_desc: str, workspace: Path) -> str:
    """Generate the architect's spec-writing prompt."""
    return f"""You are the ARCHITECT in a spec-squad development team.

YOUR ROLE: Write a complete OpenSpec for this project. You will be reviewed by a separate Reviewer session who will challenge your spec mercilessly.

PROJECT DESCRIPTION:
{project_desc}

WORKSPACE: {workspace}

INSTRUCTIONS:
1. Create the openspec/ directory structure if it doesn't exist
2. Generate artifacts in strict DAG order:
   - openspec/project.md (3W1H context capture)
   - openspec/changes/v1/proposal.md (scope definition with In Scope / Out of Scope)
   - openspec/changes/v1/design.md (architecture with rationale)
   - openspec/changes/v1/specs/<capability>/spec.md (SHALL/MUST requirements + Gherkin scenarios)
   - openspec/changes/v1/tasks.md (phased, file-referenced, 5-30 min tasks)

3. Requirements MUST use SHALL or MUST — never "should" or "could"
4. Every requirement needs at least one Gherkin scenario (Given/When/Then)
5. Every task must reference a file path and be completable in 5-30 minutes
6. Write complete, copy-pasteable code in the plan where appropriate
7. Be opinionated — make strong recommendations with trade-off analysis

After generating all artifacts, output a summary:
```json
{{"status": "spec_complete", "capabilities": N, "tasks": N, "phases": N}}
```

Write ALL the files now. Do not ask questions — decide and document your decisions."""


def reviewer_prompt(workspace: Path, review_round: int) -> str:
    """Generate the reviewer's challenge prompt."""
    return f"""You are the REVIEWER in a spec-squad development team. Round {review_round}/{MAX_REVIEW_ROUNDS}.

YOUR ROLE: Tear apart the Architect's spec. Find every gap, ambiguity, missing edge case, and weak decision. You are the adversarial reviewer — your job is to make the spec bulletproof BEFORE any code is written.

WORKSPACE: {workspace}

INSTRUCTIONS:
1. Read ALL files in openspec/ (project.md, proposal.md, design.md, specs/, tasks.md)
2. Challenge systematically:

   ARCHITECTURE:
   - Is the tech stack justified? Are there better alternatives?
   - Are component boundaries clear? Any hidden coupling?
   - Is the data model complete? Missing relationships?
   - Security considerations adequate?

   REQUIREMENTS:
   - Are all SHALL/MUST statements testable?
   - Missing edge cases in Gherkin scenarios?
   - Error handling gaps?
   - Performance/scalability blind spots?

   TASKS:
   - Are tasks properly sequenced? Missing dependencies?
   - Any task > 30 minutes that should be split?
   - Missing tasks for error handling, testing, CI/CD?
   - File paths consistent with design.md architecture?

   CROSS-CUTTING:
   - Does proposal scope match what design/specs actually cover?
   - Are there features in design.md not covered by any spec?
   - Any tasks that reference non-existent spec requirements?

3. Output your verdict as structured JSON:

If there are issues:
```json
{{"verdict": "REVISE", "issues": ["issue 1", "issue 2", ...], "severity": "high|medium|low"}}
```

If the spec is solid:
```json
{{"verdict": "APPROVED", "confidence": 0.0-1.0, "notes": "optional praise or minor notes"}}
```

Be ruthless but fair. A weak spec wastes more time in coding than a tough review saves."""


def architect_revise_prompt(workspace: Path, issues: list[str]) -> str:
    """Generate the architect's revision prompt based on reviewer feedback."""
    issues_text = "\n".join(f"  - {issue}" for issue in issues)
    return f"""You are the ARCHITECT in a spec-squad development team.

The REVIEWER has found issues with your spec. Fix them ALL.

REVIEWER'S ISSUES:
{issues_text}

WORKSPACE: {workspace}

INSTRUCTIONS:
1. Read the current spec files in openspec/
2. Address EVERY issue listed above
3. Update the affected files (proposal.md, design.md, specs/, tasks.md)
4. Do NOT rewrite files that don't need changes
5. Maintain the DAG consistency — if you change design.md, check that specs/ and tasks.md still align

After fixing, output:
```json
{{"status": "revision_complete", "files_modified": ["list of changed files"]}}
```

Fix ALL the issues now. Do not skip any."""


def coder_prompt(workspace: Path) -> str:
    """Generate the coder's blitz prompt."""
    return f"""You are the CODER in a spec-squad development team.

YOUR ROLE: Execute the approved spec exactly. The spec has been reviewed and approved — it is your contract. No improvising.

WORKSPACE: {workspace}

INSTRUCTIONS:
1. Read openspec/changes/v1/tasks.md
2. Execute tasks phase by phase, in order
3. For each task:
   - Create/modify the referenced file
   - Write production-quality code
   - Follow the architecture in design.md exactly
   - Mark the task done: [ ] → [x] in tasks.md
4. After each phase, commit: git add -A && git commit -m "Phase N: <phase title>"
5. Skip any tasks marked [codex] — those are for external execution

RULES:
- The spec is the plan. Follow it.
- If something is ambiguous, decide and add a comment explaining your choice
- Do NOT add features not in the spec
- Do NOT refactor or "improve" the architecture
- If a task fails, log it as a comment and continue

After completing all tasks, output:
```json
{{"status": "build_complete", "tasks_done": N, "tasks_total": N, "phases": N}}
```

Start building now."""


def tester_prompt(workspace: Path) -> str:
    """Generate the tester's verification prompt."""
    return f"""You are the TESTER in a spec-squad development team.

YOUR ROLE: Verify that the Coder's implementation matches the approved spec exactly. Check every requirement, run tests, and report discrepancies.

WORKSPACE: {workspace}

INSTRUCTIONS:
1. Read openspec/changes/v1/specs/ — every requirement and Gherkin scenario
2. Read the implemented code
3. For each spec requirement (SHALL/MUST):
   - Verify the code implements it
   - Check edge cases from Gherkin scenarios
   - Run any existing tests
4. Check tasks.md — are all tasks marked [x]?

OUTPUT your verdict:

If issues found:
```json
{{"verdict": "ISSUES", "failures": ["failure 1", "failure 2", ...], "pass_rate": 0.0-1.0}}
```

If everything passes:
```json
{{"verdict": "PASSED", "pass_rate": 1.0, "tests_run": N, "notes": "optional"}}
```

Be thorough. Check EVERY requirement in the specs, not just the obvious ones."""


# ── Signal extraction ────────────────────────────────────────────────────────

def extract_json_signal(output: str) -> dict | None:
    """Extract the last JSON block from claude output."""
    import re
    # Find all JSON blocks (in or out of code fences)
    patterns = [
        r'```json\s*\n({[^`]*?})\s*\n```',  # fenced
        r'({\"(?:status|verdict)\"[^}]*})',    # inline
    ]
    for pattern in patterns:
        matches = re.findall(pattern, output, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[-1])
            except json.JSONDecodeError:
                continue
    return None


# ── Phase runners ────────────────────────────────────────────────────────────

def phase_spec(workspace: Path, project_desc: str, state: dict) -> dict:
    """Phase 1: Architect writes the spec."""
    print(f"\n{'='*60}")
    print(bold("  PHASE 1: SPEC GENERATION"))
    print(f"{'='*60}")

    prompt = architect_prompt(project_desc, workspace)
    output = run_claude(prompt, workspace, "architect")

    signal = extract_json_signal(output)
    if signal and signal.get("status") == "spec_complete":
        state["phase"] = "review"
        state["review_round"] = 0
        print(f"\n{green('Spec complete.')} {signal.get('tasks', '?')} tasks across {signal.get('phases', '?')} phases.")
    else:
        print(f"\n{yellow('Spec generated (no structured signal). Moving to review.')}")
        state["phase"] = "review"

    state["turns"].append({
        "role": "architect", "phase": "spec",
        "time": datetime.now(timezone.utc).isoformat(),
        "signal": signal,
    })
    save_state(workspace, state)
    return state


def phase_review(workspace: Path, state: dict) -> dict:
    """Phase 2: Reviewer challenges the spec. Loops until approved or max rounds."""
    print(f"\n{'='*60}")
    print(bold("  PHASE 2: SPEC REVIEW"))
    print(f"{'='*60}")

    while state["review_round"] < MAX_REVIEW_ROUNDS:
        state["review_round"] += 1
        round_n = state["review_round"]

        print(f"\n{bold(f'--- Review Round {round_n}/{MAX_REVIEW_ROUNDS} ---')}")

        # Reviewer challenges
        prompt = reviewer_prompt(workspace, round_n)
        output = run_claude(prompt, workspace, "reviewer")
        signal = extract_json_signal(output)

        state["turns"].append({
            "role": "reviewer", "phase": "review", "round": round_n,
            "time": datetime.now(timezone.utc).isoformat(),
            "signal": signal,
        })

        if signal and signal.get("verdict") == "APPROVED":
            state["approved"] = True
            state["phase"] = "code"
            confidence = signal.get("confidence", "?")
            print(f"\n{green(f'SPEC APPROVED (confidence: {confidence})')}")
            save_state(workspace, state)
            return state

        # Extract issues for architect to fix
        issues = []
        if signal and signal.get("issues"):
            issues = signal["issues"]
        elif signal and signal.get("verdict") == "REVISE":
            issues = ["Reviewer requested revisions (no specific issues extracted)"]
        else:
            # Try to extract issues from raw text
            issues = ["Review completed but no structured verdict found. Architect should re-examine spec."]

        severity = signal.get("severity", "medium") if signal else "medium"
        print(f"\n{magenta(f'REVISE requested ({len(issues)} issues, severity: {severity})')}")
        for i, issue in enumerate(issues[:5], 1):
            print(f"  {i}. {issue[:100]}")
        if len(issues) > 5:
            print(f"  ... and {len(issues) - 5} more")

        # Architect revises
        prompt = architect_revise_prompt(workspace, issues)
        output = run_claude(prompt, workspace, "architect")
        revision_signal = extract_json_signal(output)

        state["turns"].append({
            "role": "architect", "phase": "revision", "round": round_n,
            "time": datetime.now(timezone.utc).isoformat(),
            "signal": revision_signal,
        })
        save_state(workspace, state)

    # Max rounds reached
    print(f"\n{yellow(f'Max review rounds ({MAX_REVIEW_ROUNDS}) reached. Proceeding with current spec.')}")
    state["approved"] = True
    state["phase"] = "code"
    save_state(workspace, state)
    return state


def phase_code(workspace: Path, state: dict) -> dict:
    """Phase 3: Coder executes the spec."""
    print(f"\n{'='*60}")
    print(bold("  PHASE 3: CODING (BLITZ)"))
    print(f"{'='*60}")

    prompt = coder_prompt(workspace)
    output = run_claude(prompt, workspace, "coder", timeout=600)

    signal = extract_json_signal(output)
    state["turns"].append({
        "role": "coder", "phase": "code",
        "time": datetime.now(timezone.utc).isoformat(),
        "signal": signal,
    })

    if signal and signal.get("status") == "build_complete":
        done = signal.get("tasks_done", "?")
        total = signal.get("tasks_total", "?")
        print(f"\n{green(f'Build complete: {done}/{total} tasks done.')}")
        state["phase"] = "test"
    else:
        print(f"\n{yellow('Build phase completed (no structured signal). Moving to test.')}")
        state["phase"] = "test"

    save_state(workspace, state)
    return state


def phase_test(workspace: Path, state: dict) -> dict:
    """Phase 4: Tester verifies the build."""
    print(f"\n{'='*60}")
    print(bold("  PHASE 4: TESTING"))
    print(f"{'='*60}")

    prompt = tester_prompt(workspace)
    output = run_claude(prompt, workspace, "tester")

    signal = extract_json_signal(output)
    state["turns"].append({
        "role": "tester", "phase": "test",
        "time": datetime.now(timezone.utc).isoformat(),
        "signal": signal,
    })

    if signal and signal.get("verdict") == "PASSED":
        rate = signal.get("pass_rate", "?")
        print(f"\n{green(f'ALL TESTS PASSED (pass rate: {rate})')}")
        state["phase"] = "done"
    elif signal and signal.get("verdict") == "ISSUES":
        failures = signal.get("failures", [])
        rate = signal.get("pass_rate", "?")
        print(f"\n{red(f'ISSUES FOUND (pass rate: {rate})')}")
        for f in failures[:5]:
            print(f"  - {f[:100]}")
        state["phase"] = "done"  # TODO: loop back to coder
    else:
        print(f"\n{yellow('Test phase completed.')}")
        state["phase"] = "done"

    save_state(workspace, state)
    return state


# ── Status display ───────────────────────────────────────────────────────────

def show_status(workspace: Path):
    """Display current spec-squad state."""
    state = load_state(workspace)
    phase = state.get("phase", "unknown")
    rounds = state.get("review_round", 0)
    approved = state.get("approved", False)
    turns = state.get("turns", [])

    print(f"\n{bold('Spec Squad Status')}")
    print(f"  Workspace: {workspace}")
    print(f"  Phase:     {bold(phase.upper())}")
    print(f"  Review:    {rounds}/{MAX_REVIEW_ROUNDS} rounds")
    print(f"  Approved:  {green('Yes') if approved else yellow('No')}")
    print(f"  Turns:     {len(turns)}")

    if turns:
        print(f"\n  {dim('Turn History:')}")
        for t in turns[-10:]:
            role = t.get("role", "?")
            phase_name = t.get("phase", "?")
            signal = t.get("signal", {})
            verdict = ""
            if signal:
                if "verdict" in signal:
                    verdict = f" → {signal['verdict']}"
                elif "status" in signal:
                    verdict = f" → {signal['status']}"
            print(f"    {role_tag(role)} {phase_name}{verdict}")


# ── Banner ───────────────────────────────────────────────────────────────────

def print_banner():
    border = "=" * 50
    print(f"""
{bold(border)}
        {cyan('SPEC SQUAD')} -- {dim('Multi-Session Spec Flow')}
{bold(border)}
  {blue('[A]')} Architect   writes the spec
  {magenta('[R]')} Reviewer    challenges the spec
  {green('[C]')} Coder       builds the approved spec
  {yellow('[T]')} Tester      verifies against requirements
{bold(border)}
""")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Spec Squad — Multi-session spec orchestrator for Clawd-Lobster",
    )
    parser.add_argument("workspace", help="Path to workspace directory")
    parser.add_argument("--phase", choices=PHASES, default=None,
                        help="Start from a specific phase")
    parser.add_argument("--plan-only", action="store_true",
                        help="Run spec + review only (no coding)")
    parser.add_argument("--status", action="store_true",
                        help="Show current state and exit")
    parser.add_argument("--project", "-p", type=str, default=None,
                        help="Project description (reads from openspec/project.md if not provided)")
    parser.add_argument("--max-rounds", type=int, default=5,
                        help="Max review rounds (default: 5)")
    parser.add_argument("--reset", action="store_true",
                        help="Reset state and start fresh")
    args = parser.parse_args()

    global MAX_REVIEW_ROUNDS
    MAX_REVIEW_ROUNDS = args.max_rounds

    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        print(red(f"Workspace not found: {workspace}"))
        return 1

    # Status mode
    if args.status:
        show_status(workspace)
        return 0

    print_banner()

    # Load or reset state
    if args.reset:
        state = {"phase": "spec", "review_round": 0, "approved": False,
                 "started": None, "turns": []}
    else:
        state = load_state(workspace)

    # Override phase if specified
    if args.phase:
        state["phase"] = args.phase

    # Get project description
    project_desc = args.project
    if not project_desc:
        project_md = workspace / "openspec" / "project.md"
        if project_md.exists():
            project_desc = project_md.read_text(encoding="utf-8")
        else:
            print(red("No project description. Use --project 'description' or create openspec/project.md"))
            return 1

    # Record start time
    if not state.get("started"):
        state["started"] = datetime.now(timezone.utc).isoformat()

    # Run phases
    phase = state["phase"]

    if phase == "spec":
        state = phase_spec(workspace, project_desc, state)
        phase = state["phase"]

    if phase == "review":
        state = phase_review(workspace, state)
        phase = state["phase"]

    if args.plan_only:
        print(f"\n{green('Plan-only mode: stopping after review.')}")
        show_status(workspace)
        return 0

    if phase == "code":
        state = phase_code(workspace, state)
        phase = state["phase"]

    if phase == "test":
        state = phase_test(workspace, state)

    # Final summary
    print(f"\n{'='*60}")
    print(bold("  SPEC SQUAD COMPLETE"))
    print(f"{'='*60}")
    show_status(workspace)

    started = state.get("started")
    if started:
        start_dt = datetime.fromisoformat(started)
        elapsed = datetime.now(timezone.utc) - start_dt
        minutes = elapsed.total_seconds() / 60
        print(f"\n  Total time: {minutes:.1f} minutes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
