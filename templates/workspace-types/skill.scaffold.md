# Skill Scaffold

## Directory Structure

```
<workspace>/
├── CLAUDE.md
├── workspace.json
├── .gitignore
├── knowledge/
├── openspec/
│   ├── project.md
│   ├── changes/
│   └── specs/
├── skill/
│   ├── SKILL.md             # Skill instructions (prompt pattern)
│   ├── skill.json           # Skill metadata
│   └── src/                 # Optional: code if skill has a runtime component
└── tests/
    └── scenarios/           # Test scenarios (Given/When/Then)
```

## Notes

- Skills are primarily prompt patterns — `SKILL.md` is the main artifact.
- `skill.json` defines metadata, config schema, and dependencies.
- No Docker or deploy pipeline — skills ship via `/skill:register`.
- Test scenarios validate the skill's behavior, not code.
- Follow the existing skill format in `clawd-lobster/skills/*/`.
