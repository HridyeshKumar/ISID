import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE projects ADD COLUMN score INTEGER")

conn.commit()
conn.close()

print("✅ Score column added")