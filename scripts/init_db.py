"""
Initialize a workspace memory.db with all required tables.
Usage: python init_db.py [path/to/memory.db]
"""
import sqlite3
import sys
from pathlib import Path


def init_db(db_path):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS decisions (
        id TEXT PRIMARY KEY, date TEXT, what TEXT NOT NULL, why TEXT, how TEXT,
        who TEXT DEFAULT 'me', where_file TEXT, tags TEXT DEFAULT '[]',
        status TEXT DEFAULT 'confirmed', created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS resolved (
        id TEXT PRIMARY KEY, what TEXT NOT NULL, why TEXT, how TEXT,
        where_file TEXT, tags TEXT DEFAULT '[]', date TEXT DEFAULT (date('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS open_questions (
        id TEXT PRIMARY KEY, question TEXT NOT NULL, context TEXT,
        tags TEXT DEFAULT '[]', raised TEXT DEFAULT (date('now')), priority INTEGER DEFAULT 2)""")

    c.execute("""CREATE TABLE IF NOT EXISTS knowledge_items (
        id TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT,
        tags TEXT DEFAULT '[]', source_session TEXT,
        written_to_obsidian INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS daily_logs (
        date TEXT PRIMARY KEY, summary TEXT, log_path TEXT, item_count INTEGER DEFAULT 0)""")

    # Learned skills (self-evolution system)
    c.execute("""CREATE TABLE IF NOT EXISTS learned_skills (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        trigger_condition TEXT NOT NULL,
        approach TEXT NOT NULL,
        tools_used TEXT DEFAULT '',
        category TEXT DEFAULT 'general',
        source_task TEXT DEFAULT '',
        source_workspace TEXT DEFAULT '',
        times_used INTEGER DEFAULT 0,
        times_improved INTEGER DEFAULT 0,
        effectiveness REAL DEFAULT 1.0,
        last_used TEXT,
        created_at TEXT DEFAULT (datetime('now')))""")

    # TODOs (evolve system — auto-processed by cron)
    c.execute("""CREATE TABLE IF NOT EXISTS todos (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        priority INTEGER DEFAULT 2,
        status TEXT DEFAULT 'pending',
        branch TEXT DEFAULT '',
        note TEXT DEFAULT '',
        workspace TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')))""")

    # Action log (local audit trail — no Oracle required)
    c.execute("""CREATE TABLE IF NOT EXISTS action_log (
        id TEXT PRIMARY KEY,
        timestamp TEXT DEFAULT (datetime('now')),
        machine_id TEXT DEFAULT '',
        action TEXT NOT NULL,
        target TEXT DEFAULT '',
        note TEXT DEFAULT '',
        tokens INTEGER DEFAULT 0,
        workspace TEXT DEFAULT '')""")

    # Salience tracking columns (safe to re-run)
    for table in ['decisions', 'resolved', 'open_questions', 'knowledge_items']:
        for col, coltype, default in [
            ('access_count', 'INTEGER', '0'),
            ('last_accessed', 'TEXT', 'NULL'),
            ('salience', 'REAL', '1.0'),
            ('machine_id', 'TEXT', "''"),
        ]:
            try:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype} DEFAULT {default}")
            except sqlite3.OperationalError:
                pass

    # machine_id on action_log (safe to re-run)
    try:
        c.execute("ALTER TABLE action_log ADD COLUMN machine_id TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print(f"[OK] memory.db initialized: {db_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python init_db.py [db_path]")
        sys.exit(1)
    init_db(sys.argv[1])
