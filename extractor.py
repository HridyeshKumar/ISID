import requests
from bs4 import BeautifulSoup
import sqlite3
from classifier import predict_category
def get_db_connection():
    return sqlite3.connect("database.db")

def extract_info(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)

        soup = BeautifulSoup(res.text, "html.parser")

        # 🔥 title
        title = soup.title.string.strip() if soup.title else "Unknown NGO"

        # 🔥 description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag["content"] if desc_tag else ""

        return title, description

    except:
        return None, None


conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT project_id, url FROM projects WHERE source='Web Discovery'")
rows = cursor.fetchall()

updated = 0

for project_id, url in rows:
    title, description = extract_info(url)

    if not title:
        continue

    # 🔥 basic category detection
    text = (title + " " + description)
    category = predict_category(text)

    cursor.execute("""
    UPDATE projects
    SET category = 'general'
    WHERE category NOT IN ('education','health','women','environment','food','rural','child','skill')
    AND project_id = ?
    """, (project_id,))

    updated += 1
    print("Updated:", title)

conn.commit()
conn.close()

print("✅ Total enriched:", updated)