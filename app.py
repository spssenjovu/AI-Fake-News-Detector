from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import pickle
from werkzeug.security import generate_password_hash, check_password_hash
from utils.preprocessing import preprocess_text
import MySQLdb
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os
from flask_wtf.csrf import CSRFProtect
from scrapper.extractor import extract_multiple_articles
from routes.prediction import classify_news_articles
from utils.credibility_layer import get_domain_trust, explain_prediction

# Load environment variables
load_dotenv()

# Encryption key setup
encryption_key = os.getenv("ENCRYPTION_KEY")
if not encryption_key:
    raise ValueError("❌ ENCRYPTION_KEY is missing! Check your .env file.")
fernet = Fernet(encryption_key)

# Flask app setup
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

# Load the trained model
model_path = os.path.join(os.getcwd(), 'Models', 'pac_model.pkl')
try:
    model = pickle.load(open(model_path, 'rb'))
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# Load the trained vectorizer
vectorizer_path = os.path.join(os.getcwd(), 'Models', 'tfidf_vectorizer.pkl')
try:
    vectorizer = pickle.load(open(vectorizer_path, 'rb'))
    print("✅ Vectorizer loaded successfully!")
except Exception as e:
    print(f"❌ Error loading vectorizer: {e}")
    vectorizer = None

# Helper to decrypt email
def get_decrypted_email():
    encrypted_email = session.get("email")
    if encrypted_email:
        return fernet.decrypt(encrypted_email.encode()).decode()
    return None

# Routes

@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

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
        encrypted_email = fernet.encrypt(email.encode()).decode()
        session['email'] = encrypted_email
        flash("✅ Login successful!", "success")
        return jsonify({"success": True, "redirect": url_for('home')})
    else:
        flash("❌ Invalid credentials. Try again.", "danger")
        return jsonify({"success": False, "message": "Invalid credentials."}), 401

@app.route('/register')
def register():
    return render_template('register.html')

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

@app.route('/home', methods=['GET'])
def home():
    if 'email' in session:
        decrypted_email = get_decrypted_email()
        return render_template('main.html')
    else:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
@csrf.exempt
def predict():
    if 'email' not in session:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))

    decrypted_email = get_decrypted_email()
    print(f"User {decrypted_email} is making a prediction!")  # Log action securely

    data = request.get_json(silent=True)
    if not data or 'news' not in data:
        return jsonify({"error": "Invalid input format"}), 400

    news_text = data['news']

    if not model or not vectorizer:
        return jsonify({"error": "Model or vectorizer not loaded"}), 500

    try:
        # Preprocess and vectorize the input
        cleaned_text = preprocess_text(news_text)
        news_text_vectorized = vectorizer.transform([cleaned_text])
        prediction = model.predict(news_text_vectorized)
        label = "Fake" if prediction[0] == 1 else "Real"
        return jsonify({"prediction": label})
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": "Prediction failed"}), 500

@app.route('/predict-news', methods=['GET'])
def predict_news():
    urls = request.args.getlist('urls')
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    articles = extract_multiple_articles(urls)
    print("🔎 Extracted:", articles)

    for i, article in enumerate(articles):
        print(f"[{i}] Extracted preview: {article[:200]}")

    results = []

    for url, article in zip(urls, articles):
        if not article or len(article.strip()) < 100:
            trust_info = get_domain_trust(url)
            results.append({
                "url": url,
                "classification": "Undetermined",
                "confidence": 0,
                "trust_level": trust_info.get("trust_level", "Unknown"),
                "source": trust_info.get("source_name", "Not Verified"),
                "explanation": "⚠️ Could not extract enough article content to make a reliable prediction."
            })
            continue

        cleaned_text = preprocess_text(article)
        text_vector = vectorizer.transform([cleaned_text])
        pred = model.predict(text_vector)[0]
        confidence = model.decision_function(text_vector)[0]
        trust_info = get_domain_trust(url)
        explanation = explain_prediction(["sensational", "fraud", "breaking", "exclusive"])  # Placeholder

        results.append({
            "url": url,
            "classification": "Fake" if pred == 1 else "Real",
            "confidence": round(float(confidence), 3),
            "trust_level": trust_info.get("trust_level", "Unknown"),
            "source": trust_info.get("source_name", "Not Verified"),
            "explanation": explanation
        })

    return jsonify({"results": results})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

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