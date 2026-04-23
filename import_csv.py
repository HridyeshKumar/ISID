import pandas as pd
import sqlite3

from category_model import predict_category
from scoring import calculate_score


# ---------------- LOAD DATA ----------------
df = pd.read_csv("ngo_dataset.csv")

# Clean column names
df.columns = df.columns.str.strip().str.lower()


# ---------------- DB ----------------
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

inserted = 0
skipped = 0


# ---------------- VALID CATEGORIES ----------------
valid_categories = ["education", "health", "social", "environment", "food"]


# ---------------- INSERT LOOP ----------------
for row in df.itertuples(index=False):

    # SAFE extraction
    title = str(getattr(row, "title", "")).strip()
    source = str(getattr(row, "source", "dataset")).strip()
    url = str(getattr(row, "url", "")).strip()
    state = str(getattr(row, "state", "india")).lower().strip()
    category = str(getattr(row, "category", "")).lower().strip()
    country = str(getattr(row, "country", "india")).lower().strip()
    status = str(getattr(row, "status", "active")).lower().strip()

    if not title:
        skipped += 1
        continue

    # 🔥 STRONG DUPLICATE CHECK
    cursor.execute("""
        SELECT 1 FROM projects 
        WHERE LOWER(title)=? OR url=?
    """, (title.lower(), url))

    if cursor.fetchone():
        skipped += 1
        continue

    # 🔥 CATEGORY FIX
    if category not in valid_categories:
        text = f"{title} {source}"
        category = predict_category(text)

    # 🔥 SCORE (FIXED)
    score = calculate_score(category, state, title, source)

    try:
        cursor.execute("""
            INSERT INTO projects 
            (title, source, url, state, category, country, status, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            source,
            url,
            state,
            category,
            country,
            status,
            score
        ))

        inserted += 1

        if inserted % 100 == 0:
            print(f"Inserted: {inserted}")

    except Exception as e:
        print("❌ Error:", e)
        skipped += 1


# ---------------- FINALIZE ----------------
conn.commit()
conn.close()

print("\n🚀 FINAL DATASET IMPORT")
print("Inserted:", inserted)
print("Skipped:", skipped)