from functools import cache

from anthropic import Anthropic

from src.config import MODEL, MAX_TOKENS, ANTHROPIC_API_KEY


@cache
def get_client() -> Anthropic:
    return Anthropic(api_key=ANTHROPIC_API_KEY)


def build_system_prompt(schema_text: str, hints: dict) -> str:
    hints_text = ""
    if hints:
        hints_text = "\n\nColumn metadata and enum meanings:\n"
        for col_path, metadata in hints.items():
            hints_text += f"\n{col_path}:\n"
            if "meaning" in metadata:
                hints_text += f"  Meaning: {metadata['meaning']}\n"
            if "values" in metadata:
                hints_text += "  Enum values:\n"
                for code, desc in metadata["values"].items():
                    hints_text += f"    {code} = {desc}\n"
            if "note" in metadata:
                hints_text += f"  Note: {metadata['note']}\n"

    return f"""You are a MySQL expert. Given a question in plain English and a database schema, write a single MySQL SELECT query that answers it.

Database schema:
{schema_text}
{hints_text}

Rules:
- Only ever write SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, ALTER, or anything that changes data.
- Return only the raw SQL query. No explanation, no markdown code fences, no semicolon-separated multiple statements.
- Use the coded column values exactly as they appear in the schema metadata, for example status_cd = 'DL', do not spell them out.
- If the question is ambiguous, make the most reasonable assumption and answer it, don't ask a clarifying question back.
- Ensure all table names and column names match the schema exactly.
- When the answer identifies an entity (a carrier, airport, passenger...), return its human-readable name column (e.g. carrier_name), joining to its table if needed, rather than only its code or ID.
"""


def extract_sql(text: str) -> str:
    """Strip an optional ```sql ... ``` fence from the model's reply."""
    sql = text.strip()
    if sql.startswith("```"):
        sql = sql.strip("`").strip()
        if sql[:3].lower() == "sql":
            sql = sql[3:]
    return sql.strip()


def generate_sql_once(question: str, schema_text: str, hints: dict, previous_error: str | None = None) -> str:
    """Generate SQL once. Returns raw SQL string."""
    system_prompt = build_system_prompt(schema_text, hints)
    user_message = question
    if previous_error:
        user_message += f"\n\n[Previous attempt failed with DB error: {previous_error}. Please fix and try again.]"

    message = get_client().messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    text = next((block.text for block in message.content if block.type == "text"), "")
    return extract_sql(text)


EXPLAIN_SYSTEM_PROMPT = """You answer a user's question about an airline database in plain English, using only the query result you are given.

Rules:
- One or two sentences, no SQL, no markdown.
- Use the numbers exactly as they appear in the result; round long decimals sensibly.
- Translate codes into words (e.g. CN = cancelled, CF = confirmed, J = business class).
- If the result is empty, say that nothing matched.
- If only some rows are shown, describe the pattern rather than listing every row."""


def build_explain_message(question: str, sql: str, rows: list[dict], max_rows: int = 20) -> str:
    shown = rows[:max_rows]
    lines = [f"Question: {question}", f"SQL: {sql}", f"Result ({len(rows)} rows" + (f", first {max_rows} shown" if len(rows) > max_rows else "") + "):"]
    lines += [", ".join(f"{k}={v}" for k, v in row.items()) for row in shown]
    return "\n".join(lines)


def explain_answer(question: str, sql: str, rows: list[dict]) -> str:
    """Summarise a query result as a short plain-English answer."""
    message = get_client().messages.create(
        model=MODEL,
        max_tokens=300,
        system=EXPLAIN_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_explain_message(question, sql, rows)}],
    )
    return next((block.text for block in message.content if block.type == "text"), "").strip()


def generate_sql_with_retry(question: str, conn, max_retries: int = 1) -> str:
    from src.schema_introspection import introspect_schema, load_hints
    from src.safety import validate_sql
    from src.executor import execute_sql

    schema_text = introspect_schema(conn)
    hints = load_hints()
    previous_error = None

    for attempt in range(max_retries + 1):
        sql = generate_sql_once(question, schema_text, hints, previous_error)
        is_safe, reason = validate_sql(sql)
        if is_safe:
            success, result = execute_sql(sql, conn)
            if success:
                return sql
            previous_error = result
        else:
            previous_error = f"Safety: {reason}"
    return sql
