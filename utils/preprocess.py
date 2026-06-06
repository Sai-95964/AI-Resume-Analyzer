"""Text Preprocessing Module"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string

# Download required NLTK data (paths differ per resource type)
_NLTK_PACKAGES = [
    ('tokenizers', 'punkt'),
    ('tokenizers', 'punkt_tab'),
    ('corpora', 'stopwords'),
    ('corpora', 'wordnet'),
    ('taggers', 'averaged_perceptron_tagger'),
]


def _ensure_nltk_data():
    for category, name in _NLTK_PACKAGES:
        try:
            nltk.data.find(f'{category}/{name}')
        except LookupError:
            try:
                nltk.download(name, quiet=True)
            except Exception:
                pass


_ensure_nltk_data()

class TextPreprocessor:
    """Preprocesses text data for analysis"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_text(self, text):
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            str: Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters except hyphens and spaces
        text = re.sub(r'[^a-zA-Z0-9\s\-]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def remove_stopwords(self, text):
        """Remove common English stopwords"""
        words = word_tokenize(text)
        filtered = [w for w in words if w.lower() not in self.stop_words and w.strip()]
        return ' '.join(filtered)
    
    def lemmatize(self, text):
        """Lemmatize words to root form"""
        words = word_tokenize(text)
        lemmatized = [self.lemmatizer.lemmatize(w) for w in words]
        return ' '.join(lemmatized)
    
    def tokenize(self, text):
        """Tokenize text into words"""
        return word_tokenize(text)
    
    def extract_keywords(self, text, top_n=20):
        """
        Extract top keywords by frequency
        
        Args:
            text: Input text
            top_n: Number of top keywords
            
        Returns:
            list: Top keywords
        """
        words = self.tokenize(text.lower())
        words = [w for w in words if w not in self.stop_words and w.isalpha()]
        
        from collections import Counter
        freq = Counter(words)
        return [word for word, _ in freq.most_common(top_n)]
    
    def preprocess(self, text):
        """Complete preprocessing pipeline"""
        text = self.clean_text(text)
        text = self.remove_stopwords(text)
        text = self.lemmatize(text)
        return text