# AI Resume Analyzer

An intelligent resume analysis tool that evaluates resumes against job descriptions using AI and machine learning.

## Features

- **ATS Scoring**: Calculates ATS (Applicant Tracking System) compatibility scores
- **Resume-Job Matching**: Matches resume content with job requirements
- **Skill Extraction**: Automatically extracts and identifies relevant skills
- **Recommendations**: Provides suggestions for resume improvement
- **Web Interface**: User-friendly Flask web application

## Project Structure

```
AI_Resume_Analyzer/
├── app.py              # Flask application entry point
├── requirements.txt    # Python dependencies
├── data/              # Data directory
│   ├── resumes/       # Resume files
│   ├── job_descriptions/  # Job description files
│   └── skills.csv     # Skills database
├── models/            # ML models
│   ├── ats_scorer.py  # ATS scoring model
│   ├── matcher.py     # Resume matching model
│   └── recommender.py # Recommendation engine
├── utils/             # Utility modules
│   ├── parser.py      # Resume parser
│   ├── preprocess.py  # Text preprocessing
│   ├── skill_extractor.py  # Skill extraction
│   └── similarity.py  # Similarity calculations
├── templates/         # HTML templates
│   ├── index.html     # Main page
│   └── result.html    # Results page
└── static/           # Static files
    ├── css/          # Stylesheets
    └── images/       # Images
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the app (recommended — sets correct working directory):
   ```bash
   python run.py
   ```
2. Open `http://127.0.0.1:5000`
3. Upload a PDF, DOCX, or TXT resume and paste a job description
4. View results on the results page

Copy `.env.example` to `.env` and set `SECRET_KEY` before production. Validate with `python TEST_SUITE.py`.

## Quick local test (after Gemini key setup)

From project root:

```bash
cd AI_Resume_Analyzer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

In another terminal (same activated venv):

```bash
cd AI_Resume_Analyzer
venv\Scripts\activate
python -c "from app import app; c=app.test_client(); h=c.get('/health').get_json(); print({'status': h.get('status'), 'llm_available': h.get('llm',{}).get('available'), 'provider': h.get('llm',{}).get('provider')})"
python -c "from app import app; c=app.test_client(); r=c.post('/api/analyze', data={}); print(r.status_code, r.get_json().get('error'))"
```

Expected:
- Health reports `status: ok`
- `llm_available` is `true` when Gemini key is configured
- Analyze validation returns `400` with `Missing resume or job description`

### LLM layer (optional)

Classical scoring always runs first (TF-IDF, skills CSV, rules). With an API key set, one LLM call adds resume review, ATS suggestions, rewrites, skill gaps, interview questions, and career guidance.

Uncheck **Include AI analysis** on the form for faster rule-only runs.

#### Google Gemini (recommended if you use Google AI Studio)

**Security:** Never commit `.env` or paste API keys in chat, screenshots, or GitHub. If a key was exposed, **delete it in Google Cloud Console → APIs & Services → Credentials** and create a new one.

1. In [Google AI Studio](https://aistudio.google.com/) or [Google Cloud Console](https://console.cloud.google.com/), create an API key.
2. Enable the **Generative Language API** for that project ([API Library](https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com)).
3. **Which Google Cloud project?** When AI Studio or Cloud Console asks you to **Import project** or pick a project, choose the project that **owns the API key and billing** (e.g. `AI-Resume-Analyzer`). Usage and charges apply to that project—not a personal Gmail account unless you created the key there. All team members should use keys from the same project if you share costs and quotas.
4. Copy the example env file and edit locally only:
   ```bash
   cd AI_Resume_Analyzer
   copy .env.example .env
   ```
5. Add these lines to `.env` (use your **new** key, not one shared publicly):
   ```env
   ENABLE_LLM=auto
   GOOGLE_API_KEY=your-google-api-key-here
   GEMINI_MODEL=gemini-2.0-flash
   ```
   (`GEMINI_API_KEY` works as an alias.) The app uses the **native** `google-generativeai` SDK (`models/gemini_analyzer.py`), not a third-party OpenAI shim.
6. Install deps and start:
   ```bash
   pip install -r requirements.txt
   python run.py
   ```
7. Verify LLM is on:
   - Browser: http://127.0.0.1:5000/health → `"llm": { "available": true, "provider": "gemini", "native_gemini": true, ... }`
   - Terminal:
     ```bash
     python -c "from models.llm_analyzer import LLMAnalyzer; print(LLMAnalyzer().status())"
     ```
8. On the home page, click **Load demo data** → **Analyze Resume** (keep **Include AI analysis** checked).

**OpenAI:** set `OPENAI_API_KEY=sk-...` and `LLM_MODEL=gpt-4o-mini` instead of `GOOGLE_API_KEY`.

**Ollama (free local):** `LLM_BASE_URL=http://localhost:11434/v1`, `LLM_MODEL=llama3.2`, `OPENAI_API_KEY=ollama`

**Rewrite API:** `POST /api/llm/rewrite` with JSON `{"text": "...", "job_description": "..."}`

Set `ENABLE_LLM=false` to disable the LLM layer entirely.

### Docker

```bash
docker build -t resume-analyzer .
docker run -p 5000:5000 -e GOOGLE_API_KEY=your-key resume-analyzer
```

### Demo data

Click **Load demo data** on the home page, or `GET /api/samples`.

## License

MIT