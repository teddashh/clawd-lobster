# Spec — Guided Workspace Creation & Spec-Driven Development

The most important skill in Clawd-Lobster. You LEAD the user through planning, spec generation, and blitz execution. The user answers questions; you do everything else.

---

## Modes

| Invocation | Mode | Description |
|-----------|------|-------------|
| `/spec` or `/spec new` | **Create** | Full guided flow: discovery → workspace → spec → TODOs → blitz |
| `/spec:status` | **Status** | Show current spec progress and blitz state |
| `/spec:add "feature"` | **Add** | Add a new change to an existing spec |
| `/spec:archive` | **Archive** | Archive a completed change |
| `/spec:blitz` | **Blitz** | Start or resume blitz execution |

---

## Mode 1: `/spec` or `/spec new` — Guided Workspace + Spec Creation

This is the main flow. Five phases, executed sequentially.

### Phase 1: Discovery (YOU ask, user answers)

Enter planning mode. Your job is to extract enough context to generate a complete spec. Ask these questions **conversationally** — not as a checklist. Adapt based on answers. Skip irrelevant ones. Ask follow-ups.

**Core questions to cover:**

1. **Vision** — "What do you want to build?" Get the high-level picture. What problem does it solve?
2. **Audience** — "Who will use this? End users? Internal team? API consumers?" Understand who benefits.
3. **Tech stack** — "What tech stack are you thinking? Or should I recommend one?" If they defer, make a strong recommendation with reasoning.
4. **Scope** — "Is this an MVP or a full product? What's the timeline pressure?" This determines task granularity.
5. **Integrations** — "Any external systems to integrate? Databases, APIs, payment, auth?" Map the dependency surface.
6. **References** — "Do you have reference projects or competitors I should look at?" Use `/absorb` on any provided repos or URLs.
7. **Constraints** — "Any non-negotiable requirements? Performance, compliance, accessibility?" These become hard specs.

**Behavior rules for Phase 1:**

- YOU lead the conversation. Do not wait for the user to know what to ask.
- Be opinionated. When the user says "whatever you think is best," make a strong recommendation with clear reasoning and trade-offs.
- Ask one or two questions at a time, not all seven at once.
- When you have enough context (typically 3-6 exchanges), announce: "I have enough to build your spec. Let me set up the workspace."
- If the user provides a reference repo/URL, use `/absorb` to scan it before proceeding.

### Phase 2: Workspace Creation (automatic)

After gathering enough context, create the workspace automatically. Do not ask for confirmation.

**Steps:**

1. Derive a workspace name from the project (kebab-case, e.g., `invoice-tracker`).
2. Determine the workspace root directory. Use the platform-appropriate location:
   - Check if `workspaces_root` is configured; if not, ask the user where they keep projects.
3. Create the workspace directory at `<workspaces_root>/<workspace_name>/`.
4. Create a private GitHub repo:
   ```bash
   gh repo create <workspace_name> --private --clone
   ```
   If `auto_create_github` config is `false`, skip this step and just `git init` instead.
5. Initialize memory:
   ```bash
   python scripts/init_db.py
   ```
   This creates `memory.db` in the workspace.
6. Create `CLAUDE.md` in the workspace root with project-specific instructions derived from Phase 1 answers.
7. Create directory structure:
   ```
   <workspace>/
   ├── CLAUDE.md
   ├── knowledge/
   ├── skills/learned/
   └── openspec/
       ├── project.md
       ├── changes/
       └── specs/
   ```
8. Register the workspace in `workspaces.json`.
9. Make an initial git commit: `git commit -m "Initialize workspace"`.

### Phase 3: Spec Generation (YOU produce, user reviews)

Generate OpenSpec-style artifacts inside the workspace. Think deeply about architecture before writing.

**Output structure:**

```
<workspace>/openspec/
├── project.md                    ← Project context from Phase 1
├── changes/v1/
│   ├── proposal.md               ← Why + What Changes
│   ├── design.md                 ← Architecture, data flows, tech stack
│   ├── tasks.md                  ← Phased task list with file paths
│   └── specs/
│       ├── <capability-1>/spec.md  ← Gherkin scenarios
│       ├── <capability-2>/spec.md
│       └── ...
```

#### project.md

Capture the full project context from the discovery conversation:

```markdown
# <Project Name>

## Vision
[What this project is and why it exists]

## Audience
[Who uses it and how]

## Tech Stack
[Chosen technologies and why]

## Scope
[MVP / Standard / Enterprise — what's in, what's out]

## Integrations
[External systems, APIs, databases]

## Constraints
[Non-negotiable requirements]

## References
[Competitor projects, inspiration, absorbed repos]
```

#### proposal.md

Every proposal MUST have these two sections:

```markdown
# V1 Proposal: <Project Name>

## Why
[Problem statement, background, motivation. Why does this need to exist?]

## What Changes
[New capabilities being introduced. Be specific.]

### In Scope
- [Capability 1]
- [Capability 2]
- ...

### Out of Scope
- [Explicitly excluded items]
- [Things deferred to later versions]
```

#### design.md

```markdown
# V1 Design: <Project Name>

## Architecture
[High-level architecture diagram in text/mermaid. Component responsibilities.]

## Data Model
[Core entities, relationships, storage strategy]

## API Design
[Endpoints, protocols, authentication — if applicable]

## Data Flow
[Key user journeys mapped to system interactions]

## Technology Choices
[Stack details with rationale for each choice]

## Security Considerations
[Auth, input validation, secrets management]

## Deployment
[How this runs — local, cloud, containerized, etc.]
```

#### tasks.md

The heartbeat of the spec. Every task must be:
- **Small enough** to complete in one focused session (5-30 minutes of work)
- **Specific enough** to include the target file path
- **Ordered** so dependencies come first
- **Phased** for logical grouping

Format:

```markdown
# V1 Tasks: <Project Name>

## Phase 1: Foundation
- [ ] Initialize project structure — `src/`, `tests/`, configs
- [ ] Set up dependency management — `package.json` / `pyproject.toml`
- [ ] Configure linter and formatter — `.eslintrc`, `.prettierrc`
- [ ] Set up test framework — `jest.config.ts` / `pytest.ini`
- [ ] Create CI pipeline — `.github/workflows/ci.yml`

## Phase 2: Core Domain
- [ ] Define data models (`src/domain/models.ts`)
- [ ] Implement core business logic (`src/services/core.ts`)
- [ ] Add unit tests for core logic (`tests/unit/core.test.ts`)
...

## Phase 3: API Layer
- [ ] Set up API framework (`src/api/server.ts`)
- [ ] Implement endpoints (`src/api/routes/`)
- [ ] Add API validation middleware (`src/api/middleware/`)
- [ ] Write API integration tests (`tests/integration/api.test.ts`)
...

## Phase 4: Frontend (if applicable)
...

## Phase 5: Integration & Polish
- [ ] End-to-end tests (`tests/e2e/`)
- [ ] Documentation (`README.md`)
- [ ] Environment configuration (`.env.example`)
- [ ] Final review and cleanup
```

Target: **100-300 tasks** for a standard project. Fewer for MVP, more for enterprise.

#### specs/<capability>/spec.md

Gherkin-style behavioral specs for each major capability:

```markdown
# Spec: <Capability Name>

## Overview
[What this capability does]

## Scenarios

### Scenario: <Happy path>
Given [precondition]
When [action]
Then [expected result]

### Scenario: <Edge case>
Given [precondition]
When [action]
Then [expected result]

### Scenario: <Error case>
Given [precondition]
When [action]
Then [expected result]
```

**After generating all spec files:**
- Present a summary to the user: number of capabilities, number of tasks, phases.
- Ask: "Want to review or adjust anything before I load the TODOs?"
- If the user says it looks good, proceed to Phase 4.

### Phase 4: Load TODOs

Automatically parse `tasks.md` and load everything into memory:

1. **Parse tasks.md** — extract every `- [ ]` line with its phase context.
2. **Create TODOs** — call `memory_todo_add()` for each task:
   - `title`: the task text
   - `description`: include the phase name and any file paths mentioned
   - `priority`: Phase 1 = priority 1, Phase 2 = priority 2, etc. (cap at 3)
3. **Record decisions** — call `memory_record_decision()` for each major decision from Phase 1 (tech stack, architecture choices, scope decisions).
4. **Store project context** — call `memory_record_knowledge()` with the project.md content.
5. **Report summary:**
   ```
   Spec loaded:
   |- 47 tasks across 5 phases
   |- 6 decisions recorded
   |- Project context stored
   \- Ready to blitz? (y/n)
   ```

### Phase 5: Blitz (optional, user confirms)

Only start if the user confirms. This is the execution phase.

**Blitz protocol:**

1. **Activate blitz** — create a `.blitz-active` marker file in the workspace root:
   ```json
   { "started": "<ISO timestamp>", "change": "v1", "phase": 1 }
   ```
2. **Execute tasks sequentially** from `tasks.md`, phase by phase:
   - Read the next `- [ ]` task
   - Complete it (create files, write code, configure tools)
   - Mark it done: change `- [ ]` to `- [x]` in `tasks.md`
   - Update TODO status via `memory_todo_update()` to `approved`
   - Continue to the next task
3. **Commit after each phase:**
   ```bash
   git add -A
   git commit -m "Phase N: <phase title> complete"
   ```
4. **Report progress** after each phase:
   ```
   Phase 2 complete: 12/47 tasks done (25%)
   Moving to Phase 3: API Layer...
   ```
5. **On completion:**
   - Remove `.blitz-active` marker file
   - Final commit:
     ```bash
     git commit -m "V1 blitz complete"
     ```
   - Report:
     ```
     Blitz complete. V1 is ready.
     |- 47/47 tasks completed
     |- 5 phases across N commits
     \- Evolve mode is now active for this workspace.
     ```

**Blitz behavior rules:**

- **Do not ask questions during blitz.** The spec is the plan. Execute it.
- If something is ambiguous, make a reasonable decision and document it in a code comment.
- If a task fails (e.g., dependency issue), log the error, mark the TODO with a note, and continue to the next task. Do not block.
- Check for `.blitz-active` marker before any evolve-tick. If present, skip evolve entirely.

---

## Mode 2: `/spec:status` — Show Current Spec Status

Read the workspace state and display:

```
Workspace: <name>
Active Change: v1
Blitz: active / inactive

Phase Progress:
  Phase 1: Foundation        ████████████ 8/8  (100%)
  Phase 2: Core Domain       ████████░░░░ 7/12 (58%)
  Phase 3: API Layer         ░░░░░░░░░░░░ 0/10 (0%)
  Phase 4: Frontend          ░░░░░░░░░░░░ 0/9  (0%)
  Phase 5: Integration       ░░░░░░░░░░░░ 0/8  (0%)

Overall: 15/47 tasks (32%)
```

**How to determine status:**
1. Find the active workspace (current directory or ask).
2. Read `openspec/changes/*/tasks.md` — count `[x]` vs `[ ]` per phase.
3. Check for `.blitz-active` marker file.
4. Display the progress table.

---

## Mode 3: `/spec:add "feature description"` — Add to Existing Spec

Create a new change for an existing workspace.

1. **Validate** — confirm the workspace exists and has an `openspec/` directory.
2. **Discover** — ask 2-3 clarifying questions about the new feature (lighter than full Phase 1).
3. **Name the change** — derive a kebab-case name (e.g., `add-notifications`).
4. **Generate artifacts** under `openspec/changes/<change-name>/`:
   - `proposal.md` — why + what changes
   - `design.md` — how it fits into the existing architecture
   - `tasks.md` — new tasks only, referencing existing code structure
   - `specs/<capability>/spec.md` — behavioral specs for new capabilities
5. **Load TODOs** — parse and add new tasks to memory.
6. **Report** — "Added N tasks for '<feature>'. Run `/spec:blitz` to execute."
7. **Do NOT auto-start blitz.** Let the user review first.

---

## Mode 4: `/spec:archive` — Archive Completed Change

Archive a change after all its tasks are complete.

1. **Verify completion** — read `tasks.md` and confirm all items are `[x]`. If not, report remaining tasks and abort.
2. **Move specs** — copy capability specs from `openspec/changes/<change>/specs/` to `openspec/specs/` (the permanent truth source).
3. **Store knowledge** — record proposal.md and design.md content via `memory_record_knowledge()` with appropriate tags.
4. **Record decisions** — extract key decisions from the change and store via `memory_record_decision()`.
5. **Git commit:**
   ```bash
   git add -A
   git commit -m "Archive change: <change-name>"
   ```
6. **Report:**
   ```
   Archived: <change-name>
   |- Specs merged to openspec/specs/
   |- N knowledge items stored
   |- N decisions recorded
   ```

---

## Mode 5: `/spec:blitz` — Resume or Start Blitz

If there are pending tasks in any change:

1. **Find pending work** — scan `openspec/changes/*/tasks.md` for unchecked items.
2. If `.blitz-active` exists, resume from where it left off (read the marker to find current phase).
3. If no marker, create one and start from the first unchecked task.
4. Follow the same blitz protocol as Phase 5 above.

If no pending tasks exist:
```
No pending tasks found. Use /spec:add to add new features, or /spec new to start a new project.
```

---

## Critical Instructions

1. **YOU lead the conversation.** Do not wait for the user to know what to ask. Ask smart questions, make recommendations, explain trade-offs.

2. **Use extended thinking** for Phase 1 and Phase 3. Think deeply about architecture before generating specs. Consider edge cases, scalability, and maintainability.

3. **Be opinionated.** When the user says "whatever you think is best," make a strong recommendation with reasoning. Do not present five options and ask them to choose.

4. **tasks.md is the heartbeat.** Every task should be small enough to complete in one focused session (5-30 minutes of work). If a task would take longer, split it into subtasks.

5. **During blitz, do not ask questions.** The spec is the plan. Execute it. If something is ambiguous, make a reasonable decision and document it in a code comment or the task's TODO note.

6. **Never run evolve during blitz.** Check for `.blitz-active` marker. If present, skip evolve-tick entirely.

7. **After blitz, set up for evolution.** Remove the marker, ensure evolve-tick can find any remaining or new TODOs.

8. **Commit early, commit often.** During blitz, commit after each completed phase. Outside blitz, commit after spec generation and after archiving.

---

## File Safety

- All spec files go inside the workspace directory, NEVER in the clawd-lobster repo itself.
- Commit `openspec/` to the workspace's git repo.
- Never commit credentials, secrets, API keys, or tokens to spec files.
- Never include personal names, hardcoded user paths, or machine-specific information in spec files.
- If the user provides sensitive information during discovery, store it in environment variables or a `.env` file (gitignored), not in the spec.
