import pandas as pd
import numpy as np
import pickle
import os
import nltk
import re
import matplotlib.pyplot as plt
import itertools

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score

# NLTK setup
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = re.sub(r"[^a-zA-Z\s]", "", str(text)).lower()
    tokens = word_tokenize(text)
    return ' '.join([t for t in tokens if t not in stop_words])

def plot_confusion_matrix(cm, classes, title='Confusion Matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    ticks = np.arange(len(classes))
    plt.xticks(ticks, classes, rotation=45)
    plt.yticks(ticks, classes)
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, str(cm[i, j]),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.show()

# Load and combine data
columns = ['label', 'statement', 'subject', 'speaker', 'speaker_job', 'state_info',
           'party_affiliation', 'barely_true_counts', 'false_counts', 'half_true_counts',
           'mostly_true_counts', 'pants_on_fire_counts', 'context']

df_train = pd.read_csv('train.tsv', sep='\t', header=None, names=columns)
df_valid = pd.read_csv('valid.tsv', sep='\t', header=None, names=columns)
df_test  = pd.read_csv('test.tsv',  sep='\t', header=None, names=columns)
df = pd.concat([df_train, df_valid, df_test], ignore_index=True)

label_map = {
    'true': 'REAL DATA',
    'mostly-true': 'REAL DATA',
    'half-true': 'REAL DATA',
    'false': 'FAKE DATA',
    'barely-true': 'FAKE DATA',
    'pants-fire': 'FAKE DATA'
}
df['label'] = df['label'].map(label_map)
df.dropna(subset=['label', 'statement'], inplace=True)
df['clean_statement'] = df['statement'].apply(clean_text)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(df['clean_statement'], df['label'], 
                                                    test_size=0.2, stratify=df['label'], random_state=42)

# TF-IDF
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2), max_df=0.9, min_df=2, max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Calibrated classifier
base_model = PassiveAggressiveClassifier(C=0.5, max_iter=50, tol=1e-4, class_weight='balanced', random_state=42)
model = CalibratedClassifierCV(estimator=base_model, method='sigmoid', cv=3)
model.fit(X_train_vec, y_train)
y_pred = model.predict(X_test_vec)

# Evaluation
print("Accuracy: {:.2f}%".format(accuracy_score(y_test, y_pred) * 100))
print("Classification Report:\n", classification_report(y_test, y_pred))

# ROC-AUC Score
lb = LabelBinarizer()
y_test_bin = lb.fit_transform(y_test)
y_proba = model.predict_proba(X_test_vec)[:, 1]
roc_auc = roc_auc_score(y_test_bin, y_proba)
print("ROC-AUC Score: {:.4f}".format(roc_auc))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred, labels=['FAKE DATA', 'REAL DATA'])
plot_confusion_matrix(cm, classes=['FAKE DATA', 'REAL DATA'])

# Save model and vectorizer
os.makedirs('Models', exist_ok=True)
with open('Models/pac_model_liar.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('Models/tfidf_vectorizer_liae.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)