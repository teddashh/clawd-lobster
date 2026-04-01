# install.ps1 — Clawd-Lobster Setup
# Usage:
#   .\install.ps1                                         # Interactive
#   .\install.ps1 -Lang en -Hub new -Env fresh -MachineId "my-server"  # Headless

param(
    [ValidateSet("", "zh-TW", "en", "zh-CN", "ja", "ko")]
    [string]$Lang = "",
    [ValidateSet("", "new", "join")]
    [string]$Hub = "",
    [ValidateSet("", "fresh", "absorb")]
    [string]$Env = "",
    [string]$MachineId = "",
    [string]$JoinCode = "",
    [ValidateSet("", "work", "personal", "hybrid")]
    [string]$Domain = ""
)

$ErrorActionPreference = "Stop"
$wrapperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$configDir = "$env:USERPROFILE\.clawd-lobster"
$configFile = "$configDir\config.json"
$claudeDir = "$env:USERPROFILE\.claude"

# ============================================================
# i18n STRINGS
# ============================================================

$i18n = @{
    "en" = @{
        title = "Clawd-Lobster Setup"
        subtitle = "Claude Code Skills Wrapper"
        lang_prompt = "Select language"
        round1_title = "What are you setting up?"
        round1_a = "New system (I'm the first machine / creating a new Hub)"
        round1_b = "Join existing Hub (I'm an additional machine)"
        round2_title = "Environment status?"
        round2_a = "Fresh start (brand new, nothing to import)"
        round2_b = "Absorb previous system (OpenClaw, Hermes, claude-setup, etc.)"
        domain_title = "This machine is for:"
        domain_work = "Work — deploy work workspaces"
        domain_personal = "Personal — deploy personal workspaces"
        domain_hybrid = "Hybrid — deploy everything"
        machine_prompt = "Name this machine"
        join_prompt = "Enter Hub URL or join code"
        step_prereq = "Checking prerequisites"
        step_auth = "Authentication"
        step_config = "Configuring"
        step_mcp = "Installing MCP Memory Server"
        step_claude = "Setting up Claude Code"
        step_workspace = "Deploying workspaces"
        step_sched = "Scheduler + registration"
        step_migrate = "Absorbing previous system"
        done = "Clawd-Lobster installed!"
        fleet_title = "Your fleet"
        next_title = "Next steps"
        this_machine = "this machine"
    }
    "zh-TW" = @{
        title = "Clawd-Lobster 安裝精靈"
        subtitle = "Claude Code 技能包裝器"
        lang_prompt = "選擇語言"
        round1_title = "你要做什麼？"
        round1_a = "建立新系統（我是第一台機器 / 建立新的 Hub）"
        round1_b = "加入現有 Hub（我是額外的機器）"
        round2_title = "環境狀態？"
        round2_a = "全新開始（什麼都沒有，從零開始）"
        round2_b = "吸收舊系統（OpenClaw、Hermes、claude-setup 等）"
        domain_title = "這台機器的用途："
        domain_work = "工作 — 部署工作用工作區"
        domain_personal = "個人 — 部署個人工作區"
        domain_hybrid = "混合 — 全部部署"
        machine_prompt = "幫這台機器命名"
        join_prompt = "輸入 Hub 網址或加入碼"
        step_prereq = "檢查前置需求"
        step_auth = "身份驗證"
        step_config = "設定中"
        step_mcp = "安裝 MCP 記憶伺服器"
        step_claude = "設定 Claude Code"
        step_workspace = "部署工作區"
        step_sched = "排程 + 機器註冊"
        step_migrate = "吸收舊系統中"
        done = "Clawd-Lobster 安裝完成！"
        fleet_title = "你的機器群"
        next_title = "接下來"
        this_machine = "本機"
    }
    "zh-CN" = @{
        title = "Clawd-Lobster 安装向导"
        subtitle = "Claude Code 技能封装器"
        lang_prompt = "选择语言"
        round1_title = "你要做什么？"
        round1_a = "创建新系统（我是第一台机器 / 创建新 Hub）"
        round1_b = "加入现有 Hub（我是额外的机器）"
        round2_title = "环境状态？"
        round2_a = "全新开始（什么都没有，从零开始）"
        round2_b = "吸收旧系统（OpenClaw、Hermes、claude-setup 等）"
        domain_title = "这台机器的用途："
        domain_work = "工作 — 部署工作用工作区"
        domain_personal = "个人 — 部署个人工作区"
        domain_hybrid = "混合 — 全部部署"
        machine_prompt = "给这台机器命名"
        join_prompt = "输入 Hub 地址或加入码"
        step_prereq = "检查前置需求"
        step_auth = "身份验证"
        step_config = "配置中"
        step_mcp = "安装 MCP 记忆服务器"
        step_claude = "设置 Claude Code"
        step_workspace = "部署工作区"
        step_sched = "调度 + 机器注册"
        step_migrate = "吸收旧系统中"
        done = "Clawd-Lobster 安装完成！"
        fleet_title = "你的机器群"
        next_title = "下一步"
        this_machine = "本机"
    }
    "ja" = @{
        title = "Clawd-Lobster セットアップ"
        subtitle = "Claude Code スキルラッパー"
        lang_prompt = "言語を選択"
        round1_title = "何をセットアップしますか？"
        round1_a = "新しいシステム（最初のマシン / 新しいHubを作成）"
        round1_b = "既存のHubに参加（追加マシン）"
        round2_title = "環境の状態は？"
        round2_a = "新規スタート（何もない状態から）"
        round2_b = "既存システムを吸収（OpenClaw、Hermes、claude-setup等）"
        domain_title = "このマシンの用途："
        domain_work = "仕事 — 仕事用ワークスペースをデプロイ"
        domain_personal = "個人 — 個人ワークスペースをデプロイ"
        domain_hybrid = "ハイブリッド — すべてデプロイ"
        machine_prompt = "このマシンの名前"
        join_prompt = "Hub URLまたは参加コードを入力"
        step_prereq = "前提条件の確認"
        step_auth = "認証"
        step_config = "設定中"
        step_mcp = "MCPメモリサーバーのインストール"
        step_claude = "Claude Codeの設定"
        step_workspace = "ワークスペースのデプロイ"
        step_sched = "スケジューラー + マシン登録"
        step_migrate = "既存システムの吸収中"
        done = "Clawd-Lobster インストール完了！"
        fleet_title = "マシン一覧"
        next_title = "次のステップ"
        this_machine = "このマシン"
    }
    "ko" = @{
        title = "Clawd-Lobster 설치"
        subtitle = "Claude Code 스킬 래퍼"
        lang_prompt = "언어 선택"
        round1_title = "무엇을 설정하시겠습니까?"
        round1_a = "새 시스템 (첫 번째 머신 / 새 Hub 생성)"
        round1_b = "기존 Hub에 참여 (추가 머신)"
        round2_title = "환경 상태?"
        round2_a = "새로 시작 (처음부터)"
        round2_b = "기존 시스템 흡수 (OpenClaw, Hermes, claude-setup 등)"
        domain_title = "이 머신의 용도:"
        domain_work = "업무 — 업무 워크스페이스 배포"
        domain_personal = "개인 — 개인 워크스페이스 배포"
        domain_hybrid = "하이브리드 — 전부 배포"
        machine_prompt = "이 머신의 이름"
        join_prompt = "Hub URL 또는 참여 코드 입력"
        step_prereq = "전제 조건 확인"
        step_auth = "인증"
        step_config = "구성 중"
        step_mcp = "MCP 메모리 서버 설치"
        step_claude = "Claude Code 설정"
        step_workspace = "워크스페이스 배포"
        step_sched = "스케줄러 + 머신 등록"
        step_migrate = "기존 시스템 흡수 중"
        done = "Clawd-Lobster 설치 완료!"
        fleet_title = "머신 목록"
        next_title = "다음 단계"
        this_machine = "이 머신"
    }
}

function T($key) { return $i18n[$Lang][$key] }
function Write-Step($step, $key) { Write-Host "`n[$step] $(T $key)" -ForegroundColor Cyan }
function Write-OK($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Skip($msg) { Write-Host "  [SKIP] $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "  [FAIL] $msg" -ForegroundColor Red }

# ============================================================
# LANGUAGE SELECTION
# ============================================================

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Magenta
Write-Host "     Clawd-Lobster" -ForegroundColor Magenta
Write-Host "     Claude Code Skills Wrapper" -ForegroundColor Gray
Write-Host "  ========================================" -ForegroundColor Magenta
Write-Host ""

if (-not $Lang) {
    Write-Host "  Select language:"
    Write-Host ""
    Write-Host "    [1] English"
    Write-Host "    [2] 繁體中文 (台灣)"
    Write-Host "    [3] 简体中文"
    Write-Host "    [4] 日本語"
    Write-Host "    [5] 한국어"
    Write-Host ""
    $langChoice = Read-Host "  (1-5)"
    switch ($langChoice) {
        "2" { $Lang = "zh-TW" }
        "3" { $Lang = "zh-CN" }
        "4" { $Lang = "ja" }
        "5" { $Lang = "ko" }
        default { $Lang = "en" }
    }
}

# ============================================================
# ROUND 1: NEW HUB OR JOIN?
# ============================================================

if (-not $Hub) {
    Write-Host ""
    Write-Host "  $(T 'round1_title')" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    [1] $(T 'round1_a')"
    Write-Host "    [2] $(T 'round1_b')"
    Write-Host ""
    $r1 = Read-Host "  (1/2)"
    if ($r1 -eq "2") { $Hub = "join" } else { $Hub = "new" }
}

# ============================================================
# ROUND 2: FRESH OR ABSORB?
# ============================================================

if (-not $Env) {
    Write-Host ""
    Write-Host "  $(T 'round2_title')" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    [1] $(T 'round2_a')"
    Write-Host "    [2] $(T 'round2_b')"
    Write-Host ""
    $r2 = Read-Host "  (1/2)"
    if ($r2 -eq "2") { $Env = "absorb" } else { $Env = "fresh" }
}

# Join code for agent mode
if ($Hub -eq "join" -and -not $JoinCode) {
    Write-Host ""
    $JoinCode = Read-Host "  $(T 'join_prompt')"
}

# ============================================================
# MACHINE ID
# ============================================================

if (-not $MachineId) {
    $defaultId = ($env:COMPUTERNAME).ToLower() -replace '[^a-z0-9-]', '-'
    Write-Host ""
    $MachineId = Read-Host "  $(T 'machine_prompt') [$defaultId]"
    if (-not $MachineId) { $MachineId = $defaultId }
}

# ============================================================
# DOMAIN SELECTION
# ============================================================

if (-not $Domain) {
    Write-Host ""
    Write-Host "  $(T 'domain_title')" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    [1] $(T 'domain_work')"
    Write-Host "    [2] $(T 'domain_personal')"
    Write-Host "    [3] $(T 'domain_hybrid')"
    Write-Host ""
    $dc = Read-Host "  (1/2/3)"
    switch ($dc) {
        "1" { $Domain = "work" }
        "2" { $Domain = "personal" }
        default { $Domain = "hybrid" }
    }
}

$setupMode = "$Hub-$Env"
Write-Host ""
Write-Host "  Machine: $MachineId | Domain: $Domain | Mode: $setupMode" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# STEP 1: PREREQUISITES
# ============================================================

Write-Step "1/8" "step_prereq"

$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) { Write-OK "Node.js $(node --version)" }
else { Write-Fail "Node.js not found"; exit 1 }

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) { Write-OK "$(python --version)" }
else { Write-Fail "Python 3.11+ not found"; exit 1 }

$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) { Write-OK "Git $(git --version)" }
else { Write-Fail "Git not found"; exit 1 }

$claude = Get-Command claude -ErrorAction SilentlyContinue
if ($claude) { Write-OK "Claude Code" }
else {
    npm install -g @anthropic-ai/claude-code
    Write-OK "Claude Code installed"
}

$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) { Write-OK "GitHub CLI" }
else { Write-Skip "GitHub CLI (optional)" }

# ============================================================
# STEP 2: AUTHENTICATION
# ============================================================

Write-Step "2/8" "step_auth"

$claudeCreds = "$claudeDir\.credentials.json"
if (Test-Path $claudeCreds) { Write-OK "Claude Code" }
else {
    claude auth login
    if (Test-Path $claudeCreds) { Write-OK "Claude Code" }
    else { Write-Fail "Claude auth failed"; exit 1 }
}

if ($gh) {
    $ghStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) { Write-OK "GitHub" }
    else { gh auth login }
}

# ============================================================
# STEP 3: CONFIG
# ============================================================

Write-Step "3/8" "step_config"

New-Item -ItemType Directory -Force -Path $configDir | Out-Null
$wsRoot = "$env:USERPROFILE\Documents\Workspace"
if (-not (Test-Path $wsRoot)) { New-Item -ItemType Directory -Force -Path $wsRoot | Out-Null }

$config = @{
    machine_id = $MachineId
    lang = $Lang
    hub = $Hub
    env = $Env
    domain = $Domain
    wrapper_dir = $wrapperDir
    data_dir = $wrapperDir
    workspace_root = $wsRoot
    knowledge_dir = "$wrapperDir\knowledge"
    l4_provider = "github"
    oracle = @{ enabled = $false }
    embedding = @{ provider = "none" }
}
$config | ConvertTo-Json -Depth 3 | Set-Content $configFile -Encoding UTF8
Write-OK "Config saved (machine: $MachineId, mode: $setupMode)"

# ============================================================
# STEP 4: MCP MEMORY SERVER
# ============================================================

Write-Step "4/8" "step_mcp"

$mcpServerDir = "$wrapperDir\skills\memory-server"
Push-Location $mcpServerDir
$pipResult = pip install -e . --quiet 2>&1
Pop-Location
if ($LASTEXITCODE -ne 0) { Write-Fail "pip install failed"; exit 1 }
Write-OK "MCP Memory Server (21 tools)"

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
Write-OK ".mcp.json"

# ============================================================
# STEP 5: CLAUDE.MD + SETTINGS
# ============================================================

Write-Step "5/8" "step_claude"

$claudeMd = Get-Content "$wrapperDir\templates\global-CLAUDE.md" -Raw
$claudeMd = $claudeMd -replace '\{\{DATA_DIR\}\}', $wrapperDir
Set-Content "$claudeDir\CLAUDE.md" -Value $claudeMd -Encoding UTF8
Write-OK "CLAUDE.md"

$settingsPath = "$claudeDir\settings.json"
if (-not (Test-Path $settingsPath) -or (Get-Content $settingsPath -Raw) -eq "{}") {
    Copy-Item "$wrapperDir\templates\settings.json.template" $settingsPath
    Write-OK "settings.json"
} else { Write-OK "settings.json (exists)" }

# ============================================================
# STEP 6: DEPLOY WORKSPACES
# ============================================================

Write-Step "6/8" "step_workspace"

$registryFile = "$wrapperDir\workspaces.json"
$deployed = @()
if (Test-Path $registryFile) {
    $registry = Get-Content $registryFile -Raw | ConvertFrom-Json
    foreach ($ws in $registry.workspaces) {
        $wsPath = "$wsRoot\$($ws.path)"
        if (Test-Path $wsPath) { Write-OK "$($ws.id) (exists)" }
        elseif ($ws.repo -and $gh) {
            git clone "https://github.com/$($ws.repo).git" $wsPath 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { Write-OK "$($ws.id) (cloned)" }
            else { New-Item -ItemType Directory -Force -Path $wsPath | Out-Null; Write-Skip "$($ws.id) (created empty)" }
        } else { New-Item -ItemType Directory -Force -Path $wsPath | Out-Null; Write-OK "$($ws.id)" }

        $memPath = "$wsPath\.claude-memory"
        if (-not (Test-Path "$memPath\memory.db")) {
            New-Item -ItemType Directory -Force -Path $memPath | Out-Null
            python "$wrapperDir\scripts\init_db.py" "$memPath\memory.db" 2>&1 | Out-Null
        }
        $deployed += $ws.id
    }
}
Write-Host "  $($deployed.Count) workspaces deployed" -ForegroundColor Green

# ============================================================
# STEP 7: SCHEDULER + REGISTRATION
# ============================================================

Write-Step "7/8" "step_sched"

$taskName = "Clawd-Lobster Sync"
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if (-not $existingTask) {
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -File `"$wrapperDir\scripts\sync-all.ps1`"" `
        -WorkingDirectory $wrapperDir
    $trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once -At (Get-Date)
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings 2>&1 | Out-Null
    Write-OK "Scheduler (every 30 min)"
} else { Write-OK "Scheduler (exists)" }

# Register machine
$clientsDir = "$wrapperDir\clients"
New-Item -ItemType Directory -Force -Path $clientsDir | Out-Null
@{
    machine_id = $MachineId
    hostname = $env:COMPUTERNAME
    os = "Windows $([System.Environment]::OSVersion.Version.Major)"
    lang = $Lang
    domain = $Domain
    hub = $Hub
    env_mode = $Env
    registered = (Get-Date -Format "yyyy-MM-dd")
    last_sync = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    deployed_workspaces = $deployed
    claude_version = try { (claude --version 2>&1).ToString().Trim() } catch { "unknown" }
    memory_server_version = "0.2.0"
} | ConvertTo-Json -Depth 3 | Set-Content "$clientsDir\$MachineId.json" -Encoding UTF8
Write-OK "Machine: $MachineId"

# ============================================================
# STEP 8: MIGRATE (if absorb mode)
# ============================================================

if ($Env -eq "absorb") {
    Write-Step "8/8" "step_migrate"

    # Scan for existing systems
    $found = @()
    if (Test-Path "$env:USERPROFILE\Documents\claude-setup") { $found += "claude-setup" }
    if (Test-Path "$env:USERPROFILE\.openclaw") { $found += "OpenClaw" }
    if (Test-Path "$env:USERPROFILE\.hermes") { $found += "Hermes Agent" }
    if (Test-Path "$claudeDir\CLAUDE.md") { $found += "Raw Claude Code" }

    if ($found.Count -gt 0) {
        Write-Host "  Detected: $($found -join ', ')" -ForegroundColor Yellow
        Write-Host "  Run this inside Claude Code to absorb:" -ForegroundColor Yellow
        Write-Host "    claude `"Read skills/migrate/SKILL.md and execute the migration`"" -ForegroundColor White
    } else {
        Write-Skip "No previous systems detected"
    }
} else {
    Write-Step "8/8" "step_migrate"
    Write-Skip "Fresh environment — nothing to absorb"
}

# ============================================================
# DONE
# ============================================================

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Green
Write-Host "     $(T 'done')" -ForegroundColor Green
Write-Host "  ========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Machine:    $MachineId ($setupMode)" -ForegroundColor Gray
Write-Host "  Wrapper:    $wrapperDir" -ForegroundColor Gray
Write-Host "  Workspaces: $($deployed.Count) deployed" -ForegroundColor Gray
Write-Host ""

# Fleet status
$fleetFiles = Get-ChildItem "$clientsDir\*.json" -ErrorAction SilentlyContinue
if ($fleetFiles.Count -ge 1) {
    Write-Host "  $(T 'fleet_title'):" -ForegroundColor Yellow
    foreach ($f in $fleetFiles) {
        $c = Get-Content $f.FullName -Raw | ConvertFrom-Json
        $tag = if ($c.machine_id -eq $MachineId) { " <-- $(T 'this_machine')" } else { "" }
        Write-Host "    $($c.machine_id) ($($c.hub)-$($c.env_mode)) — $($c.deployed_workspaces.Count) ws$tag" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "  $(T 'next_title'):" -ForegroundColor Yellow
Write-Host "    cd `"$wsRoot`" && claude" -ForegroundColor White
Write-Host ""
