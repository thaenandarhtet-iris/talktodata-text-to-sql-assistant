from src.safety import validate_sql

class TestSafetyLayer:
    def test_simple_select_is_safe(self):
        sql = "SELECT * FROM flights WHERE delay_min > 30"
        is_safe, _ = validate_sql(sql)
        assert is_safe
    
    def test_join_select_is_safe(self):
        sql = "SELECT f.flight_num, c.carrier_name FROM flights f JOIN carriers c ON f.carrier_cd = c.carrier_cd"
        is_safe, _ = validate_sql(sql)
        assert is_safe
    
    def test_aggregation_is_safe(self):
        sql = "SELECT COUNT(*), AVG(delay_min) FROM flights GROUP BY carrier_cd"
        is_safe, _ = validate_sql(sql)
        assert is_safe
    
    def test_insert_is_rejected(self):
        sql = "INSERT INTO carriers VALUES ('XX', 'BadAirline')"
        is_safe, reason = validate_sql(sql)
        assert not is_safe
        assert "INSERT" in reason
    
    def test_update_is_rejected(self):
        sql = "UPDATE flights SET delay_min = 0 WHERE flight_id = 1"
        is_safe, reason = validate_sql(sql)
        assert not is_safe
        assert "UPDATE" in reason
    
    def test_delete_is_rejected(self):
        sql = "DELETE FROM bookings WHERE pax_id = 1"
        is_safe, reason = validate_sql(sql)
        assert not is_safe
        assert "DELETE" in reason
    
    def test_drop_is_rejected(self):
        sql = "DROP TABLE passengers"
        is_safe, reason = validate_sql(sql)
        assert not is_safe
        assert "DROP" in reason
    
    def test_alter_is_rejected(self):
        sql = "ALTER TABLE flights ADD COLUMN hack INT"
        is_safe, reason = validate_sql(sql)
        assert not is_safe
        assert "ALTER" in reason
    
    def test_statement_chaining_is_rejected(self):
        sql = "SELECT * FROM flights WHERE flight_id = 1; DROP TABLE flights; --"
        is_safe, reason = validate_sql(sql)
        assert not is_safe
        assert "semicolon" in reason.lower() or "multiple" in reason.lower()
    
    def test_union_select_is_rejected(self):
        sql = "SELECT flight_id FROM flights UNION SELECT pax_id FROM passengers"
        is_safe, reason = validate_sql(sql)
        assert not is_safe
        assert "UNION" in reason

    def test_trailing_semicolon_is_allowed(self):
        is_safe, _ = validate_sql("SELECT COUNT(*) FROM flights;")
        assert is_safe

    def test_keywords_inside_string_literals_are_allowed(self):
        sql = "SELECT * FROM passengers WHERE full_name = 'Drop Update'"
        is_safe, _ = validate_sql(sql)
        assert is_safe

    def test_replace_function_is_allowed(self):
        sql = "SELECT REPLACE(carrier_name, ' ', '') FROM carriers"
        is_safe, _ = validate_sql(sql)
        assert is_safe

    def test_keyword_hidden_after_comment_is_rejected(self):
        sql = "SELECT 1 /* harmless */; DELETE FROM bookings"
        is_safe, _ = validate_sql(sql)
        assert not is_safe

    def test_file_export_is_rejected(self):
        sql = "SELECT * FROM passengers INTO OUTFILE '/tmp/pax.csv'"
        is_safe, reason = validate_sql(sql)
        assert not is_safe
        assert "OUTFILE" in reason

    def test_sleep_is_rejected(self):
        is_safe, _ = validate_sql("SELECT SLEEP(100)")
        assert not is_safe

    def test_with_cte_is_rejected(self):
        is_safe, _ = validate_sql("WITH x AS (SELECT 1) SELECT * FROM x")
        assert not is_safe
