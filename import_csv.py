import pandas as pd
import sqlite3

df = pd.read_csv("ngo_dataset.csv")

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

inserted = 0

for _, row in df.iterrows():
    # avoid duplicates
    cursor.execute("SELECT 1 FROM projects WHERE title = ?", (row["title"],))
    if cursor.fetchone():
        continue

    cursor.execute("""
        INSERT INTO projects (title, source, url, state, category, country, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        row["title"],
        row["source"],
        row["url"],
        row["state"],
        row["category"],
        row["country"],
        row["status"]
    ))

    inserted += 1

conn.commit()
conn.close()

print("✅ Inserted:", inserted)