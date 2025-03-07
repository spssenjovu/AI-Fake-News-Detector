import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import itertools
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score, classification_report

# Load the dataset
df_true = pd.read_csv('True.csv')
df_fake = pd.read_csv('Fake.csv')

# Add a label column to each DataFrame
df_true['label'] = 'True'
df_fake['label'] = 'Fake'

# Concatenate the DataFrames
df = pd.concat([df_true, df_fake])



# Extract features and labels
X = df['text'].values
y = df['label'].values


# Split the data into 60% training and 40% testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, stratify=y, random_state=42)

# Initialize the TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)

# Transform the data 
tfidf_train = tfidf_vectorizer.fit_transform(X_train)
tfidf_test = tfidf_vectorizer.transform(X_test)

# Initialize the PassiveAggressiveClassifier
pac = PassiveAggressiveClassifier(max_iter=50)

# Train the classifier
pac.fit(tfidf_train, y_train)

# Predict on the training set
y_train_pred = pac.predict(tfidf_train)

# Predict on the testing set
y_test_pred = pac.predict(tfidf_test)

# Perform cross-validation
cv_scores = cross_val_score(pac, tfidf_train, y_train, cv=5, scoring='accuracy')

# Calculate the accuracy on the training set
train_accuracy = accuracy_score(y_train, y_train_pred)
print(f'Training Accuracy: {train_accuracy * 100:.2f}%')

# Precision score on the training set
train_precision = precision_score(y_train, y_train_pred, pos_label='True')
print(f'Training Precision: {train_precision * 100:.2f}%')

# Recall score on the training set
train_recall = recall_score(y_train, y_train_pred, pos_label='True')
print(f'Training Recall: {train_recall * 100:.2f}%')

# F1 score on the training set
train_f1 = f1_score(y_train, y_train_pred, pos_label='True')
print(f'Training F1 Score: {train_f1 * 100:.2f}%')

# ROC AUC score on the training set
train_roc_auc = roc_auc_score([1 if label == 'True' else 0 for label in y_train], [1 if label == 'True' else 0 for label in y_train_pred])
print(f'Training ROC AUC Score: {train_roc_auc * 100:.2f}%')

# Print cross-validation scores
print(f'Cross-Validation Accuracy Scores: {cv_scores}')




# Classification report 
print(classification_report(y_test, y_test_pred))

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

# Visualize confusion matrix for the testing set
#accuracy score on the test data
score = accuracy_score(y_test, y_test_pred)
print(f'Accuracy: {round(score*100,2)}%')
cm = confusion_matrix(y_test, y_test_pred)
plot_confusion_matrix(cm, classes=['FAKE Data', 'REAL Data'])
plt.show()

# Save the trained model
with open('Models/pac_model.pkl', 'wb') as model_file:
    pickle.dump(pac, model_file)

# Save the TfidfVectorizer
with open('Models/tfidf_vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(tfidf_vectorizer, vectorizer_file)
