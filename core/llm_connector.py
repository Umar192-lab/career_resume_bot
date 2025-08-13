# core/llm_connector.py
"""
Uses Ollama's HTTP API (fast) with a fallback to subprocess if HTTP isn't available.
Run Ollama in the background:
    ollama serve
Pull a model first (e.g., mistral or gemma):
    ollama pull mistral
"""

import json
import os
import subprocess
import requests
from typing import Optional

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

def ask_llm(prompt: str, timeout: int = 45) -> str:
    # Try HTTP first
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        # Ollama returns {"response": "...", "done": true, ...}
        return (data.get("response") or "").strip() or "[Empty response from model]"
    except Exception:
        # Fallback to subprocess (works even if HTTP server isn't running)
        try:
            completed = subprocess.run(
                ["ollama", "run", OLLAMA_MODEL, prompt],
                capture_output=True, text=True, timeout=timeout
            )
            if completed.returncode != 0:
                err = completed.stderr.strip() or "Unknown error"
                return f"[LLM ERROR] {err}"
            return completed.stdout.strip() or "[Empty response from model]"
        except FileNotFoundError:
            return "Ollama not found. Install from https://ollama.ai and pull a model."
        except subprocess.TimeoutExpired:
            return "LLM call timed out."
        except Exception as e:
            return f"LLM call failed: {e}"
