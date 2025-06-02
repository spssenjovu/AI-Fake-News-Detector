from newspaper import Article
import validators

def extract_article(url):
    """Extracts article text from the given news URL."""
    if not validators.url(url):  # Validate URL format
        return {"error": "Invalid URL format."}

    try:
        article = Article(url)
        article.download()
        article.parse()
        return {"url": url, "text": article.text} if article.text else {"error": "No content extracted."}
    except Exception as e:
        return {"error": f"Error extracting article: {e}"}

# Batch processing
def extract_multiple_articles(urls):
    return [extract_article(url) for url in urls]

# Test extraction
if __name__ == "__main__":
    test_urls = ["https://example.com/news-article", "https://another-news-site.com/story"]
    results = extract_multiple_articles(test_urls)
    for result in results:
        print(result)