import pytest

from src.config import ANTHROPIC_API_KEY
from src.evaluation import load_gold_set


@pytest.fixture
def db_conn():
    """Live MySQL connection; skips the test if the Docker database isn't running."""
    from mysql.connector import Error
    from src.schema_introspection import get_connection

    try:
        conn = get_connection()
    except Error as e:
        pytest.skip(f"MySQL not reachable ({e.msg}); run `docker compose up -d`")
    yield conn
    conn.close()


@pytest.fixture
def api_key():
    if not ANTHROPIC_API_KEY:
        pytest.skip("ANTHROPIC_API_KEY not set")


@pytest.fixture
def gold_set():
    return load_gold_set()
