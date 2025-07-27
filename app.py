import streamlit as st
import openai
from PyPDF2 import PdfReader
from docx import Document
from utils.scoring import score_resume_to_jd

# Configure OpenAI API key securely from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit page setup
st.set_page_config(page_title="Job Analyzer MVP", layout="wide")
st.markdown("# 🌟 Job Analyzer: Match Your Resume to Any Job Description")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upload", "Summary", "Detail View"])

# --- File & Text Parsing Functions ---
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
    else:
        return ""

# --- Page Logic ---
if page == "Upload":
    st.markdown("## 💾 Upload Your Resume & Job Descriptions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📄 Resume Upload")
        resume_file = st.file_uploader("Upload resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        resume_textbox = st.text_area("Or paste resume text below:")

        if resume_file:
            resume_text = read_text(resume_file)
            st.success("✅ Resume uploaded")
        elif resume_textbox:
            resume_text = resume_textbox.strip()
            st.success("✅ Resume text received")
        else:
            resume_text = ""

    with col2:
        st.markdown("### 📝 Job Description(s)")
        jd_files = st.file_uploader("Upload 1–5 job descriptions", type=["pdf", "docx", "txt"], accept_multiple_files=True)
        jd_textbox = st.text_area(
            "Or paste one or more JDs below (separate using ---):",
            help="Example:\nJD1 description text\n---\nJD2 description text"
        )

        job_descriptions = []

        if jd_files:
            for jd in jd_files:
                text = read_text(jd)
                if text:
                    job_descriptions.append(text)

        if jd_textbox:
            jd_splits = [j.strip() for j in jd_textbox.strip().split("---") if j.strip()]
            job_descriptions.extend(jd_splits)

        if job_descriptions:
            if len(job_descriptions) > 5:
                st.warning("⚠️ You can only upload or paste up to 5 job descriptions.")
                job_descriptions = job_descriptions[:5]
            else:
                st.success(f"✅ {len(job_descriptions)} job description(s) received")

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
                    results.append((i + 1, jd[:60] + ("..." if len(jd) > 60 else ""), score, rationale))

            # --- Output ---
            st.markdown("## 📊 Ranked Matches")
            results.sort(key=lambda x: x[2], reverse=True)
            for idx, title, score, rationale in results:
                st.markdown(f"**{idx}. {title} — Score: {score}/10**")
                with st.expander("Why this score?"):
                    st.write(rationale)

elif page == "Summary":
    st.markdown("## 📋 Summary View")
    st.info("This feature is coming soon. You will be able to view key resume-JD alignment summaries here.")

elif page == "Detail View":
    st.markdown("## 🔎 Detail View")
    st.info("This feature is coming soon. You will be able to compare resumes and job descriptions in detail here.")

# Footer
st.markdown("---")
st.markdown("🧠 MVP in progress – built with 💗 by Inna using Streamlit + OpenAI")
