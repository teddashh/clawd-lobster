# install-lib.ps1 — Helper functions for Clawd-Lobster installer
# Sourced by install.ps1: . "$wrapperDir\scripts\install-lib.ps1"

# ============================================================
# JSON / FILE SAFETY
# ============================================================

function Test-JsonFile($path) {
    <# Safely parse a JSON file. Handles BOM, UTF-16, malformed JSON.
       Returns parsed object or $null on failure. #>
    if (-not (Test-Path $path)) { return $null }
    try {
        $bytes = [System.IO.File]::ReadAllBytes($path)
        # Detect UTF-16 LE BOM (FF FE)
        if ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
            $text = [System.Text.Encoding]::Unicode.GetString($bytes)
        }
        # Detect UTF-8 BOM (EF BB BF)
        elseif ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $text = [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
        }
        else {
            $text = [System.Text.Encoding]::UTF8.GetString($bytes)
        }
        return $text | ConvertFrom-Json
    } catch {
        Write-Host "  [WARN] Malformed JSON: $path" -ForegroundColor Yellow
        return $null
    }
}

function Test-FileLock($path) {
    <# Check if a file is locked by another process. Returns $true if locked. #>
    if (-not (Test-Path $path)) { return $false }
    try {
        $stream = [System.IO.File]::Open($path, 'Open', 'ReadWrite', 'None')
        $stream.Close()
        return $false
    } catch {
        return $true
    }
}

# ============================================================
# MACHINE STATE SCAN
# ============================================================

function Scan-MachineState {
    <# Comprehensive scan of the machine's current state.
       Returns a hashtable with everything the installer needs to know. #>
    param([string]$claudeDir = "$env:USERPROFILE\.claude")

    $state = @{
        claude_installed    = [bool](Get-Command claude -ErrorAction SilentlyContinue)
        claude_dir_exists   = Test-Path $claudeDir
        mcp_json            = $null
        mcp_server_count    = 0
        mcp_servers         = @()
        settings_json       = $null
        settings_local_exists = Test-Path "$claudeDir\settings.local.json"
        claude_md_exists    = Test-Path "$claudeDir\CLAUDE.md"
        claude_md_size_kb   = 0
        openclaw            = $null
        claude_setup        = $null
        hermes              = $null
        clawd_existing      = $null
        active_processes    = @()
        scheduled_tasks     = @()
        locked_files        = @()
    }

    # MCP config
    if (Test-Path "$claudeDir\.mcp.json") {
        $state.mcp_json = Test-JsonFile "$claudeDir\.mcp.json"
        if ($state.mcp_json -and $state.mcp_json.mcpServers) {
            $state.mcp_servers = @($state.mcp_json.mcpServers.PSObject.Properties.Name)
            $state.mcp_server_count = $state.mcp_servers.Count
        }
    }

    # Settings
    if (Test-Path "$claudeDir\settings.json") {
        $state.settings_json = Test-JsonFile "$claudeDir\settings.json"
    }

    # CLAUDE.md size
    if ($state.claude_md_exists) {
        $state.claude_md_size_kb = [math]::Round((Get-Item "$claudeDir\CLAUDE.md").Length / 1024, 1)
    }

    # Previous systems
    $ocDir = "$env:USERPROFILE\.openclaw"
    if (Test-Path $ocDir) {
        $state.openclaw = @{
            path = $ocDir
            has_soul = Test-Path "$ocDir\SOUL.md"
            has_claude_md = Test-Path "$ocDir\CLAUDE.md"
            skill_count = (Get-ChildItem "$ocDir\skills" -Directory -ErrorAction SilentlyContinue).Count
            hook_count = (Get-ChildItem "$ocDir\hooks" -Directory -ErrorAction SilentlyContinue).Count
            extension_count = (Get-ChildItem "$ocDir\extensions" -Directory -ErrorAction SilentlyContinue).Count
            memory_count = (Get-ChildItem "$ocDir\memory\*.md" -ErrorAction SilentlyContinue).Count
        }
    }

    $csDir = "$env:USERPROFILE\Documents\claude-setup"
    if (Test-Path $csDir) {
        $state.claude_setup = @{
            path = $csDir
            has_workspace_map = Test-Path "$csDir\workspace-map.json"
            has_soul = Test-Path "$csDir\global\soul"
        }
    }

    $hmDir = "$env:USERPROFILE\.hermes"
    if (Test-Path $hmDir) {
        $state.hermes = @{
            path = $hmDir
            has_memory = Test-Path "$hmDir\memory"
            has_skills = Test-Path "$hmDir\skills"
        }
    }

    # Existing Clawd-Lobster install
    $clDir = "$env:USERPROFILE\.clawd-lobster"
    if (Test-Path "$clDir\config.json") {
        $state.clawd_existing = Test-JsonFile "$clDir\config.json"
    }

    # Active processes
    try {
        $claudeProcs = Get-Process -Name "claude*" -ErrorAction SilentlyContinue
        foreach ($p in $claudeProcs) {
            $state.active_processes += @{ name = $p.Name; pid = $p.Id }
        }
    } catch { }

    # Scheduled tasks (from any agent framework)
    try {
        $tasks = Get-ScheduledTask -ErrorAction SilentlyContinue |
            Where-Object { $_.TaskName -match "clawd|openclaw|hermes|claude-setup" }
        foreach ($t in $tasks) {
            $state.scheduled_tasks += @{ name = $t.TaskName; state = $t.State.ToString() }
        }
    } catch { }

    # File locks
    foreach ($f in @("$claudeDir\.mcp.json", "$claudeDir\settings.json", "$claudeDir\CLAUDE.md")) {
        if (Test-FileLock $f) { $state.locked_files += $f }
    }

    return $state
}

# ============================================================
# PREFLIGHT REPORT
# ============================================================

function Show-PreflightReport($state) {
    Write-Host ""
    Write-Host "  Machine State:" -ForegroundColor Yellow

    # Claude Code
    $ccStatus = if ($state.claude_installed) { "installed" } else { "NOT FOUND" }
    Write-Host "    Claude Code: $ccStatus"
    if ($state.claude_dir_exists) {
        if ($state.mcp_server_count -gt 0) {
            Write-Host "    .mcp.json: $($state.mcp_server_count) servers ($($state.mcp_servers -join ', '))"
        } elseif (Test-Path "$env:USERPROFILE\.claude\.mcp.json") {
            Write-Host "    .mcp.json: exists (0 servers or unparseable)"
        } else {
            Write-Host "    .mcp.json: not found (will be created)"
        }
        if ($state.settings_json) { Write-Host "    settings.json: exists" }
        if ($state.settings_local_exists) { Write-Host "    settings.local.json: exists (will NOT be modified)" -ForegroundColor Gray }
        if ($state.claude_md_exists) { Write-Host "    CLAUDE.md: exists ($($state.claude_md_size_kb) KB)" }
    }

    # Previous systems
    Write-Host ""
    Write-Host "  Previous systems:" -ForegroundColor Yellow
    if ($state.openclaw) {
        $oc = $state.openclaw
        Write-Host "    OpenClaw: detected ($($oc.path))" -ForegroundColor Cyan
        $details = @()
        if ($oc.has_soul) { $details += "SOUL.md" }
        if ($oc.skill_count -gt 0) { $details += "$($oc.skill_count) skills" }
        if ($oc.hook_count -gt 0) { $details += "$($oc.hook_count) hooks" }
        if ($oc.extension_count -gt 0) { $details += "$($oc.extension_count) extensions" }
        if ($oc.memory_count -gt 0) { $details += "$($oc.memory_count) memory files" }
        if ($details.Count -gt 0) { Write-Host "      $($details -join ', ')" }
    } else { Write-Host "    OpenClaw: not found" -ForegroundColor Gray }

    if ($state.claude_setup) { Write-Host "    claude-setup: detected ($($state.claude_setup.path))" -ForegroundColor Cyan }
    else { Write-Host "    claude-setup: not found" -ForegroundColor Gray }

    if ($state.hermes) { Write-Host "    Hermes Agent: detected ($($state.hermes.path))" -ForegroundColor Cyan }
    else { Write-Host "    Hermes Agent: not found" -ForegroundColor Gray }

    if ($state.clawd_existing) {
        $mid = $state.clawd_existing.machine_id
        Write-Host "    Clawd-Lobster: previously installed (machine: $mid)" -ForegroundColor Cyan
    }

    # Active services
    if ($state.active_processes.Count -gt 0 -or $state.scheduled_tasks.Count -gt 0 -or $state.locked_files.Count -gt 0) {
        Write-Host ""
        Write-Host "  Active services:" -ForegroundColor Yellow
        foreach ($p in $state.active_processes) {
            Write-Host "    [WARN] $($p.name) running (PID $($p.pid))" -ForegroundColor Yellow
        }
        foreach ($t in $state.scheduled_tasks) {
            Write-Host "    Task: $($t.name) ($($t.state))" -ForegroundColor Gray
        }
        foreach ($f in $state.locked_files) {
            Write-Host "    [WARN] File locked: $f" -ForegroundColor Yellow
        }
    }

    Write-Host ""
}

# ============================================================
# INSTALL PLAN DISPLAY
# ============================================================

function Show-InstallPlan($state, $hub, $env, $hubName, $machineId, $domain) {
    Write-Host "  Installation Plan ($hub-$env):" -ForegroundColor Yellow
    Write-Host "    [1] Prerequisites     — verify node, python, git, claude"
    Write-Host "    [2] Authentication    — check Claude Code + GitHub auth"
    $hubAction = if ($hub -eq "new") { "create new hub `"$hubName`"" } else { "join existing hub" }
    Write-Host "    [3] Hub setup         — $hubAction"
    Write-Host "    [4] Configuration     — write ~/.clawd-lobster/config.json"
    $mcpAction = if ($state.mcp_server_count -gt 0) { "merge .mcp.json (keep $($state.mcp_server_count) existing + add memory)" } else { "create .mcp.json" }
    Write-Host "    [5] MCP Memory Server — pip install, $mcpAction"
    $mdAction = if ($state.claude_md_exists) { "merge CLAUDE.md (append)" } else { "create CLAUDE.md" }
    $stAction = if ($state.settings_json) { "merge settings.json" } else { "create settings.json" }
    Write-Host "    [6] Claude Code setup — $mdAction, $stAction"
    Write-Host "    [7] Workspaces        — deploy registered workspaces"
    Write-Host "    [8] Scheduler         — create sync + heartbeat tasks"
    $migAction = if ($env -eq "absorb") { "absorb detected systems" } else { "skip (fresh mode)" }
    Write-Host "    [9] Migration         — $migAction"
    Write-Host ""
}

# ============================================================
# INSTALL STATE TRACKING
# ============================================================

function Initialize-InstallState($configDir, $params) {
    $stateFile = "$configDir\install-state.json"
    if (Test-Path $stateFile) {
        try { return Get-Content $stateFile -Raw | ConvertFrom-Json } catch { }
    }
    $state = @{
        version = "1.0"
        started_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        completed_steps = @()
        current_step = $null
        failed_step = $null
        error = $null
        params = $params
        backups = @()
    }
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    $state | ConvertTo-Json -Depth 3 | Set-Content $stateFile -Encoding UTF8
    return $state
}

function Set-StepComplete($configDir, [ref]$state, $step) {
    if ($step -notin $state.Value.completed_steps) {
        $state.Value.completed_steps += $step
    }
    $state.Value.current_step = $null
    $state.Value | ConvertTo-Json -Depth 3 | Set-Content "$configDir\install-state.json" -Encoding UTF8
}

function Set-StepFailed($configDir, [ref]$state, $step, $errorMsg) {
    $state.Value.failed_step = $step
    $state.Value.error = $errorMsg
    $state.Value | ConvertTo-Json -Depth 3 | Set-Content "$configDir\install-state.json" -Encoding UTF8
}

function Get-ResumePoint($state) {
    if ($state.failed_step) { return $state.failed_step }
    $allSteps = 1..9
    foreach ($s in $allSteps) {
        if ($s -notin $state.completed_steps) { return $s }
    }
    return 10  # all done
}

# ============================================================
# BACKUP & ROLLBACK
# ============================================================

function Backup-File($path, $configDir, [ref]$installState) {
    <# Backup a file before modification. Returns backup path or $null. #>
    if (-not (Test-Path $path)) { return $null }
    $backupDir = "$configDir\backup"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $name = Split-Path $path -Leaf
    $ts = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupPath = "$backupDir\$name.$ts.bak"
    Copy-Item $path $backupPath -Force
    # Verify backup
    if (-not (Test-Path $backupPath) -or (Get-Item $backupPath).Length -eq 0) {
        Write-Host "  [WARN] Backup verification failed: $backupPath" -ForegroundColor Yellow
        return $null
    }
    if ($installState) {
        $installState.Value.backups += @{ original = $path; backup = $backupPath }
    }
    return $backupPath
}

function Invoke-Rollback($configDir) {
    <# Restore all backups from install-state.json. #>
    $stateFile = "$configDir\install-state.json"
    if (-not (Test-Path $stateFile)) {
        Write-Host "  [FAIL] No install state found for rollback" -ForegroundColor Red
        return
    }
    $state = Get-Content $stateFile -Raw | ConvertFrom-Json
    $restored = 0
    foreach ($b in $state.backups) {
        if (Test-Path $b.backup) {
            Copy-Item $b.backup $b.original -Force
            Write-Host "  [OK] Restored: $($b.original)" -ForegroundColor Green
            $restored++
        }
    }
    # Remove scheduled tasks created by this install
    foreach ($taskName in @("Clawd-Lobster Sync", "Clawd-Lobster Heartbeat")) {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($task) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
            Write-Host "  [OK] Removed task: $taskName" -ForegroundColor Green
        }
    }
    Write-Host "  Rollback complete: $restored files restored" -ForegroundColor Green
}

# ============================================================
# SMART MERGE HELPERS
# ============================================================

function Merge-McpJson($existingPath, $mcpServerDir, $pythonCmd) {
    <# Merge: keep all existing MCP servers, add memory server.
       Handles malformed JSON, BOM, encoding issues. #>
    $merged = @{ mcpServers = @{} }
    if (Test-Path $existingPath) {
        $existing = Test-JsonFile $existingPath
        if ($existing -and $existing.mcpServers) {
            foreach ($prop in $existing.mcpServers.PSObject.Properties) {
                $merged.mcpServers[$prop.Name] = $prop.Value
            }
        }
    }
    # Detect python command
    if (-not $pythonCmd) { $pythonCmd = "python" }
    # Add or update memory server
    $merged.mcpServers["memory"] = @{
        command = $pythonCmd
        args = @("-X", "utf8", "-m", "mcp_memory.server")
        cwd = $mcpServerDir
    }
    return $merged
}

function Merge-Settings($existingPath, $templatePath) {
    <# Merge: keep existing permissions/hooks, add Lobster permissions from template.
       Never touches settings.local.json. #>
    $settings = @{}
    if (Test-Path $existingPath) {
        $settings = Test-JsonFile $existingPath
        if (-not $settings) { $settings = @{} }
    }

    # Read Lobster permissions from template (not hardcoded)
    $lobsterAllow = @()
    if (Test-Path $templatePath) {
        $template = Test-JsonFile $templatePath
        if ($template -and $template.permissions -and $template.permissions.allow) {
            $lobsterAllow = @($template.permissions.allow)
        }
    }

    # Ensure permissions.allow exists
    if (-not $settings.permissions) {
        $settings | Add-Member -NotePropertyName "permissions" -NotePropertyValue @{ allow = @() } -Force
    }
    if (-not $settings.permissions.allow) {
        $settings.permissions | Add-Member -NotePropertyName "allow" -NotePropertyValue @() -Force
    }

    # Add missing Lobster permissions (dedup)
    $currentAllow = @($settings.permissions.allow)
    foreach ($perm in $lobsterAllow) {
        if ($perm -notin $currentAllow) { $currentAllow += $perm }
    }
    $settings.permissions.allow = $currentAllow

    return $settings
}

function Merge-ClaudeMd($existingPath, $templateContent) {
    <# Merge: append Lobster sections to existing CLAUDE.md.
       Skips if already present. Warns if file is very large. #>
    if (-not (Test-Path $existingPath)) { return $templateContent }

    $existing = Get-Content $existingPath -Raw -Encoding UTF8

    # Size warning
    $sizeKb = [math]::Round($existing.Length / 1024, 1)
    if ($sizeKb -gt 100) {
        Write-Host "  [WARN] CLAUDE.md is $sizeKb KB — unusually large" -ForegroundColor Yellow
    }

    # Section-level dedup: check for key Lobster sections
    if ($existing -match "## Boot Protocol" -and $existing -match "## MCP Memory Server") {
        return $existing  # Already has Lobster sections
    }

    # Append
    $separator = "`n`n# ============================================================`n# Clawd-Lobster (auto-appended by installer)`n# ============================================================`n`n"
    return $existing + $separator + $templateContent
}

# ============================================================
# POST-INSTALL VERIFICATION
# ============================================================

function Test-Installation($claudeDir, $wrapperDir, $pythonCmd) {
    <# Verify all outputs are valid after installation. Returns pass/fail counts. #>
    $pass = 0; $fail = 0

    # .mcp.json valid and has memory server
    $mcp = Test-JsonFile "$claudeDir\.mcp.json"
    if ($mcp -and $mcp.mcpServers -and $mcp.mcpServers.memory) {
        Write-Host "  [PASS] .mcp.json: valid, memory server present" -ForegroundColor Green; $pass++
    } else {
        Write-Host "  [FAIL] .mcp.json: missing or no memory server" -ForegroundColor Red; $fail++
    }

    # settings.json valid
    $settings = Test-JsonFile "$claudeDir\settings.json"
    if ($settings) {
        Write-Host "  [PASS] settings.json: valid" -ForegroundColor Green; $pass++
    } else {
        Write-Host "  [FAIL] settings.json: missing or invalid" -ForegroundColor Red; $fail++
    }

    # CLAUDE.md exists and has Lobster content
    if (Test-Path "$claudeDir\CLAUDE.md") {
        $md = Get-Content "$claudeDir\CLAUDE.md" -Raw
        if ($md -match "Clawd-Lobster|Boot Protocol|MCP Memory Server") {
            Write-Host "  [PASS] CLAUDE.md: contains Lobster sections" -ForegroundColor Green; $pass++
        } else {
            Write-Host "  [WARN] CLAUDE.md: exists but missing Lobster sections" -ForegroundColor Yellow; $fail++
        }
    } else {
        Write-Host "  [FAIL] CLAUDE.md: not found" -ForegroundColor Red; $fail++
    }

    # Memory server importable
    if ($pythonCmd) {
        $importResult = & $pythonCmd -c "import mcp_memory.server; print('ok')" 2>&1
        if ($importResult -match "ok") {
            Write-Host "  [PASS] MCP Memory Server: importable" -ForegroundColor Green; $pass++
        } else {
            Write-Host "  [FAIL] MCP Memory Server: import failed" -ForegroundColor Red; $fail++
        }
    }

    # Scheduled tasks (Windows only)
    foreach ($taskName in @("Clawd-Lobster Sync", "Clawd-Lobster Heartbeat")) {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "  [PASS] Task: $taskName" -ForegroundColor Green; $pass++
        } else {
            Write-Host "  [WARN] Task: $taskName not found" -ForegroundColor Yellow
        }
    }

    return @{ pass = $pass; fail = $fail }
}
