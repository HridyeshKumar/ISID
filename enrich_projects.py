from ddgs import DDGS
import sqlite3
import time

from category_model import predict_category
from scoring import calculate_score


# ---------------- DB ----------------
def get_db_connection():
    return sqlite3.connect("database.db")


# ---------------- FILTER ----------------
def is_valid_url(url):
    if not url:
        return False

    bad = ["facebook", "twitter", "linkedin", ".pdf", "login"]
    return not any(b in url.lower() for b in bad)


# ---------------- MAIN ----------------
conn = get_db_connection()
cursor = conn.cursor()

# 🔥 Find weak or incomplete records
cursor.execute("""
    SELECT project_id, title, url, source 
    FROM projects
    WHERE url = '' OR source = '' OR LENGTH(source) < 50
""")

rows = cursor.fetchall()

updated = 0
skipped = 0

with DDGS() as ddgs:
    for project_id, title, url, source in rows:

        try:
            # 🔍 Search for better info
            results = ddgs.text(title + " NGO India", max_results=5)

            for r in results:
                new_url = r.get("href")
                desc = r.get("body") or ""

                if not is_valid_url(new_url):
                    continue

                # 🔥 Improve text
                text = f"{title} {desc}"

                category = predict_category(text)
                state = "india"
                score = calculate_score(category, state, title, desc)

                cursor.execute("""
                    UPDATE projects
                    SET url=?, source=?, category=?, score=?
                    WHERE project_id=?
                """, (new_url, desc, category, score, project_id))

                updated += 1
                break

            time.sleep(0.3)

        except Exception as e:
            print("Error:", e)
            skipped += 1

conn.commit()
conn.close()

print("\n🚀 FINAL ENRICHMENT")
print("Updated:", updated)
print("Skipped:", skipped)