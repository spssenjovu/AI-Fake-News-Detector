# AI Fake News Detector
An innovative machine learning project designed to detect fake news with a focus on transparency, trust signals, and ethical AI practices.

# Table of Contents
- Overview
- Features
- Installation
- Usage
- Model Details
- API Endpoints
- Contributing
- License

# Overview
AI News Detector is a Flask-based application that uses machine learning to classify
news articles as real or fake. It leverages TF-IDF vectorization and a 
PassiveAggressiveClassifier to analyse text credibility.

# Features
✅ Detects fake news using trained ML models
✅ Provides an API for real-time predictions
✅ Secure user authentication with Flask
✅ Supports multiple text formats for analysis

# Installation 

## Prerequisites
Ensure you have Python installed (recommended: Python 3.8+).

## Setup
Clone the repository and install dependencies:
git clone https://github.com/spssenjovu/AI-Fake-News-Detector.git
cd AI-Fake-News-Detector
pip install -r requirements.txt

# Usage 

## Run the Flask App
python app.py

Access the web interface at http://localhost:5000

## Example API Call
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"text": "Breaking news: AI is taking over!"}'

# Model Details
- Vectorization: TF-IDF
- Classifier: PassiveAggressiveClassifier
- Dataset: LIAR Dataset from Kaggle

# API Endpoints
| Endpoint  | Method | Description                  |
| ----------| -------| -----------------------------|
| /predict  | POST | Classifies news as real or fake|
| /register | POST | Registers a new user           |
| /login    | POST | Authenticates user login       |

# Contributing
Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (git checkout -b feature-branch)
3. Commit changes (git commit -m "Added new feature")
4. Push to GitHub (git push origin feature-branch)
5. Open a Pull Request

# License 
This project is licensed under the MIT License
