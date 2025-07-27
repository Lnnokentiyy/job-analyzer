import streamlit as st
import os
from utils.scoring import score_resume_to_jd
from utils.file_processing import extract_text_from_file
import docx2txt
import PyPDF2
import tempfile
import requests

# Set page configuration
st.set_page_config(page_title="Job Analyzer", layout="wide")

# Initialize session state for job descriptions
if 'job_links' not in st.session_state:
    st.session_state['job_links'] = []
if 'job_files' not in st.session_state:
    st.session_state['job_files'] = []

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upload", "Summary", "Detail View"])

# --- Main Application Header ---
st.title("🌟 Job Analyzer: Match Your Resume to Any Job Description")
st.markdown("## 📂 Upload Your Resume & Job Descriptions")

# --- Resume Upload Section ---
st.subheader("📄 Resume Upload")

resume_uploaded = False
resume_text = ""

with st.container():
    uploaded_resume = st.file_uploader("Upload resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    submit_resume = st.button("Submit Resume")
    if submit_resume and uploaded_resume:
        resume_text = extract_text_from_file(uploaded_resume)
        resume_uploaded = True
        st.success("✅ Resume uploaded")

# --- Job Description Upload Section ---
st.subheader("📝 Job Description(s)")

# Radio toggle for JD upload type
jd_input_mode = st.radio("Upload job description via:", ["File Upload", "Link Upload"], horizontal=True)

# JD File Upload
if jd_input_mode == "File Upload":
    uploaded_jd = st.file_uploader("Upload job description file", type=["pdf", "docx", "txt"], key="jd_file")
    jd_file_submitted = st.button("Submit JD File")
    if jd_file_submitted and uploaded_jd:
        st.session_state.job_files.append(uploaded_jd)
        st.success("✅ Job description file submitted")

# JD Link Upload
if jd_input_mode == "Link Upload":
    jd_link = st.text_input("Paste job description link", key="jd_link")
    jd_link_submitted = st.button("Submit JD Link")
    if jd_link_submitted and jd_link:
        st.session_state.job_links.append(jd_link)
        st.success("✅ Job description link submitted")

# Show count of received JDs
jd_total_count = len(st.session_state.job_links) + len(st.session_state.job_files)
if jd_total_count:
    st.success(f"✅ {jd_total_count} job description{'s' if jd_total_count > 1 else ''} received")

# Analyze Fit Button
if st.button("🔍 Analyze Fit") and resume_uploaded and jd_total_count > 0:
    st.subheader("🧠 Analysis Results")
    for i, jd_file in enumerate(st.session_state.job_files):
        jd_text = extract_text_from_file(jd_file)
        score, rationale = score_resume_to_jd(resume_text, jd_text)
        st.markdown(f"### 📄 JD File {i + 1}")
        st.write(f"**Fit Score:** {score}")
        st.write(rationale)

    for i, link in enumerate(st.session_state.job_links):
        try:
            response = requests.get(link)
            jd_text = response.text
            score, rationale = score_resume_to_jd(resume_text, jd_text)
            st.markdown(f"### 🔗 JD Link {i + 1}")
            st.write(f"**Fit Score:** {score}")
            st.write(rationale)
        except:
            st.error(f"❌ Could not fetch content from: {link}")

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ by Inna — MVP in progress")
'''

# Save to file
with open("/mnt/data/app.py", "w") as f:
    f.write(app_py_code)
