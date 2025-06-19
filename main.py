import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower()  # Clean and lowercase
    tokens = word_tokenize(text)
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(lemmatized_tokens)



# Load the datasets
df_true = pd.read_csv('true.csv')
df_fake = pd.read_csv('fake.csv')

# Add label column
df_true['label'] = 'REAL DATA'
df_fake['label'] = 'FAKE DATA'

df_true = df_true.drop_duplicates()
df_fake = df_fake.drop_duplicates()

print(df_true.shape, df_fake.shape)  # Compare dataset sizes
print(df_true['label'].value_counts(), df_fake['label'].value_counts())  # Ensure balance

# Concatenate and shuffle
df = pd.concat([df_true, df_fake]).sample(frac=1, random_state=42).reset_index(drop=True)

# Extract features and labels
X = df['text'].values
y = df['label'].values

# Split the data (80% train, 20% test, stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42, shuffle=True
)

# TF-IDF Vectorizer with restrictions to reduce overfitting
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=3000, min_df=10, max_df=0.6, ngram_range=(1,2))
# Fit and transform
tfidf_train = tfidf_vectorizer.fit_transform(X_train)
tfidf_test = tfidf_vectorizer.transform(X_test)

# Hyperparameter tuning for PassiveAggressiveClassifier
param_grid = {
    'C': [0.1, 0.5, 1.0, 2.0, 5.0],
    'max_iter': [500, 1000, 2000],  # Increased iterations
    'tol': [1e-3, 1e-4]  # Fine-tune tolerance for better convergence
}

pac = PassiveAggressiveClassifier(random_state=42)
grid = GridSearchCV(pac, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid.fit(tfidf_train, y_train)

best_pac = grid.best_estimator_
print(f"Best parameters: {grid.best_params_}")



# Evaluate
y_train_pred = best_pac.predict(tfidf_train)
y_test_pred = best_pac.predict(tfidf_test)

print("Training Accuracy: {:.2f}%".format(accuracy_score(y_train, y_train_pred) * 100))
print("Test Accuracy: {:.2f}%".format(accuracy_score(y_test, y_test_pred) * 100))
print("\nClassification Report (Test):\n", classification_report(y_test, y_test_pred))

# Cross-validation scores
scores = cross_val_score(best_pac, tfidf_train, y_train, cv=5)
print("Cross-validation scores:", scores)

Y_pred = best_pac.predict(tfidf_test)
score = accuracy_score(y_test, Y_pred)


# Confusion matrix
cm = confusion_matrix(y_test, y_test_pred)
print("Confusion Matrix:\n", cm)

# Plot confusion matrix
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Real', 'Fake'], yticklabels=['Real', 'Fake'])
plt.xlabel('FAKE DATA')
plt.ylabel('REAL DATA')
plt.title('Confusion Matrix')
plt.show()

# Save the best model and vectorizer
with open('Models/pac_model.pkl', 'wb') as model_file:
    pickle.dump(best_pac, model_file)

with open('Models/tfidf_vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(tfidf_vectorizer, vectorizer_file)