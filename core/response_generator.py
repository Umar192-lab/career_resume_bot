# core/response_generator.py
from core.llm_connector import ask_llm

def career_advice_prompt(user_message: str, context: str = "") -> str:
    """
    Build a context-rich prompt for career advice.
    """
    prompt = (
        "You are a friendly career advisor. Provide concise, actionable advice.\n\n"
        f"Context: {context}\n"
        f"User question: {user_message}\n\n"
        "Give: 1) Short suggestion (1-2 lines). 2) Steps or resources (bullet points). 3) Suggested skill improvements.\n"
    )
    return prompt

def get_career_advice(user_message: str, context: str = "") -> str:
    prompt = career_advice_prompt(user_message, context)
    return ask_llm(prompt)

