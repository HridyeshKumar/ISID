import pandas as pd
import sqlite3

from category_model import predict_category
from scoring import calculate_score


# ---------------- LOAD DATA ----------------
df = pd.read_csv("ngo_dataset.csv")

# Clean column names (avoid hidden issues)
df.columns = df.columns.str.strip().str.lower()


# ---------------- DB ----------------
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

inserted = 0
skipped = 0


# ---------------- INSERT LOOP ----------------
for _, row in df.iterrows():
    # Safe extraction (handle missing values)
    title = str(row.get("title", "")).strip()
    source = str(row.get("source", "dataset")).strip()
    url = str(row.get("url", "")).strip()
    state = str(row.get("state", "india")).lower().strip()
    category = str(row.get("category", "")).lower().strip()
    country = str(row.get("country", "india")).lower().strip()
    status = str(row.get("status", "active")).lower().strip()

    # Skip empty titles
    if not title:
        skipped += 1
        continue

    # 🔥 Duplicate check (title + url)
    cursor.execute(
        "SELECT 1 FROM projects WHERE title = ? OR url = ?",
        (title, url)
    )
    if cursor.fetchone():
        skipped += 1
        continue

    # 🔥 AI Category (if missing or bad)
    valid_categories = ["education", "health", "social", "environment", "food"]
    if category not in valid_categories:
        category = predict_category(title)

    # 🔥 Score
    score = calculate_score(title, category, "")

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

        # Progress log
        if inserted % 100 == 0:
            print(f"Inserted {inserted} records...")

    except Exception as e:
        print("❌ Error:", e)
        skipped += 1


# ---------------- FINALIZE ----------------
conn.commit()
conn.close()

print("\n✅ Inserted:", inserted)
print("⏭️ Skipped:", skipped)