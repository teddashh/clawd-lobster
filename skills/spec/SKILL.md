# Spec — Guided Workspace Creation & Spec-Driven Development

!git branch --show-current 2>/dev/null || echo "Not in a git repo"
!ls .blitz-active 2>/dev/null && echo "BLITZ ACTIVE — check before evolving" || echo "No active blitz"
!find . -path "*/openspec/changes/*/tasks.md" -exec grep -c "^\- \[ \]" {} + 2>/dev/null || echo "No pending tasks"

The most important skill in Clawd-Lobster. You LEAD the user through planning,
spec generation, and blitz execution. The user answers questions; you do everything else.

**Philosophy:** Every artifact follows 3W1H — Why (motivation), What (scope),
Who (audience), How (approach). Specs use SHALL/MUST for testable requirements.
Tasks reference file paths. The dependency DAG is strict. Blitz is autonomous.

---

## CRITICAL: Constraint ≠ Output

The instructions in this SKILL.md are constraints for YOUR behavior.
They are NOT content to copy into generated spec files.

- Wrong: Copying "MUST have ## Why section" into proposal.md
- Right: Writing a compelling ## Why section based on user's answers

The spec files should read like professional documents written by a human
architect, not like a checklist of meta-rules about how to write specs.

---

## Modes

| Invocation | Mode | Description |
|-----------|------|-------------|
| `/spec` or `/spec new` | **Create** | Full guided flow: discovery → workspace → spec → TODOs → blitz |
| `/spec:squad` | **Squad** | Multi-session spec flow: Architect writes → Reviewer challenges → Coder builds → Tester verifies |
| `/spec:status` | **Status** | Show current spec progress and blitz state |
| `/spec:add "feature"` | **Add** | Add a new change to an existing spec (with delta operations) |
| `/spec:archive` | **Archive** | Archive a completed change + store as knowledge |
| `/spec:blitz` | **Blitz** | Start or resume blitz execution (with branch isolation) |

---

## Mode 1: `/spec` or `/spec new` — Guided Workspace + Spec Creation

Five phases, executed sequentially.

### Phase 1: Discovery (YOU ask, user answers)

Enter planning mode. Extract enough context to generate a complete spec.
Ask conversationally — not as a checklist. Adapt based on answers.

**3W1H discovery questions:**

1. **Why** — "What problem does this solve? What happens if we don't build it?"
2. **What** — "What do you want to build? What's the high-level picture?"
3. **Who** — "Who will use this? End users? Internal team? API consumers?"
4. **How** — "What tech stack? Any preferences or should I recommend?"
5. **Scope** — "MVP or full product? What's the timeline pressure?"
6. **Integrations** — "External systems? Databases, APIs, payment, auth?"
7. **References** — "Reference projects or competitors?" Use `/absorb` on any URLs.
8. **Constraints** — "Non-negotiable requirements? Performance, compliance, a11y?"

**Behavior rules:**

- YOU lead. Do not wait for the user to know what to ask.
- Be opinionated. "Whatever you think is best" = make a strong recommendation with trade-offs.
- Ask one or two questions at a time, not all eight at once.
- When you have enough context (typically 3-6 exchanges), announce:
  "I have enough to build your spec. Let me set up the workspace."
- If the user provides a reference repo/URL, use `/absorb` to scan it first.

### Phase 2: Workspace Creation (automatic)

After gathering enough context, create the workspace. Do not ask for confirmation.

1. Derive a workspace name from the project (kebab-case, e.g., `invoice-tracker`).
2. Determine the workspace root:
   - Check if `workspaces_root` is configured; if not, ask the user where they keep projects.
3. Create the workspace directory at `<workspaces_root>/<workspace_name>/`.
4. Create a private GitHub repo: `gh repo create <workspace_name> --private --clone`
   (If `auto_create_github` is `false`, just `git init` instead.)
5. Initialize memory: `python scripts/init_db.py`
6. Create `CLAUDE.md` in workspace root with project-specific instructions from Phase 1.
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
9. Initial commit: `git commit -m "Initialize workspace"`.

### Phase 3: Spec Generation (YOU produce, user reviews)

Generate OpenSpec-style artifacts inside the workspace. Use extended thinking
to reason deeply about architecture before writing.

#### Artifact Dependency Order

Artifacts MUST be generated in this strict order:

```
project.md → proposal.md → design.md → specs/ → tasks.md
```

Why this order is mandatory:
- **project.md** captures raw context — everything downstream reads it
- **proposal.md** defines scope boundaries — design needs to know what's in/out
- **design.md** defines architecture — specs need to know component boundaries
- **specs/** define testable requirements — tasks need requirements to implement
- **tasks.md** references all of the above — it's the last thing generated

Never generate tasks.md before design.md is complete. Never write specs
before the architecture is decided. The DAG is strict.

#### Output structure

```
<workspace>/openspec/
├── project.md
├── changes/v1/
│   ├── proposal.md
│   ├── design.md
│   ├── tasks.md
│   └── specs/
│       ├── <capability-1>/spec.md
│       ├── <capability-2>/spec.md
│       └── ...
```

#### project.md (3W1H: context capture)

```markdown
# <Project Name>

## Why
[Problem statement. What pain exists today?]

## What
[What this project is. High-level description.]

## Who
[Target audience and their relationship to the system]

## How
[Tech stack choices and rationale]

## Scope
[MVP / Standard / Enterprise — what's in, what's out]

## Integrations
[External systems, APIs, databases]

## Constraints
[Non-negotiable requirements]

## References
[Competitor projects, inspiration, absorbed repos]
```

#### proposal.md (3W1H: scope definition)

```markdown
# V1 Proposal: <Project Name>

## Why
[Problem statement, background, motivation. Min 2-3 sentences.]

## What Changes
[New capabilities being introduced. Be specific.]

### In Scope
- [Capability 1]
- [Capability 2]

### Out of Scope
- [Explicitly excluded items]
- [Things deferred to later versions]

## Who
[Who benefits from this change and how they'll interact with it]

## How
[High-level approach — not architecture details, just the strategy]
```

#### design.md (3W1H: architecture blueprint)

```markdown
# V1 Design: <Project Name>

## Architecture
[High-level diagram in text/mermaid. Component responsibilities.
Include WHY this architecture was chosen over alternatives.]

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

#### specs/\<capability\>/spec.md (testable requirements)

Requirements MUST use SHALL or MUST — never "should", "could", or "might".
Each requirement MUST have at least one Gherkin scenario.

```markdown
# Spec: <Capability Name>

## Requirements
- The system SHALL [requirement 1]
- The system MUST [requirement 2]

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

#### tasks.md (phased execution plan)

Every task must be:
- **Completable** in 5-30 minutes of focused work
- **File-referenced** — include the target file path in backticks or parentheses
- **Phased** — grouped by logical phase
- **Sequentially dependent** — Phase N depends on Phase N-1

```markdown
# V1 Tasks: <Project Name>

## Phase 1: Foundation
- [ ] Initialize project structure (`src/`, `tests/`, configs)
- [ ] Set up dependency management (`package.json`)
- [ ] Configure linter and formatter (`.eslintrc`, `.prettierrc`)
- [ ] Set up test framework (`jest.config.ts`)
- [ ] Create CI pipeline (`.github/workflows/ci.yml`)

## Phase 2: Core Domain
- [ ] Define data models (`src/domain/models.ts`)
- [ ] Implement core business logic (`src/services/core.ts`)
- [ ] Add unit tests for core logic (`tests/unit/core.test.ts`)
...

## Phase 3: API Layer
...

## Phase N: Integration & Polish
- [ ] End-to-end tests (`tests/e2e/`)
- [ ] Documentation (`README.md`)
- [ ] Environment configuration (`.env.example`)
- [ ] Final review and cleanup
```

Target: **100-300 tasks** for a standard project. Fewer for MVP, more for enterprise.

#### Task Delegation Markers

Tasks can be marked for external execution engine delegation:

- `- [ ] [codex] Task description` — Delegatable to external engine (Codex, etc.)
- `- [ ] Task description` — Claude handles directly

The /spec skill does not implement delegation — it recognizes the marker and
skips those tasks during blitz. A separate skill handles delegated execution.

#### Self-Validation (run after EACH artifact)

After generating each artifact, run the matching checks from the
**Self-Validation Checklist** (bottom of this file). Fix failures BEFORE
generating the next artifact in the DAG.

**After generating all artifacts:**
- Present summary: number of capabilities, number of tasks, phases.
- Ask: "Want to review or adjust anything before I load the TODOs?"
- If approved, proceed to Phase 4.

### Phase 4: Load TODOs

Parse `tasks.md` and load into memory:

1. **Parse tasks.md** — extract every `- [ ]` line with phase context.
2. **Create TODOs** — call `memory_todo_add()` for each task:
   - `title`: the task text
   - `description`: phase name + file paths + 3W1H tag (which artifact it traces to)
   - `priority`: Phase 1 = priority 1, Phase 2 = priority 2, etc. (cap at 3)
3. **Record decisions** — call `memory_record_decision()` for major Phase 1 decisions.
4. **Store project context** — call `memory_record_knowledge()` with project.md content.
5. **Report:**
   ```
   Spec loaded:
   |- 47 tasks across 5 phases
   |- 6 decisions recorded
   |- Project context stored
   \- Ready to blitz? (y/n)
   ```

### Phase 5: Blitz (optional, user confirms)

Only start if the user confirms. This is the execution phase.
All work happens on a `blitz/<change>` branch — main stays clean until verified.

**Blitz execution:**

1. **Create blitz branch:** `git checkout -b blitz/v1`
2. **Create `.blitz-active` marker** in workspace root:
   ```json
   { "started": "<ISO timestamp>", "change": "v1", "phase": 1 }
   ```
3. **Execute tasks sequentially**, phase by phase:
   - Read the next `- [ ]` task (skip `[codex]`-prefixed tasks)
   - Complete it (create files, write code, configure tools)
   - Mark done: `- [ ]` → `- [x]` in `tasks.md`
   - Update TODO via `memory_todo_update()` to `approved`
4. **Commit after each phase:** `git add -A && git commit -m "Phase N: <phase title> complete"`
5. **Report after each phase:** `Phase 2 complete: 12/47 tasks done (25%)`
6. **On completion — post-blitz hook:**
   - Remove `.blitz-active` marker
   - Merge: `git checkout main && git merge blitz/v1`
   - Store entire spec as knowledge via `memory_record_knowledge()`
   - Suggest next steps: run tests, `/spec:add` for new features, `/spec:archive` when satisfied

**Blitz rules:** No questions — the spec is the plan. If ambiguous, decide and
comment. If a task fails, log it, note the TODO, continue. Never block.
Check `.blitz-active` before evolve-tick — if present, skip evolve.

---

## Mode 2: `/spec:squad` — Multi-Session Spec Flow

Run the full spec-to-code pipeline using separate Claude sessions for each role.
This provides adversarial review and role isolation — the Architect can't see the
Reviewer's prompt, so the review is genuinely independent.

**The Team:**

| Role | ID | What It Does |
|------|----|-------------|
| **Architect** | `A` | Writes the complete OpenSpec (same DAG as Phase 3 above) |
| **Reviewer** | `R` | Challenges the spec — finds gaps, ambiguities, weak decisions |
| **Coder** | `C` | Builds exactly what the approved spec says (blitz mode) |
| **Tester** | `T` | Verifies code against spec requirements and Gherkin scenarios |

**Flow:**

```
[A] Architect writes spec
        │
        ▼
[R] Reviewer challenges  ←──┐
        │                    │ (max 5 rounds)
        ▼                    │
[A] Architect revises ───────┘
        │
        ▼ (APPROVED)
[C] Coder builds
        │
        ▼
[T] Tester verifies
```

**Invocation:**

After completing Phase 1 (Discovery) and Phase 2 (Workspace Creation), instead of
generating the spec yourself, hand off to the squad:

```bash
python scripts/spec-squad.py <workspace-path> --project "description"
```

Or from within Claude Code:
1. Complete discovery (Phase 1) and workspace creation (Phase 2) as normal
2. Run: `python scripts/spec-squad.py <workspace> --project "description from discovery"`

**Options:**
- `--plan-only` — Run Architect + Reviewer only, skip Coder/Tester
- `--phase review` — Resume from review phase
- `--status` — Show current squad state
- `--max-rounds 3` — Limit review rounds (default: 5)
- `--reset` — Start fresh

**State file:** `.spec-squad.json` in the workspace root tracks progress and
allows resumption if interrupted.

**Key difference from solo `/spec`:** In solo mode, Claude self-validates using
the checklist. In squad mode, a separate Claude session acts as an adversarial
reviewer with no knowledge of the checklist — it finds issues the checklist
wouldn't catch because it thinks independently.

---

## Mode 3: `/spec:status` — Show Current Spec Status

Read workspace state and display:

```
Workspace: <name>
Active Change: v1
Blitz: active / inactive (branch: blitz/v1)

Phase Progress:
  Phase 1: Foundation        ████████████ 8/8  (100%)
  Phase 2: Core Domain       ████████░░░░ 7/12 (58%)
  Phase 3: API Layer         ░░░░░░░░░░░░ 0/10 (0%)
  Phase 4: Frontend          ░░░░░░░░░░░░ 0/9  (0%)
  Phase 5: Integration       ░░░░░░░░░░░░ 0/8  (0%)

Overall: 15/47 tasks (32%)
Delegated: 3 tasks marked [codex] (not counted in blitz progress)
```

Determine status by reading `openspec/changes/*/tasks.md` (count `[x]` vs `[ ]`
per phase) and checking for `.blitz-active` marker.

---

## Mode 4: `/spec:add "feature"` — Add to Existing Spec (Delta Operations)

Create a new change for an existing workspace using delta operations.

1. **Validate** — confirm workspace exists and has `openspec/` directory.
2. **Discover** — ask 2-3 clarifying questions (lighter than full Phase 1).
3. **Name the change** — derive kebab-case name (e.g., `add-notifications`).
4. **Generate delta artifacts** under `openspec/changes/<change-name>/`:

   proposal.md, design.md, tasks.md, and specs/ — same format as Mode 1,
   but design.md MUST reference the existing architecture and explain how
   the new feature integrates.

   **Delta classification in proposal.md:**

   ```markdown
   ## Delta Summary
   ### ADDED — New capabilities
   - [New capability 1]

   ### MODIFIED — Changes to existing behavior
   - [Modified capability 1]: was X, now Y

   ### REMOVED — Deprecated features
   - [Removed capability 1]: reason
   ```

   Apply order when implementing: **RENAME → REMOVE → MODIFY → ADD**

5. **Run self-validation** on all generated artifacts (same checks as Mode 1).
6. **Load TODOs** — parse and add new tasks to memory.
7. **Report** — "Added N tasks for '\<feature\>'. Run `/spec:blitz` to execute."
8. **Do NOT auto-start blitz.** Let the user review first.

---

## Mode 5: `/spec:archive` — Archive Completed Change

Archive a change after all tasks are complete.

1. **Verify completion** — read `tasks.md`, confirm all items are `[x]`. If not, report remaining and abort.
2. **Move specs** — copy capability specs from `openspec/changes/<change>/specs/` to `openspec/specs/` (permanent truth source).
3. **Store knowledge** — record proposal.md and design.md via `memory_record_knowledge()`.
4. **Record decisions** — extract key decisions and store via `memory_record_decision()`.
5. **Git commit:** `git add -A && git commit -m "Archive change: <change-name>"`
6. **Report:** specs merged count, knowledge items stored, decisions recorded.

---

## Mode 6: `/spec:blitz` — Resume or Start Blitz

If there are pending tasks in any change:

1. **Find pending work** — scan `openspec/changes/*/tasks.md` for unchecked items.
2. If `.blitz-active` exists, resume from where it left off (read marker for current phase).
3. If no marker, create blitz branch and marker, start from first unchecked task.
4. Follow the same blitz protocol as Phase 5 above (branch isolation, phase commits, post-blitz hook).

If no pending tasks exist:
```
No pending tasks found. Use /spec:add to add new features, or /spec new to start a new project.
```

---

## Self-Validation Checklist

Run this after generating ANY spec artifact. This is YOUR internal checklist —
do not expose it to the user or copy it into generated files.

### proposal.md
- [ ] Has `## Why` (50-1000 chars of real motivation, not filler)
- [ ] Has `## What Changes` with specific capabilities listed
- [ ] Has `## Who` defining the audience
- [ ] Has `### In Scope` and `### Out of Scope` subsections
- [ ] 3W1H coverage: Why, What, Who, How all addressed

### design.md
- [ ] Has `## Architecture` with component diagram or description
- [ ] Has `## Data Model` with entities and relationships
- [ ] Has `## Deployment` with runtime strategy
- [ ] Architecture rationale explains WHY, not just WHAT

### specs/
- [ ] Requirements use SHALL or MUST (grep for "should", "could", "might" — zero matches)
- [ ] Every requirement has >= 1 Gherkin scenario
- [ ] All scenarios follow Given/When/Then
- [ ] Each spec lives in `specs/<capability>/spec.md`

### tasks.md
- [ ] Every task has a file path in backticks
- [ ] Tasks are grouped by named phases
- [ ] No task exceeds 30 minutes of work (split if needed)
- [ ] Phase N only depends on Phase N-1 (no circular or skip dependencies)
- [ ] `[codex]` markers are used where appropriate for delegatable tasks

### Cross-artifact
- [ ] Artifact generation followed the DAG: project → proposal → design → specs → tasks
- [ ] No artifact references content from a later artifact in the DAG
- [ ] All file paths in tasks.md align with the directory structure in design.md

---

## Critical Instructions

1. **YOU lead the conversation.** Do not wait for the user to know what to ask. Ask smart questions, make recommendations, explain trade-offs.

2. **Use extended thinking** for Phase 1 and Phase 3. Think deeply about architecture before generating specs. Consider edge cases, scalability, and maintainability.

3. **Be opinionated.** "Whatever you think is best" = make a strong recommendation with reasoning. Do not present five options and ask them to choose.

4. **3W1H consistency.** Every artifact must address Why, What, Who, and How at its appropriate level. project.md is broad context. proposal.md is scope. design.md is architecture. specs are requirements. tasks are execution.

5. **tasks.md is the heartbeat.** Every task: 5-30 minutes, file path included, phased. If a task would take longer, split it.

6. **During blitz, do not ask questions.** The spec is the plan. Execute it.

7. **Never run evolve during blitz.** Check `.blitz-active` marker first.

8. **Branch isolation during blitz.** Work on `blitz/<change>` branch. Merge to main only after all phases complete.

9. **Constraint ≠ Output.** These rules constrain YOUR generation behavior. The generated documents should read like professional engineering documents, not like rule-echo.

10. **Delegation markers are passive.** Recognize `[codex]` tasks, skip them during blitz, but do not implement the delegation mechanism.

---

## File Safety

- All spec files go inside the workspace directory, NEVER in the clawd-lobster repo itself.
- Commit `openspec/` to the workspace's git repo.
- Never commit credentials, secrets, API keys, or tokens to spec files.
- Never include personal names, hardcoded user paths, or machine-specific information.
- If the user provides sensitive information during discovery, store it in environment variables or a `.env` file (gitignored), not in the spec.

## Gotchas

1. **Generating tasks.md before design.md.** Claude gets eager and jumps to task generation because it "knows enough." The DAG is strict: project.md, then proposal.md, then design.md, then specs/, then tasks.md. Generating tasks without a finalized architecture means tasks reference files and patterns that don't exist yet.

2. **Copying SKILL.md constraints into generated spec files.** This file contains behavioral constraints for Claude, not content for output documents. The generated proposal.md should read like a professional engineering document, not a meta-checklist of "MUST have ## Why section." Constraint does not equal output.

3. **Tasks without file paths.** Every task in tasks.md MUST include a target file path in backticks. "Implement authentication" is not a valid task. "Implement authentication middleware (`src/middleware/auth.ts`)" is. Without file paths, blitz execution stalls because Claude doesn't know where to write.

4. **Asking questions during blitz.** Once blitz starts, the spec is the plan. Claude tends to pause and ask "should I use library X or Y?" mid-blitz. If the spec is ambiguous, decide, add a comment explaining the choice, and continue. Never block on user input during blitz.

5. **Running evolve during an active blitz.** The `.blitz-active` marker exists to prevent evolve-tick from extracting patterns from half-finished work. If Claude manually invokes evolve or if the cron fires during blitz, check for the marker first and skip. Evolving mid-build causes style inconsistency across phases.
