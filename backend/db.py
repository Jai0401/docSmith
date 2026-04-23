"""Database setup and models."""
import sqlite3
import json
from pathlib import Path
from typing import Optional

DB_PATH = "/tmp/docsmith.db"


def get_db_path():
    return DB_PATH


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_url TEXT UNIQUE NOT NULL,
            generation_type TEXT NOT NULL,
            content TEXT,
            status TEXT DEFAULT 'pending',
            agent_log TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def create_generation(repo_url: str, generation_type: str) -> int:
    """Create a new generation record, return its id."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "INSERT INTO generations (repo_url, generation_type, status) VALUES (?, ?, 'pending')",
        (repo_url, generation_type),
    )
    gen_id = cur.lastrowid
    conn.commit()
    conn.close()
    return gen_id


def get_generation(gen_id: int) -> Optional[dict]:
    """Get a generation record by id."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT * FROM generations WHERE id = ?", (gen_id,)).fetchone()
    conn.close()
    if not row:
        return None
    keys = ["id", "repo_url", "generation_type", "content", "status", "agent_log", "created_at", "updated_at"]
    return dict(zip(keys, row))


def update_status(gen_id: int, status: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE generations SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, gen_id),
    )
    conn.commit()
    conn.close()


def update_content(gen_id: int, content: str, status: str = "done"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE generations SET content = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (content, status, gen_id),
    )
    conn.commit()
    conn.close()


def append_agent_log(gen_id: int, entry: dict):
    """Append an entry to the agent_log JSON array."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT agent_log FROM generations WHERE id = ?", (gen_id,)).fetchone()
    log_list = []
    if row and row[0]:
        try:
            log_list = json.loads(row[0])
        except Exception:
            log_list = []
    log_list.append(entry)
    conn.execute(
        "UPDATE generations SET agent_log = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (json.dumps(log_list), gen_id),
    )
    conn.commit()
    conn.close()


def list_generations():
    """Return all generations ordered by created_at desc."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, repo_url, generation_type, status, created_at, updated_at FROM generations ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    keys = ["id", "repo_url", "generation_type", "status", "created_at", "updated_at"]
    return [dict(zip(keys, r)) for r in rows]