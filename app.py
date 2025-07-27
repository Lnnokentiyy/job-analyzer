import streamlit as st
import openai
import docx2txt
import PyPDF2
import os
import tempfile
import requests
from utils.scoring import score_resume_to_jd

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Job Analyzer", layout="wide")

st.title("🌟 Job Analyzer: Match Your Resume to Any Job Description")

# Sidebar navigation
st.sidebar.title("Navigation")
view = st.sidebar.radio("Select View", ["Upload", "Summary", "Detail View"])

# Initialize session state
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "job_descriptions" not in st.session_state:
    st.session_state.job_descriptions = []
if "upload_option" not in st.session_state:
    st.session_state.upload_option = "File"

# Upload options (File or Link)
st.subheader("📄 Upload Your Resume & Job Descriptions")

# Resume Upload
st.markdown("### 📌 Resume Upload")
resume_upload = st.radio("Select Resume Upload Method", ["File"], key="resume_upload_radio")

if resume_upload == "File":
    uploaded_resume = st.file_uploader("Upload resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="resume_file")
    if uploaded_resume is not None:
        file_type = uploaded_resume.name.split(".")[-1]
        if file_type == "pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_resume)
            resume_text = ""
            for page in pdf_reader.pages:
                resume_text += page.extract_text()
        elif file_type == "docx":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                tmp_file.write(uploaded_resume.read())
                resume_text = docx2txt.process(tmp_file.name)
        else:
            resume_text = uploaded_resume.read().decode("utf-8")
        st.session_state.resume_text = resume_text
        st.success("✅ Resume uploaded")

# Job Description Upload
st.markdown("### 📝 Job Description(s)")
upload_option = st.radio("Select Job Description Upload Method", ["File", "Link"], key="jd_upload_radio")

if upload_option == "File":
    jd_files = st.file_uploader("Upload 1–5 job descriptions", accept_multiple_files=True, type=["pdf", "docx", "txt"], key="jd_files")
    if jd_files:
        for jd_file in jd_files:
            file_type = jd_file.name.split(".")[-1]
            if file_type == "pdf":
                pdf_reader = PyPDF2.PdfReader(jd_file)
                jd_text = ""
                for page in pdf_reader.pages:
                    jd_text += page.extract_text()
            elif file_type == "docx":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                    tmp_file.write(jd_file.read())
                    jd_text = docx2txt.process(tmp_file.name)
            else:
                jd_text = jd_file.read().decode("utf-8")
            st.session_state.job_descriptions.append(jd_text)
        st.success(f"✅ {len(jd_files)} job description(s) received")

elif upload_option == "Link":
    link_container = st.container()
    new_link = link_container.text_input("Paste job description link:")
    if link_container.button("Submit", key="link_submit"):
        if new_link:
            try:
                response = requests.get(new_link)
                if response.status_code == 200:
                    jd_text = response.text
                    st.session_state.job_descriptions.append(jd_text)
                    st.success(f"✅ {len(st.session_state.job_descriptions)} job description(s) received")
                else:
                    st.error("❌ Failed to fetch job description from the link")
            except Exception as e:
                st.error(f"❌ Error fetching link: {str(e)}")

# Analyze Fit
if view == "Upload":
    if st.button("🔍 Analyze Fit"):
        if not st.session_state.resume_text:
            st.error("❌ Please upload a resume first.")
        elif not st.session_state.job_descriptions:
            st.error("❌ Please upload at least one job description.")
        else:
            for idx, jd in enumerate(st.session_state.job_descriptions):
                score, rationale = score_resume_to_jd(st.session_state.resume_text, jd)
                st.markdown(f"### 🧠 Match Result for Job Description {idx + 1}")
                st.markdown(f"**Fit Score:** {score}")
                st.markdown(f"**Rationale:** {rationale}")
"""

# Save the updated code
with open("/mnt/data/app.py", "w") as f:
    f.write(updated_code.strip())
