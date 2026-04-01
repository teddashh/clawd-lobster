# sync-all.ps1 — Pull, push, and optional Oracle sync for all workspaces
# Scheduled to run every 30 minutes via OS task scheduler
# Usage: powershell -File sync-all.ps1 [-Pull] [-Push] [-Oracle] [-All]

param(
    [switch]$Pull,
    [switch]$Push,
    [switch]$Oracle,
    [switch]$All
)

if (-not $Pull -and -not $Push -and -not $Oracle) { $All = $true }

# Load config
$configFile = "$env:USERPROFILE\.clawd-lobster\config.json"
if (Test-Path $configFile) {
    $config = Get-Content $configFile -Raw | ConvertFrom-Json
    $wsRoot = $config.workspace_root
    $wrapperDir = $config.wrapper_dir
    $dataDir = $config.data_dir
} else {
    $docs = "$env:USERPROFILE\Documents"
    $wsRoot = "$docs\Workspace"
    $wrapperDir = "$docs\clawd-lobster"
    $dataDir = $wrapperDir
}

$logDir = "$wrapperDir\.claude-memory"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
$logFile = "$logDir\sync.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Log($msg) {
    $line = "[$timestamp] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

Log "=== Sync started ==="

# Discover all git repos under workspace root
$repos = @($wrapperDir)
if ($wrapperDir -ne $dataDir) { $repos += $dataDir }

# Add all workspace repos (auto-detect: any dir with .git/)
Get-ChildItem -Path $wsRoot -Recurse -Directory -Filter ".git" -Depth 3 -ErrorAction SilentlyContinue | ForEach-Object {
    $repos += $_.Parent.FullName
}
$repos = $repos | Sort-Object -Unique

# Step 1: Git Pull
if ($Pull -or $All) {
    Log "--- Step 1: Git Pull ---"
    foreach ($repo in $repos) {
        if (Test-Path "$repo\.git") {
            Push-Location $repo
            $result = git pull 2>&1
            $name = Split-Path $repo -Leaf
            if ($result -notmatch "Already up to date") {
                Log "  PULL $name : $result"
            }
            Pop-Location
        }
    }
    Log "  Pull complete"
}

# Step 2: Git Push
if ($Push -or $All) {
    Log "--- Step 2: Git Push ---"
    foreach ($repo in $repos) {
        if (Test-Path "$repo\.git") {
            Push-Location $repo
            $status = git status --porcelain 2>&1
            if ($status) {
                $name = Split-Path $repo -Leaf
                # Only add tracked files + known safe patterns (not git add -A)
                git add -u 2>&1 | Out-Null
                git add "*.md" "*.json" "*.py" "*.ps1" "*.sh" "*.toml" "*.yml" "*.yaml" "*.html" "*.css" "*.js" 2>&1 | Out-Null
                $staged = git diff --cached --name-only 2>&1
                if ($staged) {
                    git commit -m "auto-sync $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>&1 | Out-Null
                    git push 2>&1 | Out-Null
                    Log "  PUSH $name : committed and pushed"
                }
            }
            Pop-Location
        }
    }
    Log "  Push complete"
}

# Step 3: Oracle Sync (optional)
if ($Oracle -or $All) {
    $oracleScript = "$wrapperDir\scripts\oracle_sync.py"
    if (Test-Path $oracleScript) {
        Log "--- Step 3: Oracle Sync ---"
        try {
            $result = python -X utf8 $oracleScript 2>&1
            Log "  ORACLE: $($result | Select-String 'Sync complete')"
        } catch {
            Log "  ORACLE: skipped or error"
        }
    }
}

# Step 4: Salience Decay (once daily)
if ($All) {
    $decayMarker = "$wrapperDir\.claude-memory\.decay-last"
    $today = (Get-Date).ToString("yyyy-MM-dd")
    $lastDecay = if (Test-Path $decayMarker) { Get-Content $decayMarker } else { "" }

    if ($lastDecay -ne $today) {
        Log "--- Step 4: Salience Decay ---"
        $mcpPath = "$wrapperDir\skills\memory-server"
        if (Test-Path "$mcpPath\mcp_memory\server.py") {
            try {
                Push-Location $mcpPath
                $result = python -X utf8 -m mcp_memory.server --decay 2>&1
                Log "  DECAY: $($result | Select-String 'Decay complete')"
                Set-Content $decayMarker $today
                Pop-Location
            } catch {
                Log "  DECAY ERROR: $_"
                Pop-Location
            }
        }
    }
}

# Step 5: Update machine status
$machineConfigFile = "$env:USERPROFILE\.clawd-lobster\config.json"
if (Test-Path $machineConfigFile) {
    try {
        $machineConfig = Get-Content $machineConfigFile -Raw | ConvertFrom-Json
        $mid = $machineConfig.machine_id
        if ($mid) {
            $clientFile = "$wrapperDir\clients\$mid.json"
            if (Test-Path $clientFile) {
                $status = Get-Content $clientFile -Raw | ConvertFrom-Json
                $status.last_sync = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
                $status | ConvertTo-Json -Depth 3 | Set-Content $clientFile -Encoding UTF8
            }
        }
    } catch { }
}

Log "=== Sync finished ==="
