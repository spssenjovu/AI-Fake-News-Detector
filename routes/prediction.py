from utils.preprocessing import preprocess_text

def preprocess_and_classify(articles, model, vectorizer):
    processed = [preprocess_text(article) for article in articles]
    transformed = vectorizer.transform(processed)
    predictions = model.predict(transformed)
    confidences = model.predict_proba(transformed).max(axis=1)

    return [
        {"classification": pred, "confidence": float(conf)}
        for pred, conf in zip(predictions, confidences)
    ]


def classify_news_articles(articles):
    results = []
    processed_articles = vectorizer.transform(articles)
    predictions = model.predict(processed_articles)
    probabilities = model.predict_proba(processed_articles)

    for article, prediction, prob in zip(articles, predictions, probabilities):
        classification = "Fake" if prediction == 1 else "Real"
        confidence = round(max(prob), 3)

        results.append({
            "text": article,
            "classification": classification,
            "confidence": confidence,
            "confidence_scores": {
                "Fake": round(prob[1], 3),
                "Real": round(prob[0], 3)
            }
        })

    return results