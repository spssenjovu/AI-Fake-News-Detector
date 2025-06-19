# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import logging, os, pickle, MySQLdb
from urllib.parse import urlparse
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from flask_wtf.csrf import CSRFProtect
from credibility import get_domain_trust, explain_prediction


from utils.preprocessing import preprocess_text
from scrapper.extractor import extract_multiple_articles
from routes.prediction import classify_news_articles

# === Initial Setup ===
load_dotenv()
logging.basicConfig(filename='app.log', level=logging.INFO)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'your_secret_key'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Lax',
    MYSQL_USER=os.getenv('MYSQL_USER'),
    MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD'),
    MYSQL_DB=os.getenv('MYSQL_DB')
)
csrf = CSRFProtect(app)

# === DB Connection ===
try:
    mysql = MySQLdb.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB']
    )
    cursor = mysql.cursor()
except Exception as e:
    logging.critical(f"Database connection failed: {e}")
    raise

# === Encryption Key ===
encryption_key = os.getenv("ENCRYPTION_KEY")
if not encryption_key:
    raise ValueError("❌ Missing ENCRYPTION_KEY in environment.")
fernet = Fernet(encryption_key)

# === Model Loading ===
try:
    model = pickle.load(open('Models/pac_model.pkl', 'rb'))
    vectorizer = pickle.load(open('Models/tfidf_vectorizer.pkl', 'rb'))
    logging.info("✅ Model and vectorizer loaded.")
except Exception as e:
    model, vectorizer = None, None
    logging.error(f"❌ Model/vectorizer loading failed: {e}")

# === Helpers ===
def get_decrypted_email():
    try:
        encrypted_email = session.get("email")
        return fernet.decrypt(encrypted_email.encode()).decode() if encrypted_email else None
    except Exception as e:
        logging.warning(f"Session decryption failed: {e}")
        return None

def get_domain_trust_score(url):
    domain = urlparse(url).netloc
    # Stub logic — replace with real API call
    trusted_sources = ['bbc.co.uk', 'reuters.com', 'theguardian.com']
    return "High" if domain in trusted_sources else "Unknown"

# === Routes ===
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/submit-login', methods=['POST'])
@csrf.exempt
def submit_login():
    data = request.get_json(force=True)
    email, password = data.get("email"), data.get("password")

    cursor.execute("SELECT password_hash FROM users WHERE email=%s", (email,))
    row = cursor.fetchone()

    if row and check_password_hash(row[0], password):
        session['email'] = fernet.encrypt(email.encode()).decode()
        flash("✅ Logged in!", "success")
        return jsonify(success=True, redirect=url_for('home'))
    return jsonify(success=False, message="Invalid credentials."), 401

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/submit-register', methods=['POST'])
@csrf.exempt
def submit_register():
    data = request.get_json(force=True)
    if data.get('password') != data.get('confirmPassword'):
        return jsonify(success=False, message="Passwords don't match"), 400

    hashed_pw = generate_password_hash(data['password'])
    try:
        cursor.execute("""
            INSERT INTO users (firstname, lastname, email, password_hash)
            VALUES (%s, %s, %s, %s)
        """, (data['firstname'], data['lastname'], data['email'], hashed_pw))
        mysql.commit()
        return jsonify(success=True, redirect=url_for('login'))
    except MySQLdb.Error as e:
        return jsonify(success=False, message=f"DB Error: {e}"), 500

@app.route('/home')
def home():
    if 'email' not in session:
        flash("⚠️ You must be logged in.", "warning")
        return redirect(url_for('login'))
    return render_template('main.html')

@app.route('/predict', methods=['POST'])
@csrf.exempt
def predict():
    if not model or not vectorizer:
        return jsonify(error="Model not loaded"), 500
    if 'email' not in session:
        return redirect(url_for('login'))

    data = request.get_json(force=True)
    text = preprocess_text(data.get('news', ''))

    try:
        vec = vectorizer.transform([text])
        confidence = model.decision_function(vec)[0]
        label = "Fake" if confidence > 0.5 else "Real"
        return jsonify(prediction=label, confidence=round(confidence, 3))
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify(error="Prediction failed"), 500

@app.route('/predict-news')
def predict_news():
    urls = request.args.getlist('urls')
    if not urls:
        return jsonify(error="No URLs provided"), 400

    articles = extract_multiple_articles(urls)
    cleaned = [preprocess_text(a) for a in articles]
    vectors = vectorizer.transform(cleaned)
    predictions = model.predict(vectors)

    results = []
    for url, pred, vec in zip(urls, predictions, vectors):
        trust_info = get_domain_trust(url)
        confidence = model.decision_function(vec)[0]
        explanation = explain_prediction(["sensational", "all-caps", "fraud", "breaking", "exclusive"])  # Mock

        results.append({
            "url": url,
            "classification": "Fake" if pred == 1 else "Real",
            "confidence": round(confidence, 3),
            "trust_level": trust_info["trust_level"],
            "source": trust_info["source_name"],
            "explanation": explanation
        })

    return jsonify(results=results)

@app.route('/logout')
def logout():
    session.clear()
    flash("ℹ️ Logged out.", "info")
    return redirect(url_for('login'))

# === Error Handlers ===
@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error='Unauthorized'), 401

@app.errorhandler(500)
def server_error(e):
    logging.error("🚨 Internal Server Error", exc_info=True)
    return jsonify(error='Internal server error'), 500

# === Entry Point ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)