import sqlite3
from collections import Counter
import ast


# ---------------- DATABASE ----------------

conn = sqlite3.connect("database.db")

conn.row_factory = sqlite3.Row

cursor = conn.cursor()


# ---------------- LOAD DATA ----------------

cursor.execute("""

SELECT

    topics,
    detected_locations,
    impact_score

FROM projects

""")

projects = cursor.fetchall()


# ---------------- COUNTERS ----------------

topic_counter = Counter()

location_counter = Counter()

impact_scores = []


# ---------------- PROCESS PROJECTS ----------------

for project in projects:

    # ---------------- TOPICS ----------------

    try:

        topics = ast.literal_eval(
            str(project["topics"] or "[]")
        )

        for topic in topics:

            topic_counter[topic] += 1

    except:
        pass

    # ---------------- LOCATIONS ----------------

    try:

        locations = ast.literal_eval(
            str(project["detected_locations"] or "[]")
        )

        for loc in locations:

            if len(loc) > 2:

                location_counter[loc] += 1

    except:
        pass

    # ---------------- IMPACT ----------------

    try:

        impact_scores.append(
            float(project["impact_score"] or 0)
        )

    except:
        pass


# ---------------- RESULTS ----------------

print("\n🚀 DASHBOARD ANALYTICS")


# ---------------- TOP SDGs ----------------

print("\n📚 TOP SDGs\n")

for topic, count in topic_counter.most_common(10):

    print(
        f"{topic} -> {count}"
    )


# ---------------- TOP LOCATIONS ----------------

print("\n🌍 TOP LOCATIONS\n")

for loc, count in location_counter.most_common(10):

    print(
        f"{loc} -> {count}"
    )


# ---------------- IMPACT ANALYTICS ----------------

if impact_scores:

    avg_impact = sum(
        impact_scores
    ) / len(impact_scores)

    max_impact = max(
        impact_scores
    )

    min_impact = min(
        impact_scores
    )

    print("\n⭐ IMPACT ANALYTICS\n")

    print(
        "Average Impact:",
        round(avg_impact, 2)
    )

    print(
        "Highest Impact:",
        round(max_impact, 2)
    )

    print(
        "Lowest Impact:",
        round(min_impact, 2)
    )


# ---------------- TOTAL STATS ----------------

print("\n📊 PLATFORM STATS\n")

print(
    "Total Projects:",
    len(projects)
)

print(
    "Unique Topics:",
    len(topic_counter)
)

print(
    "Unique Locations:",
    len(location_counter)
)