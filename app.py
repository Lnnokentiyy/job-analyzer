import streamlit as st
import openai
import os
import docx2txt
import PyPDF2
import requests

st.set_page_config(page_title="AI Job Analyzer", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upload", "Summary", "Detail View"])

# Page title
st.title("🌟 Job Analyzer: Match Your Resume to Any Job Description")

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Utilities for extracting text
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_file):
    return docx2txt.process(docx_file)

def fetch_text_from_link(url):
    try:
        response = requests.get(url)
        return response.text
    except Exception as e:
        return f"Error fetching from URL: {e}"

# AI scoring logic
def score_resume_to_jd(resume_text, jd_text):
    prompt = f\"\"\"
You are a professional career coach. Score the resume against the job description.
Return only a JSON object with:
- "score" (0-100)
- "rationale" (concise explanation in 2-3 bullet points)

Resume:
{resume_text}

Job Description:
{jd_text}
\"\"\"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

# Initialize session state
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "jd_files" not in st.session_state:
    st.session_state.jd_files = []
if "jd_links" not in st.session_state:
    st.session_state.jd_links = []

# Upload Page
if page == "Upload":
    st.subheader("📄 Upload Your Resume & Job Descriptions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Resume Upload**")
        resume_file = st.file_uploader("Upload resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if st.button("Submit Resume"):
            if resume_file:
                file_type = resume_file.name.split(".")[-1]
                if file_type == "pdf":
                    st.session_state.resume_text = extract_text_from_pdf(resume_file)
                elif file_type == "docx":
                    st.session_state.resume_text = extract_text_from_docx(resume_file)
                else:
                    st.session_state.resume_text = resume_file.read().decode("utf-8")
                st.success("✅ Resume uploaded successfully!")

    with col2:
        st.markdown("**Job Description(s)**")
        jd_upload_method = st.radio("Select input type:", ["File Upload", "Link Upload"])

        if jd_upload_method == "File Upload":
            jd_file = st.file_uploader("Upload job description file", type=["pdf", "docx", "txt"], key="jd_file")
            if st.button("Submit JD File"):
                if jd_file:
                    ext = jd_file.name.split(".")[-1]
                    if ext == "pdf":
                        jd_text = extract_text_from_pdf(jd_file)
                    elif ext == "docx":
                        jd_text = extract_text_from_docx(jd_file)
                    else:
                        jd_text = jd_file.read().decode("utf-8")
                    st.session_state.jd_files.append(jd_text)
                    st.success(f"✅ JD file uploaded ({len(st.session_state.jd_files)} total)")

        elif jd_upload_method == "Link Upload":
            new_link = st.text_input("Paste job description link", key="jd_link")
            if st.button("Submit JD Link"):
                if new_link:
                    jd_text = fetch_text_from_link(new_link)
                    st.session_state.jd_links.append(jd_text)
                    st.success(f"✅ JD link submitted ({len(st.session_state.jd_links)} total)")

    if st.session_state.jd_files or st.session_state.jd_links:
        total_jds = len(st.session_state.jd_files) + len(st.session_state.jd_links)
        st.success(f"🎯 {total_jds} job description(s) received")

    if st.button("🔍 Analyze Fit"):
        resume = st.session_state.resume_text
        if not resume:
            st.warning("Please upload a resume.")
        elif not (st.session_state.jd_files or st.session_state.jd_links):
            st.warning("Please upload at least one job description.")
        else:
            st.subheader("Results")
            for idx, jd in enumerate(st.session_state.jd_files + st.session_state.jd_links):
                st.markdown(f"**Job Description {idx+1}**")
                result = score_resume_to_jd(resume, jd)
                st.json(result)

# Future pages
if page == "Summary":
    st.write("Summary view coming soon...")

if page == "Detail View":
    st.write("Detailed view coming soon...")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>🚀 MVP in progress — made with ❤️ by Inna</p>", unsafe_allow_html=True)
"""

import ace_tools as tools; tools.display_text_to_user(name="Final app.py", text=app_code)
