import pandas as pd
import sqlite3

from ontology import detect_topics
from scoring import calculate_dimension_scores
from location_extractor import extract_locations


# ---------------- DATABASE ----------------

conn = sqlite3.connect("database.db")
cursor = conn.cursor()


# ---------------- LOAD DATASET ----------------

df = pd.read_csv("ngo_dataset.csv")
# ---------------- CLEAN DATA ----------------

df.columns = df.columns.str.strip().str.lower()

# remove empty titles
df = df[df["title"].notna()]

# remove duplicate titles
df = df.drop_duplicates(subset=["title"])

# optional: remove duplicate URLs
df = df.drop_duplicates(subset=["title"])

print("✅ Clean dataset size:", len(df))


# ---------------- COUNTERS ----------------

inserted = 0
skipped = 0


# ---------------- IMPORT LOOP ----------------

for _, row in df.iterrows():

    # SAFE FIELD EXTRACTION

    title = str(row.get("title", "")).strip()

    source = str(
        row.get("source", "dataset")
    ).strip()

    url = str(
        row.get("url", "")
    ).strip()

    state = str(
        row.get("state", "india")
    ).strip()

    category = str(
        row.get("category", "general")
    ).strip()

    country = str(
        row.get("country", "india")
    ).strip()

    status = str(
        row.get("status", "active")
    ).strip()

    description = str(
        row.get("description", "")
    ).strip()

    # SKIP EMPTY TITLES

    if not title:
        skipped += 1
        continue

    # DUPLICATE CHECK

    cursor.execute(
        "SELECT 1 FROM projects WHERE title = ?",
        (title,)
    )

    if cursor.fetchone():
        skipped += 1
        continue

    # ---------------- AI ENRICHMENT ----------------

    text = title + " " + description

    topics = detect_topics(text)

    locations = extract_locations(text)

    scores = calculate_dimension_scores(text)

    # ---------------- INSERT ----------------

    try:

        cursor.execute("""
        INSERT INTO projects (

            title,
            source,
            url,
            state,
            category,
            country,
            status,

            topics,
            detected_locations,

            impact_score,
            innovation_score,
            scale_score,
            sustainability_score,
            collaboration_score

        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            title,
            source,
            url,
            state,
            category,
            country,
            status,

            str(topics),
            str(locations),

            scores["impact_score"],
            scores["innovation_score"],
            scores["scale_score"],
            scores["sustainability_score"],
            scores["collaboration_score"]
        ))

        inserted += 1

        # progress log
        if inserted % 100 == 0:
            print(f"✅ Inserted: {inserted}")

    except Exception as e:

        print("❌ Error:", e)

        skipped += 1


# ---------------- FINALIZE ----------------

conn.commit()
conn.close()

print("\n🚀 IMPORT COMPLETE")
print("✅ Inserted:", inserted)
print("⚠️ Skipped:", skipped)
print("Dataset rows:", len(df))
print(df.head())