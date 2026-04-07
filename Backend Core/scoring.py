# ---------------- SCORING FUNCTION ----------------
def calculate_score(title, category, description=""):
    score = 0

    # ---------------- SAFE INPUT ----------------
    title = (title or "").lower()
    category = (category or "").lower()
    description = (description or "").lower()

    text = f"{title} {description}"

    # ---------------- 1. CATEGORY WEIGHT ----------------
    weights = {
        "education": 6,
        "health": 6,
        "women": 5,
        "social": 5,
        "environment": 5,
        "food": 4,
        "rural": 5,
        "child": 5,
        "skill": 4,
        "general": 2
    }

    score += weights.get(category, 2)

    # ---------------- 2. KEYWORD SCORING (FREQUENCY BASED) ----------------
    keywords = {
        "rural": 2,
        "women": 2,
        "child": 2,
        "children": 2,
        "education": 2,
        "health": 2,
        "sustainability": 2,
        "empowerment": 2,
        "community": 1,
        "development": 1,
        "support": 1
    }

    for word, value in keywords.items():
        count = text.count(word)
        score += min(count * value, 5)  # cap to avoid spam

    # ---------------- 3. TITLE BOOST ----------------
    # Title is more important than description
    for word in keywords:
        if word in title:
            score += 1

    # ---------------- 4. DESCRIPTION QUALITY ----------------
    desc_len = len(description)

    if desc_len > 200:
        score += 3
    elif desc_len > 100:
        score += 2
    elif desc_len > 50:
        score += 1

    # ---------------- 5. PENALTY (LOW QUALITY / SPAM) ----------------
    if len(title) < 5:
        score -= 2

    if "login" in text or "signup" in text:
        score -= 3

    if ".pdf" in text:
        score -= 2

    # ---------------- FINAL NORMALIZATION ----------------
    score = max(score, 0)   # avoid negative
    score = min(score, 20)  # cap max score

    return score