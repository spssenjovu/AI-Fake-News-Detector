from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, static_folder='Desktop/public', template_folder='Desktop/public')
app.secret_key = 'your_secret_key'  # Change this to a secure random key
csrf = CSRFProtect(app)

# Load the trained model and vectorizer
model = pickle.load(open('path/to/pac_model.pkl', 'rb'))  # Update the path to your model file
vectorizer = pickle.load(open('path/to/tfidf_vectorizer.pkl', 'rb'))  # Update the path to your vectorizer file

# Mock user data for example purposes
users = {
    'email': generate_password_hash('your_password')
}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/submit-login', methods=['POST'])
@csrf.exempt
def submit_login():
    email = request.form['email']
    password = request.form['password']
    
    if email in users and check_password_hash(users[email], password):
        session['email'] = email
        return redirect(url_for('home'))
    else:
        return "Invalid credentials!", 401

@app.route('/home', methods=['GET'])
def home():
    if 'username' in session:
        return "Welcome to the AI News Detector!"
    else:
        return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
@csrf.exempt
def predict():
    if 'email' not in session:
        return "Unauthorized", 401

    data = request.json['text']
    # Transform the input text using the vectorizer
    transformed_data = vectorizer.transform([data])
    # Predict the label using the loaded model
    prediction = model.predict(transformed_data)
    return jsonify({'prediction': prediction[0]})

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app
