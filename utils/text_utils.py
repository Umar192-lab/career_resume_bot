# utils/text_utils.py
import re

def clean_text(text: str) -> str:
    # simple normalization
    t = text.strip()
    t = re.sub(r"\r\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t

