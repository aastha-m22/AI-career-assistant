"""
app.py — AI Career Assistant: Streamlit Entry Point.

Design: Luxury dark editorial meets sleek fintech dashboard.
Deep obsidian backgrounds, gold/teal accent system, Freight Display typography.
Every element communicates precision and professional excellence.

Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import time

st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

from config import llm_config
from modules.resume_parser import extract_text_from_pdf, parse_resume
from modules.jd_matcher import full_match_analysis
from modules.llm_engine import generate_resume_feedback, generate_interview_questions, generate_study_roadmap
from modules.interview import get_quick_tips, generate_answer_feedback
from modules.roadmap import build_roadmap, get_resource_links, estimate_total_hours, TIMELINE_OPTIONS, LEVEL_OPTIONS

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Mulish:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Mulish', system-ui, sans-serif;
    background: #0c0c10;
    color: #e8e4d8;
}
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1300px; }

/* ── Sidebar ──────────────────────────────── */
[data-testid="stSidebar"] {
    background: #08080d;
    border-right: 1px solid #1a1a28;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem; }

.sidebar-logo {
    font-family: 'Libre Baskerville', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #e8d88a;
    border-bottom: 1px solid #1a1a28;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    letter-spacing: -0.3px;
}
.sidebar-logo span { color: #5eead4; }

.nav-item {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.65rem 0.9rem;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 0.3rem;
    font-size: 0.88rem;
    font-weight: 500;
    color: #7a7870;
    transition: all 0.15s;
    border: 1px solid transparent;
}
.nav-item.active {
    background: rgba(232,216,138,0.08);
    border-color: rgba(232,216,138,0.15);
    color: #e8d88a;
}
.nav-item:hover { background: rgba(255,255,255,0.04); color: #c8c4b8; }

/* ── Page header ──────────────────────────── */
.page-header {
    background: linear-gradient(135deg, #10101a 0%, #141422 100%);
    border: 1px solid #1e1e35;
    border-left: 4px solid #e8d88a;
    border-radius: 0 8px 8px 0;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
}
.page-title {
    font-family: 'Libre Baskerville', serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: #e8e4d8;
    margin: 0;
    letter-spacing: -0.3px;
}
.page-subtitle { color: #5a5850; font-size: 0.85rem; margin-top: 0.3rem; font-weight: 300; }

/* ── Cards ────────────────────────────────── */
.card {
    background: #10101a;
    border: 1px solid #1e1e35;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-gold   { border-top: 3px solid #e8d88a; }
.card-teal   { border-top: 3px solid #5eead4; }
.card-coral  { border-top: 3px solid #f87171; }
.card-violet { border-top: 3px solid #a78bfa; }

/* ── KPI row ──────────────────────────────── */
.kpi-row { display: flex; gap: 1rem; margin: 1.2rem 0; flex-wrap: wrap; }
.kpi-box {
    flex: 1; min-width: 120px;
    background: #0c0c14;
    border: 1px solid #1e1e35;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.kpi-val {
    font-family: 'Libre Baskerville', serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    color: #e8e4d8;
}
.kpi-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #3a3830;
    margin-top: 0.3rem;
}

/* ── Score ring ───────────────────────────── */
.score-ring {
    display: flex; flex-direction: column; align-items: center;
    padding: 2rem; border-radius: 8px;
    background: linear-gradient(135deg, #10101a, #0c0c14);
    border: 1px solid #1e1e35;
}
.score-big {
    font-family: 'Libre Baskerville', serif;
    font-size: 4.5rem; font-weight: 700; line-height: 1;
}
.score-label { font-family: 'DM Mono', monospace; font-size: 0.72rem;
    text-transform: uppercase; letter-spacing: 2px; color: #5a5850; margin-top: 0.5rem; }

/* ── Skill tags ───────────────────────────── */
.tag {
    display: inline-block;
    padding: 3px 10px; margin: 2px;
    border-radius: 4px; font-size: 0.78rem;
    font-family: 'DM Mono', monospace;
}
.tag-skill   { background: rgba(94,234,212,0.1); border: 1px solid rgba(94,234,212,0.25); color: #5eead4; }
.tag-missing { background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.25); color: #f87171; }
.tag-matched { background: rgba(232,216,138,0.1); border: 1px solid rgba(232,216,138,0.25); color: #e8d88a; }

/* ── Section rule ─────────────────────────── */
.section-rule {
    display: flex; align-items: center; gap: 1rem;
    margin: 1.8rem 0 1.2rem;
}
.section-rule-line { flex: 1; height: 1px; background: #1a1a28; }
.section-rule-label {
    font-family: 'DM Mono', monospace; font-size: 0.62rem;
    text-transform: uppercase; letter-spacing: 2.5px; color: #3a3830; white-space: nowrap;
}

/* ── Interview Q card ─────────────────────── */
.q-card {
    background: #0c0c14;
    border: 1px solid #1e1e35;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.q-number {
    font-family: 'DM Mono', monospace; font-size: 0.65rem;
    text-transform: uppercase; letter-spacing: 2px; color: #3a3830;
}
.q-text {
    font-family: 'Libre Baskerville', serif;
    font-size: 1.05rem; color: #e8e4d8; margin: 0.5rem 0;
    line-height: 1.5;
}
.q-why { font-size: 0.82rem; color: #5a5850; font-style: italic; }
.q-answer { font-size: 0.88rem; color: #c8c4b8; line-height: 1.6; margin-top: 0.5rem; }
.q-tip { font-size: 0.82rem; color: #e8d88a; margin-top: 0.4rem; }

/* ── Roadmap phase ────────────────────────── */
.phase-card {
    background: #0c0c14;
    border: 1px solid #1e1e35;
    border-radius: 8px;
    padding: 1.3rem 1.6rem;
    margin-bottom: 1rem;
    position: relative;
}
.phase-num {
    font-family: 'Libre Baskerville', serif;
    font-size: 3rem; font-weight: 700;
    color: rgba(232,216,138,0.08);
    position: absolute; top: 0.5rem; right: 1rem;
    line-height: 1;
}
.phase-title {
    font-family: 'Libre Baskerville', serif;
    font-size: 1.1rem; font-weight: 700; color: #e8e4d8;
}
.phase-weeks {
    font-family: 'DM Mono', monospace; font-size: 0.68rem;
    color: #e8d88a; text-transform: uppercase; letter-spacing: 1.5px;
    margin-top: 0.2rem;
}
.phase-focus { font-size: 0.88rem; color: #7a7870; margin-top: 0.5rem; line-height: 1.5; }
.resource-item {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.4rem 0; border-bottom: 1px solid #14141e;
    font-size: 0.85rem; color: #c8c4b8;
}
.res-type {
    font-family: 'DM Mono', monospace; font-size: 0.62rem;
    padding: 2px 7px; border-radius: 3px;
    background: rgba(94,234,212,0.08); color: #5eead4;
    text-transform: uppercase; white-space: nowrap;
}
.milestone-item { font-size: 0.85rem; color: #c8c4b8; padding: 0.25rem 0; }
.milestone-item::before { content: "✓ "; color: #5eead4; }

/* ── Progress bar ─────────────────────────── */
.prog-bar-track {
    background: #1a1a28; border-radius: 3px; height: 6px; overflow: hidden;
}
.prog-bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease; }

/* ── Feedback item ────────────────────────── */
.fb-item {
    padding: 0.65rem 0.9rem; border-radius: 6px; margin: 0.4rem 0;
    font-size: 0.9rem; line-height: 1.55; color: #c8c4b8;
}
.fb-strength { background: rgba(94,234,212,0.06); border-left: 3px solid #5eead4; }
.fb-improve  { background: rgba(232,216,138,0.06); border-left: 3px solid #e8d88a; }
.fb-missing  { background: rgba(248,113,113,0.06); border-left: 3px solid #f87171; }
.fb-ats      { background: rgba(167,139,250,0.06); border-left: 3px solid #a78bfa; }

/* ── Priority box ─────────────────────────── */
.priority-box {
    background: linear-gradient(135deg, rgba(232,216,138,0.08), rgba(232,216,138,0.04));
    border: 1px solid rgba(232,216,138,0.2);
    border-radius: 8px; padding: 1rem 1.3rem;
    font-size: 0.95rem; color: #e8d88a; line-height: 1.6;
}

/* ── Buttons ──────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #1e1e30, #252540) !important;
    color: #e8d88a !important;
    border: 1px solid rgba(232,216,138,0.3) !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.5rem !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #e8d88a, #d4c478) !important;
    color: #0c0c10 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(232,216,138,0.2) !important;
}

/* ── Inputs ───────────────────────────────── */
.stTextArea textarea, .stTextInput input {
    background: #0c0c14 !important;
    border: 1px solid #1e1e35 !important;
    border-radius: 6px !important;
    color: #c8c4b8 !important;
    font-family: 'Mulish', sans-serif !important;
    font-size: 0.92rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(232,216,138,0.4) !important;
    box-shadow: 0 0 0 2px rgba(232,216,138,0.06) !important;
}

/* ── Select/upload ────────────────────────── */
.stSelectbox > div > div { background: #0c0c14 !important; border: 1px solid #1e1e35 !important; }
[data-testid="stFileUploader"] { background: #0c0c14 !important; border: 1px dashed #1e1e35 !important; border-radius: 8px !important; }

/* ── Progress ─────────────────────────────── */
.stProgress > div > div > div { background: linear-gradient(90deg, #e8d88a, #5eead4) !important; }

/* ── Expander ─────────────────────────────── */
[data-testid="stExpander"] { border: 1px solid #1e1e35 !important; border-radius: 8px !important; background: #0c0c14 !important; }
details > summary { font-family: 'DM Mono', monospace !important; font-size: 0.7rem !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; color: #5a5850 !important; }

/* ── Provider pill ────────────────────────── */
.provider-pill {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 3px 10px; border-radius: 20px; margin: 2px;
    font-family: 'DM Mono', monospace; font-size: 0.65rem;
    font-weight: 500; letter-spacing: 1px; text-transform: uppercase;
}
.pill-groq   { background: rgba(94,234,212,0.1); border: 1px solid rgba(94,234,212,0.3); color: #5eead4; }
.pill-openai { background: rgba(167,139,250,0.1); border: 1px solid rgba(167,139,250,0.3); color: #a78bfa; }
.pill-none   { background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.3); color: #f87171; }

/* ── Footer ───────────────────────────────── */
.app-footer {
    border-top: 1px solid #1a1a28; margin-top: 4rem; padding-top: 1.2rem;
    text-align: center; font-family: 'DM Mono', monospace;
    font-size: 0.62rem; color: #2a2828; letter-spacing: 2px; text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "page": "Resume Analyzer",
    "resume_text": "",
    "parsed": None,
    "jd_text": "",
    "match_result": None,
    "feedback": None,
    "interview_qs": None,
    "roadmap": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">AI Career<br><span>Assistant ✦</span></div>', unsafe_allow_html=True)

    provider = llm_config.provider
    pill_cls = {"groq": "pill-groq", "openai": "pill-openai", "none": "pill-none"}[provider]
    pill_txt = {"groq": "⚡ Groq Active", "openai": "✦ OpenAI Active", "none": "⚠ No LLM Key"}[provider]
    st.markdown(f'<div class="provider-pill {pill_cls}">{pill_txt}</div>', unsafe_allow_html=True)
    st.write("")

    PAGES = [
        ("📄", "Resume Analyzer",    "Parse & extract your resume"),
        ("🔍", "JD Matcher",         "Match resume to job description"),
        ("🤖", "AI Feedback",        "Get LLM-powered improvement tips"),
        ("🎤", "Interview Prep",     "Practice with AI questions"),
        ("📅", "Study Roadmap",      "Build your learning plan"),
    ]

    for icon, name, desc in PAGES:
        active = "active" if st.session_state.page == name else ""
        if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
            st.session_state.page = name
            st.rerun()

    st.markdown("---")
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.62rem;color:#2a2828;text-transform:uppercase;letter-spacing:2px">Resume Status</div>', unsafe_allow_html=True)
    if st.session_state.parsed:
        p = st.session_state.parsed
        st.markdown(f'<div style="font-size:0.82rem;color:#5eead4;margin-top:0.3rem">✓ {p["word_count"]} words · {len(p["skills"])} skills</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:0.82rem;color:#3a3830;margin-top:0.3rem">No resume loaded</div>', unsafe_allow_html=True)

    if st.session_state.match_result:
        score = st.session_state.match_result["score"]
        color = "#5eead4" if score >= 60 else "#e8d88a" if score >= 40 else "#f87171"
        st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:0.62rem;color:#2a2828;text-transform:uppercase;letter-spacing:2px;margin-top:0.6rem">Match Score</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.82rem;color:{color};margin-top:0.2rem">✓ {score}% — {st.session_state.match_result["strength"]}</div>', unsafe_allow_html=True)

# ── Helper functions ──────────────────────────────────────────────────────────
def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">{icon} {title}</div>
        {f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ''}
    </div>""", unsafe_allow_html=True)

def section_rule(label):
    st.markdown(f"""<div class="section-rule">
        <div class="section-rule-line"></div>
        <div class="section-rule-label">{label}</div>
        <div class="section-rule-line"></div>
    </div>""", unsafe_allow_html=True)

def render_tags(items, tag_cls):
    if not items:
        st.markdown('<em style="color:#3a3830;font-size:0.85rem">None detected</em>', unsafe_allow_html=True)
        return
    html = "".join(f'<span class="tag {tag_cls}">{item}</span>' for item in items)
    st.markdown(html, unsafe_allow_html=True)

def feedback_item(text, css_cls):
    st.markdown(f'<div class="fb-item {css_cls}">• {text}</div>', unsafe_allow_html=True)

def score_color(score):
    if score >= 75: return "#5eead4"
    if score >= 50: return "#e8d88a"
    if score >= 30: return "#fb923c"
    return "#f87171"

# ════════════════════════════════════════════════════════════════════════════
# PAGE 1: RESUME ANALYZER
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Resume Analyzer":
    page_header("📄", "Resume Analyzer", "Upload your PDF resume to extract skills, education and experience")

    col_upload, col_preview = st.columns([1, 1], gap="large")

    with col_upload:
        uploaded = st.file_uploader("Upload PDF Resume", type=["pdf"], label_visibility="collapsed")

        if uploaded:
            with st.spinner("Extracting text from PDF..."):
                try:
                    text = extract_text_from_pdf(uploaded)
                    st.session_state.resume_text = text
                    with st.spinner("Running NLP extraction..."):
                        st.session_state.parsed = parse_resume(text)
                    st.success(f"✓ Resume parsed — {len(text.split())} words extracted")
                except Exception as e:
                    st.error(f"PDF parsing failed: {e}")

        # Sample resume input
        st.write("")
        if st.button("📝 Load Sample Resume", use_container_width=True):
            sample = """Alex Morgan  |  alex.morgan@email.com  |  +1-555-0123
Senior Software Engineer

SUMMARY
Results-driven software engineer with 6 years of experience building scalable backend systems
and ML pipelines. Passionate about Python, distributed systems, and LLM applications.

EXPERIENCE
Senior Software Engineer — TechCorp Inc.  |  2021 – Present
• Led migration of monolithic app to microservices using Docker and Kubernetes, reducing latency 35%
• Built ML pipeline for real-time recommendation system using Python, scikit-learn, and AWS SageMaker
• Mentored team of 4 junior engineers; conducted 50+ code reviews per quarter

Software Engineer — DataViz Solutions  |  2019 – 2021
• Developed REST APIs with Django and FastAPI serving 2M+ daily requests
• Implemented PostgreSQL schema optimizations reducing query time by 60%
• Built ETL pipelines using Apache Airflow processing 10GB+ daily data

EDUCATION
B.S. Computer Science — University of California, Berkeley  |  2019

SKILLS
Python, JavaScript, TypeScript, Django, FastAPI, React, PostgreSQL, MongoDB, Redis,
Docker, Kubernetes, AWS, Terraform, scikit-learn, PyTorch, pandas, numpy, Airflow,
Git, CI/CD, REST API, Agile, System Design, Machine Learning, NLP, MLOps

CERTIFICATIONS
AWS Certified Solutions Architect — Professional  |  2022
Google Cloud Professional Data Engineer  |  2023"""
            st.session_state.resume_text = sample
            st.session_state.parsed = parse_resume(sample)
            st.success("✓ Sample resume loaded")
            st.rerun()

    with col_preview:
        if st.session_state.resume_text:
            with st.expander("📃 View Extracted Text", expanded=False):
                st.text(st.session_state.resume_text[:2000] + ("..." if len(st.session_state.resume_text) > 2000 else ""))

    if st.session_state.parsed:
        p = st.session_state.parsed
        c = p["contact"]

        # Contact strip
        section_rule("CONTACT INFORMATION")
        st.markdown(f"""
        <div class="card" style="display:flex;gap:2rem;flex-wrap:wrap;align-items:center">
            <div><span style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:1.5px;color:#3a3830">Name</span><br>
            <span style="color:#e8e4d8;font-weight:600">{c['name']}</span></div>
            <div><span style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:1.5px;color:#3a3830">Email</span><br>
            <span style="color:#c8c4b8">{c['email']}</span></div>
            <div><span style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:1.5px;color:#3a3830">Phone</span><br>
            <span style="color:#c8c4b8">{c['phone']}</span></div>
            <div><span style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:1.5px;color:#3a3830">Word Count</span><br>
            <span style="color:#e8d88a;font-family:'DM Mono',monospace">{p['word_count']:,}</span></div>
        </div>""", unsafe_allow_html=True)

        # Three columns
        section_rule("EXTRACTED DATA")
        c1, c2, c3 = st.columns(3, gap="medium")

        with c1:
            st.markdown('<div class="card card-teal">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#5eead4;margin-bottom:0.7rem">🛠 Skills ({len(p["skills"])})</div>', unsafe_allow_html=True)
            render_tags(p["skills"], "tag-skill")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
            st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#e8d88a;margin-bottom:0.7rem">🎓 Education</div>', unsafe_allow_html=True)
            if p["education"]:
                for edu in p["education"]:
                    st.markdown(f'<div style="font-size:0.85rem;color:#c8c4b8;padding:0.3rem 0;border-bottom:1px solid #1a1a28">• {edu}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<em style="color:#3a3830;font-size:0.85rem">None detected</em>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="card card-violet">', unsafe_allow_html=True)
            st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#a78bfa;margin-bottom:0.7rem">💼 Experience</div>', unsafe_allow_html=True)
            if p["experience"]:
                for exp in p["experience"]:
                    st.markdown(f'<div style="font-size:0.82rem;color:#c8c4b8;padding:0.3rem 0;border-bottom:1px solid #1a1a28">• {exp}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<em style="color:#3a3830;font-size:0.85rem">None detected</em>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Navigate prompt
        st.info("✓ Resume loaded. Go to **JD Matcher** to score against a job description, or **AI Feedback** for improvement tips.")
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:3rem">
            <div style="font-size:3rem;margin-bottom:1rem">📄</div>
            <div style="font-family:'Libre Baskerville',serif;font-size:1.2rem;color:#5a5850">Upload a PDF resume or load the sample to begin</div>
        </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 2: JD MATCHER
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "JD Matcher":
    page_header("🔍", "JD Matcher", "Paste a job description to calculate your match score and keyword gaps")

    if not st.session_state.resume_text:
        st.warning("Please upload a resume first on the **Resume Analyzer** page.")
    else:
        jd_input = st.text_area("Paste Job Description", value=st.session_state.jd_text,
            height=260, placeholder="Paste the full job description here...")

        # Sample JD
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📋 Load Sample JD", use_container_width=True):
                st.session_state.jd_text = """Senior Machine Learning Engineer

We are looking for a Senior ML Engineer to join our AI Platform team.

Requirements:
• 5+ years of experience in machine learning and Python development
• Strong expertise in PyTorch, TensorFlow, and scikit-learn
• Experience with MLOps: model deployment, monitoring, and CI/CD pipelines
• Proficiency in cloud platforms (AWS or GCP), Docker, and Kubernetes
• Experience with NLP and LLM applications, RAG pipelines, and prompt engineering
• Knowledge of distributed computing: Spark, Kafka, or Airflow
• Strong SQL and NoSQL database skills (PostgreSQL, MongoDB, Redis)
• Experience with REST API development using FastAPI or Django
• Familiarity with vector databases (Pinecone, ChromaDB, Weaviate)
• Excellent communication and cross-functional collaboration skills

Nice to have:
• Publications or contributions to ML research
• Experience with fine-tuning large language models
• Knowledge of system design for high-throughput ML systems

Responsibilities:
• Design and build end-to-end ML pipelines from data ingestion to model serving
• Collaborate with data scientists to productionize research models
• Optimize model performance, latency, and cost at scale
• Implement A/B testing frameworks for model evaluation
• Mentor junior engineers and contribute to team best practices"""
                st.rerun()
        with col_btn2:
            analyze_btn = st.button("🔍 Analyze Match", use_container_width=True)

        if analyze_btn and jd_input.strip():
            st.session_state.jd_text = jd_input
            with st.spinner("Computing TF-IDF similarity and skill gaps..."):
                result = full_match_analysis(
                    st.session_state.resume_text,
                    jd_input,
                    st.session_state.parsed["skills"] if st.session_state.parsed else [],
                )
                st.session_state.match_result = result

        if st.session_state.match_result:
            r = st.session_state.match_result
            sc = score_color(r["score"])

            section_rule("MATCH RESULTS")
            left, right = st.columns([1, 2], gap="large")

            with left:
                st.markdown(f"""
                <div class="score-ring">
                    <div class="score-big" style="color:{sc}">{r['score']}%</div>
                    <div class="score-label">Match Score</div>
                    <div style="margin-top:0.8rem;font-family:'DM Mono',monospace;font-size:0.82rem;color:{sc};font-weight:600">{r['strength']}</div>
                    <div style="margin-top:1rem;width:100%">
                        <div class="prog-bar-track"><div class="prog-bar-fill" style="width:{min(r['score'],100)}%;background:{sc}"></div></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            with right:
                sg = r["skill_gap"]
                st.markdown(f"""
                <div class="kpi-row">
                    <div class="kpi-box">
                        <div class="kpi-val" style="color:{sc}">{r['score']}%</div>
                        <div class="kpi-lbl">Overall</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-val" style="color:#5eead4">{len(sg['matched'])}</div>
                        <div class="kpi-lbl">Skills Matched</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-val" style="color:#f87171">{len(sg['missing'])}</div>
                        <div class="kpi-lbl">Skills Missing</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-val" style="color:#a78bfa">{len(r['matching_kw'])}</div>
                        <div class="kpi-lbl">KW Matches</div>
                    </div>
                </div>""", unsafe_allow_html=True)

                if sg["matched"]:
                    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.62rem;text-transform:uppercase;letter-spacing:2px;color:#3a3830;margin-bottom:0.4rem">✅ Matching Skills</div>', unsafe_allow_html=True)
                    render_tags(sg["matched"], "tag-matched")
                if sg["missing"]:
                    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.62rem;text-transform:uppercase;letter-spacing:2px;color:#3a3830;margin:0.6rem 0 0.4rem">❌ Missing Skills</div>', unsafe_allow_html=True)
                    render_tags(sg["missing"], "tag-missing")

            # Keyword analysis
            section_rule("KEYWORD ANALYSIS")
            kw1, kw2 = st.columns(2, gap="medium")
            with kw1:
                st.markdown('<div class="card card-teal">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#5eead4;margin-bottom:0.7rem">🔑 Matched Keywords</div>', unsafe_allow_html=True)
                render_tags(r["matching_kw"][:15], "tag-matched")
                st.markdown('</div>', unsafe_allow_html=True)
            with kw2:
                st.markdown('<div class="card card-coral">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#f87171;margin-bottom:0.7rem">⚠ Missing Keywords</div>', unsafe_allow_html=True)
                render_tags(r["missing_kw"][:15], "tag-missing")
                st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 3: AI FEEDBACK
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "AI Feedback":
    page_header("🤖", "AI Feedback", "LLM-powered analysis of your resume against the job description")

    if not st.session_state.resume_text:
        st.warning("Please upload a resume first.")
    elif not st.session_state.jd_text:
        st.warning("Please paste a job description on the **JD Matcher** page first.")
    elif llm_config.provider == "none":
        st.error("No API key found. Add GROQ_API_KEY or OPENAI_API_KEY to your .env file.")
    else:
        if st.button("✨ Generate AI Feedback", use_container_width=False):
            with st.spinner(f"Consulting AI ({llm_config.provider.title()})..."):
                try:
                    fb = generate_resume_feedback(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        st.session_state.parsed or {},
                        st.session_state.match_result["score"] if st.session_state.match_result else 0,
                        st.session_state.match_result["missing_kw"] if st.session_state.match_result else [],
                    )
                    st.session_state.feedback = fb
                except Exception as e:
                    st.error(f"LLM call failed: {e}")

        if st.session_state.feedback:
            fb = st.session_state.feedback

            # Overall assessment
            section_rule("OVERALL ASSESSMENT")
            st.markdown(f"""
            <div class="priority-box">
                <div style="font-family:'Libre Baskerville',serif;font-size:1rem;line-height:1.7">
                    {fb.get('overall_assessment','')}
                </div>
            </div>""", unsafe_allow_html=True)

            if fb.get("priority_action"):
                st.markdown(f"""
                <div style="margin-top:0.8rem;background:rgba(94,234,212,0.06);
                    border:1px solid rgba(94,234,212,0.2);border-radius:6px;
                    padding:0.8rem 1.2rem;font-size:0.9rem;color:#5eead4;line-height:1.6">
                    🎯 <strong>Priority Action:</strong> {fb['priority_action']}
                </div>""", unsafe_allow_html=True)

            # Four columns of feedback
            section_rule("DETAILED FEEDBACK")
            c1, c2 = st.columns(2, gap="medium")

            with c1:
                st.markdown('<div class="card card-teal">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#5eead4;margin-bottom:0.7rem">✅ Strengths</div>', unsafe_allow_html=True)
                for item in fb.get("strengths", []):
                    feedback_item(item, "fb-strength")
                st.markdown('</div>', unsafe_allow_html=True)

                st.write("")
                st.markdown('<div class="card card-violet">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#a78bfa;margin-bottom:0.7rem">📋 ATS Optimization</div>', unsafe_allow_html=True)
                for item in fb.get("ats_tips", []):
                    feedback_item(item, "fb-ats")
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#e8d88a;margin-bottom:0.7rem">💡 Improvements</div>', unsafe_allow_html=True)
                for item in fb.get("improvements", []):
                    feedback_item(item, "fb-improve")
                st.markdown('</div>', unsafe_allow_html=True)

                st.write("")
                st.markdown('<div class="card card-coral">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#f87171;margin-bottom:0.7rem">🎯 Missing Skills</div>', unsafe_allow_html=True)
                for item in fb.get("missing_skills", []):
                    feedback_item(item, "fb-missing")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:2.5rem">
                <div style="font-size:2.5rem;margin-bottom:0.8rem">🤖</div>
                <div style="font-family:'Libre Baskerville',serif;font-size:1.1rem;color:#5a5850">
                    Click "Generate AI Feedback" to get personalized improvement recommendations
                </div>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 4: INTERVIEW PREP
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Interview Prep":
    page_header("🎤", "Interview Prep", "AI-generated questions tailored to your resume and target role")

    if not st.session_state.resume_text:
        st.warning("Please upload a resume first.")
    elif llm_config.provider == "none":
        st.error("No API key found. Add GROQ_API_KEY or OPENAI_API_KEY to your .env file.")
    else:
        jd_for_interview = st.text_area(
            "Job Description (for tailored questions)",
            value=st.session_state.jd_text,
            height=120,
            placeholder="Paste job description for more targeted questions..."
        )

        gen_btn = st.button("🎤 Generate Interview Questions", use_container_width=False)

        if gen_btn:
            with st.spinner("Generating role-specific interview questions..."):
                try:
                    qs = generate_interview_questions(
                        st.session_state.resume_text,
                        jd_for_interview or "Software Engineering position"
                    )
                    st.session_state.interview_qs = qs
                except Exception as e:
                    st.error(f"Failed: {e}")

        # General tips always visible
        section_rule("INTERVIEW TIPS")
        tips = get_quick_tips([])
        tip_cols = st.columns(2)
        for i, tip in enumerate(tips):
            with tip_cols[i % 2]:
                st.markdown(f'<div style="font-size:0.85rem;color:#c8c4b8;padding:0.4rem 0;border-bottom:1px solid #1a1a28">💡 {tip}</div>', unsafe_allow_html=True)

        if st.session_state.interview_qs:
            qs = st.session_state.interview_qs
            CATEGORIES = [
                ("behavioral",  "🧠", "Behavioral",  "#818cf8"),
                ("technical",   "⚙️",  "Technical",   "#5eead4"),
                ("situational", "🎯", "Situational", "#fb923c"),
            ]
            for cat_key, icon, label, color in CATEGORIES:
                q_list = qs.get(cat_key, [])
                if not q_list: continue

                section_rule(f"{icon} {label.upper()} QUESTIONS ({len(q_list)})")
                for i, q in enumerate(q_list, 1):
                    with st.expander(f"Q{i}: {q.get('question','')[:80]}...", expanded=(i==1 and cat_key=="behavioral")):
                        st.markdown(f'<div class="q-why">Why asked: {q.get("why_asked","")}</div>', unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style="background:rgba(94,234,212,0.05);border:1px solid rgba(94,234,212,0.15);
                            border-radius:6px;padding:0.8rem 1rem;margin:0.6rem 0">
                            <div style="font-family:'DM Mono',monospace;font-size:0.62rem;text-transform:uppercase;
                                letter-spacing:1.5px;color:#5eead4;margin-bottom:0.4rem">Sample Answer</div>
                            <div class="q-answer">{q.get('sample_answer','')}</div>
                        </div>""", unsafe_allow_html=True)
                        if q.get("tip"):
                            st.markdown(f'<div class="q-tip">💡 Tip: {q["tip"]}</div>', unsafe_allow_html=True)

                        # Practice answer box
                        st.write("")
                        user_ans = st.text_area(f"Your answer (Q{i})", key=f"ans_{cat_key}_{i}", height=100, placeholder="Type your practice answer here...")
                        if st.button(f"📊 Evaluate My Answer", key=f"eval_{cat_key}_{i}"):
                            if user_ans.strip():
                                with st.spinner("Evaluating..."):
                                    eval_result = generate_answer_feedback(q.get("question",""), user_ans, jd_for_interview[:300])
                                score = eval_result.get("score", 0)
                                sc_color = "#5eead4" if score >= 7 else "#e8d88a" if score >= 5 else "#f87171"
                                st.markdown(f"""
                                <div class="card" style="margin-top:0.5rem">
                                    <div style="display:flex;gap:1rem;align-items:center;margin-bottom:0.8rem">
                                        <div style="font-family:'Libre Baskerville',serif;font-size:2rem;font-weight:700;color:{sc_color}">{score}/10</div>
                                        <div style="color:#c8c4b8;font-size:0.9rem">{eval_result.get('verdict','')}</div>
                                    </div>
                                    <div style="font-family:'DM Mono',monospace;font-size:0.62rem;text-transform:uppercase;letter-spacing:1.5px;color:#5eead4;margin-bottom:0.4rem">Enhanced Answer</div>
                                    <div style="font-size:0.88rem;color:#e8e4d8;line-height:1.6;background:rgba(94,234,212,0.04);padding:0.8rem;border-radius:6px">{eval_result.get('enhanced_answer','')}</div>
                                </div>""", unsafe_allow_html=True)
                            else:
                                st.warning("Please type your answer first.")
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:2.5rem;margin-top:1rem">
                <div style="font-size:2.5rem;margin-bottom:0.8rem">🎤</div>
                <div style="font-family:'Libre Baskerville',serif;font-size:1.1rem;color:#5a5850">
                    Click "Generate Interview Questions" for AI-tailored practice questions
                </div>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 5: STUDY ROADMAP
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Study Roadmap":
    page_header("📅", "Study Roadmap", "AI-generated personalized learning plan for your skill gaps")

    if llm_config.provider == "none":
        st.error("No API key found. Add GROQ_API_KEY or OPENAI_API_KEY to your .env file.")
    else:
        # Config row
        cfg1, cfg2, cfg3 = st.columns(3)
        with cfg1:
            timeline_choice = st.selectbox("Timeline", list(TIMELINE_OPTIONS.keys()), index=1)
        with cfg2:
            level_choice = st.selectbox("Current Level", LEVEL_OPTIONS, index=1)
        with cfg3:
            custom_skills_input = st.text_input("Additional skills to learn", placeholder="e.g. kubernetes, kafka")

        # Detect skills to learn
        auto_missing = []
        if st.session_state.match_result:
            auto_missing = st.session_state.match_result["skill_gap"]["missing"][:8]
        if st.session_state.feedback:
            auto_missing += st.session_state.feedback.get("missing_skills", [])[:4]

        custom_skills = [s.strip() for s in custom_skills_input.split(",") if s.strip()]
        all_missing = list(dict.fromkeys(auto_missing + custom_skills))[:12]

        if all_missing:
            st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#3a3830;margin-bottom:0.4rem">Skills to Learn:</div>', unsafe_allow_html=True)
            render_tags(all_missing, "tag-missing")
        else:
            st.info("No skill gaps detected yet. Run JD Matcher and AI Feedback first, or add skills above.")

        gen_roadmap_btn = st.button("🗺 Generate Study Roadmap", use_container_width=False)

        if gen_roadmap_btn:
            if not all_missing:
                st.warning("No skills to build a roadmap for. Add custom skills above.")
            else:
                with st.spinner("Building your personalized learning roadmap..."):
                    try:
                        roadmap = build_roadmap(all_missing, timeline_choice, level_choice)
                        st.session_state.roadmap = roadmap
                    except Exception as e:
                        st.error(f"Roadmap generation failed: {e}")

        if st.session_state.roadmap:
            rm = st.session_state.roadmap
            phases = rm.get("phases", [])
            total_h = estimate_total_hours(phases)

            # Summary header
            section_rule("ROADMAP OVERVIEW")
            st.markdown(f"""
            <div class="priority-box">
                <div style="font-family:'Libre Baskerville',serif;font-size:1rem;line-height:1.7">{rm.get('summary','')}</div>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="kpi-row" style="margin-top:1rem">
                <div class="kpi-box">
                    <div class="kpi-val" style="color:#e8d88a">{len(phases)}</div>
                    <div class="kpi-lbl">Phases</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-val" style="color:#5eead4">{len(all_missing)}</div>
                    <div class="kpi-lbl">Skills</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-val" style="color:#a78bfa">{int(total_h)}</div>
                    <div class="kpi-lbl">Est. Hours</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-val" style="color:#fb923c">{timeline_choice.split()[0]}</div>
                    <div class="kpi-lbl">Timeline</div>
                </div>
            </div>""", unsafe_allow_html=True)

            if rm.get("weekly_schedule"):
                st.markdown(f'<div style="font-size:0.85rem;color:#7a7870;margin:0.5rem 0;font-style:italic">📆 {rm["weekly_schedule"]}</div>', unsafe_allow_html=True)

            # Phases
            section_rule("LEARNING PHASES")
            PHASE_COLORS = ["#e8d88a", "#5eead4", "#a78bfa", "#fb923c", "#f472b6"]
            for i, phase in enumerate(phases):
                color = PHASE_COLORS[i % len(PHASE_COLORS)]
                with st.expander(f"Phase {phase.get('phase',i+1)}: {phase.get('title','')}  ·  Weeks {phase.get('weeks','')}", expanded=(i==0)):
                    p_c1, p_c2 = st.columns([3, 2], gap="medium")
                    with p_c1:
                        st.markdown(f"""
                        <div class="phase-card">
                            <div class="phase-num">{phase.get('phase', i+1)}</div>
                            <div class="phase-title" style="color:{color}">{phase.get('title','')}</div>
                            <div class="phase-weeks">Weeks {phase.get('weeks','')}</div>
                            <div class="phase-focus">{phase.get('focus','')}</div>
                            <div style="margin-top:0.8rem">
                                <div style="font-family:'DM Mono',monospace;font-size:0.62rem;text-transform:uppercase;letter-spacing:1.5px;color:#3a3830;margin-bottom:0.4rem">Skills</div>
                        """, unsafe_allow_html=True)
                        render_tags(phase.get("skills", []), "tag-skill")
                        st.markdown(f"""
                            <div style="margin-top:0.6rem;font-family:'DM Mono',monospace;font-size:0.72rem;color:#3a3830">⏱ {phase.get('daily_hours',1.5)} hrs/day</div>
                        </div></div>""", unsafe_allow_html=True)

                    with p_c2:
                        # Resources
                        st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.62rem;text-transform:uppercase;letter-spacing:1.5px;color:#3a3830;margin-bottom:0.5rem">Resources</div>', unsafe_allow_html=True)
                        for res in phase.get("resources", [])[:5]:
                            if isinstance(res, dict):
                                st.markdown(f"""
                                <div class="resource-item">
                                    <span class="res-type">{res.get('type','Course')[:8]}</span>
                                    <span>{res.get('name','')} — <em style="color:#5a5850">{res.get('url_hint','')}</em></span>
                                    {f'<span style="color:#3a3830;font-size:0.78rem;margin-left:auto">{res.get("time","")}</span>' if res.get("time") else ''}
                                </div>""", unsafe_allow_html=True)

                        # Milestones
                        if phase.get("milestones"):
                            st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.62rem;text-transform:uppercase;letter-spacing:1.5px;color:#3a3830;margin:0.8rem 0 0.4rem">Milestones</div>', unsafe_allow_html=True)
                            for m in phase["milestones"]:
                                st.markdown(f'<div class="milestone-item">{m}</div>', unsafe_allow_html=True)

            # Tips
            if rm.get("tips"):
                section_rule("PRO TIPS")
                for tip in rm["tips"]:
                    st.markdown(f'<div style="font-size:0.88rem;color:#c8c4b8;padding:0.4rem 0;border-bottom:1px solid #1a1a28">💡 {tip}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:2.5rem;margin-top:1rem">
                <div style="font-size:2.5rem;margin-bottom:0.8rem">📅</div>
                <div style="font-family:'Libre Baskerville',serif;font-size:1.1rem;color:#5a5850">
                    Click "Generate Study Roadmap" to get your personalized learning plan
                </div>
            </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    AI Career Assistant · Resume Analysis · JD Matching · Interview Prep · Study Roadmap
</div>""", unsafe_allow_html=True)
