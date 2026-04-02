"""
Clawd-Lobster MCP Memory Server — unified memory interface for AI agents.

Tools (24):
  Write:    memory_store, memory_record_decision, memory_record_resolved,
            memory_record_question, memory_record_knowledge
  Read:     memory_list, memory_get, memory_get_summary
  Delete:   memory_delete
  Search:   memory_search (vector + text, salience-weighted, ALL tables)
  Salience: memory_reinforce (boost important memories)
  Evolve:   memory_learn_skill, memory_list_skills, memory_improve_skill
  Trail:    memory_log_action, memory_audit_search, memory_audit_stats,
            memory_daily_report, memory_activity_log
  Admin:    memory_compact, memory_status, memory_oracle_summary

Usage:
  python -m mcp_memory.server          # stdio (Claude Code)
  python -m mcp_memory.server --http   # HTTP (other clients)
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP

from .db import detect_workspace, get_sqlite, get_oracle, new_id, tags_to_json

# Security: max content length for write tools
_MAX_CONTENT_LEN = 50_000
# Security: max query results
_MAX_LIMIT = 100

mcp = FastMCP(
    "Clawd Memory",
    instructions=(
        "Unified memory system for all workspaces. "
        "Use memory_store for quick saves (auto-classifies type). "
        "Use memory_search for semantic search across all knowledge. "
        "Use memory_list to see recent items. "
        "Use memory_log_action to record task actions. "
        "Use memory_status for system overview."
    ),
)


def _get_machine_id() -> str:
    """Get machine ID for tagging records."""
    from .config import get_machine_id
    return get_machine_id()


# ============================================================
# WRITE TOOLS
# ============================================================

@mcp.tool()
def memory_store(content: str, type: str = "auto", tags: str = "", priority: int = 2) -> str:
    """Store a memory. Type: 'decision', 'resolved', 'question', 'knowledge', 'learning', or 'auto' (auto-detect).
    For decisions: content = 'what | why | how'. For questions: priority 1=high, 2=medium, 3=low.
    For learnings (mistakes, pitfalls, lessons): auto-tagged with 'learning'."""
    if type == "auto":
        cl = content.lower()
        if any(w in cl for w in ["decided", "chose", "decision", "will use", "going with"]):
            type = "decision"
        elif any(w in cl for w in ["fixed", "solved", "resolved", "the fix", "root cause"]):
            type = "resolved"
        elif any(w in cl for w in ["?", "should we", "how to", "what if", "need to figure"]):
            type = "question"
        elif any(w in cl for w in ["learned", "lesson", "mistake", "never again", "pitfall",
                                    "gotcha", "watch out", "踩坑", "教訓", "原來", "別再"]):
            type = "learning"
        else:
            type = "knowledge"

    if type == "decision":
        parts = [p.strip() for p in content.split("|")]
        what = parts[0]
        why = parts[1] if len(parts) > 1 else ""
        how = parts[2] if len(parts) > 2 else ""
        return memory_record_decision(what=what, why=why, how=how, tags=tags)
    elif type == "resolved":
        parts = [p.strip() for p in content.split("|")]
        what = parts[0]
        how = parts[1] if len(parts) > 1 else ""
        return memory_record_resolved(what=what, how=how, tags=tags)
    elif type == "question":
        return memory_record_question(question=content, tags=tags, priority=priority)
    elif type == "learning":
        # Learnings stored as knowledge_items with auto-tag "learning"
        learning_tags = "learning," + tags if tags else "learning"
        return memory_record_knowledge(title=content[:100], content=content, tags=learning_tags)
    else:
        return memory_record_knowledge(title=content[:100], content=content, tags=tags)


@mcp.tool()
def memory_record_decision(what: str, why: str = "", how: str = "", tags: str = "") -> str:
    """Record a decision made in this workspace."""
    if len(what) > _MAX_CONTENT_LEN:
        return f"Content too large (max {_MAX_CONTENT_LEN} chars)"
    conn = get_sqlite()
    try:
        rid = new_id()
        mid = _get_machine_id()
        conn.execute(
            "INSERT INTO decisions (id, date, what, why, how, tags, machine_id) VALUES (?, date('now'), ?, ?, ?, ?, ?)",
            (rid, what, why, how, tags_to_json(tags), mid),
        )
        conn.commit()
        return f"Decision recorded [{detect_workspace()}@{mid}]: {what[:60]} (id: {rid})"
    finally:
        conn.close()


@mcp.tool()
def memory_record_resolved(what: str, how: str = "", tags: str = "") -> str:
    """Record a resolved issue or problem."""
    if len(what) > _MAX_CONTENT_LEN:
        return f"Content too large (max {_MAX_CONTENT_LEN} chars)"
    conn = get_sqlite()
    try:
        rid = new_id()
        mid = _get_machine_id()
        conn.execute(
            "INSERT INTO resolved (id, what, how, tags, machine_id) VALUES (?, ?, ?, ?, ?)",
            (rid, what, how, tags_to_json(tags), mid),
        )
        conn.commit()
        return f"Resolved recorded [{detect_workspace()}@{mid}]: {what[:60]} (id: {rid})"
    finally:
        conn.close()


@mcp.tool()
def memory_record_question(question: str, context: str = "", tags: str = "", priority: int = 2) -> str:
    """Record an open question. Priority: 1=high, 2=medium, 3=low."""
    priority = max(1, min(priority, 3))
    conn = get_sqlite()
    try:
        rid = new_id()
        mid = _get_machine_id()
        conn.execute(
            "INSERT INTO open_questions (id, question, context, tags, priority, machine_id) VALUES (?, ?, ?, ?, ?, ?)",
            (rid, question, context, tags_to_json(tags), priority, mid),
        )
        conn.commit()
        return f"Question recorded [{detect_workspace()}@{mid}] P{priority}: {question[:60]} (id: {rid})"
    finally:
        conn.close()


@mcp.tool()
def memory_record_knowledge(title: str, content: str = "", tags: str = "") -> str:
    """Record a knowledge item. Use tags='learning' for lessons/pitfalls/mistakes."""
    if len(content) > _MAX_CONTENT_LEN:
        return f"Content too large (max {_MAX_CONTENT_LEN} chars)"
    conn = get_sqlite()
    try:
        rid = new_id()
        mid = _get_machine_id()
        conn.execute(
            "INSERT INTO knowledge_items (id, title, content, tags, written_to_obsidian, machine_id) VALUES (?, ?, ?, ?, 0, ?)",
            (rid, title, content, tags_to_json(tags), mid),
        )
        conn.commit()
        return f"Knowledge recorded [{detect_workspace()}@{mid}]: {title[:60]} (id: {rid})"
    finally:
        conn.close()


# ============================================================
# READ TOOLS
# ============================================================

@mcp.tool()
def memory_list(type: str = "all", workspace: str = "current", limit: int = 20) -> str:
    """List recent memories. Type: 'all', 'decisions', 'resolved', 'questions', 'knowledge', 'actions'."""
    limit = max(1, min(limit, _MAX_LIMIT))
    valid_types = ("all", "decisions", "resolved", "questions", "knowledge", "actions")
    if type not in valid_types:
        return f"Invalid type: {type}. Use one of: {', '.join(valid_types)}"
    ws = detect_workspace() if workspace == "current" else workspace
    conn = get_sqlite(ws)
    results = []

    tables = {
        "decisions": ("id, date, what, tags, status", "created_at"),
        "resolved": ("id, what, how, tags, date", "date"),
        "open_questions": ("id, question, priority, tags, raised", "raised"),
        "knowledge_items": ("id, title, tags, written_to_obsidian, created_at", "created_at"),
    }

    if type in ("all", "decisions"):
        rows = conn.execute(f"SELECT {tables['decisions'][0]} FROM decisions ORDER BY {tables['decisions'][1]} DESC LIMIT ?", (limit,)).fetchall()
        for r in rows:
            results.append(f"  [DEC] {r['id']} | {r['date']} | {r['what'][:70]} | {r['tags']}")

    if type in ("all", "resolved"):
        rows = conn.execute(f"SELECT {tables['resolved'][0]} FROM resolved ORDER BY {tables['resolved'][1]} DESC LIMIT ?", (limit,)).fetchall()
        for r in rows:
            results.append(f"  [RES] {r['id']} | {r['date']} | {r['what'][:70]}")

    if type in ("all", "questions"):
        rows = conn.execute(f"SELECT {tables['open_questions'][0]} FROM open_questions ORDER BY priority, {tables['open_questions'][1]} DESC LIMIT ?", (limit,)).fetchall()
        for r in rows:
            results.append(f"  [Q:P{r['priority']}] {r['id']} | {r['question'][:70]} | {r['raised']}")

    if type in ("all", "knowledge"):
        rows = conn.execute(f"SELECT {tables['knowledge_items'][0]} FROM knowledge_items ORDER BY {tables['knowledge_items'][1]} DESC LIMIT ?", (limit,)).fetchall()
        for r in rows:
            s = "synced" if r['written_to_obsidian'] else "pending"
            results.append(f"  [KNO] {r['id']} | {r['title'][:60]} | {s} | {r['created_at']}")

    if type in ("all", "actions"):
        try:
            rows = conn.execute(
                "SELECT id, timestamp, machine_id, action, target, note FROM action_log ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
            for r in rows:
                results.append(f"  [ACT] {r['id']} | {r['timestamp'][:16]} | {r['machine_id']} | {r['action']} | {r['target'][:40]}")
        except Exception:
            pass

    conn.close()
    if not results:
        return f"No memories found in [{ws}]"
    return f"[{ws}] {len(results)} memories:\n" + "\n".join(results)


@mcp.tool()
def memory_get(id: str, workspace: str = "current") -> str:
    """Get a specific memory by ID. Searches all tables. Auto-tracks access."""
    ws = detect_workspace() if workspace == "current" else workspace
    conn = get_sqlite(ws)
    try:
        for table in ["decisions", "resolved", "open_questions", "knowledge_items"]:
            row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (id,)).fetchone()
            if row:
                _touch_access(conn, table, id)
                conn.commit()
                return f"[{ws}/{table}] " + json.dumps(dict(row), ensure_ascii=False, default=str)
        # Also check action_log
        try:
            row = conn.execute("SELECT * FROM action_log WHERE id = ?", (id,)).fetchone()
            if row:
                return f"[{ws}/action_log] " + json.dumps(dict(row), ensure_ascii=False, default=str)
        except Exception:
            pass
        return f"Memory '{id}' not found in [{ws}]"
    finally:
        conn.close()


@mcp.tool()
def memory_get_summary(workspace: str = "current") -> str:
    """Get memory summary (counts) for a workspace."""
    ws = detect_workspace() if workspace == "current" else workspace
    conn = get_sqlite(ws)
    try:
        d = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        r = conn.execute("SELECT COUNT(*) FROM resolved").fetchone()[0]
        q = conn.execute("SELECT COUNT(*) FROM open_questions").fetchone()[0]
        k = conn.execute("SELECT COUNT(*) FROM knowledge_items").fetchone()[0]
        kp = conn.execute("SELECT COUNT(*) FROM knowledge_items WHERE written_to_obsidian=0").fetchone()[0]
        dl = conn.execute("SELECT COUNT(*) FROM daily_logs").fetchone()[0]
        al = 0
        try:
            al = conn.execute("SELECT COUNT(*) FROM action_log").fetchone()[0]
        except Exception:
            pass
    except Exception:
        return f"Error retrieving summary for [{ws}]. Database may need initialization."
    finally:
        conn.close()
    return (f"[{ws}] Decisions:{d} Resolved:{r} Questions:{q} "
            f"Knowledge:{k} (pending:{kp}) DailyLogs:{dl} Actions:{al}")


# ============================================================
# DELETE
# ============================================================

@mcp.tool()
def memory_delete(id: str, workspace: str = "current") -> str:
    """Delete a memory by ID. Searches all tables."""
    ws = detect_workspace() if workspace == "current" else workspace
    conn = get_sqlite(ws)
    try:
        for table in ["decisions", "resolved", "open_questions", "knowledge_items", "action_log"]:
            try:
                cur = conn.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
                if cur.rowcount > 0:
                    conn.commit()
                    return f"Deleted '{id}' from {table} [{ws}]"
            except Exception:
                continue
        return f"Memory '{id}' not found in [{ws}]"
    finally:
        conn.close()


# ============================================================
# TRAIL — Action Log (local SQLite, syncs to Oracle if available)
# ============================================================

@mcp.tool()
def memory_log_action(action: str, target: str = "", note: str = "", tokens: int = 0) -> str:
    """Log a task action. Actions: TASK_START, SPEC, DELEGATE, REVIEW, REVIEW_OK,
    REVIEW_FIX, COMMIT, TASK_DONE, or any custom action.
    All actions are tagged with machine_id for multi-machine audit trails."""
    conn = get_sqlite()
    ws = detect_workspace()
    mid = _get_machine_id()
    try:
        rid = new_id()
        conn.execute(
            "INSERT INTO action_log (id, machine_id, action, target, note, tokens, workspace) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (rid, mid, action, target, note, tokens, ws),
        )
        conn.commit()
        return f"Action logged [{ws}@{mid}]: {action} {target[:40]} (id: {rid})"
    finally:
        conn.close()


# ============================================================
# EVOLVE — Self-improving skill system
# ============================================================

@mcp.tool()
def memory_learn_skill(
    name: str, trigger: str, approach: str, tools_used: str = "",
    category: str = "general", source_task: str = "", workspace: str = "current"
) -> str:
    """Learn a new skill from a successful task pattern.
    Called automatically after completing complex multi-step tasks.
    - name: Short skill name (e.g. "debug-oracle-connection")
    - trigger: When to use this skill (e.g. "Oracle connection fails with TNS error")
    - approach: Step-by-step pattern that worked
    - tools_used: Comma-separated list of tools involved
    - category: Skill category (debug, refactor, deploy, analysis, workflow, etc.)
    - source_task: Brief description of the original task that created this skill"""
    ws = detect_workspace() if workspace == "current" else workspace
    if len(approach) > _MAX_CONTENT_LEN:
        return f"Approach too large (max {_MAX_CONTENT_LEN} chars)"
    conn = get_sqlite(ws)
    try:
        rid = new_id()
        conn.execute("""
            INSERT INTO learned_skills (id, name, trigger_condition, approach, tools_used,
                category, source_task, source_workspace, times_used, times_improved, effectiveness)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 1.0)
        """, (rid, name, trigger, approach, tools_used, category, source_task, ws))
        conn.commit()
    finally:
        conn.close()

    # Also save as a file for cross-session availability
    _save_skill_file(rid, name, trigger, approach, tools_used, category, source_task, ws)

    return (f"Skill learned [{ws}]: '{name}' (id: {rid})\n"
            f"  Trigger: {trigger[:80]}\n"
            f"  Category: {category}\n"
            f"  This skill will be available in future sessions.")


@mcp.tool()
def memory_list_skills(category: str = "all", workspace: str = "current") -> str:
    """List all learned skills. Filter by category. Shows usage stats and effectiveness."""
    ws = detect_workspace() if workspace == "current" else workspace
    conn = get_sqlite(ws)
    try:
        if category == "all":
            rows = conn.execute("""
                SELECT id, name, category, trigger_condition, times_used, times_improved,
                       effectiveness, created_at
                FROM learned_skills ORDER BY effectiveness DESC, times_used DESC
            """).fetchall()
        else:
            rows = conn.execute("""
                SELECT id, name, category, trigger_condition, times_used, times_improved,
                       effectiveness, created_at
                FROM learned_skills WHERE category = ? ORDER BY effectiveness DESC
            """, (category,)).fetchall()
    except Exception:
        return f"No learned_skills table in [{ws}]. Run init_db.py to create it."
    finally:
        conn.close()

    if not rows:
        return f"No learned skills in [{ws}]" + (f" (category: {category})" if category != "all" else "")

    lines = [f"[{ws}] {len(rows)} learned skills:"]
    for r in rows:
        eff = f"{r['effectiveness']:.1f}" if r['effectiveness'] else "1.0"
        lines.append(
            f"  [{r['category']}] {r['name']} | used:{r['times_used']}x "
            f"improved:{r['times_improved']}x | eff:{eff} | {r['id']}"
        )
        lines.append(f"    trigger: {r['trigger_condition'][:80]}")
    return "\n".join(lines)


@mcp.tool()
def memory_improve_skill(id: str, improvement: str, workspace: str = "current") -> str:
    """Improve an existing learned skill based on new experience.
    Called when using a skill and finding a better approach.
    - id: Skill ID
    - improvement: What changed and why (appended to approach)"""
    ws = detect_workspace() if workspace == "current" else workspace
    conn = get_sqlite(ws)
    try:
        row = conn.execute("SELECT * FROM learned_skills WHERE id = ?", (id,)).fetchone()
        if not row:
            conn.close()
            return f"Skill '{id}' not found in [{ws}]"

        # Append improvement to approach
        updated_approach = row["approach"] + f"\n\n## Improvement ({datetime.now().strftime('%Y-%m-%d')})\n{improvement}"
        conn.execute("""
            UPDATE learned_skills SET
                approach = ?,
                times_improved = COALESCE(times_improved, 0) + 1,
                effectiveness = MIN(COALESCE(effectiveness, 1.0) * 1.1, 3.0),
                last_used = datetime('now')
            WHERE id = ?
        """, (updated_approach, id))
        conn.commit()

        # Update the skill file too
        _save_skill_file(
            id, row["name"], row["trigger_condition"], updated_approach,
            row["tools_used"], row["category"], row["source_task"],
            row["source_workspace"]
        )

        new_eff = min((row["effectiveness"] or 1.0) * 1.1, 3.0)
        conn.close()
        return (f"Skill improved [{ws}]: '{row['name']}'\n"
                f"  Improvements: {row['times_improved'] + 1}x | Effectiveness: {new_eff:.1f}\n"
                f"  Change: {improvement[:100]}")
    except Exception:
        conn.close()
        return f"Error improving skill '{id}' in [{ws}]. Check database."


def _mark_skill_used(conn, skill_id: str):
    """Track skill usage (called internally when agent uses a skill)."""
    try:
        conn.execute("""
            UPDATE learned_skills SET
                times_used = COALESCE(times_used, 0) + 1,
                last_used = datetime('now'),
                effectiveness = MIN(COALESCE(effectiveness, 1.0) * 1.02, 3.0)
            WHERE id = ?
        """, (skill_id,))
    except Exception:
        pass


def _save_skill_file(rid, name, trigger, approach, tools_used, category, source_task, workspace):
    """Save skill as a markdown file for cross-session persistence."""
    from .config import load_config
    config = load_config()
    skill_dir = Path(config["wrapper_dir"]) / "skills" / "learned"
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Security: sanitize name to prevent path traversal
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '-', name.lower()).strip('-')
    if not safe_name:
        safe_name = rid
    filename = f"{safe_name}.md"
    content = f"""# {name}

## When to use
{trigger}

## Approach
{approach}

## Tools used
{tools_used or '(not specified)'}

## Metadata
- ID: {rid}
- Category: {category}
- Source workspace: {workspace}
- Source task: {source_task or '(not specified)'}
- Learned: {datetime.now().strftime('%Y-%m-%d')}
"""
    (skill_dir / filename).write_text(content, encoding="utf-8")


# ============================================================
# CJK-AWARE TOKEN ESTIMATION
# ============================================================

def estimate_tokens(text: str) -> int:
    """Estimate token count with CJK awareness."""
    if not text:
        return 0
    tokens = 0.0
    for ch in text:
        cp = ord(ch)
        if (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or
            0xF900 <= cp <= 0xFAFF or 0x3000 <= cp <= 0x303F or
            0x3040 <= cp <= 0x309F or 0x30A0 <= cp <= 0x30FF or
            0xAC00 <= cp <= 0xD7AF or 0xFF00 <= cp <= 0xFFEF):
            tokens += 1.5
        elif cp >= 0x1F600:
            tokens += 2.0
        else:
            tokens += 0.25
    return int(tokens + 0.5)


# ============================================================
# SALIENCE
# ============================================================

def _touch_access(conn, table: str, record_id: str):
    try:
        conn.execute(f"""
            UPDATE {table} SET
                access_count = COALESCE(access_count, 0) + 1,
                last_accessed = datetime('now'),
                salience = MIN(COALESCE(salience, 1.0) * 1.05, 2.0)
            WHERE id = ?
        """, (record_id,))
    except Exception:
        pass


@mcp.tool()
def memory_reinforce(id: str, workspace: str = "current") -> str:
    """Manually boost a memory's salience (+20%). Use when a memory proves especially valuable."""
    ws = detect_workspace() if workspace == "current" else workspace
    conn = get_sqlite(ws)
    for table in ["decisions", "resolved", "open_questions", "knowledge_items"]:
        row = conn.execute(f"SELECT id, salience, access_count FROM {table} WHERE id = ?", (id,)).fetchone()
        if row:
            new_salience = min((row["salience"] or 1.0) * 1.2, 2.0)
            conn.execute(f"""
                UPDATE {table} SET salience = ?, access_count = COALESCE(access_count, 0) + 1,
                    last_accessed = datetime('now') WHERE id = ?
            """, (new_salience, id))
            conn.commit()
            conn.close()
            return f"Reinforced '{id}' in {table} [{ws}]: salience {row['salience']:.2f} -> {new_salience:.2f}"
    conn.close()
    return f"Memory '{id}' not found in [{ws}]"


def run_decay(workspace_id: str = None, decay_factor: float = 0.95, stale_days: int = 30):
    """Run salience decay on stale memories. Called by scheduler."""
    ws = workspace_id or detect_workspace()
    conn = get_sqlite(ws)
    total = 0
    for table in ["decisions", "resolved", "open_questions", "knowledge_items"]:
        try:
            cur = conn.execute(f"""
                UPDATE {table} SET salience = COALESCE(salience, 1.0) * ?
                WHERE (last_accessed IS NULL AND created_at < datetime('now', '-{stale_days} days'))
                   OR (last_accessed < datetime('now', '-{stale_days} days'))
            """, (decay_factor,))
            total += cur.rowcount
        except Exception:
            pass
    conn.commit()
    conn.close()
    return total


# ============================================================
# SEARCH — searches ALL tables (not just knowledge_items)
# ============================================================

@mcp.tool()
def memory_search(query: str, domain: str = "all", limit: int = 10) -> str:
    """Search across ALL workspaces and ALL memory types (decisions, resolved, knowledge, questions).
    Uses Oracle vector search if available, falls back to local text search."""
    oracle = get_oracle()
    if oracle is None:
        return _local_text_search(query, limit)

    cur = oracle.cursor()
    embedding = _get_embedding(query)
    if embedding:
        return _vector_search(cur, embedding, domain, limit, oracle)

    sql = """
        SELECT k.id, k.title, k.tags, w.workspace_id, w.domain,
               COALESCE(k.salience, 1.0) as sal
        FROM KNOWLEDGE_ITEMS k JOIN WORKSPACES w ON k.workspace_id = w.workspace_id
        WHERE LOWER(k.title) LIKE :q OR LOWER(k.tags) LIKE :q OR LOWER(k.content) LIKE :q
    """
    params = {"q": f"%{query.lower()}%"}
    if domain != "all":
        sql += " AND w.domain = :domain"
        params["domain"] = domain
    sql += " ORDER BY sal DESC, k.created_at DESC FETCH FIRST :lim ROWS ONLY"
    params["lim"] = limit

    cur.execute(sql, params)
    rows = cur.fetchall()
    if not rows:
        return f"No results for '{query}'"
    lines = [f"Search '{query}' ({len(rows)} results):"]
    for r in rows:
        lines.append(f"  [{r[3]}|{r[4]}] {r[1][:55]} | sal={r[5]:.2f} | tags={r[2]}")
    return "\n".join(lines)


def _vector_search(cur, embedding, domain, limit, conn):
    import array
    vec = array.array('d', embedding)
    sql = """
        SELECT k.id, k.title, k.tags, w.workspace_id, w.domain,
               VECTOR_DISTANCE(k.embedding, :qvec, COSINE) AS distance
        FROM KNOWLEDGE_ITEMS k JOIN WORKSPACES w ON k.workspace_id = w.workspace_id
        WHERE k.embedding IS NOT NULL
    """
    params = {"qvec": vec}
    if domain != "all":
        sql += " AND w.domain = :domain"
        params["domain"] = domain
    sql += " ORDER BY distance FETCH FIRST :lim ROWS ONLY"
    params["lim"] = limit
    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        if not rows:
            return "No vector search results"
        lines = [f"Vector search ({len(rows)} results):"]
        for r in rows:
            lines.append(f"  [{r[3]}|{r[4]}] {r[1][:50]} | dist={r[5]:.4f} | tags={r[2]}")
        return "\n".join(lines)
    except Exception:
        return "Vector search unavailable. Check Oracle connection and embeddings."


def _get_embedding(text: str):
    from .config import load_config
    config = load_config()
    provider = config["embedding"]["provider"]
    if provider == "openai" and config["embedding"]["api_key"]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config["embedding"]["api_key"])
            resp = client.embeddings.create(model=config["embedding"]["model"], input=text)
            return resp.data[0].embedding
        except Exception:
            return None
    return None


def _local_text_search(query: str, limit: int) -> str:
    """Search ALL tables across ALL workspaces. Opens connections lazily, closes immediately."""
    from .config import load_config, get_workspace_map_path
    config = load_config()
    results = []
    q = f"%{query.lower()}%"

    try:
        with open(get_workspace_map_path()) as f:
            registry = json.load(f)
        workspaces = registry.get("workspaces", [])
        if isinstance(workspaces, list):
            ws_ids = [w.get("id") for w in workspaces]
        else:
            ws_ids = list(workspaces.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        # No registry — search current workspace only
        ws_ids = [detect_workspace()]

    for ws_id in ws_ids:
        try:
            conn = get_sqlite(ws_id)
        except (FileNotFoundError, ValueError):
            continue
        try:
            # Search knowledge_items
            rows = conn.execute(
                """SELECT id, title, tags, COALESCE(salience, 1.0) as sal
                   FROM knowledge_items
                   WHERE LOWER(title) LIKE ? OR LOWER(content) LIKE ?
                   ORDER BY sal DESC LIMIT ?""",
                (q, q, limit),
            ).fetchall()
            for r in rows:
                _touch_access(conn, "knowledge_items", r["id"])
                results.append((r["sal"], f"  [{ws_id}] [KNO] {r['id']} | {r['title'][:55]} | sal={r['sal']:.2f} | {r['tags']}"))

            # Search decisions
            rows = conn.execute(
                """SELECT id, what, tags, COALESCE(salience, 1.0) as sal
                   FROM decisions
                   WHERE LOWER(what) LIKE ? OR LOWER(why) LIKE ? OR LOWER(how) LIKE ?
                   ORDER BY sal DESC LIMIT ?""",
                (q, q, q, limit),
            ).fetchall()
            for r in rows:
                _touch_access(conn, "decisions", r["id"])
                results.append((r["sal"], f"  [{ws_id}] [DEC] {r['id']} | {r['what'][:55]} | sal={r['sal']:.2f} | {r['tags']}"))

            # Search resolved
            rows = conn.execute(
                """SELECT id, what, tags, COALESCE(salience, 1.0) as sal
                   FROM resolved
                   WHERE LOWER(what) LIKE ? OR LOWER(how) LIKE ?
                   ORDER BY sal DESC LIMIT ?""",
                (q, q, limit),
            ).fetchall()
            for r in rows:
                _touch_access(conn, "resolved", r["id"])
                results.append((r["sal"], f"  [{ws_id}] [RES] {r['id']} | {r['what'][:55]} | sal={r['sal']:.2f} | {r['tags']}"))

            # Search open_questions
            rows = conn.execute(
                """SELECT id, question, tags, COALESCE(salience, 1.0) as sal
                   FROM open_questions
                   WHERE LOWER(question) LIKE ? OR LOWER(context) LIKE ?
                   ORDER BY sal DESC LIMIT ?""",
                (q, q, limit),
            ).fetchall()
            for r in rows:
                _touch_access(conn, "open_questions", r["id"])
                results.append((r["sal"], f"  [{ws_id}] [Q] {r['id']} | {r['question'][:55]} | sal={r['sal']:.2f} | {r['tags']}"))

            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()

    if not results:
        return f"No local results for '{query}'"
    results.sort(key=lambda x: x[0], reverse=True)
    return f"Local search '{query}' ({len(results)} results):\n" + "\n".join(r[1] for r in results[:limit])


# ============================================================
# TRAIL / AUDIT TOOLS — SQLite-first, Oracle as sync target
# ============================================================

@mcp.tool()
def memory_audit_search(query: str = "", date: str = "", action: str = "",
                        machine: str = "", workspace: str = "all", limit: int = 20) -> str:
    """Search audit trail (action_log). Filter by keyword, date, action type, machine ID.
    Searches local SQLite first. If Oracle L4 is connected, also searches cloud."""
    limit = max(1, min(limit, _MAX_LIMIT))
    results = []

    # Local SQLite search
    results.extend(_local_audit_search(query, date, action, machine, workspace, limit))

    # Oracle L4 search (if available, for cross-workspace data)
    oracle = get_oracle()
    if oracle:
        try:
            results.extend(_oracle_audit_search(oracle, query, date, action, machine, workspace, limit))
        except Exception:
            pass

    if not results:
        return "No audit entries found"
    # Deduplicate by ID, sort by timestamp
    seen = set()
    unique = []
    for r in results:
        if r[0] not in seen:
            seen.add(r[0])
            unique.append(r)
    unique.sort(key=lambda x: x[1], reverse=True)
    lines = [f"Audit trail ({len(unique)} entries):"]
    for r in unique[:limit]:
        lines.append(r[2])
    return "\n".join(lines)


def _local_audit_search(query, date, action, machine, workspace, limit):
    """Search action_log in local SQLite."""
    from .config import load_config, get_workspace_map_path
    results = []

    try:
        with open(get_workspace_map_path()) as f:
            registry = json.load(f)
        ws_list = registry.get("workspaces", [])
        ws_ids = [w.get("id") for w in ws_list] if isinstance(ws_list, list) else list(ws_list.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        ws_ids = [detect_workspace()]

    if workspace != "all":
        ws_ids = [workspace] if workspace in ws_ids else []

    for ws_id in ws_ids:
        try:
            conn = get_sqlite(ws_id)
        except (FileNotFoundError, ValueError):
            continue
        try:
            conditions, params = [], []
            if query:
                conditions.append("(LOWER(action) LIKE ? OR LOWER(target) LIKE ? OR LOWER(note) LIKE ?)")
                params.extend([f"%{query.lower()}%"] * 3)
            if date:
                conditions.append("timestamp LIKE ?")
                params.append(f"{date}%")
            if action:
                conditions.append("LOWER(action) LIKE ?")
                params.append(f"%{action.lower()}%")
            if machine:
                conditions.append("LOWER(machine_id) LIKE ?")
                params.append(f"%{machine.lower()}%")

            where = "WHERE " + " AND ".join(conditions) if conditions else ""
            rows = conn.execute(
                f"SELECT id, timestamp, machine_id, action, target, note, workspace FROM action_log {where} ORDER BY timestamp DESC LIMIT ?",
                params + [limit],
            ).fetchall()
            for r in rows:
                rid = r["id"]
                ts = r["timestamp"][:16] if r["timestamp"] else "?"
                line = f"  {ts} | {r['machine_id']:15s} | {r['action']:15s} | {(r['target'] or '')[:40]} | [{ws_id}]"
                results.append((rid, r["timestamp"] or "", line))
        except Exception:
            pass
        finally:
            conn.close()

    return results


def _oracle_audit_search(oracle, query, date, action, machine, workspace, limit):
    """Search AUDIT_LOG in Oracle L4."""
    cur = oracle.cursor()
    conditions, params = [], {}
    if query:
        conditions.append("(LOWER(a.subject) LIKE :q OR LOWER(a.what) LIKE :q OR LOWER(a.keywords) LIKE :q)")
        params["q"] = f"%{query.lower()}%"
    if date:
        conditions.append("a.ts LIKE :dt")
        params["dt"] = f"{date}%"
    if machine:
        conditions.append("LOWER(a.machine_id) LIKE :mid")
        params["mid"] = f"%{machine.lower()}%"
    if workspace != "all":
        conditions.append("a.workspace_id = :ws")
        params["ws"] = workspace

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"SELECT a.ts, a.folder, a.direction, a.from_name, a.subject, a.importance, a.category, a.is_suspicious, a.workspace_id FROM AUDIT_LOG a {where} ORDER BY a.ts DESC FETCH FIRST :lim ROWS ONLY"
    params["lim"] = limit
    cur.execute(sql, params)
    rows = cur.fetchall()
    results = []
    for r in rows:
        flag = " [!SUSPICIOUS]" if r[7] else ""
        rid = f"oracle-{r[0][:16]}"
        line = f"  {r[0][:16]} | {'L4':15s} | {r[5] or '-':15s} | {(r[4] or '')[:40]}{flag}"
        results.append((rid, str(r[0]), line))
    return results


@mcp.tool()
def memory_audit_stats(date: str = "", workspace: str = "all") -> str:
    """Audit trail statistics — local action counts + Oracle stats if available."""
    lines = []

    # Local stats from SQLite action_log
    from .config import get_workspace_map_path
    total_local = 0
    action_counts = {}
    machine_counts = {}

    try:
        with open(get_workspace_map_path()) as f:
            registry = json.load(f)
        ws_list = registry.get("workspaces", [])
        ws_ids = [w.get("id") for w in ws_list] if isinstance(ws_list, list) else list(ws_list.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        ws_ids = [detect_workspace()]

    for ws_id in ws_ids:
        if workspace != "all" and ws_id != workspace:
            continue
        try:
            conn = get_sqlite(ws_id)
            date_filter = f" WHERE timestamp LIKE '{date}%'" if date else ""
            rows = conn.execute(f"SELECT action, machine_id, COUNT(*) as cnt FROM action_log{date_filter} GROUP BY action, machine_id").fetchall()
            for r in rows:
                action_counts[r["action"]] = action_counts.get(r["action"], 0) + r["cnt"]
                machine_counts[r["machine_id"]] = machine_counts.get(r["machine_id"], 0) + r["cnt"]
                total_local += r["cnt"]
            conn.close()
        except Exception:
            pass

    lines.append(f"Local action log: {total_local} entries")
    if action_counts:
        lines.append("\nBy action:")
        for a, c in sorted(action_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {a}: {c}")
    if machine_counts:
        lines.append("\nBy machine:")
        for m, c in sorted(machine_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {m}: {c}")

    # Oracle stats (if available)
    oracle = get_oracle()
    if oracle:
        try:
            cur = oracle.cursor()
            cur.execute("SELECT COUNT(*) FROM AUDIT_LOG")
            lines.append(f"\nOracle L4: {cur.fetchone()[0]} audit entries")
        except Exception:
            pass

    return "\n".join(lines)


@mcp.tool()
def memory_daily_report(date: str = "", workspace: str = "all", limit: int = 7) -> str:
    """Get daily reports. Shows action summaries from local data + Oracle if available."""
    lines = []

    # Local daily summary from action_log
    from .config import get_workspace_map_path
    try:
        with open(get_workspace_map_path()) as f:
            registry = json.load(f)
        ws_list = registry.get("workspaces", [])
        ws_ids = [w.get("id") for w in ws_list] if isinstance(ws_list, list) else list(ws_list.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        ws_ids = [detect_workspace()]

    day_data = {}
    for ws_id in ws_ids:
        if workspace != "all" and ws_id != workspace:
            continue
        try:
            conn = get_sqlite(ws_id)
            rows = conn.execute(
                """SELECT DATE(timestamp) as day, COUNT(*) as cnt, SUM(tokens) as tok,
                          GROUP_CONCAT(DISTINCT machine_id) as machines
                   FROM action_log GROUP BY DATE(timestamp) ORDER BY day DESC LIMIT ?""",
                (limit,),
            ).fetchall()
            for r in rows:
                day = r["day"]
                if day not in day_data:
                    day_data[day] = {"actions": 0, "tokens": 0, "machines": set(), "workspaces": set()}
                day_data[day]["actions"] += r["cnt"]
                day_data[day]["tokens"] += r["tok"] or 0
                if r["machines"]:
                    day_data[day]["machines"].update(r["machines"].split(","))
                day_data[day]["workspaces"].add(ws_id)
            conn.close()
        except Exception:
            pass

    if day_data:
        lines.append(f"Daily Reports (local, {len(day_data)} days):")
        for day in sorted(day_data.keys(), reverse=True)[:limit]:
            d = day_data[day]
            machines = ", ".join(d["machines"]) if d["machines"] else "?"
            lines.append(f"  {day} | actions:{d['actions']} | tokens:{d['tokens']} | machines:{machines} | ws:{len(d['workspaces'])}")
    else:
        lines.append("No local daily data found")

    # Oracle daily reports (if available)
    oracle = get_oracle()
    if oracle:
        try:
            cur = oracle.cursor()
            if date:
                sql = "SELECT workspace_id, report_date, day_of_week, email_count, inbox_count, sent_count, calendar_count, h_count, m_count, l_count, suspicious_count, top_senders, h_subjects, narrative FROM DAILY_REPORTS WHERE report_date = TO_DATE(:dt, 'YYYY-MM-DD')"
                params = {"dt": date}
            else:
                sql = "SELECT workspace_id, report_date, day_of_week, email_count, inbox_count, sent_count, calendar_count, h_count, m_count, l_count, suspicious_count, top_senders, h_subjects, narrative FROM DAILY_REPORTS ORDER BY report_date DESC FETCH FIRST :lim ROWS ONLY"
                params = {"lim": limit}
            cur.execute(sql, params)
            rows = cur.fetchall()
            if rows:
                lines.append(f"\nOracle L4 Reports ({len(rows)} entries):")
                for r in rows:
                    lines.append(f"  {str(r[1])[:10]} ({r[2] or '?'}) [{r[0]}] | email:{r[3]} cal:{r[6]} | H:{r[7]} M:{r[8]} L:{r[9]}")
        except Exception:
            pass

    return "\n".join(lines) if lines else "No daily reports found"


@mcp.tool()
def memory_activity_log(agent: str = "", action: str = "", workspace: str = "all", limit: int = 20) -> str:
    """View agent activity log. Searches local SQLite first, Oracle L4 if available.
    Filter by agent/machine, action, workspace."""
    limit = max(1, min(limit, _MAX_LIMIT))

    # Local search
    results = _local_audit_search(
        query="", date="", action=action, machine=agent, workspace=workspace, limit=limit
    )

    # Oracle search (if available)
    oracle = get_oracle()
    if oracle:
        try:
            cur = oracle.cursor()
            conditions, params = [], {}
            if agent:
                conditions.append("LOWER(a.agent) LIKE :ag")
                params["ag"] = f"%{agent.lower()}%"
            if action:
                conditions.append("LOWER(a.action) LIKE :act")
                params["act"] = f"%{action.lower()}%"
            if workspace != "all":
                conditions.append("a.workspace_id = :ws")
                params["ws"] = workspace
            where = "WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT a.logged_at, a.log_type, a.agent, a.action, a.task_type, a.target, a.result_status, a.workspace_id FROM ACTIVITY_LOG a {where} ORDER BY a.logged_at DESC FETCH FIRST :lim ROWS ONLY"
            params["lim"] = limit
            cur.execute(sql, params)
            rows = cur.fetchall()
            for r in rows:
                ts = str(r[0])[:16] if r[0] else "?"
                rid = f"oracle-{ts}"
                line = f"  {ts} | {r[2] or '?':15s} | {r[3] or r[4] or '?':15s} | {(r[5] or '')[:40]}"
                results.append((rid, str(r[0] or ""), line))
        except Exception:
            pass

    if not results:
        return "No activity log entries found"

    # Deduplicate and sort
    seen = set()
    unique = []
    for r in results:
        if r[0] not in seen:
            seen.add(r[0])
            unique.append(r)
    unique.sort(key=lambda x: x[1], reverse=True)

    lines = [f"Activity log ({len(unique)} entries):"]
    for r in unique[:limit]:
        lines.append(r[2])
    return "\n".join(lines)


# ============================================================
# ADMIN
# ============================================================

@mcp.tool()
def memory_status() -> str:
    """System status: local counts, machine info, Oracle sync status."""
    from .config import load_config
    config = load_config()
    mid = _get_machine_id()
    lines = [f"Clawd-Lobster Memory Server v0.3.0",
             f"Workspace: {detect_workspace()}",
             f"Machine: {mid}"]
    try:
        lines.append(f"Local: {memory_get_summary()}")
    except Exception as e:
        lines.append(f"Local: error - {e}")
    oracle = get_oracle()
    if oracle:
        cur = oracle.cursor()
        cur.execute("SELECT COUNT(*) FROM WORKSPACES WHERE is_active = 1")
        ws_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM KNOWLEDGE_ITEMS")
        ki_count = cur.fetchone()[0]
        lines.append(f"Oracle L4: {ws_count} workspaces, {ki_count} knowledge items")
    else:
        lines.append(f"L4: {config['l4_provider']} (Oracle not connected)")
    lines.append(f"Embeddings: {config['embedding']['provider']}")
    return "\n".join(lines)


@mcp.tool()
def memory_compact(workspace: str = "current") -> str:
    """Check memory database health and recommend actions if needed.
    Reports: DB size, table row counts, salience distribution, stale items."""
    ws = detect_workspace() if workspace == "current" else workspace
    from .config import load_config, get_workspace_map_path
    config = load_config()

    # Find memory.db
    ws_root = Path(config["workspace_root"])
    try:
        with open(get_workspace_map_path()) as f:
            registry = json.load(f)
        workspaces = registry.get("workspaces", [])
        display_path = None
        if isinstance(workspaces, list):
            for w in workspaces:
                if w.get("id") == ws:
                    display_path = w.get("path", ws)
                    break
        elif isinstance(workspaces, dict):
            display_path = workspaces.get(ws)
        if display_path:
            db_path = ws_root / display_path / ".claude-memory" / "memory.db"
        else:
            db_path = ws_root / ws / ".claude-memory" / "memory.db"
    except (FileNotFoundError, json.JSONDecodeError):
        db_path = ws_root / ws / ".claude-memory" / "memory.db"

    if not db_path.exists():
        return f"No memory.db found for [{ws}]. Run init_db.py to create it."

    # DB file size
    db_size_kb = db_path.stat().st_size / 1024
    db_size_str = f"{db_size_kb:.0f} KB" if db_size_kb < 1024 else f"{db_size_kb/1024:.1f} MB"

    conn = get_sqlite(ws)
    lines = [f"[{ws}] Memory DB Health:"]
    lines.append(f"  File: {db_path}")
    lines.append(f"  Size: {db_size_str}")

    # Row counts
    total_rows = 0
    for table in ["decisions", "resolved", "open_questions", "knowledge_items", "learned_skills"]:
        try:
            cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            lines.append(f"  {table}: {cnt} rows")
            total_rows += cnt
        except Exception:
            pass
    try:
        al_cnt = conn.execute("SELECT COUNT(*) FROM action_log").fetchone()[0]
        lines.append(f"  action_log: {al_cnt} rows")
        total_rows += al_cnt
    except Exception:
        pass

    # Stale items (salience < 0.5)
    stale = 0
    for table in ["decisions", "resolved", "open_questions", "knowledge_items"]:
        try:
            cnt = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE salience < 0.5").fetchone()[0]
            stale += cnt
        except Exception:
            pass

    lines.append(f"  Total: {total_rows} rows | Stale (sal<0.5): {stale}")

    # Recommendations
    if db_size_kb > 10240:
        lines.append("  -> COMPACT RECOMMENDED: DB > 10MB. Consider archiving old entries.")
    elif stale > 50:
        lines.append(f"  -> {stale} stale items. Consider reviewing or deleting low-salience entries.")
    else:
        lines.append("  -> OK: No compaction needed.")

    conn.close()
    return "\n".join(lines)


@mcp.tool()
def memory_oracle_summary() -> str:
    """Cross-workspace summary from Oracle L4."""
    oracle = get_oracle()
    if oracle is None:
        return "Oracle L4 not connected"
    cur = oracle.cursor()
    cur.execute("""
        SELECT w.workspace_id, w.domain,
            (SELECT COUNT(*) FROM DECISIONS d WHERE d.workspace_id = w.workspace_id),
            (SELECT COUNT(*) FROM RESOLVED r WHERE r.workspace_id = w.workspace_id),
            (SELECT COUNT(*) FROM OPEN_QUESTIONS q WHERE q.workspace_id = w.workspace_id),
            (SELECT COUNT(*) FROM KNOWLEDGE_ITEMS k WHERE k.workspace_id = w.workspace_id)
        FROM WORKSPACES w WHERE w.is_active = 1 ORDER BY w.domain, w.workspace_id
    """)
    rows = cur.fetchall()
    lines = [f"{'Workspace':<35} {'Domain':<10} {'Dec':>4} {'Res':>4} {'Q':>4} {'Know':>5}"]
    lines.append("-" * 70)
    for r in rows:
        lines.append(f"{r[0]:<35} {r[1]:<10} {r[2]:>4} {r[3]:>4} {r[4]:>4} {r[5]:>5}")
    return "\n".join(lines)


# ============================================================
# Entry point
# ============================================================

def main():
    if "--decay" in sys.argv:
        from .config import load_config, get_workspace_map_path
        try:
            with open(get_workspace_map_path()) as f:
                registry = json.load(f)
            workspaces = registry.get("workspaces", [])
            ws_ids = [w.get("id") for w in workspaces] if isinstance(workspaces, list) else list(workspaces.keys())
            total = 0
            for ws_id in ws_ids:
                try:
                    n = run_decay(ws_id)
                    if n:
                        print(f"  [{ws_id}] decayed {n} items")
                    total += n
                except Exception:
                    pass
            print(f"Decay complete: {total} items decayed")
        except Exception as e:
            print(f"Decay error: {e}")
    elif "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8787)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
