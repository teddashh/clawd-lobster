# Self-Evolution Rules

## When to Learn a Skill
After completing complex multi-step tasks (3+ tool calls), evaluate:
- Was a non-trivial task completed successfully?
- Is the approach a reusable pattern for future tasks?
- Does no existing skill already cover this?

If yes: call `memory_learn_skill` with name, trigger, approach, tools, category.

## When to Use Learned Skills
- Before starting a task: `memory_list_skills()` for relevant patterns
- If a matching skill exists: follow its approach
- If you modified the approach: `memory_improve_skill()` to update

## Skill Effectiveness
- Each use: +2%, each improvement: +10% (cap 3.0x)
- Skills > 2.0 effectiveness = proven patterns — trust them
- Skills unused 90+ days = possibly stale — verify first
