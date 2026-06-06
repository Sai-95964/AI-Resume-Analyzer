"""Similarity Calculation Module"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimilarityCalculator:
    """Calculates similarity between texts"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
    
    def cosine_similarity(self, text1, text2):
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            float: Similarity score (0-1)
        """
        try:
            vectors = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return round(similarity, 3)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def jaccard_similarity(self, text1, text2):
        """Calculate Jaccard similarity between two texts"""
        set1 = set(text1.split())
        set2 = set(text2.split())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return round(intersection / union, 3)
    
    def levenshtein_distance(self, text1, text2):
        """Calculate Levenshtein distance between two texts"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()