#!/usr/bin/env bash
# heartbeat.sh — Session Lifecycle Manager (macOS/Linux)
# Ensures every registered workspace has a live Claude Code session.
# If a session is dead, it gets revived via claude --resume.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WRAPPER_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$HOME/.clawd-lobster/config.json"

# Load config
if [ ! -f "$CONFIG_FILE" ]; then
    echo "[heartbeat] No config found. Run install first."
    exit 1
fi

MACHINE_ID=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('machine_id','unknown'))" 2>/dev/null || echo "unknown")
DOMAIN=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('domain','hybrid'))" 2>/dev/null || echo "hybrid")
WS_ROOT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('workspace_root','$HOME/Documents/Workspace'))" 2>/dev/null || echo "$HOME/Documents/Workspace")

LOG_DIR="$WRAPPER_DIR/.claude-memory"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/heartbeat.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

log "=== Heartbeat started (machine: $MACHINE_ID, domain: $DOMAIN) ==="

REGISTRY="$WRAPPER_DIR/workspaces.json"
if [ ! -f "$REGISTRY" ]; then
    log "No workspaces.json found"
    exit 1
fi

alive=0
revived=0
skipped=0

# Get workspace IDs and paths from registry
python3 -c "
import json, sys
reg = json.load(open('$REGISTRY'))
domain = '$DOMAIN'
roots = {}
for d, v in reg.get('domains', {}).items():
    roots[d] = v.get('workspace_root', '').replace('~', '$HOME')
default_root = '$WS_ROOT'

for ws in reg.get('workspaces', []):
    deploy = ws.get('deploy', '')
    ws_domain = ws.get('domain', 'work')
    should = False
    if domain == 'hybrid': should = True
    elif deploy == 'all': should = True
    elif deploy == domain: should = True
    elif ws_domain == domain: should = True
    if not should: continue
    root = roots.get(ws_domain, default_root)
    print(f\"{ws['id']}|{root}/{ws.get('path', ws['id'])}\")
" 2>/dev/null | while IFS='|' read -r ws_id ws_path; do
    if [ ! -d "$ws_path" ]; then
        log "  [$ws_id] path not found, skipping"
        skipped=$((skipped + 1))
        continue
    fi

    # Check if claude is running with this workspace
    is_alive=false
    if pgrep -f "claude.*$ws_id" >/dev/null 2>&1; then
        is_alive=true
    elif pgrep -f "claude.*$(basename "$ws_path")" >/dev/null 2>&1; then
        is_alive=true
    fi

    if $is_alive; then
        log "  [$ws_id] alive"
        alive=$((alive + 1))
    else
        # Revive
        if command -v claude &>/dev/null; then
            log "  [$ws_id] dead -> reviving..."
            OS_TYPE="$(uname -s)"
            case "$OS_TYPE" in
                Darwin)
                    # macOS: open in new Terminal tab
                    osascript -e "tell application \"Terminal\" to do script \"cd '$ws_path' && claude --resume\"" 2>/dev/null
                    ;;
                Linux)
                    # Linux: start in background with nohup
                    if command -v gnome-terminal &>/dev/null; then
                        gnome-terminal -- bash -c "cd '$ws_path' && claude --resume" 2>/dev/null &
                    elif command -v tmux &>/dev/null; then
                        tmux new-session -d -s "$ws_id" -c "$ws_path" "claude --resume" 2>/dev/null
                    else
                        nohup bash -c "cd '$ws_path' && claude --resume" >/dev/null 2>&1 &
                    fi
                    ;;
            esac
            revived=$((revived + 1))
            log "  [$ws_id] revived"
        else
            log "  [$ws_id] cannot revive: claude not in PATH"
            skipped=$((skipped + 1))
        fi
    fi
done

log "=== Heartbeat complete: $alive alive, $revived revived, $skipped skipped ==="

# Update machine status
CLIENT_FILE="$WRAPPER_DIR/clients/$MACHINE_ID.json"
if [ -f "$CLIENT_FILE" ]; then
    python3 -c "
import json
from datetime import datetime
with open('$CLIENT_FILE') as f:
    s = json.load(f)
s['last_heartbeat'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
s['sessions_alive'] = $alive + $revived
s['last_sync'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
with open('$CLIENT_FILE', 'w') as f:
    json.dump(s, f, indent=2)
" 2>/dev/null
fi
