def calculate_score(category, state, title, description=""):
    score = 0

    title = (title or "").lower()
    category = (category or "").lower()
    description = (description or "").lower()
    state = (state or "").lower()

    text = f"{title} {description}"

    weights = {
        "education": 25,
        "health": 25,
        "social": 20,
        "environment": 20,
        "food": 18,
    }

    score += weights.get(category, 10)

    if state in ["delhi", "maharashtra", "karnataka"]:
        score += 8
    elif state == "india":
        score += 5

    keywords = {
        "rural": 4, "women": 5, "child": 5, "education": 5,
        "health": 5, "empowerment": 4, "community": 3
    }

    for word, value in keywords.items():
        score += min(text.count(word) * value, 10)

    if len(description) > 200:
        score += 6

    return min(max(score, 0), 100)