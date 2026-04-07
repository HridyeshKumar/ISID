import os
os.environ["DDGS_HEADERS"] = "Mozilla/5.0"

from ddgs import DDGS
import sqlite3

def get_db_connection():
    return sqlite3.connect("database.db")

queries = [
    "education NGO India",
    "health NGO Delhi",
    "women empowerment NGO India",
    "rural development NGO India"
]

websites = set()

with DDGS() as ddgs:
    for q in queries:
        print(f"Searching: {q}")

        results = ddgs.text(q, max_results=20)

        for r in results:
            link = r.get("href")

            if not link:
                continue

            if any(x in link for x in ["facebook", "twitter", "linkedin", "youtube", ".pdf"]):
                continue

            websites.add(link)

print("Total websites found:", len(websites))

# 🔥 STORE
conn = get_db_connection()
cursor = conn.cursor()

inserted = 0

for site in websites:
    title = site.split("//")[-1][:50]

    cursor.execute("SELECT 1 FROM projects WHERE url = ?", (site,))
    if cursor.fetchone():
        continue

    cursor.execute("""
        INSERT INTO projects (title, source, url, state, category, country, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        "Web Discovery",
        site,
        "unknown",
        "general",
        "india",
        "active"
    ))

    inserted += 1

conn.commit()
conn.close()

print("Inserted:", inserted)