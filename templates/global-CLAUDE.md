# Clawd-Lobster
# Added by the Clawd-Lobster installer. This is your file: edit or remove any part of it.

## Boot Protocol
At the start of a session, get your bearings before changing anything:
1. `memory_status()`: current workspace, machine and memory health
2. `memory_list(limit=5)`: the most recent records for this workspace
3. `memory_list_skills()`: learned patterns that may apply
4. When resuming earlier work: `memory_audit_search(limit=3)` for the last actions
5. If the workspace has `openspec/changes/*/tasks.md`, count `[x]` against `[ ]` to report spec progress
6. If a `.blitz-active` marker exists, a blitz run was interrupted: say so and resume it
7. Report ready in one line, for example "No active spec" or "Spec active: 4/10 tasks (40%)"

Skip these steps when the user says "continue".

## MCP Memory Server
Use the memory tools for every memory operation and never edit the `.db` files directly.
- **Write:** memory_store, memory_record_decision, memory_record_knowledge
- **Read:** memory_list, memory_get, memory_search
- **Learned skills:** memory_learn_skill, memory_list_skills, memory_improve_skill
- **Audit trail:** memory_log_action, memory_audit_search, memory_activity_log
- **Admin:** memory_status, memory_compact

Memory belongs to one workspace: do not read another workspace's memory.
- Learnings record mistakes to avoid: `memory_store(content, type="learning")`
- Learned skills record patterns to follow: `memory_learn_skill()`

After a complex task (three or more tool calls), check whether it produced a reusable pattern. Look for an existing skill with `memory_list_skills()`, then improve it with `memory_improve_skill()` or record a new one with `memory_learn_skill()`. Log significant steps with `memory_log_action` so the audit trail shows what was done.

## Safety
- Never commit secrets, API keys, tokens, passwords or connection strings.
- Keep personal data and machine details (real names, home directory paths, host names) out of files that are shared or pushed.
- Review the diff before every commit, and never force-push without the user's explicit approval.
- Ask before deploying to production or deleting data.

## Workspaces
Each workspace can describe itself in a `workspace.json` (type, stack and deploy settings). Rules for one project belong in that workspace's own `CLAUDE.md` and `.claude/rules/`, not in this file.
