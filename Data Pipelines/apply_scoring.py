import sqlite3
from scoring import calculate_score

# ---------------- DB CONNECTION ---------------
def get_db_connection():
    conn = sqlite3.connect("database.db")
    return conn


# ---------------- MAIN SCORING ----------------
def apply_scoring():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Include state (important for scoring)
    cursor.execute("""
        SELECT project_id, title, category, state, url 
        FROM projects
    """)
    rows = cursor.fetchall()

    updated = 0

    for row in rows:
        project_id, title, category, state, url = row

        # Future use (AI/NLP)
        description = ""

        # Handle None values safely
        title = title or ""
        category = category or ""
        state = state or ""

        # 🔥 Calculate score (updated logic)
        score = calculate_score(category, state, title)

        cursor.execute(
            "UPDATE projects SET score = ? WHERE project_id = ?",
            (score, project_id)
        )

        updated += 1

        # Optional: progress print every 100 rows
        if updated % 100 == 0:
            print(f"Processed {updated} records...")

    conn.commit()
    conn.close()

    print(f"✅ Scoring complete. Total updated: {updated}")


# ---------------- RUN --------------
if __name__ == "__main__":
    apply_scoring()