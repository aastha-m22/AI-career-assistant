"""
modules/resume_parser.py — PDF parsing and NLP-based resume extraction.
Uses PyMuPDF for text extraction and spaCy + regex for structured extraction.
"""
import re
import fitz  # PyMuPDF
import sys, ssl

# spaCy setup
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

from config import SKILLS_DB
from utils.text_cleaning import clean_text, extract_sections

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract raw text from an uploaded PDF using PyMuPDF."""
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(page.get_text("text") for page in doc)
    doc.close()
    return clean_text(text)

def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in SKILLS_DB:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill.title())
    return sorted(set(found))

def extract_education(text: str) -> list:
    lines = text.split("\n")
    education = []
    degree_re = re.compile(
        r"\b(B\.?Tech|B\.?E|B\.?Sc|B\.?A|M\.?Tech|M\.?Sc|M\.?A|MBA|Ph\.?D|Bachelor|Master|Associate|Diploma|B\.S\.|M\.S\.)\b",
        re.IGNORECASE
    )
    for line in lines:
        if degree_re.search(line) and len(line.strip()) > 5:
            education.append(line.strip())
    # spaCy ORG entities near education keywords
    if nlp:
        doc = nlp(text[:4000])
        edu_kws = {"university","college","institute","school","academy"}
        for ent in doc.ents:
            if ent.label_ == "ORG" and any(k in ent.text.lower() for k in edu_kws):
                education.append(ent.text.strip())
    seen = set()
    return [x for x in education if not (x.lower() in seen or seen.add(x.lower()))][:8]

def extract_experience(text: str) -> list:
    lines = text.split("\n")
    experience = []
    year_re = re.compile(r"\b(19|20)\d{2}\s*[-–—to]+\s*((19|20)\d{2}|present|current|now)\b", re.IGNORECASE)
    for i, line in enumerate(lines):
        line = line.strip()
        if year_re.search(line) and len(line) > 10:
            prev = lines[i-1].strip() if i > 0 else ""
            entry = f"{prev} | {line}" if prev else line
            experience.append(entry)
    if len(experience) < 2 and nlp:
        doc = nlp(text[:4000])
        for ent in doc.ents:
            if ent.label_ == "ORG" and len(ent.text) > 3:
                experience.append(ent.text.strip())
    seen = set()
    return [x for x in experience if not (x.lower() in seen or seen.add(x.lower()))][:10]

def extract_contact(text: str) -> dict:
    email = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    phone = re.findall(r"(\+?\d[\d\s\-().]{7,}\d)", text)
    name = ""
    if nlp:
        doc = nlp(text[:500])
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                break
    return {
        "name":  name or "Not detected",
        "email": email[0] if email else "Not found",
        "phone": phone[0].strip() if phone else "Not found",
    }

def parse_resume(text: str) -> dict:
    sections = extract_sections(text)
    return {
        "skills":     extract_skills(text),
        "education":  extract_education(text),
        "experience": extract_experience(text),
        "contact":    extract_contact(text),
        "sections":   sections,
        "word_count": len(text.split()),
    }
