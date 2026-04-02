#!/usr/bin/env bash
# install-lib.sh — Helper functions for Clawd-Lobster installer
# Sourced by install.sh: source "$WRAPPER_DIR/scripts/install-lib.sh"

# Requires: PYTHON, CONFIG_DIR, CLAUDE_DIR set by caller

# ============================================================
# JSON / FILE SAFETY
# ============================================================

test_json_file() {
    # Safely parse and validate a JSON file. Returns 0 if valid, 1 if not.
    local path="$1"
    [ ! -f "$path" ] && return 1
    $PYTHON -c "
import json, sys
try:
    # Handle BOM
    with open('$path', 'rb') as f:
        raw = f.read()
    if raw[:3] == b'\xef\xbb\xbf':
        raw = raw[3:]
    elif raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
        raw = raw.decode('utf-16').encode('utf-8')
    data = json.loads(raw)
    sys.exit(0)
except Exception as e:
    print(f'WARN: Malformed JSON: $path ({e})', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null
}

# ============================================================
# MACHINE STATE SCAN
# ============================================================

scan_machine_state() {
    # Comprehensive scan. Outputs a structured report to stdout as key=value pairs.
    echo "claude_installed=$(command -v claude &>/dev/null && echo true || echo false)"
    echo "claude_dir_exists=$([ -d "$CLAUDE_DIR" ] && echo true || echo false)"

    # MCP servers
    if [ -f "$CLAUDE_DIR/.mcp.json" ]; then
        local count=$($PYTHON -c "
import json
try:
    with open('$CLAUDE_DIR/.mcp.json') as f: d = json.load(f)
    servers = list(d.get('mcpServers', {}).keys())
    print(f'mcp_server_count={len(servers)}')
    print(f'mcp_servers={','.join(servers)}')
except: print('mcp_server_count=0')
" 2>/dev/null)
        echo "$count"
    else
        echo "mcp_server_count=0"
    fi

    # Settings
    echo "settings_json_exists=$([ -f "$CLAUDE_DIR/settings.json" ] && echo true || echo false)"
    echo "settings_local_exists=$([ -f "$CLAUDE_DIR/settings.local.json" ] && echo true || echo false)"

    # CLAUDE.md
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        local size_kb=$(du -k "$CLAUDE_DIR/CLAUDE.md" 2>/dev/null | cut -f1)
        echo "claude_md_exists=true"
        echo "claude_md_size_kb=${size_kb:-0}"
    else
        echo "claude_md_exists=false"
    fi

    # Previous systems
    echo "openclaw_exists=$([ -d "$HOME/.openclaw" ] && echo true || echo false)"
    echo "claude_setup_exists=$([ -d "$HOME/Documents/claude-setup" ] && echo true || echo false)"
    echo "hermes_exists=$([ -d "$HOME/.hermes" ] && echo true || echo false)"
    echo "clawd_existing=$([ -f "$CONFIG_DIR/config.json" ] && echo true || echo false)"

    # Active processes
    local claude_procs=$(pgrep -c -f "claude" 2>/dev/null || echo 0)
    echo "active_claude_processes=$claude_procs"

    # Cron jobs from other frameworks
    local cron_conflicts=$(crontab -l 2>/dev/null | grep -ci "openclaw\|hermes\|claude-setup" || echo 0)
    echo "cron_conflicts=$cron_conflicts"
}

show_preflight_report() {
    # Parse scan output and display formatted report
    local scan_output="$1"
    echo ""
    echo -e "  ${YELLOW}Machine State:${NC}"

    local installed=$(echo "$scan_output" | grep "claude_installed=" | cut -d= -f2)
    [ "$installed" = "true" ] && echo "    Claude Code: installed" || echo -e "    Claude Code: ${RED}NOT FOUND${NC}"

    local mcp_count=$(echo "$scan_output" | grep "mcp_server_count=" | cut -d= -f2)
    local mcp_names=$(echo "$scan_output" | grep "mcp_servers=" | cut -d= -f2)
    if [ "$mcp_count" -gt 0 ] 2>/dev/null; then
        echo "    .mcp.json: $mcp_count servers ($mcp_names)"
    elif [ -f "$CLAUDE_DIR/.mcp.json" ]; then
        echo "    .mcp.json: exists (0 servers or unparseable)"
    else
        echo "    .mcp.json: not found (will be created)"
    fi

    local sl_exists=$(echo "$scan_output" | grep "settings_local_exists=" | cut -d= -f2)
    [ "$sl_exists" = "true" ] && echo -e "    settings.local.json: exists ${GRAY}(will NOT be modified)${NC}"

    local md_exists=$(echo "$scan_output" | grep "claude_md_exists=" | cut -d= -f2)
    local md_size=$(echo "$scan_output" | grep "claude_md_size_kb=" | cut -d= -f2)
    [ "$md_exists" = "true" ] && echo "    CLAUDE.md: exists (${md_size}KB)"

    echo ""
    echo -e "  ${YELLOW}Previous systems:${NC}"
    local oc=$(echo "$scan_output" | grep "openclaw_exists=" | cut -d= -f2)
    [ "$oc" = "true" ] && echo -e "    OpenClaw: ${CYAN}detected${NC} (~/.openclaw)" || echo -e "    OpenClaw: ${GRAY}not found${NC}"
    local cs=$(echo "$scan_output" | grep "claude_setup_exists=" | cut -d= -f2)
    [ "$cs" = "true" ] && echo -e "    claude-setup: ${CYAN}detected${NC}" || echo -e "    claude-setup: ${GRAY}not found${NC}"
    local hm=$(echo "$scan_output" | grep "hermes_exists=" | cut -d= -f2)
    [ "$hm" = "true" ] && echo -e "    Hermes: ${CYAN}detected${NC}" || echo -e "    Hermes: ${GRAY}not found${NC}"

    local procs=$(echo "$scan_output" | grep "active_claude_processes=" | cut -d= -f2)
    if [ "$procs" -gt 0 ] 2>/dev/null; then
        echo ""
        echo -e "  ${YELLOW}Active services:${NC}"
        echo -e "    ${YELLOW}[WARN] $procs claude process(es) running${NC}"
    fi
    echo ""
}

# ============================================================
# BACKUP
# ============================================================

backup_file() {
    local path="$1"
    [ ! -f "$path" ] && return 1
    local backup_dir="$CONFIG_DIR/backup"
    mkdir -p "$backup_dir"
    local name=$(basename "$path")
    local ts=$(date +%Y%m%d-%H%M%S)
    local backup_path="$backup_dir/$name.$ts.bak"
    cp "$path" "$backup_path"
    # Verify
    [ -f "$backup_path" ] && [ -s "$backup_path" ] && echo "$backup_path" && return 0
    return 1
}

# ============================================================
# SMART MERGE HELPERS
# ============================================================

merge_mcp_json() {
    # Merge .mcp.json: keep existing servers, add memory
    local mcp_path="$1"
    local wrapper_dir="$2"
    local python_cmd="$3"

    if [ -f "$mcp_path" ]; then
        backup_file "$mcp_path" >/dev/null
        $python_cmd -c "
import json, sys
try:
    with open('$mcp_path') as f:
        raw = f.read()
        # Strip BOM
        if raw.startswith('\ufeff'): raw = raw[1:]
        existing = json.loads(raw)
    servers = existing.get('mcpServers', {})
except (json.JSONDecodeError, FileNotFoundError):
    servers = {}
servers['memory'] = {
    'command': '$python_cmd',
    'args': ['-X', 'utf8', '-m', 'mcp_memory.server'],
    'cwd': '$wrapper_dir/skills/memory-server'
}
with open('$mcp_path', 'w') as f:
    json.dump({'mcpServers': servers}, f, indent=2)
print(len(servers))
" 2>/dev/null
    else
        cat > "$mcp_path" << MCPEOF
{
  "mcpServers": {
    "memory": {
      "command": "$python_cmd",
      "args": ["-X", "utf8", "-m", "mcp_memory.server"],
      "cwd": "$wrapper_dir/skills/memory-server"
    }
  }
}
MCPEOF
        echo "1"
    fi
}

merge_settings_json() {
    # Merge settings.json: keep existing, add Lobster permissions from template
    local settings_path="$1"
    local template_path="$2"
    local python_cmd="$3"

    if [ -f "$settings_path" ]; then
        backup_file "$settings_path" >/dev/null
    fi

    $python_cmd -c "
import json, sys
# Load existing
existing = {}
try:
    with open('$settings_path') as f: existing = json.load(f)
except (FileNotFoundError, json.JSONDecodeError): pass

# Load template permissions
template_perms = []
try:
    with open('$template_path') as f: t = json.load(f)
    template_perms = t.get('permissions', {}).get('allow', [])
except (FileNotFoundError, json.JSONDecodeError): pass

# Merge permissions (dedup)
perms = existing.get('permissions', {})
current = perms.get('allow', [])
for p in template_perms:
    if p not in current:
        current.append(p)
perms['allow'] = current
existing['permissions'] = perms

with open('$settings_path', 'w') as f:
    json.dump(existing, f, indent=2)
print(len(current))
" 2>/dev/null
}

merge_claude_md() {
    # Merge CLAUDE.md: append Lobster sections if not present
    local md_path="$1"
    local template_content="$2"

    if [ -f "$md_path" ]; then
        backup_file "$md_path" >/dev/null
        if grep -q "Clawd-Lobster\|Boot Protocol" "$md_path" 2>/dev/null; then
            echo "exists"  # Already has Lobster sections
        else
            local size_kb=$(du -k "$md_path" 2>/dev/null | cut -f1)
            [ "$size_kb" -gt 100 ] 2>/dev/null && echo -e "  ${YELLOW}[WARN] CLAUDE.md is ${size_kb}KB — unusually large${NC}" >&2
            printf "\n\n# ============================================================\n# Clawd-Lobster (auto-appended by installer)\n# ============================================================\n\n%s" "$template_content" >> "$md_path"
            echo "merged"
        fi
    else
        echo "$template_content" > "$md_path"
        echo "created"
    fi
}

# ============================================================
# POST-INSTALL VERIFICATION
# ============================================================

test_installation() {
    local claude_dir="$1"
    local wrapper_dir="$2"
    local python_cmd="$3"
    local pass=0 fail=0

    # .mcp.json valid with memory server
    if $python_cmd -c "import json; d=json.load(open('$claude_dir/.mcp.json')); assert 'memory' in d['mcpServers']" 2>/dev/null; then
        echo -e "  ${GREEN}[PASS]${NC} .mcp.json: valid, memory server present"; ((pass++))
    else
        echo -e "  ${RED}[FAIL]${NC} .mcp.json: missing or no memory server"; ((fail++))
    fi

    # settings.json valid
    if $python_cmd -c "import json; json.load(open('$claude_dir/settings.json'))" 2>/dev/null; then
        echo -e "  ${GREEN}[PASS]${NC} settings.json: valid"; ((pass++))
    else
        echo -e "  ${RED}[FAIL]${NC} settings.json: missing or invalid"; ((fail++))
    fi

    # CLAUDE.md has Lobster content
    if grep -q "Clawd-Lobster\|Boot Protocol\|MCP Memory Server" "$claude_dir/CLAUDE.md" 2>/dev/null; then
        echo -e "  ${GREEN}[PASS]${NC} CLAUDE.md: contains Lobster sections"; ((pass++))
    else
        echo -e "  ${RED}[FAIL]${NC} CLAUDE.md: missing Lobster sections"; ((fail++))
    fi

    # Memory server importable
    if $python_cmd -c "import mcp_memory.server; print('ok')" 2>/dev/null | grep -q "ok"; then
        echo -e "  ${GREEN}[PASS]${NC} MCP Memory Server: importable"; ((pass++))
    else
        echo -e "  ${RED}[FAIL]${NC} MCP Memory Server: import failed"; ((fail++))
    fi

    echo ""
    echo "  Verification: $pass passed, $fail failed"
}
