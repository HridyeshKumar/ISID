import sqlite3
import re
import networkx as nx


# ---------------- DATABASE ----------------

conn = sqlite3.connect("database.db")

conn.row_factory = sqlite3.Row

cursor = conn.cursor()


# ---------------- LOAD PROJECTS ----------------

cursor.execute("""

SELECT

    project_id,
    title,
    source,
    detected_locations,
    topics

FROM projects

""")

projects = cursor.fetchall()


# ---------------- ACTOR KEYWORDS ----------------

ACTOR_PATTERNS = {

    "government": [

        "government",
        "ministry",
        "municipal",
        "state government",
        "central government"
    ],

    "university": [

        "university",
        "college",
        "iit",
        "research institute"
    ],

    "csr": [

        "csr",
        "corporate social responsibility",
        "foundation"
    ],

    "ngo": [

        "ngo",
        "non-profit",
        "nonprofit",
        "charity"
    ]
}


# ---------------- GRAPH ----------------

G = nx.Graph()


# ---------------- CLEAN TEXT ----------------

def clean_text(text):

    text = re.sub(

        r'\s+',

        ' ',

        str(text)
    )

    return text.strip()


# ---------------- DETECT ACTORS ----------------

def detect_actors(text):

    text = str(text).lower()

    found = []

    for actor_type, keywords in ACTOR_PATTERNS.items():

        for keyword in keywords:

            if keyword in text:

                found.append(actor_type)

                break

    return found


# ---------------- BUILD NETWORK ----------------

for project in projects:

    project_name = clean_text(
        project["title"]
    )

    project_node = f"PROJECT::{project_name}"

    G.add_node(

        project_node,

        type="project"
    )

    # ---------------- ACTORS ----------------

    actors = detect_actors(

        project["source"]
    )

    for actor in actors:

        actor_node = f"ACTOR::{actor}"

        G.add_node(

            actor_node,

            type="actor"
        )

        G.add_edge(

            project_node,

            actor_node
        )

    # ---------------- LOCATIONS ----------------

    locations = str(

        project["detected_locations"] or ""

    ).replace("[", "").replace("]", "")

    for loc in locations.split(","):

        loc = loc.strip().replace("'", "")

        if len(loc) > 2:

            location_node = f"LOCATION::{loc}"

            G.add_node(

                location_node,

                type="location"
            )

            G.add_edge(

                project_node,

                location_node
            )

    # ---------------- TOPICS ----------------

    topics = str(

        project["topics"] or ""

    ).replace("[", "").replace("]", "")

    for topic in topics.split(","):

        topic = topic.strip().replace("'", "")

        if len(topic) > 2:

            topic_node = f"TOPIC::{topic}"

            G.add_node(

                topic_node,

                type="topic"
            )

            G.add_edge(

                project_node,

                topic_node
            )


# ---------------- PROJECT SIMILARITY LINKS ----------------

project_list = list(projects)

STOPWORDS = {

    "india",
    "ngo",
    "foundation",
    "project",
    "development",
    "rural",
    "women",
    "education",
    "health",
    "empowerment",
    "organization",
    "initiative",
    "program",
    "social",
    "support",
    "indian",
    "community",
    "digital",
    "children",
    "trust",
    "society",
    "mission",
    "association"
}

for i in range(len(project_list)):

    p1 = project_list[i]

    title1 = str(p1["title"] or "").lower()

    # ---------------- SKIP SYNTHETIC PROJECTS ----------------

    if "ngo foundation" in title1:

        continue

    topics1 = {

        t.strip().lower()

        for t in str(
            p1["topics"] or ""
        ).split(",")

        if t.strip()
    }

    locations1 = {

        l.strip().lower()

        for l in str(
            p1["detected_locations"] or ""
        ).split(",")

        if l.strip()
    }

    words1 = {

        w.lower()

        for w in re.findall(
            r'\b[a-zA-Z]{5,}\b',
            title1
        )

        if w.lower() not in STOPWORDS
    }

    for j in range(i + 1, len(project_list)):

        p2 = project_list[j]

        title2 = str(
            p2["title"] or ""
        ).lower()

        # ---------------- SKIP SYNTHETIC PROJECTS ----------------

        if "ngo foundation" in title2:

            continue

        topics2 = {

            t.strip().lower()

            for t in str(
                p2["topics"] or ""
            ).split(",")

            if t.strip()
        }

        locations2 = {

            l.strip().lower()

            for l in str(
                p2["detected_locations"] or ""
            ).split(",")

            if l.strip()
        }

        words2 = {

            w.lower()

            for w in re.findall(
                r'\b[a-zA-Z]{5,}\b',
                title2
            )

            if w.lower() not in STOPWORDS
        }

        # ---------------- OVERLAPS ----------------

        topic_overlap = topics1.intersection(
            topics2
        )

        location_overlap = locations1.intersection(
            locations2
        )

        word_overlap = words1.intersection(
            words2
        )

        # ---------------- REMOVE WEAK LOCATIONS ----------------

        location_overlap = {

            l for l in location_overlap

            if l not in {
                "india",
                "delhi",
                "goa"
            }
        }

        # ---------------- STRICT FILTER ----------------

        similarity = 0

        similarity += len(topic_overlap) * 4
        similarity += len(location_overlap) * 3
        similarity += len(word_overlap) * 2

        # ---------------- REQUIRE STRONG SIGNAL ----------------

        strong_topic_match = len(topic_overlap) >= 2
        strong_word_match = len(word_overlap) >= 2

        if similarity >= 10 and (

            strong_topic_match or
            strong_word_match

        ):

            p1_node = f"PROJECT::{p1['title']}"
            p2_node = f"PROJECT::{p2['title']}"

            G.add_edge(

                p1_node,
                p2_node,
                weight=similarity
            )

# ---------------- OUTPUT ----------------

print("\n🚀 NETWORK GRAPH BUILT")

print(
    "📊 Total Nodes:",
    G.number_of_nodes()
)

print(
    "🔗 Total Connections:",
    G.number_of_edges()
)


# ---------------- SAMPLE CONNECTIONS ----------------

print("\n📌 SAMPLE NETWORKS\n")

count = 0

for node in G.nodes():

    neighbors = list(

        G.neighbors(node)
    )

    if neighbors:

        print(node)

        print(" → ", neighbors[:5])

        print()

        count += 1

    if count >= 10:

        break