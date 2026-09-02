import pytest
from src.executor import execute_sql, compare_results
from src.schema_introspection import get_connection

@pytest.fixture
def db_conn():
    conn = get_connection()
    yield conn
    conn.close()

class TestExecutor:
    def test_simple_select_executes(self, db_conn):
        sql = "SELECT COUNT(*) as cnt FROM flights"
        success, result = execute_sql(sql, db_conn)
        assert success
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["cnt"] > 0
    
    def test_select_with_where_executes(self, db_conn):
        sql = "SELECT flight_num FROM flights WHERE carrier_cd = "HZ" LIMIT 5"
        success, result = execute_sql(sql, db_conn)
        assert success
        assert isinstance(result, list)
    
    def test_invalid_sql_returns_error(self, db_conn):
        sql = "SELECT * FROM nonexistent_table"
        success, result = execute_sql(sql, db_conn)
        assert not success
        assert isinstance(result, str)
        assert "nonexistent" in result.lower() or "doesn"t exist" in result.lower()
    
    def test_compare_identical_results(self):
        actual = [
            {"flight_id": 1, "carrier_cd": "HZ"},
            {"flight_id": 2, "carrier_cd": "PW"},
        ]
        expected = [
            {"flight_id": 1, "carrier_cd": "HZ"},
            {"flight_id": 2, "carrier_cd": "PW"},
        ]
        assert compare_results(actual, expected)
    
    def test_compare_order_insensitive(self):
        actual = [
            {"flight_id": 2, "carrier_cd": "PW"},
            {"flight_id": 1, "carrier_cd": "HZ"},
        ]
        expected = [
            {"flight_id": 1, "carrier_cd": "HZ"},
            {"flight_id": 2, "carrier_cd": "PW"},
        ]
        assert compare_results(actual, expected)
    
    def test_compare_different_lengths(self):
        actual = [{"id": 1}, {"id": 2}]
        expected = [{"id": 1}]
        assert not compare_results(actual, expected)
    
    def test_compare_different_values(self):
        actual = [{"id": 1}]
        expected = [{"id": 2}]
        assert not compare_results(actual, expected)
