def preprocess_and_classify(articles, model, vectorizer=None, fake_threshold=0.5):
    if vectorizer is None:
        model_input = articles
    else:
        from utils.preprocessing import preprocess_text

        processed = [preprocess_text(article) for article in articles]
        model_input = vectorizer.transform(processed)

    probabilities = model.predict_proba(model_input)
    classes = list(model.classes_)
    fake_index = classes.index("FAKE DATA")

    results = []
    for probability in probabilities:
        fake_score = float(probability[fake_index])
        classification = "Fake" if fake_score >= fake_threshold else "Real"
        results.append({
            "classification": classification,
            "confidence": fake_score if classification == "Fake" else 1.0 - fake_score,
            "confidence_scores": {"Fake": fake_score, "Real": 1.0 - fake_score},
        })

    return results