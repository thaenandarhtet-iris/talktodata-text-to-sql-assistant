import mysql.connector
from mysql.connector import Error

def execute_sql(sql: str, conn) -> tuple[bool, list[dict] | str]:
    """
    Execute a validated SELECT query and return results.
    
    Args:
        sql: SQL query string (assumed pre-validated)
        conn: MySQL connection object
    
    Returns:
        (success: bool, data_or_error: list[dict] or error string)
        - On success: (True, list of result rows as dicts)
        - On failure: (False, error message string)
    """
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return True, results
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def normalize_result_row(row: dict) -> dict:
    """
    Normalize a result row for comparison.
    Converts bytes to str, standardizes None/NULL, sorts keys.
    """
    normalized = {}
    for key, val in row.items():
        if isinstance(val, bytes):
            normalized[key] = val.decode("utf-8")
        elif val is None:
            normalized[key] = None
        else:
            normalized[key] = val
    return normalized

def compare_results(actual: list[dict], expected: list[dict]) -> bool:
    """
    Compare two result-sets for equality.
    Ignores row order; compares normalized values.
    
    Args:
        actual: Result set from executed query
        expected: Gold-standard result set
    
    Returns:
        True if sets contain the same rows (order-insensitive)
    """
    if len(actual) != len(expected):
        return False
    
    # Normalize both sets
    actual_norm = [normalize_result_row(row) for row in actual]
    expected_norm = [normalize_result_row(row) for row in expected]
    
    # Convert to sorted tuples for comparison (handles order-insensitivity)
    actual_sorted = sorted([tuple(sorted(row.items())) for row in actual_norm])
    expected_sorted = sorted([tuple(sorted(row.items())) for row in expected_norm])
    
    return actual_sorted == expected_sorted
