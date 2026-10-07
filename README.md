# AI Fake News Detector

A Flask-based web application for classifying online news content as likely real or fake using a trained text-classification model. The project combines machine learning, article extraction, and a credibility layer to provide a practical newsroom-style verification workflow.

## Overview

This application analyzes article text and estimates whether it is more likely to be fake or real. It uses a TF-IDF feature pipeline with a Passive Aggressive classifier, trained on labeled political claim data and adapted for article-level classification. The system also evaluates source credibility using a lightweight trust layer and can classify one or more URLs through a web endpoint.

## Features

- Fake/real news classification using a trained ML model
- URL-based article extraction and preprocessing
- Source credibility assessment for article domains
- User registration and login flow
- Local deployment with Docker support
- Model persistence for reuse without retraining

## Project Structure

```text
.
├── app.py                     # Flask application entry point
├── main.py                   # Model training pipeline
├── requirements.txt          # Python dependencies
├── compose.yaml              # Docker Compose configuration
├── Dockerfile                # Container definition
├── .env.example              # Environment template
├── Models/                   # Saved model artifacts
├── routes/                   # Route-level application logic
├── utils/                    # Preprocessing and credibility utilities
├── scrapper/                 # Article extraction logic
├── templates/                # Front-end templates
├── static/                  # Static assets
├── train.tsv                # Training data
├── valid.tsv                # Validation data
├── test.tsv                 # Test data
├── README.md                 # Project documentation
└── .gitignore
```

## Model Details

The system uses a text-based classification pipeline built with:

- TF-IDF vectorization (unigrams and bigrams)
- Random oversampling for class balancing during training
- Passive Aggressive Classifier as the final estimator
- CalibratedClassifierCV for probability estimation
- Validation-selected fake-class threshold for final decisioning

The model is trained from the LIAR dataset, which contains short claims rather than full news articles. Because of this, predictions on full articles are estimates rather than definitive fact checks.

Training command:

```bash
python main.py
```

This writes the trained pipeline to:

```text
Models/news_pipeline.pkl
```

## Prerequisites

- Python 3.10+
- MySQL database
- Docker (optional, for containerized setup)
- Virtual environment recommended

## Environment Configuration

Create a local environment file based on `.env.example` and populate the variables required by the app.

Example configuration:

```env
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_fernet_key
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=your_database_name
```

Generate secure values:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Installation

Clone the repository:

```bash
git clone https://github.com/spssenjovu/AI-Fake-News-Detector.git
cd AI-Fake-News-Detector
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate   # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask server:

```bash
python app.py
```

Then open the app in your browser:

```text
http://127.0.0.1:5000
```

### Docker Setup

To run with Docker Compose:

```bash
docker compose up --build
```

The app will be available at:

```text
http://localhost:5000
```

## Application Flow

1. User registers or logs in
2. User enters a news URL in the application
3. The app extracts article text and preprocesses it
4. The model predicts whether the content is likely fake or real
5. The system returns the classification and confidence score
6. The credibility layer adds a trust signal derived from the domain

## API Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/` | GET | Login page |
| `/register` | GET | Registration page |
| `/submit-login` | POST | Authenticate user |
| `/submit-register` | POST | Create a new user account |
| `/home` | GET | Main application page |
| `/predict-news` | GET | Classify one or more article URLs |
| `/about` | GET | About page |
| `/settings` | GET | User settings page |

### Example Prediction Request

```bash
curl "http://localhost:5000/predict-news?urls=https://example.com/article" 
```

## Usage Notes

- The application is intended for local development and experimentation.
- Predictions are probabilistic estimates and should not be treated as definitive truth verification.
- Article classification quality depends on text quality, source content, and dataset alignment.
- The project is best suited for educational, research, and prototype use cases.

## Limitations

- The model is trained on short political statements, not a broad cross-domain news corpus.
- Full-article classification may be less reliable than claim-level classification.
- Source trust signals are heuristics and should be interpreted as supporting context, not standalone evidence.
- The project does not yet provide a production-grade security or deployment model for public internet use.

## Contributing

Contributions are welcome. To contribute:

```bash
git checkout -b feature/your-feature-name
# make your changes
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

Then open a pull request in the repository.

## License

This project does not currently include a license file. If you intend to share or distribute it publicly, consider adding an open-source license such as MIT or Apache 2.0.

## Contact

For questions or collaboration opportunities, contact the repository owner or open an issue in the project.

