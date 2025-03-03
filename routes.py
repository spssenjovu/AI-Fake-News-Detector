from flask import Flask
from app import app
from user import user

@app.route('/')
def home():
    return 'Home Page'  # Return a simple message