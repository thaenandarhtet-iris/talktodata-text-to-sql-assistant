import yaml
import pytest
from src.executor import execute_sql, compare_results
from src.schema_introspection import get_connection, introspect_schema, load_hints
from src.safety import validate_sql

@pytest.fixture
def db_conn():
    conn = get_connection()
    yield conn
    conn.close()

@pytest.fixture
def gold_set():
    with open("tests/gold_sql.yaml", "r") as f:
        return yaml.safe_load(f)["test_cases"]

def run_eval(sql_generator_func, conn, gold_set):
    """
    Run evaluation against gold question set.
    
    Args:
        sql_generator_func: Function that takes (question, schema_text, hints) -> sql
        conn: MySQL connection
        gold_set: List of test cases from gold_sql.yaml
    
    Returns:
        Dict with overall accuracy and per-category breakdown
    """
    schema_text = introspect_schema(conn)
    hints = load_hints()
    
    results_by_category = {}
    total_passed = 0
    total_tests = 0
    
    for test in gold_set:
        category = test["category"]
        question = test["question"]
        expected_result = test["expected_result"]
        gold_sql = test["gold_sql"]
        
        if category not in results_by_category:
            results_by_category[category] = {"passed": 0, "total": 0, "failures": []}
        
        results_by_category[category]["total"] += 1
        total_tests += 1
        
        try:
            generated_sql = sql_generator_func(question, schema_text, hints)
            is_safe, reason = validate_sql(generated_sql)
            if not is_safe:
                results_by_category[category]["failures"].append({"test_id": test["id"], "question": question, "error": f"Safety check failed: {reason}"})
                continue
            
            success, actual_result = execute_sql(generated_sql, conn)
            if not success:
                results_by_category[category]["failures"].append({"test_id": test["id"], "question": question, "error": f"Execution failed: {actual_result}", "gold_sql": gold_sql, "generated_sql": generated_sql})
                continue
            
            if compare_results(actual_result, expected_result):
                results_by_category[category]["passed"] += 1
                total_passed += 1
            else:
                results_by_category[category]["failures"].append({"test_id": test["id"], "question": question, "error": "Result mismatch", "gold_sql": gold_sql, "generated_sql": generated_sql, "expected": expected_result, "actual": actual_result})
        except Exception as e:
            results_by_category[category]["failures"].append({"test_id": test["id"], "question": question, "error": f"Exception: {str(e)}"})
    
    accuracy = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    return {"overall_accuracy": accuracy, "total_passed": total_passed, "total_tests": total_tests, "by_category": results_by_category}

class TestEval:
    def test_gold_set_is_valid(self, gold_set):
        for test in gold_set:
            assert "id" in test
            assert "category" in test
            assert "question" in test
            assert "gold_sql" in test
            assert "expected_result" in test
