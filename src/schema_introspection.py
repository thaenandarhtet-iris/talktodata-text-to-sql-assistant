import mysql.connector
from src.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def get_connection():
    return mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

def introspect_schema(conn) -> str:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME", (DB_NAME,))
    tables = [row["TABLE_NAME"] for row in cursor.fetchall()]
    schema_lines = []
    for table in tables:
        cursor.execute("SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s ORDER BY ORDINAL_POSITION", (DB_NAME, table))
        columns = cursor.fetchall()
        cursor.execute("SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND REFERENCED_TABLE_NAME IS NOT NULL", (DB_NAME, table))
        fks = cursor.fetchall()
        fk_map = {row["COLUMN_NAME"]: row for row in fks}
        schema_lines.append(f"{table}(")
        for col in columns:
            col_name, col_type = col["COLUMN_NAME"], col["COLUMN_TYPE"]
            nullable = "NULL" if col["IS_NULLABLE"] == "YES" else "NOT NULL"
            key = "PRIMARY KEY" if col["COLUMN_KEY"] == "PRI" else ("UNIQUE" if col["COLUMN_KEY"] == "UNI" else "")
            line = f"    {col_name} {col_type}"
            if key: line += f" {key}"
            line += f" {nullable}"
            if col_name in fk_map: line += f", references {fk_map[col_name]["REFERENCED_TABLE_NAME"]}({fk_map[col_name]["REFERENCED_COLUMN_NAME"]})"
            schema_lines.append(line + ",")
        schema_lines[-1] = schema_lines[-1].rstrip(",")
        schema_lines.append(")")
        schema_lines.append("")
    cursor.close()
    return "\n".join(schema_lines)

def load_hints() -> dict:
    import yaml
    with open("schema_hints.yaml", "r") as f:
        return yaml.safe_load(f) or {}