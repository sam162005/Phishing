import numpy as np
import re
from feature import FeatureExtraction
from urllib.parse import urlparse

def calculate_trust_score(url, prediction, features=None):
    """
    Calculate a dynamic trust score based on URL features, model prediction, and real-time analysis.
    Returns a score from 0 to 100.
    """
    score = 60  # Higher base score for legitimate sites

    if features is None:
        try:
            obj = FeatureExtraction(url)
            features = obj.getFeaturesList()
        except:
            features = []

    # Major adjustment based on model prediction
    if prediction == 1:
        score += 25  # Safe prediction significantly boosts score
    else:
        score -= 45  # Phishing prediction heavily reduces score

    # Enhanced feature-based adjustments with higher weights
    if len(features) >= 30:
        # Critical positive features (high weight)
        if features[7] == 1:  # HTTPS
            score += 15
        if features[23] == 1:  # Domain age >= 6 months
            score += 12
        if features[24] == 1:  # DNS recording
            score += 8

        # Important positive features
        if features[0] == 1:  # Not using IP
            score += 8
        if features[2] == 1:  # Not short URL
            score += 7
        if features[8] == 1:  # Domain registration length
            score += 6

        # Critical negative features (high penalty)
        if features[0] == -1:  # Using IP
            score -= 20
        if features[2] == -1:  # Short URL
            score -= 18
        if features[3] == -1:  # Contains @
            score -= 15

        # Moderate negative features
        if features[4] == -1:  # Redirecting
            score -= 8
        if features[5] == -1:  # Prefix/Suffix
            score -= 7
        if features[6] == -1:  # Many subdomains
            score -= 6
        if features[7] == -1:  # No HTTPS
            score -= 12

    # Additional real-time URL analysis
    score += analyze_url_patterns(url)

    # Domain reputation check (basic)
    score += check_domain_reputation(url)

    # Clamp score between 0 and 100
    score = max(0, min(100, score))

    return int(score)

def analyze_url_patterns(url):
    """
    Analyze URL patterns for additional scoring.
    """
    bonus = 0
    penalty = 0

    # Parse URL
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        query = parsed.query.lower()
    except:
        return -10  # Malformed URL

    # Positive patterns (trusted domains)
    trusted_domains = ['google', 'microsoft', 'apple', 'amazon', 'facebook', 'twitter', 'github', 'wikipedia']
    if any(td in domain for td in trusted_domains):
        bonus += 10

    # Negative patterns (suspicious indicators)
    suspicious_patterns = [
        'login', 'secure', 'verify', 'account', 'password', 'bank', 'paypal',
        'free', 'win', 'prize', 'gift', 'urgent', 'alert', 'confirm'
    ]

    suspicious_count = sum(1 for pattern in suspicious_patterns if pattern in domain or pattern in path)
    penalty -= suspicious_count * 3

    # Special characters in domain (penalty)
    if re.search(r'[-_]{2,}', domain):
        penalty -= 5

    # Length penalties
    if len(domain) > 50:
        penalty -= 5
    if len(url) > 100:
        penalty -= 3

    # HTTPS bonus
    if url.startswith('https://'):
        bonus += 5

    return bonus + penalty

def check_domain_reputation(url):
    """
    Basic domain reputation check.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Known good domains get bonus
        good_domains = [
            '.gov', '.edu', '.org', '.com', '.net',
            'google.', 'microsoft.', 'apple.', 'amazon.'
        ]

        if any(domain.endswith(gd) for gd in good_domains):
            return 5

        # Suspicious TLDs get penalty
        bad_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.xyz']
        if any(domain.endswith(bt) for bt in bad_tlds):
            return -10

        return 0
    except:
        return -5

def get_recommendations(url, prediction):
    """
    Provide safe alternatives based on the scanned URL.
    """
    recommendations = []

    if prediction == 0:  # Phishing detected
        domain = url.lower().split('/')[2] if '://' in url else url.lower()

        if 'bank' in domain or 'paypal' in domain or 'login' in domain:
            recommendations = [
                "Use official banking apps or visit verified bank websites directly.",
                "Recommended safe alternatives: bankofamerica.com, chase.com, paypal.com"
            ]
        elif 'amazon' in domain or 'shop' in domain:
            recommendations = [
                "Shop only on verified e-commerce sites.",
                "Recommended safe alternatives: amazon.com, ebay.com, walmart.com"
            ]
        elif 'news' in domain or 'article' in domain:
            recommendations = [
                "Read news from reputable sources.",
                "Recommended safe alternatives: nytimes.com, bbc.com, cnn.com"
            ]
        else:
            recommendations = [
                "Avoid clicking suspicious links.",
                "Recommended safe alternatives: google.com, wikipedia.org, youtube.com"
            ]
    else:
        recommendations = ["This URL appears safe to visit."]

    return recommendations
