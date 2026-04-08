# Absorb — Universal Knowledge Ingestion Engine

!git log --oneline -5 2>/dev/null || echo "Not in a git repo"

When `/absorb` is invoked, follow this protocol exactly.

## 1. Parse Input

Determine the source type from the user's argument:

- **Local folder path** (e.g., `./my-project`, `/home/user/repo`) — scan the directory directly.
- **GitHub URL** (e.g., `https://github.com/org/repo`) — clone to a temp directory, then scan.
- **Web URL** (e.g., `https://docs.example.com/guide`) — fetch the page content, extract knowledge.
- **No argument** — ask the user: "What should I absorb? Provide a folder path, GitHub URL, or web URL."

## 2. Detect Backend

Check which storage backend is available:

| Check | Backend | How |
|-------|---------|-----|
| Oracle vault configured? | **The Vault (L3)** — preferred | Check `~/.clawd-lobster/config.json` → `oracle.enabled = true` |
| memory-server running? | **Memory Server (L1+L2)** | Check via memory_store tool |
| Neither? | **Dry-run mode** | Parse and report without storing |

**When Vault is available**, use the parser framework (`vault_parsers.py`) for structured ingestion:
```bash
python scripts/vault_parsers.py absorb <source> --vault
```

**When only L1+L2 is available**, fall back to the legacy knowledge extraction flow (Section 3b).

## 3a. Vault Ingestion Flow (Oracle L3)

When The Vault is available:

1. **ParserRouter** detects file types and routes to correct parser:
   - `.pdf` → PdfParser → `doc_type='pdf'` or `'research_paper'`
   - `.eml/.mbox` → EmailParser → `doc_type='email'`
   - LINE exports → LineParser → `doc_type='conversation'`
   - Facebook JSON → FacebookParser → `doc_type='social_post'`
   - `.jpg/.png` → ImageParser → `doc_type='image'`
   - `.vtt/.srt` → MeetingParser → `doc_type='meeting_transcript'`
   - URLs → WebParser → `doc_type='webpage'`
   - `.m4a/.wav/.mp3` → VoiceMemoParser → `doc_type='voice_memo'`
   - Debate markdown → DebateParser → `doc_type='debate_transcript'`
   - Code/text/config → TextFileParser → `doc_type='code_artifact'`/`'note'`/`'file'`

2. **DedupEngine** checks each document (3-layer):
   - Layer 1: content_hash match → **skip** (exact duplicate)
   - Layer 2: original_path match + different hash → **new version** (document updated)
   - Layer 3: no match → **new document**

3. **vault_api.ingest()** stores each document into Oracle with full metadata.

4. **Report** summary tree (see Section 5).

### Available Parsers

| Parser | File Types | doc_type | Status |
|--------|-----------|----------|--------|
| TextFileParser | .txt, .md, .py, .js, .json, .yaml, etc. | note / code_artifact / file | Ready |
| PdfParser | .pdf | pdf / research_paper | Ready (needs PyMuPDF) |
| EmailParser | .eml, .mbox | email | Ready |
| LineParser | LINE .txt exports | conversation | Ready |
| FacebookParser | FB data export JSON | social_post | Ready |
| ImageParser | .jpg, .png, .heic, .webp, etc. | image | Ready (needs Pillow) |
| MeetingParser | .vtt, .srt | meeting_transcript | Ready |
| WebParser | URLs, .html | webpage | Ready (needs requests) |
| VoiceMemoParser | .m4a, .wav, .mp3, .ogg | voice_memo | Ready (needs whisper) |
| DebateParser | AI debate markdown | debate_transcript | Ready |

### Parser Selection

- **Automatic**: ParserRouter selects parser by file extension + content detection.
- **Manual override**: `/absorb ~/exports/chat.txt --parser line` forces LineParser.

## 3b. Legacy Knowledge Extraction (L1+L2 fallback)

When only memory-server is available (no Oracle):

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

## 4. Determine Depth

Check the `depth` config (default: `normal`):

| Depth | What to scan |
|-------|-------------|
| `shallow` | README, CLAUDE.md, top-level config files only (package.json, pyproject.toml, Cargo.toml, etc.) |
| `normal` | Everything in shallow + key source files, skill definitions, important docs, .claude/ directory |
| `deep` | Full codebase analysis — all source files, tests, CI configs, scripts |

## 5. Report Results

After absorption, print a summary tree:

```
Absorbed from: <source>
Backend: Vault (L3) / Memory (L1+L2) / Dry Run
Depth: <shallow|normal|deep>
|-- N total files parsed
|-- N new documents
|-- N version updates
|-- N skipped (duplicates)
\-- N errors

By type:
  email                     86420
  note                        149
  code_artifact                23
  pdf                          12
```

If any items are particularly notable, list them briefly:
```
Key findings:
  - [research_paper] quantum_computing_review.pdf (47 pages)
  - [conversation] LINE: David Chen - 2024/03/15 (142 messages)
  - [email] Re: FPC Project Update (high importance)
```

## 6. Special Case: Workspace Migration

If the source folder contains `.claude/`, `CLAUDE.md`, or `sessions/` (i.e., it looks like an existing Claude Code workspace), offer these additional actions:

1. **Import CLAUDE.md content** — extract project instructions and store as knowledge items.
2. **Import custom skills** — scan `.claude/skills/` for skill definitions, store as learned skills or suggest adding to this instance.
3. **Import session context** — scan session files for valuable context, decisions, and learnings worth preserving.

Ask the user before importing workspace-specific content: "This looks like a Claude Code workspace. Import its project context, skills, and session knowledge?"

## 7. Dry Run Mode

If `dry_run` is true:
- Perform all scanning, parsing, and classification steps.
- Do NOT call vault_api.ingest() or any memory write tools.
- Show the full report with `[DRY RUN]` prefix and indicate what WOULD be stored.
- This lets the user preview before committing.

## 8. Safety Rules

- Never store file contents verbatim if they exceed 5000 characters. Summarize instead. (Vault mode stores full content — the Vault handles large CLOBs natively.)
- Never store secrets, API keys, tokens, or credentials found in source files. Log a warning if detected.
- Never store personal names, hardcoded paths, or machine-specific information in L1/L2 mode. (Vault mode preserves these — The Vault is private by design.)
- Tag all absorbed items with `source:absorb` and the source identifier for traceability.
- If the source is unreachable or empty, report clearly and exit — do not fabricate content.
- Skip binary executables, system files, node_modules, .git, __pycache__, and similar directories.
- Files larger than 50MB are skipped with a warning.

## Gotchas

1. **Verbatim dump instead of synthesis.** In L1/L2 mode, Claude tends to store raw file contents as knowledge items instead of summarizing. Always distill before storing. In Vault mode, raw content is fine — the enrichment pipeline handles summarization later.

2. **Missing source tags make items untraceable.** Every absorbed item MUST include a source identifier. Without this, you cannot distinguish absorbed knowledge from manually stored knowledge, making cleanup impossible.

3. **Shallow scan misses the real architecture.** When `depth=shallow`, only README/config files are scanned and may not reflect actual codebase state. If the user seems confused by results, suggest re-running with `depth=normal`.

4. **GitHub URLs fail silently on private repos.** If `git clone` fails due to auth, report the auth failure explicitly — don't proceed with empty results.

5. **Duplicate absorption creates noise.** The DedupEngine (3-layer: content_hash → original_path → new) prevents duplicates in Vault mode. In L1/L2 mode, search existing memory for items tagged with the same source identifier and skip duplicates.

6. **LINE .txt files look like regular text.** LineParser auto-detects LINE format by checking for date + tab-separated message patterns. If mis-detected, use `--parser line` to force.

7. **PDF text extraction requires PyMuPDF.** Without it, PDFs are stored as metadata-only. Install with `pip install PyMuPDF`.
