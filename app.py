from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pickle
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='Desktop/public', template_folder='Desktop/public')
app.secret_key = 'your_secret_key'  # Change this to a secure random key

# Load the trained model and vectorizer
# model = pickle.load(open('path/to/pac_model.pkl', 'rb'))  # Update the path to your model file
# vectorizer = pickle.load(open('path/to/tfidf_vectorizer.pkl', 'rb'))  # Update the path to your vectorizer file

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
    if 'email' in session:
        return "Welcome to the AI News Detector!"
    else:
        return redirect(url_for('login'))

try:
    model = pickle.load(open('path/to/pac_model.pkl', 'rb'))
    vectorizer = pickle.load(open('path/to/tfidf_vectorizer.pkl', 'rb'))
except FileNotFoundError:
    print("Model or vectorizer file not found. Please check the path.")


@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

