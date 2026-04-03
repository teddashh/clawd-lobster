#!/bin/bash
# Setup git hooks for spec validation in a workspace
# Usage: bash setup-hooks.sh /path/to/workspace

WORKSPACE="${1:-.}"
HOOK_DIR="$WORKSPACE/.git/hooks"

if [ ! -d "$HOOK_DIR" ]; then
    echo "Error: $WORKSPACE is not a git repository"
    exit 1
fi

cat > "$HOOK_DIR/pre-commit" << 'HOOKEOF'
#!/bin/bash
# Clawd-Lobster: Validate spec on commit
# Only runs if openspec/ directory exists

if [ -d "openspec/changes" ]; then
    # Find validate-spec.py
    VALIDATOR=""
    if [ -f "scripts/validate-spec.py" ]; then
        VALIDATOR="scripts/validate-spec.py"
    elif command -v validate-spec.py &>/dev/null; then
        VALIDATOR="validate-spec.py"
    fi

    if [ -n "$VALIDATOR" ]; then
        python3 "$VALIDATOR" . --errors-only
        if [ $? -ne 0 ]; then
            echo ""
            echo "Spec validation failed. Fix errors before committing."
            echo "Run: python3 $VALIDATOR . for details."
            exit 1
        fi
    fi
fi
HOOKEOF

chmod +x "$HOOK_DIR/pre-commit"
echo "Pre-commit hook installed at $HOOK_DIR/pre-commit"
