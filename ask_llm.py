import time
import os
import ollama  # Make sure to install: pip install ollama

# 🔧 Configuration (override via environment variables if needed)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

def ask_llm(prompt: str) -> str:
    """
    Send a prompt to Ollama and return the response text.
    Limits the response to 100 words.
    """
    if not prompt.strip():
        return "⚠️ Empty prompt."

    # Add instruction to limit response length
    limited_prompt = f"{prompt}\n\nPlease answer in less than 100 words."

    start = time.time()
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": limited_prompt}],
        )
        elapsed = time.time() - start
        print(f"⏱️ LLM response time: {elapsed:.2f} seconds")
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