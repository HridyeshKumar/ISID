import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ---------------- NEW COLUMNS ----------------

columns = [
    "ALTER TABLE projects ADD COLUMN impact_score REAL DEFAULT 0",
    "ALTER TABLE projects ADD COLUMN innovation_score REAL DEFAULT 0",
    "ALTER TABLE projects ADD COLUMN scale_score REAL DEFAULT 0",
    "ALTER TABLE projects ADD COLUMN sustainability_score REAL DEFAULT 0",
    "ALTER TABLE projects ADD COLUMN collaboration_score REAL DEFAULT 0",

    "ALTER TABLE projects ADD COLUMN topics TEXT",
    "ALTER TABLE projects ADD COLUMN detected_locations TEXT"
]

# ---------------- EXECUTE ----------------

for query in columns:
    try:
        cursor.execute(query)
        print("✅ Executed:", query)

    except Exception as e:
        print("⚠️ Skipped:", e)

conn.commit()
conn.close()

print("\n🚀 Database upgraded successfully")