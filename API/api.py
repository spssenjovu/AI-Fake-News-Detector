from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/your_database_name"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return 'Home Page'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})
        if user and bcrypt.check_password_hash(user['password'], password):
            return 'Login successful'
        else:
            return 'Invalid email or password'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        mongo.db.users.insert_one({'email': email, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
