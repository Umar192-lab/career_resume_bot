import os
import time
import ollama

# 🔧 Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:2b")

# Predefined casual responses
CASUAL_RESPONSES = {
    "hello": "👋 Hello!",
    "hi": "👋 Hi there!",
    "hey": "👋 Hey!",
    "hola": "👋 Hola!",
    "namaste": "🙏 Namaste!",
    "whats up": "😎 All good, what about you?",
    "how are you": "😊 I'm doing great, thanks for asking! How about you?",
}

def typing_effect(text: str, delay: float = 0.08):
    """
    Simulate a typing effect by printing text word by word.
    """
    for word in text.split():
        print(word, end=" ", flush=True)
        time.sleep(delay)
    print("\n")


def ask_llm(prompt: str) -> str:
    """
    Responds with predefined casual replies for greetings/small talk.
    Otherwise, queries the LLM (Ollama).
    """
    if not prompt.strip():
        return "⚠️ Empty prompt."

    cleaned_prompt = prompt.lower().strip()

    # 🎯 Handle small talk without hitting LLM
    if cleaned_prompt in CASUAL_RESPONSES:
        return CASUAL_RESPONSES[cleaned_prompt]

    # ✅ Otherwise, send to Ollama for a career/resume-related response
    formatted_prompt = (
        f"{prompt}\n\n"
        "Please answer concisely in less than 100 words."
    )

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": formatted_prompt}],
        )
        full_text = response["message"]["content"].strip()

        # 🎭 Show typing effect
        typing_effect(full_text)

        return full_text
    except Exception as e:
        return f"⚠️ LLM request failed: {str(e)}"


if __name__ == "__main__":
    print(f"🟢 Ollama LLM Connector Ready (model: {OLLAMA_MODEL})")

    while True:
        try:
            user_input = input("\n💬 Ask me anything (or type 'exit'): ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Exiting...")
                break

            print("🤖 Response: ", end="", flush=True)
            reply = ask_llm(user_input)

            if reply:
                print(reply)

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
