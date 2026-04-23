import requests
from bs4 import BeautifulSoup
import sqlite3
import time

from category_model import predict_category
from scoring import calculate_score


# ---------------- DB ----------------
def get_db_connection():
    return sqlite3.connect("database.db")


# ---------------- STATE EXTRACTION ----------------
def extract_state(text):
    states = [
        "delhi", "maharashtra", "karnataka", "uttar pradesh",
        "tamil nadu", "assam", "bihar", "west bengal",
        "rajasthan", "gujarat", "kerala", "madhya pradesh"
    ]

    text = text.lower()

    for state in states:
        if state in text:
            return state

    return "unknown"


# ---------------- CLEAN TEXT ----------------
def clean_text(text):
    if not text:
        return ""

    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())

    return text[:1000]  # limit length


# ---------------- SCRAPER ----------------
def extract_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=8)

        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")

        # 🔥 TITLE
        title = "Unknown NGO"
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # 🔥 META DESCRIPTION
        description = ""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            description = meta["content"].strip()

        # 🔥 FALLBACK → PARAGRAPHS
        if len(description) < 80:
            paragraphs = soup.find_all("p")
            texts = [p.get_text() for p in paragraphs if len(p.get_text()) > 50]

            if texts:
                description = " ".join(texts[:5])

        description = clean_text(description)

        return title[:100], description

    except Exception as e:
        print("❌ Error:", url, e)
        return None, None


# ---------------- MAIN ----------------
conn = get_db_connection()
cursor = conn.cursor()

# 🔥 Target weak data
cursor.execute("""
    SELECT project_id, url 
    FROM projects
    WHERE source='Web Discovery' OR LENGTH(source) < 50
""")

rows = cursor.fetchall()

updated = 0
skipped = 0

for project_id, url in rows:

    if not url:
        skipped += 1
        continue

    title, description = extract_content(url)

    if not title:
        skipped += 1
        continue

    text = f"{title} {description}"

    # 🔥 STATE DETECTION
    state = extract_state(text)

    # 🔥 CATEGORY
    category = predict_category(text)

    # 🔥 SCORE
    score = calculate_score(category, state, title, description)

    try:
        cursor.execute("""
            UPDATE projects
            SET title=?, source=?, state=?, category=?, score=?
            WHERE project_id=?
        """, (title, description, state, category, score, project_id))

        updated += 1

        if updated % 50 == 0:
            print(f"Updated: {updated}")

        time.sleep(0.5)

    except Exception as e:
        print("❌ DB Error:", e)
        skipped += 1


conn.commit()
conn.close()

print("\n🚀 FINAL DEEP SCRAPER")
print("Updated:", updated)
print("Skipped:", skipped)