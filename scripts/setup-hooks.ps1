# Setup git hooks for spec validation in a workspace
param([string]$Workspace = ".")

$hookDir = Join-Path $Workspace ".git" "hooks"

if (-not (Test-Path $hookDir)) {
    Write-Host "Error: $Workspace is not a git repository" -ForegroundColor Red
    exit 1
}

$hookContent = @'
#!/bin/bash
# Clawd-Lobster: Validate spec on commit
# Only runs if openspec/ directory exists

if [ -d "openspec/changes" ]; then
    VALIDATOR=""
    if [ -f "scripts/validate-spec.py" ]; then
        VALIDATOR="scripts/validate-spec.py"
    elif command -v validate-spec.py &>/dev/null; then
        VALIDATOR="validate-spec.py"
    fi
    if [ -n "$VALIDATOR" ]; then
        python3 "$VALIDATOR" . --errors-only
        if [ $? -ne 0 ]; then
            echo "Spec validation failed. Fix errors before committing."
            exit 1
        fi
    fi
fi
'@

$hookPath = Join-Path $hookDir "pre-commit"
Set-Content -Path $hookPath -Value $hookContent -Encoding UTF8
Write-Host "Pre-commit hook installed at $hookPath" -ForegroundColor Green
