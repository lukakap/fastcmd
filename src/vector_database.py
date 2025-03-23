import sqlite3
import sqlite_vec
import struct
import numpy as np
from typing import List
import os

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands.db")

# serialize embedding to bytes
def serialize(vector: List[float]) -> bytes:
    return struct.pack("%sf" % len(vector), *vector)

def init_db(db_path=DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            description TEXT
        );
    """)

    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_commands USING vec0(
            id INTEGER PRIMARY KEY,
            embedding FLOAT[1536]
        );
    """)
    conn.commit()
    conn.close()

def add_entry(embedding: List[float], command: str, description: str, db_path=DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO commands (command, description) VALUES (?, ?)",
        (command, description)
    )
    entry_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO vec_commands (id, embedding) VALUES (?, ?)",
        (entry_id, serialize(embedding))
    )
    conn.commit()
    conn.close()

def fetch_similar(user_embedding: List[float], top_k: int = 3, db_path=DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    results = conn.execute("""
        SELECT
            commands.command,
            commands.description,
            distance
        FROM vec_commands
        LEFT JOIN commands ON commands.id = vec_commands.id
        WHERE embedding MATCH ?
          AND k = ?
        ORDER BY distance ASC;
    """, (serialize(user_embedding), top_k)).fetchall()

    conn.close()

    return [
        {"command": row[0], "description": row[1], "distance": row[2]}
        for row in results
    ]

