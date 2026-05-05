"""
modules/llm_engine.py — Unified LLM client (Groq + OpenAI via OpenAI SDK).
All modules call _call_llm() for AI generation.
"""
from openai import OpenAI
from config import llm_config

def _get_client():
    if llm_config.provider == "none":
        raise EnvironmentError("No API key found. Set GROQ_API_KEY or OPENAI_API_KEY in .env")
    kwargs = {"api_key": llm_config.active_key}
    if llm_config.base_url:
        kwargs["base_url"] = llm_config.base_url
    return OpenAI(**kwargs)

def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = None) -> str:
    """Core LLM call. Returns response text."""
    client = _get_client()
    resp = client.chat.completions.create(
        model=llm_config.model,
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_prompt},
        ],
        temperature=llm_config.temperature,
        max_tokens=max_tokens or llm_config.max_tokens,
    )
    return resp.choices[0].message.content.strip()

def generate_resume_feedback(resume_text: str, jd_text: str, parsed: dict,
                              match_score: float, missing_kw: list) -> dict:
    """Generate structured AI resume feedback."""
    import json, re
    system = """You are an expert career coach and senior technical recruiter with 15+ years experience.
Provide specific, actionable feedback. Be direct and professional. No generic advice."""

    user = f"""Analyze this resume against the job description.

JOB DESCRIPTION:
{jd_text[:1500]}

RESUME (extracted text):
{resume_text[:2000]}

MATCH SCORE: {match_score}%
DETECTED SKILLS: {", ".join(parsed.get("skills", [])) or "None"}
MISSING KEYWORDS: {", ".join(missing_kw[:12]) or "None"}

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "overall_assessment": "2-3 sentence honest overall assessment",
  "strengths": ["strength 1", "strength 2", "strength 3", "strength 4"],
  "improvements": ["specific improvement 1", "specific improvement 2", "specific improvement 3", "specific improvement 4"],
  "missing_skills": ["skill 1", "skill 2", "skill 3", "skill 4", "skill 5"],
  "ats_tips": ["ATS tip 1", "ATS tip 2", "ATS tip 3"],
  "priority_action": "The single most impactful thing to do right now"
}}"""

    raw = call_llm(system, user, max_tokens=900)
    raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
    try:
        return json.loads(raw)
    except Exception:
        return {
            "overall_assessment": raw[:300],
            "strengths":    ["See full analysis above"],
            "improvements": missing_kw[:4],
            "missing_skills": missing_kw[:5],
            "ats_tips": ["Use standard section headers", "Quantify achievements", "Match JD keywords"],
            "priority_action": "Address the missing keywords listed above",
        }

def generate_interview_questions(resume_text: str, jd_text: str, num_questions: int = 8) -> dict:
    """Generate role-specific interview Q&A with tips."""
    import json, re
    system = """You are a senior technical interviewer at a top tech company.
Generate realistic, challenging interview questions tailored to this specific role and candidate."""

    user = f"""Generate interview questions for this candidate applying to this role.

JOB DESCRIPTION:
{jd_text[:1200]}

RESUME SUMMARY:
{resume_text[:1500]}

Respond ONLY with valid JSON:
{{
  "behavioral": [
    {{"question": "...", "why_asked": "...", "sample_answer": "...", "tip": "..."}}
  ],
  "technical": [
    {{"question": "...", "why_asked": "...", "sample_answer": "...", "tip": "..."}}
  ],
  "situational": [
    {{"question": "...", "why_asked": "...", "sample_answer": "...", "tip": "..."}}
  ]
}}
Include 3 behavioral, 3 technical, 2 situational questions."""

    raw = call_llm(system, user, max_tokens=1600)
    raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
    try:
        return json.loads(raw)
    except Exception:
        return {
            "behavioral":  [{"question": raw[:200], "why_asked": "General fit", "sample_answer": "Use STAR method", "tip": "Be specific"}],
            "technical":   [],
            "situational": [],
        }

def generate_study_roadmap(missing_skills: list, timeline_weeks: int = 12,
                           current_level: str = "intermediate") -> dict:
    """Generate a structured learning roadmap for missing skills."""
    import json, re
    if not missing_skills:
        return {"phases": [], "summary": "No skill gaps detected!"}

    system = """You are a senior learning architect and career development specialist.
Create practical, achievable learning roadmaps with real resources."""

    user = f"""Create a {timeline_weeks}-week learning roadmap for a {current_level}-level professional.

SKILLS TO LEARN: {", ".join(missing_skills[:10])}

Respond ONLY with valid JSON:
{{
  "summary": "brief overview of the roadmap",
  "phases": [
    {{
      "phase": 1,
      "title": "Foundation Phase",
      "weeks": "1-3",
      "focus": "what to focus on",
      "skills": ["skill1", "skill2"],
      "resources": [
        {{"name": "resource name", "type": "Course/Book/Tutorial/Practice", "url_hint": "platform name", "time": "X hours"}}
      ],
      "milestones": ["milestone 1", "milestone 2"],
      "daily_hours": 1.5
    }}
  ],
  "tips": ["practical tip 1", "practical tip 2", "practical tip 3"],
  "weekly_schedule": "brief description of ideal weekly study schedule"
}}
Create 3-4 phases covering all skills progressively."""

    raw = call_llm(system, user, max_tokens=1600)
    raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
    try:
        return json.loads(raw)
    except Exception:
        # Fallback structured response
        return {
            "summary": f"A {timeline_weeks}-week plan to master {len(missing_skills)} skills.",
            "phases": [
                {
                    "phase": 1, "title": "Core Skills", "weeks": f"1-{timeline_weeks//2}",
                    "focus": "Build foundational knowledge",
                    "skills": missing_skills[:5],
                    "resources": [{"name": r, "type": "Course", "url_hint": "Online", "time": "10-20 hours"}
                                   for r in ["Coursera", "Udemy", "Official Docs"]],
                    "milestones": ["Complete first course", "Build a small project"],
                    "daily_hours": 1.5,
                }
            ],
            "tips": ["Consistency beats intensity", "Build projects as you learn", "Join communities"],
            "weekly_schedule": "1-2 hours daily, focus on one skill at a time",
        }
