import streamlit as st
import os
from PyPDF2 import PdfReader
from docx import Document
import openai
from utils.scoring import score_resume_to_jd

# Use Streamlit secrets for API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Job Analyzer MVP", layout="wide")
st.markdown("# 🌟 Job Analyzer: Match Your Resume to Any Job Description")

# === File & Text Parsing Functions ===
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def extract_text_from_docx(file):
    doc = Document(file)
    return "\\n".join([p.text for p in doc.paragraphs if p.text])

def read_text(file):
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        return ""

# === Session State Setup ===
if "jd_files" not in st.session_state:
    st.session_state.jd_files = []
if "jd_links" not in st.session_state:
    st.session_state.jd_links = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# === Upload Resume ===
st.markdown("## 💾 Upload Your Resume")
resume_file = st.file_uploader("Upload resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
if resume_file:
    st.session_state.resume_text = read_text(resume_file)
    st.success("✅ Resume uploaded successfully.")

# === Upload Job Descriptions ===
st.markdown("## 📥 Upload Job Descriptions")

upload_type = st.radio("Choose input method:", ["Upload File", "Paste Link"])

if upload_type == "Upload File":
    jd_file = st.file_uploader("Upload job description", key="jd_file", type=["pdf", "docx", "txt"])
    if st.button("Submit JD File") and jd_file:
        if len(st.session_state.jd_files) + len(st.session_state.jd_links) >= 5:
            st.warning("⚠️ You can only add up to 5 job descriptions.")
        else:
            st.session_state.jd_files.append(jd_file)
elif upload_type == "Paste Link":
    jd_link = st.text_input("Paste job description link here", key="jd_link")
    if st.button("Submit JD Link") and jd_link:
        if len(st.session_state.jd_files) + len(st.session_state.jd_links) >= 5:
            st.warning("⚠️ You can only add up to 5 job descriptions.")
        else:
            st.session_state.jd_links.append(jd_link.strip())

# === Display current JDs ===
st.markdown("### ✅ Added Job Descriptions:")
for i, file in enumerate(st.session_state.jd_files):
    col1, col2 = st.columns([8,1])
    with col1:
        st.write(f"📄 File: {file.name}")
    with col2:
        if st.button("❌", key=f"remove_file_{i}"):
            st.session_state.jd_files.pop(i)
            st.experimental_rerun()

for i, link in enumerate(st.session_state.jd_links):
    col1, col2 = st.columns([8,1])
    with col1:
        st.write(f"🔗 Link: {link}")
    with col2:
        if st.button("❌", key=f"remove_link_{i}"):
            st.session_state.jd_links.pop(i)
            st.experimental_rerun()

total_jds = len(st.session_state.jd_files) + len(st.session_state.jd_links)
st.markdown(f"**Total job descriptions received: {total_jds}**")

# === Analyze Button ===
if st.button("🔍 Analyze Fit"):
    if not st.session_state.resume_text:
        st.error("❌ Please upload your resume first.")
    elif total_jds == 0:
        st.error("❌ Please upload at least one job description.")
    else:
        job_descriptions = []

        # Extract text from uploaded files
        for file in st.session_state.jd_files:
            job_descriptions.append(read_text(file))

        # Fetch content from links (placeholder logic)
        for link in st.session_state.jd_links:
            job_descriptions.append(link)  # You can replace with real fetch logic

        with st.spinner("Analyzing resume against job descriptions..."):
            results = []
            for i, jd in enumerate(job_descriptions):
                score, rationale = score_resume_to_jd(st.session_state.resume_text, jd)
                results.append((i + 1, jd[:60] + ("..." if len(jd) > 60 else ""), score, rationale))

        st.markdown("## 📊 Ranked Matches")
        results.sort(key=lambda x: x[2], reverse=True)
        for idx, title, score, rationale in results:
            st.markdown(f"**{idx}. {title} — Score: {score}/10**")
            with st.expander("Why this score?"):
                st.write(rationale)

st.markdown("---")
st.caption("🧠 MVP in progress – built with 💗 by Inna using Streamlit + OpenAI")
"""

# Save the code as a file to be accessed by the user
path = "/mnt/data/app.py"
with open(path, "w") as f:
    f.write(app_py_code)

path
Result
'/mnt/data/app.py'
