import re

FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "UNION", "EXEC", "EXECUTE",
}

def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate that SQL is safe to execute.
    Returns: (is_safe: bool, reason_if_unsafe: str)
    
    Rules:
    - Only SELECT allowed
    - No semicolons (prevents statement chaining)
    - No forbidden keywords (INSERT, UPDATE, DROP, etc.)
    - No UNION (bypasses intended join context)
    """
    sql_normalized = sql.strip().upper()
    
    # Check for multiple statements
    if ";" in sql:
        return False, "Multiple statements (semicolon) not allowed"
    
    # Check for forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_normalized):
            return False, f"{keyword} operation not allowed; read-only queries only"
    
    # Ensure query starts with SELECT
    cleaned = sql_normalized.split("--")[0].split("/*")[0].strip()
    if not cleaned.startswith("SELECT"):
        return False, "Only SELECT queries are allowed"
    
    return True, ""
