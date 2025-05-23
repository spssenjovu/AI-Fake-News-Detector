from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
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
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"

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


app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret')
csrf = CSRFProtect(app)

# User registration and login
@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@csrf.exempt
@app.route('/submit-login', methods=['POST'])
def submit_login():
    data = request.get_json()
    print("Received login data:", data)  # Debugging output

    if not data or "email" not in data or "password" not in data:
        return jsonify({"success": False, "message": "Invalid request format!"}), 400

    email = data.get("email")
    password = data.get("password")

    cursor.execute("SELECT password_hash FROM users WHERE email=%s", (email,))
    user_data = cursor.fetchone()

    if user_data and check_password_hash(user_data[0], password):
        session['email'] = email
        return jsonify({"success": True, "redirect": url_for('home')})
    else:
        return jsonify({"success": False, "message": "Invalid credentials."})

@app.route('/register')
def register():
    return render_template('register.html')

@csrf.exempt
@app.route('/submit-register', methods=['POST'])
def submit_register():
    print("Headers:", request.headers)
    print("Raw data:", request.data)
    data = request.get_json()
    if not data:
        print("❌ No JSON received! Request might be incorrectly formatted.")
        return jsonify({"success": False, "message": "Invalid request format!"}), 400
    
    print("✅ Received data:", data)  # Debugging log

    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match!"}), 400

    hashed_password = generate_password_hash(password)

    cursor.execute(
    "INSERT INTO users (firstname, lastname, email, password_hash) VALUES (%s, %s, %s, %s)",   
    (str(firstname), str(lastname), str(email), str(hashed_password))
) 
    mysql.commit()

    return jsonify({"success": True, "message": "Registration successful!", "redirect": url_for('login')})

# Loading the model and vectorizer
model_path = os.path.join(os.getcwd(), 'models', 'pac_model.pkl')
vectorizer_path = os.path.join(os.getcwd(), 'models', 'tfidf_vectorizer.pkl')

try:
    model = pickle.load(open(model_path, 'rb'))
    print("✅ Model loaded successfully!")
except FileNotFoundError:
    print(f"❌ Model file not found: {model_path}")
except pickle.UnpicklingError:
    print("❌ Error: Model file is corrupted or incompatible.")
except Exception as e:
    print(f"❌ Unexpected error loading model: {e}")

@app.route('/home', methods=['GET'])
def home():
    if 'email' in session:
        return render_template('main.html')  # ✅ Confirm this file exists in /templates
    else:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))
    
@app.route('/predict', methods=['POST'])
def predict():
    news_text = request.form.get("news")
    if not news_text:
        flash("Please enter news text.", "warning")
        return redirect(url_for('home'))

    # Process with AI model here
    prediction = model.predict([news_text])

    return render_template('main.html', result=prediction)



@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

