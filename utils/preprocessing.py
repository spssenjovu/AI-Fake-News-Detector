import re

def preprocess_text(text):
    """Cleans text for classification."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\W+', ' ', text)  # Remove special characters
    text = text.strip()  # Remove extra spaces
    return text