from sentence_transformers import SentenceTransformer
import sqlite3
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

DATA = []
EMBEDDINGS = None


def load_data():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT project_id, title, source FROM projects")
    data = cursor.fetchall()

    conn.close()
    return data


def build_cache():
    global DATA, EMBEDDINGS

    print("🔄 Building embeddings cache...")
    DATA = load_data()

    texts = [(d["title"] or "") + " " + (d["source"] or "") for d in DATA]
    EMBEDDINGS = model.encode(texts, normalize_embeddings=True)

    print(f"✅ Cache built for {len(DATA)} projects")


def search(query, top_k=10):
    global DATA, EMBEDDINGS

    if EMBEDDINGS is None:
        build_cache()

    q_vec = model.encode([query], normalize_embeddings=True)[0]

    scores = []
    for i, emb in enumerate(EMBEDDINGS):
        sim = np.dot(q_vec, emb)
        scores.append((sim, DATA[i]))

    scores.sort(reverse=True)
    return scores[:top_k]


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