import sqlite3
from scoring import calculate_score

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT project_id, title, category, url FROM projects")
rows = cursor.fetchall()

updated = 0

for project_id, title, category, url in rows:
    description = ""  # (we’ll improve this later)

    score = calculate_score(title, category, description)

    cursor.execute(
        "UPDATE projects SET score = ? WHERE project_id = ?",
        (score, project_id)
    )

    updated += 1

conn.commit()
conn.close()

print("✅ Scored:", updated)