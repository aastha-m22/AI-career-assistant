"""
modules/jd_matcher.py — Job Description matching using TF-IDF + cosine similarity.
"""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_cleaning import clean_text
from config import SKILLS_DB

def compute_match_score(resume_text: str, jd_text: str) -> float:
    """TF-IDF cosine similarity between resume and JD. Returns 0-100."""
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=10000)
    tfidf = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(float(score) * 100, 1)

def get_matching_keywords(resume_text: str, jd_text: str, top_n: int = 20) -> list:
    """Find important JD keywords that ARE present in the resume."""
    vectorizer = TfidfVectorizer(stop_words="english", max_features=80, ngram_range=(1, 2))
    vectorizer.fit([jd_text])
    jd_terms = set(vectorizer.get_feature_names_out())
    resume_lower = resume_text.lower()
    return sorted([t for t in jd_terms if t.lower() in resume_lower])[:top_n]

def get_missing_keywords(resume_text: str, jd_text: str, top_n: int = 20) -> list:
    """Find important JD keywords ABSENT from the resume."""
    vectorizer = TfidfVectorizer(stop_words="english", max_features=80, ngram_range=(1, 2))
    vectorizer.fit([jd_text])
    jd_terms = set(vectorizer.get_feature_names_out())
    resume_lower = resume_text.lower()
    return sorted([t for t in jd_terms if t.lower() not in resume_lower])[:top_n]

def get_skill_gap(resume_skills: list, jd_text: str) -> dict:
    """Compare detected resume skills against skills mentioned in JD."""
    jd_lower = jd_text.lower()
    resume_skills_lower = {s.lower() for s in resume_skills}
    jd_skills = []
    for skill in SKILLS_DB:
        if re.search(r"\b" + re.escape(skill) + r"\b", jd_lower):
            jd_skills.append(skill.title())
    matched  = [s for s in jd_skills if s.lower() in resume_skills_lower]
    missing  = [s for s in jd_skills if s.lower() not in resume_skills_lower]
    return {"jd_skills": jd_skills, "matched": matched, "missing": missing}

def full_match_analysis(resume_text: str, jd_text: str, resume_skills: list) -> dict:
    """Run all matching analyses and return consolidated result."""
    score        = compute_match_score(resume_text, jd_text)
    matching_kw  = get_matching_keywords(resume_text, jd_text)
    missing_kw   = get_missing_keywords(resume_text, jd_text)
    skill_gap    = get_skill_gap(resume_skills, jd_text)
    # Strength labels
    if score >= 75:   strength = ("Strong Match", "green")
    elif score >= 50: strength = ("Good Match", "orange")
    elif score >= 30: strength = ("Moderate Match", "yellow")
    else:             strength = ("Weak Match", "red")
    return {
        "score":        score,
        "strength":     strength[0],
        "color":        strength[1],
        "matching_kw":  matching_kw,
        "missing_kw":   missing_kw,
        "skill_gap":    skill_gap,
    }
