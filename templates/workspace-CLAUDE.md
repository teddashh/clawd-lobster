# [PROJECT_NAME] — Workspace

## About
This workspace is for [PROJECT_NAME]. Describe the project goals and context here.

## Rules
Additional rules are in `.claude/rules/` (if present):
- `memory.md` — memory architecture, learnings vs skills
- `safety.md` — workspace isolation, security, git safety
- `evolution.md` — self-evolution patterns
- `tools.md` — MCP tools reference, skill manager

## Workspace Type: [TYPE]
<!-- Replaced by /spec Phase 2 with type-specific content from templates/workspace-types/<type>.claude.md -->

## Conventions
- List coding conventions, naming patterns, or project-specific rules here

## Key Files
- `workspace.json` — Workspace metadata, stack, and deploy config
- `openspec/` — Specs, proposals, designs, and task lists
- List other important files and their purposes here

## Commands
- `/spec` — Plan new features
- `/spec:status` — Check progress
- `/spec:blitz` — Execute tasks autonomously
- `/deploy:init` — Set up deploy pipeline (webapp/api types)
- `/deploy:build` — Generate Docker configs
- `/deploy:ship <env>` — Deploy to dev/staging/prod
- `/deploy:status` — Check deployment state
