"""
config.py — Centralized configuration for AI Career Assistant.
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
load_dotenv()

@dataclass
class LLMConfig:
    groq_api_key: str   = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    groq_model: str     = "llama3-8b-8192"
    openai_model: str   = "gpt-3.5-turbo"
    temperature: float  = 0.4
    max_tokens: int     = 1800

    @property
    def provider(self):
        if self.groq_api_key:   return "groq"
        if self.openai_api_key: return "openai"
        return "none"

    @property
    def active_key(self):
        return self.groq_api_key if self.provider == "groq" else self.openai_api_key

    @property
    def model(self):
        return self.groq_model if self.provider == "groq" else self.openai_model

    @property
    def base_url(self):
        return "https://api.groq.com/openai/v1" if self.provider == "groq" else None

SKILLS_DB = [
    "python","java","javascript","typescript","c++","c#","ruby","go","rust","scala","r",
    "kotlin","swift","php","bash","sql","html","css","matlab",
    "react","angular","vue","django","flask","fastapi","spring","rails","nextjs","nodejs",
    "express","tensorflow","pytorch","keras","scikit-learn","pandas","numpy","opencv",
    "langchain","transformers","aws","azure","gcp","docker","kubernetes","terraform",
    "ansible","jenkins","git","github actions","ci/cd","linux","nginx",
    "mysql","postgresql","mongodb","redis","elasticsearch","dynamodb","sqlite","firebase",
    "snowflake","bigquery","cassandra","machine learning","deep learning","nlp",
    "computer vision","data analysis","data engineering","etl","spark","hadoop","kafka",
    "airflow","tableau","power bi","statistics","a/b testing","feature engineering",
    "model deployment","agile","scrum","rest api","graphql","microservices","oop","tdd",
    "devops","mlops","system design","rag","llm","prompt engineering","openai",
]

RESOURCE_TEMPLATES = {
    "python": ["Python.org Docs","Real Python","Automate the Boring Stuff","LeetCode Python"],
    "machine learning": ["fast.ai","Andrew Ng Coursera","Hands-On ML (Geron)","Kaggle"],
    "deep learning": ["fast.ai Part 2","Deep Learning Specialization","PyTorch Docs"],
    "data analysis": ["Kaggle Courses","DataCamp","Wes McKinney Pandas Book"],
    "aws": ["AWS Free Tier","A Cloud Guru","AWS Skill Builder"],
    "docker": ["Docker Docs","Play with Docker","Docker & Kubernetes (Udemy)"],
    "react": ["React Docs","Scrimba React Course","Epic React"],
    "sql": ["SQLZoo","Mode Analytics SQL","LeetCode Database"],
    "nlp": ["Hugging Face Course","Stanford CS224N","spaCy Course"],
    "default": ["Coursera","Udemy","YouTube Tutorials","Official Documentation"],
}

llm_config = LLMConfig()
