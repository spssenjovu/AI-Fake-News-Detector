import os
import joblib
import MySQLdb
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

# Local imports
from scrapper.extractor import extract_article
from routes.prediction import preprocess_and_classify
from utils.credibility_layer import get_domain_trust

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')
app.secret_key = app.config['SECRET_KEY']

# App configuration
app.config.update(
    MYSQL_USER=os.getenv('MYSQL_USER'),
    MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD'),
    MYSQL_DB=os.getenv('MYSQL_DB'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Security setup
csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# Encryption setup
encryption_key = os.getenv("ENCRYPTION_KEY")
if not encryption_key:
    raise ValueError("Missing ENCRYPTION_KEY.")
fernet = Fernet(encryption_key)

# MySQL connection
try:
    mysql = MySQLdb.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB']
    )
    cursor = mysql.cursor()
except MySQLdb.Error as e:
    raise RuntimeError(f"Database connection failed: {e}")

# Load the complete pipeline when available, with support for existing artifacts.
try:
    model_path = os.path.join("Models", "news_pipeline.pkl")
    if os.path.exists(model_path):
        artifact = joblib.load(model_path)
        if isinstance(artifact, dict) and "model" in artifact:
            model = artifact["model"]
            fake_threshold = float(artifact.get("fake_threshold", 0.5))
        else:
            model = artifact
            fake_threshold = 0.5
        vectorizer = None
        MODEL_VERSION = "2.0.0"
    else:
        model = joblib.load(os.path.join("Models", "pac_model.pkl"))
        vectorizer = joblib.load(os.path.join("Models", "tfidf_vectorizer.pkl"))
        fake_threshold = 0.5
        MODEL_VERSION = "1.0.0"
except Exception as e:
    raise RuntimeError(f"Model loading failed: {e}")

# Helper function
def get_decrypted_email():
    enc = session.get("email")
    return fernet.decrypt(enc.encode()).decode() if enc else None

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/submit-login', methods=['POST'])
@csrf.exempt
@limiter.limit("10 per minute")
def submit_login():
    if request.content_type != "application/json":
        return jsonify({"success": False, "message": "Unsupported media type"}), 415

    data = request.get_json(force=True)
    email, password = data.get("email"), data.get("password")

    try:
        cursor.execute("SELECT password_hash FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
    except MySQLdb.Error as e:
        return jsonify({"success": False, "message": f"DB error: {e}"}), 500

    if user and check_password_hash(user[0], password):
        session['email'] = fernet.encrypt(email.encode()).decode()
        flash("Login successful!", "success")
        return jsonify({"success": True, "redirect": url_for('home')})
    else:
        flash("Invalid credentials.", "danger")
        return jsonify({"success": False, "message": "Invalid credentials."}), 401

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/submit-register', methods=['POST'])
@csrf.exempt
@limiter.limit("10 per minute")
def submit_register():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match!"}), 400

    hashed = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO users (firstname, lastname, email, password_hash) VALUES (%s, %s, %s, %s)",
            (firstname, lastname, email, hashed)
        )
        mysql.commit()
    except MySQLdb.IntegrityError:
        return jsonify({"success": False, "message": "Email already registered."}), 409
    except MySQLdb.Error as e:
        return jsonify({"success": False, "message": f"Database error: {e}"}), 500

    return jsonify({"success": True, "redirect": url_for('login')})

@app.route('/home')
def home():
    if 'email' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    return render_template('main.html')

@app.route('/predict-news', methods=['GET'])
@limiter.limit("30 per minute")
def predict_news():
    urls = request.args.getlist('urls')
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    results = []
    for url in urls:
        article = extract_article(url)
        trust_info = get_domain_trust(url)
        trust_level = trust_info.get("trust_level", "Unknown")
        source = trust_info.get("source_name", "Not Verified")

        if not article or len(article.strip()) < 100:
            results.append({
                "url": url,
                "classification": "Undetermined",
                "confidence": 0,
                "trust_level": trust_level,
                "source": source,
                "explanation": "Article too short or unavailable.",
                "model_version": MODEL_VERSION
            })
            continue

        try:
            predictions = preprocess_and_classify(
                [article],
                model=model,
                vectorizer=vectorizer,
                fake_threshold=fake_threshold,
            )
            pred_result = predictions[0]

            results.append({
                "url": url,
                "classification": pred_result["classification"],
                "confidence": pred_result["confidence"],
                "confidence_scores": pred_result["confidence_scores"],
                "trust_level": trust_level,
                "source": source,
                "explanation": (
                    "Text-pattern estimate, not an independent fact-check. "
                    "The model was trained on short claims, so full-article results may be less reliable."
                ),
                "model_version": MODEL_VERSION
            })
        except Exception as e:
            results.append({
                "url": url,
                "classification": "Error",
                "confidence": 0,
                "explanation": str(e),
                "model_version": MODEL_VERSION
            })

    return jsonify({"results": results})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/settings')
def settings():
    if 'email' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    try:
        decrypted_email = get_decrypted_email()
    except Exception as e:
        decrypted_email = "Unavailable"
        print("Decryption error:", e)

    return render_template('settings.html', email=decrypted_email)

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Error handlers
@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(500)
def internal_error(e):
    flash("Internal Server Error.", "danger")
    return jsonify({'error': 'Internal server error'}), 500

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)