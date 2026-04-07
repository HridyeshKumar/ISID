from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# 🔥 Training data (basic for now)
texts = [
    "education school learning students",
    "hospital healthcare medical health",
    "women empowerment gender equality",
    "environment climate sustainability",
    "food hunger nutrition feeding"
]

labels = [
    "education",
    "health",
    "women",
    "environment",
    "food"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)


def predict_category(text):
    X_test = vectorizer.transform([text])
    return model.predict(X_test)[0]