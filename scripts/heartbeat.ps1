# heartbeat.ps1 — Session Lifecycle Manager
# Ensures every registered workspace has a live Claude Code session.
# If a session is dead, it gets revived via claude --resume.
# Runs via OS scheduler (every 30 min alongside sync-all).
#
# Usage:
#   powershell -File heartbeat.ps1           # Check all workspaces
#   powershell -File heartbeat.ps1 -Domain work   # Only work workspaces

param(
    [string]$Domain = ""
)

$configFile = "$env:USERPROFILE\.clawd-lobster\config.json"
$wrapperDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Load config
if (Test-Path $configFile) {
    $config = Get-Content $configFile -Raw | ConvertFrom-Json
    $MachineId = $config.machine_id
    if (-not $Domain) { $Domain = $config.domain }
} else {
    Write-Host "[heartbeat] No config found. Run install.ps1 first."
    exit 1
}

# Load workspace registry
$registryFile = "$wrapperDir\workspaces.json"
if (-not (Test-Path $registryFile)) {
    Write-Host "[heartbeat] No workspaces.json found."
    exit 1
}
$registry = Get-Content $registryFile -Raw | ConvertFrom-Json

# Resolve workspace roots (support domain-based roots)
$wsRoots = @{}
if ($registry.domains) {
    foreach ($d in $registry.domains.PSObject.Properties) {
        $wsRoots[$d.Name] = $d.Value.workspace_root -replace '~', $env:USERPROFILE
    }
}
$defaultRoot = if ($config.workspace_root) { $config.workspace_root } else { "$env:USERPROFILE\Documents\Workspace" }

# Track results
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logDir = "$wrapperDir\.claude-memory"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
$logFile = "$logDir\heartbeat.log"

function Log($msg) {
    $line = "[$timestamp] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

Log "=== Heartbeat started (machine: $MachineId, domain: $Domain) ==="

# Get list of running claude processes and their working directories
$claudeProcesses = @()
try {
    # Check for running claude CLI processes
    $procs = Get-Process -Name "claude*" -ErrorAction SilentlyContinue
    foreach ($p in $procs) {
        try {
            # Try to get the working directory from command line
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)" -ErrorAction SilentlyContinue).CommandLine
            if ($cmdLine) { $claudeProcesses += $cmdLine }
        } catch { }
    }

    # Also check for terminal windows (Better Agent Terminal, Windows Terminal, etc.)
    $terminals = Get-Process -Name "BetterAgentTerminal", "WindowsTerminal", "powershell", "pwsh" -ErrorAction SilentlyContinue
    foreach ($t in $terminals) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId=$($t.Id)" -ErrorAction SilentlyContinue).CommandLine
            if ($cmdLine) { $claudeProcesses += $cmdLine }
        } catch { }
    }
} catch { }

$alive = 0
$revived = 0
$skipped = 0

foreach ($ws in $registry.workspaces) {
    # Filter by domain
    $shouldCheck = $false
    if ($Domain -eq "hybrid") { $shouldCheck = $true }
    elseif ($ws.deploy -eq "all") { $shouldCheck = $true }
    elseif ($ws.deploy -eq $Domain) { $shouldCheck = $true }
    elseif ($ws.domain -eq $Domain) { $shouldCheck = $true }

    if (-not $shouldCheck) {
        $skipped++
        continue
    }

    # Resolve workspace path
    $wsDomain = if ($ws.domain) { $ws.domain } else { "work" }
    $wsRoot = $wsRoots[$wsDomain]
    if (-not $wsRoot) { $wsRoot = $defaultRoot }
    $wsPath = "$wsRoot\$($ws.path)"

    if (-not (Test-Path $wsPath)) {
        Log "  [$($ws.id)] path not found, skipping"
        $skipped++
        continue
    }

    # Check if any claude process is running in this workspace
    $wsPathNorm = $wsPath.Replace('\', '/').ToLower()
    $isAlive = $false
    foreach ($cmd in $claudeProcesses) {
        if ($cmd -and $cmd.ToLower().Contains($ws.id)) { $isAlive = $true; break }
        if ($cmd -and $cmd.ToLower().Replace('\', '/').Contains($wsPathNorm)) { $isAlive = $true; break }
    }

    # Also check for .claude session files with recent activity
    $sessionDir = "$env:USERPROFILE\.claude\projects"
    if (-not $isAlive -and (Test-Path $sessionDir)) {
        $recentSessions = Get-ChildItem "$sessionDir\*\sessions\*.json" -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-1) }
        # If there's a recent session, consider it alive
        if ($recentSessions.Count -gt 0) {
            # Check if any session content references this workspace
            foreach ($sf in $recentSessions) {
                $content = Get-Content $sf.FullName -Raw -ErrorAction SilentlyContinue
                if ($content -and ($content.Contains($ws.id) -or $content.Contains($ws.path))) {
                    $isAlive = $true
                    break
                }
            }
        }
    }

    if ($isAlive) {
        Log "  [$($ws.id)] alive"
        $alive++
    } else {
        # Revive: find the most recent session for this workspace, then resume it
        Log "  [$($ws.id)] dead -> reviving..."
        try {
            $claudePath = (Get-Command claude -ErrorAction SilentlyContinue).Source
            if ($claudePath) {
                # Find the most recent session ID for this workspace
                $resumeArg = "--resume"
                $sessionDir = "$env:USERPROFILE\.claude\projects"
                if (Test-Path $sessionDir) {
                    $latestSession = Get-ChildItem "$sessionDir\*\sessions\*.json" -ErrorAction SilentlyContinue |
                        Where-Object {
                            $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
                            $content -and ($content.Contains($ws.id) -or $content.Contains($ws.path))
                        } |
                        Sort-Object LastWriteTime -Descending |
                        Select-Object -First 1
                    if ($latestSession) {
                        $sessionId = [System.IO.Path]::GetFileNameWithoutExtension($latestSession.Name)
                        $resumeArg = "--resume $sessionId"
                        Log "  [$($ws.id)] found session: $sessionId"
                    }
                }
                Start-Process -FilePath "cmd.exe" `
                    -ArgumentList "/c cd /d `"$wsPath`" && claude $resumeArg" `
                    -WindowStyle Minimized
                $revived++
                Log "  [$($ws.id)] revived (claude $resumeArg)"
            } else {
                Log "  [$($ws.id)] cannot revive: claude not in PATH"
                $skipped++
            }
        } catch {
            Log "  [$($ws.id)] revive failed: $_"
            $skipped++
        }
    }
}

Log "=== Heartbeat complete: $alive alive, $revived revived, $skipped skipped ==="

# Health check: memory.db sizes, last sync age, learned skills count
$healthData = @{}
foreach ($ws in $registry.workspaces) {
    $wsDomain = if ($ws.domain) { $ws.domain } else { "work" }
    $wsRoot2 = $wsRoots[$wsDomain]
    if (-not $wsRoot2) { $wsRoot2 = $defaultRoot }
    $dbPath = "$wsRoot2\$($ws.path)\.claude-memory\memory.db"
    if (Test-Path $dbPath) {
        $dbSize = (Get-Item $dbPath).Length
        $healthData[$ws.id] = @{ db_size_kb = [math]::Round($dbSize / 1024) }
    }
}

# Update machine status
$clientFile = "$wrapperDir\clients\$MachineId.json"
if (Test-Path $clientFile) {
    try {
        $status = Get-Content $clientFile -Raw | ConvertFrom-Json
        $status.last_sync = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        if (-not ($status | Get-Member "last_heartbeat" -ErrorAction SilentlyContinue)) {
            $status | Add-Member -NotePropertyName "last_heartbeat" -NotePropertyValue "" -Force
        }
        if (-not ($status | Get-Member "sessions_alive" -ErrorAction SilentlyContinue)) {
            $status | Add-Member -NotePropertyName "sessions_alive" -NotePropertyValue 0 -Force
        }
        if (-not ($status | Get-Member "health" -ErrorAction SilentlyContinue)) {
            $status | Add-Member -NotePropertyName "health" -NotePropertyValue @{} -Force
        }
        $status.last_heartbeat = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        $status.sessions_alive = $alive + $revived
        $status.health = $healthData
        $status | ConvertTo-Json -Depth 4 | Set-Content $clientFile -Encoding UTF8
    } catch { }
}
