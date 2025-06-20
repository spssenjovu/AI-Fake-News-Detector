from urllib.parse import urlparse

TRUSTED_DOMAINS = {
    "bbc.co.uk": {"level": "High", "source": "BBC"},
    "reuters.com": {"level": "High", "source": "Reuters"},
    "theguardian.com": {"level": "High", "source": "The Guardian"},
    # Add more as needed
}

def get_domain_trust(url):
    domain = urlparse(url).netloc.replace("www.", "")
    info = TRUSTED_DOMAINS.get(domain, {"level": "Unknown", "source": "Not Verified"})
    return {
        "domain": domain,
        "trust_level": info["level"],
        "source_name": info["source"]
    }

def explain_prediction(features):
    return "This prediction is based on features: " + ", ".join(features)