from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import pickle
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb
import os
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__,template_folder='./templates',static_folder='./static')

app.secret_key = 'your_secret_key'  # Change this to a secure random key

# Load the trained model and vectorizer
# model = pickle.load(open('path/to/pac_model.pkl', 'rb'))  # Update the path to your model file
# vectorizer = pickle.load(open('path/to/tfidf_vectorizer.pkl', 'rb'))  # Update the path to your vectorizer file

# Database connection
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Database#2010'
app.config['MYSQL_DB'] = 'ai_connection'

try:
    mysql = MySQLdb.connect(
        host="127.0.0.1",
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    cursor = mysql.cursor()
    print("✅ Database connected successfully!")
except MySQLdb.Error as e:
    print(f"❌ Error connecting to MySQL: {e}")


@app.route('/test-db')
def test_db():
    try:
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        return f"Connected to database: {db_name[0]}"
    except MySQLdb.Error as e:
        return f"Database connection error: {e}"


app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret')
csrf = CSRFProtect(app)

# User registration and login

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/submit-login', methods=['POST'])
def submit_login():
    email = request.form['email']
    password = request.form['password']

    cursor.execute("SELECT password_hash FROM users WHERE email=%s", (email,))
    user_data = cursor.fetchone()

    if user_data and check_password_hash(user_data[0], password):
        session['email'] = email
        return redirect(url_for('home'))
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/home', methods=['GET'])
def home():
    if 'email' in session:
        return "Welcome to the AI News Detector!"
    else:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

try:
    model = pickle.load(open('models/pac_model.pkl', 'rb'))
    vectorizer = pickle.load(open('models/tfidf_vectorizer.pkl', 'rb'))
except FileNotFoundError:
    print("Model or vectorizer file missing! Check paths.")
    model, vectorizer = None, None


@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

