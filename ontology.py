# ---------------- SDG ONTOLOGY ----------------

ONTOLOGY = {

    "sdg_education": [

        "education",
        "school",
        "literacy",
        "learning",
        "students",
        "teaching",
        "digital literacy"
    ],

    "sdg_health": [

        "health",
        "medical",
        "hospital",
        "healthcare",
        "nutrition",
        "mental health"
    ],

    "sdg_climate": [

        "climate",
        "green",
        "environment",
        "sustainability",
        "renewable",
        "ecology"
    ],

    "sdg_gender": [

        "women",
        "girls",
        "empowerment",
        "gender equality",
        "female"
    ],

    "sdg_hunger": [

        "food",
        "nutrition",
        "hunger",
        "malnutrition"
    ],

    "sdg_livelihood": [

        "employment",
        "livelihood",
        "skills",
        "training",
        "income"
    ]
}


# ---------------- DETECT TOPICS ----------------

def detect_topics(text):

    text = text.lower()

    scores = {}

    # ---------------- SCORE EACH SDG ----------------

    for topic, keywords in ONTOLOGY.items():

        score = 0

        for keyword in keywords:

            if keyword in text:

                score += 1

        if score > 0:

            scores[topic] = score

    # ---------------- SORT BY RELEVANCE ----------------

    ranked = sorted(

        scores.items(),

        key=lambda x: x[1],

        reverse=True
    )

    # ---------------- KEEP TOP 2 ONLY ----------------

    final_topics = [

        r[0]

        for r in ranked[:2]
    ]

    return final_topics


# ---------------- TEST ----------------

if __name__ == "__main__":

    text = """

    AI platform supporting women empowerment,
    climate sustainability, and rural education

    """

    topics = detect_topics(text)

    print(topics)