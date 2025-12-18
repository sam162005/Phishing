import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import math
from textblob import TextBlob
from langdetect import detect, LangDetectException
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextAnalyzer:
    def __init__(self):
        self.spam_keywords = {
            'amazing', 'awesome', 'excellent', 'fantastic', 'great', 'love', 'perfect',
            'wonderful', 'best', 'super', 'incredible', 'outstanding', 'brilliant',
            'recommend', 'highly', 'definitely', 'absolutely', 'totally', 'completely',
            'extremely', 'very', 'so', 'much', 'really', 'truly', 'genuinely'
        }
        self.stop_words = set(stopwords.words('english'))

    def analyze_text(self, text):
        """Main analysis function returning comprehensive text analytics."""
        if not text or not text.strip():
            return self._empty_analysis()

        # Basic metrics
        word_count = len(word_tokenize(text))
        sentence_count = len(sent_tokenize(text))
        char_count = len(text)

        # Readability score (simplified Flesch Reading Ease)
        readability = self._calculate_readability(text)

        # Sentiment analysis
        sentiment = self._analyze_sentiment(text)

        # Language detection
        language = self._detect_language(text)

        # Spam analysis
        spam_density = self._calculate_spam_density(text)

        # Advanced detection
        ai_patterns = self._detect_ai_patterns(text)
        duplicate_check = self._check_duplicate_content(text)

        # Word frequency
        word_freq = self._get_word_frequency(text)

        return {
            'basic_metrics': {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'char_count': char_count,
                'avg_words_per_sentence': round(word_count / max(sentence_count, 1), 1)
            },
            'readability': readability,
            'sentiment': sentiment,
            'language': language,
            'spam_analysis': spam_density,
            'advanced_detection': {
                'ai_generated_patterns': ai_patterns,
                'duplicate_content': duplicate_check
            },
            'word_frequency': word_freq
        }

    def _empty_analysis(self):
        """Return empty analysis structure."""
        return {
            'basic_metrics': {'word_count': 0, 'sentence_count': 0, 'char_count': 0, 'avg_words_per_sentence': 0},
            'readability': {'score': 0, 'level': 'N/A'},
            'sentiment': {'polarity': 0, 'subjectivity': 0, 'label': 'neutral'},
            'language': 'unknown',
            'spam_analysis': {'density': 0, 'spam_words': 0, 'total_words': 0},
            'advanced_detection': {'ai_generated_patterns': [], 'duplicate_content': {'is_duplicate': False, 'confidence': 0}},
            'word_frequency': []
        }

    def _calculate_readability(self, text):
        """Calculate simplified readability score."""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)

        if not sentences or not words:
            return {'score': 0, 'level': 'N/A'}

        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Simplified Flesch formula
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
        score = max(0, min(100, score))

        # Determine level
        if score >= 90:
            level = 'Very Easy'
        elif score >= 80:
            level = 'Easy'
        elif score >= 70:
            level = 'Fairly Easy'
        elif score >= 60:
            level = 'Standard'
        elif score >= 50:
            level = 'Fairly Difficult'
        elif score >= 30:
            level = 'Difficult'
        else:
            level = 'Very Difficult'

        return {'score': round(score, 1), 'level': level}

    def _analyze_sentiment(self, text):
        """Analyze sentiment using TextBlob."""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Determine label
        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'polarity': round(polarity, 2),
            'subjectivity': round(subjectivity, 2),
            'label': label
        }

    def _detect_language(self, text):
        """Detect language of the text."""
        try:
            lang_code = detect(text)
            lang_map = {
                'en': 'English',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
                'it': 'Italian',
                'pt': 'Portuguese',
                'ru': 'Russian',
                'ja': 'Japanese',
                'ko': 'Korean',
                'zh': 'Chinese'
            }
            return lang_map.get(lang_code, f'{lang_code.upper()}')
        except LangDetectException:
            return 'unknown'

    def _calculate_spam_density(self, text):
        """Calculate spam word density."""
        words = word_tokenize(text.lower())
        words = [word for word in words if word not in self.stop_words and word not in string.punctuation]

        spam_words = [word for word in words if word in self.spam_keywords]
        total_words = len(words)

        density = (len(spam_words) / max(total_words, 1)) * 100

        return {
            'density': round(density, 1),
            'spam_words': len(spam_words),
            'total_words': total_words
        }

    def _detect_ai_patterns(self, text):
        """Detect patterns typical of AI-generated content."""
        patterns = []

        # Check for repetitive phrases
        sentences = sent_tokenize(text)
        if len(sentences) > 3:
            # Look for similar sentence structures
            sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
            if len(set(sentence_lengths)) <= 2:  # Very similar lengths
                patterns.append("Repetitive sentence lengths")

        # Check for unnatural word combinations
        words = word_tokenize(text.lower())
        if len(words) > 10:
            # Look for excessive adjectives
            pos_tags = nltk.pos_tag(words)
            adjectives = [word for word, pos in pos_tags if pos.startswith('JJ')]
            adj_ratio = len(adjectives) / len(words)
            if adj_ratio > 0.15:  # More than 15% adjectives
                patterns.append("Excessive use of adjectives")

        # Check for perfect grammar patterns (uncommon in real reviews)
        if re.search(r'\b(?:however|therefore|moreover|consequently|furthermore)\b', text.lower()):
            patterns.append("Formal transition words")

        # Check for template-like structures
        if re.search(r'\b(?:i (?:love|like|enjoy|appreciate|recommend)|this (?:is|was) (?:great|amazing|excellent))\b', text.lower()):
            patterns.append("Template-like phrases")

        return patterns

    def _check_duplicate_content(self, text):
        """Simple duplicate content check (in a real app, this would check against a database)."""
        # For demo purposes, check for very similar known spam patterns
        spam_patterns = [
            "love this product great quality",
            "awesome item fast shipping",
            "excellent service quick delivery",
            "good product nice price"
        ]

        text_lower = text.lower().strip()
        max_similarity = 0

        for pattern in spam_patterns:
            # Simple similarity check
            pattern_words = set(word_tokenize(pattern))
            text_words = set(word_tokenize(text_lower))
            similarity = len(pattern_words.intersection(text_words)) / len(pattern_words.union(text_words))
            max_similarity = max(max_similarity, similarity)

        is_duplicate = max_similarity > 0.7  # 70% similarity threshold

        return {
            'is_duplicate': is_duplicate,
            'confidence': round(max_similarity * 100, 1)
        }

    def _get_word_frequency(self, text, top_n=10):
        """Get most frequent words."""
        words = word_tokenize(text.lower())
        words = [word for word in words if word not in self.stop_words and word not in string.punctuation and len(word) > 2]

        word_counts = Counter(words)
        return word_counts.most_common(top_n)

# Global analyzer instance
analyzer = TextAnalyzer()

def analyze_text_comprehensive(text):
    """Convenience function for comprehensive text analysis."""
    return analyzer.analyze_text(text)
