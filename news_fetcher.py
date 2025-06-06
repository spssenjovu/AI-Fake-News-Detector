import requests
import os

API_KEY = "069f64da73e34e95a9fc9d974e8afb30"
URL = f"https://newsapi.org/v2/top-headlines?country=gb&apiKey={API_KEY}"

def get_news_articles(limit=10):
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
        data = response.json()

        # Ensure "articles" exists in the API response
        if not data or "articles" not in data:
            return ["Error: No articles found. Check API response."]

        articles = []
        for article in data.get("articles", [])[:limit]:
            title = article.get("title", "No Title Available")
            description = article.get("description", "No Description Available")
            articles.append(f"{title} - {description}")

        return articles if articles else ["No articles found."]
    
    except requests.exceptions.RequestException as e:
        return [f"Error fetching news: {e}"]