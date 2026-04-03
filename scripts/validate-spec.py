#!/usr/bin/env python3
"""
validate-spec.py — Hard validation for OpenSpec-style artifacts.

Enforces structural rules on proposal.md, design.md, tasks.md, and spec files.
Runs as a git pre-commit hook or manually from the CLI.

Usage:
    python validate-spec.py /path/to/workspace
    python validate-spec.py . --strict
    python validate-spec.py . --errors-only
    python validate-spec.py . --json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# ANSI colors (graceful fallback)
# ---------------------------------------------------------------------------

_COLOR_SUPPORT: Optional[bool] = None
_UNICODE_SUPPORT: Optional[bool] = None


def _supports_color() -> bool:
    global _COLOR_SUPPORT
    if _COLOR_SUPPORT is not None:
        return _COLOR_SUPPORT
    if os.environ.get("NO_COLOR"):
        _COLOR_SUPPORT = False
    elif os.environ.get("FORCE_COLOR"):
        _COLOR_SUPPORT = True
    elif not hasattr(sys.stdout, "isatty"):
        _COLOR_SUPPORT = False
    else:
        _COLOR_SUPPORT = sys.stdout.isatty()
    return _COLOR_SUPPORT


def _supports_unicode() -> bool:
    global _UNICODE_SUPPORT
    if _UNICODE_SUPPORT is not None:
        return _UNICODE_SUPPORT
    try:
        encoding = getattr(sys.stdout, "encoding", "") or ""
        _UNICODE_SUPPORT = encoding.lower().replace("-", "") in (
            "utf8", "utf16", "utf32", "utf8sig",
        )
    except Exception:
        _UNICODE_SUPPORT = False
    return _UNICODE_SUPPORT


def _sym(unicode_char: str, ascii_fallback: str) -> str:
    return unicode_char if _supports_unicode() else ascii_fallback


def _ansi(code: str, text: str) -> str:
    if _supports_color():
        return f"\033[{code}m{text}\033[0m"
    return text


def green(t: str) -> str:
    return _ansi("32", t)


def red(t: str) -> str:
    return _ansi("31", t)


def yellow(t: str) -> str:
    return _ansi("33", t)


def bold(t: str) -> str:
    return _ansi("1", t)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

class CheckResult:
    """Single validation check result."""

    def __init__(self, passed: bool, message: str, *, warning: bool = False):
        self.passed = passed
        self.warning = warning  # only meaningful when passed is False
        self.message = message

    def to_dict(self) -> dict:
        d = {"passed": self.passed, "message": self.message}
        if not self.passed:
            d["severity"] = "warning" if self.warning else "error"
        return d

    def pretty(self) -> str:
        if self.passed:
            return f"  {green(_sym('✓', 'OK'))} {self.message}"
        if self.warning:
            return f"  {yellow(_sym('⚠', '!!'))} {self.message}"
        return f"  {red(_sym('✗', 'FAIL'))} {self.message}"


class FileResults:
    """All check results for a single file."""

    def __init__(self, relpath: str):
        self.relpath = relpath
        self.checks: List[CheckResult] = []

    @property
    def errors(self) -> int:
        return sum(1 for c in self.checks if not c.passed and not c.warning)

    @property
    def warnings(self) -> int:
        return sum(1 for c in self.checks if not c.passed and c.warning)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    def to_dict(self) -> dict:
        return {"file": self.relpath, "checks": [c.to_dict() for c in self.checks]}


class ValidationReport:
    """Full validation report for a workspace."""

    def __init__(self, workspace: str):
        self.workspace = workspace
        self.file_results: List[FileResults] = []

    @property
    def total_passed(self) -> int:
        return sum(f.passed for f in self.file_results)

    @property
    def total_errors(self) -> int:
        return sum(f.errors for f in self.file_results)

    @property
    def total_warnings(self) -> int:
        return sum(f.warnings for f in self.file_results)

    def exit_code(self, strict: bool = False) -> int:
        if self.total_errors > 0:
            return 1
        if strict and self.total_warnings > 0:
            return 2
        return 0

    def to_dict(self) -> dict:
        return {
            "workspace": self.workspace,
            "summary": {
                "passed": self.total_passed,
                "errors": self.total_errors,
                "warnings": self.total_warnings,
            },
            "files": [f.to_dict() for f in self.file_results],
        }

    def pretty(self, errors_only: bool = False) -> str:
        lines: List[str] = []
        lines.append(f"Validating workspace: {bold(self.workspace)}")
        lines.append("")
        for fr in self.file_results:
            lines.append(bold(fr.relpath))
            for c in fr.checks:
                if errors_only and c.passed:
                    continue
                lines.append(c.pretty())
            lines.append("")
        lines.append(
            f"Summary: {self.total_passed} checks passed, "
            f"{self.total_errors} errors, {self.total_warnings} warnings"
        )
        ec = self.exit_code(strict=True)
        if ec == 0:
            lines.append(f"Exit code: {green('0 (all pass)')}")
        elif ec == 1:
            lines.append(f"Exit code: {red('1 (has errors)')}")
        else:
            lines.append(f"Exit code: {yellow('2 (has warnings)')}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _has_section(text: str, heading: str, level: int = 2) -> Optional[str]:
    """Return the section body if found, else None."""
    prefix = "#" * level
    pattern = re.compile(
        rf"^{prefix}\s+{re.escape(heading)}\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = pattern.search(text)
    if not m:
        return None
    start = m.end()
    # Find next heading of same or higher level
    next_heading = re.compile(rf"^#{{{1},{level}}}\s+", re.MULTILINE)
    n = next_heading.search(text, start)
    body = text[start : n.start() if n else len(text)]
    return body.strip()


def validate_proposal(path: Path, relpath: str) -> FileResults:
    fr = FileResults(relpath)
    text = _read(path)
    if not text:
        fr.checks.append(CheckResult(False, "File is empty or unreadable"))
        return fr

    # ## Why (50-1000 chars)
    why_body = _has_section(text, "Why")
    if why_body is None:
        fr.checks.append(CheckResult(False, "Missing ## Why section"))
    else:
        length = len(why_body)
        if length < 50:
            fr.checks.append(
                CheckResult(False, f"## Why section too short ({length} chars, need >= 50)")
            )
        elif length > 1000:
            fr.checks.append(
                CheckResult(
                    False,
                    f"## Why section too long ({length} chars, max 1000)",
                    warning=True,
                )
            )
        else:
            fr.checks.append(CheckResult(True, f"Has ## Why section ({length} chars)"))

    # ## What Changes
    if _has_section(text, "What Changes") is not None:
        fr.checks.append(CheckResult(True, "Has ## What Changes section"))
    else:
        fr.checks.append(CheckResult(False, "Missing ## What Changes section"))

    # ## Who
    if _has_section(text, "Who") is not None:
        fr.checks.append(CheckResult(True, "Has ## Who section"))
    else:
        fr.checks.append(CheckResult(False, "Missing ## Who section"))

    # ### In Scope
    if _has_section(text, "In Scope", level=3) is not None:
        fr.checks.append(CheckResult(True, "Has ### In Scope"))
    else:
        fr.checks.append(CheckResult(False, "Missing ### In Scope section"))

    # ### Out of Scope
    if _has_section(text, "Out of Scope", level=3) is not None:
        fr.checks.append(CheckResult(True, "Has ### Out of Scope"))
    else:
        fr.checks.append(CheckResult(False, "Missing ### Out of Scope section"))

    return fr


def validate_design(path: Path, relpath: str) -> FileResults:
    fr = FileResults(relpath)
    text = _read(path)
    if not text:
        fr.checks.append(CheckResult(False, "File is empty or unreadable"))
        return fr

    for section in ("Architecture", "Data Model", "Deployment"):
        if _has_section(text, section) is not None:
            fr.checks.append(CheckResult(True, f"Has ## {section} section"))
        else:
            fr.checks.append(CheckResult(False, f"Missing ## {section} section"))

    return fr


def validate_tasks(path: Path, relpath: str) -> FileResults:
    fr = FileResults(relpath)
    text = _read(path)
    if not text:
        fr.checks.append(CheckResult(False, "File is empty or unreadable"))
        return fr

    lines = text.splitlines()

    # Checkbox format
    checkbox_re = re.compile(r"^\s*-\s+\[([ xX])\]")
    pending = 0
    complete = 0
    task_lines: List[Tuple[int, str]] = []
    for i, line in enumerate(lines, 1):
        m = checkbox_re.match(line)
        if m:
            task_lines.append((i, line))
            if m.group(1) == " ":
                pending += 1
            else:
                complete += 1

    total_tasks = pending + complete
    if total_tasks > 0:
        fr.checks.append(
            CheckResult(
                True,
                f"Checkbox format: {total_tasks} tasks ({pending} pending, {complete} complete)",
            )
        )
    else:
        fr.checks.append(CheckResult(False, "No checkbox tasks found (use - [ ] format)"))

    # File path references
    path_re = re.compile(r"`[^`]*[/\\][^`]+`|\([^)]*[/\\][^)]+\)")
    missing_path_lines: List[int] = []
    for lineno, line in task_lines:
        if not path_re.search(line):
            missing_path_lines.append(lineno)

    if not missing_path_lines:
        fr.checks.append(CheckResult(True, "All tasks have file path references"))
    else:
        count = len(missing_path_lines)
        sample = ", ".join(str(n) for n in missing_path_lines[:10])
        if count > 10:
            sample += ", ..."
        fr.checks.append(
            CheckResult(
                False,
                f"{count} tasks missing file path references (lines {sample})",
                warning=True,
            )
        )

    # Phase headers
    phase_re = re.compile(r"^##\s+Phase", re.MULTILINE | re.IGNORECASE)
    phases = phase_re.findall(text)
    if phases:
        fr.checks.append(CheckResult(True, f"{len(phases)} phases detected"))
    else:
        fr.checks.append(
            CheckResult(False, "No ## Phase headers found", warning=True)
        )

    # Minimum task count
    if total_tasks >= 10:
        fr.checks.append(
            CheckResult(True, f"Minimum task count met ({total_tasks} >= 10)")
        )
    else:
        fr.checks.append(
            CheckResult(False, f"Too few tasks ({total_tasks} < 10 minimum)")
        )

    return fr


def validate_spec(path: Path, relpath: str) -> FileResults:
    fr = FileResults(relpath)
    text = _read(path)
    if not text:
        fr.checks.append(CheckResult(False, "File is empty or unreadable"))
        return fr

    # Check subdirectory (spec files should not be directly in specs/)
    # relpath looks like: openspec/changes/v1/specs/auth/spec.md
    parts = Path(relpath).parts
    try:
        specs_idx = list(parts).index("specs")
        # There should be at least one dir between specs/ and spec.md
        after_specs = parts[specs_idx + 1 :]
        if len(after_specs) >= 2:
            fr.checks.append(CheckResult(True, "In subdirectory"))
        else:
            fr.checks.append(
                CheckResult(False, "Spec file should be in a subdirectory of specs/")
            )
    except ValueError:
        fr.checks.append(
            CheckResult(False, "Cannot determine spec directory structure", warning=True)
        )

    # SHALL / MUST
    shall_must_re = re.compile(r"\b(SHALL|MUST)\b")
    weak_re = re.compile(r"\b(should|could|might)\b", re.IGNORECASE)
    has_shall_must = bool(shall_must_re.search(text))
    weak_matches = weak_re.findall(text)

    if has_shall_must:
        fr.checks.append(CheckResult(True, "Requirements use SHALL/MUST"))
    else:
        fr.checks.append(CheckResult(False, "No SHALL or MUST keywords found"))

    if weak_matches:
        unique = sorted(set(w.lower() for w in weak_matches))
        fr.checks.append(
            CheckResult(
                False,
                f"Weak requirement words found: {', '.join(unique)} - prefer SHALL/MUST",
                warning=True,
            )
        )

    # Scenarios with Given/When/Then
    scenario_re = re.compile(r"^###\s+Scenario:", re.MULTILINE)
    scenario_positions = [m.start() for m in scenario_re.finditer(text)]

    if scenario_positions:
        good_scenarios = 0
        for i, pos in enumerate(scenario_positions):
            end = (
                scenario_positions[i + 1] if i + 1 < len(scenario_positions) else len(text)
            )
            block = text[pos:end]
            has_given = bool(re.search(r"\bGiven\b", block))
            has_when = bool(re.search(r"\bWhen\b", block))
            has_then = bool(re.search(r"\bThen\b", block))
            if has_given and has_when and has_then:
                good_scenarios += 1

        total_scenarios = len(scenario_positions)
        if good_scenarios == total_scenarios:
            fr.checks.append(
                CheckResult(True, f"{total_scenarios} scenarios with Given/When/Then")
            )
        else:
            missing = total_scenarios - good_scenarios
            fr.checks.append(
                CheckResult(
                    False,
                    f"{missing}/{total_scenarios} scenarios missing Given/When/Then keywords",
                )
            )
    else:
        fr.checks.append(
            CheckResult(False, "No ### Scenario: sections found", warning=True)
        )

    return fr


# ---------------------------------------------------------------------------
# Discovery & orchestration
# ---------------------------------------------------------------------------

def discover_changes(workspace: Path) -> List[Path]:
    """Find all openspec/changes/*/ directories, excluding archive."""
    changes_dir = workspace / "openspec" / "changes"
    if not changes_dir.is_dir():
        return []
    result = []
    for child in sorted(changes_dir.iterdir()):
        if child.is_dir() and child.name.lower() != "archive":
            result.append(child)
    return result


def validate_workspace(workspace: str) -> ValidationReport:
    """Run all validations on a workspace. Importable entry point."""
    ws = Path(workspace).resolve()
    report = ValidationReport(str(ws))

    change_dirs = discover_changes(ws)
    if not change_dirs:
        return report

    for change_dir in change_dirs:
        rel_base = change_dir.relative_to(ws)

        # proposal.md
        proposal = change_dir / "proposal.md"
        if proposal.is_file():
            report.file_results.append(
                validate_proposal(proposal, str(rel_base / "proposal.md"))
            )

        # design.md
        design = change_dir / "design.md"
        if design.is_file():
            report.file_results.append(
                validate_design(design, str(rel_base / "design.md"))
            )

        # tasks.md
        tasks = change_dir / "tasks.md"
        if tasks.is_file():
            report.file_results.append(
                validate_tasks(tasks, str(rel_base / "tasks.md"))
            )

        # specs/*/spec.md
        specs_dir = change_dir / "specs"
        if specs_dir.is_dir():
            for spec_file in sorted(specs_dir.rglob("spec.md")):
                rel = str(spec_file.relative_to(ws))
                report.file_results.append(validate_spec(spec_file, rel))

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate OpenSpec-style artifacts in a workspace."
    )
    parser.add_argument(
        "workspace",
        nargs="?",
        default=".",
        help="Path to workspace (default: current directory)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures (exit code 2)",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Show only errors (suppress passing checks and warnings)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    args = parser.parse_args(argv)

    report = validate_workspace(args.workspace)

    if args.json_output:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(report.pretty(errors_only=args.errors_only))

    return report.exit_code(strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
