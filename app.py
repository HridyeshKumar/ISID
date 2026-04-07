from flask import Flask, request, render_template, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
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
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM projects")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("""
        INSERT INTO projects (title, source, url, state, category, country, status)
        VALUES
        ('Pratham', 'Education NGO', 'https://pratham.org', 'delhi', 'education', 'india', 'active'),
        ('Goonj', 'Rural NGO', 'https://goonj.org', 'delhi', 'social', 'india', 'active'),
        ('Akshaya Patra', 'Midday Meals', 'https://akshayapatra.org', 'karnataka', 'food', 'india', 'active'),
        ('Teach For India', 'Education NGO', 'https://teachforindia.org', 'maharashtra', 'education', 'india', 'active')
        """)
        conn.commit()

    conn.close()
init_db()
seed_data()
# 🔍 HOME + FILTER
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

    sql = "SELECT * FROM projects ORDER BY score DESC"
    params = []

    if query:
        sql += " AND title LIKE ?"
        params.append("%" + query + "%")

    if state:
        sql += " AND state LIKE ?"
        params.append("%" + state + "%")

    if category:
        sql += " AND category LIKE ?"
        params.append("%" + category + "%")

    if status:
        sql += " AND status LIKE ?"
        params.append("%" + status + "%")

    sql += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(sql, params)
    data = cursor.fetchall()

    # 🔥 Dropdown values
    cursor.execute("SELECT DISTINCT state FROM projects")
    states = [row[0] for row in cursor.fetchall() if row[0]]

    cursor.execute("SELECT DISTINCT category FROM projects")
    categories = [row[0] for row in cursor.fetchall() if row[0]]

    states = sorted(states)
    categories = sorted(categories)

    cursor.close()
    conn.close()

    return render_template(
        "home.html",
        data=data,
        states=states,
        categories=categories,
        page=page
    )
@app.route("/project/<int:id>")
def project_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects WHERE project_id = ?", (id,))
    project = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("project_detail.html", project=project)
# ➕ ADD PROJECT
@app.route("/add_project", methods=["POST"])
def add_project():
    title = request.form["title"]
    source = request.form["source"]
    url = request.form["url"]
    state = request.form["state"].lower()
    category = request.form["category"].lower()
    country = request.form["country"].lower()
    status = request.form["status"].lower()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO projects (title, source, url, state, category, country, status) VALUES (?,?,?,?,?,?,?)",
        (title, source, url, state, category, country, status)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/home")
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

        cursor.execute(
            """UPDATE projects 
               SET title=?, source=?, url=?, state=?, category=?, country=?, status=? 
               WHERE project_id=?""",
            (title, source, url, state, category, country, status, id)
        )
        conn.commit()

        cursor.close()
        conn.close()
        return redirect("/home")

    cursor.execute("SELECT * FROM projects WHERE project_id=?", (id,))
    project = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("project_edit.html", project=project)
@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # NGOs per state
    cursor.execute("SELECT state, COUNT(*) as count FROM projects GROUP BY state")
    state_data = [dict(row) for row in cursor.fetchall()]

    # NGOs per category
    cursor.execute("SELECT category, COUNT(*) as count FROM projects GROUP BY category")
    category_data = [dict(row) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        state_data=state_data,
        category_data=category_data
    )
if __name__ == "__main__":
    app.run(debug=True)