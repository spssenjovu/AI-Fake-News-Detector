import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# Load the dataset
df = pd.read_csv('True.csv')
df1 = pd.read_csv('Fake.csv')

# Add a label column to each DataFrame
df['label'] = 'True'
df1['label'] = 'Fake'

# Concatenate the DataFrames
df = pd.concat([df, df1])

# Extract features and labels
X = df['text'].values
y = df['label'].values

# Initialize the TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)

# Initialize the PassiveAggressiveClassifier
pac = PassiveAggressiveClassifier(max_iter=50)

# Initialize StratifiedKFold
skf = StratifiedKFold(n_splits=5)

# Arrays to store the scores
accuracy_scores = []
conf_matrices = []

# Perform Stratified K-Fold Cross-Validation
for train_index, test_index in skf.split(X, y):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    # Fit and transform the data
    tfidf_train = tfidf_vectorizer.fit_transform(X_train)
    tfidf_test = tfidf_vectorizer.transform(X_test)

    # Train the classifier
    pac.fit(tfidf_train, y_train)

    # Predict on the test set
    y_pred = pac.predict(tfidf_test)

    # Calculate accuracy
    score = accuracy_score(y_test, y_pred)
    accuracy_scores.append(score)

    # Build confusion matrix
    conf_matrix = confusion_matrix(y_test, y_pred)
    conf_matrices.append(conf_matrix)

# Calculate the mean accuracy
mean_accuracy = np.mean(accuracy_scores)
print(f'Mean Accuracy: {mean_accuracy * 100:.2f}%')

# Aggregate confusion matrices
total_conf_matrix = np.sum(conf_matrices, axis=0)
print(f'Total Confusion Matrix:\n{total_conf_matrix}')

# Visualize accuracy scores
plt.figure(figsize=(10, 5))
plt.bar(range(1, len(accuracy_scores) + 1), accuracy_scores)
plt.xlabel('Fold')
plt.ylabel('Accuracy')
plt.title('Accuracy Scores for Each Fold')
plt.show()

# Visualize confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(total_conf_matrix, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()
