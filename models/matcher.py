"""Resume-Job Description Matching Module"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ResumeMatcher:
    """Matches resume content with job requirements using multiple metrics"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)
    
    def match(self, resume_text, job_description):
        """
        Calculate matching score between resume and job description
        
        Args:
            resume_text: Resume content
            job_description: Job description content
            
        Returns:
            float: Match score (0-100)
        """
        try:
            # Vectorize texts
            texts = [resume_text, job_description]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Convert to percentage
            score = similarity * 100
            return round(score, 2)
        except Exception as e:
            print(f"Error calculating match score: {e}")
            return 0.0
    
    def find_matching_skills(self, resume_skills, job_skills):
        """
        Find skills that match between resume and job
        
        Args:
            resume_skills: Skills from resume
            job_skills: Skills required by job
            
        Returns:
            list: Matched skills
        """
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        matched = resume_set & job_set
        return sorted(list(matched))
    
    def find_missing_skills(self, resume_skills, job_skills):
        """
        Find skills from job that are missing in resume
        
        Args:
            resume_skills: Skills from resume
            job_skills: Skills required by job
            
        Returns:
            list: Missing skills
        """
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        missing = job_set - resume_set
        return sorted(list(missing))
    
    def detailed_match(self, resume_text, job_description, resume_skills, job_skills):
        """
        Provide detailed matching analysis
        
        Returns:
            dict: Comprehensive matching analysis
        """
        matched_skills = self.find_matching_skills(resume_skills, job_skills)
        missing_skills = self.find_missing_skills(resume_skills, job_skills)
        similarity_score = self.match(resume_text, job_description)
        
        skill_match_percentage = (
            (len(matched_skills) / len(job_skills) * 100) 
            if job_skills else 0
        )
        
        return {
            'similarity_score': similarity_score,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'skill_match_percentage': round(skill_match_percentage, 2),
            'match_count': len(matched_skills),
            'missing_count': len(missing_skills),
            'total_required': len(job_skills)
        }