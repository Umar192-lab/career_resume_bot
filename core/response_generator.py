from core.llm_connector import ask_llm

def get_response(user_input: str, mode: str = "career") -> str:
    """
    Generates a response using the local LLM.
    - mode = "career" → structured career advice
    - mode = "general" → answers any type of question
    Limits the response to 100 words.
    """
    if not user_input.strip():
        return "⚠️ Please enter a question."

    if mode == "career":
        prompt = f"""
You are an AI career guidance assistant. 
The user has asked the following career-related question:

{user_input}

Please provide:
1. A clear and helpful explanation.
2. Practical next steps the user can take.
3. Any relevant skills, tools, or resources they should explore.

Please answer in less than 100 words.
        """
    else:  # general mode
        prompt = f"The user asked: {user_input}\n\nPlease give a clear, helpful answer in less than 100 words."

    try:
        response = ask_llm(prompt)
        return response.strip() if response else "⚠️ No response from LLM. Please try again."
    except Exception as e:
        return f"⚠️ Error while generating advice: {str(e)}"