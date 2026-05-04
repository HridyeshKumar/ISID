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
    impact_score

FROM projects

""")

projects = cursor.fetchall()


# ---------------- COUNTERS ----------------

topic_counter = Counter()

location_counter = Counter()

high_impact_topics = Counter()

high_impact_locations = Counter()


# ---------------- PROCESS ----------------

for project in projects:

    try:

        topics = ast.literal_eval(
            str(project["topics"] or "[]")
        )

    except:

        topics = []

    try:

        locations = ast.literal_eval(
            str(project["detected_locations"] or "[]")
        )

    except:

        locations = []

    try:

        impact = float(
            project["impact_score"] or 0
        )

    except:

        impact = 0

    # ---------------- COUNT ----------------

    for topic in topics:

        topic_counter[topic] += 1

        if impact >= 7:

            high_impact_topics[topic] += 1

    for loc in locations:

        if len(loc) > 2:

            location_counter[loc] += 1

            if impact >= 7:

                high_impact_locations[loc] += 1


# ---------------- AI INSIGHTS ----------------

print("\n🚀 AI INSIGHT ENGINE")


# ---------------- TOP SDGs ----------------

print("\n📚 MOST ACTIVE SDGs\n")

for topic, count in topic_counter.most_common(10):

    print(
        f"{topic} -> {count} projects"
    )


# ---------------- HIGH IMPACT SDGs ----------------

print("\n🔥 HIGH IMPACT SDGs\n")

for topic, count in high_impact_topics.most_common(10):

    print(
        f"{topic} -> {count} high-impact projects"
    )


# ---------------- ACTIVE REGIONS ----------------

print("\n🌍 MOST ACTIVE REGIONS\n")

for loc, count in location_counter.most_common(10):

    print(
        f"{loc} -> {count} projects"
    )


# ---------------- HIGH IMPACT REGIONS ----------------

print("\n⭐ HIGH IMPACT REGIONS\n")

for loc, count in high_impact_locations.most_common(10):

    print(
        f"{loc} -> {count} high-impact projects"
    )


# ---------------- UNDERSERVED REGIONS ----------------

print("\n⚠️ UNDERSERVED REGIONS\n")

underserved = []

for loc, count in location_counter.items():

    if count <= 2:

        underserved.append(loc)

underserved = sorted(underserved)

for loc in underserved[:20]:

    print(loc)


# ---------------- STRATEGIC INSIGHTS ----------------

print("\n🧠 STRATEGIC INSIGHTS\n")


# Top SDG
if topic_counter:

    top_sdg = topic_counter.most_common(1)[0]

    print(

        f"Most active SDG ecosystem: "
        f"{top_sdg[0]} "
        f"({top_sdg[1]} projects)"
    )


# Top region
if location_counter:

    top_region = location_counter.most_common(1)[0]

    print(

        f"Most active ecosystem region: "
        f"{top_region[0]} "
        f"({top_region[1]} projects)"
    )


# High impact ecosystem
if high_impact_topics:

    best_topic = high_impact_topics.most_common(1)[0]

    print(

        f"Strongest high-impact ecosystem: "
        f"{best_topic[0]}"
    )


# Underserved count
print(

    f"Potential underserved regions detected: "
    f"{len(underserved)}"
)


# ---------------- TOTAL STATS ----------------

print("\n📊 TOTAL ECOSYSTEM STATS\n")

print(
    "Total Projects:",
    len(projects)
)

print(
    "Unique SDGs:",
    len(topic_counter)
)

print(
    "Unique Locations:",
    len(location_counter)
)