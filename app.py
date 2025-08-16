import streamlit as st
from core.response_generator import get_response
from core.resume_processor import (
    extract_text_from_uploaded,
    compute_ats_score,
    llm_resume_review
)
from utils.text_utils import clean_text

# ----------------- Streamlit Config -----------------
st.set_page_config(page_title="Career & Resume Assistant", layout="centered")
st.title("💼 Career & Resume Assistant (Powered by Local LLM)")

# ----------------- Sidebar -----------------
st.sidebar.header("Actions")
mode = st.sidebar.radio("Choose Mode", ["Career Advice Chat", "Resume Review"])

# ----------------- Career Advice Chat -----------------
if mode == "Career Advice Chat":
    st.header("🧑‍💼 Career Advice Chat")
    st.write("Ask career-related questions (job search, upskilling, interview prep, etc.).")

    user_q = st.text_area(
        "Ask your question:",
        height=120,
        placeholder="E.g., What skills should I learn for a Data Analyst role?"
    )
    
    if st.button("Get Advice"):
        if not user_q.strip():
            st.warning("⚠️ Please enter a question before asking.")
        else:
            with st.spinner("🤔 Thinking..."):
                resp = get_response(user_q)
            st.subheader("💡 Advice")
            st.write(resp)

# ----------------- Resume Review -----------------
elif mode == "Resume Review":
    st.header("📄 Resume Review & ATS Score")
    st.write("Upload your resume or paste text below to get an ATS score and LLM feedback.")

    uploaded = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
    pasted = st.text_area(
        "Or paste resume text here:",
        height=200,
        placeholder="Paste your resume content..."
    )
    job_title = st.text_input("Target Job Title (e.g., Data Analyst):", value="Data Analyst")

    if st.button("Analyze Resume"):
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
            st.json(result["components"])  # ✅ Display in structured JSON

            if result["matched_keywords"]:
                st.write("✅ Matched Keywords:", ", ".join(result["matched_keywords"]))
            if result["detected_headers"]:
                st.write("📝 Detected Headers:", ", ".join(result["detected_headers"]))

            # Generate LLM review
            with st.spinner("🤖 Generating detailed feedback with LLM..."):
                review = llm_resume_review(resume_text, job_title)

            st.subheader("📢 LLM Review & Suggestions")
            st.write(review)
