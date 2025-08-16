import time
import os
import ollama  # Make sure to install: pip install ollama

# 🔧 Configuration (override via environment variables if needed)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:2b")

def ask_llm(prompt: str) -> str:
    """
    Send a prompt to Ollama and return the response text.
    """
    if not prompt.strip():
        return "⚠️ Empty prompt."

    start = time.time()
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
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