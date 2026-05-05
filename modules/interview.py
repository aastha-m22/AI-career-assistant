"""
modules/interview.py — Interview preparation module.
Wraps llm_engine.generate_interview_questions with formatting helpers.
"""
from modules.llm_engine import call_llm
import json, re

QUESTION_CATEGORIES = {
    "behavioral":  {"icon": "🧠", "label": "Behavioral",  "color": "#818cf8"},
    "technical":   {"icon": "⚙️",  "label": "Technical",   "color": "#34d399"},
    "situational": {"icon": "🎯",  "label": "Situational", "color": "#fb923c"},
}

def generate_questions(resume_text: str, jd_text: str) -> dict:
    from modules.llm_engine import generate_interview_questions
    return generate_interview_questions(resume_text, jd_text)

def generate_answer_feedback(question: str, user_answer: str, job_context: str = "") -> dict:
    """Evaluate a user's practice answer and provide structured feedback."""
    system = """You are an expert interview coach. Evaluate answers fairly and constructively.
Be specific, encouraging, and actionable."""

    user = f"""Evaluate this interview answer.

QUESTION: {question}
CANDIDATE'S ANSWER: {user_answer}
{"JOB CONTEXT: " + job_context[:300] if job_context else ""}

Respond ONLY with valid JSON:
{{
  "score": 7,
  "verdict": "Good answer with room for improvement",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"],
  "enhanced_answer": "A stronger version of this answer in 3-4 sentences",
  "star_breakdown": {{"situation": "...", "task": "...", "action": "...", "result": "..."}}
}}"""

    raw = call_llm(system, user, max_tokens=700)
    raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
    try:
        return json.loads(raw)
    except Exception:
        return {
            "score": 6,
            "verdict": "Answer received",
            "strengths": ["You provided an answer"],
            "improvements": ["Add specific examples", "Quantify outcomes"],
            "enhanced_answer": user_answer,
            "star_breakdown": {"situation":"","task":"","action":"","result":""},
        }

def get_quick_tips(role_keywords: list) -> list:
    """Return general interview tips relevant to the role."""
    tips = [
        "Research the company's recent news, products, and culture before the interview",
        "Prepare 2-3 questions to ask the interviewer — it shows genuine interest",
        "Use the STAR method (Situation, Task, Action, Result) for behavioral questions",
        "Quantify your achievements wherever possible (e.g., 'improved performance by 40%')",
        "Practice out loud — hearing your own answers reveals weak spots",
        "Have your resume open and refer to specific projects when relevant",
        "Arrive 5-10 minutes early for in-person; test your tech 15 mins before virtual",
        "Follow up with a thank-you email within 24 hours",
    ]
    return tips
