# install.ps1 — Clawd-Lobster Setup
# Usage:
#   .\install.ps1                                         # Interactive
#   .\install.ps1 -Lang en -Hub new -Env fresh -MachineId "my-server"  # Headless
#   .\install.ps1 -DryRun                                 # Preview only
#   .\install.ps1 -Resume                                 # Resume from failure

param(
    [ValidateSet("", "zh-TW", "en", "zh-CN", "ja", "ko")]
    [string]$Lang = "",
    [ValidateSet("", "new", "join")]
    [string]$Hub = "",
    [ValidateSet("", "fresh", "absorb")]
    [string]$Env = "",
    [string]$MachineId = "",
    [string]$JoinCode = "",
    [string]$HubName = "",
    [switch]$DryRun,
    [switch]$Resume,
    [switch]$SkipServices,
    [ValidateSet("", "work", "personal", "hybrid")]
    [string]$Domain = ""
)

$ErrorActionPreference = "Stop"
$script:DryRun = $DryRun.IsPresent
$wrapperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$configDir = "$env:USERPROFILE\.clawd-lobster"
$configFile = "$configDir\config.json"

# Load helper library
. "$wrapperDir\scripts\install-lib.ps1"
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
        hub_name_prompt = "Name your Hub (e.g. clawd-yourname)"
        hub_name_hint = "This creates a private GitHub repo that becomes your command center"
        machine_prompt = "Name this machine"
        join_prompt = "Enter Hub repo URL (e.g. github.com/you/clawd-yourname)"
        step_prereq = "Checking prerequisites"
        step_auth = "Authentication"
        step_hub = "Creating your Hub"
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
        hub_name_prompt = "幫你的 Hub 取個名字 (例如 clawd-你的名字)"
        hub_name_hint = "這會建立一個 private GitHub repo，成為你的指揮中心"
        machine_prompt = "幫這台機器命名"
        join_prompt = "輸入 Hub repo 網址 (例如 github.com/你/clawd-你的名字)"
        step_prereq = "檢查前置需求"
        step_auth = "身份驗證"
        step_hub = "建立你的 Hub"
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
        hub_name_prompt = "给你的 Hub 起个名字 (例如 clawd-你的名字)"
        hub_name_hint = "这会创建一个 private GitHub repo，成为你的指挥中心"
        machine_prompt = "给这台机器命名"
        join_prompt = "输入 Hub repo 地址 (例如 github.com/你/clawd-你的名字)"
        step_prereq = "检查前置需求"
        step_auth = "身份验证"
        step_hub = "创建你的 Hub"
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
        hub_name_prompt = "Hubの名前を決めてください (例: clawd-あなたの名前)"
        hub_name_hint = "プライベートGitHubリポジトリが作成され、あなたの司令塔になります"
        machine_prompt = "このマシンの名前"
        join_prompt = "Hub リポジトリURLを入力 (例: github.com/you/clawd-yourname)"
        step_prereq = "前提条件の確認"
        step_auth = "認証"
        step_hub = "Hubを作成中"
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
        hub_name_prompt = "Hub 이름을 정해주세요 (예: clawd-당신의이름)"
        hub_name_hint = "프라이빗 GitHub 리포지토리가 생성되어 당신의 지휘 센터가 됩니다"
        machine_prompt = "이 머신의 이름"
        join_prompt = "Hub 리포지토리 URL 입력 (예: github.com/you/clawd-yourname)"
        step_prereq = "전제 조건 확인"
        step_auth = "인증"
        step_hub = "Hub 생성 중"
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

# Merge helpers are now in scripts/install-lib.ps1 (loaded above)

# ============================================================
# RESUME MODE
# ============================================================

if ($Resume) {
    $stateFile = "$configDir\install-state.json"
    if (-not (Test-Path $stateFile)) {
        Write-Host "  [FAIL] No previous install state found. Run without -Resume." -ForegroundColor Red
        exit 1
    }
    $savedState = Get-Content $stateFile -Raw | ConvertFrom-Json
    Write-Host "  Resuming from step $($savedState.failed_step ?? 'unknown')..." -ForegroundColor Yellow
    if ($savedState.params) {
        if ($savedState.params.hub) { $Hub = $savedState.params.hub }
        if ($savedState.params.env) { $Env = $savedState.params.env }
        if ($savedState.params.machine_id) { $MachineId = $savedState.params.machine_id }
        if ($savedState.params.lang) { $Lang = $savedState.params.lang }
        if ($savedState.params.hub_name) { $HubName = $savedState.params.hub_name }
        if ($savedState.params.domain) { $Domain = $savedState.params.domain }
    }
}

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

# Hub naming (new mode) or join URL (join mode)
if ($Hub -eq "new" -and -not $HubName) {
    Write-Host ""
    Write-Host "  $(T 'hub_name_hint')" -ForegroundColor Gray
    $defaultHub = "clawd-$(($env:USERNAME ?? 'me').ToLower() -replace '[^a-z0-9]', '')"
    $HubName = Read-Host "  $(T 'hub_name_prompt') [$defaultHub]"
    if (-not $HubName) { $HubName = $defaultHub }
    # Sanitize
    $HubName = ($HubName.ToLower() -replace '[^a-z0-9-]', '-').TrimStart('-').TrimEnd('-')
    Write-Host "  Hub: $HubName" -ForegroundColor Cyan
}

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

# ============================================================
# PHASE 1: PREFLIGHT SCAN
# ============================================================

Write-Host ""
Write-Host "  Scanning machine state..." -ForegroundColor Gray
$machineState = Scan-MachineState -claudeDir $claudeDir
Show-PreflightReport $machineState

# Warn about active services
if (-not $SkipServices -and $machineState.active_processes.Count -gt 0) {
    Write-Host "  Active Claude processes detected. Recommended: close Claude Code before installing." -ForegroundColor Yellow
    $cont = Read-Host "  Continue anyway? (Y/n)"
    if ($cont -eq "n") { Write-Host "  Aborted."; exit 0 }
}
if ($machineState.locked_files.Count -gt 0) {
    Write-Host "  [WARN] Some config files are locked. Close Claude Code first." -ForegroundColor Yellow
    Write-Host "  Locked: $($machineState.locked_files -join ', ')" -ForegroundColor Yellow
    $cont = Read-Host "  Continue anyway? (Y/n)"
    if ($cont -eq "n") { Write-Host "  Aborted."; exit 0 }
}

# ============================================================
# PHASE 2: SHOW PLAN
# ============================================================

Show-InstallPlan $machineState $Hub $Env $HubName $MachineId $Domain

if ($DryRun) {
    Write-Host "  Dry run complete. No changes were made." -ForegroundColor Green
    exit 0
}

$proceed = Read-Host "  Proceed? (Y/n)"
if ($proceed -eq "n") { Write-Host "  Aborted."; exit 0 }

# ============================================================
# PHASE 3: EXECUTE — Initialize state tracking
# ============================================================

$installParams = @{
    hub = $Hub; env = $Env; machine_id = $MachineId
    lang = $Lang; hub_name = $HubName; domain = $Domain
}
$installState = Initialize-InstallState $configDir $installParams
$resumeFrom = if ($Resume) { Get-ResumePoint $installState } else { 1 }

# ============================================================
# STEP 1: PREREQUISITES
# ============================================================

if ($resumeFrom -le 1) {

Write-Step "1/9" "step_prereq"

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

Set-StepComplete $configDir ([ref]$installState) 1
} # end step 1

if ($resumeFrom -le 2) {
Write-Step "2/9" "step_auth"

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
# STEP 3: CREATE OR CLONE HUB
# ============================================================

Set-StepComplete $configDir ([ref]$installState) 2
} # end step 2

if ($resumeFrom -le 3) {
Write-Step "3/9" "step_hub"

$hubDir = ""
if ($Hub -eq "new") {
    # Create hub repo from clawd-lobster template
    $hubDir = "$env:USERPROFILE\Documents\$HubName"
    if (Test-Path $hubDir) {
        Write-OK "$HubName already exists at $hubDir"
    } else {
        # Copy clawd-lobster as template
        Copy-Item -Path $wrapperDir -Destination $hubDir -Recurse -Force
        # Remove clawd-lobster's .git — this is a new repo
        Remove-Item -Path "$hubDir\.git" -Recurse -Force -ErrorAction SilentlyContinue
        # Init fresh git
        Push-Location $hubDir
        git init 2>&1 | Out-Null
        # Create private GitHub repo
        if ($gh) {
            git add -A 2>&1 | Out-Null
            git commit -m "Initial hub: $HubName (generated by clawd-lobster)" 2>&1 | Out-Null
            gh repo create $HubName --private --source=. --remote=origin --push --description "My AI agent hub (generated by clawd-lobster)" 2>&1 | Out-Null
            Write-OK "Hub created: github.com/$(gh api user --jq '.login' 2>&1)/$HubName (private)"
        } else {
            git add -A 2>&1 | Out-Null
            git commit -m "Initial hub: $HubName" 2>&1 | Out-Null
            Write-OK "Hub created locally (push to GitHub manually: gh repo create $HubName --private)"
        }
        Pop-Location
    }
    # Switch context: everything now runs from the hub, not clawd-lobster
    $wrapperDir = $hubDir
} elseif ($Hub -eq "join") {
    # Clone existing hub
    $hubUrl = $JoinCode
    # Normalize URL
    if ($hubUrl -notmatch "^https?://") { $hubUrl = "https://github.com/$hubUrl" }
    if ($hubUrl -notmatch "\.git$") { $hubUrl = "$hubUrl.git" }
    $HubName = [System.IO.Path]::GetFileNameWithoutExtension(($hubUrl -split '/')[-1])
    $hubDir = "$env:USERPROFILE\Documents\$HubName"
    if (Test-Path $hubDir) {
        Write-OK "$HubName already exists, pulling latest..."
        Push-Location $hubDir
        git pull 2>&1 | Out-Null
        Pop-Location
    } else {
        git clone $hubUrl $hubDir 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-OK "Hub cloned: $HubName" }
        else { Write-Fail "Failed to clone hub from $hubUrl"; exit 1 }
    }
    $wrapperDir = $hubDir
}

# ============================================================
# STEP 4: CONFIG
# ============================================================

Set-StepComplete $configDir ([ref]$installState) 3
} # end step 3

if ($resumeFrom -le 4) {
Write-Step "4/9" "step_config"

New-Item -ItemType Directory -Force -Path $configDir | Out-Null
$wsRoot = "$env:USERPROFILE\Documents\Workspace"
if (-not (Test-Path $wsRoot)) { New-Item -ItemType Directory -Force -Path $wsRoot | Out-Null }

$config = @{
    machine_id = $MachineId
    lang = $Lang
    hub = $Hub
    hub_name = $HubName
    hub_dir = $hubDir
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
Write-OK "Config saved (hub: $HubName, machine: $MachineId)"

# ============================================================
# STEP 4: MCP MEMORY SERVER
# ============================================================

Set-StepComplete $configDir ([ref]$installState) 4
} # end step 4

if ($resumeFrom -le 5) {
Write-Step "5/9" "step_mcp"

$mcpServerDir = "$wrapperDir\skills\memory-server"
Push-Location $mcpServerDir
$pipResult = pip install -e . --quiet 2>&1
Pop-Location
if ($LASTEXITCODE -ne 0) { Write-Fail "pip install failed"; exit 1 }
Write-OK "MCP Memory Server (24 tools)"

New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
$mcpJsonPath = "$claudeDir\.mcp.json"
$pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
Backup-File $mcpJsonPath $configDir ([ref]$installState) | Out-Null
$mergedMcp = Merge-McpJson $mcpJsonPath $mcpServerDir $pythonCmd
$mergedMcp | ConvertTo-Json -Depth 4 | Set-Content $mcpJsonPath -Encoding UTF8
$serverCount = ($mergedMcp.mcpServers.PSObject.Properties | Measure-Object).Count
$action = if ($serverCount -gt 1) { "merged — $serverCount servers" } else { "created" }
Write-OK ".mcp.json ($action)"

# Initialize skill registry
Write-Host "  Initializing skill registry..." -ForegroundColor Gray
$skillManagerPath = Join-Path $wrapperDir "scripts" "skill-manager.py"
if (Test-Path $skillManagerPath) {
    python $skillManagerPath reconcile 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Skill registry initialized" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Skill registry init skipped (non-critical)" -ForegroundColor Yellow
    }
}

# ============================================================
# STEP 5: CLAUDE.MD + SETTINGS
# ============================================================

Set-StepComplete $configDir ([ref]$installState) 5
} # end step 5

if ($resumeFrom -le 6) {
Write-Step "6/9" "step_claude"

$templateMd = Get-Content "$wrapperDir\templates\global-CLAUDE.md" -Raw
$templateMd = $templateMd -replace '\{\{DATA_DIR\}\}', $wrapperDir
$claudeMdPath = "$claudeDir\CLAUDE.md"
if (Test-Path $claudeMdPath) {
    Backup-File $claudeMdPath $configDir ([ref]$installState) | Out-Null
    $mergedMd = Merge-ClaudeMd $claudeMdPath $templateMd
    Set-Content $claudeMdPath -Value $mergedMd -Encoding UTF8
    Write-OK "CLAUDE.md (merged — existing content preserved)"
} else {
    Set-Content $claudeMdPath -Value $templateMd -Encoding UTF8
    Write-OK "CLAUDE.md (created)"
}

$settingsPath = "$claudeDir\settings.json"
if (Test-Path $settingsPath) {
    $rawSettings = (Get-Content $settingsPath -Raw).Trim()
    if ($rawSettings -ne "{}" -and $rawSettings -ne "") {
        Backup-File $settingsPath $configDir ([ref]$installState) | Out-Null
        $mergedSettings = Merge-Settings $settingsPath "$wrapperDir\templates\settings.json.template"
        $mergedSettings | ConvertTo-Json -Depth 4 | Set-Content $settingsPath -Encoding UTF8
        Write-OK "settings.json (merged — added memory permissions)"
    } else {
        Copy-Item "$wrapperDir\templates\settings.json.template" $settingsPath
        Write-OK "settings.json (created)"
    }
} else {
    Copy-Item "$wrapperDir\templates\settings.json.template" $settingsPath
    Write-OK "settings.json (created)"
}
# Never touch settings.local.json — user's permission overrides are sacred
if (Test-Path "$claudeDir\settings.local.json") {
    Write-OK "settings.local.json (preserved — not modified)"
}

# ============================================================
# STEP 6: DEPLOY WORKSPACES
# ============================================================

Set-StepComplete $configDir ([ref]$installState) 6
} # end step 6

if ($resumeFrom -le 7) {
Write-Step "7/9" "step_workspace"

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

Set-StepComplete $configDir ([ref]$installState) 7
} # end step 7

if ($resumeFrom -le 8) {
Write-Step "8/9" "step_sched"

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

# Heartbeat task (every 30 min — ensures all workspace sessions stay alive)
$hbTaskName = "Clawd-Lobster Heartbeat"
$existingHb = Get-ScheduledTask -TaskName $hbTaskName -ErrorAction SilentlyContinue
if (-not $existingHb) {
    $hbAction = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -File `"$wrapperDir\scripts\heartbeat.ps1`"" `
        -WorkingDirectory $wrapperDir
    $hbTrigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once -At (Get-Date)
    $hbSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
    Register-ScheduledTask -TaskName $hbTaskName -Action $hbAction -Trigger $hbTrigger -Settings $hbSettings 2>&1 | Out-Null
    Write-OK "Heartbeat (session lifecycle, every 30 min)"
} else { Write-OK "Heartbeat (exists)" }

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
    memory_server_version = "0.3.0"
} | ConvertTo-Json -Depth 3 | Set-Content "$clientsDir\$MachineId.json" -Encoding UTF8
Write-OK "Machine: $MachineId"

Set-StepComplete $configDir ([ref]$installState) 8
} # end step 8

# ============================================================
# STEP 9: MIGRATE (if absorb mode)
# ============================================================

if ($resumeFrom -le 9) {
if ($Env -eq "absorb") {
    Write-Step "9/9" "step_migrate"

    # Scan for existing systems
    $found = @()
    $openclawDir = "$env:USERPROFILE\.openclaw"
    $claudeSetupDir = "$env:USERPROFILE\Documents\claude-setup"
    $hermesDir = "$env:USERPROFILE\.hermes"

    if (Test-Path $openclawDir) { $found += "OpenClaw" }
    if (Test-Path $claudeSetupDir) { $found += "claude-setup" }
    if (Test-Path $hermesDir) { $found += "Hermes Agent" }

    if ($found.Count -eq 0) {
        Write-Skip "No previous systems detected"
    } else {
        Write-Host "  Detected: $($found -join ', ')" -ForegroundColor Yellow
        $imported = 0

        # --- OpenClaw Migration ---
        if ("OpenClaw" -in $found) {
            Write-Host "  --- OpenClaw ---" -ForegroundColor Cyan

            # 1. Soul/Personality
            $soulSrc = "$openclawDir\SOUL.md"
            if (Test-Path $soulSrc) {
                $soulDst = "$wrapperDir\soul\personality.md"
                New-Item -ItemType Directory -Force -Path "$wrapperDir\soul" | Out-Null
                Copy-Item $soulSrc $soulDst -Force
                Write-OK "SOUL.md -> soul/personality.md"
                $imported++
            }

            # 2. Identity files (IDENTITY.md, AGENTS.md, HEARTBEAT.md)
            foreach ($idFile in @("IDENTITY.md", "AGENTS.md", "HEARTBEAT.md")) {
                $src = "$openclawDir\$idFile"
                if (Test-Path $src) {
                    Copy-Item $src "$wrapperDir\soul\$idFile" -Force
                    Write-OK "$idFile -> soul/$idFile"
                    $imported++
                }
            }

            # 3. Memory files → import key items to knowledge base
            $memoryDir = "$openclawDir\memory"
            if (Test-Path $memoryDir) {
                $memFiles = Get-ChildItem "$memoryDir\*.md" -ErrorAction SilentlyContinue
                if ($memFiles.Count -gt 0) {
                    $knowledgeDst = "$wrapperDir\knowledge\imported-openclaw"
                    New-Item -ItemType Directory -Force -Path $knowledgeDst | Out-Null
                    foreach ($mf in $memFiles) {
                        Copy-Item $mf.FullName "$knowledgeDst\$($mf.Name)" -Force
                    }
                    Write-OK "Memory files ($($memFiles.Count) files) -> knowledge/imported-openclaw/"
                    $imported++
                }
            }

            # 4. Skills inventory (list, don't copy — Lobster has its own skill format)
            $skillsDir = "$openclawDir\skills"
            if (Test-Path $skillsDir) {
                $skillDirs = Get-ChildItem $skillsDir -Directory -ErrorAction SilentlyContinue
                if ($skillDirs.Count -gt 0) {
                    Write-OK "Skills found: $($skillDirs.Count) (use memory_learn_skill to recreate relevant ones)"
                    # Save inventory for reference
                    $skillList = $skillDirs | ForEach-Object { $_.Name }
                    $skillList | Out-File "$wrapperDir\soul\openclaw-skills-inventory.txt" -Encoding UTF8
                    $imported++
                }
            }

            # 5. OpenClaw CLAUDE.md → extract useful sections
            $ocClaudeMd = "$openclawDir\CLAUDE.md"
            if (Test-Path $ocClaudeMd) {
                Copy-Item $ocClaudeMd "$wrapperDir\soul\openclaw-CLAUDE.md.reference" -Force
                Write-OK "CLAUDE.md saved as reference -> soul/openclaw-CLAUDE.md.reference"
                $imported++
            }

            # 6. Extensions inventory
            $extDir = "$openclawDir\extensions"
            if (Test-Path $extDir) {
                $exts = Get-ChildItem $extDir -Directory -ErrorAction SilentlyContinue
                if ($exts.Count -gt 0) {
                    Write-OK "Extensions found: $($exts.Name -join ', ') (keep alongside Lobster)"
                }
            }

            # 7. Hooks → note them (user should manually add to settings.json if wanted)
            $hooksDir = "$openclawDir\hooks"
            if (Test-Path $hooksDir) {
                $hooks = Get-ChildItem $hooksDir -Directory -ErrorAction SilentlyContinue
                if ($hooks.Count -gt 0) {
                    Write-OK "Hooks found: $($hooks.Name -join ', ') (add to settings.json hooks if needed)"
                }
            }

            # 8. Learnings (scan common locations relative to detected system root)
            $learningsSources = @(
                "$openclawDir\knowledge\learnings",
                "$openclawDir\learnings",
                "$env:USERPROFILE\Documents\Knowledge\Learnings",
                "$env:USERPROFILE\Documents\Workspace\Knowledge\Learnings"
            )
            foreach ($learningsDir in $learningsSources) {
                if (Test-Path $learningsDir) {
                    $learningFiles = Get-ChildItem "$learningsDir\*.md" -ErrorAction SilentlyContinue
                    if ($learningFiles.Count -gt 0) {
                        $lrnDst = "$wrapperDir\knowledge\learnings"
                        New-Item -ItemType Directory -Force -Path $lrnDst | Out-Null
                        foreach ($lf in $learningFiles) {
                            Copy-Item $lf.FullName "$lrnDst\$($lf.Name)" -Force
                        }
                        Write-OK "Learnings ($($learningFiles.Count) files from $learningsDir) -> knowledge/learnings/"
                        $imported++
                        break
                    }
                }
            }
        }

        # --- claude-setup Migration ---
        if ("claude-setup" -in $found) {
            Write-Host "  --- claude-setup ---" -ForegroundColor Cyan

            # Workspace map
            $wsMap = "$claudeSetupDir\workspace-map.json"
            if (Test-Path $wsMap) {
                Copy-Item $wsMap "$wrapperDir\soul\claude-setup-workspace-map.json.reference" -Force
                Write-OK "workspace-map.json saved as reference"
                $imported++
            }

            # Soul files
            $cssSoul = "$claudeSetupDir\global\soul"
            if (Test-Path $cssSoul) {
                Get-ChildItem "$cssSoul\*" -ErrorAction SilentlyContinue | ForEach-Object {
                    Copy-Item $_.FullName "$wrapperDir\soul\$($_.Name)" -Force
                }
                Write-OK "Soul files -> soul/"
                $imported++
            }

            # Memory databases (keep in place — Lobster can read them via workspace registry)
            $cssMemDbs = Get-ChildItem "$claudeSetupDir\*\.claude-memory\memory.db" -Recurse -ErrorAction SilentlyContinue
            if ($cssMemDbs.Count -gt 0) {
                Write-OK "Memory databases: $($cssMemDbs.Count) (kept in place)"
            }
        }

        # --- Hermes Agent Migration ---
        if ("Hermes Agent" -in $found) {
            Write-Host "  --- Hermes Agent ---" -ForegroundColor Cyan

            # Memory + skills → reference only
            if (Test-Path "$hermesDir\memory") {
                Copy-Item "$hermesDir\memory" "$wrapperDir\soul\hermes-memory.reference" -Recurse -Force -ErrorAction SilentlyContinue
                Write-OK "Memory -> soul/hermes-memory.reference/"
                $imported++
            }
            if (Test-Path "$hermesDir\skills") {
                $hermesSkills = Get-ChildItem "$hermesDir\skills" -ErrorAction SilentlyContinue
                Write-OK "Skills found: $($hermesSkills.Count) (reference only)"
            }
        }

        # --- CC Auto-Memory (always check) ---
        $ccMemDir = "$claudeDir\projects"
        if (Test-Path $ccMemDir) {
            $ccMemFiles = Get-ChildItem "$ccMemDir\*\memory\*.md" -Recurse -ErrorAction SilentlyContinue
            if ($ccMemFiles.Count -gt 0) {
                Write-OK "CC auto-memory: $($ccMemFiles.Count) files (native — no migration needed)"
            }
        }

        Write-Host ""
        Write-Host "  Migration complete: $imported items imported" -ForegroundColor Green
        Write-Host "  Backups saved to: $env:USERPROFILE\.clawd-lobster\backup\" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  For deep migration (reading content, storing to L2 memory):" -ForegroundColor Yellow
        Write-Host "    Open Claude Code and run: /migrate" -ForegroundColor White
    }
} else {
    Write-Step "9/9" "step_migrate"
    Write-Skip "Fresh environment — nothing to absorb"
}
Set-StepComplete $configDir ([ref]$installState) 9
} # end step 9

# ============================================================
# PHASE 4: VERIFY
# ============================================================

Write-Host ""
Write-Host "  Verifying installation..." -ForegroundColor Yellow
$pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
$verifyResult = Test-Installation $claudeDir $wrapperDir $pythonCmd
if ($verifyResult.fail -gt 0) {
    Write-Host ""
    Write-Host "  Some checks failed. Run with -Resume to retry, or check the issues above." -ForegroundColor Yellow
}

# ============================================================
# DONE
# ============================================================

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Green
Write-Host "     $(T 'done')" -ForegroundColor Green
Write-Host "  ========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Hub:        $HubName" -ForegroundColor Gray
Write-Host "  Hub dir:    $hubDir" -ForegroundColor Gray
Write-Host "  Machine:    $MachineId ($Domain, $setupMode)" -ForegroundColor Gray
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
