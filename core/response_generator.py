# core/response_generator.py
import os
import ollama
import time

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:2b")

def ask_llm(prompt: str) -> str:
    """
    Ask Ollama LLM with greeting handling + concise responses.
    """
    if not prompt.strip():
        return "⚠️ Empty prompt."

    # Greeting handling
    greetings = {"hello", "hi", "hey", "hola", "namaste","bye","goodbye"}
    if prompt.strip().lower() in greetings:
        return prompt.strip().capitalize() + "!"
    

    formatted_prompt = (
        f"{prompt}\n\n"
        "Please answer concisely in less than 100 words."
    )

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": formatted_prompt}],
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ LLM request failed: {str(e)}"

def get_response(user_input: str) -> str:
    """
    Public function for app.py to call.
    """
    return ask_llm(user_input)
