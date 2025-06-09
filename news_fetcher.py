import requests
import os
from dotenv import load_dotenv

# Load environment variables securely
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/top-headlines?country=gb&page={page}&pageSize={limit}&apiKey=" + API_KEY

def get_news_articles(page=1, limit=10):
    """Fetches news articles securely with proper error handling."""
    url = BASE_URL.format(page=page, limit=limit)

    try:
        response = requests.get(url, timeout=5)  # Timeout prevents hanging requests
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        data = response.json()
        if "articles" not in data or not data["articles"]:
            return ["Error: No articles found."]

        return [
            f"{article.get('title', 'No Title Available')} - {article.get('description', 'No Description Available')}"
            for article in data.get("articles", [])[:limit]
        ]

    except requests.exceptions.Timeout:
        return ["Error: API request timed out."]
    except requests.exceptions.ConnectionError:
        return ["Error: Network connection failed."]
    except requests.exceptions.RequestException as e:
        return [f"Error fetching news: {e}"]
    
    