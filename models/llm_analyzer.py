"""LLM layer: resume review, ATS tips, rewrites, skill gaps, interview prep."""

import json
import os
import re
import concurrent.futures
from typing import Any

MAX_RESUME_CHARS = 12_000
MAX_JOB_CHARS = 6_000

JSON_SCHEMA_HINT = """{
  "summary": "2-3 sentence fit assessment for this role",
  "fit_score": 0-100,
  "resume_review": {
    "strengths": ["..."],
    "weaknesses": ["..."],
    "improvements": ["..."]
  },
  "ats_suggestions": [
    {"priority": "high|medium|low", "category": "ATS", "message": "...", "action": "..."}
  ],
  "recommendations": [
    {"priority": "high|medium|low", "category": "Career", "message": "...", "action": "..."}
  ],
  "missing_skills_analysis": {
    "missing_skills": ["skill names"],
    "learning_path": ["course or certification suggestions"]
  },
  "resume_rewrites": [
    {"original": "weak bullet from resume", "improved": "stronger ATS-friendly bullet with metrics"}
  ],
  "interview_questions": ["technical and behavioral questions"],
  "career_guidance": "short paragraph on next steps"
}"""

# Compact schema for local/Ollama models (smaller prompt, faster generation).
OLLAMA_JSON_SCHEMA_HINT = """{
  "summary": "1 sentence",
  "fit_score": 0-100,
  "resume_review": {"strengths": ["max 2"], "weaknesses": ["max 2"], "improvements": ["max 2"]},
  "ats_suggestions": [{"priority": "high|medium|low", "message": "short", "action": "short"}],
  "resume_rewrites": [{"original": "short", "improved": "short"}],
  "interview_questions": ["max 2 questions"]
}"""


def _env(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


class LLMAnalyzer:
    """LLM service for post-ATS analysis (native Gemini or OpenAI-compatible)."""

    GEMINI_OPENAI_BASE = 'https://generativelanguage.googleapis.com/v1beta/openai/'
    DEFAULT_GEMINI_MODEL = 'gemini-2.0-flash'
    DEFAULT_TIMEOUT_S = 20.0
    OLLAMA_TIMEOUT_S = 50.0

    def __init__(self):
        google_key = _env('GOOGLE_API_KEY') or _env('GEMINI_API_KEY')
        openai_key = _env('OPENAI_API_KEY')
        llm_key = _env('LLM_API_KEY')

        self.api_key = openai_key or llm_key or google_key
        self.base_url = _env('LLM_BASE_URL')
        self.model = _env('LLM_MODEL') or 'gpt-4o-mini'
        self.provider = 'openai'
        self._use_native_gemini = False

        # Native Google Gemini SDK (GOOGLE_API_KEY / GEMINI_API_KEY)
        if google_key and not openai_key and not llm_key:
            self._use_native_gemini = True
            self.provider = 'gemini'
            self.api_key = google_key
            self.model = _env('GEMINI_MODEL') or self.DEFAULT_GEMINI_MODEL
            self.base_url = None
        elif self.base_url and '11434' in self.base_url:
            self.provider = 'ollama'
        elif self.base_url and 'generativelanguage.googleapis.com' in self.base_url:
            self.provider = 'gemini'
            if self.model == 'gpt-4o-mini':
                self.model = _env('GEMINI_MODEL') or self.DEFAULT_GEMINI_MODEL
        elif llm_key or openai_key:
            self.provider = 'openai'

        self._client = None

    def _is_ollama(self) -> bool:
        return self.provider == 'ollama' or bool(self.base_url and '11434' in self.base_url)

    def _request_timeout_s(self) -> float:
        return self.OLLAMA_TIMEOUT_S if self._is_ollama() else self.DEFAULT_TIMEOUT_S

    @staticmethod
    def _call_with_timeout(fn, timeout_s: float):
        """Hard timeout wrapper (prevents Flask request from hanging)."""
        ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        fut = ex.submit(fn)
        try:
            return fut.result(timeout=timeout_s)
        except concurrent.futures.TimeoutError:
            raise
        finally:
            # Do not wait for the worker thread after timeout (otherwise Flask hangs).
            ex.shutdown(wait=False, cancel_futures=True)

    def is_available(self) -> bool:
        flag = os.getenv('ENABLE_LLM', 'auto').lower()
        if flag in ('0', 'false', 'no', 'off'):
            return False
        if flag in ('1', 'true', 'yes', 'on'):
            return bool(self.api_key)
        return bool(self.api_key)

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError('Install openai: pip install openai') from e

        timeout_s = self._request_timeout_s()
        kwargs = {'api_key': self.api_key, 'timeout': timeout_s}
        if self.base_url:
            kwargs['base_url'] = self.base_url.rstrip('/')
        self._client = OpenAI(**kwargs)
        return self._client

    @staticmethod
    def _is_timeout_error(exc: Exception) -> bool:
        error_msg = str(exc).lower()
        return 'timeout' in error_msg or 'timed out' in error_msg

    def _chat_json(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int | None = None,
        use_json_mode: bool = True,
        timeout_s: float | None = None,
        temperature: float = 0.35,
    ) -> dict[str, Any]:
        client = self._get_client()
        request_timeout = timeout_s if timeout_s is not None else self._request_timeout_s()
        messages = [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user},
        ]
        create_kwargs: dict[str, Any] = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'timeout': request_timeout,
        }
        if use_json_mode:
            create_kwargs['response_format'] = {'type': 'json_object'}
        try:
            response = client.chat.completions.create(**create_kwargs)
        except Exception as first_error:
            if self._is_timeout_error(first_error) or not use_json_mode:
                if self._is_timeout_error(first_error):
                    raise TimeoutError(
                        f'LLM request timed out after {request_timeout:.0f}s: {first_error}'
                    ) from first_error
                raise
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=request_timeout,
                )
            except Exception as retry_error:
                if self._is_timeout_error(retry_error):
                    raise TimeoutError(
                        f'LLM request timed out after {request_timeout:.0f}s: {retry_error}'
                    ) from retry_error
                raise
        raw = response.choices[0].message.content or '{}'
        return self._parse_json(raw)

    def analyze(
        self,
        resume_text: str,
        job_description: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Full LLM pipeline after classical ATS scoring."""
        if not self.is_available():
            return {
                'enabled': False,
                'reason': (
                    'Set GOOGLE_API_KEY or GEMINI_API_KEY (Gemini) or OPENAI_API_KEY in .env. '
                    'See .env.example'
                ),
            }

        if self._use_native_gemini:
            try:
                from models import gemini_analyzer

                return gemini_analyzer.analyze(
                    self.api_key,
                    self.model,
                    resume_text,
                    job_description,
                    context,
                )
            except Exception as e:
                return {
                    'enabled': False,
                    'error': str(e),
                    'reason': 'Gemini request failed',
                }

        # Ollama/local models: keep prompts small to avoid long CPU-bound runs.
        is_ollama = self._is_ollama()
        job_limit = 1000 if is_ollama else MAX_JOB_CHARS
        resume_limit = 2000 if is_ollama else MAX_RESUME_CHARS
        max_tokens = 520 if is_ollama else 1200
        schema_hint = OLLAMA_JSON_SCHEMA_HINT if is_ollama else JSON_SCHEMA_HINT

        system = (
            'You are an expert technical recruiter and ATS specialist. '
            'Respond with valid JSON only matching this schema. '
            + ('Keep arrays to at most 2 items; keep strings concise; finish the JSON object.\n' if is_ollama else '')
            + schema_hint
        )

        user = (
            f'Role seniority (heuristic): {context.get("job_seniority", "unknown")}\n'
            f'Rule-based ATS score: {context.get("ats_score")}%\n'
            f'Skill match: {context.get("skill_match_percentage")}%\n'
            f'Matched skills: {", ".join(context.get("matched_skills") or []) or "none"}\n'
            f'Missing skills (extracted): {", ".join(context.get("missing_skills") or []) or "none"}\n\n'
            'Tasks:\n'
            + (
                '1) Resume review (max 2 items per list)\n'
                '2) Up to 2 ATS suggestions\n'
                '3) 1 resume bullet rewrite\n'
                '4) 2 interview questions\n'
                if is_ollama
                else
                '1) Resume review — strengths, weaknesses, improvements\n'
                '2) Personalized ATS suggestions (not generic rules)\n'
                '3) Up to 3 resume bullet rewrites (original → improved)\n'
                '4) Missing skills + learning path\n'
                '5) 5 interview questions (mix technical + behavioral)\n'
                '6) Brief career guidance\n'
            )
            + '\n'
            f'--- JOB DESCRIPTION ---\n{job_description[:job_limit]}\n\n'
            f'--- RESUME ---\n{resume_text[:resume_limit]}'
        )

        llm_timeout = self.OLLAMA_TIMEOUT_S if is_ollama else self.DEFAULT_TIMEOUT_S
        try:
            parsed = self._call_with_timeout(
                lambda: self._chat_json(
                    system,
                    user,
                    max_tokens=max_tokens,
                    use_json_mode=not is_ollama,
                    timeout_s=llm_timeout,
                    temperature=0.2 if is_ollama else 0.35,
                ),
                timeout_s=llm_timeout + 2.0,
            )
            out = self._normalize(parsed)
            out['provider'] = self.provider
            return out
        except (concurrent.futures.TimeoutError, TimeoutError):
            return {
                'enabled': False,
                'error': f'LLM timed out after {llm_timeout:.0f}s',
                'reason': 'LLM request timed out',
            }
        except json.JSONDecodeError as e:
            return {
                'enabled': False,
                'error': str(e),
                'reason': 'LLM returned invalid JSON',
            }
        except Exception as e:
            return {
                'enabled': False,
                'error': str(e),
                'reason': 'LLM request failed',
            }

    def rewrite_bullet(self, text: str, job_description: str = '') -> dict[str, Any]:
        """Rewrite a single resume line/bullet for ATS impact."""
        if not self.is_available():
            return {'enabled': False, 'reason': 'LLM not configured'}

        if self._use_native_gemini:
            try:
                from models import gemini_analyzer

                return gemini_analyzer.rewrite_bullet(
                    self.api_key,
                    self.model,
                    text,
                    job_description,
                )
            except Exception as e:
                return {'enabled': False, 'error': str(e)}

        is_ollama = self._is_ollama()
        rewrite_timeout = self.OLLAMA_TIMEOUT_S if is_ollama else self.DEFAULT_TIMEOUT_S
        original_text = text.strip()

        system = (
            'Improve resume bullet points for ATS and impact. '
            + (
                'Output ONLY a JSON object with keys original, improved, tips. '
                'No markdown, no code fences, no extra prose.'
                if is_ollama
                else 'Return JSON: {"original": "...", "improved": "...", "tips": "one line why"}'
            )
        )
        user = f'Bullet to improve:\n{original_text}\n'
        if job_description:
            user += f'\nTarget job context:\n{job_description[:2000 if not is_ollama else 1000]}'

        def _fetch_rewrite() -> dict[str, Any]:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
                temperature=0.2 if is_ollama else 0.35,
                max_tokens=220 if is_ollama else 220,
                timeout=rewrite_timeout,
            )
            raw = response.choices[0].message.content or ''
            return self._parse_rewrite_response(raw, original_text)

        try:
            parsed = self._call_with_timeout(_fetch_rewrite, timeout_s=rewrite_timeout + 2.0)
            parsed['enabled'] = True
            parsed['model'] = self.model
            return parsed
        except (concurrent.futures.TimeoutError, TimeoutError):
            return {'enabled': False, 'error': f'LLM timed out after {rewrite_timeout:.0f}s'}
        except Exception as e:
            return {'enabled': False, 'error': str(e)}

    def _normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        """Map LLM JSON to a stable API shape for the UI."""
        review = data.get('resume_review') or {}
        missing = data.get('missing_skills_analysis') or {}

        strengths = review.get('strengths') or data.get('strengths') or []
        weaknesses = review.get('weaknesses') or data.get('weaknesses') or data.get('gaps') or []
        improvements = review.get('improvements') or []

        ats_suggestions = data.get('ats_suggestions') or []
        recommendations = data.get('recommendations') or []
        if not recommendations and ats_suggestions:
            recommendations = ats_suggestions

        return {
            'enabled': True,
            'model': self.model,
            'provider': 'openai-compatible',
            'summary': data.get('summary', ''),
            'fit_score': data.get('fit_score'),
            'resume_review': {
                'strengths': strengths,
                'weaknesses': weaknesses,
                'improvements': improvements,
            },
            'strengths': strengths,
            'weaknesses': weaknesses,
            'gaps': weaknesses,
            'improvements': improvements,
            'ats_suggestions': ats_suggestions,
            'recommendations': recommendations,
            'missing_skills_analysis': {
                'missing_skills': missing.get('missing_skills') or [],
                'learning_path': missing.get('learning_path') or [],
            },
            'resume_rewrites': data.get('resume_rewrites') or [],
            'interview_questions': data.get('interview_questions') or data.get('interview_tips') or [],
            'interview_tips': data.get('interview_questions') or data.get('interview_tips') or [],
            'career_guidance': data.get('career_guidance', ''),
        }

    @staticmethod
    def _parse_rewrite_response(text: str, fallback_original: str) -> dict[str, Any]:
        text = (text or '').strip()
        if not text:
            raise json.JSONDecodeError('Empty LLM response', text, 0)
        try:
            data = LLMAnalyzer._parse_json(text)
        except json.JSONDecodeError:
            improved = re.search(
                r'\*\*Improved\*\*:\s*(.+?)(?:\n\n|\*\*Tips|\Z)',
                text,
                re.S | re.I,
            )
            original = re.search(
                r'\*\*Original\*\*:\s*(.+?)(?:\n\n|\*\*Improved|\Z)',
                text,
                re.S | re.I,
            )
            tips = re.search(r'\*\*Tips\*\*:\s*(.+?)(?:\n\n|\Z)', text, re.S | re.I)
            if not improved:
                raise
            data = {
                'original': original.group(1).strip() if original else fallback_original,
                'improved': improved.group(1).strip(),
                'tips': tips.group(1).strip() if tips else '',
            }
        if not data.get('improved'):
            raise ValueError('LLM response missing improved bullet')
        data.setdefault('original', fallback_original)
        return data

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        text = text.strip()
        fence = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if fence:
            text = fence.group(1).strip()
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError('LLM response was not a JSON object')
        return data

    def status(self) -> dict[str, Any]:
        if self._use_native_gemini:
            default_base = 'google-generativeai (native SDK)'
        elif self.provider == 'gemini':
            default_base = self.GEMINI_OPENAI_BASE
        else:
            default_base = 'https://api.openai.com/v1'
        return {
            'available': self.is_available(),
            'provider': self.provider if self.is_available() else None,
            'model': self.model if self.is_available() else None,
            'base_url': self.base_url or default_base,
            'native_gemini': self._use_native_gemini,
            'features': [
                'resume_review',
                'ats_suggestions',
                'resume_rewrites',
                'missing_skills_analysis',
                'interview_questions',
                'career_guidance',
            ],
        }
