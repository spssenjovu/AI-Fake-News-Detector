import joblib
from utils.preprocessing import preprocess_text  # Adjust the path as needed

model = joblib.load("models/pac_model.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

def classify_news_articles(articles):
    results = []
    processed_articles = vectorizer.transform(articles)  # Apply TF-IDF vectorization
    predictions = model.predict(processed_articles)

    for article, prediction in zip(articles, predictions):
        results.append({"text": article, "classification": "Fake" if prediction == 1 else "Real"})

    return results

def preprocess_and_classify(articles):
    cleaned_articles = [preprocess_text(article) for article in articles]
    return classify_news_articles(cleaned_articles)