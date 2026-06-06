"""ATS (Applicant Tracking System) Scoring Module"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np

class ATSScorer:
    """Scores resumes based on ATS compatibility with weighted factors"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)
        # Weights for ATS score calculation
        self.weights = {
            'skill_match': 0.40,
            'keyword_match': 0.30,
            'experience': 0.15,
            'education': 0.10,
            'format': 0.05
        }
    
    def score(self, resume_text, job_description, resume_skills, job_skills, 
              matched_skills, resume_data=None):
        """
        Calculate comprehensive ATS score with multiple factors
        
        Args:
            resume_text: Resume content
            job_description: Job description content
            resume_skills: Skills extracted from resume
            job_skills: Skills required by job
            matched_skills: Skills that match between resume and job
            resume_data: Dict with education, experience info (optional)
            
        Returns:
            dict: Detailed ATS score breakdown
        """
        try:
            scores = {}
            
            # 1. Skill Match Score (40%)
            scores['skill_match'] = self._calculate_skill_score(
                resume_skills, job_skills, matched_skills
            )
            
            # 2. Keyword Match Score (30%)
            scores['keyword_match'] = self._calculate_keyword_score(
                resume_text, job_description
            )
            
            # 3. Experience Score (15%)
            scores['experience'] = self._calculate_experience_score(
                resume_text, resume_data
            )
            
            # 4. Education Score (10%)
            scores['education'] = self._calculate_education_score(
                resume_text, resume_data
            )
            
            # 5. Format Score (5%)
            scores['format'] = self._calculate_format_score(resume_text)
            
            # Calculate weighted ATS score
            ats_score = sum(
                scores[key] * self.weights[key]
                for key in scores.keys()
            )
            
            return {
                'ats_score': round(ats_score, 2),
                'scores': {k: round(v, 2) for k, v in scores.items()},
                'weights': self.weights
            }
        except Exception as e:
            print(f"Error calculating ATS score: {e}")
            return {'ats_score': 0.0, 'scores': {}, 'weights': self.weights}
    
    def _calculate_skill_score(self, resume_skills, job_skills, matched_skills):
        """Calculate skill match percentage"""
        if not job_skills:
            return 100.0
        
        match_percentage = (len(matched_skills) / len(job_skills)) * 100
        return min(match_percentage, 100.0)
    
    def _calculate_keyword_score(self, resume_text, job_description):
        """
        Calculate keyword match using TF-IDF cosine similarity
        """
        try:
            texts = [resume_text, job_description]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity * 100
        except Exception:
            return 0.0
    
    def _calculate_experience_score(self, resume_text, resume_data=None):
        """
        Calculate experience score based on years and keywords
        """
        score = 50.0  # Base score
        
        # Check for experience keywords
        experience_keywords = [
            'experience', 'worked', 'managed', 'led', 'developed',
            'designed', 'implemented', 'year', 'years', 'project'
        ]
        
        resume_lower = resume_text.lower()
        for keyword in experience_keywords:
            if keyword in resume_lower:
                score += 5.0
        
        return min(score, 100.0)
    
    def _calculate_education_score(self, resume_text, resume_data=None):
        """
        Calculate education score based on degrees mentioned
        """
        score = 50.0  # Base score
        
        education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'diploma',
            'certified', 'certificate', 'university', 'college'
        ]
        
        resume_lower = resume_text.lower()
        for keyword in education_keywords:
            if keyword in resume_lower:
                score += 10.0
        
        return min(score, 100.0)
    
    def _calculate_format_score(self, resume_text):
        """
        Calculate format score based on structure and length
        """
        score = 50.0  # Base score
        lines = resume_text.strip().split('\n')
        word_count = len(resume_text.split())
        
        # Good resume has 200-1000 words
        if 200 <= word_count <= 1000:
            score += 30.0
        elif word_count > 100:
            score += 20.0
        
        # Good resume has 10+ lines
        if len(lines) >= 10:
            score += 20.0
        
        return min(score, 100.0)