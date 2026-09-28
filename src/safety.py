import re

FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "UNION", "EXEC", "EXECUTE", "GRANT", "REVOKE",
    "OUTFILE", "DUMPFILE", "SLEEP", "BENCHMARK",
}

_STRING_LITERAL = re.compile(r"'(?:[^'\\]|\\.|'')*'|\"(?:[^\"\\]|\\.|\"\")*\"")
_COMMENT = re.compile(r"--[^\n]*|#[^\n]*|/\*.*?\*/", re.DOTALL)


def _strip_literals_and_comments(sql: str) -> str:
    """Blank out string literals and comments so keywords inside them are ignored."""
    sql = _STRING_LITERAL.sub("''", sql)
    return _COMMENT.sub(" ", sql)


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate that SQL is safe to execute.
    Returns: (is_safe: bool, reason_if_unsafe: str)

    This is the first line of defence; the app should also connect as a
    read-only database user (see data/01_readonly_user.sql).

    Rules:
    - Exactly one statement; a single trailing semicolon is tolerated
    - Must start with SELECT
    - No forbidden keywords (writes, DDL, UNION, file export, SLEEP/BENCHMARK)
    """
    code = _strip_literals_and_comments(sql).strip().upper()
    code = code.removesuffix(";").rstrip()

    if ";" in code:
        return False, "Multiple statements (semicolon) not allowed"

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", code):
            return False, f"{keyword} not allowed; read-only queries only"

    if not code.startswith("SELECT"):
        return False, "Only SELECT queries are allowed"

    return True, ""
