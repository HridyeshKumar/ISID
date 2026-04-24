import sqlite3
import numpy as np

# 🔥 LAZY MODEL LOAD
model = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        print("🔄 Loading model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model


# ---------------- GLOBAL CACHE ----------------
DATA = []
EMBEDDINGS = None


# ---------------- LOAD DATA ----------------
def load_data():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 🔥 LIMIT DATA (VERY IMPORTANT)
    cursor.execute("""
        SELECT project_id, title, source 
        FROM projects
        ORDER BY score DESC
        LIMIT 1000
    """)

    data = cursor.fetchall()
    conn.close()
    return data


# ---------------- BUILD CACHE ----------------
def build_cache():
    global DATA, EMBEDDINGS

    print("🔄 Building embeddings cache...")

    DATA = load_data()
    texts = [(d["title"] or "") + " " + (d["source"] or "") for d in DATA]

    EMBEDDINGS = get_model().encode(texts, normalize_embeddings=True)

    print(f"✅ Cache built for {len(DATA)} projects")


# ---------------- SEARCH ----------------
def search(query, top_k=10):
    global DATA, EMBEDDINGS

    if EMBEDDINGS is None:
        build_cache()

    q_vec = get_model().encode([query], normalize_embeddings=True)[0]

    scores = []
    for i, emb in enumerate(EMBEDDINGS):
        sim = np.dot(q_vec, emb)
        scores.append((sim, DATA[i]))

    scores.sort(reverse=True)
    return scores[:top_k]


# ---------------- RECOMMEND ----------------
def get_similar_projects(project_id, top_k=5):
    global DATA, EMBEDDINGS

    if EMBEDDINGS is None:
        build_cache()

    idx = None
    for i, d in enumerate(DATA):
        if d["project_id"] == project_id:
            idx = i
            break

    if idx is None:
        return []

    target_vec = EMBEDDINGS[idx]

    scores = []
    for i, emb in enumerate(EMBEDDINGS):
        if i == idx:
            continue
        sim = np.dot(target_vec, emb)
        scores.append((sim, DATA[i]))

    scores.sort(reverse=True)
    return scores[:top_k]