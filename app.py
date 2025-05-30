from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import pickle
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
import MySQLdb # type: ignore
import os
from flask_wtf.csrf import CSRFProtect # type: ignore

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Set only once

# Database configuration
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Database#2010'
app.config['MYSQL_DB'] = 'ai_connection'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Connect to MySQL
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

# Test database connection
@app.route('/test-db')
def test_db():
    try:
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        return f"Connected to database: {db_name[0]}"
    except MySQLdb.Error as e:
        return f"Database connection error: {e}"

# User login page
@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

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
        session['email'] = email
        flash("✅ Login successful!", "success")
        return jsonify({"success": True, "redirect": url_for('home')})
    else:
        flash("❌ Invalid credentials. Try again.", "danger")
        return jsonify({"success": False, "message": "Invalid credentials."})

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

# Load the model and vectorizer
model_path = os.path.join(os.getcwd(), 'models', 'pac_model.pkl')
try:
    model = pickle.load(open(model_path, 'rb'))
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# Main page (requires login)
@app.route('/home', methods=['GET'])
def home():
    if 'email' in session:
        return render_template('main.html')
    else:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))

# Prediction endpoint (requires login)
@app.route('/predict', methods=['POST'])
def predict():
    if 'email' not in session:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))

    news_text = request.form.get("news")
    if not news_text:
        flash("Please enter news link.", "warning")
        return redirect(url_for('home'))

    if not model:
        flash("Model not loaded.", "danger")
        return redirect(url_for('home'))

    prediction = model.predict([news_text])
    return render_template('main.html', result=prediction)

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Settings 
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