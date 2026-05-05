"""utils/text_cleaning.py"""
import re

def clean_text(text: str) -> str:
    if not isinstance(text, str): return ""
    text = text.replace("\r\n","\n").replace("\r","\n")
    for old,new in [("\u2018","'"),("\u2019","'"),("\u201c","\""),("\u201d","\""),
                    ("\u2013","-"),("\u2014","--"),("\u2022","*")]:
        text = text.replace(old,new)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def extract_sections(text: str) -> dict:
    section_patterns = {
        "experience":  r"(experience|work history|employment|career)",
        "education":   r"(education|academic|qualification|degree|university|college)",
        "skills":      r"(skills|technical skills|competencies|technologies|expertise)",
        "projects":    r"(projects|portfolio|personal projects|key projects)",
        "certifications": r"(certif|credential|award|achievement|license)",
        "summary":     r"(summary|objective|profile|about|overview)",
    }
    lines = text.split("\n")
    sections = {"_header": []}
    current_section = "_header"
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        matched = False
        for sec_name, pattern in section_patterns.items():
            if re.search(pattern, stripped, re.IGNORECASE) and len(stripped) < 60:
                current_section = sec_name
                matched = True
                break
        if not matched:
            sections.setdefault(current_section, []).append(stripped)
    return {k: "\n".join(v) for k, v in sections.items() if v}

def truncate_for_llm(text: str, max_words: int = 2500) -> tuple:
    words = text.split()
    if len(words) <= max_words: return text, False
    truncated = " ".join(words[:max_words])
    last_period = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))
    if last_period > len(truncated) * 0.7:
        truncated = truncated[:last_period+1]
    return truncated, True

def count_words(text: str) -> int:
    return len(text.split())
