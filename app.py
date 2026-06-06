from flask import Flask, render_template, request, jsonify
from models.ats_scorer import ATSScorer
from models.matcher import ResumeMatcher
from models.recommender import ResumeRecommender
from models.job_processor import JobDescriptionProcessor
from models.ranker import CandidateRanker
from models.llm_analyzer import LLMAnalyzer
from utils.parser import ResumeParser
from utils.preprocess import TextPreprocessor
from utils.skill_extractor import SkillExtractor
from utils.paths import PROJECT_ROOT, project_path
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.report import generate_report_pdf

load_dotenv(project_path('.env'))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = project_path('data', 'resumes')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize components
ats_scorer = ATSScorer()
matcher = ResumeMatcher()
recommender = ResumeRecommender()
job_processor = JobDescriptionProcessor()
ranker = CandidateRanker()
parser = ResumeParser()
preprocessor = TextPreprocessor()
skill_extractor = SkillExtractor()
llm_analyzer = LLMAnalyzer()

@app.route('/')
def index():
    """Main analysis page"""
    return render_template('index.html', llm_available=llm_analyzer.is_available())


@app.route('/api/samples')
def get_samples():
    """Demo resume and job description text."""
    try:
        resume_path = project_path('data', 'samples', 'sample_resume.txt')
        job_path = project_path('data', 'samples', 'sample_job.txt')
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume = f.read()
        with open(job_path, 'r', encoding='utf-8') as f:
            job = f.read()
        return jsonify({'resume_text': resume, 'job_description': job}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Comprehensive resume analysis API endpoint"""
    try:
        resume_file = request.files.get('resume')
        job_description = request.form.get('job_description')
        
        if not resume_file or not job_description:
            return jsonify({'error': 'Missing resume or job description'}), 400
        
        # Parse resume
        resume_text = parser.parse(resume_file)
        if not resume_text or not resume_text.strip():
            return jsonify({'error': 'Could not parse resume file or file is empty'}), 400
        
        # Preprocess texts
        resume_cleaned = preprocessor.preprocess(resume_text)
        job_cleaned = preprocessor.preprocess(job_description)
        
        # Extract skills
        resume_skills = skill_extractor.extract(resume_text)
        job_skills = skill_extractor.extract(job_description)
        
        # Find matching skills
        matched_skills = matcher.find_matching_skills(resume_skills, job_skills)
        missing_skills = matcher.find_missing_skills(resume_skills, job_skills)
        
        # Detailed matching analysis
        match_analysis = matcher.detailed_match(
            resume_text, job_description, resume_skills, job_skills
        )
        
        # Calculate ATS Score with all factors
        ats_result = ats_scorer.score(
            resume_text, job_description, resume_skills, 
            job_skills, matched_skills
        )
        
        # Process job description
        job_data = job_processor.process(job_description)
        job_requirements = job_processor.extract_job_requirements(job_description)
        job_seniority = job_processor.extract_seniority_level(job_description)
        
        # Generate recommendations
        analysis_data = {
            'ats_score': ats_result['ats_score'],
            'skill_match_percentage': match_analysis['skill_match_percentage'],
            'missing_skills': missing_skills,
            'matched_skills': matched_skills
        }
        recommendations = recommender.generate_recommendations(analysis_data)

        use_llm = request.form.get('use_llm', 'true').lower() in ('1', 'true', 'yes', 'on')
        llm_insights = {'enabled': False, 'reason': 'LLM analysis skipped'}
        if use_llm and llm_analyzer.is_available():
            llm_context = {
                'ats_score': ats_result['ats_score'],
                'skill_match_percentage': match_analysis['skill_match_percentage'],
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'job_seniority': job_seniority,
            }
            llm_insights = llm_analyzer.analyze(resume_text, job_description, llm_context)
        elif use_llm and not llm_analyzer.is_available():
            llm_insights = {
                'enabled': False,
                'reason': 'LLM requested but GOOGLE_API_KEY/GEMINI_API_KEY or OPENAI_API_KEY not configured',
            }

        display_recommendations = recommendations[:5]
        if llm_insights.get('enabled'):
            llm_recs = (llm_insights.get('ats_suggestions') or []) + (
                llm_insights.get('recommendations') or []
            )
            if llm_recs:
                display_recommendations = llm_recs[:6]
        
        # Compile results
        results = {
            'ats_score': ats_result['ats_score'],
            'ats_details': ats_result['scores'],
            'similarity_score': match_analysis['similarity_score'],
            'skill_match_percentage': match_analysis['skill_match_percentage'],
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'resume_skills': resume_skills,
            'job_skills': job_skills,
            'resume_skill_categories': skill_extractor.categorize_skills(resume_skills),
            'job_skill_categories': skill_extractor.categorize_skills(job_skills),
            'match_count': match_analysis['match_count'],
            'missing_count': match_analysis['missing_count'],
            'total_required': match_analysis['total_required'],
            'job_seniority': job_seniority,
            'recommendations': display_recommendations,
            'rule_based_recommendations': recommendations[:5],
            'llm_insights': llm_insights,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(results), 200
    
    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results():
    """Results page"""
    return render_template('result.html')

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple resumes against a job description"""
    try:
        resume_files = request.files.getlist('resumes')
        job_description = request.form.get('job_description')
        
        if not resume_files or not job_description:
            return jsonify({'error': 'Missing resumes or job description'}), 400
        
        ranker.clear_candidates()
        results_list = []
        
        for resume_file in resume_files:
            try:
                resume_text = parser.parse(resume_file)
                if not resume_text:
                    continue
                
                # Extract and match
                resume_skills = skill_extractor.extract(resume_text)
                job_skills = skill_extractor.extract(job_description)
                matched_skills = matcher.find_matching_skills(resume_skills, job_skills)
                
                # Score
                ats_result = ats_scorer.score(
                    resume_text, job_description, resume_skills,
                    job_skills, matched_skills
                )
                
                match_analysis = matcher.detailed_match(
                    resume_text, job_description, resume_skills, job_skills
                )
                
                candidate_data = {
                    'name': resume_file.filename,
                    'ats_score': ats_result['ats_score'],
                    'skill_match_percentage': match_analysis['skill_match_percentage'],
                    'matched_skills': matched_skills,
                    'missing_skills': matcher.find_missing_skills(resume_skills, job_skills)
                }
                
                ranker.add_candidate(candidate_data)
                results_list.append(candidate_data)
            
            except Exception as e:
                print(f"Error processing {resume_file.filename}: {str(e)}")
                continue
        
        # Rank candidates
        ranked = ranker.rank_candidates()
        stats = ranker.get_candidate_stats()
        
        return jsonify({
            'candidates': ranked,
            'stats': stats,
            'total_processed': len(results_list)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-analysis', methods=['POST'])
def job_analysis():
    """Analyze a job description"""
    try:
        job_description = request.json.get('job_description')
        if not job_description:
            return jsonify({'error': 'Missing job description'}), 400
        
        job_data = job_processor.process(job_description)
        requirements = job_processor.extract_job_requirements(job_description)
        summary = job_processor.get_job_summary(job_description)
        
        return jsonify({
            'skills': job_data['skills'],
            'keywords': job_data['keywords'],
            'requirements': requirements,
            'summary': summary,
            'skill_categories': job_data['skill_categories']
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/skills', methods=['GET'])
def get_skills():
    """Get available skills database"""
    try:
        import csv
        skills_list = []
        with open(project_path('data', 'skills.csv'), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            skills_list = list(reader)
        
        return jsonify(skills_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/llm/rewrite', methods=['POST'])
def llm_rewrite():
    """Rewrite a single resume bullet using the LLM."""
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get('text') or '').strip()
        job_description = (data.get('job_description') or '').strip()
        if not text:
            return jsonify({'error': 'Missing text to rewrite'}), 400
        result = llm_analyzer.rewrite_bullet(text, job_description)
        if not result.get('enabled'):
            return jsonify(result), 503
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/report', methods=['POST'])
def generate_report():
    """Generate a PDF report from POSTed analysis JSON."""
    try:
        data = request.get_json(silent=True) or {}
        if not data:
            return jsonify({'error': 'Missing analysis data'}), 400
        pdf_bytes = generate_report_pdf(data)
        return (pdf_bytes, 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': 'attachment; filename="resume_analysis.pdf"'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'llm': llm_analyzer.status(),
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    os.chdir(PROJECT_ROOT)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    debug = os.getenv('FLASK_DEBUG', 'true').lower() in ('1', 'true', 'yes')
    app.run(debug=debug, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))