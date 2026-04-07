# ---------------- IMPORTS ----------------
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


# ---------------- TRAINING DATA ----------------
texts = [
    # Education
    "education school learning students teaching literacy",
    "child education ngo teaching poor students school support",
    "free education rural children literacy program",

    # Health
    "hospital healthcare medical health treatment clinic",
    "health awareness medical camps rural healthcare services",
    "free medical camp health support rural areas",

    # Women / Social
    "women empowerment gender equality support women rights",
    "self help groups women development rural women support",
    "women safety empowerment skill development programs",

    # Environment
    "environment climate sustainability conservation green nature",
    "tree plantation environmental protection climate action",
    "clean environment sustainability green energy projects",

    # Food
    "food hunger nutrition feeding poor midday meals",
    "food distribution hunger relief feeding children",
    "midday meal food support poor children nutrition"
]

labels = [
    "education", "education", "education",
    "health", "health", "health",
    "social", "social", "social",
    "environment", "environment", "environment",
    "food", "food", "food"
]


# ---------------- VECTORIZER ----------------
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),   # unigrams + bigrams
    max_features=500
)

X = vectorizer.fit_transform(texts)


# ---------------- MODEL ----------------
model = MultinomialNB()
model.fit(X, labels)


# ---------------- PREDICT CATEGORY ----------------
def predict_category(text):
    if not text:
        return "social"   # fallback

    text = text.lower()
    X_test = vectorizer.transform([text])

    prediction = model.predict(X_test)[0]
    return prediction


# ---------------- PREDICT WITH CONFIDENCE ----------------
def predict_with_confidence(text):
    if not text:
        return "social", 0.0

    text = text.lower()
    X_test = vectorizer.transform([text])

    probs = model.predict_proba(X_test)[0]
    max_index = probs.argmax()

    return model.classes_[max_index], probs[max_index]


# ---------------- OPTIONAL: BULK PREDICT ----------------
def predict_bulk(texts_list):
    results = []
    for text in texts_list:
        category = predict_category(text)
        results.append(category)
    return results


# ---------------- TEST ----------------
if __name__ == "__main__":
    samples = [
        "NGO working for child education and rural schools",
        "Free medical camp and healthcare services",
        "Women empowerment and skill development",
        "Tree plantation and environmental protection",
        "Food distribution for poor children"
    ]

    for s in samples:
        cat, conf = predict_with_confidence(s)
        print(f"\nText: {s}")
        print(f"Category: {cat} | Confidence: {round(conf, 2)}")