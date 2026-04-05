# Stop hook: quick verification when Claude finishes a turn (Windows)
# Checks for uncommitted changes and basic project health.
# Must complete in < 2 seconds. Fails gracefully.

$ErrorActionPreference = "SilentlyContinue"
$warnings = @()

# Check for uncommitted changes
if (Get-Command git -ErrorAction SilentlyContinue) {
    $isGit = git rev-parse --is-inside-work-tree 2>$null
    if ($isGit -eq "true") {
        $changed = (git diff --name-only 2>$null | Measure-Object -Line).Lines
        $staged = (git diff --cached --name-only 2>$null | Measure-Object -Line).Lines
        if ($changed -gt 0 -or $staged -gt 0) {
            $warnings += "Uncommitted changes: $changed modified, $staged staged."
        }
    }
}

# Check for test runner
if (Test-Path "package.json") {
    $pkg = Get-Content "package.json" -Raw 2>$null
    if ($pkg -match '"test"') { $warnings += "Tests available (npm test)." }
}
elseif ((Test-Path "pyproject.toml") -or (Test-Path "setup.py")) {
    if (Get-Command pytest -ErrorAction SilentlyContinue) { $warnings += "Tests available (pytest)." }
}

if ($warnings.Count -gt 0) {
    $hint = $warnings -join " "
    Write-Output "{`"hint`": `"Before finishing: $hint Consider verifying your work.`"}"
}

exit 0
