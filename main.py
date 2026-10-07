from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import RandomOverSampler
from imblearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import balanced_accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve

ROOT_DIR = Path(__file__).resolve().parent
MODEL_DIR = ROOT_DIR / "Models"
MODEL_PATH = MODEL_DIR / "news_pipeline.pkl"
FAKE_LABEL = "FAKE DATA"
REAL_LABEL = "REAL DATA"

DATA_COLUMNS = [
    "label", "statement", "subject", "speaker", "speaker_job", "state_info",
    "party_affiliation", "barely_true_counts", "false_counts", "half_true_counts",
    "mostly_true_counts", "pants_on_fire_counts", "context",
]
LABEL_MAP = {
    "true": REAL_LABEL,
    "mostly-true": REAL_LABEL,
    "half-true": REAL_LABEL,
    "false": FAKE_LABEL,
    "barely-true": FAKE_LABEL,
    "pants-fire": FAKE_LABEL,
}


def load_split(filename):
    dataset = pd.read_csv(ROOT_DIR / filename, sep="\t", header=None, names=DATA_COLUMNS)
    dataset["label"] = dataset["label"].map(LABEL_MAP)
    dataset.dropna(subset=["label", "statement"], inplace=True)
    return dataset["statement"].astype(str), dataset["label"]


def build_model():
    text_classifier = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english",
            max_df=0.7,
            min_df=2,
            ngram_range=(1, 2),
            max_features=10000,
        )),
        ("oversample", RandomOverSampler(random_state=42)),
        ("classifier", PassiveAggressiveClassifier(
            C=0.5,
            max_iter=1000,
            tol=1e-4,
            random_state=42,
        )),
    ])
    return CalibratedClassifierCV(estimator=text_classifier, method="sigmoid", cv=3)


def select_fake_threshold(model, texts, labels):
    probabilities = model.predict_proba(texts)
    fake_index = list(model.classes_).index(FAKE_LABEL)
    fake_targets = (np.asarray(labels) == FAKE_LABEL).astype(int)
    false_positive_rates, true_positive_rates, thresholds = roc_curve(
        fake_targets, probabilities[:, fake_index]
    )
    finite_thresholds = np.isfinite(thresholds)
    if not finite_thresholds.any():
        return 0.5

    balanced_accuracies = (
        true_positive_rates + (1 - false_positive_rates)
    ) / 2
    finite_indices = np.flatnonzero(finite_thresholds)
    best_index = finite_indices[int(np.argmax(balanced_accuracies[finite_thresholds]))]
    return float(thresholds[best_index])


def predict_with_threshold(model, texts, fake_threshold):
    probabilities = model.predict_proba(texts)
    classes = list(model.classes_)
    fake_index = classes.index(FAKE_LABEL)
    fake_probabilities = probabilities[:, fake_index]
    predictions = [
        FAKE_LABEL if probability >= fake_threshold else REAL_LABEL
        for probability in fake_probabilities
    ]
    return predictions, fake_probabilities


def evaluate(model, name, texts, labels, fake_threshold):
    predictions, fake_probabilities = predict_with_threshold(model, texts, fake_threshold)
    fake_targets = (np.asarray(labels) == FAKE_LABEL).astype(int)

    print(f"\n{name} classification report:")
    print(classification_report(
        labels,
        predictions,
        labels=[FAKE_LABEL, REAL_LABEL],
        target_names=["Fake", "Real"],
        zero_division=0,
    ))
    print("Confusion matrix [Fake, Real]:")
    print(confusion_matrix(labels, predictions, labels=[FAKE_LABEL, REAL_LABEL]))
    print("Balanced accuracy: {:.4f}".format(balanced_accuracy_score(labels, predictions)))
    print("Fake-class ROC-AUC: {:.4f}".format(
        roc_auc_score(fake_targets, fake_probabilities)
    ))


def main():
    train_text, train_labels = load_split("train.tsv")
    valid_text, valid_labels = load_split("valid.tsv")
    test_text, test_labels = load_split("test.tsv")

    print("Training label distribution:")
    print(train_labels.value_counts(normalize=True))

    model = build_model()
    model.fit(train_text, train_labels)

    fake_threshold = select_fake_threshold(model, valid_text, valid_labels)
    print(f"Validation-selected Fake threshold (balanced accuracy): {fake_threshold:.4f}")
    evaluate(model, "Validation", valid_text, valid_labels, fake_threshold)
    evaluate(model, "Held-out test", test_text, test_labels, fake_threshold)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "fake_threshold": fake_threshold}, MODEL_PATH)
    print(f"\nSaved text-classification pipeline to {MODEL_PATH}")


if __name__ == "__main__":
    main()