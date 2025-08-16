from core.llm_connector import ask_llm

def get_career_advice(user_input: str) -> str:
    """
    Generates structured career advice using the local LLM.
    """
    if not user_input.strip():
        return "⚠️ Please enter your career question or interests."

    prompt = f"""
You are an AI career guidance assistant. 
The user has asked the following career-related question:

{user_input}

Please provide:
1. A clear and helpful explanation.
2. Practical next steps the user can take.
3. Any relevant skills, tools, or resources they should explore.
    """

    try:
        response = ask_llm(prompt)
        return response.strip() if response else "⚠️ No response from LLM. Please try again."
    except Exception as e:
        return f"⚠️ Error while generating advice: {str(e)}"
