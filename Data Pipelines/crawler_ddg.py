import os
os.environ["DDGS_HEADERS"] = "Mozilla/5.0"

from ddgs import DDGS
import sqlite3
from urllib.parse import urlparse

# 🔥 Import your ML + scoring
from category_model import predict_category
from scoring import calculate_score


# ---------------- DB ----------------
def get_db_connection():
    return sqlite3.connect("database.db")


# ---------------- CLEAN TITLE ----------------
def extract_title_from_url(url):
    domain = urlparse(url).netloc
    domain = domain.replace("www.", "")
    return domain[:50]


# ---------------- FILTER ----------------
def is_valid_url(url):
    if not url:
        return False

    bad_keywords = [
        "facebook", "twitter", "linkedin",
        "youtube", "instagram",
        ".pdf", "login", "signup"
    ]

    return not any(bad in url.lower() for bad in bad_keywords)


# ---------------- QUERIES ----------------
queries = [
    "education NGO India",
    "health NGO Delhi",
    "women empowerment NGO India",
    "rural development NGO India",
    "food NGO India",
    "child welfare NGO India"
]


# ---------------- SCRAPING ----------------
websites = set()

with DDGS() as ddgs:
    for q in queries:
        print(f"\n🔍 Searching: {q}")

        results = ddgs.text(q, max_results=25)

        for r in results:
            link = r.get("href")

            if not is_valid_url(link):
                continue

            websites.add(link)

print(f"\n🌐 Total unique websites found: {len(websites)}")


# ---------------- STORE ----------------
conn = get_db_connection()
cursor = conn.cursor()

inserted = 0
skipped = 0

for site in websites:
    # Check duplicate
    cursor.execute("SELECT 1 FROM projects WHERE url = ?", (site,))
    if cursor.fetchone():
        skipped += 1
        continue

    title = extract_title_from_url(site)

    # 🔥 AI Category
    category = predict_category(title)

    # Default state (can improve later)
    state = "india"

    # 🔥 Score
    score = calculate_score(category, state, title)

    try:
        cursor.execute("""
            INSERT INTO projects 
            (title, source, url, state, category, country, status, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            "Web Discovery",
            site,
            state,
            category,
            "india",
            "active",
            score
        ))

        inserted += 1

    except Exception as e:
        print("Error inserting:", site, e)
        skipped += 1


conn.commit()
conn.close()

print("\n✅ Inserted:", inserted)
print("⏭️ Skipped (duplicates/errors):", skipped)