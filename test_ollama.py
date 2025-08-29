# test_ollama.py

from core.llm_connector import ask_llm

def main():
    prompt = "Say hello in one sentence"
    print(f"➡️ Sending prompt: {prompt}")
    reply = ask_llm(prompt)
    print("✅ LLM Response:", reply)

if __name__ == "__main__":
    main()
