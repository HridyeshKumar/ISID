import sqlite3
import ast
from collections import Counter


# ---------------- DATABASE ----------------

conn = sqlite3.connect("database.db")

conn.row_factory = sqlite3.Row

cursor = conn.cursor()


# ---------------- LOAD PROJECTS ----------------

cursor.execute("""

SELECT

    title,
    topics,
    detected_locations,
    impact_score,
    summary

FROM projects

""")

projects = cursor.fetchall()


# ---------------- COUNTERS ----------------

keyword_counter = Counter()

topic_counter = Counter()

location_counter = Counter()

high_impact_keywords = Counter()


# ---------------- TREND KEYWORDS ----------------

TREND_KEYWORDS = [

    "ai",
    "digital",
    "climate",
    "women",
    "health",
    "education",
    "sustainability",
    "startup",
    "innovation",
    "rural",
    "livelihood",
    "csr",
    "technology",
    "water",
    "agriculture"
]


# ---------------- PROCESS ----------------

for project in projects:

    text = (

        str(project["title"] or "") + " " +
        str(project["summary"] or "")
    ).lower()

    try:

        impact = float(
            project["impact_score"] or 0
        )

    except:

        impact = 0

    # ---------------- KEYWORDS ----------------

    for keyword in TREND_KEYWORDS:

        if keyword in text:

            keyword_counter[keyword] += 1

            if impact >= 7:

                high_impact_keywords[keyword] += 1

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

            location_counter[loc] += 1

    except:
        pass


# ---------------- OUTPUT ----------------

print("\n🚀 TREND ANALYSIS ENGINE")


# ---------------- TRENDING KEYWORDS ----------------

print("\n🔥 TRENDING THEMES\n")

for keyword, count in keyword_counter.most_common(15):

    print(
        f"{keyword} -> {count}"
    )


# ---------------- HIGH IMPACT TRENDS ----------------

print("\n⭐ HIGH IMPACT TRENDS\n")

for keyword, count in high_impact_keywords.most_common(15):

    print(
        f"{keyword} -> {count}"
    )


# ---------------- TRENDING SDGs ----------------

print("\n📚 TRENDING SDGs\n")

for topic, count in topic_counter.most_common(10):

    print(
        f"{topic} -> {count}"
    )


# ---------------- TRENDING LOCATIONS ----------------

print("\n🌍 TRENDING REGIONS\n")

for loc, count in location_counter.most_common(10):

    print(
        f"{loc} -> {count}"
    )


# ---------------- AI INSIGHTS ----------------

print("\n🧠 AI TREND INSIGHTS\n")


if keyword_counter:

    top_keyword = keyword_counter.most_common(1)[0]

    print(

        f"Fastest growing ecosystem theme: "
        f"{top_keyword[0]}"
    )


if high_impact_keywords:

    top_high_impact = high_impact_keywords.most_common(1)[0]

    print(

        f"Most successful high-impact trend: "
        f"{top_high_impact[0]}"
    )


if topic_counter:

    top_topic = topic_counter.most_common(1)[0]

    print(

        f"Dominant SDG ecosystem: "
        f"{top_topic[0]}"
    )


if location_counter:

    top_location = location_counter.most_common(1)[0]

    print(

        f"Most active innovation region: "
        f"{top_location[0]}"
    )