# core/resume_processor.py
import re
import json
from typing import Tuple, Dict, List, Optional, IO
from config.config import JOB_KEYWORDS_PATH, WEIGHTS
from core.llm_connector import ask_llm

# Optional heavy libs imported lazily inside functions
try:
    with open(JOB_KEYWORDS_PATH, "r", encoding="utf-8") as f:
        JOB_KEYWORDS = json.load(f)
except Exception:
    JOB_KEYWORDS = {}

# -------- Text extraction --------
def _extract_txt(file_obj: IO[bytes]) -> str:
    data = file_obj.read()
    for enc in ("utf-8", "latin-1", "utf-16"):
        try:
            t = data.decode(enc)
            if len(t.strip()) > 10:
                return t
        except Exception:
            pass
    return ""

def _extract_pdf(file_obj: IO[bytes]) -> str:
    import io
    import pdfplumber
    text_parts = []
    file_obj.seek(0)
    with pdfplumber.open(io.BytesIO(file_obj.read())) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t:
                text_parts.append(t)
    return "\n".join(text_parts).strip()

def _extract_docx(file_obj: IO[bytes]) -> str:
    import io
    from docx import Document
    file_obj.seek(0)
    doc = Document(io.BytesIO(file_obj.read()))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(parts).strip()

def extract_text_from_uploaded(file) -> str:
    """
    Accepts a Streamlit UploadedFile (has .name and .read()).
    Supports .txt, .pdf, .docx
    """
    name = (file.name or "").lower()
    if name.endswith(".pdf"):
        try:
            return _extract_pdf(file)
        except Exception:
            file.seek(0)
            return _extract_txt(file)
    if name.endswith(".docx"):
        try:
            return _extract_docx(file)
        except Exception:
            file.seek(0)
            return _extract_txt(file)
    # default .txt or unknown — try plain text
    return _extract_txt(file)

# -------- Heuristic checks --------
def has_contact_info(text: str) -> bool:
    email_re = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_re = r"(\+?\d[\d\s\-]{6,15})"  # a bit more permissive
    return bool(re.search(email_re, text)) or bool(re.search(phone_re, text))

def detect_section_headers(text: str) -> List[str]:
    headers = []
    candidates = [
        "experience", "work experience", "education", "skills", "projects",
        "summary", "objective", "certifications", "internship", "contact", "achievements"
    ]
    lower = text.lower()
    for c in candidates:
        if c in lower:
            headers.append(c)
    # de-duplicate while preserving order
    seen = set()
    uniq = []
    for h in headers:
        if h not in seen:
            uniq.append(h); seen.add(h)
    return uniq

def estimate_formatting_score(text: str) -> float:
    bullets = re.findall(r"(\n[-•*]\s+)", text)
    lines = max(1, text.count("\n"))
    avg_line_len = len(text) / lines
    score = 0.0
    if bullets:
        score += 0.6
    if lines >= 8 and avg_line_len < 120:
        score += 0.4
    return min(1.0, score)

def keywords_match_score(text: str, job_title: str) -> Tuple[float, List[str]]:
    jt = job_title.lower().strip()
    keywords = JOB_KEYWORDS.get(jt)
    if not keywords:
        # Try simple contains match on known roles
        for key in JOB_KEYWORDS.keys():
            if key in jt or jt in key:
                keywords = JOB_KEYWORDS[key]
                break
    keywords = keywords or []
    text_lower = text.lower()
    matched = [kw for kw in keywords if kw.lower() in text_lower]
    score = len(matched) / max(1, len(keywords)) if keywords else 0.0
    return score, matched

def length_ok_score(text: str) -> float:
    words = len(text.split())
    if 300 <= words <= 900:
        return 1.0
    if words < 300:
        return words / 300
    return max(0.0, 1.0 - (words - 900) / 2000)

def compute_ats_score(text: str, job_title: str) -> Dict:
    c_contact = 1.0 if has_contact_info(text) else 0.0
    headers = detect_section_headers(text)
    c_headers = 1.0 if len(headers) >= 3 else min(1.0, len(headers) / 3.0)
    c_len = length_ok_score(text)
    c_format = estimate_formatting_score(text)
    c_kw, matched = keywords_match_score(text, job_title)

    w = WEIGHTS
    score = (
        w["has_contact"] * c_contact +
        w["has_section_headers"] * c_headers +
        w["length_ok"] * c_len +
        w["formatting"] * c_format +
        w["keywords_match"] * c_kw
    )
    percent = round(max(0.0, min(1.0, score)) * 100, 1)
    return {
        "score_percent": percent,
        "components": {
            "has_contact": round(c_contact, 3),
            "section_headers": round(c_headers, 3),
            "length_ok": round(c_len, 3),
            "formatting": round(c_format, 3),
            "keywords_match": round(c_kw, 3)
        },
        "matched_keywords": matched,
        "detected_headers": headers
    }

def llm_resume_review(text: str, job_title: str, max_tokens: int = 400) -> str:
    prompt = (
        f"You are an expert resume reviewer and career coach.\n"
        f"Target job title: {job_title}\n"
        f"Resume text (may be messy OCR):\n{text[:5000]}\n\n"
        "Provide:\n"
        "1) ATS-style summary (2 lines)\n"
        "2) Top 5 prioritized fixes (clear bullets)\n"
        "3) Skill gaps to address (tools/frameworks)\n"
        "4) A 2-3 line rewritten professional summary\n"
        "Be concise and actionable.\n"
    )
    return ask_llm(prompt)
