"""
modules/roadmap.py — Study roadmap generation module.
"""
from modules.llm_engine import generate_study_roadmap
from config import RESOURCE_TEMPLATES

LEVEL_OPTIONS = ["beginner", "intermediate", "advanced"]
TIMELINE_OPTIONS = {
    "1 Month (Intensive)": 4,
    "3 Months (Balanced)": 12,
    "6 Months (Steady)": 24,
    "1 Year (Comprehensive)": 52,
}

def build_roadmap(missing_skills: list, timeline_label: str = "3 Months (Balanced)",
                  current_level: str = "intermediate") -> dict:
    """Build a complete study roadmap for the given missing skills."""
    if not missing_skills:
        return {"phases": [], "summary": "Great news — no significant skill gaps detected!", "tips": [], "weekly_schedule": ""}
    weeks = TIMELINE_OPTIONS.get(timeline_label, 12)
    return generate_study_roadmap(missing_skills, timeline_weeks=weeks, current_level=current_level)

def get_resource_links(skill: str) -> list:
    """Return curated resources for a skill from the template database."""
    skill_lower = skill.lower()
    for key, resources in RESOURCE_TEMPLATES.items():
        if key in skill_lower or skill_lower in key:
            return resources
    return RESOURCE_TEMPLATES["default"]

def estimate_total_hours(phases: list) -> float:
    """Estimate total study hours from roadmap phases."""
    total = 0.0
    for phase in phases:
        daily = phase.get("daily_hours", 1.5)
        # Parse week range e.g. "1-4" or "5-8"
        weeks_str = str(phase.get("weeks", "1-4"))
        try:
            parts = [int(x) for x in weeks_str.replace("–","-").split("-")]
            num_weeks = parts[-1] - parts[0] + 1 if len(parts) == 2 else 2
        except Exception:
            num_weeks = 2
        total += daily * 5 * num_weeks  # 5 days/week
    return round(total, 0)
