import os
os.environ["DDGS_HEADERS"] = "Mozilla/5.0"

from ddgs import DDGS
import sqlite3
import time
from urllib.parse import urlparse

from category_model import predict_category
from scoring import calculate_score


# ---------------- DB ----------------
def get_db_connection():
    return sqlite3.connect("database.db")


# ---------------- CLEAN TITLE ----------------
def extract_title(title, url):
    if title:
        return title[:80]

    domain = urlparse(url).netloc.replace("www.", "")
    return domain.split(".")[0][:50]


# ---------------- FILTER ----------------
def is_valid_url(url):
    if not url:
        return False

    bad_keywords = [
        "facebook", "twitter", "linkedin",
        "youtube", "instagram",
        ".pdf", "login", "signup", "donate"
    ]

    if any(bad in url.lower() for bad in bad_keywords):
        return False

    # 🔥 keep NGO-like domains
    good_domains = [".org", ".ngo", ".in"]
    if not any(g in url for g in good_domains):
        return False

    return True


# ---------------- ADVANCED QUERIES ----------------
queries = [
    # Core NGOs
    "list of NGOs in India with website",
    "top NGOs in India education health",
    "NGO directory India official websites",
    "NGOs in Assam India",
    "NGOs in Bihar rural development",
    "NGOs in Kerala health projects",
    "NGOs in Northeast India",
    # Sector-based
    "education NGOs India projects",
    "health NGOs India projects",
    "environment NGOs India sustainability",
    "women empowerment NGOs India",
    "child welfare NGOs India",

    # Development
    "rural development NGOs India",
    "village development projects India NGO",

    # Innovation
    "social innovation projects India NGOs",
    "social enterprises India NGO projects",

    # Climate
    "climate change NGOs India projects",
    "sustainability NGOs India renewable energy",

    # CSR + Government
    "CSR projects India NGOs collaboration",
    "government social schemes India NGOs",

    # Global but India
    "international NGOs working in India projects",
]


# ---------------- SCRAPING ----------------
websites = set()

with DDGS() as ddgs:
    for q in queries:
        print(f"\n🔍 Searching: {q}")

        # 🔥 run multiple times (important trick)
        for _ in range(3):
            try:
                results = ddgs.text(q + " India NGO", max_results=50)

                for r in results:
                    url = r.get("href")
                    title = r.get("title")
                    desc = r.get("body") or ""

                    if not is_valid_url(url):
                        continue

                    websites.add((url, title, desc))

                time.sleep(1)

            except Exception as e:
                print("Error:", e)

print(f"\n🌐 Total unique websites found: {len(websites)}")


# ---------------- STORE ----------------
conn = get_db_connection()
cursor = conn.cursor()

inserted = 0
skipped = 0

for url, title, desc in websites:

    # 🔥 DUPLICATE CHECK
    cursor.execute("SELECT 1 FROM projects WHERE url = ?", (url,))
    if cursor.fetchone():
        skipped += 1
        continue

    title = extract_title(title, url)

    # 🔥 AI TEXT
    text = title + " " + desc

    category = predict_category(text)
    state = "india"

    score = calculate_score(category, state, title, desc)

    try:
        cursor.execute("""
            INSERT INTO projects 
            (title, source, url, state, category, country, status, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            desc[:500],  # 🔥 better than "Web Discovery"
            url,
            state,
            category,
            "india",
            "active",
            score
        ))

        inserted += 1

        if inserted % 50 == 0:
            print(f"Inserted: {inserted}")

    except Exception as e:
        print("Error inserting:", url, e)
        skipped += 1


conn.commit()
conn.close()

print("\n🚀 FINAL STATS")
print("Inserted:", inserted)
print("Skipped:", skipped)