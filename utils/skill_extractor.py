"""Skill Extraction Module"""

import csv
import re
import os
from fuzzywuzzy import fuzz
from collections import defaultdict
from utils.paths import project_path

class SkillExtractor:
    """Extracts skills from resume and job descriptions"""
    
    def __init__(self, skills_file='data/skills.csv'):
        if os.path.isabs(skills_file):
            resolved_path = skills_file
        else:
            resolved_path = project_path(skills_file)
        
        self.skills_file = resolved_path
        self.skills_db, self.skills_categories = self._load_skills_db(resolved_path)
        self.FUZZY_THRESHOLD = 75
    
    def _load_skills_db(self, skills_file):
        """Load skills database from CSV"""
        skills = []
        categories = {}
        try:
            with open(skills_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skill = row['skill'].lower().strip()
                    skills.append(skill)
                    category = row.get('category', 'Other')
                    categories[skill] = category
        except Exception as e:
            print(f"Error loading skills database: {e}")
        return skills, categories
    
    def extract(self, text):
        """
        Extract skills from text with fuzzy matching
        
        Args:
            text: Text to extract skills from
            
        Returns:
            list: Extracted skills (deduplicated)
        """
        extracted_skills = set()
        text_lower = text.lower()
        
        for skill in self.skills_db:
            # Exact match with word boundaries
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                extracted_skills.add(skill)
            # Fuzzy match for partial matches
            else:
                ratio = fuzz.partial_ratio(skill, text_lower)
                if ratio > self.FUZZY_THRESHOLD:
                    extracted_skills.add(skill)
        
        return sorted(list(extracted_skills))
    
    def extract_with_scores(self, text):
        """
        Extract skills with confidence scores
        
        Args:
            text: Text to extract skills from
            
        Returns:
            dict: Skills with confidence scores
        """
        skills_with_scores = {}
        text_lower = text.lower()
        
        for skill in self.skills_db:
            # Check exact match
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skills_with_scores[skill] = 1.0
            else:
                ratio = fuzz.partial_ratio(skill, text_lower)
                if ratio > self.FUZZY_THRESHOLD:
                    skills_with_scores[skill] = ratio / 100.0
        
        return {k: v for k, v in sorted(skills_with_scores.items(), 
                                        key=lambda x: x[1], reverse=True)}
    
    def categorize_skills(self, skills):
        """
        Categorize skills by type
        
        Args:
            skills: List of skills
            
        Returns:
            dict: Skills grouped by category
        """
        categories = defaultdict(list)
        for skill in skills:
            skill_lower = skill.lower()
            category = self.skills_categories.get(skill_lower, 'Other')
            categories[category].append(skill)
        return dict(categories)
    
    def get_skill_level(self, skill):
        """Get the level of a skill from database"""
        try:
            with open(self.skills_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['skill'].lower() == skill.lower():
                        return row.get('level', 'intermediate')
        except Exception:
            pass
        return 'intermediate'
    
    def get_missing_skills(self, resume_skills, job_skills):
        """
        Find skills required but missing from resume
        
        Args:
            resume_skills: Skills found in resume
            job_skills: Skills required by job
            
        Returns:
            list: Missing skills
        """
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        return sorted(list(job_set - resume_set))