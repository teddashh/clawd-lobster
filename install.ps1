# install.ps1 — Clawd-Lobster Setup (Master / Agent dual mode)
# Usage:
#   .\install.ps1                                        # Interactive
#   .\install.ps1 -Mode master -MachineId "my-server"    # Headless master
#   .\install.ps1 -Mode agent  -MachineId "my-laptop"    # Headless agent

param(
    [ValidateSet("interactive", "master", "agent")]
    [string]$Mode = "interactive",
    [string]$MachineId = "",
    [string]$JoinCode = ""
)

$ErrorActionPreference = "Stop"
$wrapperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$configDir = "$env:USERPROFILE\.clawd-lobster"
$configFile = "$configDir\config.json"
$claudeDir = "$env:USERPROFILE\.claude"

function Write-Step($step, $msg) { Write-Host "`n[$step] $msg" -ForegroundColor Cyan }
function Write-OK($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Skip($msg) { Write-Host "  [SKIP] $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "  [FAIL] $msg" -ForegroundColor Red }

# ============================================================
# MODE + MACHINE ID
# ============================================================

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Magenta
Write-Host "     Clawd-Lobster Setup" -ForegroundColor Magenta
Write-Host "     Claude Code Skills Wrapper" -ForegroundColor Gray
Write-Host "  ========================================" -ForegroundColor Magenta
Write-Host ""

if ($Mode -eq "interactive") {
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

# Machine ID
if (-not $MachineId) {
    $defaultId = ($env:COMPUTERNAME).ToLower() -replace '[^a-z0-9-]', '-'
    $MachineId = Read-Host "  Name this machine [$defaultId]"
    if (-not $MachineId) { $MachineId = $defaultId }
}
Write-Host ""
Write-Host "  Mode: $Mode | Machine: $MachineId" -ForegroundColor Cyan

# ============================================================
# STEP 1: PREREQUISITES
# ============================================================

Write-Step "1/7" "Checking prerequisites"

$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) { Write-OK "Node.js $(node --version)" }
else { Write-Fail "Node.js not found. Install from https://nodejs.org/"; exit 1 }

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) { Write-OK "$(python --version)" }
else { Write-Fail "Python 3.11+ not found"; exit 1 }

$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) { Write-OK "Git $(git --version)" }
else { Write-Fail "Git not found"; exit 1 }

$claude = Get-Command claude -ErrorAction SilentlyContinue
if ($claude) { Write-OK "Claude Code installed" }
else {
    Write-Host "  Installing Claude Code..." -ForegroundColor Yellow
    npm install -g @anthropic-ai/claude-code
    Write-OK "Claude Code installed"
}

$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) { Write-OK "GitHub CLI installed" }
else { Write-Skip "GitHub CLI not found (optional but recommended)" }

# ============================================================
# STEP 2: AUTHENTICATION
# ============================================================

Write-Step "2/7" "Authentication"

$claudeCreds = "$claudeDir\.credentials.json"
if (Test-Path $claudeCreds) { Write-OK "Claude Code authenticated" }
else {
    Write-Host "  Authenticating Claude Code..." -ForegroundColor Yellow
    claude auth login
    if (Test-Path $claudeCreds) { Write-OK "Authenticated" }
    else { Write-Fail "Claude auth failed"; exit 1 }
}

if ($gh) {
    $ghStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) { Write-OK "GitHub authenticated" }
    else {
        Write-Host "  Authenticating GitHub..." -ForegroundColor Yellow
        gh auth login
    }
}

# ============================================================
# STEP 3: CONFIG
# ============================================================

Write-Step "3/7" "Configuring Clawd-Lobster"

New-Item -ItemType Directory -Force -Path $configDir | Out-Null

$wsRoot = "$env:USERPROFILE\Documents\Workspace"
if (-not (Test-Path $wsRoot)) {
    New-Item -ItemType Directory -Force -Path $wsRoot | Out-Null
}

$config = @{
    machine_id = $MachineId
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
Write-OK "Config saved (machine: $MachineId)"

# ============================================================
# STEP 4: MCP MEMORY SERVER
# ============================================================

Write-Step "4/7" "Installing MCP Memory Server"

$mcpServerDir = "$wrapperDir\skills\memory-server"
Push-Location $mcpServerDir
$pipResult = pip install -e . --quiet 2>&1
Pop-Location
if ($LASTEXITCODE -ne 0) { Write-Fail "pip install failed: $pipResult"; exit 1 }
Write-OK "MCP Memory Server installed (21 tools)"

New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
@{
    mcpServers = @{
        memory = @{
            command = "python"
            args = @("-X", "utf8", "-m", "mcp_memory.server")
            cwd = $mcpServerDir
        }
    }
} | ConvertTo-Json -Depth 4 | Set-Content "$claudeDir\.mcp.json" -Encoding UTF8
Write-OK ".mcp.json configured"

# ============================================================
# STEP 5: CLAUDE.MD + SETTINGS
# ============================================================

Write-Step "5/7" "Setting up Claude Code config"

$claudeMd = Get-Content "$wrapperDir\templates\global-CLAUDE.md" -Raw
$claudeMd = $claudeMd -replace '\{\{DATA_DIR\}\}', $wrapperDir
Set-Content "$claudeDir\CLAUDE.md" -Value $claudeMd -Encoding UTF8
Write-OK "CLAUDE.md generated"

$settingsPath = "$claudeDir\settings.json"
if (-not (Test-Path $settingsPath) -or (Get-Content $settingsPath -Raw) -eq "{}") {
    Copy-Item "$wrapperDir\templates\settings.json.template" $settingsPath
    Write-OK "settings.json created"
} else {
    Write-OK "settings.json already configured"
}

# ============================================================
# STEP 6: DEPLOY WORKSPACES (from workspaces.json)
# ============================================================

Write-Step "6/7" "Deploying workspaces"

$registryFile = "$wrapperDir\workspaces.json"
$deployed = @()

if (Test-Path $registryFile) {
    $registry = Get-Content $registryFile -Raw | ConvertFrom-Json
    foreach ($ws in $registry.workspaces) {
        $wsPath = "$wsRoot\$($ws.path)"

        if (Test-Path $wsPath) {
            Write-OK "$($ws.id) (exists)"
        } elseif ($ws.repo -and $gh) {
            git clone "https://github.com/$($ws.repo).git" $wsPath 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { Write-OK "$($ws.id) (cloned)" }
            else {
                New-Item -ItemType Directory -Force -Path $wsPath | Out-Null
                Write-Skip "$($ws.id) (clone failed, created empty)"
            }
        } else {
            New-Item -ItemType Directory -Force -Path $wsPath | Out-Null
            Write-OK "$($ws.id) (created)"
        }

        # Init memory
        $memPath = "$wsPath\.claude-memory"
        if (-not (Test-Path "$memPath\memory.db")) {
            New-Item -ItemType Directory -Force -Path $memPath | Out-Null
            python "$wrapperDir\scripts\init_db.py" "$memPath\memory.db" 2>&1 | Out-Null
        }
        $deployed += $ws.id
    }
}

Write-Host "  Deployed $($deployed.Count) workspaces" -ForegroundColor Green

# ============================================================
# STEP 7: SCHEDULER + MACHINE REGISTRATION
# ============================================================

Write-Step "7/7" "Scheduler + machine registration"

$taskName = "Clawd-Lobster Sync"
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if (-not $existingTask) {
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -File `"$wrapperDir\scripts\sync-all.ps1`"" `
        -WorkingDirectory $wrapperDir
    $trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once -At (Get-Date)
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Clawd-Lobster: git sync + salience decay" 2>&1 | Out-Null
    Write-OK "Scheduled task registered (every 30 min)"
} else {
    Write-OK "Scheduled task already exists"
}

# Register this machine
$clientsDir = "$wrapperDir\clients"
New-Item -ItemType Directory -Force -Path $clientsDir | Out-Null

$machineStatus = @{
    machine_id = $MachineId
    hostname = $env:COMPUTERNAME
    os = "Windows $([System.Environment]::OSVersion.Version.Major)"
    mode = $Mode
    registered = (Get-Date -Format "yyyy-MM-dd")
    last_sync = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    deployed_workspaces = $deployed
    claude_version = try { (claude --version 2>&1).ToString().Trim() } catch { "unknown" }
    memory_server_version = "0.2.0"
}

$machineStatus | ConvertTo-Json -Depth 3 | Set-Content "$clientsDir\$MachineId.json" -Encoding UTF8
Write-OK "Machine registered: $MachineId"

# ============================================================
# DONE
# ============================================================

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Green
Write-Host "     Clawd-Lobster installed!" -ForegroundColor Green
Write-Host "  ========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Machine:    $MachineId" -ForegroundColor Gray
Write-Host "  Wrapper:    $wrapperDir" -ForegroundColor Gray
Write-Host "  Config:     $configFile" -ForegroundColor Gray
Write-Host "  Workspaces: $($deployed.Count) deployed" -ForegroundColor Gray
Write-Host ""

# Show fleet status
$fleetFiles = Get-ChildItem "$clientsDir\*.json" -ErrorAction SilentlyContinue
if ($fleetFiles.Count -gt 1) {
    Write-Host "  Your fleet:" -ForegroundColor Yellow
    foreach ($f in $fleetFiles) {
        $c = Get-Content $f.FullName -Raw | ConvertFrom-Json
        $isCurrent = if ($c.machine_id -eq $MachineId) { " <-- this machine" } else { "" }
        Write-Host "    $($c.machine_id) ($($c.mode)) — $($c.deployed_workspaces.Count) workspaces$isCurrent" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "    1. Create workspace:  .\scripts\new-workspace.ps1 -name `"my-project`""
Write-Host "    2. Open Claude Code:  cd `"$wsRoot\my-project`" && claude"
Write-Host "    3. Migrate existing:  claude `"/migrate`" (inside Claude Code)"
Write-Host ""
