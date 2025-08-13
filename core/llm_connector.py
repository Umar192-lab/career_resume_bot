# core/llm_connector.py
"""
Calls local Ollama via subprocess to run the chosen model.
Make sure ollama is installed and you've pulled the model:
    ollama pull <model>
"""
import subprocess
from config.config import OLLAMA_MODEL
import shlex

def ask_llm(prompt: str, timeout: int = 30) -> str:
    """
    Synchronous call to ollama: `ollama run <model> "<prompt>"`.
    Returns the stdout text. In production you may want to run ollama
    as a server and use its HTTP API for better performance.
    """
    try:
        # Build a safe command
        cmd = ["ollama", "run", OLLAMA_MODEL, prompt]
        # run and capture output
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if completed.returncode != 0:
            return f"[LLM ERROR] {completed.stderr.strip()}"
        return completed.stdout.strip()
    except FileNotFoundError:
        return "Ollama not found. Install Ollama and pull a model first."
    except subprocess.TimeoutExpired:
        return "LLM call timed out."
    except Exception as e:
        return f"LLM call failed: {e}"

