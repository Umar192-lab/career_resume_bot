# app.py
import streamlit as st
from core.response_generator import get_career_advice
from core.resume_processor import extract_text_from_uploaded, compute_ats_score, llm_resume_review
from utils.text_utils import clean_text

st.set_page_config(page_title="Career & Resume Assistant", layout="centered")
st.title("Career & Resume Assistant (Local LLM)")

st.sidebar.header("Actions")
mode = st.sidebar.radio("Choose mode", ["Career Advice Chat", "Resume Review"])

if mode == "Career Advice Chat":
    st.header("Career Advice Chat")
    st.write("Ask career questions (job search, upskilling, interview tips). Answers come from your local LLM.")
    user_q = st.text_area("Ask your question:", height=120)
    if st.button("Get Advice"):
        if not user_q.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                resp = get_career_advice(user_q)
            st.subheader("Advice")
            st.write(resp)

else:
    st.header("Resume Review & ATS Score")
    st.write("Upload your resume as PDF/DOCX/TXT or paste content.")
    uploaded = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
    pasted = st.text_area("Or paste your resume text here:", height=200)
    job_title = st.text_input("Target job title (e.g., Data Analyst):", value="Data Analyst")

    if st.button("Analyze Resume"):
        resume_text = ""
        if uploaded:
            resume_text = extract_text_from_uploaded(uploaded)
        if pasted.strip():
            resume_text = pasted if not resume_text else (resume_text + "\n\n" + pasted)
        resume_text = clean_text(resume_text)

        if len(resume_text) < 30:
            st.warning("Please upload or paste a longer resume (at least a few lines).")
        else:
            with st.spinner("Computing ATS score..."):
                result = compute_ats_score(resume_text, job_title)
            st.metric("ATS Score", f"{result['score_percent']}%")
            st.write("Breakdown:", result["components"])
            if result["matched_keywords"]:
                st.write("Matched keywords:", ", ".join(result["matched_keywords"]))
            if result["detected_headers"]:
                st.write("Detected headers:", ", ".join(result["detected_headers"]))

            with st.spinner("Generating detailed feedback (LLM)..."):
                review = llm_resume_review(resume_text, job_title)
            st.subheader("LLM Review & Suggestions")
            st.write(review)
