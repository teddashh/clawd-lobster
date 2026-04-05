#!/usr/bin/env bash
# Stop hook: quick verification when Claude finishes a turn.
# Checks for uncommitted changes and basic project health.
# Must complete in < 2 seconds. Fails gracefully.

set -euo pipefail

WARNINGS=""

# Check for uncommitted changes
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  CHANGED=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
  STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
  if [ "$CHANGED" -gt 0 ] || [ "$STAGED" -gt 0 ]; then
    WARNINGS="${WARNINGS}Uncommitted changes: ${CHANGED} modified, ${STAGED} staged. "
  fi
fi

# Check if any test runner exists and tests are passing (quick check only)
if [ -f "package.json" ] && command -v npm >/dev/null 2>&1; then
  # Only check if test script exists, don't run full suite
  if grep -q '"test"' package.json 2>/dev/null; then
    WARNINGS="${WARNINGS}Tests available (npm test). "
  fi
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
  if command -v pytest >/dev/null 2>&1; then
    WARNINGS="${WARNINGS}Tests available (pytest). "
  fi
fi

if [ -n "$WARNINGS" ]; then
  echo "{\"hint\": \"Before finishing: ${WARNINGS}Consider verifying your work.\"}"
fi

exit 0
