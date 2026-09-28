import pytest

from src.sql_generator import build_explain_message, explain_answer, extract_sql, generate_sql_with_retry


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


class TestExplainMessage:
    def test_includes_question_sql_and_rows(self):
        msg = build_explain_message("How many?", "SELECT 1", [{"cnt": 4000}])
        assert "How many?" in msg and "SELECT 1" in msg and "cnt=4000" in msg

    def test_truncates_long_results(self):
        rows = [{"n": i} for i in range(50)]
        msg = build_explain_message("q", "s", rows, max_rows=20)
        assert "50 rows, first 20 shown" in msg
        assert "n=19" in msg and "n=20" not in msg


@pytest.mark.usefixtures("api_key")
class TestExplainAnswer:
    def test_answer_uses_the_result(self):
        answer = explain_answer("How many flights were delayed?", "SELECT COUNT(*) AS cnt FROM flights WHERE status_cd = 'DL'", [{"cnt": 809}])
        assert "809" in answer
