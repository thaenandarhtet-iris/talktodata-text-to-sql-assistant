import os
from anthropic import Anthropic
from src.config import MODEL, MAX_TOKENS, ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)

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
"""

def extract_sql_from_response(message) -> str:
    """Extract SQL text from Claude response, handling ThinkingBlocks."""
    for block in message.content:
        if hasattr(block, 'text'):
            sql = block.text.strip()
            if sql.startswith("```"):
                sql = sql.strip("`")
                if sql.startswith("sql"):
                    sql = sql[3:].strip()
            return sql
    raise ValueError("No text content found in response")

def generate_sql_once(question: str, schema_text: str, hints: dict, previous_error: str = None) -> str:
    """Generate SQL once. Returns raw SQL string."""
def generate_sql_once(question: str, schema_text: str, hints: dict, previous_error: str = None) -> str:
    system_prompt = build_system_prompt(schema_text, hints)
    user_message = question
    if previous_error:
        user_message += f"\n\n[Previous attempt failed with DB error: {previous_error}. Please fix and try again.]"
    
    message = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, system=system_prompt, messages=[{"role": "user", "content": user_message}])
    
    sql = ""
    for block in message.content:
        if hasattr(block, 'text'):
            sql = block.text.strip()
            break
    
    if sql.startswith("```"):
        sql = sql.strip("`").lstrip("sql").strip()
    
    return sql

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
        if not is_safe:
            if attempt < max_retries:
                previous_error = f"Safety: {reason}"
                continue
            return sql
        success, result = execute_sql(sql, conn)
        if success:
            return sql
        if attempt < max_retries:
            previous_error = result
        else:
            return sql
    return sql
