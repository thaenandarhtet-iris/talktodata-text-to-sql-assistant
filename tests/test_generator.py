import pytest

from src.sql_generator import extract_sql, generate_sql_with_retry


class TestExtractSql:
    def test_plain_sql_is_unchanged(self):
        assert extract_sql("SELECT 1") == "SELECT 1"

    def test_strips_sql_fence(self):
        assert extract_sql("```sql\nSELECT 1\n```") == "SELECT 1"

    def test_lowercase_select_survives_fence_stripping(self):
        assert extract_sql("```\nselect 1\n```") == "select 1"


@pytest.mark.usefixtures("api_key")
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
