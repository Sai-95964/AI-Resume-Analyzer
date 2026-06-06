"""Candidate Ranking Module"""

class CandidateRanker:
    """Ranks multiple candidates based on analysis"""
    
    def __init__(self):
        self.candidates = []
    
    def add_candidate(self, candidate_data):
        """
        Add a candidate to ranking pool
        
        Args:
            candidate_data: Dict with candidate analysis data
        """
        self.candidates.append(candidate_data)
    
    def rank_candidates(self, job_requirements=None):
        """
        Rank candidates by ATS score and match metrics
        
        Args:
            job_requirements: Optional job requirements for context
            
        Returns:
            list: Sorted candidates with ranks
        """
        ranked = sorted(
            [dict(c) for c in self.candidates],
            key=lambda x: x.get('ats_score', 0),
            reverse=True
        )
        
        for idx, candidate in enumerate(ranked, 1):
            candidate['rank'] = idx
            n = len(ranked)
            candidate['percentile'] = round((1 - idx / n) * 100, 2) if n else 0
        
        return ranked
    
    def get_top_candidates(self, n=5):
        """Get top N candidates"""
        ranked = self.rank_candidates()
        return ranked[:n]
    
    def get_candidate_stats(self):
        """Get statistics about all candidates"""
        if not self.candidates:
            return {}
        
        ats_scores = [c.get('ats_score', 0) for c in self.candidates]
        skill_matches = [c.get('skill_match_percentage', 0) for c in self.candidates]
        
        return {
            'total_candidates': len(self.candidates),
            'avg_ats_score': round(sum(ats_scores) / len(ats_scores), 2),
            'max_ats_score': max(ats_scores),
            'min_ats_score': min(ats_scores),
            'avg_skill_match': round(sum(skill_matches) / len(skill_matches), 2),
            'max_skill_match': max(skill_matches),
            'min_skill_match': min(skill_matches),
        }
    
    def compare_candidates(self, candidate1_id, candidate2_id):
        """
        Compare two candidates
        
        Args:
            candidate1_id: Index or ID of first candidate
            candidate2_id: Index or ID of second candidate
            
        Returns:
            dict: Comparison results
        """
        try:
            c1 = self.candidates[candidate1_id]
            c2 = self.candidates[candidate2_id]
            
            return {
                'candidate1': c1.get('name', 'Candidate 1'),
                'candidate2': c2.get('name', 'Candidate 2'),
                'ats_diff': round(
                    c1.get('ats_score', 0) - c2.get('ats_score', 0), 2
                ),
                'skill_match_diff': round(
                    c1.get('skill_match_percentage', 0) - 
                    c2.get('skill_match_percentage', 0), 2
                ),
                'c1_advantage': self._get_advantages(c1, c2),
                'c2_advantage': self._get_advantages(c2, c1),
            }
        except (IndexError, KeyError):
            return {}
    
    def _get_advantages(self, candidate1, candidate2):
        """Get advantages of candidate1 over candidate2"""
        advantages = []
        
        if candidate1.get('ats_score', 0) > candidate2.get('ats_score', 0):
            advantages.append('Higher ATS score')
        
        if candidate1.get('skill_match_percentage', 0) > candidate2.get('skill_match_percentage', 0):
            advantages.append('Better skill match')
        
        c1_missing = len(candidate1.get('missing_skills', []))
        c2_missing = len(candidate2.get('missing_skills', []))
        if c1_missing < c2_missing:
            advantages.append(f'Fewer missing skills ({c1_missing} vs {c2_missing})')
        
        return advantages
    
    def filter_by_threshold(self, min_ats_score=60, min_skill_match=50):
        """
        Filter candidates by minimum thresholds
        
        Args:
            min_ats_score: Minimum ATS score required
            min_skill_match: Minimum skill match percentage
            
        Returns:
            list: Candidates meeting thresholds
        """
        qualified = [
            c for c in self.candidates
            if c.get('ats_score', 0) >= min_ats_score and
               c.get('skill_match_percentage', 0) >= min_skill_match
        ]
        return sorted(qualified, key=lambda x: x.get('ats_score', 0), reverse=True)
    
    def clear_candidates(self):
        """Clear all candidates"""
        self.candidates = []
