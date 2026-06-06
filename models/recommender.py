"""Recommendation Engine Module"""

class ResumeRecommender:
    """Generates recommendations for resume improvement"""
    
    def __init__(self):
        self.recommendations = []
    
    def generate_recommendations(self, analysis_results):
        """
        Generate recommendations based on analysis results
        
        Args:
            analysis_results: Dictionary with analysis data
            
        Returns:
            list: List of recommendations with priority
        """
        recommendations = []
        
        # Extract scores
        ats_score = analysis_results.get('ats_score', 0)
        skill_match_percentage = analysis_results.get('skill_match_percentage', 0)
        missing_skills = analysis_results.get('missing_skills', [])
        matched_skills = analysis_results.get('matched_skills', [])
        
        # Priority 1: Low ATS Score
        if ats_score < 60:
            recommendations.append({
                'priority': 'high',
                'category': 'ATS Compatibility',
                'message': f'Your ATS score is {ats_score}%. Format your resume with clear sections and standard fonts.',
                'action': 'Use standard headings like: SKILLS, EXPERIENCE, EDUCATION'
            })
        elif ats_score < 75:
            recommendations.append({
                'priority': 'medium',
                'category': 'ATS Compatibility',
                'message': f'Improve ATS compatibility (current: {ats_score}%)',
                'action': 'Avoid fancy formatting, use bullet points instead of tables'
            })
        
        # Priority 2: Missing Skills
        if missing_skills:
            top_missing = missing_skills[:3]
            recommendations.append({
                'priority': 'high',
                'category': 'Missing Skills',
                'message': f'Add experience with: {", ".join(top_missing)}',
                'action': f'Include these {len(missing_skills)} skills in your experience or certifications section'
            })
        
        # Priority 3: Low Skill Match
        if skill_match_percentage < 50:
            recommendations.append({
                'priority': 'high',
                'category': 'Skill Alignment',
                'message': f'Only {skill_match_percentage}% of required skills match. Tailor your resume to the job.',
                'action': 'Reorder skills to highlight most relevant ones first'
            })
        elif skill_match_percentage < 75:
            recommendations.append({
                'priority': 'medium',
                'category': 'Skill Alignment',
                'message': f'Skill match is {skill_match_percentage}%. Good but can be better.',
                'action': 'Emphasize related experience that demonstrates missing skills'
            })
        
        # Priority 4: General Resume Improvements
        if len(matched_skills) > 0:
            recommendations.append({
                'priority': 'low',
                'category': 'Optimization',
                'message': f'You have {len(matched_skills)} matching skills. Highlight these prominently.',
                'action': 'Place matched skills at the top and include quantified achievements'
            })
        
        # Add action-specific recommendations
        recommendations.extend(self._get_action_recommendations(analysis_results))
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations
    
    def _get_action_recommendations(self, analysis_results):
        """Generate specific action-based recommendations"""
        actions = []
        
        # Keyword recommendations
        actions.append({
            'priority': 'medium',
            'category': 'Keywords',
            'message': 'Use specific keywords from the job description',
            'action': 'Mirror the exact job title, technology names, and key phrases'
        })
        
        # Achievement recommendations
        actions.append({
            'priority': 'medium',
            'category': 'Content',
            'message': 'Include measurable achievements',
            'action': 'Add metrics like "30% faster", "Increased by 50%", "Managed team of 5"'
        })
        
        # Format recommendations
        actions.append({
            'priority': 'low',
            'category': 'Format',
            'message': 'Optimize resume formatting',
            'action': 'Keep to 1-2 pages, use consistent formatting, save as PDF'
        })
        
        return actions
    
    def rank_improvements(self, recommendations):
        """Rank recommendations by priority and impact"""
        return sorted(recommendations, 
                     key=lambda x: (x.get('priority', 'low'), x.get('message', '')))
    
    def get_top_recommendations(self, analysis_results, top_n=5):
        """
        Get top N recommendations
        
        Args:
            analysis_results: Analysis data
            top_n: Number of top recommendations
            
        Returns:
            list: Top recommendations
        """
        recommendations = self.generate_recommendations(analysis_results)
        return recommendations[:top_n]