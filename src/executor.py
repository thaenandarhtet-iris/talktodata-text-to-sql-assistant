import datetime
from collections import Counter
from decimal import Decimal

from mysql.connector import Error


def execute_sql(sql: str, conn, max_rows: int | None = None) -> tuple[bool, list[dict] | str]:
    """
    Execute a validated SELECT query and return results.

    Args:
        sql: SQL query string (assumed pre-validated)
        conn: MySQL connection object
        max_rows: If set, return at most this many rows

    Returns:
        (success: bool, data_or_error: list[dict] or error string)
        - On success: (True, list of result rows as dicts)
        - On failure: (False, error message string)
    """
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(sql)
        results = cursor.fetchall() if max_rows is None else cursor.fetchmany(max_rows)
        cursor.close()
        return True, results
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def normalize_value(val):
    """Normalize a single cell so MySQL and YAML values compare equal."""
    if isinstance(val, bytes):
        return val.decode("utf-8")
    if isinstance(val, bool):
        return int(val)
    if isinstance(val, (int, float, Decimal)):
        return round(float(val), 2)
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.isoformat(sep=" ") if isinstance(val, datetime.datetime) else val.isoformat()
    return val


def normalize_row(row: dict) -> Counter:
    """
    Reduce a row to a multiset of its values, ignoring column names and order.

    Generated SQL is free to alias columns differently from the gold SQL
    (e.g. `COUNT(*) AS total` vs `AS cnt`), so only the values are compared.
    """
    return Counter(normalize_value(v) for v in row.values())


def _row_matches(actual: Counter, expected: Counter) -> bool:
    """True if the actual row contains every expected value (extra columns allowed)."""
    return all(actual[value] >= count for value, count in expected.items())


def compare_results(actual: list[dict], expected: list[dict]) -> bool:
    """
    Compare a generated result-set with the gold one.

    Ignores row order, column names and column order, and allows extra
    columns (answering "which carrier?" with the name plus its flight count
    is still correct). Numbers are compared to 2 decimal places.

    Returns:
        True if every expected row is matched by a distinct actual row
    """
    if len(actual) != len(expected):
        return False
    remaining = [normalize_row(row) for row in actual]
    for expected_row in map(normalize_row, expected):
        match = next((i for i, row in enumerate(remaining) if _row_matches(row, expected_row)), None)
        if match is None:
            return False
        remaining.pop(match)
    return True
