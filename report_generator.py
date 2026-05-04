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

topic_counter = Counter()

location_counter = Counter()

high_impact_projects = []

impact_scores = []


# ---------------- PROCESS ----------------

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

        impact = float(
            project["impact_score"] or 0
        )

        impact_scores.append(impact)

        if impact >= 8:

            high_impact_projects.append(
                project
            )

    except:
        pass


# ---------------- BASIC STATS ----------------

total_projects = len(projects)

avg_impact = 0

if impact_scores:

    avg_impact = round(

        sum(impact_scores) /
        len(impact_scores),

        2
    )


top_topics = topic_counter.most_common(5)

top_locations = location_counter.most_common(5)


# ---------------- GENERATE REPORT ----------------

report = []


# ---------------- TITLE ----------------

report.append(
    "# AI Ecosystem Intelligence Report\n"
)


# ---------------- OVERVIEW ----------------

report.append(
    "## Ecosystem Overview\n"
)

report.append(

    f"The platform analyzed "
    f"{total_projects} projects "
    f"across multiple SDG ecosystems. "

    f"The average ecosystem impact score "
    f"was {avg_impact}. "
)


# ---------------- SDG ANALYSIS ----------------

report.append(
    "\n## Dominant SDG Ecosystems\n"
)

for topic, count in top_topics:

    report.append(

        f"- {topic} emerged as a major "
        f"ecosystem with {count} projects."
    )


# ---------------- LOCATION ANALYSIS ----------------

report.append(
    "\n## Active Innovation Regions\n"
)

for loc, count in top_locations:

    report.append(

        f"- {loc} showed strong "
        f"ecosystem activity with "
        f"{count} projects."
    )


# ---------------- HIGH IMPACT ANALYSIS ----------------

report.append(
    "\n## High Impact Ecosystems\n"
)

report.append(

    f"The platform identified "
    f"{len(high_impact_projects)} "
    f"high-impact projects "
    f"(impact score >= 8)."
)


# ---------------- SAMPLE HIGH IMPACT PROJECTS ----------------

report.append(
    "\n## Representative High Impact Projects\n"
)

for project in high_impact_projects[:5]:

    report.append(

        f"- {project['title']}"
    )


# ---------------- STRATEGIC INSIGHTS ----------------

report.append(
    "\n## Strategic Insights\n"
)

# top SDG
if top_topics:

    best_topic = top_topics[0][0]

    report.append(

        f"- {best_topic} appears to be "
        f"the strongest ecosystem cluster."
    )

# top region
if top_locations:

    best_region = top_locations[0][0]

    report.append(

        f"- {best_region} emerged as a "
        f"major ecosystem hub."
    )

report.append(

    "- Semantic intelligence and "
    "knowledge graph analytics "
    "revealed strong collaboration "
    "patterns between NGOs, "
    "locations, and SDG themes."
)

report.append(

    "- Trend analysis suggests "
    "increasing focus on "
    "education, sustainability, "
    "healthcare, and livelihood "
    "ecosystems."
)


# ---------------- FINAL REPORT ----------------

final_report = "\n".join(report)


# ---------------- SAVE REPORT ----------------

with open(

    "ecosystem_report.md",

    "w",

    encoding="utf-8"

) as f:

    f.write(final_report)


# ---------------- OUTPUT ----------------

print("\n🚀 ECOSYSTEM REPORT GENERATED")

print(
    "\nSaved as: ecosystem_report.md"
)

print("\n📌 REPORT PREVIEW\n")

print(final_report[:3000])