# AI Career Assistant

> A full-stack AI-powered career platform combining **NLP extraction**, **TF-IDF matching**, and **LLM-powered coaching** across five integrated modules — all in a single Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit)
![spaCy](https://img.shields.io/badge/spaCy-3.7+-09a3d5)
![LLM](https://img.shields.io/badge/LLM-Groq%20%2F%20OpenAI-orange)

---

## Features

| Module | Capability |
|---|---|
|  **Resume Analyzer** | PDF parsing (PyMuPDF), NLP extraction (spaCy + regex): skills, education, experience, contact |
| **JD Matcher** | TF-IDF + cosine similarity match score, skill gap analysis, keyword overlap |
|  **AI Feedback** | LLM-powered strengths, improvement suggestions, ATS tips, priority action |
|  **Interview Prep** | AI-generated behavioral/technical/situational Q&A, answer evaluator with STAR scoring |
|  **Study Roadmap** | Phased learning plan with resources, milestones, timeline, and daily hour estimates |

---

##  Project Structure

```
ai-career-assistant/
│
├── app.py                    # Streamlit UI — all 5 pages
├── config.py                 # LLM config, skills DB, resource templates
├── modules/
│   ├── resume_parser.py      # PDF extraction + NLP parsing
│   ├── jd_matcher.py         # TF-IDF cosine similarity + skill gap
│   ├── llm_engine.py         # Unified LLM client (Groq/OpenAI)
│   ├── interview.py          # Question generation + answer evaluation
│   └── roadmap.py            # Study roadmap builder
├── utils/
│   └── text_cleaning.py      # Text normalization, section extraction
├── assets/
├── requirements.txt
├── .env.example
└── README.md
```

---

##  Quick Start

### 1. Clone & setup
```bash
git clone https://github.com/yourname/ai-career-assistant.git
cd ai-career-assistant
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure API key
```bash
cp .env.example .env
# Edit .env — add your GROQ_API_KEY (free) or OPENAI_API_KEY
```

>  **Groq is free** — get a key at [console.groq.com](https://console.groq.com). Resume parsing and JD matching work without any API key.

### 4. Run
```bash
streamlit run app.py
```

---

##  Environment Variables

```env
GROQ_API_KEY=gsk_...      # Groq (recommended — free)
OPENAI_API_KEY=sk-...     # OR OpenAI (paid)
```

The app checks `GROQ_API_KEY` first.

---

##  How It Works

### Resume Parser
1. PyMuPDF extracts raw text from PDF
2. Regex + spaCy NER identify education (degree patterns) and experience (year ranges + ORG entities)
3. 70+ skill keywords matched against a curated database
4. Contact info extracted via regex

### JD Matcher
1. Both texts vectorized with `TfidfVectorizer(ngram_range=(1,2), max_features=10000)`
2. Cosine similarity computed → match percentage
3. Skill gap: resume skills vs. JD skills from the same 70+ skill database
4. Keyword gap: top TF-IDF terms from JD absent in resume

### LLM Integration
- Single `call_llm(system, user)` function in `llm_engine.py`
- Groq uses OpenAI SDK with `base_url="https://api.groq.com/openai/v1"`
- All LLM outputs request structured JSON with safe fallback parsers

### Answer Evaluator
- STAR method scoring (Situation/Task/Action/Result)
- 1-10 score derived from LLM assessment
- Enhanced answer suggestion generated alongside feedback

---
##  Demo

###  Dashboard Upload & Analysis
![Dashboard Upload](assets1/dashborad.png)


##  Tech Stack

| Layer | Library |
|---|---|
| UI | Streamlit |
| PDF Parsing | PyMuPDF (fitz) |
| NLP | spaCy en_core_web_sm |
| ML Similarity | scikit-learn TF-IDF + cosine |
| LLM | OpenAI SDK (Groq + OpenAI) |
| Config | python-dotenv |

---

##  License

MIT © 2024
