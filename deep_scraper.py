import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import urllib3

from ontology import detect_topics
from scoring import calculate_dimension_scores
from location_extractor import extract_locations


# =========================================================
# DISABLE SSL WARNINGS
# =========================================================

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("database.db")

cursor = conn.cursor()


# =========================================================
# NOISY FILTERS
# =========================================================

NOISY_PATTERNS = [

    "top 10",
    "top 20",
    "best ngos",
    "directory",
    "funding agencies",
    "ngo reporter",
    "archives",
    "jobs",
    "wikipedia",
    "list of",
    "portal",
    "npo",
    "npodarpan",
    "ranking",
    "government scheme",
    "news",
    "blog",
    "media",
    "press release",
    "award",
    "conference",
    "seminar",
    "event",
    "page 2",
    "page 3"
]


# =========================================================
# QUALITY SIGNALS
# =========================================================

GOOD_SIGNALS = [

    "program",
    "initiative",
    "impact",
    "beneficiaries",
    "community",
    "implementation",
    "project",
    "csr",
    "women",
    "children",
    "rural",
    "education",
    "healthcare",
    "livelihood",
    "training",
    "empowerment",
    "sustainability",
    "development"
]


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    text = re.sub(
        r'\s+',
        ' ',
        str(text)
    )

    return text.strip()


# =========================================================
# GENERATE SUMMARY
# =========================================================

def generate_summary(text):

    sentences = text.split(".")

    clean_sentences = []

    for s in sentences:

        s = s.strip()

        if len(s) > 40:

            clean_sentences.append(s)

    summary = ". ".join(
        clean_sentences[:2]
    )

    return summary[:500]


# =========================================================
# EXTRACT TEXT
# =========================================================

def extract_text(soup):

    collected_text = []

    # H1
    for h in soup.find_all("h1")[:3]:

        text = clean_text(
            h.get_text()
        )

        if len(text) > 20:

            collected_text.append(text)

    # H2
    for h in soup.find_all("h2")[:8]:

        text = clean_text(
            h.get_text()
        )

        if len(text) > 20:

            collected_text.append(text)

    # PARAGRAPHS
    for p in soup.find_all("p")[:40]:

        text = clean_text(
            p.get_text()
        )

        if len(text) > 40:

            collected_text.append(text)

    # ARTICLE
    for article in soup.find_all("article"):

        text = clean_text(
            article.get_text()
        )

        if len(text) > 80:

            collected_text.append(text)

    # REMOVE DUPLICATES

    unique_text = []

    seen = set()

    for t in collected_text:

        short = t[:120]

        if short not in seen:

            unique_text.append(t)

            seen.add(short)

    final_text = " ".join(
        unique_text
    )

    return final_text[:10000]


# =========================================================
# SCRAPE WEBSITE
# =========================================================

def scrape_website(url):

    try:

        headers = {

            "User-Agent":
            "Mozilla/5.0"
        }

        response = requests.get(

            url,

            headers=headers,

            timeout=20,

            verify=False
        )

        soup = BeautifulSoup(

            response.text,

            "html.parser"
        )

        # =================================================
        # TITLE
        # =================================================

        title = ""

        if soup.title:

            title = clean_text(
                soup.title.text
            )

        title_lower = title.lower()

        # =================================================
        # NOISY TITLE FILTER
        # =================================================

        for bad in NOISY_PATTERNS:

            if bad in title_lower:

                print(
                    "⛔ Skipped noisy page:",
                    title
                )

                return None

        # =================================================
        # META DESCRIPTION
        # =================================================

        description = ""

        meta_desc = soup.find(

            "meta",

            attrs={
                "name": "description"
            }
        )

        if meta_desc:

            description = clean_text(

                meta_desc.get(
                    "content",
                    ""
                )
            )

        # =================================================
        # EXTRACT TEXT
        # =================================================

        extracted_text = extract_text(
            soup
        )

        full_text = (

            title + " " +
            description + " " +
            extracted_text
        )

        full_text = clean_text(
            full_text
        )

        # =================================================
        # MINIMUM CONTENT CHECK
        # =================================================

        if len(full_text.split()) < 50:

            return None

        # =================================================
        # QUALITY SCORE
        # =================================================

        quality_score = 0

        lower_text = full_text.lower()

        for signal in GOOD_SIGNALS:

            if signal in lower_text:

                quality_score += 1

        # =================================================
        # WEAK PAGE FILTER
        # =================================================

        if quality_score < 3:

            print(
                "⛔ Weak project page:",
                title
            )

            return None

        # =================================================
        # AI ENRICHMENT
        # =================================================

        topics = detect_topics(
            full_text
        )

        locations = extract_locations(
            full_text
        )

        scores = calculate_dimension_scores(
            full_text
        )

        summary = generate_summary(
            full_text
        )

        return {

            "title": title,

            "summary": summary,

            "full_text": full_text,

            "topics": topics,

            "locations": locations,

            "scores": scores
        }

    except Exception as e:

        print(
            "❌ Error scraping:",
            url,
            e
        )

        return None


# =========================================================
# LOAD PROJECTS
# =========================================================

cursor.execute("""

SELECT

    project_id,
    url,
    title

FROM projects

WHERE (

    impact_score IS NULL
    OR impact_score = 0
    OR topics IS NULL
    OR detected_locations IS NULL

)

""")

rows = cursor.fetchall()


# =========================================================
# UPDATE PROJECTS
# =========================================================

updated = 0

for project_id, url, title in rows:

    if not url:

        continue

    url = str(url).strip()

    if (

        url == "nan"

        or

        not url.startswith("http")

    ):

        continue

    data = scrape_website(url)

    if not data:

        continue

    try:

        cursor.execute("""

        UPDATE projects

        SET

            full_text = ?,

            summary = ?,

            topics = ?,

            detected_locations = ?,

            impact_score = ?,

            innovation_score = ?,

            sustainability_score = ?,

            scale_score = ?,

            collaboration_score = ?

        WHERE project_id = ?

        """, (

            data["full_text"],

            data["summary"],

            str(data["topics"]),

            str(data["locations"]),

            data["scores"]["impact_score"],

            data["scores"]["innovation_score"],

            data["scores"]["sustainability_score"],

            data["scores"]["scale_score"],

            data["scores"]["collaboration_score"],

            project_id
        ))

        conn.commit()

        updated += 1

        if updated % 10 == 0:

            print(
                f"✅ Updated: {updated}"
            )

    except Exception as e:

        print(
            "❌ Database Error:",
            e
        )


# =========================================================
# CLOSE
# =========================================================

conn.close()


# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n🚀 ENRICHMENT COMPLETE")

print(
    f"✅ Total Updated: {updated}"
)