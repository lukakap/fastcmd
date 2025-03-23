import pytest
from src.vector_database import add_entry, fetch_similar, init_db

# Example embeddings
EMB_SIZE = 1536
embedding1 = [0.1] * EMB_SIZE
embedding2 = [0.2] * EMB_SIZE
query_embedding = [0.15] * EMB_SIZE

@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test_commands.db"
    init_db(db_path=str(db_path))
    return str(db_path)

def test_add_entry(temp_db):
    add_entry(embedding1, "ls -la", "List all files", db_path=temp_db)
    results = fetch_similar(embedding1, top_k=1, db_path=temp_db)

    assert len(results) == 1
    assert results[0]["command"] == "ls -la"
    assert results[0]["description"] == "List all files"

def test_fetch_similar(temp_db):
    add_entry(embedding1, "ls -la", "List all files", db_path=temp_db)
    add_entry(embedding2, "git status", "Check git repository status", db_path=temp_db)

    results = fetch_similar(query_embedding, top_k=2, db_path=temp_db)

    assert len(results) == 2
    assert results[0]["command"] == "git status"
    assert results[1]["command"] == "ls -la"

def test_no_similar_entries(temp_db):
    results = fetch_similar(query_embedding, top_k=3, db_path=temp_db)
    assert len(results) == 0
