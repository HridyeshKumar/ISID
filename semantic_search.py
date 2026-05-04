from sentence_transformers import SentenceTransformer
import sqlite3
import numpy as np
import faiss


# ---------------- MODEL ----------------

model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)


# ---------------- CACHE ----------------

cached_data = None
cached_embeddings = None
faiss_index = None


# ---------------- LOAD DATA ----------------

def load_data():

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        project_id,
        title,
        source,
        topics,
        detected_locations,
        impact_score,
        innovation_score,
        sustainability_score
    FROM projects
    """)

    rows = cursor.fetchall()

    conn.close()

    # convert sqlite rows -> dicts

    data = [

        dict(row)

        for row in rows
    ]

    return data


# ---------------- BUILD CACHE ----------------

def build_cache():

    global cached_data
    global cached_embeddings
    global faiss_index

    print("🚀 Building semantic cache...")

    cached_data = load_data()

    texts = []

    for d in cached_data:

        text = (

            str(d["title"] or "") + " " +
            str(d["source"] or "") + " " +
            str(d["topics"] or "") + " " +
            str(d["detected_locations"] or "") + " " +
            str(d["impact_score"] or "") + " " +
            str(d["innovation_score"] or "") + " " +
            str(d["sustainability_score"] or "")
        )

        texts.append(text)

    # ---------------- EMBEDDINGS ----------------

    cached_embeddings = model.encode(

        texts,

        normalize_embeddings=True
    )

    vectors = np.array(

        cached_embeddings

    ).astype("float32")

    # ---------------- FAISS INDEX ----------------

    faiss_index = faiss.IndexFlatL2(

        vectors.shape[1]
    )

    faiss_index.add(vectors)

    print("✅ Cache built")

    print(
        "📊 Total projects:",
        len(cached_data)
    )


# ---------------- SEARCH ----------------

def search(query, top_k=10):

    global faiss_index

    if faiss_index is None:

        build_cache()

    # ---------------- QUERY VECTOR ----------------

    q_vec = model.encode(

        [query],

        normalize_embeddings=True

    ).astype("float32")

    D, I = faiss_index.search(

        q_vec,

        top_k * 3
    )

    query_lower = query.lower()

    ranked_results = []

    # ---------------- HYBRID RANKING ----------------

    for rank, idx in enumerate(I[0]):

        if idx >= len(cached_data):

            continue

        project = dict(cached_data[idx])

        # ---------------- SEMANTIC SCORE ----------------

        semantic_score = 1 / (

            1 + D[0][rank]
        )

        # ---------------- IMPACT SCORE ----------------

        impact_score = float(

            project["impact_score"] or 0
        ) / 10

        # ---------------- TOPIC BONUS ----------------

        topic_bonus = 0

        topics = str(

            project["topics"] or ""

        ).lower()

        if any(

            word in topics

            for word in query_lower.split()

        ):

            topic_bonus = 0.1

        # ---------------- LOCATION BONUS ----------------

        location_bonus = 0

        locations = str(

            project["detected_locations"] or ""

        ).lower()

        if any(

            word in locations

            for word in query_lower.split()

        ):

            location_bonus = 0.1

        # ---------------- FINAL SCORE ----------------

        final_score = (

            semantic_score * 0.65 +

            impact_score * 0.25 +

            topic_bonus +

            location_bonus
        )

        ranked_results.append(

            (final_score, project)
        )

    # ---------------- SORT RESULTS ----------------

    ranked_results.sort(

        key=lambda x: x[0],

        reverse=True
    )

    # ---------------- RETURN ----------------

    return [

        r[1]

        for r in ranked_results[:top_k]
    ]


# ---------------- GET SIMILAR PROJECTS ----------------

def get_similar_projects(project_id, top_k=10):

    """
    Find similar projects
    based on semantic similarity.
    """

    global faiss_index
    global cached_data

    if faiss_index is None:

        build_cache()

    # ---------------- FIND TARGET PROJECT ----------------

    target_project = None
    target_idx = None

    for idx, project in enumerate(cached_data):

        if project["project_id"] == project_id:

            target_project = project
            target_idx = idx

            break

    if target_project is None:

        return []

    # ---------------- SAFE FIELDS ----------------

    title = str(

        target_project["title"] or ""
    )

    source = str(

        target_project["source"] or ""
    )

    topics = str(

        target_project["topics"] or ""
    )

    locations = str(

        target_project["detected_locations"] or ""
    )

    impact = str(

        target_project["impact_score"] or ""
    )

    innovation = str(

        target_project["innovation_score"] or ""
    )

    sustainability = str(

        target_project["sustainability_score"] or ""
    )

    # ---------------- BUILD QUERY ----------------

    query_text = f"""

    {title}

    {source}

    {topics}

    {locations}

    Impact {impact}

    Innovation {innovation}

    Sustainability {sustainability}

    """

    # ---------------- ENCODE ----------------

    q_vec = model.encode(

        [query_text],

        normalize_embeddings=True

    ).astype("float32")

    # ---------------- SEARCH ----------------

    D, I = faiss_index.search(

        q_vec,

        top_k + 5
    )

    results = []

    for idx in I[0]:

        # skip same project

        if idx == target_idx:

            continue

        if idx >= len(cached_data):

            continue

        similar_project = dict(cached_data[idx])

        similar_project["explanations"] = explain_similarity(
            target_project,
            similar_project
        )

        results.append(similar_project)

        if len(results) >= top_k:

            break

    return results
def explain_similarity(project1, project2):

    reasons = []

    # ---------------- TOPICS ----------------

    topics1 = str(
        project1["topics"] or ""
    ).lower()

    topics2 = str(
        project2["topics"] or ""
    ).lower()

    for topic in topics1.split(","):

        topic = topic.strip()

        if topic and topic in topics2:

            reasons.append(
                f"Shared topic: {topic}"
            )

    # ---------------- LOCATIONS ----------------

    loc1 = str(
        project1["detected_locations"] or ""
    ).lower()

    loc2 = str(
        project2["detected_locations"] or ""
    ).lower()

    for loc in loc1.split(","):

        loc = loc.strip()

        if loc and loc in loc2:

            reasons.append(
                f"Shared location: {loc}"
            )

    # ---------------- IMPACT SCORE ----------------

    try:

        score_diff = abs(
            float(project1["impact_score"] or 0)
            -
            float(project2["impact_score"] or 0)
        )

        if score_diff <= 2:

            reasons.append(
                "Similar impact level"
            )

    except:
        pass

    if not reasons:

        reasons.append(
            "Semantic similarity match"
        )

    return reasons

# ---------------- TEST ----------------

if __name__ == "__main__":

    build_cache()

    results = search(

        "women empowerment education"
    )

    for r in results:

        print(
            "\n📌",
            r["title"]
        )

        print(
            "🌍",
            r["detected_locations"]
        )

        print(
            "📚",
            r["topics"]
        )

        print(
            "⭐ Impact:",
            r["impact_score"]
        )