#!/usr/bin/env bash
# PostToolUse hook: auto-format files after Edit/Write
# Detects project formatter and runs it on the changed file.
# Fails gracefully — never blocks Claude.

set -euo pipefail

# Extract file path from tool input (passed via CLAUDE_TOOL_INPUT env)
FILE_PATH="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"
[ -z "$FILE_PATH" ] && exit 0
[ ! -f "$FILE_PATH" ] && exit 0

EXT="${FILE_PATH##*.}"

format_file() {
  case "$EXT" in
    py)
      command -v black >/dev/null 2>&1 && black -q "$FILE_PATH" 2>/dev/null && return
      command -v ruff >/dev/null 2>&1 && ruff format -q "$FILE_PATH" 2>/dev/null && return
      ;;
    js|ts|jsx|tsx|json|css|md|html|yaml|yml)
      command -v prettier >/dev/null 2>&1 && prettier --write "$FILE_PATH" 2>/dev/null && return
      ;;
    rs)
      command -v rustfmt >/dev/null 2>&1 && rustfmt "$FILE_PATH" 2>/dev/null && return
      ;;
    go)
      command -v gofmt >/dev/null 2>&1 && gofmt -w "$FILE_PATH" 2>/dev/null && return
      ;;
    rb)
      command -v rubocop >/dev/null 2>&1 && rubocop -A --fail-level error "$FILE_PATH" 2>/dev/null && return
      ;;
  esac
}

format_file || true
exit 0
