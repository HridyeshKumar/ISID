import sqlite3
import ast
import statistics

from semantic_search import search
from recommendation_engine import recommend_projects


# ---------------- DATABASE ----------------

conn = sqlite3.connect("database.db")

conn.row_factory = sqlite3.Row

cursor = conn.cursor()


# ---------------- LOAD PROJECTS ----------------

cursor.execute("""

SELECT

    project_id,
    title,
    topics,
    impact_score

FROM projects

LIMIT 100

""")

projects = cursor.fetchall()


# =========================================================
# PRECISION@K
# =========================================================

def precision_at_k(query, expected_topic, k=10):

    results = search(query, top_k=k)

    relevant = 0

    for r in results:

        try:

            topics = ast.literal_eval(
                r["topics"] or "[]"
            )

        except:

            topics = []

        if expected_topic in topics:

            relevant += 1

    precision = relevant / k

    return round(precision, 2)


# =========================================================
# RECOMMENDATION OVERLAP
# =========================================================

def recommendation_quality(project_id):

    recommendations = recommend_projects(project_id)

    if not recommendations:

        return 0

    target = None

    for p in projects:

        if p["project_id"] == project_id:

            target = p
            break

    if not target:

        return 0

    try:

        target_topics = ast.literal_eval(
            target["topics"] or "[]"
        )

    except:

        target_topics = []

    overlaps = []

    for item in recommendations:

        project = item["project"]

        try:

            topics = ast.literal_eval(
                project["topics"] or "[]"
            )

        except:

            topics = []

        overlap = len(

            set(target_topics) &
            set(topics)
        )

        overlaps.append(overlap)

    if not overlaps:

        return 0

    return round(

        statistics.mean(overlaps),

        2
    )


# =========================================================
# IMPACT ANALYTICS
# =========================================================

def impact_statistics():

    scores = []

    for p in projects:

        try:

            score = float(
                p["impact_score"] or 0
            )

            scores.append(score)

        except:

            pass

    return {

        "average": round(
            statistics.mean(scores), 2
        ),

        "highest": max(scores),

        "lowest": min(scores)
    }


# =========================================================
# RUN EVALUATION
# =========================================================

print("\n🚀 ISID EVALUATION REPORT\n")

# ---------------- SEARCH ----------------

precision = precision_at_k(

    "women empowerment education",

    "sdg_gender"
)

print(

    "🎯 Precision@10:",

    precision
)

# ---------------- RECOMMENDATIONS ----------------

quality = recommendation_quality(1)

print(

    "🤖 Recommendation Topic Overlap:",

    quality
)

# ---------------- IMPACT ----------------

stats = impact_statistics()

print("\n📊 IMPACT ANALYTICS")

print(

    "Average Impact:",

    stats["average"]
)

print(

    "Highest Impact:",

    stats["highest"]
)

print(

    "Lowest Impact:",

    stats["lowest"]
)