from newspaper import Article
def extract_article(url):
    """Extracts article text from the given news URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error extracting article from {url}: {e}")
        return None

# Test extraction
if __name__ == "__main__":
    test_url = "https://example.com/news-article"
    article_text = extract_article(test_url)
    if article_text:
        print("Article extracted successfully:")
        print(article_text[:500])  # Print first 500 characters
    else:
        print("Failed to extract article.")