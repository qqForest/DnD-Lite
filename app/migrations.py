"""
Lightweight startup migrations for SQLite.

Each migration is a dict with:
  - table: target table name
  - column: column to add
  - sql: ALTER TABLE statement

On startup, the system checks which columns already exist
and only runs ALTER TABLE for missing ones. Safe to re-run.
"""

from sqlalchemy import text, inspect
from app.database import engine

MIGRATIONS = [
    {
        "table": "players",
        "column": "is_ready",
        "sql": "ALTER TABLE players ADD COLUMN is_ready BOOLEAN DEFAULT 0",
    },
    {
        "table": "players",
        "column": "user_id",
        "sql": "ALTER TABLE players ADD COLUMN user_id INTEGER REFERENCES users(id)",
    },
    {
        "table": "user_characters",
        "column": "sessions_played",
        "sql": "ALTER TABLE user_characters ADD COLUMN sessions_played INTEGER DEFAULT 0",
    },
    {
        "table": "players",
        "column": "can_move",
        "sql": "ALTER TABLE players ADD COLUMN can_move BOOLEAN DEFAULT 0",
    },
]


def run_migrations():
    """Check schema and apply missing columns. Idempotent."""
    insp = inspect(engine)
    cache = {}

    applied = 0
    for migration in MIGRATIONS:
        table = migration["table"]
        column = migration["column"]

        if table not in cache:
            try:
                cols = insp.get_columns(table)
                cache[table] = {c["name"] for c in cols}
            except Exception:
                # Table doesn't exist yet — create_all will handle it
                cache[table] = set()
                continue

        if column not in cache[table]:
            with engine.begin() as conn:
                conn.execute(text(migration["sql"]))
            cache[table].add(column)
            applied += 1
            print(f"Migration applied: {table}.{column}")

    if applied:
        print(f"Migrations complete: {applied} applied")
