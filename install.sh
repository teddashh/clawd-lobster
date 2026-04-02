#!/usr/bin/env bash
# install.sh — Clawd-Lobster Setup for Linux/macOS
# Usage:
#   ./install.sh                                    # Interactive
#   ./install.sh --lang en --hub new --env fresh     # Headless
#   ./install.sh --sync-only                         # Just run sync

set -e

WRAPPER_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$HOME/.clawd-lobster"
CONFIG_FILE="$CONFIG_DIR/config.json"
CLAUDE_DIR="$HOME/.claude"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; GRAY='\033[0;37m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}[OK]${NC} $1"; }
fail() { echo -e "  ${RED}[FAIL]${NC} $1"; }
skip() { echo -e "  ${YELLOW}[SKIP]${NC} $1"; }
step() { echo -e "\n${CYAN}[$1]${NC} $2"; }

# Parse args
LANG="" HUB="" ENV_MODE="" MACHINE_ID="" JOIN_CODE="" HUB_NAME="" DOMAIN=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --lang)       LANG="$2"; shift 2 ;;
        --hub)        HUB="$2"; shift 2 ;;
        --env)        ENV_MODE="$2"; shift 2 ;;
        --machine)    MACHINE_ID="$2"; shift 2 ;;
        --join)       JOIN_CODE="$2"; shift 2 ;;
        --hub-name)   HUB_NAME="$2"; shift 2 ;;
        --domain)     DOMAIN="$2"; shift 2 ;;
        --sync-only)  exec "$WRAPPER_DIR/scripts/sync-all.sh"; exit 0 ;;
        *)            shift ;;
    esac
done

# Detect Python
if command -v python3 &>/dev/null; then PYTHON=python3
elif command -v python &>/dev/null; then PYTHON=python
else PYTHON=""
fi

# ============================================================
# LANGUAGE SELECTION
# ============================================================

echo ""
echo -e "  ${MAGENTA}========================================${NC}"
echo -e "  ${MAGENTA}   Clawd-Lobster${NC}"
echo -e "     Claude Code Skills Wrapper"
echo -e "  ${MAGENTA}========================================${NC}"
echo ""

if [ -z "$LANG" ]; then
    echo "  Select language:"
    echo ""
    echo "    [1] English"
    echo "    [2] 繁體中文 (台灣)"
    echo "    [3] 简体中文"
    echo "    [4] 日本語"
    echo "    [5] 한국어"
    echo ""
    read -rp "  (1-5): " lang_choice
    case $lang_choice in
        2) LANG="zh-TW" ;; 3) LANG="zh-CN" ;; 4) LANG="ja" ;; 5) LANG="ko" ;; *) LANG="en" ;;
    esac
fi

# i18n (keep it simple — key messages only)
case $LANG in
    zh-TW) MSG_NEW="建立新系統"; MSG_JOIN="加入現有 Hub"; MSG_FRESH="全新開始"; MSG_ABSORB="吸收舊系統"
           MSG_HUB_PROMPT="幫你的 Hub 取個名字"; MSG_MACHINE="幫這台機器命名"
           MSG_DONE="Clawd-Lobster 安裝完成！"; MSG_NEXT="接下來" ;;
    zh-CN) MSG_NEW="创建新系统"; MSG_JOIN="加入现有 Hub"; MSG_FRESH="全新开始"; MSG_ABSORB="吸收旧系统"
           MSG_HUB_PROMPT="给你的 Hub 起个名字"; MSG_MACHINE="给这台机器命名"
           MSG_DONE="Clawd-Lobster 安装完成！"; MSG_NEXT="下一步" ;;
    ja)    MSG_NEW="新しいシステム"; MSG_JOIN="既存のHubに参加"; MSG_FRESH="新規スタート"; MSG_ABSORB="既存システムを吸収"
           MSG_HUB_PROMPT="Hubの名前"; MSG_MACHINE="このマシンの名前"
           MSG_DONE="Clawd-Lobster インストール完了！"; MSG_NEXT="次のステップ" ;;
    ko)    MSG_NEW="새 시스템"; MSG_JOIN="기존 Hub에 참여"; MSG_FRESH="새로 시작"; MSG_ABSORB="기존 시스템 흡수"
           MSG_HUB_PROMPT="Hub 이름"; MSG_MACHINE="이 머신의 이름"
           MSG_DONE="Clawd-Lobster 설치 완료！"; MSG_NEXT="다음 단계" ;;
    *)     MSG_NEW="New system (create Hub)"; MSG_JOIN="Join existing Hub"; MSG_FRESH="Fresh start"; MSG_ABSORB="Absorb previous system"
           MSG_HUB_PROMPT="Name your Hub"; MSG_MACHINE="Name this machine"
           MSG_DONE="Clawd-Lobster installed!"; MSG_NEXT="Next steps" ;;
esac

# ============================================================
# ROUND 1: NEW OR JOIN?
# ============================================================

if [ -z "$HUB" ]; then
    echo ""
    echo -e "  ${YELLOW}What are you setting up?${NC}"
    echo "    [1] $MSG_NEW"
    echo "    [2] $MSG_JOIN"
    read -rp "  (1/2): " r1
    [ "$r1" = "2" ] && HUB="join" || HUB="new"
fi

# ============================================================
# ROUND 2: FRESH OR ABSORB?
# ============================================================

if [ -z "$ENV_MODE" ]; then
    echo ""
    echo -e "  ${YELLOW}Environment?${NC}"
    echo "    [1] $MSG_FRESH"
    echo "    [2] $MSG_ABSORB"
    read -rp "  (1/2): " r2
    [ "$r2" = "2" ] && ENV_MODE="absorb" || ENV_MODE="fresh"
fi

# Hub naming
if [ "$HUB" = "new" ] && [ -z "$HUB_NAME" ]; then
    default_hub="clawd-$(whoami | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9')"
    echo ""
    read -rp "  $MSG_HUB_PROMPT [$default_hub]: " HUB_NAME
    [ -z "$HUB_NAME" ] && HUB_NAME="$default_hub"
    HUB_NAME=$(echo "$HUB_NAME" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9-' '-' | sed 's/^-//;s/-$//')
fi

if [ "$HUB" = "join" ] && [ -z "$JOIN_CODE" ]; then
    echo ""
    read -rp "  Hub repo URL (e.g. github.com/you/clawd-yourname): " JOIN_CODE
fi

# Machine ID
if [ -z "$MACHINE_ID" ]; then
    default_id=$(hostname | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9-' '-')
    read -rp "  $MSG_MACHINE [$default_id]: " MACHINE_ID
    [ -z "$MACHINE_ID" ] && MACHINE_ID="$default_id"
fi

# Domain
if [ -z "$DOMAIN" ]; then
    echo ""
    echo "  This machine is for:"
    echo "    [1] Work"
    echo "    [2] Personal"
    echo "    [3] Hybrid"
    read -rp "  (1/2/3): " dc
    case $dc in 1) DOMAIN="work" ;; 2) DOMAIN="personal" ;; *) DOMAIN="hybrid" ;; esac
fi

SETUP_MODE="$HUB-$ENV_MODE"
echo ""
echo -e "  Machine: ${CYAN}$MACHINE_ID${NC} | Domain: ${CYAN}$DOMAIN${NC} | Mode: ${CYAN}$SETUP_MODE${NC}"

# ============================================================
# STEP 1: PREREQUISITES
# ============================================================
step "1/9" "Checking prerequisites"

command -v node &>/dev/null && ok "Node.js $(node --version)" || { fail "Node.js not found"; exit 1; }
[ -n "$PYTHON" ] && ok "$($PYTHON --version)" || { fail "Python 3.11+ not found"; exit 1; }
command -v git &>/dev/null && ok "Git $(git --version | cut -d' ' -f3)" || { fail "Git not found"; exit 1; }

if command -v claude &>/dev/null; then ok "Claude Code"
else npm install -g @anthropic-ai/claude-code && ok "Claude Code installed"
fi

GH_AVAILABLE=false
if command -v gh &>/dev/null; then ok "GitHub CLI"; GH_AVAILABLE=true
else skip "GitHub CLI (optional)"
fi

# ============================================================
# STEP 2: AUTHENTICATION
# ============================================================
step "2/9" "Authentication"

if [ -f "$CLAUDE_DIR/.credentials.json" ]; then ok "Claude Code"
else
    claude auth login
    [ -f "$CLAUDE_DIR/.credentials.json" ] && ok "Claude Code" || { fail "Auth failed"; exit 1; }
fi

if $GH_AVAILABLE; then
    if gh auth status &>/dev/null 2>&1; then ok "GitHub"
    else gh auth login
    fi
fi

# ============================================================
# STEP 3: CREATE OR CLONE HUB
# ============================================================
step "3/9" "Hub setup"

HUB_DIR=""
if [ "$HUB" = "new" ]; then
    HUB_DIR="$HOME/Documents/$HUB_NAME"
    if [ -d "$HUB_DIR" ]; then
        ok "$HUB_NAME already exists at $HUB_DIR"
    else
        cp -r "$WRAPPER_DIR" "$HUB_DIR"
        rm -rf "$HUB_DIR/.git"
        cd "$HUB_DIR"
        git init -q
        if $GH_AVAILABLE; then
            git add -A && git commit -q -m "Initial hub: $HUB_NAME (generated by clawd-lobster)"
            gh repo create "$HUB_NAME" --private --source=. --remote=origin --push --description "My AI agent hub (generated by clawd-lobster)" 2>/dev/null
            GH_USER=$(gh api user --jq '.login' 2>/dev/null || echo "you")
            ok "Hub created: github.com/$GH_USER/$HUB_NAME (private)"
        else
            git add -A && git commit -q -m "Initial hub: $HUB_NAME"
            ok "Hub created locally (push manually: gh repo create $HUB_NAME --private)"
        fi
        cd "$WRAPPER_DIR"
    fi
    WRAPPER_DIR="$HUB_DIR"
elif [ "$HUB" = "join" ]; then
    hub_url="$JOIN_CODE"
    [[ "$hub_url" != https://* ]] && hub_url="https://github.com/$hub_url"
    [[ "$hub_url" != *.git ]] && hub_url="$hub_url.git"
    HUB_NAME=$(basename "$hub_url" .git)
    HUB_DIR="$HOME/Documents/$HUB_NAME"
    if [ -d "$HUB_DIR" ]; then
        ok "$HUB_NAME exists, pulling latest..."
        cd "$HUB_DIR" && git pull -q && cd "$WRAPPER_DIR"
    else
        git clone -q "$hub_url" "$HUB_DIR" && ok "Hub cloned: $HUB_NAME" || { fail "Clone failed"; exit 1; }
    fi
    WRAPPER_DIR="$HUB_DIR"
fi

# ============================================================
# STEP 4: CONFIG
# ============================================================
step "4/9" "Configuring"

mkdir -p "$CONFIG_DIR"
WS_ROOT="$HOME/Documents/Workspace"
mkdir -p "$WS_ROOT"

cat > "$CONFIG_FILE" << EOF
{
  "machine_id": "$MACHINE_ID",
  "lang": "$LANG",
  "hub": "$HUB",
  "hub_name": "$HUB_NAME",
  "hub_dir": "$HUB_DIR",
  "env": "$ENV_MODE",
  "domain": "$DOMAIN",
  "wrapper_dir": "$WRAPPER_DIR",
  "data_dir": "$WRAPPER_DIR",
  "workspace_root": "$WS_ROOT",
  "knowledge_dir": "$WRAPPER_DIR/knowledge",
  "l4_provider": "github",
  "oracle": { "enabled": false },
  "embedding": { "provider": "none" }
}
EOF
chmod 600 "$CONFIG_FILE"
ok "Config saved (hub: $HUB_NAME, machine: $MACHINE_ID)"

# ============================================================
# STEP 5: MCP MEMORY SERVER
# ============================================================
step "5/9" "Installing MCP Memory Server"

cd "$WRAPPER_DIR/skills/memory-server"
$PYTHON -m pip install -e . --quiet 2>/dev/null
cd "$WRAPPER_DIR"
ok "MCP Memory Server (24 tools)"

mkdir -p "$CLAUDE_DIR"
MCP_JSON="$CLAUDE_DIR/.mcp.json"
if [ -f "$MCP_JSON" ]; then
    # Merge: keep existing MCP servers, add memory
    mkdir -p "$CONFIG_DIR/backup"
    cp "$MCP_JSON" "$CONFIG_DIR/backup/.mcp.json.$(date +%Y%m%d-%H%M%S).bak"
    $PYTHON -c "
import json, sys
try:
    with open('$MCP_JSON') as f: existing = json.load(f)
    servers = existing.get('mcpServers', {})
except (json.JSONDecodeError, FileNotFoundError):
    servers = {}
servers['memory'] = {
    'command': '$PYTHON',
    'args': ['-X', 'utf8', '-m', 'mcp_memory.server'],
    'cwd': '$WRAPPER_DIR/skills/memory-server'
}
with open('$MCP_JSON', 'w') as f:
    json.dump({'mcpServers': servers}, f, indent=2)
print(f'{len(servers)} servers')
" 2>/dev/null
    server_count=$($PYTHON -c "import json; print(len(json.load(open('$MCP_JSON')).get('mcpServers',{})))" 2>/dev/null || echo "?")
    ok ".mcp.json (merged — $server_count servers)"
else
    cat > "$MCP_JSON" << MCPEOF
{
  "mcpServers": {
    "memory": {
      "command": "$PYTHON",
      "args": ["-X", "utf8", "-m", "mcp_memory.server"],
      "cwd": "$WRAPPER_DIR/skills/memory-server"
    }
  }
}
MCPEOF
    ok ".mcp.json (created)"
fi

# ============================================================
# STEP 6: CLAUDE.MD + SETTINGS
# ============================================================
step "6/9" "Setting up Claude Code"

CLAUDE_MD_PATH="$CLAUDE_DIR/CLAUDE.md"
TEMPLATE_MD=$(sed "s|{{DATA_DIR}}|$WRAPPER_DIR|g" "$WRAPPER_DIR/templates/global-CLAUDE.md")
if [ -f "$CLAUDE_MD_PATH" ]; then
    # Merge: append Lobster sections if not already present
    mkdir -p "$CONFIG_DIR/backup"
    cp "$CLAUDE_MD_PATH" "$CONFIG_DIR/backup/CLAUDE.md.$(date +%Y%m%d-%H%M%S).bak"
    if grep -q "Clawd-Lobster" "$CLAUDE_MD_PATH" 2>/dev/null; then
        ok "CLAUDE.md (already has Lobster sections)"
    else
        printf "\n\n# ============================================================\n# Clawd-Lobster (auto-appended by installer)\n# ============================================================\n\n%s" "$TEMPLATE_MD" >> "$CLAUDE_MD_PATH"
        ok "CLAUDE.md (merged — existing content preserved)"
    fi
else
    echo "$TEMPLATE_MD" > "$CLAUDE_MD_PATH"
    ok "CLAUDE.md (created)"
fi

SETTINGS="$CLAUDE_DIR/settings.json"
if [ -f "$CLAUDE_DIR/settings.local.json" ]; then
    ok "settings.local.json (preserved — not modified)"
fi
if [ ! -f "$SETTINGS" ] || [ "$(cat "$SETTINGS" 2>/dev/null)" = "{}" ]; then
    cp "$WRAPPER_DIR/templates/settings.json.template" "$SETTINGS"
    ok "settings.json"
else
    ok "settings.json (exists)"
fi

# ============================================================
# STEP 7: DEPLOY WORKSPACES
# ============================================================
step "7/9" "Deploying workspaces"

REGISTRY_FILE="$WRAPPER_DIR/workspaces.json"
DEPLOYED=()
if [ -f "$REGISTRY_FILE" ]; then
    # Parse workspace IDs and paths using python (portable JSON parsing)
    WS_LIST=$($PYTHON -c "
import json, sys
with open('$REGISTRY_FILE') as f: data = json.load(f)
for ws in data.get('workspaces', []):
    print(ws.get('id','') + '|' + ws.get('path', ws.get('id','')) + '|' + ws.get('repo',''))
" 2>/dev/null || true)

    while IFS='|' read -r ws_id ws_path ws_repo; do
        [ -z "$ws_id" ] && continue
        ws_full="$WS_ROOT/$ws_path"
        if [ -d "$ws_full" ]; then
            ok "$ws_id (exists)"
        elif [ -n "$ws_repo" ] && $GH_AVAILABLE; then
            git clone -q "https://github.com/$ws_repo.git" "$ws_full" 2>/dev/null && ok "$ws_id (cloned)" || { mkdir -p "$ws_full"; skip "$ws_id (created empty)"; }
        else
            mkdir -p "$ws_full"
            ok "$ws_id"
        fi
        # Init memory.db
        mem_dir="$ws_full/.claude-memory"
        if [ ! -f "$mem_dir/memory.db" ]; then
            mkdir -p "$mem_dir"
            $PYTHON "$WRAPPER_DIR/scripts/init_db.py" "$mem_dir/memory.db" 2>/dev/null
        fi
        DEPLOYED+=("$ws_id")
    done <<< "$WS_LIST"
fi
echo -e "  ${GREEN}${#DEPLOYED[@]} workspaces deployed${NC}"

# ============================================================
# STEP 8: SCHEDULER + MACHINE REGISTRATION
# ============================================================
step "8/9" "Scheduler + registration"

chmod +x "$WRAPPER_DIR/scripts/sync-all.sh" "$WRAPPER_DIR/scripts/heartbeat.sh" 2>/dev/null

OS_TYPE="$(uname -s)"
case "$OS_TYPE" in
    Darwin)
        mkdir -p "$HOME/Library/LaunchAgents"
        for job in sync heartbeat; do
            PLIST="$HOME/Library/LaunchAgents/com.clawd-lobster.$job.plist"
            SCRIPT="$WRAPPER_DIR/scripts/${job/sync/sync-all}.sh"
            [ "$job" = "sync" ] && SCRIPT="$WRAPPER_DIR/scripts/sync-all.sh"
            [ "$job" = "heartbeat" ] && SCRIPT="$WRAPPER_DIR/scripts/heartbeat.sh"
            if [ ! -f "$PLIST" ]; then
                cat > "$PLIST" << PEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.clawd-lobster.$job</string>
    <key>ProgramArguments</key><array><string>/bin/bash</string><string>$SCRIPT</string></array>
    <key>StartInterval</key><integer>1800</integer>
    <key>WorkingDirectory</key><string>$WRAPPER_DIR</string>
</dict>
</plist>
PEOF
                launchctl load "$PLIST" 2>/dev/null || true
                ok "launchd $job (every 30 min)"
            else ok "launchd $job (exists)"; fi
        done
        ;;
    Linux)
        if ! crontab -l 2>/dev/null | grep -q "clawd-lobster"; then
            (crontab -l 2>/dev/null
             echo "# clawd-lobster sync + heartbeat"
             echo "*/30 * * * * bash $WRAPPER_DIR/scripts/sync-all.sh >> $WRAPPER_DIR/.claude-memory/sync.log 2>&1"
             echo "*/30 * * * * bash $WRAPPER_DIR/scripts/heartbeat.sh >> $WRAPPER_DIR/.claude-memory/heartbeat.log 2>&1"
            ) | crontab -
            ok "Cron jobs registered (every 30 min)"
        else ok "Cron jobs (exist)"; fi
        ;;
esac

# Register machine
CLIENTS_DIR="$WRAPPER_DIR/clients"
mkdir -p "$CLIENTS_DIR"
CLAUDE_VER=$(claude --version 2>/dev/null || echo "unknown")
cat > "$CLIENTS_DIR/$MACHINE_ID.json" << EOF
{
  "machine_id": "$MACHINE_ID",
  "hostname": "$(hostname)",
  "os": "$OS_TYPE $(uname -r | cut -d- -f1)",
  "lang": "$LANG",
  "domain": "$DOMAIN",
  "hub": "$HUB",
  "env_mode": "$ENV_MODE",
  "registered": "$(date +%Y-%m-%d)",
  "last_sync": "$(date +%Y-%m-%dT%H:%M:%S)",
  "deployed_workspaces": $(printf '%s\n' "${DEPLOYED[@]}" | $PYTHON -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" 2>/dev/null || echo "[]"),
  "claude_version": "$CLAUDE_VER",
  "memory_server_version": "0.3.0"
}
EOF
ok "Machine: $MACHINE_ID"

# ============================================================
# STEP 9: MIGRATION
# ============================================================
step "9/9" "Migration"

if [ "$ENV_MODE" = "absorb" ]; then
    found=()
    [ -d "$HOME/Documents/claude-setup" ] && found+=("claude-setup")
    [ -d "$HOME/.openclaw" ] && found+=("OpenClaw")
    [ -d "$HOME/.hermes" ] && found+=("Hermes Agent")
    [ -f "$CLAUDE_DIR/CLAUDE.md" ] && found+=("Raw Claude Code")

    if [ ${#found[@]} -gt 0 ]; then
        echo -e "  ${YELLOW}Detected: ${found[*]}${NC}"
        echo -e "  ${YELLOW}Run inside Claude Code to absorb:${NC}"
        echo -e "    claude \"Read skills/migrate/SKILL.md and execute the migration\""
    else
        skip "No previous systems detected"
    fi
else
    skip "Fresh environment — nothing to absorb"
fi

# ============================================================
# DONE
# ============================================================

echo ""
echo -e "  ${GREEN}========================================${NC}"
echo -e "  ${GREEN}   $MSG_DONE${NC}"
echo -e "  ${GREEN}========================================${NC}"
echo ""
echo -e "  Hub:        ${GRAY}$HUB_NAME${NC}"
echo -e "  Hub dir:    ${GRAY}${HUB_DIR:-$WRAPPER_DIR}${NC}"
echo -e "  Machine:    ${GRAY}$MACHINE_ID ($DOMAIN, $SETUP_MODE)${NC}"
echo -e "  Workspaces: ${GRAY}${#DEPLOYED[@]} deployed${NC}"
echo ""

# Fleet status
if [ -d "$CLIENTS_DIR" ]; then
    echo -e "  ${YELLOW}Fleet:${NC}"
    for f in "$CLIENTS_DIR"/*.json; do
        [ -f "$f" ] || continue
        mid=$($PYTHON -c "import json; d=json.load(open('$f')); print(d.get('machine_id','?'))" 2>/dev/null)
        ws_cnt=$($PYTHON -c "import json; d=json.load(open('$f')); print(len(d.get('deployed_workspaces',[])))" 2>/dev/null)
        tag=""
        [ "$mid" = "$MACHINE_ID" ] && tag=" <-- this machine"
        echo "    $mid — ${ws_cnt} ws${tag}"
    done
    echo ""
fi

echo -e "  ${YELLOW}$MSG_NEXT:${NC}"
echo "    cd \"$WS_ROOT\" && claude"
echo ""
