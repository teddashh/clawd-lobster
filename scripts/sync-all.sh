#!/usr/bin/env bash
# sync-all.sh — Pull, push, and optional decay for all workspaces
# Scheduled to run every 30 minutes via cron (Linux) or launchd (macOS)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WRAPPER_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$HOME/.clawd-lobster/config.json"

# Load config
if [ -f "$CONFIG_FILE" ]; then
    WS_ROOT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('workspace_root','$HOME/Documents/Workspace'))" 2>/dev/null || echo "$HOME/Documents/Workspace")
else
    WS_ROOT="$HOME/Documents/Workspace"
fi

LOG_DIR="$WRAPPER_DIR/.claude-memory"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/sync.log"
LOCK_FILE="/tmp/clawd-lobster-sync.lock"

# Prevent concurrent runs
if command -v flock &>/dev/null; then
    exec 200>"$LOCK_FILE"
    flock -n 200 || { echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sync already running, skipping" >> "$LOG_FILE"; exit 0; }
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

log "=== Sync started ==="

# Step 1: Git Pull
log "--- Pull ---"
git -C "$WRAPPER_DIR" pull --quiet 2>/dev/null || log "  PULL wrapper: failed"
find "$WS_ROOT" -maxdepth 3 -name ".git" -type d 2>/dev/null | while read -r gitdir; do
    repo="$(dirname "$gitdir")"
    name="$(basename "$repo")"
    git -C "$repo" pull --quiet 2>/dev/null || log "  PULL $name: failed"
done
log "  Pull complete"

# Step 2: Git Push (tracked files + known safe patterns only)
log "--- Push ---"
for repo in "$WRAPPER_DIR" $(find "$WS_ROOT" -maxdepth 3 -name ".git" -type d 2>/dev/null | xargs -I{} dirname {}); do
    if [ -n "$(git -C "$repo" status --porcelain 2>/dev/null)" ]; then
        name="$(basename "$repo")"
        git -C "$repo" add -u 2>/dev/null
        git -C "$repo" add "*.md" "*.json" "*.py" "*.ps1" "*.sh" "*.toml" "*.yml" "*.yaml" "*.html" 2>/dev/null
        if [ -n "$(git -C "$repo" diff --cached --name-only 2>/dev/null)" ]; then
            git -C "$repo" commit -m "auto-sync $(date '+%Y-%m-%d %H:%M')" --quiet 2>/dev/null
            git -C "$repo" push --quiet 2>/dev/null && log "  PUSH $name: done" || log "  PUSH $name: failed"
        fi
    fi
done
log "  Push complete"

# Step 3: Salience Decay (once daily)
DECAY_MARKER="$LOG_DIR/.decay-last"
TODAY=$(date '+%Y-%m-%d')
LAST_DECAY=$(cat "$DECAY_MARKER" 2>/dev/null || echo "")

if [ "$LAST_DECAY" != "$TODAY" ]; then
    log "--- Decay ---"
    MCP_DIR="$WRAPPER_DIR/skills/memory-server"
    if [ -f "$MCP_DIR/mcp_memory/server.py" ]; then
        (cd "$MCP_DIR" && python3 -X utf8 -m mcp_memory.server --decay 2>/dev/null) && echo "$TODAY" > "$DECAY_MARKER"
        log "  Decay complete"
    fi
fi

log "=== Sync finished ==="
