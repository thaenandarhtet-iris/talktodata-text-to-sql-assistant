from src.executor import execute_sql, compare_results


class TestGoldSet:
    def test_gold_set_is_valid(self, gold_set):
        ids = [test["id"] for test in gold_set]
        assert len(ids) == len(set(ids)), "duplicate test ids"
        for test in gold_set:
            for field in ("id", "category", "question", "gold_sql", "expected_result"):
                assert field in test, f"{test.get('id')} missing {field}"

    def test_gold_sql_produces_expected_results(self, db_conn, gold_set):
        """The answer key itself must be right, or accuracy numbers mean nothing."""
        for test in gold_set:
            success, result = execute_sql(test["gold_sql"], db_conn)
            assert success, f"{test['id']}: {result}"
            assert compare_results(result, test["expected_result"]), test["id"]
