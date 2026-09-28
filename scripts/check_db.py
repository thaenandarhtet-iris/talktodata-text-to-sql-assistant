"""Smoke-test the database connection: prints flight counts by status code.

Usage:
    python -m scripts.check_db
"""
from src.schema_introspection import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT status_cd, COUNT(*) FROM flights GROUP BY status_cd ORDER BY status_cd")
for status, count in cursor.fetchall():
    print(f"{status}: {count}")
conn.close()
