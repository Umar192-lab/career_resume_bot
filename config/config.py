# config/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ollama model to use (pick a small model name you pulled with ollama pull)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")  # change if you pulled a different model
# KB / data
JOB_KEYWORDS_PATH = os.path.join(BASE_DIR, "data", "job_keywords.json")

# Heuristic weights for ATS scoring (you can tune)
WEIGHTS = {
    "has_contact": 0.15,
    "has_section_headers": 0.20,
    "length_ok": 0.10,
    "keywords_match": 0.35,
    "formatting": 0.20
}

