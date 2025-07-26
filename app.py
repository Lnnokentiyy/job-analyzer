import streamlit as st
import docx2txt
import PyPDF2
import re
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---- GPT-3.5 function ----
def get_gpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
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

# ---- Session State ----
if 'resume' not in st.session_state:
    st.session_state.resume = None
if 'job_descriptions' not in st.session_state:
    st.session_state.job_descriptions = []

# ---- Navigation ----
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
            jds = st.session_state.job_descriptions

            # ---- Extract Resume Text ----
            if hasattr(resume, 'read'):
                if resume.name.endswith(".pdf"):
                    pdf_reader = PyPDF2.PdfReader(resume)
                    resume_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
                elif resume.name.endswith(".docx"):
                    resume_text = docx2txt.process(resume)
                elif resume.name.endswith(".txt"):
                    resume_text = resume.read().decode("utf-8")
                else:
                    resume_text = "Unsupported file format."
            else:
                resume_text = resume

            resume_text = resume_text.strip()

            ranked_results = []

            # ---- Handle Multiple Uploaded Files ----
            if isinstance(jds, list) and hasattr(jds[0], 'read'):
                for jd_file in jds:
                    if jd_file.name.endswith(".pdf"):
                        pdf_reader = PyPDF2.PdfReader(jd_file)
                        jd_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
                    elif jd_file.name.endswith(".docx"):
                        jd_text = docx2txt.process(jd_file)
                    elif jd_file.name.endswith(".txt"):
                        jd_text = jd_file.read().decode("utf-8")
                    else:
                        jd_text = "Unsupported file format."

                    jd_text = jd_text.strip()

                    prompt = f"""Compare this resume and job description. Rate the fit from 0 to 10. 
Explain briefly why. Start your answer with: Score: X/10\n\nResume:\n{resume_text}\n\nJob Description:\n{jd_text}"""

                    with st.spinner(f"Analyzing {jd_file.name}..."):
                        result = get_gpt_response(prompt)

                    score_match = re.search(r"Score:\s*(\d+)/10", result)
                    score = int(score_match.group(1)) if score_match else 0
                    ranked_results.append((jd_file.name, score, result))

            else:
                # ---- Handle Pasted JDs ----
                jds_texts = jds.split("---") if isinstance(jds, str) else []
                for idx, jd_text in enumerate(jds_texts, 1):
                    jd_text = jd_text.strip()
                    prompt = f"""Compare this resume and job description. Rate the fit from 0 to 10. 
Explain briefly why. Start your answer with: Score: X/10\n\nResume:\n{resume_text}\n\nJob Description:\n{jd_text}"""
                    with st.spinner(f"Analyzing JD {idx}..."):
                        result = get_gpt_response(prompt)
                    score_match = re.search(r"Score:\s*(\d+)/10", result)
                    score = int(score_match.group(1)) if score_match else 0
                    ranked_results.append((f"Pasted JD {idx}", score, result))

            # ---- Display Sorted Results ----
            ranked_results.sort(key=lambda x: x[1], reverse=True)

            st.subheader("📊 Ranked Matches")
            for i, (jd_name, score, explanation) in enumerate(ranked_results, 1):
                st.markdown(f"### {i}. {jd_name} — Score: {score}/10")
                st.write(explanation)
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
