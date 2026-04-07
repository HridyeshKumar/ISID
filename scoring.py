def calculate_score(title, category, state):
    score = 0

    # category importance
    if category == "education":
        score += 3
    elif category == "health":
        score += 3
    elif category == "women":
        score += 2
    elif category == "environment":
        score += 2
    else:
        score += 1

    # state impact (example logic)
    if state in ["bihar", "uttar pradesh"]:
        score += 2

    # keyword boost
    text = title.lower()
    if "rural" in text:
        score += 2
    if "foundation" in text:
        score += 1

    return score