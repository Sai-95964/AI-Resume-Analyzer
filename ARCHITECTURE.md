"""
ARCHITECTURE DOCUMENTATION
AI Resume Analyzer & ATS Scorer
"""

# SYSTEM ARCHITECTURE

## 1. HIGH-LEVEL WORKFLOW

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ Upload Resume + Job Description
       ▼
┌─────────────────────────────────────────┐
│     Flask Web Application (app.py)      │
│  - /api/analyze (single resume)        │
│  - /api/batch-analyze (multiple)       │
│  - /api/job-analysis                   │
└──────┬──────────────────────────────────┘
       │
       ▼
┌──────────────────────────┐
│  Resume Parser           │
│  (PDF/DOCX/TXT)         │
└──────┬───────────────────┘
       │ Raw Text
       ▼
┌──────────────────────────┐      ┌─────────────────┐
│  Text Preprocessor       │──────▶ NLTK Data Files │
│  - Clean                 │      └─────────────────┘
│  - Tokenize              │
│  - Lemmatize             │
│  - Remove Stopwords      │
└──────┬───────────────────┘
       │ Cleaned Text
       ▼
┌──────────────────────────┐      ┌─────────────────┐
│  Skill Extractor         │──────▶ skills.csv      │
│  - Exact Match           │      │ (Database)      │
│  - Fuzzy Match           │      └─────────────────┘
│  - Categorization        │
└──────┬───────────────────┘
       │ Extracted Skills
       ▼
┌──────────────────────────────────┐
│  Job Description Processor       │
│  - Extract Requirements          │
│  - Detect Seniority Level        │
│  - Analyze Keywords              │
└──────┬───────────────────────────┘
       │
       ├─ Resume Skills
       ├─ Job Skills
       └─ Matched/Missing Skills
       │
       ▼
┌──────────────────────────────────┐
│  Resume Matcher                  │
│  - TF-IDF Vectorization         │
│  - Cosine Similarity            │
│  - Detailed Analysis            │
└──────┬───────────────────────────┘
       │ Match Scores & Skills
       ▼
┌──────────────────────────────────┐
│  ATS Scorer (Weighted)           │
│  - Skill Match (40%)            │
│  - Keyword Match (30%)          │
│  - Experience (15%)             │
│  - Education (10%)              │
│  - Format (5%)                  │
└──────┬───────────────────────────┘
       │ ATS Score + Breakdown
       ▼
┌──────────────────────────────────┐
│  Recommendation Engine           │
│  - Priority Ranking             │
│  - Actionable Suggestions       │
│  - Category Organization        │
└──────┬───────────────────────────┘
       │ Recommendations
       ▼
┌──────────────────────────────────┐
│  Candidate Ranker (Batch)       │
│  - Ranking                      │
│  - Statistics                   │
│  - Comparison                   │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Results Dashboard               │
│  - JSON API Response            │
│  - HTML Result Page             │
└──────────────────────────────────┘
```

## 2. MODULE INTERACTION DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask App (Entry Point)                 │
├─────────────────────────────────────────────────────────────┤
│  Routes:                                                    │
│  ├─ /                  (index page)                        │
│  ├─ /api/analyze       (single resume analysis)            │
│  ├─ /api/batch-analyze (multiple resume analysis)          │
│  ├─ /api/job-analysis  (job description analysis)          │
│  ├─ /api/skills        (skills database)                   │
│  └─ /health            (health check)                      │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├─────────────────────┬──────────────────────┬────────────────┐
       │                     │                      │                │
       ▼                     ▼                      ▼                ▼
┌─────────────┐      ┌──────────────┐    ┌───────────────┐  ┌──────────────┐
│   Parser    │      │Preprocessor  │    │SkillExtractor│  │    Matcher   │
│  (utils)    │      │  (utils)     │    │  (utils)      │  │   (models)   │
└─────────────┘      └──────────────┘    └───────────────┘  └──────────────┘
       │                     │                      │                │
       │                     ▼                      ▼                │
       │             ┌──────────────────────────────────┐           │
       │             │  Text Processing Pipeline       │           │
       │             │  1. Clean Text                 │           │
       │             │  2. Remove URLs/Emails        │           │
       │             │  3. Tokenize                  │           │
       │             │  4. Remove Stopwords          │           │
       │             │  5. Lemmatize                 │           │
       │             │  6. Extract Keywords          │           │
       │             └──────────┬───────────────────┘            │
       │                        │                                 │
       │                        └─────┬──────────────────────────┘
       │                              │
       │                              ▼
       │                     ┌──────────────────────┐
       │                     │  Cleaned Text        │
       │                     │  + Keywords          │
       │                     │  + Tokens            │
       │                     └────────┬─────────────┘
       │                              │
       └──────────────┬───────────────┴──────────────────┬───────────┐
                      │                                  │           │
                      ▼                                  ▼           ▼
         ┌─────────────────────┐      ┌────────────┐  ┌──────────────────┐
         │  Job Processor      │      │ATSScorer   │  │ Candidate Ranker │
         │  - Extract Reqs     │      │(models)    │  │ (models)         │
         │  - Detect Seniority │      │ Weighted   │  └──────────────────┘
         │  - Parse Keywords   │      │ Formula    │
         └──────┬──────────────┘      └─────┬──────┘
                │                           │
                ▼                           ▼
      ┌──────────────────────┐  ┌──────────────────────┐
      │  Job Requirements    │  │  ATS Score Details   │
      │  - Must-have skills  │  │  - Score breakdown   │
      │  - Nice-to-have      │  │  - Component scores  │
      │  - Seniority level   │  └────────┬─────────────┘
      └────────┬─────────────┘           │
               │                         ▼
               │                ┌──────────────────────┐
               │                │ Recommendation Engine│
               │                │ - Analyze scores    │
               │                │ - Generate actions  │
               │                │ - Prioritize items  │
               │                └────────┬─────────────┘
               │                         │
               └──────────┬──────────────┘
                          │
                          ▼
                  ┌──────────────────────┐
                  │  Final Results JSON  │
                  │  - ATS Score: 85/100 │
                  │  - Matched Skills: []│
                  │  - Missing Skills: []│
                  │  - Recommendations:[]│
                  │  - Rankings: []      │
                  └────────────────────────┘
```

## 3. DATA FLOW EXAMPLE

### Input:
```
Resume: "Python developer with 5 years experience..."
Job Description: "Looking for Python engineer with AWS experience..."
```

### Processing:

1. **Parser**: Extract text from resume file
2. **Preprocessor**: Clean and normalize text
3. **SkillExtractor**: Find "Python", "AWS" in texts
4. **Matcher**: Calculate TF-IDF similarity (82%)
5. **ATSScorer**: Calculate weighted score (85/100)
6. **Recommender**: Generate suggestions
7. **Ranker**: Rank among other candidates

### Output:
```json
{
  "ats_score": 85.0,
  "matched_skills": ["Python"],
  "missing_skills": ["AWS"],
  "recommendations": [
    {
      "priority": "high",
      "message": "Add AWS experience"
    }
  ]
}
```

## 4. COMPONENT RESPONSIBILITIES

### Parser (utils/parser.py)
- Convert PDF/DOCX/TXT → Plain Text
- Handle encoding issues
- Error handling for corrupted files

### TextPreprocessor (utils/preprocess.py)
- Normalize text (lowercase, remove special chars)
- Remove noise (URLs, emails)
- Tokenization and lemmatization
- Keyword extraction

### SkillExtractor (utils/skill_extractor.py)
- Load skills database from CSV
- Perform exact and fuzzy matching
- Calculate confidence scores
- Categorize by skill type

### ResumeMatcher (models/matcher.py)
- Vectorize texts using TF-IDF
- Calculate cosine similarity
- Find matching/missing skills
- Provide detailed metrics

### ATSScorer (models/ats_scorer.py)
- Calculate 5 component scores
- Apply weighted formula
- Return breakdown

### RecommendationEngine (models/recommender.py)
- Analyze all metrics
- Generate prioritized suggestions
- Provide actionable advice

### JobProcessor (models/job_processor.py)
- Extract job requirements
- Detect seniority level
- Analyze keywords

### CandidateRanker (models/ranker.py)
- Store candidate data
- Rank by ATS score
- Compare candidates
- Filter by threshold

## 5. ATS SCORE CALCULATION

```
Component Weights:
├─ Skill Match:       40%
│  └─ Matched / Total Required Skills
├─ Keyword Match:     30%
│  └─ TF-IDF Cosine Similarity
├─ Experience:        15%
│  └─ Keywords: worked, managed, led, developed
├─ Education:         10%
│  └─ Keywords: bachelor, master, certified
└─ Format:            5%
   └─ Word count (200-1000) + structure

Formula:
ATS Score = (skill_score × 0.40) +
            (keyword_score × 0.30) +
            (experience_score × 0.15) +
            (education_score × 0.10) +
            (format_score × 0.05)

Range: 0-100
```

## 6. API RESPONSE STRUCTURE

```json
{
  "ats_score": 85.5,
  "ats_details": {
    "skill_match": 90.0,
    "keyword_match": 80.0,
    "experience": 70.0,
    "education": 100.0,
    "format": 85.0
  },
  "similarity_score": 82.5,
  "skill_match_percentage": 75.0,
  "matched_skills": ["Python", "SQL", "Flask"],
  "missing_skills": ["AWS", "Docker"],
  "resume_skills": ["Python", "SQL", "Flask", "JavaScript"],
  "job_skills": ["Python", "SQL", "Flask", "AWS", "Docker"],
  "resume_skill_categories": {
    "Programming": ["Python", "JavaScript"],
    "Database": ["SQL"],
    "Web Framework": ["Flask"]
  },
  "job_skill_categories": {...},
  "match_count": 3,
  "missing_count": 2,
  "total_required": 5,
  "job_seniority": "mid",
  "recommendations": [
    {
      "priority": "high",
      "category": "Missing Skills",
      "message": "Add experience with: AWS, Docker",
      "action": "Include these 2 skills..."
    }
  ],
  "timestamp": "2024-06-02T10:30:45"
}
```

## 7. PERFORMANCE CHARACTERISTICS

| Operation | Time | Complexity |
|-----------|------|-----------|
| PDF Parsing | ~200ms | O(pages) |
| Text Cleaning | ~50ms | O(words) |
| Skill Extraction | ~100ms | O(skills × words) |
| TF-IDF Vectorization | ~120ms | O(documents × vocabulary) |
| Similarity Calculation | ~30ms | O(vector_size²) |
| Scoring | ~50ms | O(1) |
| **Total** | **<500ms** | **O(n)** |

## 8. ERROR HANDLING

```
Try-Catch at each stage:
├─ File upload → Validate format
├─ Parsing → Handle corrupted files
├─ Preprocessing → Handle encoding
├─ Skill extraction → Graceful fallback
├─ Scoring → Default values
└─ Response → JSON error format
```

## 9. DATABASE STRUCTURE

### skills.csv
```
skill,category,level
Python,Programming,intermediate
Java,Programming,beginner
JavaScript,Programming,intermediate
SQL,Database,intermediate
MongoDB,Database,beginner
Flask,Web Framework,intermediate
...
```

## 10. DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────┐
│      Client (Browser)               │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Nginx / Load Balancer              │
└──────────┬──────────────────────────┘
           │
      ┌────┴────┬─────────┐
      │          │         │
      ▼          ▼         ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Gunicorn │ │ Gunicorn │ │ Gunicorn │
│ (Worker) │ │ (Worker) │ │ (Worker) │
└────┬─────┘ └────┬─────┘ └────┬─────┘
     └────────┬───────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Flask App         │
    │   - All Modules     │
    │   - All Routes      │
    └────────┬────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
   ┌────────┐  ┌──────────┐
   │Local   │  │ Optional │
   │Storage │  │ Database │
   └────────┘  └──────────┘
```

---

**Architecture Version**: 1.0  
**Last Updated**: June 2024  
**Status**: Production Ready
