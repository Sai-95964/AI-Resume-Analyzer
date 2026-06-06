"""
COMPREHENSIVE TEST SUITE
AI Resume Analyzer & ATS Scorer
"""

import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

FAILURES = 0


def report_ok(message):
    print(f"[PASS] {message}")


def report_fail(message, exc=None):
    global FAILURES
    FAILURES += 1
    print(f"[FAIL] {message}")
    if exc:
        import traceback
        traceback.print_exc()

print("=" * 80)
print("AI RESUME ANALYZER - COMPREHENSIVE TEST SUITE")
print("=" * 80)
print()

# Test 1: Import Test
print("TEST 1: Testing Imports...")
try:
    from models.ats_scorer import ATSScorer
    from models.matcher import ResumeMatcher
    from models.recommender import ResumeRecommender
    from models.job_processor import JobDescriptionProcessor
    from models.ranker import CandidateRanker
    from utils.parser import ResumeParser
    from utils.preprocess import TextPreprocessor
    from utils.skill_extractor import SkillExtractor
    report_ok("All imports successful")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Component Initialization
print("TEST 2: Testing Component Initialization...")
try:
    ats_scorer = ATSScorer()
    matcher = ResumeMatcher()
    recommender = ResumeRecommender()
    job_processor = JobDescriptionProcessor()
    ranker = CandidateRanker()
    preprocessor = TextPreprocessor()
    skill_extractor = SkillExtractor()
    report_ok("All components initialized successfully")
except Exception as e:
    print(f"[FAIL] Initialization failed: {e}")
    sys.exit(1)

print()

# Test 3: Text Preprocessing
print("TEST 3: Testing Text Preprocessing Pipeline...")
try:
    sample_text = """
    I am a Senior Python Developer with 5+ years of experience.
    I have worked with Flask, Django, and FastAPI frameworks.
    I am skilled in AWS, Docker, and Kubernetes.
    Visit my website: https://example.com or email me at john@example.com
    """
    
    # Test individual preprocessing steps
    cleaned = preprocessor.clean_text(sample_text)
    assert len(cleaned) < len(sample_text), "Cleaning should reduce text length"
    assert "https://" not in cleaned, "URLs should be removed"
    assert "@" not in cleaned, "Emails should be removed"
    
    # Test tokenization
    tokens = preprocessor.tokenize(sample_text)
    assert len(tokens) > 0, "Tokenization should produce tokens"
    
    # Test lemmatization
    lemmatized = preprocessor.lemmatize(cleaned)
    assert len(lemmatized) > 0, "Lemmatization should produce text"
    
    # Test keyword extraction
    keywords = preprocessor.extract_keywords(sample_text, top_n=5)
    assert len(keywords) > 0, "Should extract keywords"
    
    # Test full pipeline
    preprocessed = preprocessor.preprocess(sample_text)
    assert len(preprocessed) > 0, "Preprocessing pipeline should work"
    
    report_ok("Text preprocessing working correctly")
except Exception as e:
    report_fail(f"Preprocessing failed: {e}", e)

print()

# Test 4: Skill Extraction
print("TEST 4: Testing Skill Extraction...")
try:
    resume_text = "I have 5 years of Python and SQL experience. I also know Flask, Django, and AWS."
    job_text = "We need someone with Python, JavaScript, SQL, Docker, and Kubernetes skills."
    
    # Test basic extraction
    resume_skills = skill_extractor.extract(resume_text)
    assert "python" in [s.lower() for s in resume_skills], "Should extract Python"
    assert len(resume_skills) > 0, "Should extract skills from resume"
    
    job_skills = skill_extractor.extract(job_text)
    assert len(job_skills) > 0, "Should extract skills from job description"
    
    # Test extraction with scores
    skills_with_scores = skill_extractor.extract_with_scores(resume_text)
    assert isinstance(skills_with_scores, dict), "Should return dict with scores"
    assert all(0 <= score <= 1 for score in skills_with_scores.values()), "Scores should be 0-1"
    
    # Test categorization
    categorized = skill_extractor.categorize_skills(resume_skills)
    assert isinstance(categorized, dict), "Should return categorized skills"
    
    # Test missing skills
    missing = skill_extractor.get_missing_skills(resume_skills, job_skills)
    assert isinstance(missing, list), "Should return list of missing skills"
    
    report_ok("Skill extraction working correctly")
    print(f"   Resume skills: {', '.join(resume_skills[:3])}...")
    print(f"   Job skills: {', '.join(job_skills[:3])}...")
    print(f"   Missing skills: {', '.join(missing[:3])}..." if missing else "   No missing skills")
except Exception as e:
    report_fail(f"Skill extraction failed: {e}", e)

print()

# Test 5: Resume Matching
print("TEST 5: Testing Resume Matching...")
try:
    resume_text = "I have Python, SQL, and Flask experience. Worked with AWS for 3 years."
    job_text = "We need Python developer with SQL and Flask skills. AWS experience is required."
    
    resume_skills = skill_extractor.extract(resume_text)
    job_skills = skill_extractor.extract(job_text)
    
    # Test basic matching
    match_score = matcher.match(resume_text, job_text)
    assert 0 <= match_score <= 100, "Match score should be 0-100"
    assert match_score > 0, "Similar texts should produce a non-zero match score"
    
    # Test skill matching
    matched_skills = matcher.find_matching_skills(resume_skills, job_skills)
    assert len(matched_skills) > 0, "Should find matching skills"
    
    # Test missing skills
    missing_skills = matcher.find_missing_skills(resume_skills, job_skills)
    assert isinstance(missing_skills, list), "Should return list of missing skills"
    
    # Test detailed matching
    detailed = matcher.detailed_match(resume_text, job_text, resume_skills, job_skills)
    assert 'similarity_score' in detailed, "Should have similarity score"
    assert 'matched_skills' in detailed, "Should have matched skills"
    assert 'missing_skills' in detailed, "Should have missing skills"
    
    report_ok("Resume matching working correctly")
    print(f"   Match score: {match_score:.1f}%")
    print(f"   Matched skills: {', '.join(matched_skills)}")
except Exception as e:
    report_fail(f"Resume matching failed: {e}", e)

print()

# Test 6: ATS Scoring
print("TEST 6: Testing ATS Scoring...")
try:
    resume_text = "Senior Python Developer with 5 years experience. Skills: Python, SQL, Flask, Django, AWS. Bachelor's degree in Computer Science."
    job_text = "Python Developer required. Must have: Python, SQL, Flask, Docker, Kubernetes, AWS. Bachelor's required. Experience with machine learning a plus."
    
    resume_skills = skill_extractor.extract(resume_text)
    job_skills = skill_extractor.extract(job_text)
    matched_skills = matcher.find_matching_skills(resume_skills, job_skills)
    
    # Calculate ATS score
    ats_result = ats_scorer.score(
        resume_text, job_text, resume_skills, 
        job_skills, matched_skills
    )
    
    assert 'ats_score' in ats_result, "Should return ATS score"
    assert 0 <= ats_result['ats_score'] <= 100, "ATS score should be 0-100"
    assert 'scores' in ats_result, "Should have score breakdown"
    assert 'weights' in ats_result, "Should have weights"
    
    # Verify weights sum to 1.0
    weights = ats_result['weights']
    total_weight = sum(weights.values())
    assert 0.99 <= total_weight <= 1.01, f"Weights should sum to 1.0, got {total_weight}"
    
    report_ok("ATS scoring working correctly")
    print(f"   ATS Score: {ats_result['ats_score']:.1f}%")
    print(f"   Component Breakdown:")
    for component, score in ats_result['scores'].items():
        weight = weights.get(component, 0)
        print(f"     - {component}: {score:.1f} (weight: {weight:.0%})")
except Exception as e:
    report_fail(f"ATS scoring failed: {e}", e)

print()

# Test 7: Job Processing
print("TEST 7: Testing Job Description Processing...")
try:
    job_description = "We are looking for a Senior Python Developer with 5+ years experience. Must have: Python, SQL, Docker, Kubernetes, AWS. Nice to have: Machine Learning, React. Bachelor's degree required."
    
    # Test job processing
    job_data = job_processor.process(job_description)
    assert 'raw_text' in job_data, "Should have raw text"
    assert 'cleaned_text' in job_data, "Should have cleaned text"
    assert 'skills' in job_data, "Should have extracted skills"
    assert 'keywords' in job_data, "Should have keywords"
    assert 'word_count' in job_data, "Should have word count"
    
    # Test job requirements extraction
    requirements = job_processor.extract_job_requirements(job_description)
    assert 'total_skills' in requirements, "Should have total skills"
    
    # Test seniority level extraction
    seniority = job_processor.extract_seniority_level(job_description)
    assert seniority in ['junior', 'mid', 'senior'], f"Seniority should be junior/mid/senior, got {seniority}"
    
    report_ok("Job processing working correctly")
    print(f"   Detected Skills: {', '.join(job_data['skills'][:3])}...")
    print(f"   Detected Seniority: {seniority}")
    print(f"   Word Count: {job_data['word_count']}")
except Exception as e:
    report_fail(f"Job processing failed: {e}", e)

print()

# Test 8: Recommendations
print("TEST 8: Testing Recommendation Engine...")
try:
    analysis_results = {
        'ats_score': 65,
        'skill_match_percentage': 45,
        'missing_skills': ['Docker', 'Kubernetes', 'React'],
        'matched_skills': ['Python', 'SQL', 'Flask']
    }
    
    recommendations = recommender.generate_recommendations(analysis_results)
    
    assert isinstance(recommendations, list), "Should return list of recommendations"
    assert len(recommendations) > 0, "Should have at least one recommendation"
    
    # Check recommendation structure
    for rec in recommendations:
        assert 'priority' in rec, "Recommendation should have priority"
        assert 'category' in rec, "Recommendation should have category"
        assert 'message' in rec, "Recommendation should have message"
        assert 'action' in rec, "Recommendation should have action"
        assert rec['priority'] in ['high', 'medium', 'low'], "Priority should be high/medium/low"
    
    # Check priority ordering
    ranked = recommender.rank_improvements(recommendations)
    assert ranked[0]['priority'] in ['high', 'medium', 'low'], "Should be ranked by priority"
    
    report_ok("Recommendations working correctly")
    print(f"   Generated {len(recommendations)} recommendations")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"   {i}. [{rec['priority'].upper()}] {rec['category']}: {rec['message'][:60]}...")
except Exception as e:
    report_fail(f"Recommendations failed: {e}", e)

print()

# Test 9: Candidate Ranking
print("TEST 9: Testing Candidate Ranking...")
try:
    # Add multiple candidates
    candidates = [
        {'name': 'Alice', 'ats_score': 85, 'skill_match_percentage': 90},
        {'name': 'Bob', 'ats_score': 72, 'skill_match_percentage': 80},
        {'name': 'Charlie', 'ats_score': 95, 'skill_match_percentage': 95},
        {'name': 'Diana', 'ats_score': 60, 'skill_match_percentage': 50},
    ]
    
    for candidate in candidates:
        ranker.add_candidate(candidate)
    
    # Rank candidates
    ranked = ranker.rank_candidates()
    assert len(ranked) == 4, "Should rank all candidates"
    assert ranked[0]['ats_score'] >= ranked[1]['ats_score'], "Should sort by ATS score descending"
    
    # Check ranks and percentiles
    for i, candidate in enumerate(ranked, 1):
        assert candidate['rank'] == i, "Rank should be sequential"
        assert 0 <= candidate['percentile'] <= 100, "Percentile should be 0-100"
    
    # Get statistics
    stats = ranker.get_candidate_stats()
    assert 'total_candidates' in stats, "Should have total candidates"
    assert 'avg_ats_score' in stats, "Should have average ATS score"
    assert stats['total_candidates'] == 4, "Should count candidates correctly"
    
    # Get top candidates
    top = ranker.get_top_candidates(n=2)
    assert len(top) == 2, "Should return top N"
    
    report_ok("Candidate ranking working correctly")
    print(f"   Total candidates: {stats['total_candidates']}")
    print(f"   Average ATS score: {stats['avg_ats_score']:.1f}")
    print(f"   Top candidate: {ranked[0]['name']} (Score: {ranked[0]['ats_score']})")
except Exception as e:
    report_fail(f"Candidate ranking failed: {e}", e)

print()

# Test 10: Integration Test (Complete Workflow)
print("TEST 10: Integration Test - Complete Workflow...")
try:
    # Sample data
    sample_resume = """
    John Doe
    Senior Software Engineer
    
    Summary:
    5+ years of experience in Python development with expertise in Flask, Django, and AWS.
    Strong background in SQL and relational databases. Experience with Docker containerization.
    
    Skills:
    - Python (Expert)
    - SQL (Advanced)
    - Flask (Advanced)
    - Django (Intermediate)
    - AWS (Intermediate)
    - Docker (Beginner)
    - Git (Advanced)
    
    Experience:
    Senior Python Developer at TechCorp (2020-Present)
    - Led development of microservices using Flask
    - Managed AWS infrastructure
    - Mentored junior developers
    
    Education:
    Bachelor's Degree in Computer Science, University of Technology
    """
    
    sample_job = """
    Senior Python Developer Required
    
    About the Role:
    We are seeking an experienced Python developer to join our growing team.
    
    Required Skills:
    - 5+ years Python experience
    - Flask or Django framework experience
    - SQL and database design
    - AWS cloud services
    - Docker containerization
    - Team collaboration and mentoring
    
    Nice to Have:
    - Kubernetes experience
    - React/JavaScript
    - Machine Learning basics
    
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - Strong problem-solving skills
    - Experience with agile methodologies
    """
    
    # Run complete workflow
    resume_cleaned = preprocessor.preprocess(sample_resume)
    job_cleaned = preprocessor.preprocess(sample_job)
    
    resume_skills = skill_extractor.extract(sample_resume)
    job_skills = skill_extractor.extract(sample_job)
    
    matched_skills = matcher.find_matching_skills(resume_skills, job_skills)
    missing_skills = matcher.find_missing_skills(resume_skills, job_skills)
    
    match_analysis = matcher.detailed_match(sample_resume, sample_job, resume_skills, job_skills)
    
    ats_result = ats_scorer.score(
        sample_resume, sample_job, resume_skills, 
        job_skills, matched_skills
    )
    
    job_data = job_processor.process(sample_job)
    job_reqs = job_processor.extract_job_requirements(sample_job)
    job_seniority = job_processor.extract_seniority_level(sample_job)
    
    analysis_data = {
        'ats_score': ats_result['ats_score'],
        'skill_match_percentage': match_analysis['skill_match_percentage'],
        'missing_skills': missing_skills,
        'matched_skills': matched_skills
    }
    recommendations = recommender.generate_recommendations(analysis_data)
    
    # Verify complete results
    assert ats_result['ats_score'] >= 40, "Should produce a reasonable ATS score for similar profiles"
    assert len(matched_skills) > 3, "Should match multiple skills"
    assert len(recommendations) > 0, "Should generate recommendations"
    
    report_ok("Complete workflow executed successfully")
    print(f"   ATS Score: {ats_result['ats_score']:.1f}%")
    print(f"   Matched Skills: {len(matched_skills)}/{len(job_skills)}")
    print(f"   Missing Skills: {len(missing_skills)}")
    print(f"   Job Seniority: {job_seniority}")
    print(f"   Recommendations: {len(recommendations)}")
    
except Exception as e:
    report_fail(f"Integration test failed: {e}", e)

print()
print("=" * 80)
print("TEST SUITE COMPLETE")
print("=" * 80)
if FAILURES:
    print(f"{FAILURES} test(s) failed. Install deps: pip install -r requirements.txt")
    sys.exit(1)
print("All tests passed.")
sys.exit(0)
