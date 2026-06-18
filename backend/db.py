"""Database access layer for Tranzformation Nation.

ONE module owns all DB access so swapping SQLite <-> Postgres is trivial.

Selection rule (see ENV_SETUP.md):
  - If DATABASE_URL starts with "postgres" -> use psycopg (Postgres).
  - Otherwise -> use the Python stdlib sqlite3 driver against a local file.

All application SQL is written with "?" placeholders (SQLite style). When a
Postgres connection is in use we transparently translate "?" -> "%s" and adapt
a couple of dialect details. This keeps the rest of the codebase dialect-free.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional

BACKEND_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BACKEND_DIR / "schema.sql"
SEED_PATH = BACKEND_DIR / "seed.sql"

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
# Default SQLite file lives next to the backend so the app runs out of the box.
SQLITE_PATH = os.environ.get("SQLITE_PATH", str(BACKEND_DIR / "app.db"))

IS_POSTGRES = DATABASE_URL.lower().startswith("postgres")


def _translate(sql: str) -> str:
    """Translate SQLite-flavored SQL to the active dialect."""
    if IS_POSTGRES:
        # psycopg uses %s placeholders.
        return sql.replace("?", "%s")
    return sql


def get_conn():
    """Open a new connection. Caller is responsible for closing it."""
    if IS_POSTGRES:
        # Imported lazily so SQLite-only installs don't need psycopg.
        import psycopg  # type: ignore
        from psycopg.rows import dict_row  # type: ignore

        return psycopg.connect(DATABASE_URL, row_factory=dict_row)

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    # Enforce foreign keys + reasonable concurrency for a small app.
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def _rows_to_dicts(rows: Iterable[Any]) -> list[dict]:
    out: list[dict] = []
    for r in rows:
        if isinstance(r, sqlite3.Row):
            out.append({k: r[k] for k in r.keys()})
        elif isinstance(r, dict):
            out.append(dict(r))
        else:
            out.append(r)
    return out


def query(sql: str, params: tuple | list = ()) -> list[dict]:
    conn = get_conn()
    try:
        cur = conn.execute(_translate(sql), tuple(params))
        rows = cur.fetchall()
        return _rows_to_dicts(rows)
    finally:
        conn.close()


def query_one(sql: str, params: tuple | list = ()) -> Optional[dict]:
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple | list = ()) -> None:
    conn = get_conn()
    try:
        conn.execute(_translate(sql), tuple(params))
        conn.commit()
    finally:
        conn.close()


def insert(sql: str, params: tuple | list = ()) -> int | None:
    """Run an INSERT and return the new row id (best effort).

    SQLite: uses cursor.lastrowid.
    Postgres: appends RETURNING id and reads it back.
    """
    conn = get_conn()
    try:
        if IS_POSTGRES:
            sql_ret = sql.rstrip().rstrip(";")
            if "returning" not in sql_ret.lower():
                sql_ret += " RETURNING id"
            cur = conn.execute(_translate(sql_ret), tuple(params))
            row = cur.fetchone()
            conn.commit()
            if row is None:
                return None
            # dict_row -> {'id': ...}
            return list(row.values())[0] if isinstance(row, dict) else row[0]
        else:
            cur = conn.execute(_translate(sql), tuple(params))
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()


def _strip_sql_comments(sql_text: str) -> str:
    lines = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _split_statements(sql_text: str) -> list[str]:
    """Split into statements after stripping full-line `--` comments.

    Good enough for our simple schema/seed files (no semicolons inside strings).
    """
    cleaned = _strip_sql_comments(sql_text)
    statements = []
    for chunk in cleaned.split(";"):
        stmt = chunk.strip()
        if stmt:
            statements.append(stmt)
    return statements


def _run_script(conn, sql_text: str) -> None:
    """Execute a multi-statement SQL script across dialects."""
    if IS_POSTGRES:
        for stmt in _split_statements(sql_text):
            conn.execute(_translate(stmt))
    else:
        # SQLite handles comments + multiple statements natively here.
        conn.executescript(sql_text)


def _table_exists(conn, name: str) -> bool:
    try:
        if IS_POSTGRES:
            cur = conn.execute(
                "SELECT 1 FROM information_schema.tables WHERE table_name = %s",
                (name,),
            )
        else:
            cur = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (name,),
            )
        return cur.fetchone() is not None
    except Exception:
        return False


def init_db(force_seed: bool = False) -> dict:
    """Create the schema and seed default data if needed.

    Returns a small report dict so initdb.sh can print what happened.
    Idempotent: safe to run repeatedly.
    """
    report = {"backend": "postgres" if IS_POSTGRES else "sqlite", "created": False, "seeded": False}

    schema_sql = SCHEMA_PATH.read_text()
    seed_sql = SEED_PATH.read_text()

    conn = get_conn()
    try:
        already = _table_exists(conn, "users")
        _run_script(conn, schema_sql)
        conn.commit()
        report["created"] = not already

        # Seed only when there is no admin yet (or when forced).
        need_seed = force_seed
        if not need_seed:
            cur = conn.execute("SELECT COUNT(*) AS c FROM users")
            row = cur.fetchone()
            count = (row["c"] if isinstance(row, (dict, sqlite3.Row)) else row[0]) or 0
            need_seed = count == 0

        if need_seed:
            _run_script(conn, seed_sql)
            conn.commit()
            report["seeded"] = True
    finally:
        conn.close()

    return report


if __name__ == "__main__":
    print(init_db())
