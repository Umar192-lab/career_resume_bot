import os
import ollama  # Make sure to install: pip install ollama

# 🔧 Configuration (override via environment variables if needed)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

def ask_llm(prompt: str) -> str:
    """
    Send a prompt to Ollama and return the response text.
    Formats the response as bullet points and limits to less than 100 words.
    """
    if not prompt.strip():
        return "⚠️ Empty prompt."

    # Add instruction for bullet points and word limit
    formatted_prompt = (
        f"{prompt}\n\n"
        "Please answer using concise bullet points. Limit your response to less than 100 words."
    )

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": formatted_prompt}],
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ LLM request failed: {str(e)}"


# ✅ Interactive test mode
if __name__ == "__main__":
    print("🟢 Ollama LLM Connector Ready (model:", OLLAMA_MODEL, ")")
    while True:
        try:
            user_input = input("\n💬 Ask me anything (or type 'exit'): ")
            if user_input.lower().strip() in {"exit", "quit"}:
                print("👋 Exiting...")
                break
            answer = ask_llm(user_input)
            print("🤖 Response:", answer)
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break