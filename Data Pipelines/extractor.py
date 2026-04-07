import requests
from bs4 import BeautifulSoup
import sqlite3

from category_model import predict_category
from scoring import calculate_score


# ---------------- DB ----------------
def get_db_connection():
    return sqlite3.connect("database.db")


# ---------------- SCRAPER ----------------
def extract_info(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)

        soup = BeautifulSoup(res.text, "html.parser")

        # 🔥 Title
        title = soup.title.string.strip() if soup.title and soup.title.string else "Unknown NGO"

        # 🔥 Description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""

        return title, description

    except Exception as e:
        print("❌ Error scraping:", url, "|", e)
        return None, None


# ---------------- MAIN ----------------
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT project_id, url 
    FROM projects 
    WHERE source='Web Discovery'
""")

rows = cursor.fetchall()

updated = 0
skipped = 0

for project_id, url in rows:
    title, description = extract_info(url)

    if not title:
        skipped += 1
        continue

    text = f"{title} {description}"

    # 🔥 AI Category
    category = predict_category(text)

    # 🔥 Score
    score = calculate_score(title, category, description)

    try:
        cursor.execute("""
        UPDATE projects
        SET title = ?, 
            category = ?, 
            score = ?
        WHERE project_id = ?
        """, (title, category, score, project_id))

        updated += 1
        print(f"✅ Updated: {title[:60]}...")

    except Exception as e:
        print("❌ DB Error:", e)
        skipped += 1


conn.commit()
conn.close()

print("\n🎯 Total Updated:", updated)
print("⏭️ Skipped:", skipped)