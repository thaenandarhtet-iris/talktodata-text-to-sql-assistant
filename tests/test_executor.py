from datetime import date
from decimal import Decimal

from src.executor import execute_sql, compare_results

class TestExecutor:
    def test_simple_select_executes(self, db_conn):
        sql = "SELECT COUNT(*) as cnt FROM flights"
        success, result = execute_sql(sql, db_conn)
        assert success
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["cnt"] > 0
    
    def test_select_with_where_executes(self, db_conn):
        sql = "SELECT flight_num FROM flights WHERE carrier_cd = 'HZ' LIMIT 5"
        success, result = execute_sql(sql, db_conn)
        assert success
        assert isinstance(result, list)
    
    def test_invalid_sql_returns_error(self, db_conn):
        sql = "SELECT * FROM nonexistent_table"
        success, result = execute_sql(sql, db_conn)
        assert not success
        assert isinstance(result, str)
        assert "nonexistent" in result.lower() or "doesn't exist" in result.lower()
    
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

    def test_compare_ignores_column_aliases(self):
        assert compare_results([{"total": 5000}], [{"cnt": 5000}])

    def test_compare_ignores_column_order(self):
        actual = [{"carrier_cd": "HZ", "flights": 10}]
        expected = [{"flights": 10, "carrier_cd": "HZ"}]
        assert compare_results(actual, expected)

    def test_compare_decimal_against_yaml_float(self):
        assert compare_results([{"revenue": Decimal("1234.50")}], [{"revenue": 1234.5}])

    def test_compare_rounds_to_two_places(self):
        assert compare_results([{"avg_delay": Decimal("12.3456")}], [{"avg_delay": 12.35}])

    def test_compare_dates_against_yaml_strings(self):
        assert compare_results([{"d": date(2024, 3, 1)}], [{"d": "2024-03-01"}])

    def test_max_rows_caps_results(self, db_conn):
        success, result = execute_sql("SELECT flight_id FROM flights", db_conn, max_rows=10)
        assert success
        assert len(result) == 10

    def test_compare_allows_extra_columns(self):
        actual = [{"carrier_name": "Meridian Air", "flight_count": 705}]
        assert compare_results(actual, [{"carrier_name": "Meridian Air"}])

    def test_compare_missing_column_fails(self):
        expected = [{"carrier_name": "Meridian Air", "avg_delay": 21.45}]
        assert not compare_results([{"carrier_name": "Meridian Air"}], expected)

    def test_compare_extra_rows_fail(self):
        actual = [{"carrier_name": "Meridian Air"}, {"carrier_name": "AeroLoop"}]
        assert not compare_results(actual, [{"carrier_name": "Meridian Air"}])

    def test_compare_duplicate_values_need_distinct_rows(self):
        actual = [{"n": 1}, {"n": 2}]
        expected = [{"n": 1}, {"n": 1}]
        assert not compare_results(actual, expected)
