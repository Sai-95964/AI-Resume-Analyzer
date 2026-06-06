"""Job Description Processor Module"""

from utils.preprocess import TextPreprocessor
from utils.skill_extractor import SkillExtractor

class JobDescriptionProcessor:
    """Processes and analyzes job descriptions"""
    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.skill_extractor = SkillExtractor()
    
    def process(self, job_description):
        """
        Comprehensive job description analysis
        
        Args:
            job_description: Raw job description text
            
        Returns:
            dict: Processed job data
        """
        return {
            'raw_text': job_description,
            'cleaned_text': self.preprocessor.clean_text(job_description),
            'skills': self.skill_extractor.extract(job_description),
            'keywords': self.preprocessor.extract_keywords(job_description),
            'skill_categories': self.skill_extractor.categorize_skills(
                self.skill_extractor.extract(job_description)
            ),
            'word_count': len(job_description.split()),
            'sentence_count': len(job_description.split('.')),
        }
    
    def extract_job_requirements(self, job_description):
        """
        Extract structured job requirements
        
        Args:
            job_description: Job description text
            
        Returns:
            dict: Extracted requirements
        """
        requirements = {
            'must_have': [],
            'nice_to_have': [],
            'total_skills': []
        }
        
        # Extract all skills
        all_skills = self.skill_extractor.extract(job_description)
        requirements['total_skills'] = all_skills
        
        # Categorize by priority (simple heuristic based on position)
        doc_lower = job_description.lower()
        
        for skill in all_skills:
            # Skills mentioned near "required" are must-have
            if any(word in doc_lower for word in ['required', 'must have', 'essential']):
                if skill.lower() in doc_lower.split():
                    requirements['must_have'].append(skill)
            # Skills mentioned near "preferred" are nice-to-have
            elif any(word in doc_lower for word in ['preferred', 'nice to have', 'desired']):
                requirements['nice_to_have'].append(skill)
        
        # If no categorization worked, split 50-50
        if not requirements['must_have'] and not requirements['nice_to_have']:
            mid = len(all_skills) // 2
            requirements['must_have'] = all_skills[:mid]
            requirements['nice_to_have'] = all_skills[mid:]
        
        return requirements
    
    def extract_seniority_level(self, job_description):
        """
        Extract seniority level from job description
        
        Returns:
            str: Detected seniority level (junior, mid, senior, lead)
        """
        doc_lower = job_description.lower()
        
        if any(word in doc_lower for word in ['lead', 'principal', 'staff']):
            return 'senior'
        elif any(word in doc_lower for word in ['senior', '5+ years', 'decade']):
            return 'senior'
        elif any(word in doc_lower for word in ['mid-level', 'intermediate', '3+ years', '3-5']):
            return 'mid'
        elif any(word in doc_lower for word in ['junior', 'entry', '0-2 years', 'recent']):
            return 'junior'
        else:
            return 'mid'  # Default to mid-level
    
    def get_job_summary(self, job_description):
        """Get a summary of the job"""
        words = self.preprocessor.extract_keywords(job_description, top_n=10)
        return {
            'top_keywords': words,
            'seniority': self.extract_seniority_level(job_description),
            'skill_count': len(self.skill_extractor.extract(job_description))
        }
