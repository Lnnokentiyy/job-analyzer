import openai
import streamlit as st

# Set your OpenAI API key using Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to get GPT response
def get_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # FREE tier / low-cost
        messages=[
            {"role": "system", "content": "You are a helpful assistant that compares resumes and job descriptions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )
    return response.choices[0].message.content

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
        if st.session_state.resume and st.session_state.job_descriptions:
            resume = st.session_state.resume
            jd = st.session_state.job_descriptions

            # Extract resume text
            if hasattr(resume, 'read'):
                resume_text = resume.read().decode("utf-8")
            else:
                resume_text = resume

            # Extract job description text
            if isinstance(jd, list) and hasattr(jd[0], 'read'):
                jd_text = jd[0].read().decode("utf-8")
            else:
                jd_text = jd if isinstance(jd, str) else ""

            # 🔧 Cleaner UX: strip trailing/leading whitespace
            resume_text = resume_text.strip() if isinstance(resume_text, str) else resume_text
            jd_text = jd_text.strip() if isinstance(jd_text, str) else jd_text

            prompt = f"""Compare the following resume to the job description and give a fit summary:\n\nResume:\n{resume_text}\n\nJob Description:\n{jd_text}"""

            with st.spinner("Analyzing..."):
                result = get_gpt_response(prompt)

            st.subheader("✅ Match Summary")
            st.write(result)
        else:
            st.warning("Please upload both a resume and at least one job description.")

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
