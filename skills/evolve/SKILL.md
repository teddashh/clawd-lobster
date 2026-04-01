# Evolve — Self-Improving Skill System

Your agents don't just execute tasks — they learn from them.

After completing complex or multi-step tasks, the agent should automatically evaluate whether the experience contains a reusable pattern worth saving as a new skill.

## When to evolve

Trigger skill generation when ALL of these are true:
1. A non-trivial task was completed successfully (3+ tool calls, or multi-step reasoning)
2. The approach involved a pattern that could apply to future similar tasks
3. No existing skill already covers this pattern

## How to evolve

### Step 1: Detect the pattern
After completing a task, reflect:
- What was the task type? (debugging, refactoring, data analysis, deployment, etc.)
- What sequence of tools/steps solved it?
- What non-obvious decisions were made?
- Would this approach work for similar problems?

### Step 2: Generate the skill
Create a new file in `skills/learned/` with this format:

```markdown
# [Skill Name]

## When to use
[Describe the trigger conditions — what kind of task/question activates this skill]

## Approach
[Step-by-step pattern that worked]

## Key decisions
[Non-obvious choices that made this successful]

## Tools used
[Which MCP tools or Claude Code tools were involved]

## Learned from
- Date: [YYYY-MM-DD]
- Workspace: [workspace name]
- Task: [brief description of the original task]
```

### Step 3: Announce it
Tell the user: "I noticed a reusable pattern and saved it as a skill: [name]. It will be available in future sessions."

## Skill improvement

When using a previously learned skill:
1. Check if the skill's approach still works
2. If you had to modify the approach, UPDATE the skill file with improvements
3. Add a `## Revision history` section tracking what changed and why

## Skill retirement

If a learned skill hasn't been useful in 90+ days (check via `memory_search`), suggest archiving it:
- Move to `skills/learned/archive/`
- The user decides whether to keep or delete

## Examples of good learned skills

- "How to debug Oracle connection issues on AVD" (specific env + solution pattern)
- "Optimal git workflow for multi-workspace sync" (sequence of operations)
- "PowerShell Task Scheduler registration pattern" (reusable script template)
- "CJK-heavy document summarization approach" (token management strategy)

## Examples of things that are NOT skills

- One-off fixes (just use memory_record_resolved)
- Simple facts (just use memory_record_knowledge)
- User preferences (belongs in CLAUDE.md or soul/)
