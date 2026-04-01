"""
Clawd-Lobster MCP Memory Server — unified memory interface for AI agents.

Tools (21):
  Write:    memory_store, memory_record_decision, memory_record_resolved,
            memory_record_question, memory_record_knowledge
  Read:     memory_list, memory_get, memory_get_summary
  Delete:   memory_delete
  Search:   memory_search (vector + text, salience-weighted)
  Salience: memory_reinforce (boost important memories)
  Evolve:   memory_learn_skill, memory_list_skills, memory_improve_skill
  Trail:    memory_audit_search, memory_audit_stats, memory_daily_report,
            memory_activity_log
  Admin:    memory_compact, memory_status, memory_oracle_summary

Usage:
  python -m mcp_memory.server          # stdio (Claude Code)
  python -m mcp_memory.server --http   # HTTP (other clients)
"""
import json
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
        "Use memory_status for system overview."
    ),
)


# ============================================================
# WRITE TOOLS
# ============================================================

@mcp.tool()
def memory_store(content: str, type: str = "auto", tags: str = "", priority: int = 2) -> str:
    """Store a memory. Type: 'decision', 'resolved', 'question', 'knowledge', or 'auto' (auto-detect).
    For decisions: content = 'what | why | how'. For questions: priority 1=high, 2=medium, 3=low."""
    if type == "auto":
        cl = content.lower()
        if any(w in cl for w in ["decided", "chose", "decision", "will use", "going with"]):
            type = "decision"
        elif any(w in cl for w in ["fixed", "solved", "resolved", "the fix", "root cause"]):
            type = "resolved"
        elif any(w in cl for w in ["?", "should we", "how to", "what if", "need to figure"]):
            type = "question"
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
        conn.execute(
            "INSERT INTO decisions (id, date, what, why, how, tags) VALUES (?, date('now'), ?, ?, ?, ?)",
            (rid, what, why, how, tags_to_json(tags)),
        )
        conn.commit()
        return f"Decision recorded [{detect_workspace()}]: {what[:60]} (id: {rid})"
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
        conn.execute(
            "INSERT INTO resolved (id, what, how, tags) VALUES (?, ?, ?, ?)",
            (rid, what, how, tags_to_json(tags)),
        )
        conn.commit()
        return f"Resolved recorded [{detect_workspace()}]: {what[:60]} (id: {rid})"
    finally:
        conn.close()


@mcp.tool()
def memory_record_question(question: str, context: str = "", tags: str = "", priority: int = 2) -> str:
    """Record an open question. Priority: 1=high, 2=medium, 3=low."""
    priority = max(1, min(priority, 3))
    conn = get_sqlite()
    try:
        rid = new_id()
        conn.execute(
            "INSERT INTO open_questions (id, question, context, tags, priority) VALUES (?, ?, ?, ?, ?)",
            (rid, question, context, tags_to_json(tags), priority),
        )
        conn.commit()
        return f"Question recorded [{detect_workspace()}] P{priority}: {question[:60]} (id: {rid})"
    finally:
        conn.close()


@mcp.tool()
def memory_record_knowledge(title: str, content: str = "", tags: str = "") -> str:
    """Record a knowledge item."""
    if len(content) > _MAX_CONTENT_LEN:
        return f"Content too large (max {_MAX_CONTENT_LEN} chars)"
    conn = get_sqlite()
    try:
        rid = new_id()
        conn.execute(
            "INSERT INTO knowledge_items (id, title, content, tags, written_to_obsidian) VALUES (?, ?, ?, ?, 0)",
            (rid, title, content, tags_to_json(tags)),
        )
        conn.commit()
        return f"Knowledge recorded [{detect_workspace()}]: {title[:60]} (id: {rid})"
    finally:
        conn.close()


# ============================================================
# READ TOOLS
# ============================================================

@mcp.tool()
def memory_list(type: str = "all", workspace: str = "current", limit: int = 20) -> str:
    """List recent memories. Type: 'all', 'decisions', 'resolved', 'questions', 'knowledge'."""
    limit = max(1, min(limit, _MAX_LIMIT))
    valid_types = ("all", "decisions", "resolved", "questions", "knowledge")
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
    except Exception:
        return f"Error retrieving summary for [{ws}]. Database may need initialization."
    finally:
        conn.close()
    return (f"[{ws}] Decisions:{d} Resolved:{r} Questions:{q} "
            f"Knowledge:{k} (pending:{kp}) DailyLogs:{dl}")


# ============================================================
# DELETE
# ============================================================

@mcp.tool()
def memory_delete(id: str, workspace: str = "current") -> str:
    """Delete a memory by ID. Searches all tables."""
    ws = detect_workspace() if workspace == "current" else workspace
    conn = get_sqlite(ws)
    try:
        for table in ["decisions", "resolved", "open_questions", "knowledge_items"]:
            cur = conn.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
            if cur.rowcount > 0:
                conn.commit()
                return f"Deleted '{id}' from {table} [{ws}]"
        return f"Memory '{id}' not found in [{ws}]"
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
# SEARCH
# ============================================================

@mcp.tool()
def memory_search(query: str, domain: str = "all", limit: int = 10) -> str:
    """Semantic search across ALL workspaces. Falls back to text search if vector not available."""
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
    from .config import load_config, get_workspace_map_path
    config = load_config()
    results = []

    try:
        with open(get_workspace_map_path()) as f:
            registry = json.load(f)
        workspaces = registry.get("workspaces", [])
        if isinstance(workspaces, list):
            ws_ids = [w.get("id") for w in workspaces]
        else:
            ws_ids = list(workspaces.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        return "No workspace registry found"

    for ws_id in ws_ids:
        try:
            conn = get_sqlite(ws_id)
            rows = conn.execute(
                """SELECT id, title, tags, COALESCE(salience, 1.0) as sal
                   FROM knowledge_items
                   WHERE LOWER(title) LIKE ? OR LOWER(content) LIKE ?
                   ORDER BY sal DESC LIMIT ?""",
                (f"%{query.lower()}%", f"%{query.lower()}%", limit),
            ).fetchall()
            for r in rows:
                _touch_access(conn, "knowledge_items", r["id"])
                results.append((r["sal"], f"  [{ws_id}] {r['id']} | {r['title'][:60]} | sal={r['sal']:.2f} | {r['tags']}"))
            conn.commit()
            conn.close()
        except Exception:
            continue

    if not results:
        return f"No local results for '{query}'"
    results.sort(key=lambda x: x[0], reverse=True)
    return f"Local search '{query}' ({len(results)} results):\n" + "\n".join(r[1] for r in results[:limit])


# ============================================================
# TRAIL / AUDIT TOOLS
# ============================================================

@mcp.tool()
def memory_audit_search(query: str = "", date: str = "", sender: str = "",
                        importance: str = "", workspace: str = "all", limit: int = 20) -> str:
    """Search audit trail. Filter by keyword, date, sender, importance (H/M/L)."""
    oracle = get_oracle()
    if oracle is None:
        return "Audit trail requires Oracle L4 connection"

    cur = oracle.cursor()
    conditions, params = [], {}
    if query:
        conditions.append("(LOWER(a.subject) LIKE :q OR LOWER(a.what) LIKE :q OR LOWER(a.keywords) LIKE :q)")
        params["q"] = f"%{query.lower()}%"
    if date:
        conditions.append("a.ts LIKE :dt")
        params["dt"] = f"{date}%"
    if sender:
        conditions.append("(LOWER(a.from_name) LIKE :snd OR LOWER(a.from_addr) LIKE :snd)")
        params["snd"] = f"%{sender.lower()}%"
    if importance:
        conditions.append("a.importance = :imp")
        params["imp"] = importance.upper()[:1]
    if workspace != "all":
        conditions.append("a.workspace_id = :ws")
        params["ws"] = workspace

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"SELECT a.ts, a.folder, a.direction, a.from_name, a.subject, a.importance, a.category, a.is_suspicious, a.workspace_id FROM AUDIT_LOG a {where} ORDER BY a.ts DESC FETCH FIRST :lim ROWS ONLY"
    params["lim"] = limit
    cur.execute(sql, params)
    rows = cur.fetchall()
    if not rows:
        return "No audit entries found"
    lines = [f"Audit trail ({len(rows)} entries):"]
    for r in rows:
        flag = " [!SUSPICIOUS]" if r[7] else ""
        lines.append(f"  {r[0][:16]} | {r[5] or '-'} | {r[3][:25]:25s} | {(r[4] or '')[:50]}{flag}")
    return "\n".join(lines)


@mcp.tool()
def memory_audit_stats(date: str = "", workspace: str = "all") -> str:
    """Audit trail statistics by importance, direction, category."""
    oracle = get_oracle()
    if oracle is None:
        return "Audit stats require Oracle L4 connection"
    cur = oracle.cursor()
    conditions, params = [], {}
    if date:
        conditions.append("a.ts LIKE :dt")
        params["dt"] = f"{date}%"
    if workspace != "all":
        conditions.append("a.workspace_id = :ws")
        params["ws"] = workspace
    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    lines = []
    cur.execute(f"SELECT COUNT(*) FROM AUDIT_LOG a {where}", params)
    lines.append(f"Audit trail: {cur.fetchone()[0]} total entries")
    cur.execute(f"SELECT importance, COUNT(*) FROM AUDIT_LOG a {where} GROUP BY importance ORDER BY importance", params)
    lines.append("\nBy importance:")
    for r in cur.fetchall():
        label = {"H": "High", "M": "Medium", "L": "Low"}.get(r[0], r[0] or "?")
        lines.append(f"  {label}: {r[1]}")
    cur.execute(f"SELECT direction, COUNT(*) FROM AUDIT_LOG a {where} GROUP BY direction", params)
    lines.append("\nBy direction:")
    for r in cur.fetchall():
        lines.append(f"  {r[0] or '?'}: {r[1]}")
    return "\n".join(lines)


@mcp.tool()
def memory_daily_report(date: str = "", workspace: str = "all", limit: int = 7) -> str:
    """Get daily reports. Shows email counts, calendar, priorities, summary."""
    oracle = get_oracle()
    if oracle is None:
        return "Daily reports require Oracle L4 connection"
    cur = oracle.cursor()
    if date:
        sql = "SELECT workspace_id, report_date, day_of_week, email_count, inbox_count, sent_count, calendar_count, h_count, m_count, l_count, suspicious_count, top_senders, h_subjects, narrative FROM DAILY_REPORTS WHERE report_date = TO_DATE(:dt, 'YYYY-MM-DD')"
        params = {"dt": date}
        if workspace != "all":
            sql += " AND workspace_id = :ws"
            params["ws"] = workspace
        sql += " ORDER BY workspace_id"
    else:
        sql = "SELECT workspace_id, report_date, day_of_week, email_count, inbox_count, sent_count, calendar_count, h_count, m_count, l_count, suspicious_count, top_senders, h_subjects, narrative FROM DAILY_REPORTS"
        params = {}
        if workspace != "all":
            sql += " WHERE workspace_id = :ws"
            params["ws"] = workspace
        sql += " ORDER BY report_date DESC FETCH FIRST :lim ROWS ONLY"
        params["lim"] = limit
    cur.execute(sql, params)
    rows = cur.fetchall()
    if not rows:
        return "No daily reports found"
    lines = [f"Daily Reports ({len(rows)} entries):"]
    for r in rows:
        lines.append(f"\n--- {str(r[1])[:10]} ({r[2] or '?'}) [{r[0]}] ---")
        lines.append(f"  Email: {r[3]} (inbox:{r[4]} sent:{r[5]}) | Calendar: {r[6]}")
        lines.append(f"  Priority: H={r[7]} M={r[8]} L={r[9]} | Suspicious: {r[10]}")
        if r[13]:
            lines.append(f"  Summary: {str(r[13])[:300]}")
    return "\n".join(lines)


@mcp.tool()
def memory_activity_log(agent: str = "", action: str = "", workspace: str = "all", limit: int = 20) -> str:
    """View agent activity log. Filter by agent, action, workspace."""
    oracle = get_oracle()
    if oracle is None:
        return "Activity log requires Oracle L4 connection"
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
    if not rows:
        return "No activity log entries found"
    lines = [f"Activity log ({len(rows)} entries):"]
    for r in rows:
        ts = str(r[0])[:16] if r[0] else "?"
        lines.append(f"  {ts} | {r[2] or '?':15s} | {r[3] or r[4] or '?':15s} | {(r[5] or '')[:40]}")
    return "\n".join(lines)


# ============================================================
# ADMIN
# ============================================================

@mcp.tool()
def memory_status() -> str:
    """System status: local counts + Oracle sync status."""
    from .config import load_config
    config = load_config()
    lines = [f"Clawd-Lobster Memory Server v0.2.0", f"Workspace: {detect_workspace()}"]
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
    """Check session.md status and recommend compaction if needed."""
    ws = detect_workspace() if workspace == "current" else workspace
    from .config import load_config, get_workspace_map_path
    config = load_config()

    # Find session.md
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
            session_path = ws_root / display_path / ".claude-memory" / "session.md"
        else:
            session_path = ws_root / ws / ".claude-memory" / "session.md"
    except (FileNotFoundError, json.JSONDecodeError):
        session_path = ws_root / ws / ".claude-memory" / "session.md"

    if not session_path.exists():
        return f"No session.md found for [{ws}]"

    content = session_path.read_text(encoding="utf-8")
    line_count = len(content.splitlines())
    token_count = estimate_tokens(content)
    needs_compact = token_count > 3000 or line_count > 100
    status = "COMPACT RECOMMENDED" if needs_compact else "OK"

    return (
        f"[{ws}] session.md: {status}\n"
        f"  Lines: {line_count} | Tokens: ~{token_count} (CJK-aware)\n"
        f"  Threshold: 100 lines or 3000 tokens\n"
        f"{'  -> Extract items via memory_record_*, then trim session.md' if needs_compact else '  -> No compaction needed'}"
    )


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
