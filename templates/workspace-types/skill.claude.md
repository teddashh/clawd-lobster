# Skill — Workspace Rules

## Skill Structure
- `skill/SKILL.md` — The skill prompt pattern (main artifact)
- `skill/skill.json` — Metadata, config, dependencies

## Ship
- Use `/skill:register` to install into Clawd-Lobster
- No Docker, no deploy pipeline

## Conventions
- Follow existing skill format in `clawd-lobster/skills/`
- SKILL.md instructions constrain Claude's behavior, not output content
- Test with scenarios (Given/When/Then), not unit tests
- Keep skill.json `dependencies` accurate
