import streamlit as st
import openai
from PyPDF2 import PdfReader
from docx import Document
from utils.scoring import score_resume_to_jd

# Set OpenAI API Key from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---- App Config ----
st.set_page_config(page_title="Job Analyzer MVP", layout="wide")
st.markdown("# 🌟 Job Analyzer: Match Your Resume to Any Job Description")

# ---- File/Text Parsing ----
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text])

def read_text(file):
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    return ""

# ---- Resume & JD Upload ----
st.markdown("## 💾 Upload Your Resume & Job Descriptions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Resume Upload")
    resume_file = st.file_uploader("Upload resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    resume_textbox = st.text_area("Or paste resume text below:")

    resume_text = ""
    if resume_file:
        resume_text = read_text(resume_file)
        st.success("✅ Resume uploaded")
    elif resume_textbox:
        resume_text = resume_textbox.strip()
        st.success("✅ Resume text received")

with col2:
    st.markdown("### 📝 Job Description(s)")
    jd_files = st.file_uploader("Upload 1–5 job descriptions", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    jd_textbox = st.text_area("Or paste one or more JDs below (separate using ---):")

    job_descriptions = []

    if jd_files:
        for jd in jd_files:
            job_descriptions.append(read_text(jd))

    if jd_textbox:
        jd_splits = [j.strip() for j in jd_textbox.strip().split("---") if j.strip()]
        job_descriptions.extend(jd_splits)

    if job_descriptions:
        if len(job_descriptions) > 5:
            st.warning("⚠️ Only up to 5 job descriptions are allowed.")
            job_descriptions = job_descriptions[:5]
        else:
            st.success("✅ Job descriptions received")

# ---- Run Analysis ----
if st.button("🔍 Analyze Fit"):
    if not resume_text:
        st.error("Please upload or paste your resume.")
    elif not job_descriptions:
        st.error("Please upload or paste at least one job description.")
    else:
        with st.spinner("Analyzing resume against job descriptions..."):
            results = []
            for i, jd in enumerate(job_descriptions):
                score, rationale = score_resume_to_jd(resume_text, jd)
                snippet = jd[:60] + "..." if len(jd) > 60 else jd
                results.append((i + 1, snippet, score, rationale))

        # ---- Display Results ----
        results.sort(key=lambda x: x[2], reverse=True)
        st.markdown("## 📊 Ranked Matches")
        for idx, snippet, score, rationale in results:
            st.markdown(f"**{idx}. JD Snippet: _{snippet}_ — Score: {score}/10**")
            with st.expander("Why this score?"):
                st.write(rationale)

# ---- Footer ----
st.markdown("---")
st.markdown("🧠 MVP in progress – built with 💗 by Inna using Streamlit + OpenAI")
