from newspaper import Article
import validators
import time

def extract_article(url, retries=2, delay=2):
    """Extracts article text from the given news URL with retry logic."""
    if not validators.url(url):
        print(f" Invalid URL: {url}")
        return ""

    for attempt in range(retries):
        try:
            article = Article(url)
            article.download()
            article.parse()
            if article.text and len(article.text.strip()) > 100:
                print(f" Extracted from {url} (length: {len(article.text)} chars)")
                return article.text
            else:
                print(f" No usable content from {url}")
                return ""
        except Exception as e:
            print(f" Error extracting {url} (attempt {attempt + 1}): {e}")
            time.sleep(delay)

    return ""

def extract_multiple_articles(urls):
    """Extracts articles from a list of URLs."""
    return [extract_article(url) for url in urls]

# Test extraction
if __name__ == "__main__":
    test_urls = [
        "https://www.reuters.com/world/europe/ukraine-war-latest-updates-2025-08-10/",
        "https://www.bbc.com/news/world-12345678"
    ]
    results = extract_multiple_articles(test_urls)
    for i, result in enumerate(results):
        print(f"\n--- Article {i+1} ---\n{result[:500]}")