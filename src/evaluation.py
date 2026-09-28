"""
Score the SQL generator against the hand-written gold set.

Usage:
    python -m src.evaluation            # print the report
    python -m src.evaluation --save     # also write docs/accuracy_report.txt
    python -m src.evaluation --no-hints --save   # ablation: no schema_hints.yaml in the prompt
"""
import argparse
from datetime import date
from pathlib import Path

import yaml

from src.config import MODEL
from src.executor import execute_sql, compare_results
from src.safety import validate_sql
from src.schema_introspection import get_connection, introspect_schema, load_hints

ROOT = Path(__file__).resolve().parent.parent
GOLD_PATH = ROOT / "tests" / "gold_sql.yaml"
REPORT_PATH = ROOT / "docs" / "accuracy_report.txt"
NO_HINTS_REPORT_PATH = ROOT / "docs" / "accuracy_report_no_hints.txt"


def load_gold_set() -> list[dict]:
    with open(GOLD_PATH, "r") as f:
        return yaml.safe_load(f)["test_cases"]


def run_eval(sql_generator_func, conn, gold_set, use_hints: bool = True):
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
    hints = load_hints() if use_hints else {}

    results_by_category = {}
    total_passed = 0

    for test in gold_set:
        category = results_by_category.setdefault(test["category"], {"passed": 0, "total": 0, "failures": []})
        category["total"] += 1
        failure = {"test_id": test["id"], "question": test["question"]}

        try:
            generated_sql = sql_generator_func(test["question"], schema_text, hints)
            failure["generated_sql"] = generated_sql
            is_safe, reason = validate_sql(generated_sql)
            if not is_safe:
                category["failures"].append({**failure, "error": f"Safety check failed: {reason}"})
                continue

            success, actual_result = execute_sql(generated_sql, conn)
            if not success:
                category["failures"].append({**failure, "error": f"Execution failed: {actual_result}"})
                continue

            if compare_results(actual_result, test["expected_result"]):
                category["passed"] += 1
                total_passed += 1
            else:
                category["failures"].append({**failure, "error": "Result mismatch"})
        except Exception as e:
            category["failures"].append({**failure, "error": f"Exception: {str(e)}"})

    total_tests = len(gold_set)
    accuracy = (total_passed / total_tests * 100) if total_tests > 0 else 0

    return {"overall_accuracy": accuracy, "total_passed": total_passed, "total_tests": total_tests, "by_category": results_by_category}


def format_report(results: dict, use_hints: bool = True) -> str:
    lines = [
        "ACCURACY REPORT: TalkToData NL->SQL",
        f"Generated {date.today().isoformat()} with `python -m src.evaluation`",
        f"Model: {MODEL}",
        f"Schema hints: {'on' if use_hints else 'off (ablation)'}",
        "Metric: execution accuracy on one attempt, no retry (row order, column names and extra columns ignored; numbers to 2 dp)",
        "",
        f"Overall: {results['overall_accuracy']:.1f}% ({results['total_passed']}/{results['total_tests']})",
        "",
        "By category:",
    ]
    for name, cat in results["by_category"].items():
        lines.append(f"- {name}: {cat['passed']}/{cat['total']}")

    failures = [f for cat in results["by_category"].values() for f in cat["failures"]]
    if failures:
        lines += ["", "Failures:"]
        for f in failures:
            lines.append(f"- [{f['test_id']}] {f['question']}")
            lines.append(f"    {f['error']}")
            if "generated_sql" in f:
                lines.append(f"    SQL: {' '.join(f['generated_sql'].split())}")
    return "\n".join(lines) + "\n"


def main():
    from src.sql_generator import generate_sql_once

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--save", action="store_true", help="write the report to docs/")
    parser.add_argument("--no-hints", action="store_true", help="leave schema_hints.yaml out of the prompt")
    args = parser.parse_args()
    use_hints = not args.no_hints

    conn = get_connection()
    try:
        report = format_report(run_eval(generate_sql_once, conn, load_gold_set(), use_hints), use_hints)
    finally:
        conn.close()

    print(report)
    if args.save:
        path = REPORT_PATH if use_hints else NO_HINTS_REPORT_PATH
        path.write_text(report)
        print(f"Saved to {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
