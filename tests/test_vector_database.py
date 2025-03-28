from pathlib import Path
from typing import Generator

import pytest

from src.vector_database import add_entry, fetch_similar, init_db

# Example embeddings
EMB_SIZE = 1536
embedding1 = [0.1] * EMB_SIZE
embedding2 = [0.2] * EMB_SIZE
query_embedding = [0.15] * EMB_SIZE


@pytest.fixture
def temp_db(tmp_path: Path) -> Generator[str, None, None]:
    db_path = tmp_path / "test_commands.db"

    # Set the test database path
    from src.vector_database import TEST_DB_PATH

    original_test_db_path = TEST_DB_PATH
    import src.vector_database

    src.vector_database.TEST_DB_PATH = str(db_path)

    # Initialize the database
    init_db()

    yield str(db_path)

    # Reset the test database path
    src.vector_database.TEST_DB_PATH = original_test_db_path

    # Clean up happens automatically with tmp_path


def test_add_entry(temp_db: str) -> None:
    add_entry(embedding1, "ls -la", "List all files")
    results = fetch_similar(embedding1, top_k=1)

    assert len(results) == 1
    assert results[0]["command"] == "ls -la"
    assert results[0]["description"] == "List all files"


def test_fetch_similar(temp_db: str) -> None:
    add_entry(embedding1, "ls -la", "List all files")
    add_entry(embedding2, "git status", "Check git repository status")

    results = fetch_similar(query_embedding, top_k=2)

    assert len(results) == 2
    assert results[0]["command"] == "git status"
    assert results[1]["command"] == "ls -la"


def test_no_similar_entries(temp_db: str) -> None:
    results = fetch_similar(query_embedding, top_k=3)
    assert len(results) == 0
