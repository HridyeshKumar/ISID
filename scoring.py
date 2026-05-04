# ---------------- MULTI-DIMENSIONAL SCORING ----------------

KEYWORDS = {

    "impact": {

        # strong indicators
        "women empowerment": 3,
        "rural development": 3,
        "community impact": 3,
        "social impact": 3,

        # medium indicators
        "education": 2,
        "healthcare": 2,
        "livelihood": 2,
        "nutrition": 2,
        "children": 2,

        # weak indicators
        "support": 1,
        "community": 1,
        "social": 1
    },

    "innovation": {

        "artificial intelligence": 3,
        "machine learning": 3,
        "innovation": 2,
        "technology": 2,
        "digital": 2,
        "platform": 2,
        "automation": 2,
        "research": 1,
        "data": 1
    },

    "scale": {

        "nationwide": 3,
        "across india": 3,
        "multi-state": 3,

        "national": 2,
        "large scale": 2,
        "thousands": 2,
        "network": 2,

        "india": 1
    },

    "sustainability": {

        "climate change": 3,
        "renewable energy": 3,

        "sustainable": 2,
        "green": 2,
        "environment": 2,
        "ecology": 2,

        "climate": 1
    },

    "collaboration": {

        "government partnership": 3,
        "university collaboration": 3,

        "partner": 2,
        "collaboration": 2,
        "joint initiative": 2,
        "funded by": 2,

        "ngo": 1
    }
}


# ---------------- WEIGHTED SCORING ----------------

def weighted_score(text, keyword_dict):

    text = text.lower()

    total = 0

    max_possible = sum(
        keyword_dict.values()
    )

    for keyword, weight in keyword_dict.items():

        if keyword in text:

            total += weight

    normalized = (
        total / max_possible
    ) * 10

    return round(
        min(normalized, 10),
        1
    )


# ---------------- CONTEXT BONUS ----------------

def contextual_bonus(text):

    text = text.lower()

    bonus = 0

    # strong social context
    if (
        "women empowerment" in text or
        "rural development" in text
    ):

        bonus += 1

    # strong scale context
    if (
        "nationwide" in text or
        "across india" in text
    ):

        bonus += 1

    return bonus


# ---------------- MAIN SCORING ----------------

def calculate_dimension_scores(text):

    impact = weighted_score(
        text,
        KEYWORDS["impact"]
    )

    innovation = weighted_score(
        text,
        KEYWORDS["innovation"]
    )

    scale = weighted_score(
        text,
        KEYWORDS["scale"]
    )

    sustainability = weighted_score(
        text,
        KEYWORDS["sustainability"]
    )

    collaboration = weighted_score(
        text,
        KEYWORDS["collaboration"]
    )

    # ---------------- CONTEXT BONUS ----------------

    bonus = contextual_bonus(text)

    impact = min(
        impact + bonus,
        10
    )

    scale = min(
        scale + (bonus * 0.5),
        10
    )

    # ---------------- FALLBACK ----------------

    if (
        len(text.split()) > 40 and
        impact == 0
    ):

        impact = 1.5

    return {

        "impact_score": round(impact, 1),

        "innovation_score": round(innovation, 1),

        "scale_score": round(scale, 1),

        "sustainability_score": round(sustainability, 1),

        "collaboration_score": round(collaboration, 1)
    }


# ---------------- BACKWARD COMPATIBILITY ----------------

def calculate_score(text):

    scores = calculate_dimension_scores(
        text
    )

    return round(
        sum(scores.values()),
        1
    )


# ---------------- TEST ----------------

if __name__ == "__main__":

    text = """

    AI platform supporting women empowerment
    and rural education across India.

    """

    scores = calculate_dimension_scores(
        text
    )

    print(scores)