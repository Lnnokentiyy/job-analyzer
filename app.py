import openai
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---- App Config ----
st.set_page_config(page_title="Job Analyzer", layout="wide")
st.title("🎯 Job Analyzer: Match Your Resume to Any Job Description")

# ---- Session State Setup ----
if 'resume' not in st.session_state:
    st.session_state.resume = None
if 'job_descriptions' not in st.session_state:
    st.session_state.job_descriptions = []

# ---- Page Navigation ----
page = st.sidebar.radio("Navigation", ["Upload", "Summary", "Detail View"])

# ---- Upload Page ----
if page == "Upload":
    st.header("1️⃣ Upload Your Resume & Job Descriptions")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Resume Upload")
        resume_file = st.file_uploader("Upload resume (PDF or DOCX)", type=["pdf", "docx"])
        resume_text = st.text_area("Or paste resume text below:")

        if resume_file or resume_text:
            st.success("✅ Resume received")
            st.session_state.resume = resume_file or resume_text

    with col2:
        st.subheader("📝 Job Description(s)")
        jd_files = st.file_uploader("Upload 1–5 job descriptions", type=["pdf", "docx", "txt"], accept_multiple_files=True)
        jd_text = st.text_area("Or paste one or more JDs below (separated by ---):")

        if jd_files or jd_text:
            st.success("✅ Job descriptions received")
            st.session_state.job_descriptions = jd_files or jd_text

    if st.button("🔍 Analyze Fit"):
        st.success("🚀 Analysis starting... (placeholder only)")
        # In future: run GPT/OpenAI logic here

# ---- Summary Page ----
elif page == "Summary":
    st.header("📊 Results Summary")
    st.write("This section will show scorecards for each JD.")
    st.info("Placeholder summary table — AI logic coming soon!")

# ---- Detail View Page ----
elif page == "Detail View":
    st.header("🧠 Job Detail Feedback")
    st.write("Select a job to view personalized resume tips.")
    st.info("This will contain feedback, bullet points, copy buttons, etc.")

# ---- Footer ----
st.markdown("---")
st.caption("🚧 MVP in progress – built with ❤️ by Inna using Streamlit + OpenAI")
