# Tools & Skill Management

## MCP Memory Server (32 tools)

**Write:** memory_store, memory_record_decision, memory_record_resolved, memory_record_question, memory_record_knowledge
**Read:** memory_list, memory_get, memory_get_summary
**Delete:** memory_delete
**Search:** memory_search (cross-workspace, salience-weighted, ALL tables)
**Salience:** memory_reinforce
**Evolve:** memory_learn_skill, memory_list_skills, memory_improve_skill
**Trail:** memory_log_action, memory_audit_search, memory_audit_stats, memory_daily_report, memory_activity_log
**Admin:** memory_status, memory_compact, memory_oracle_summary

## Action Logging
Log significant actions using `memory_log_action`:
- Actions: TASK_START, SPEC, DELEGATE, REVIEW, REVIEW_OK, REVIEW_FIX, COMMIT, TASK_DONE
- All auto-tagged with `machine_id`
- View with `memory_audit_search` or `memory_activity_log`

## Skill Manager
```
python scripts/skill-manager.py list        # show all skills
python scripts/skill-manager.py enable <id> # enable a skill
python scripts/skill-manager.py reconcile   # regenerate configs from registry
```
