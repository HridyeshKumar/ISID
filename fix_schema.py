import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

columns = [
    ("country", "TEXT"),
    ("status", "TEXT")
]

for col, datatype in columns:
    try:
        cursor.execute(f"ALTER TABLE projects ADD COLUMN {col} {datatype}")
        print(f"✅ Added column: {col}")
    except Exception as e:
        print(f"⚠️ {col} may already exist:", e)

conn.commit()
conn.close()