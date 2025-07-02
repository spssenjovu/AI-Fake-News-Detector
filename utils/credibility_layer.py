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

def compute_credibility_score(confidence, trust_level, flags=None):
    trust_map = {
        "High": 1.0,
        "Medium": 0.7,
        "Low": 0.4,
        "Unknown": 0.5
    }
    trust_factor = trust_map.get(trust_level, 0.5)

    penalty = 0.0
    if flags:
        penalty = min(len(flags) * 0.05, 0.2)  # Cap penalty

    raw_score = (confidence * 0.5) + (trust_factor * 0.5) - penalty
    return round(max(0.0, min(raw_score, 1.0)), 3)