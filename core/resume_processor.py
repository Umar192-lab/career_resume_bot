# core/resume_processor.py
import re
import json
from typing import Tuple, Dict, List
from config.config import JOB_KEYWORDS_PATH, WEIGHTS
from core.llm_connector import ask_llm

# Load job keywords mapping (simple job title -> list of skills)
try:
    with open(JOB_KEYWORDS_PATH, "r", encoding="utf-8") as f:
        JOB_KEYWORDS = json.load(f)
except Exception:
    JOB_KEYWORDS = {}

# ---- Text extraction helpers (Streamlit will pass bytes; here we expect plain text) ----
def extract_text_from_uploaded(file) -> str:
    """
    file is a Streamlit uploaded file (BytesIO). We try a simple decode,
    otherwise we extract text from common types if needed.
    For robust extraction you can add pdfplumber / python-docx logic later.
    """
    data = file.read()
    # Try UTF-8 decode fallback
    for enc in ("utf-8", "latin-1", "utf-16"):
        try:
            text = data.decode(enc)
            if len(text.strip()) > 10:
                return text
        except Exception:
            pass
    # As a last resort, return empty string
    return ""

# ---- Heuristic checks ----
def has_contact_info(text: str) -> bool:
    email_re = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_re = r"(\+?\d{7,15})"
    return bool(re.search(email_re, text)) or bool(re.search(phone_re, text))

def detect_section_headers(text: str) -> List[str]:
    headers = []
    candidates = ["experience", "education", "skills", "projects", "summary", "certifications", "internship", "contact"]
    lower = text.lower()
    for c in candidates:
        if c in lower:
            headers.append(c)
    return headers

def estimate_formatting_score(text: str) -> float:
    """
    Basic heuristic for formatting: presence of bullet points or lines, and not a single dense paragraph.
    Returns 0..1
    """
    bullets = re.findall(r"(\n[-•*]\s+)", text)
    lines = text.count("\n")
    avg_line_len = (len(text) / max(1, lines))
    score = 0.0
    if bullets:
        score += 0.6
    if lines >= 6 and avg_line_len < 120:
        score += 0.4
    return min(1.0, score)

def keywords_match_score(text: str, job_title: str) -> Tuple[float, List[str]]:
    """
    Score based on overlap between JOB_KEYWORDS[job_title] and resume text.
    If job_title unknown, try fuzzy matching of keys or default empty list.
    """
    jt = job_title.lower().strip()
    # naive match: direct key or contains
    keywords = JOB_KEYWORDS.get(jt)
    if not keywords:
        # try find a close match
        for key in JOB_KEYWORDS.keys():
            if key in jt or jt in key:
                keywords = JOB_KEYWORDS[key]
                break
    if not keywords:
        keywords = []  # no keywords known

    text_lower = text.lower()
    matched = [kw for kw in keywords if kw.lower() in text_lower]
    score = len(matched) / max(1, len(keywords)) if keywords else 0.0
    return score, matched

def length_ok_score(text: str) -> float:
    words = len(text.split())
    # prefer 350-700 words for most resumes (1-2 pages)
    if 300 <= words <= 900:
        return 1.0
    if words < 300:
        return words / 300
    # if too long, penalize slowly
    return max(0.0, 1.0 - (words - 900) / 2000)

# ---- Combined ATS score ----
def compute_ats_score(text: str, job_title: str) -> Dict:
    c_contact = 1.0 if has_contact_info(text) else 0.0
    headers = detect_section_headers(text)
    c_headers = 1.0 if len(headers) >= 2 else len(headers) / 2.0
    c_len = length_ok_score(text)
    c_format = estimate_formatting_score(text)
    c_kw, matched = keywords_match_score(text, job_title)

    weights = WEIGHTS
    score = (
        weights["has_contact"] * c_contact +
        weights["has_section_headers"] * c_headers +
        weights["length_ok"] * c_len +
        weights["formatting"] * c_format +
        weights["keywords_match"] * c_kw
    )
    # normalize to 0-100
    percent = round(max(0.0, min(1.0, score)) * 100, 1)
    return {
        "score_percent": percent,
        "components": {
            "has_contact": c_contact,
            "section_headers": c_headers,
            "length_ok": round(c_len, 3),
            "formatting": round(c_format, 3),
            "keywords_match": round(c_kw, 3)
        },
        "matched_keywords": matched,
        "detected_headers": headers
    }

# ---- LLM-based review (adds qualitative suggestions) ----
def llm_resume_review(text: str, job_title: str, max_tokens: int = 400) -> str:
    prompt = (
        f"You are an expert resume reviewer and career coach.\n"
        f"Job title: {job_title}\n"
        f"Resume text:\n{text[:4000]}\n\n"  # limit prompt size
        "Provide:\n"
        "1) Short ATS-style summary (2 lines).\n"
        "2) Top 5 improvement suggestions prioritized.\n"
        "3) Short rewritten professional summary (2-3 lines) the candidate can use.\n"
        "Be concise and action-oriented."
    )
    return ask_llm(prompt)

