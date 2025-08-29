import streamlit as st
import time

from core.response_generator import get_response
from core.resume_processor import (
    extract_text_from_uploaded,
    compute_ats_score,
    llm_resume_review
)
from utils.text_utils import clean_text

# ----------------- Streamlit Config -----------------
st.set_page_config(page_title="Career & Resume Chatbot", layout="centered")
st.title("💼 Career & Resume Chatbot (Powered by Local LLM)")

# ----------------- Sidebar -----------------
st.sidebar.header("⚙️ Actions")
mode = st.sidebar.radio("Choose Mode", ["Career Advice Chat", "Resume Review"])

# ----------------- Career Advice Chat -----------------
if mode == "Career Advice Chat":
    st.header("🧑‍💼 Career Advice Chat")
    st.write("Chat with me about jobs, interviews, programming, or courses. 🚀")

    # Keep chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Input box with ENTER submission (no button)
    user_q = st.chat_input("Type your question here...")

    if user_q:  # When user presses Enter
        # Store user message
        st.session_state.chat_history.append({"role": "user", "content": user_q})

        # Get LLM response
        with st.spinner("🤔 Thinking..."):
            response_text = get_response(user_q)

        # Typing effect simulation
        typed_text = ""
        placeholder = st.empty()
        for word in response_text.split():
            typed_text += word + " "
            placeholder.markdown("💡 " + typed_text)
            time.sleep(0.05)

        # Store bot response
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})

    # Display full conversation history
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.chat_message("user").markdown(chat["content"])
        else:
            st.chat_message("assistant").markdown(chat["content"])

# ----------------- Resume Review -----------------
elif mode == "Resume Review":
    st.header("📄 Resume Review & ATS Score")
    st.write("Upload your resume or paste text below to get an ATS score and LLM feedback.")

    uploaded = st.file_uploader("📂 Upload your resume", type=["pdf", "docx", "txt"])
    pasted = st.text_area(
        "📋 Or paste resume text here:",
        height=200,
        placeholder="Paste your resume content..."
    )
    job_title = st.text_input("🎯 Target Job Title:", value="Data Analyst")

    if st.button("🔍 Analyze Resume"):
        resume_text = ""

        # Extract from uploaded file
        if uploaded:
            resume_text = extract_text_from_uploaded(uploaded)

        # Append pasted text if provided
        if pasted.strip():
            resume_text = pasted if not resume_text else (resume_text + "\n\n" + pasted)

        # Clean text
        resume_text = clean_text(resume_text)

        # Validate
        if len(resume_text) < 30:
            st.warning("⚠️ Please upload or paste a longer resume (at least a few lines).")
        else:
            # Compute ATS Score
            with st.spinner("📊 Computing ATS score..."):
                result = compute_ats_score(resume_text, job_title)

            st.metric("ATS Score", f"{result['score_percent']}%")
            st.write("### 🔍 Breakdown")
            st.json(result["components"])

            if result["matched_keywords"]:
                st.write("✅ Matched Keywords:", ", ".join(result["matched_keywords"]))
            if result["detected_headers"]:
                st.write("📝 Detected Headers:", ", ".join(result["detected_headers"]))

            # Generate LLM review with typing effect
            with st.spinner("🤖 Generating detailed feedback..."):
                review = llm_resume_review(resume_text, job_title)

            placeholder = st.empty()
            typed_text = ""
            for word in review.split():
                typed_text += word + " "
                placeholder.markdown("📢 " + typed_text)
                time.sleep(0.05)
