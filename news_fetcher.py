import os
import requests
from dotenv import load_dotenv

# Load environment variables securely
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

def get_news_articles(page=1, limit=10):
    """Fetches top UK news headlines with structured metadata and safe error handling."""
    
    if not API_KEY:
        return [{"error": "Missing API key. Please check your .env file."}]
    
    endpoint = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "gb",
        "page": page,
        "pageSize": limit,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(endpoint, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if not data.get("articles"):
            return [{"error": "No articles found."}]

        articles = []
        for article in data["articles"][:limit]:
            articles.append({
                "title": article.get("title", "No Title"),
                "description": article.get("description", "No Description"),
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url")
            })

        return articles

    except requests.exceptions.Timeout:
        return [{"error": "API request timed out."}]
    except requests.exceptions.ConnectionError:
        return [{"error": "Network connection failed."}]
    except requests.exceptions.RequestException as e:
        return [{"error": f"Request error: {e}"}]