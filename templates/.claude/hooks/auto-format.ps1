# PostToolUse hook: auto-format files after Edit/Write (Windows)
# Detects project formatter and runs it on the changed file.
# Fails gracefully — never blocks Claude.

$ErrorActionPreference = "SilentlyContinue"
$FilePath = $env:CLAUDE_TOOL_INPUT_FILE_PATH
if (-not $FilePath -or -not (Test-Path $FilePath)) { exit 0 }

$ext = [System.IO.Path]::GetExtension($FilePath).TrimStart('.')

switch ($ext) {
    { $_ -in 'py' } {
        if (Get-Command black -ErrorAction SilentlyContinue) { black -q $FilePath 2>$null; exit 0 }
        if (Get-Command ruff -ErrorAction SilentlyContinue) { ruff format -q $FilePath 2>$null; exit 0 }
    }
    { $_ -in 'js','ts','jsx','tsx','json','css','md','html','yaml','yml' } {
        if (Get-Command prettier -ErrorAction SilentlyContinue) { prettier --write $FilePath 2>$null; exit 0 }
    }
    { $_ -eq 'go' } {
        if (Get-Command gofmt -ErrorAction SilentlyContinue) { gofmt -w $FilePath 2>$null; exit 0 }
    }
    { $_ -eq 'rs' } {
        if (Get-Command rustfmt -ErrorAction SilentlyContinue) { rustfmt $FilePath 2>$null; exit 0 }
    }
}
exit 0
