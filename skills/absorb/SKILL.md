# Absorb — Knowledge Absorption Engine

!git log --oneline -5 2>/dev/null || echo "Not in a git repo"

When `/absorb` is invoked, follow this protocol exactly.

## 1. Parse Input

Determine the source type from the user's argument:

- **Local folder path** (e.g., `./my-project`, `/home/user/repo`) — scan the directory directly.
- **GitHub URL** (e.g., `https://github.com/org/repo`) — clone to a temp directory, then scan.
- **Web URL** (e.g., `https://docs.example.com/guide`) — fetch the page content, extract knowledge.
- **No argument** — ask the user: "What should I absorb? Provide a folder path, GitHub URL, or web URL."

## 2. Determine Depth

Check the `depth` config (default: `normal`):

| Depth | What to scan |
|-------|-------------|
| `shallow` | README, CLAUDE.md, top-level config files only (package.json, pyproject.toml, Cargo.toml, etc.) |
| `normal` | Everything in shallow + key source files, skill definitions, important docs, .claude/ directory |
| `deep` | Full codebase analysis — all source files, tests, CI configs, scripts |

## 3. Scan and Extract

Walk through the source and collect findings into these categories:

### Facts / Knowledge
General information about the project: architecture, stack, conventions, patterns.
- Store each with: `memory_record_knowledge(title, content, tags)`
- Tag with source identifier (e.g., `absorb:my-project`)

### Decisions / Lessons
Architectural decisions, resolved problems, lessons learned, pitfalls documented.
- Explicit decisions: `memory_record_decision(what, why, how)`
- Lessons/pitfalls: `memory_store(content, type="learning")`
- Look for: ADR files, DECISIONS.md, comments with "decided", "lesson", "gotcha", "watch out"

### Executable Patterns / Skills
Reusable approaches, workflows, or techniques that can be applied elsewhere.
- Store with: `memory_learn_skill(name, trigger, approach, tools, category)`
- Look for: custom scripts, Makefiles, CI pipelines, skill definitions, automation patterns

### Complete Tools / Repos
If the source is a full tool or repo that could become a skill:
- Output a draft `skill.json` for the user to review
- Do NOT auto-register — present it as a suggestion

### Action Items / TODOs
Tasks discovered during scanning: missing tests, deprecated deps, migration needs, open issues.
- Store with: `memory_todo_add(title, description, priority, source="absorb")`
- Only if `auto_create_todos` config is true (default: true)
- Look for: TODO/FIXME/HACK comments, open GitHub issues, incomplete features

## 4. Report Results

After absorption, print a summary tree:

```
Absorbed from: <source>
Depth: <shallow|normal|deep>
|-  N knowledge items stored
|-  N decisions recorded
|-  N skill patterns learned
|-  N TODO items created
\-  N items skipped (dry run) [only if dry_run=true]
```

If any items are particularly notable, list them briefly:
```
Key findings:
  - [knowledge] Uses event-driven architecture with Redis pub/sub
  - [decision] Chose SQLite over PostgreSQL for local-first design
  - [todo] P1: 12 tests are skipped and need fixing
```

## 5. Special Case: Workspace Migration

If the source folder contains `.claude/`, `CLAUDE.md`, or `sessions/` (i.e., it looks like an existing Claude Code workspace), offer these additional actions:

1. **Import CLAUDE.md content** — extract project instructions and store as knowledge items.
2. **Import custom skills** — scan `.claude/skills/` for skill definitions, store as learned skills or suggest adding to this instance.
3. **Import session context** — scan session files for valuable context, decisions, and learnings worth preserving.

Ask the user before importing workspace-specific content: "This looks like a Claude Code workspace. Import its project context, skills, and session knowledge?"

## 6. Dry Run Mode

If `dry_run` is true:
- Perform all scanning and classification steps.
- Do NOT call any `memory_*` write tools.
- Show the full report with `[DRY RUN]` prefix and indicate what WOULD be stored.
- This lets the user preview before committing.

## 7. Safety Rules

- Never store file contents verbatim if they exceed 5000 characters. Summarize instead.
- Never store secrets, API keys, tokens, or credentials found in source files. Log a warning if detected.
- Never store personal names, hardcoded paths, or machine-specific information.
- Tag all absorbed items with `source:absorb` and the source identifier for traceability.
- If the source is unreachable or empty, report clearly and exit — do not fabricate content.

## Gotchas

1. **Verbatim dump instead of synthesis.** Claude tends to store raw file contents as knowledge items instead of summarizing. Always distill before storing — if the content exceeds a few hundred words, extract the key insight, don't paste the whole thing.

2. **Missing source tags make items untraceable.** Every absorbed item MUST include a `source:absorb` tag plus the source identifier. Without this, you cannot distinguish absorbed knowledge from manually stored knowledge, making cleanup impossible.

3. **Shallow scan misses the real architecture.** When `depth=shallow`, Claude reads only README/config files and may conclude the project uses a stack that the actual source code contradicts. If the user seems confused by results, suggest re-running with `depth=normal`.

4. **GitHub URLs fail silently on private repos.** If `git clone` fails due to auth, Claude may proceed with an empty directory and report "0 items found" without explaining why. Always check the clone exit code and report auth failures explicitly.

5. **Duplicate absorption creates noise.** Running `/absorb` twice on the same source creates duplicate knowledge items. Before storing, search existing memory for items tagged with the same source identifier and skip duplicates.
