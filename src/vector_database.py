import os
import sqlite3
import struct
from typing import List, Optional

import sqlite_vec

# This will be used to override the database path during testing
# If TEST_DB_PATH is set, it will be used instead of DEFAULT_DB_PATH
TEST_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "commands-test.db",
)

# Get database path from environment or use default
DEFAULT_DB_PATH = os.path.join(
    os.getenv(
        "FASTCMD_DB_DIR",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ),
    "commands.db",
)


def get_db_path() -> str:
    """
    Return TEST_DB_PATH if we're explicitly in test mode, else DEFAULT_DB_PATH.
    """
    if os.getenv("TESTING") == "1":
        return TEST_DB_PATH
    else:
        return DEFAULT_DB_PATH


# serialize embedding to bytes
def serialize(vector: List[float]) -> bytes:
    return struct.pack("%sf" % len(vector), *vector)


def init_db(db_path: Optional[str] = None) -> None:
    db_path = db_path or get_db_path()
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            description TEXT
        );
    """
    )

    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_commands USING vec0(
            id INTEGER PRIMARY KEY,
            embedding FLOAT[1536]
        );
    """
    )
    conn.commit()
    conn.close()


def add_entry(
    embedding: List[float],
    command: str,
    description: str,
    db_path: Optional[str] = None,
) -> None:
    db_path = db_path or get_db_path()
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO commands (command, description) VALUES (?, ?)",
        (command, description),
    )
    entry_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO vec_commands (id, embedding) VALUES (?, ?)",
        (entry_id, serialize(embedding)),
    )
    conn.commit()
    conn.close()


def fetch_similar(
    user_embedding: List[float], top_k: int = 3, db_path: Optional[str] = None
) -> list:
    db_path = db_path or get_db_path()
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    results = conn.execute(
        """
        SELECT
            commands.command,
            commands.description,
            distance
        FROM vec_commands
        LEFT JOIN commands ON commands.id = vec_commands.id
        WHERE embedding MATCH ?
          AND k = ?
        ORDER BY distance ASC;
    """,
        (serialize(user_embedding), top_k),
    ).fetchall()

    conn.close()

    return [
        {"command": row[0], "description": row[1], "distance": row[2]}
        for row in results
    ]


def fetch_all_commands(db_path: Optional[str] = None) -> list:
    """
    Fetch all commands from the database.

    Args:
        db_path: Optional path to the database file

    Returns:
        list: List of dictionaries containing command and description
    """
    db_path = db_path or get_db_path()
    conn = sqlite3.connect(db_path)

    results = conn.execute(
        """
        SELECT command, description
        FROM commands
        ORDER BY id ASC;
    """
    ).fetchall()

    conn.close()

    return [{"command": row[0], "description": row[1]} for row in results]
