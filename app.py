from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import pickle
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import base64
import os
from flask_wtf.csrf import CSRFProtect
from scrapper.extractor import extract_multiple_articles
from routes.prediction import classify_news_articles

# Load environment variables
load_dotenv()

# Ensure the encryption key is set
fernet = Fernet(os.getenv("ENCRYPTION_KEY"))


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.secret_key = app.config['SECRET_KEY']

# CSRF protection
csrf = CSRFProtect(app)

# Database configuration
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize MySQL connection and cursor
mysql = MySQLdb.connect(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    user=app.config['MYSQL_USER'],
    passwd=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)
cursor = mysql.cursor()

# Load the model
model_path = os.path.join(os.getcwd(), 'models', 'pac_model.pkl')
try:
    model = pickle.load(open(model_path, 'rb'))
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# User login page
@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

def get_decrypted_email():
    """Retrieve and decrypt the logged-in user's email."""
    encrypted_email = session.get("email")
    if encrypted_email:
        return fernet.decrypt(encrypted_email.encode()).decode()
    return None  # User not logged in


# Handle login submission
@app.route('/submit-login', methods=['POST'])
@csrf.exempt
def submit_login():
    if request.content_type != "application/json":
        return jsonify({"success": False, "message": "Unsupported media type"}), 415

    data = request.get_json(force=True)
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON format!"}), 400

    email = data.get("email")
    password = data.get("password")

    cursor.execute("SELECT password_hash FROM users WHERE email=%s", (email,))
    user_data = cursor.fetchone()

    if user_data and check_password_hash(user_data[0], password):
        encrypted_email = fernet.encrypt(email.encode()).decode()  # Encrypt email
        session['email'] = encrypted_email  # Store encrypted email in session
        flash("✅ Login successful!", "success")
        return jsonify({"success": True, "redirect": url_for('home')})
    else:
        flash("❌ Invalid credentials. Try again.", "danger")
        return jsonify({"success": False, "message": "Invalid credentials."}), 401



# Registration page
@app.route('/register')
def register():
    return render_template('register.html')

# Handle registration submission
@app.route('/submit-register', methods=['POST'])
@csrf.exempt
def submit_register():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request format!"}), 400

    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match!"}), 400

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute(
            "INSERT INTO users (firstname, lastname, email, password_hash) VALUES (%s, %s, %s, %s)",
            (firstname, lastname, email, hashed_password)
        )
        mysql.commit()
    except MySQLdb.Error as e:
        return jsonify({"success": False, "message": f"Database error: {e}"}), 500

    return jsonify({"success": True, "message": "Registration successful!", "redirect": url_for('login')})

# Main page (requires login)
@app.route('/home', methods=['GET'])
def home():
    if 'email' in session:
        decrypted_email = fernet.decrypt(session.get("email").encode()).decode()  # 🔓 Decrypt email
        return render_template('main.html')
    else:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))

# Prediction endpoint (requires login)
@app.route('/predict', methods=['POST'])
@csrf.exempt
def predict():
    if 'email' not in session:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))
    
    decrypted_email = fernet.decrypt(session.get("email").encode()).decode()  # 🔓 Decrypt email
    print(f"User {decrypted_email} is making a prediction!")  # Log action securely

    data = request.get_json(silent=True)
    if not data or 'news' not in data:
        return jsonify({"error": "Invalid input format"}), 400

    news_input = data['news']
    if news_input.startswith("http://") or news_input.startswith("https://"):
        articles = extract_multiple_articles([news_input])
        if not articles or not articles[0]:
            return jsonify({"error": "Failed to extract article from URL"}), 400
        news_text = articles[0]
    else:
        news_text = news_input

    if not model:
        return jsonify({"error": "Model not loaded"}), 500

    prediction = model.predict([news_text])
    return jsonify({"prediction": prediction[0]})

# News classification endpoint (batch)
@app.route('/predict-news', methods=['GET'])
def predict_news():
    urls = request.args.getlist('urls')
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    articles = extract_multiple_articles(urls)
    if not articles:
        return jsonify({"error": "Failed to extract articles from provided URLs"}), 400

    predictions = classify_news_articles(articles)
    return jsonify({"results": predictions})

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Settings page
@app.route('/settings')
def settings():
    return render_template('settings.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("ℹ️ You have been logged out.", "info")
    return redirect(url_for('login'))

# Error handlers
@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(500)
def server_error(error):
    flash("🚨 Internal Server Error. Please try again later.", "danger")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)