import re
import os
from collections import Counter

# pip install PyPDF2
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

# -----------------------------
# Skills Keywords
# -----------------------------
SKILLS_KEYWORDS = {
    "python": ["python"],
    "sql": ["sql", "mysql", "postgres", "postgresql", "sqlite"],
    "powerbi": ["power bi", "powerbi"],
    "excel": ["excel", "vba"],
    "nlp": ["nlp", "natural language", "spacy", "nltk", "transformer", "bert"],
    "machine_learning": ["machine learning", "ml", "scikit-learn", "sklearn", "random forest", "xgboost"],
    "deep_learning": ["deep learning", "tensorflow", "keras", "pytorch"],
    "django": ["django", "drf", "rest framework"],
    "flask": ["flask", "fastapi"],
    "aws": ["aws", "azure", "gcp", "google cloud"],
    "cybersecurity": ["security", "penetration", "vulnerability", "cybersecurity", "cissp"],
    "ux": ["ux", "user experience", "ui/ux", "figma", "adobe xd"],
    "legal": ["law", "legal", "attorney", "paralegal"],
    "support": ["customer support", "support", "helpdesk"],
    "executive_assistant": ["assistant", "executive assistant", "admin"],
}

# -----------------------------
# Job Role Mapping
# -----------------------------
JOB_ROLE_MAP = {
    "Data Scientist": ["python", "machine_learning", "deep_learning", "nlp", "sql"],
    "Data Analyst": ["sql", "excel", "powerbi", "python"],
    "ML Engineer": ["python", "machine_learning", "deep_learning", "tensorflow", "pytorch"],
    "NLP Engineer": ["nlp", "python", "machine_learning"],
    "Backend Engineer": ["django", "flask", "python"],
    "DevOps Engineer": ["aws", "docker", "kubernetes"],
    "Cybersecurity Analyst": ["cybersecurity", "security"],
    "UX Designer": ["ux"],
    "Legal Advisor": ["legal"],
    "Customer Support Executive": ["support"],
    "Executive Assistant": ["executive_assistant"],
}

# -----------------------------
# Extract text from CV
# -----------------------------
def extract_cv_text(path):
    text = ""
    if not os.path.exists(path):
        return ""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf" and PdfReader:
            reader = PdfReader(path)
            pages = [p.extract_text() or "" for p in reader.pages]
            text = "\n".join(pages)
        else:
            # try reading as UTF-8 text or binary decode
            with open(path, "rb") as f:
                raw = f.read()
            try:
                text = raw.decode('utf-8')
            except:
                try:
                    text = raw.decode('latin-1')
                except:
                    text = ""
    except Exception:
        text = ""
    # normalize
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

# -----------------------------
# Score CV and get top jobs
# -----------------------------
def score_cv_and_get_jobs(text):
    if not text:
        return 0, []

    # normalize text
    text = text.lower()

    # Count keyword hits per skill
    skill_hits = Counter()
    for skill, variants in SKILLS_KEYWORDS.items():
        for v in variants:
            # match as whole word OR within sentences
            hits = len(re.findall(r'\b' + re.escape(v.lower()) + r'\b', text))
            skill_hits[skill] += hits

    # Base score: each hit adds points, cap at 100
    total_hits = sum(skill_hits.values())
    raw_score = min(100, total_hits * 8)

    # Boost if years of experience mentioned
    exp_match = re.search(r'(\d+)\+?\s+(years|yrs)\s+of', text)
    if exp_match:
        years = int(exp_match.group(1))
        raw_score = min(100, raw_score + min(20, years * 2))

    # Determine job relevance
    job_scores = []
    for job, job_skills in JOB_ROLE_MAP.items():
        score = 0
        for jk in job_skills:
            # check the skill keyword in hits
            if jk in skill_hits:
                score += skill_hits[jk]
            # check if literal keyword exists in CV text
            if re.search(r'\b' + re.escape(jk.replace("_"," ")) + r'\b', text):
                score += 1
        job_scores.append((job, score))

    # Sort jobs by relevance
    job_scores.sort(key=lambda x: x[1], reverse=True)
    top_jobs = [j for j, s in job_scores if s > 0][:5]
    if not top_jobs:
        top_jobs = [j for j, _ in job_scores[:5]]

    return raw_score, top_jobs
