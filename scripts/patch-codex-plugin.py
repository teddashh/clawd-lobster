#!/usr/bin/env python3
"""
Patch Codex Plugin — Remove disable-model-invocation from review commands.

By default, the codex-plugin-cc marks /codex:review and /codex:adversarial-review
with `disable-model-invocation: true`, preventing Claude from using them proactively.
This script patches the cached plugin files to remove that restriction.

Run after:
  - Initial plugin install (`claude plugin install openai/codex-plugin-cc`)
  - Plugin updates
  - `skill-manager.py reconcile` (called automatically)

Safe to run multiple times (idempotent).
"""

import os
import re
import sys
from pathlib import Path

PLUGIN_CACHE = Path.home() / ".claude" / "plugins" / "cache" / "openai-codex" / "codex"

PATCHES = {
    "commands/review.md": {
        "remove_line": "disable-model-invocation: true",
        "description_append": ". Use proactively after writing significant code, before committing.",
    },
    "commands/adversarial-review.md": {
        "remove_line": "disable-model-invocation: true",
        "description_append": ". Use for risky changes, security-sensitive code, or architecture decisions.",
    },
}


def find_latest_version(cache_dir: Path) -> Path | None:
    if not cache_dir.exists():
        return None
    versions = sorted(cache_dir.iterdir(), key=lambda p: p.name, reverse=True)
    return versions[0] if versions else None


def patch_file(filepath: Path, patch: dict) -> bool:
    if not filepath.exists():
        print(f"  SKIP {filepath.name} — not found")
        return False

    content = filepath.read_text(encoding="utf-8")
    original = content
    changed = False

    # Remove disable-model-invocation line
    remove = patch["remove_line"]
    if remove in content:
        content = re.sub(rf"^{re.escape(remove)}\n?", "", content, flags=re.MULTILINE)
        changed = True
        print(f"  PATCH {filepath.name} — removed '{remove}'")

    # Append to description if not already appended
    append = patch["description_append"]
    if append and append not in content:
        content = re.sub(
            r"^(description: .+?)(\n)",
            rf"\1{append}\2",
            content,
            count=1,
            flags=re.MULTILINE,
        )
        changed = True
        print(f"  PATCH {filepath.name} — updated description")

    if changed:
        filepath.write_text(content, encoding="utf-8")
    else:
        print(f"  OK   {filepath.name} — already patched")

    return changed


def main():
    version_dir = find_latest_version(PLUGIN_CACHE)
    if not version_dir:
        print("Codex plugin not found in cache. Install with:")
        print("  claude plugin install openai/codex-plugin-cc")
        sys.exit(1)

    print(f"Codex plugin: {version_dir.name}")
    patched = 0
    for relpath, patch in PATCHES.items():
        filepath = version_dir / relpath
        if patch_file(filepath, patch):
            patched += 1

    if patched:
        print(f"\nOK: Patched {patched} file(s). Claude can now proactively use /codex:review and /codex:adversarial-review.")
    else:
        print("\nOK: All files already patched.")


if __name__ == "__main__":
    main()
