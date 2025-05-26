import sqlite3
import pandas as pd

# Replace with your file path
db_path = r'C:\GenAI Complete\aceint_whatsapp\tmp\memory.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# View data from a specific table (e.g., memory)
cursor.execute("SELECT * FROM memory LIMIT 10;")
rows = cursor.fetchall()
for row in rows:
    print(row)

df = pd.read_sql_query("SELECT * FROM memory", sqlite3.connect(db_path))
print(df.head())


conn.close()
