from flask import Flask, request, render_template, redirect
import sqlite3
import os
from hybrid_recommender import hybrid_recommendations
from semantic_search import (
    search,
    get_similar_projects,
    build_cache
)
from collections import Counter
import ast
app = Flask(__name__)


# ---------------- DB CONNECTION ----------------

def get_db_connection():

    conn = sqlite3.connect(
        "database.db",
        check_same_thread=False
    )

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

        impact_score REAL DEFAULT 0,
        innovation_score REAL DEFAULT 0,
        scale_score REAL DEFAULT 0,
        sustainability_score REAL DEFAULT 0,
        collaboration_score REAL DEFAULT 0,

        topics TEXT,
        detected_locations TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- INITIALIZE ----------------

init_db()
build_cache()


# ---------------- HOME ----------------

@app.route("/")
@app.route("/home")
def home():

    query = request.args.get("q", "").lower()

    conn = get_db_connection()
    cursor = conn.cursor()

    # ---------------- SEMANTIC SEARCH ----------------

    if query:

        results = search(query)

        cleaned_data = []

        for row in results:

            row = dict(row)

            # summary
            summary = ""

            if row.get("source"):

                summary = (
                    row["source"][:250] + "..."
                )

            row["summary"] = summary

            # safe fallbacks
            row["topics"] = (
                str(row.get("topics") or "")
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace("_", " ")
            )

            row["detected_locations"] = (
                str(row.get("detected_locations") or "")
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
            )

            row["impact_score"] = (
                row.get("impact_score") or 0
            )

            cleaned_data.append(row)

        conn.close()

        return render_template(
            "home.html",
            data=cleaned_data
        )

    # ---------------- NORMAL DISPLAY ----------------

    cursor.execute("""
    SELECT *
    FROM projects
    ORDER BY impact_score DESC
    LIMIT 50
    """)

    rows = cursor.fetchall()

    cleaned_data = []

    for row in rows:

        row = dict(row)

        summary = ""

        if row.get("source"):

            summary = (
                row["source"][:250] + "..."
            )

        row["summary"] = summary

        row["topics"] = (
            str(row.get("topics") or "")
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace("_", " ")
        )

        row["detected_locations"] = (
            str(row.get("detected_locations") or "")
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )

        row["impact_score"] = (
            row.get("impact_score") or 0
        )

        cleaned_data.append(row)

    conn.close()

    return render_template(
        "home.html",
        data=cleaned_data
    )


# ---------------- PROJECT DETAIL ----------------

@app.route("/project/<int:id>")
def project_detail(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM projects WHERE project_id=?",
        (id,)
    )

    project = cursor.fetchone()

    conn.close()

    if not project:
        return "Project not found", 404

    project = dict(project)

    # AI recommendations
    recommendations = hybrid_recommendations(id)

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

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO projects (

        title,
        source,
        url,
        state,
        category,
        country,
        status

    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (

        title,
        source,
        url,
        state,
        category,
        country,
        status
    ))

    conn.commit()
    conn.close()

    build_cache()

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

        cursor.execute("""
        UPDATE projects
        SET

            title=?,
            source=?,
            url=?,
            state=?,
            category=?,
            country=?,
            status=?

        WHERE project_id=?
        """, (

            title,
            source,
            url,
            state,
            category,
            country,
            status,
            id
        ))

        conn.commit()
        conn.close()

        build_cache()

        return redirect("/home")

    cursor.execute(
        "SELECT * FROM projects WHERE project_id=?",
        (id,)
    )

    project = cursor.fetchone()

    conn.close()

    return render_template(
        "project_edit.html",
        project=project
    )


# ---------------- DELETE PROJECT ----------------

@app.route("/delete/<int:id>")
def delete_project(id):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM projects WHERE project_id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    build_cache()

    return redirect("/home")


# ---------------- REBUILD CACHE ----------------

@app.route("/rebuild-cache")
def rebuild_cache():

    build_cache()

    return "✅ Cache rebuilt successfully!"


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    import ast
    import sqlite3

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # ---------------- LOAD PROJECTS ----------------

    cursor.execute("""

    SELECT

        detected_locations,
        topics

    FROM projects

    """)

    projects = cursor.fetchall()

    conn.close()

    # ---------------- COUNTERS ----------------

    location_counts = {}

    topic_counts = {}

    # ---------------- PROCESS PROJECTS ----------------

    for project in projects:

        # ---------- LOCATIONS ----------

        locations = project["detected_locations"]

        if locations:

            try:

                locations = ast.literal_eval(
                    locations
                )

            except:

                locations = []

            for loc in locations:

                loc = str(loc).strip()

                if loc:

                    location_counts[loc] = (

                        location_counts.get(loc, 0) + 1
                    )

        # ---------- TOPICS ----------

        topics = project["topics"]

        if topics:

            try:

                topics = ast.literal_eval(
                    topics
                )

            except:

                topics = []

            for topic in topics:

                topic = str(topic).strip()

                if topic:

                    topic_counts[topic] = (

                        topic_counts.get(topic, 0) + 1
                    )

    # ---------------- FORMAT STATE DATA ----------------

    state_data = sorted(

        [

            {

                "state": key,

                "count": value

            }

            for key, value in location_counts.items()

        ],

        key=lambda x: x["count"],

        reverse=True

    )[:10]

    # ---------------- FORMAT CATEGORY DATA ----------------

    category_data = sorted(

        [

            {

                "category": key,

                "count": value

            }

            for key, value in topic_counts.items()

        ],

        key=lambda x: x["count"],

        reverse=True

    )[:10]

    # ---------------- RENDER TEMPLATE ----------------

    return render_template(

        "dashboard.html",

        state_data=state_data,

        category_data=category_data
    )
@app.route("/graph")
def graph():

    return render_template(

        "interactive_graph.html"
    )
# ---------------- RUN ----------------

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )