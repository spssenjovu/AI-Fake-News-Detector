from flask import Flask, request, jsonify
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)  # Initialize the Flask app

# Load the trained model and vectorizer
model = pickle.load(open('pac_model.pkl', 'rb'))
vectorizer = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the AI News Detector!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json['text']
    # Transform the input text using the vectorizer
    transformed_data = vectorizer.transform([data])
    # Predict the label using the loaded model
    prediction = model.predict(transformed_data)
    return jsonify({'prediction': prediction[0]})

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app
