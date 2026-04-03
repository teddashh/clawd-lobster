# Evolve — Hybrid Self-Evolution System

Two modes: **automatic** (cron) and **interactive** (user-invoked).

---

## Automatic Mode (Cron)

Every 2 hours, `scripts/evolve-tick.py` runs and:

1. **Scans** all workspace `memory.db` files for TODO items with `status='pending'`
2. **Picks** the highest-priority pending TODO (priority ASC, then oldest first)
3. **Creates a git worktree** for isolated work:
   ```
   git -C <workspace> worktree add /tmp/evolve-<id> -b evolve/<id>-<slug>
   ```
4. **Runs Claude Code** in print mode inside the worktree to complete the TODO
5. **Updates status**:
   - If Claude made commits: status becomes `staged` with the branch name recorded
   - If no changes or error: status becomes `in_progress` with a note explaining why
6. **Logs the action** via `action_log` for audit trail

### Key constraints
- Only processes **ONE** todo per tick (keeps it simple and safe)
- **Never auto-merges** to main — all work stays on feature branches
- Timeout: 5 minutes per TODO
- All work happens in git worktrees (isolated from the working tree)

### TODO table schema

The `todos` table in `memory.db` (created by `scripts/init_db.py`):

| Column       | Type    | Description                                           |
|-------------|---------|-------------------------------------------------------|
| id          | TEXT PK | Unique identifier                                     |
| title       | TEXT    | Short description of what needs to be done             |
| description | TEXT    | Detailed context, acceptance criteria                  |
| priority    | INTEGER | 1=high, 2=medium (default), 3=low                     |
| status      | TEXT    | pending / in_progress / staged / approved / rejected   |
| branch      | TEXT    | Git branch name (set when staged)                      |
| note        | TEXT    | Processing notes (Claude output, error messages)       |
| workspace   | TEXT    | Workspace name                                         |
| created_at  | TEXT    | ISO timestamp                                          |
| updated_at  | TEXT    | ISO timestamp (updated on status change)               |

---

## Interactive Mode (User-Invoked)

When you invoke `/evolve` or the agent detects a skill-worthy pattern:

### Pattern Detection

After completing a complex task (3+ tool calls or multi-step reasoning), evaluate:
1. Was a reusable pattern discovered?
2. Does it apply to future similar tasks?
3. Is it not already covered by an existing skill?

If all true, generate a learned skill in `skills/learned/`:

```markdown
# [Skill Name]

## When to use
[Trigger conditions]

## Approach
[Step-by-step pattern]

## Key decisions
[Non-obvious choices]

## Tools used
[MCP tools / Claude Code tools involved]

## Learned from
- Date: [YYYY-MM-DD]
- Workspace: [workspace name]
- Task: [brief description]
```

### Manual TODO Processing

Users can also trigger "process next TODO" interactively:
- Review what TODOs are pending
- Choose which one to process
- Watch Claude work on it in real-time

### Staged Branch Review

Users can review branches created by automatic mode:
- List staged TODOs and their branches
- Review the diff for each branch
- Approve or reject

---

## Review Workflow

When a TODO reaches `status='staged'`:

1. **Discover**: User sees staged TODOs in the Workspace tab of the Web UI, or via `memory_search` for status=staged
2. **Review**: User clicks "Review with Claude" (or asks interactively)
3. **Explain**: Claude explains what changes were made and why
4. **Decide**:
   - **Approve**: Merge the branch and clean up the worktree
     ```bash
     git -C <workspace> merge evolve/<id>-<slug>
     git -C <workspace> worktree remove /tmp/evolve-<id>
     git -C <workspace> branch -d evolve/<id>-<slug>
     ```
     Update TODO status to `approved`.
   - **Reject**: Archive the branch and record what was learned
     ```bash
     git -C <workspace> worktree remove /tmp/evolve-<id>
     git -C <workspace> branch -D evolve/<id>-<slug>
     ```
     Update TODO status to `rejected` with a note explaining why.

---

## Git Workflow

- Evolve **creates branches**, never pushes to main
- All work happens in **worktrees** (isolated from the main working tree)
- Branch naming: `evolve/<todo_id>-<slugified-title>`
- Worktree location: `<temp_dir>/evolve-<todo_id>`
- **Clean up** after approve/reject: `git worktree remove` + branch delete

---

## Skill Improvement

When using a previously learned skill:
1. Check if the approach still works
2. If modified, **update** the skill file with improvements
3. Add a `## Revision history` section tracking what changed and why

## Skill Retirement

If a learned skill hasn't been useful in 90+ days (check via `memory_search`), suggest archiving it:
- Move to `skills/learned/archive/`
- The user decides whether to keep or delete

---

## Examples of Good Learned Skills

- "How to debug Oracle connection issues on AVD" (specific env + solution pattern)
- "Optimal git workflow for multi-workspace sync" (sequence of operations)
- "PowerShell Task Scheduler registration pattern" (reusable script template)
- "CJK-heavy document summarization approach" (token management strategy)

## Examples of Things That Are NOT Skills

- One-off fixes (just use `memory_record_resolved`)
- Simple facts (just use `memory_record_knowledge`)
- User preferences (belongs in `CLAUDE.md` or `soul/`)
