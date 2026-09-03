import pytest
from src.sql_generator import generate_sql_with_retry
from src.schema_introspection import get_connection

@pytest.fixture
def db_conn():
    conn = get_connection()
    yield conn
    conn.close()

class TestGenerator:
    def test_generate_simple_select(self, db_conn):
        question = "How many flights are there?"
        sql = generate_sql_with_retry(question, db_conn)
        assert "SELECT" in sql.upper()
        assert "COUNT" in sql.upper()
        assert "flights" in sql.lower()
    
    def test_generate_with_where_clause(self, db_conn):
        question = "Which flights were delayed?"
        sql = generate_sql_with_retry(question, db_conn)
        assert "SELECT" in sql.upper()
        assert "WHERE" in sql.upper()
        assert "flights" in sql.lower()
    
    def test_generate_join_query(self, db_conn):
        question = "Which carrier has the most flights?"
        sql = generate_sql_with_retry(question, db_conn)
        assert "SELECT" in sql.upper()
        assert ("JOIN" in sql.upper() or "flights" in sql.lower())
