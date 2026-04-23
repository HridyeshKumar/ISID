from flask import Flask, request, render_template, redirect
import sqlite3
from semantic_search import search,get_similar_projects,build_cache

app = Flask(__name__)

# ---------------- DB CONNECTION ----------------
def get_db_connection():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- INIT DB ----------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        source TEXT,
        url TEXT,
        state TEXT,
        category TEXT,
        country TEXT,
        status TEXT,
        score INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# ---------------- SEED DATA ----------------
def seed_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM projects")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("""
        INSERT INTO projects (title, source, url, state, category, country, status, score)
        VALUES
        ('Pratham', 'Education NGO', 'https://pratham.org', 'delhi', 'education', 'india', 'active', 40),
        ('Goonj', 'Rural NGO', 'https://goonj.org', 'delhi', 'social', 'india', 'active', 30),
        ('Akshaya Patra', 'Midday Meals', 'https://akshayapatra.org', 'karnataka', 'food', 'india', 'active', 35),
        ('Teach For India', 'Education NGO', 'https://teachforindia.org', 'maharashtra', 'education', 'india', 'active', 45)
        """)
        conn.commit()

    conn.close()


# ---------------- SCORING FUNCTION ----------------
def calculate_score(category, state, title):
    score = 0

    weights = {
        "education": 30,
        "food": 25,
        "social": 20,
        "health": 28
    }
    score += weights.get(category, 10)

    high_priority_states = ["delhi", "maharashtra", "karnataka"]
    if state in high_priority_states:
        score += 10

    title = (title or "").lower()

    keywords = {
        "child": 10,
        "children": 10,
        "women": 10,
        "rural": 6,
        "health": 8,
        "education": 8,
        "hunger": 9,
        "poverty": 9,
        "development": 5
    }

    for word, value in keywords.items():
        if word in title:
            score += value

    return score


def recalculate_all_scores():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    for p in projects:
        new_score = calculate_score(p["category"], p["state"], p["title"])

        cursor.execute(
            "UPDATE projects SET score=? WHERE project_id=?",
            (new_score, p["project_id"])
        )

    conn.commit()
    conn.close()


# INIT
init_db()
seed_data()
recalculate_all_scores()
# 🔥 BUILD CACHE
try:
    print("🔄 Initializing AI search cache...")
    build_cache()
except Exception as e:
    print("⚠️ Cache build failed:", e)
# ---------------- HOME + FILTER ----------------
@app.route("/")
@app.route("/home")
def home():
    query = request.args.get("q", "").lower()
    state = request.args.get("state", "").lower()
    category = request.args.get("category", "").lower()
    status = request.args.get("status", "").lower()
    page = int(request.args.get("page", 1))

    limit = 5
    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM projects WHERE 1=1"
    params = []

    min_score = request.args.get("min_score")
    if min_score:
        sql += " AND score >= ?"
        params.append(int(min_score))

    if query:
        results = search(query)
        data = [r[1] for r in results]

        # still need dropdowns
        cursor.execute("SELECT DISTINCT state FROM projects")
        states = sorted([row[0] for row in cursor.fetchall() if row[0]])

        cursor.execute("SELECT DISTINCT category FROM projects")
        categories = sorted([row[0] for row in cursor.fetchall() if row[0]])

        conn.close()

        return render_template(
            "home.html",
            data=data,
            states=states,
            categories=categories,
            page=1
        )

    if state:
        sql += " AND LOWER(state) LIKE ?"
        params.append("%" + state + "%")

    if category:
        sql += " AND LOWER(category) LIKE ?"
        params.append("%" + category + "%")

    if status:
        sql += " AND LOWER(status) LIKE ?"
        params.append("%" + status + "%")

    sql += " ORDER BY score DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(sql, params)
    data = cursor.fetchall()

    cursor.execute("SELECT DISTINCT state FROM projects")
    states = sorted([row[0] for row in cursor.fetchall() if row[0]])

    cursor.execute("SELECT DISTINCT category FROM projects")
    categories = sorted([row[0] for row in cursor.fetchall() if row[0]])

    conn.close()

    return render_template(
        "home.html",
        data=data,
        states=states,
        categories=categories,
        page=page
    )


# ---------------- PROJECT DETAIL ----------------
@app.route("/project/<int:id>")
def project_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects WHERE project_id = ?", (id,))
    project = cursor.fetchone()

    conn.close()

    if not project:
        return "Project not found", 404

    # 🔥 AI recommendations
    results = get_similar_projects(id)
    recommendations = [r[1] for r in results]

    return render_template(
        "project_detail.html",
        project=project,
        recommendations=recommendations
    )


# ---------------- ADD PROJECT ----------------
@app.route("/add_project", methods=["POST"])
def add_project():
    title = request.form["title"]
    source = request.form["source"]
    url = request.form["url"]
    state = request.form["state"].lower()
    category = request.form["category"].lower()
    country = request.form["country"].lower()
    status = request.form["status"].lower()

    score = calculate_score(category, state, title)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO projects 
        (title, source, url, state, category, country, status, score) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (title, source, url, state, category, country, status, score)
    )

    conn.commit()
    conn.close()

    return redirect("/home")


# ---------------- EDIT PROJECT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_project(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        source = request.form["source"]
        url = request.form["url"]
        state = request.form["state"].lower()
        category = request.form["category"].lower()
        country = request.form["country"].lower()
        status = request.form["status"].lower()

        score = calculate_score(category, state, title)  # ✅ FIXED

        cursor.execute(
            """UPDATE projects 
            SET title=?, source=?, url=?, state=?, category=?, country=?, status=?, score=? 
            WHERE project_id=?""",
            (title, source, url, state, category, country, status, score, id)
        )

        conn.commit()
        conn.close()

        return redirect("/home")

    cursor.execute("SELECT * FROM projects WHERE project_id=?", (id,))
    project = cursor.fetchone()

    conn.close()

    return render_template("project_edit.html", project=project)


# ---------------- TOP PROJECTS ----------------
@app.route("/top")
def top_projects():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM projects
        WHERE score IS NOT NULL
        ORDER BY score DESC
        LIMIT 20
    """)

    data = cursor.fetchall()
    conn.close()

    return render_template("home.html", data=data)
@app.route("/delete/<int:id>")
def delete_project(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM projects WHERE project_id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/home")
@app.route("/rebuild-cache")
def rebuild_cache():
    from semantic_search import build_cache
    build_cache()
    return "Cache rebuilt successfully!"
# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT state, COUNT(*) as count 
        FROM projects 
        GROUP BY state 
        ORDER BY count DESC
    """)
    state_data = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM projects 
        GROUP BY category 
        ORDER BY count DESC
    """)
    category_data = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "dashboard.html",
        state_data=state_data,
        category_data=category_data
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)