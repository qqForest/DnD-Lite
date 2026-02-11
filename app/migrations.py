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
    {
        "table": "map_tokens",
        "column": "icon",
        "sql": "ALTER TABLE map_tokens ADD COLUMN icon VARCHAR",
    },
    {
        "table": "maps",
        "column": "source_user_map_id",
        "sql": "ALTER TABLE maps ADD COLUMN source_user_map_id VARCHAR(36)",
    },
    {
        "table": "user_characters",
        "column": "appearance",
        "sql": "ALTER TABLE user_characters ADD COLUMN appearance TEXT",
    },
    {
        "table": "user_characters",
        "column": "avatar_url",
        "sql": "ALTER TABLE user_characters ADD COLUMN avatar_url VARCHAR",
    },
    {
        "table": "characters",
        "column": "appearance",
        "sql": "ALTER TABLE characters ADD COLUMN appearance TEXT",
    },
    {
        "table": "characters",
        "column": "avatar_url",
        "sql": "ALTER TABLE characters ADD COLUMN avatar_url VARCHAR",
    },
    {
        "table": "characters",
        "column": "armor_class",
        "sql": "ALTER TABLE characters ADD COLUMN armor_class INTEGER DEFAULT 10",
    },
    {
        "table": "user_characters",
        "column": "armor_class",
        "sql": "ALTER TABLE user_characters ADD COLUMN armor_class INTEGER DEFAULT 10",
    },
    {
        "table": "players",
        "column": "left_at",
        "sql": "ALTER TABLE players ADD COLUMN left_at DATETIME DEFAULT NULL",
    },
    {
        "table": "initiative_rolls",
        "column": "character_id",
        "sql": "ALTER TABLE initiative_rolls ADD COLUMN character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE",
    },
]

# NOTE: player_id in initiative_rolls should be nullable to support NPC rolls (which use character_id instead).
# SQLite doesn't support ALTER COLUMN for nullable changes, so we recreate the table.

def _fix_initiative_rolls_nullable():
    """Fix initiative_rolls.player_id to be nullable (for NPC support).

    SQLite doesn't support ALTER COLUMN, so we recreate the table.
    This is safe to run multiple times - it checks the schema first.
    """
    with engine.begin() as conn:
        # Check current schema
        result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='initiative_rolls'"))
        row = result.fetchone()

        if not row:
            # Table doesn't exist yet, will be created by create_all
            return False

        schema = row[0]

        # Check if player_id is already nullable (NOT NULL не присутствует после player_id)
        if 'player_id INTEGER NOT NULL' not in schema:
            # Already fixed
            return False

        print("Migrating initiative_rolls to make player_id nullable...")

        # Recreate table with correct schema
        conn.execute(text("DROP TABLE IF EXISTS initiative_rolls_backup"))
        conn.execute(text("ALTER TABLE initiative_rolls RENAME TO initiative_rolls_backup"))

        conn.execute(text("""
            CREATE TABLE initiative_rolls (
                id INTEGER NOT NULL,
                combat_id INTEGER NOT NULL,
                player_id INTEGER,
                character_id INTEGER,
                roll INTEGER NOT NULL,
                rolled_at DATETIME,
                PRIMARY KEY (id),
                FOREIGN KEY(combat_id) REFERENCES combats (id),
                FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE,
                FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE
            )
        """))

        conn.execute(text("CREATE INDEX ix_initiative_rolls_id ON initiative_rolls (id)"))

        # Copy data from backup (if any)
        conn.execute(text("""
            INSERT INTO initiative_rolls (id, combat_id, player_id, character_id, roll, rolled_at)
            SELECT id, combat_id, player_id, character_id, roll, rolled_at
            FROM initiative_rolls_backup
        """))

        conn.execute(text("DROP TABLE initiative_rolls_backup"))

        print("Initiative_rolls migration complete")
        return True


def run_migrations():
    """Check schema and apply missing columns. Idempotent."""
    # First, fix initiative_rolls table structure if needed
    _fix_initiative_rolls_nullable()

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
