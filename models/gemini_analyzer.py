"""Native Google Gemini SDK for resume LLM analysis."""

from typing import Any

from models.llm_analyzer import (
    JSON_SCHEMA_HINT,
    MAX_JOB_CHARS,
    MAX_RESUME_CHARS,
    LLMAnalyzer,
)


def _get_model(api_key: str, model_name: str, system: str):
    try:
        import google.generativeai as genai
    except ImportError as e:
        raise RuntimeError(
            'Install google-generativeai: pip install google-generativeai'
        ) from e

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system,
        generation_config=genai.GenerationConfig(
            temperature=0.35,
            response_mime_type='application/json',
        ),
    )


def _chat_json(api_key: str, model_name: str, system: str, user: str) -> dict[str, Any]:
    model = _get_model(api_key, model_name, system)
    response = model.generate_content(user)
    raw = (response.text or '{}').strip()
    return LLMAnalyzer._parse_json(raw)


def analyze(
    api_key: str,
    model_name: str,
    resume_text: str,
    job_description: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Full LLM pipeline via native Gemini; same JSON shape as LLMAnalyzer.analyze."""
    system = (
        'You are an expert technical recruiter, ATS specialist, and career coach. '
        'Given a resume and job description, produce actionable, specific feedback. '
        'Use quantified rewrite examples where possible. '
        'Respond with valid JSON only matching this schema:\n'
        + JSON_SCHEMA_HINT
    )

    user = (
        f'Role seniority (heuristic): {context.get("job_seniority", "unknown")}\n'
        f'Rule-based ATS score: {context.get("ats_score")}%\n'
        f'Skill match: {context.get("skill_match_percentage")}%\n'
        f'Matched skills: {", ".join(context.get("matched_skills") or []) or "none"}\n'
        f'Missing skills (extracted): {", ".join(context.get("missing_skills") or []) or "none"}\n\n'
        'Tasks:\n'
        '1) Resume review — strengths, weaknesses, improvements\n'
        '2) Personalized ATS suggestions (not generic rules)\n'
        '3) Up to 3 resume bullet rewrites (original → improved)\n'
        '4) Missing skills + learning path\n'
        '5) 5 interview questions (mix technical + behavioral)\n'
        '6) Brief career guidance\n\n'
        f'--- JOB DESCRIPTION ---\n{job_description[:MAX_JOB_CHARS]}\n\n'
        f'--- RESUME ---\n{resume_text[:MAX_RESUME_CHARS]}'
    )

    parsed = _chat_json(api_key, model_name, system, user)
    result = LLMAnalyzer._normalize(parsed)
    result['provider'] = 'gemini'
    result['model'] = model_name
    return result


def rewrite_bullet(
    api_key: str,
    model_name: str,
    text: str,
    job_description: str = '',
) -> dict[str, Any]:
    """Rewrite a single resume bullet via native Gemini."""
    system = (
        'Improve resume bullet points for ATS and impact. '
        'Return JSON: {"original": "...", "improved": "...", "tips": "one line why"}'
    )
    user = f'Bullet to improve:\n{text.strip()}\n'
    if job_description:
        user += f'\nTarget job context:\n{job_description[:2000]}'

    parsed = _chat_json(api_key, model_name, system, user)
    parsed['enabled'] = True
    parsed['model'] = model_name
    parsed['provider'] = 'gemini'
    return parsed
