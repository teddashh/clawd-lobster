# new-workspace.ps1 — Create a new workspace with memory, git, and GitHub repo
# Usage: .\new-workspace.ps1 -name "project-name" [-subfolder "Category"]
#        .\new-workspace.ps1 -name "my-api" -subfolder "Web Projects"

param(
    [Parameter(Mandatory=$true)]
    [string]$name,
    [string]$subfolder = "",
    [switch]$NoGitHub
)

# Load config
$configFile = "$env:USERPROFILE\.clawd-lobster\config.json"
if (Test-Path $configFile) {
    $config = Get-Content $configFile -Raw | ConvertFrom-Json
    $wsRoot = $config.workspace_root
    $wrapperDir = $config.wrapper_dir
} else {
    $docs = "$env:USERPROFILE\Documents"
    $wsRoot = "$docs\Workspace"
    $wrapperDir = "$docs\clawd-lobster"
}

if ($subfolder) {
    $projectPath = "$wsRoot\$subfolder\$name"
    $mapRelPath = "$subfolder/$name"
} else {
    $projectPath = "$wsRoot\$name"
    $mapRelPath = $name
}
$memoryPath = "$projectPath\.claude-memory"
$repoName = ($name -replace ' ', '-').ToLower()

Write-Host "`nCreating workspace: $name" -ForegroundColor Cyan
Write-Host "Path: $projectPath" -ForegroundColor Gray

# Create directories
New-Item -ItemType Directory -Force -Path $projectPath | Out-Null
New-Item -ItemType Directory -Force -Path $memoryPath | Out-Null

# CLAUDE.md from template
$templatePath = "$wrapperDir\templates\workspace-CLAUDE.md"
if (Test-Path $templatePath) {
    $template = Get-Content $templatePath -Raw
    $template = $template -replace '\[PROJECT_NAME\]', $name
    Set-Content -Path "$projectPath\CLAUDE.md" -Value $template -Encoding UTF8
}

# Init memory.db
python "$wrapperDir\scripts\init_db.py" "$memoryPath\memory.db"

# .gitignore
@"
.claude-memory/
*.tmp
__pycache__/
*.pyc
node_modules/
browser-session/
"@ | Set-Content -Path "$projectPath\.gitignore" -Encoding UTF8

# Git init + optional GitHub repo
Push-Location $projectPath
git init
git add -A
git commit -m "Initial commit: workspace setup"
if (-not $NoGitHub) {
    gh repo create $repoName --private --source=. --remote=origin --push 2>&1
    Write-Host "[OK] GitHub repo: $repoName (private)" -ForegroundColor Green
}
Pop-Location

# Update workspaces.json
$registryFile = "$wrapperDir\workspaces.json"
if (-not (Test-Path $registryFile)) {
    # Try data dir
    $dataDir = if ($config.data_dir) { $config.data_dir } else { $wrapperDir }
    $registryFile = "$dataDir\workspaces.json"
}

if (Test-Path $registryFile) {
    $registry = Get-Content $registryFile -Raw | ConvertFrom-Json
    $newEntry = [PSCustomObject]@{
        id = $repoName
        path = $mapRelPath
        repo = ""
        tags = @()
        deploy = "all"
    }
    if (-not $NoGitHub) {
        $ghUser = gh api user --jq '.login' 2>&1
        $newEntry.repo = "$ghUser/$repoName"
    }
    $registry.workspaces += $newEntry
    $registry | ConvertTo-Json -Depth 5 | Set-Content $registryFile -Encoding UTF8
    Write-Host "[OK] workspaces.json updated" -ForegroundColor Green
}

Write-Host "`n[OK] Workspace '$name' ready!" -ForegroundColor Green
Write-Host "  cd `"$projectPath`" && claude" -ForegroundColor Yellow
