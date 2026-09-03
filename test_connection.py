import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()
conn = mysql.connector.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))
cursor = conn.cursor()
cursor.execute("SELECT status_cd, COUNT(*) FROM flights GROUP BY status_cd;")
print(cursor.fetchall())
