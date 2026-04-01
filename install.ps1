# install.ps1 — Clawd-Lobster Setup (Master / Agent dual mode)
# Usage:
#   .\install.ps1                    # Interactive setup
#   .\install.ps1 -Mode master       # First-time master setup
#   .\install.ps1 -Mode agent -JoinCode "XXXX-XXXX"  # Join existing system

param(
    [ValidateSet("interactive", "master", "agent")]
    [string]$Mode = "interactive",
    [string]$JoinCode = ""
)

$ErrorActionPreference = "Stop"
$wrapperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$configDir = "$env:USERPROFILE\.clawd-lobster"
$configFile = "$configDir\config.json"
$claudeDir = "$env:USERPROFILE\.claude"

function Write-Step($step, $msg) {
    Write-Host "`n[$step] $msg" -ForegroundColor Cyan
}

function Write-OK($msg) {
    Write-Host "  [OK] $msg" -ForegroundColor Green
}

function Write-Skip($msg) {
    Write-Host "  [SKIP] $msg" -ForegroundColor Yellow
}

function Write-Fail($msg) {
    Write-Host "  [FAIL] $msg" -ForegroundColor Red
}

# ============================================================
# MODE SELECTION
# ============================================================

if ($Mode -eq "interactive") {
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Magenta
    Write-Host "     Clawd-Lobster Setup" -ForegroundColor Magenta
    Write-Host "     Claude Code Skills Wrapper" -ForegroundColor Gray
    Write-Host "  ========================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  [1] Master Setup  — I'm setting up a NEW system"
    Write-Host "  [2] Agent Setup   — I'm joining an EXISTING system"
    Write-Host ""
    $choice = Read-Host "  Select (1 or 2)"
    if ($choice -eq "2") {
        $Mode = "agent"
        if (-not $JoinCode) {
            $JoinCode = Read-Host "  Enter join code (or wrapper repo URL)"
        }
    } else {
        $Mode = "master"
    }
}

# ============================================================
# STEP 1: PREREQUISITES
# ============================================================

Write-Step "1/6" "Checking prerequisites"

# Node.js
$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
    $nodeVer = (node --version 2>&1).ToString().TrimStart('v')
    Write-OK "Node.js $nodeVer"
} else {
    Write-Fail "Node.js not found. Install from https://nodejs.org/"
    exit 1
}

# Python
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $pyVer = (python --version 2>&1).ToString()
    Write-OK "$pyVer"
} else {
    Write-Fail "Python not found. Install Python 3.11+"
    exit 1
}

# Git
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) { Write-OK "Git $(git --version)" }
else { Write-Fail "Git not found"; exit 1 }

# Claude Code
$claude = Get-Command claude -ErrorAction SilentlyContinue
if ($claude) {
    Write-OK "Claude Code installed"
} else {
    Write-Host "  Installing Claude Code..." -ForegroundColor Yellow
    npm install -g @anthropic-ai/claude-code
    Write-OK "Claude Code installed"
}

# GitHub CLI
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) { Write-OK "GitHub CLI installed" }
else { Write-Skip "GitHub CLI not found (optional but recommended)" }

# ============================================================
# STEP 2: AUTHENTICATION
# ============================================================

Write-Step "2/6" "Authentication"

# Claude auth
$claudeCreds = "$claudeDir\.credentials.json"
if (Test-Path $claudeCreds) {
    Write-OK "Claude Code authenticated"
} else {
    Write-Host "  Authenticating Claude Code..." -ForegroundColor Yellow
    claude auth login
    if (Test-Path $claudeCreds) { Write-OK "Claude Code authenticated" }
    else { Write-Fail "Claude auth failed"; exit 1 }
}

# GitHub auth (optional)
if ($gh) {
    $ghStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-OK "GitHub authenticated"
    } else {
        Write-Host "  Authenticating GitHub..." -ForegroundColor Yellow
        gh auth login
    }
}

# ============================================================
# STEP 3: CONFIG
# ============================================================

Write-Step "3/6" "Configuring Clawd-Lobster"

New-Item -ItemType Directory -Force -Path $configDir | Out-Null

$wsRoot = "$env:USERPROFILE\Documents\Workspace"
if (-not (Test-Path $wsRoot)) {
    New-Item -ItemType Directory -Force -Path $wsRoot | Out-Null
}

$config = @{
    wrapper_dir = $wrapperDir
    data_dir = $wrapperDir
    workspace_root = $wsRoot
    knowledge_dir = "$wrapperDir\knowledge"
    l4_provider = "github"
    oracle = @{
        enabled = $false
        wallet_dir = ""
        wallet_password = ""
        dsn = ""
        user = "CLAUDE_MEMORY"
        password = ""
    }
    embedding = @{
        provider = "none"
        model = "text-embedding-3-small"
        api_key = ""
    }
}

$config | ConvertTo-Json -Depth 3 | Set-Content $configFile -Encoding UTF8
Write-OK "Config saved to $configFile"

# ============================================================
# STEP 4: MCP MEMORY SERVER
# ============================================================

Write-Step "4/6" "Installing MCP Memory Server"

$mcpServerDir = "$wrapperDir\skills\memory-server"
Push-Location $mcpServerDir
pip install -e . --quiet 2>&1 | Out-Null
Pop-Location
Write-OK "MCP Memory Server installed"

# Configure Claude Code MCP
$mcpConfig = @{
    mcpServers = @{
        memory = @{
            command = "python"
            args = @("-X", "utf8", "-m", "mcp_memory.server")
            cwd = $mcpServerDir
        }
    }
}

New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
$mcpConfig | ConvertTo-Json -Depth 4 | Set-Content "$claudeDir\.mcp.json" -Encoding UTF8
Write-OK ".mcp.json configured"

# ============================================================
# STEP 5: CLAUDE.MD + SETTINGS
# ============================================================

Write-Step "5/6" "Setting up Claude Code config"

# Generate CLAUDE.md from template
$claudeMd = Get-Content "$wrapperDir\templates\global-CLAUDE.md" -Raw
$claudeMd = $claudeMd -replace '\{\{DATA_DIR\}\}', $wrapperDir
Set-Content "$claudeDir\CLAUDE.md" -Value $claudeMd -Encoding UTF8
Write-OK "CLAUDE.md generated"

# Settings.json (merge, don't overwrite)
$settingsPath = "$claudeDir\settings.json"
$settingsTemplate = Get-Content "$wrapperDir\templates\settings.json.template" -Raw | ConvertFrom-Json
if (Test-Path $settingsPath) {
    $existing = Get-Content $settingsPath -Raw | ConvertFrom-Json
    if (-not $existing.permissions) {
        $existing | Add-Member -NotePropertyName "permissions" -NotePropertyValue $settingsTemplate.permissions -Force
        $existing | ConvertTo-Json -Depth 5 | Set-Content $settingsPath -Encoding UTF8
        Write-OK "settings.json updated (merged permissions)"
    } else {
        Write-OK "settings.json already configured"
    }
} else {
    $settingsTemplate | ConvertTo-Json -Depth 5 | Set-Content $settingsPath -Encoding UTF8
    Write-OK "settings.json created"
}

# ============================================================
# STEP 6: SCHEDULER
# ============================================================

Write-Step "6/6" "Setting up scheduler"

# Register sync-all task (Windows Task Scheduler)
$taskName = "Clawd-Lobster Sync"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if (-not $existing) {
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -File `"$wrapperDir\scripts\sync-all.ps1`"" `
        -WorkingDirectory $wrapperDir

    $trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once -At (Get-Date)
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Clawd-Lobster: git sync + oracle sync + salience decay" 2>&1 | Out-Null
    Write-OK "Scheduled task '$taskName' registered (every 30 min)"
} else {
    Write-OK "Scheduled task already exists"
}

# ============================================================
# DONE
# ============================================================

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Green
Write-Host "     Clawd-Lobster installed!" -ForegroundColor Green
Write-Host "  ========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Wrapper:    $wrapperDir" -ForegroundColor Gray
Write-Host "  Config:     $configFile" -ForegroundColor Gray
Write-Host "  Workspaces: $wsRoot" -ForegroundColor Gray
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "    1. Create a workspace:  .\scripts\new-workspace.ps1 -name `"my-project`""
Write-Host "    2. Open Claude Code:    cd `"$wsRoot\my-project`" && claude"
Write-Host "    3. Migrate existing:    claude `"/migrate`" (inside Claude Code)"
Write-Host ""

if ($Mode -eq "master") {
    Write-Host "  To add another machine:" -ForegroundColor Yellow
    Write-Host "    Share this repo URL and run install.ps1 on the new machine"
    Write-Host ""
}
