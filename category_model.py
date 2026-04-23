# ---------------- IMPORTS ----------------
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


# ---------------- TRAINING DATA (ENHANCED) ----------------
texts = [
    # Education
    "education school learning students teaching literacy rural education",
    "child education ngo teaching poor students school support india",
    "free education rural children literacy program schooling",

    # Health
    "hospital healthcare medical health treatment clinic services",
    "health awareness medical camps rural healthcare india NGO",
    "free medical camp health support rural areas disease prevention",

    # Women / Social
    "women empowerment gender equality women rights NGO india",
    "self help groups women development rural women support livelihood",
    "women safety empowerment skill development programs NGO",

    # Environment
    "environment climate sustainability conservation green nature india",
    "tree plantation environmental protection climate change NGO",
    "clean environment sustainability green energy renewable projects",

    # Food
    "food hunger nutrition feeding poor midday meals india NGO",
    "food distribution hunger relief feeding children NGO india",
    "midday meal food support poor children nutrition program",

    # General social
    "social development NGO community upliftment rural development",
    "nonprofit organization working for society welfare india NGO"
]

labels = [
    "education", "education", "education",
    "health", "health", "health",
    "social", "social", "social",
    "environment", "environment", "environment",
    "food", "food", "food",
    "social", "social"
]


# ---------------- KEYWORD BACKUP (VERY IMPORTANT) ----------------
keyword_map = {
    "education": ["school", "education", "literacy", "student", "learning"],
    "health": ["health", "hospital", "medical", "clinic", "treatment"],
    "environment": ["environment", "climate", "tree", "sustainability", "green"],
    "food": ["food", "hunger", "nutrition", "meal"],
    "social": ["women", "community", "empowerment", "development", "rural"]
}


# ---------------- VECTORIZER ----------------
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    max_features=1000
)

X = vectorizer.fit_transform(texts)


# ---------------- MODEL ----------------
model = MultinomialNB()
model.fit(X, labels)


# ---------------- KEYWORD FALLBACK ----------------
def keyword_category(text):
    text = text.lower()

    for category, words in keyword_map.items():
        for w in words:
            if w in text:
                return category

    return None


# ---------------- MAIN PREDICT ----------------
def predict_category(text):
    if not text:
        return "social"

    text = text.lower()

    # 🔥 ML prediction
    X_test = vectorizer.transform([text])
    probs = model.predict_proba(X_test)[0]
    max_index = probs.argmax()

    predicted = model.classes_[max_index]
    confidence = probs[max_index]

    # 🔥 fallback if low confidence
    if confidence < 0.65:
        keyword_pred = keyword_category(text)
        if keyword_pred:
            return keyword_pred

    return predicted


# ---------------- WITH CONFIDENCE ----------------
def predict_with_confidence(text):
    if not text:
        return "social", 0.0

    text = text.lower()
    X_test = vectorizer.transform([text])

    probs = model.predict_proba(X_test)[0]
    max_index = probs.argmax()

    return model.classes_[max_index], float(probs[max_index])


# ---------------- BULK ----------------
def predict_bulk(texts_list):
    return [predict_category(t) for t in texts_list]


# ---------------- TEST ----------------
if __name__ == "__main__":
    samples = [
        "NGO working for child education and rural schools",
        "Free medical camp and healthcare services",
        "Women empowerment and skill development",
        "Tree plantation and environmental protection",
        "Food distribution for poor children",
        "Community development NGO in rural India"
    ]

    for s in samples:
        cat, conf = predict_with_confidence(s)
        print(f"\nText: {s}")
        print(f"Category: {cat} | Confidence: {round(conf, 2)}")