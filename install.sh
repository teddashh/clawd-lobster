#!/usr/bin/env bash
# install.sh — Clawd-Lobster Setup for Linux/macOS
# Usage:
#   ./install.sh                 # Interactive
#   ./install.sh --master        # First-time master setup
#   ./install.sh --agent         # Join existing system

set -e

WRAPPER_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$HOME/.clawd-lobster"
CONFIG_FILE="$CONFIG_DIR/config.json"
CLAUDE_DIR="$HOME/.claude"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}[OK]${NC} $1"; }
fail() { echo -e "  ${RED}[FAIL]${NC} $1"; }
skip() { echo -e "  ${YELLOW}[SKIP]${NC} $1"; }
step() { echo -e "\n${CYAN}[$1]${NC} $2"; }

# ============================================================
# MODE SELECTION
# ============================================================
MODE="interactive"
for arg in "$@"; do
    case $arg in
        --master)    MODE="master" ;;
        --agent)     MODE="agent" ;;
        --sync-only) exec "$WRAPPER_DIR/scripts/sync-all.sh"; exit 0 ;;
    esac
done

if [ "$MODE" = "interactive" ]; then
    echo ""
    echo -e "  ${MAGENTA}========================================${NC}"
    echo -e "  ${MAGENTA}   Clawd-Lobster Setup${NC}"
    echo -e "     Claude Code Skills Wrapper"
    echo -e "  ${MAGENTA}========================================${NC}"
    echo ""
    echo "  [1] Master Setup  — New system"
    echo "  [2] Agent Setup   — Join existing"
    echo ""
    read -rp "  Select (1 or 2): " choice
    [ "$choice" = "2" ] && MODE="agent" || MODE="master"
fi

# ============================================================
# STEP 1: PREREQUISITES
# ============================================================
step "1/6" "Checking prerequisites"

# Node.js
if command -v node &>/dev/null; then
    ok "Node.js $(node --version)"
else
    fail "Node.js not found. Install from https://nodejs.org/"
    exit 1
fi

# Python
if command -v python3 &>/dev/null; then
    ok "$(python3 --version)"
    PYTHON=python3
elif command -v python &>/dev/null; then
    ok "$(python --version)"
    PYTHON=python
else
    fail "Python 3.11+ not found"
    exit 1
fi

# Git
if command -v git &>/dev/null; then
    ok "Git $(git --version | cut -d' ' -f3)"
else
    fail "Git not found"
    exit 1
fi

# Claude Code
if command -v claude &>/dev/null; then
    ok "Claude Code installed"
else
    echo -e "  ${YELLOW}Installing Claude Code...${NC}"
    npm install -g @anthropic-ai/claude-code
    ok "Claude Code installed"
fi

# GitHub CLI
if command -v gh &>/dev/null; then
    ok "GitHub CLI installed"
else
    skip "GitHub CLI not found (optional)"
fi

# ============================================================
# STEP 2: AUTHENTICATION
# ============================================================
step "2/6" "Authentication"

if [ -f "$CLAUDE_DIR/.credentials.json" ]; then
    ok "Claude Code authenticated"
else
    echo -e "  ${YELLOW}Authenticating Claude Code...${NC}"
    claude auth login
    [ -f "$CLAUDE_DIR/.credentials.json" ] && ok "Authenticated" || { fail "Auth failed"; exit 1; }
fi

if command -v gh &>/dev/null; then
    if gh auth status &>/dev/null 2>&1; then
        ok "GitHub authenticated"
    else
        echo -e "  ${YELLOW}Authenticating GitHub...${NC}"
        gh auth login
    fi
fi

# ============================================================
# STEP 3: CONFIG
# ============================================================
step "3/6" "Configuring Clawd-Lobster"

mkdir -p "$CONFIG_DIR"
WS_ROOT="$HOME/Documents/Workspace"
mkdir -p "$WS_ROOT"

cat > "$CONFIG_FILE" << EOF
{
  "wrapper_dir": "$WRAPPER_DIR",
  "data_dir": "$WRAPPER_DIR",
  "workspace_root": "$WS_ROOT",
  "knowledge_dir": "$WRAPPER_DIR/knowledge",
  "l4_provider": "github",
  "oracle": {
    "enabled": false
  },
  "embedding": {
    "provider": "none"
  }
}
EOF
ok "Config saved to $CONFIG_FILE"

# ============================================================
# STEP 4: MCP MEMORY SERVER
# ============================================================
step "4/6" "Installing MCP Memory Server"

cd "$WRAPPER_DIR/skills/memory-server"
$PYTHON -m pip install -e . --quiet 2>/dev/null
cd "$WRAPPER_DIR"
ok "MCP Memory Server installed"

# Configure Claude Code MCP
mkdir -p "$CLAUDE_DIR"
cat > "$CLAUDE_DIR/.mcp.json" << EOF
{
  "mcpServers": {
    "memory": {
      "command": "$PYTHON",
      "args": ["-X", "utf8", "-m", "mcp_memory.server"],
      "cwd": "$WRAPPER_DIR/skills/memory-server"
    }
  }
}
EOF
ok ".mcp.json configured"

# ============================================================
# STEP 5: CLAUDE.MD + SETTINGS
# ============================================================
step "5/6" "Setting up Claude Code config"

CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
sed "s|{{DATA_DIR}}|$WRAPPER_DIR|g" "$WRAPPER_DIR/templates/global-CLAUDE.md" > "$CLAUDE_MD"
ok "CLAUDE.md generated"

SETTINGS="$CLAUDE_DIR/settings.json"
if [ ! -f "$SETTINGS" ] || [ "$(cat "$SETTINGS")" = "{}" ]; then
    cp "$WRAPPER_DIR/templates/settings.json.template" "$SETTINGS"
    ok "settings.json created"
else
    ok "settings.json already configured"
fi

# ============================================================
# STEP 6: SCHEDULER
# ============================================================
step "6/6" "Setting up scheduler"

OS_TYPE="$(uname -s)"
case "$OS_TYPE" in
    Darwin)
        # macOS: launchd
        PLIST="$HOME/Library/LaunchAgents/com.clawd-lobster.sync.plist"
        if [ ! -f "$PLIST" ]; then
            cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.clawd-lobster.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$WRAPPER_DIR/scripts/sync-all.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>WorkingDirectory</key>
    <string>$WRAPPER_DIR</string>
    <key>StandardOutPath</key>
    <string>$WRAPPER_DIR/.claude-memory/sync.log</string>
    <key>StandardErrorPath</key>
    <string>$WRAPPER_DIR/.claude-memory/sync-error.log</string>
</dict>
</plist>
EOF
            launchctl load "$PLIST" 2>/dev/null || true
            ok "launchd sync agent registered (every 30 min)"
        else
            ok "launchd sync agent already exists"
        fi
        # Heartbeat
        HB_PLIST="$HOME/Library/LaunchAgents/com.clawd-lobster.heartbeat.plist"
        if [ ! -f "$HB_PLIST" ]; then
            cat > "$HB_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.clawd-lobster.heartbeat</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$WRAPPER_DIR/scripts/heartbeat.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>WorkingDirectory</key>
    <string>$WRAPPER_DIR</string>
</dict>
</plist>
EOF
            launchctl load "$HB_PLIST" 2>/dev/null || true
            ok "launchd heartbeat agent registered (every 30 min)"
        else
            ok "launchd heartbeat agent already exists"
        fi
        ;;
    Linux)
        # Linux: cron
        CRON_CMD="*/30 * * * * bash $WRAPPER_DIR/scripts/sync-all.sh"
        CRON_HB="*/30 * * * * bash $WRAPPER_DIR/scripts/heartbeat.sh"
        if ! crontab -l 2>/dev/null | grep -q "clawd-lobster"; then
            (crontab -l 2>/dev/null; echo "# clawd-lobster sync + heartbeat"; echo "$CRON_CMD"; echo "$CRON_HB") | crontab -
            ok "Cron jobs registered (sync + heartbeat, every 30 min)"
        else
            ok "Cron jobs already exist"
        fi
        ;;
esac

chmod +x "$WRAPPER_DIR/scripts/heartbeat.sh" 2>/dev/null

# ============================================================
# DONE
# ============================================================
echo ""
echo -e "  ${GREEN}========================================${NC}"
echo -e "  ${GREEN}   Clawd-Lobster installed!${NC}"
echo -e "  ${GREEN}========================================${NC}"
echo ""
echo "  Wrapper:    $WRAPPER_DIR"
echo "  Config:     $CONFIG_FILE"
echo "  Workspaces: $WS_ROOT"
echo ""
echo -e "  ${YELLOW}Next steps:${NC}"
echo "    1. Create workspace:  ./scripts/new-workspace.ps1 -name \"my-project\" (or create manually)"
echo "    2. Open Claude Code:  cd \"$WS_ROOT/my-project\" && claude"
echo "    3. Migrate existing:  claude \"/migrate\" (inside Claude Code)"
echo ""
