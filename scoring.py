# scoring.py

def calculate_score(title, category, description=""):
    score = 0

    # 🔥 1. Category weight (impact priority)
    weights = {
        "education": 5,
        "health": 5,
        "women": 4,
        "environment": 4,
        "food": 3,
        "rural": 4,
        "child": 4,
        "skill": 3,
        "general": 2
    }

    score += weights.get(category, 2)

    text = (title + " " + description).lower()

    # 🔥 2. Impact keywords
    keywords = {
        "rural": 2,
        "women": 2,
        "children": 2,
        "education": 2,
        "health": 2,
        "sustainability": 2,
        "empowerment": 2,
        "community": 1
    }

    for word, val in keywords.items():
        if word in text:
            score += val

    # 🔥 3. Description richness
    if len(description) > 150:
        score += 2
    elif len(description) > 80:
        score += 1

    return score