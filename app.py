import streamlit as st
import docx2txt
import PyPDF2
from openai import OpenAI, RateLimitError, OpenAIError
import re

# ✅ NEW: Instantiate OpenAI Client using new SDK
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---- Helper: Extract Text ----
def extract_text(file):
    if file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
    elif file.name.endswith(".docx"):
        return docx2txt.process(file)
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        return "Unsupported file format."

# ---- GPT Call ----
def get_gpt_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that compares resumes and job descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except RateLimitError:
        return "⚠️ Rate limit hit. Please try again in a minute."
    except OpenAIError as e:
        return f"❌ API error: {e}"

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

# ---- Upload ----
if page == "Upload":
    st.header("1️⃣ Upload Your Resume & Job Descriptions")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Resume Upload")
        resume_file = st.file_uploader("Upload resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        resume_textbox = st.text_area("Or paste resume text below:")

        if resume_file or resume_textbox:
            st.session_state.resume = resume_file or resume_textbox
            st.success("✅ Resume received")

    with col2:
        st.subheader("📝 Job Description(s)")
        jd_files = st.file_uploader("Upload 1–5 job descriptions", type=["pdf", "docx", "txt"], accept_multiple_files=True)
        jd_textbox = st.text_area("Or paste one or more JDs below (separated by ---):")

        if jd_files or jd_textbox:
            st.session_state.job_descriptions = jd_files or jd_textbox
            st.success("✅ Job descriptions received")

    if st.button("🔍 Analyze Fit"):
        resume = st.session_state.resume
        jds = st.session_state.job_descriptions

        # Extract resume text
        resume_text = extract_text(resume) if hasattr(resume, "read") else resume
        resume_text = resume_text.strip()

        ranked_results = []

        # MULTI JD COMPARISON
        if isinstance(jds, list) and all(hasattr(jd, "read") for jd in jds):
            for jd_file in jds:
                jd_text = extract_text(jd_file).strip()
                prompt = f"""Compare this resume and job description. Rate the fit from 0 to 10. 
Start with: Score: X/10. Then explain briefly.

Resume:
{resume_text}

Job Description:
{jd_text}"""

                with st.spinner(f"Analyzing {jd_file.name}..."):
                    result = get_gpt_response(prompt)

                match = re.search(r"Score:\s*(\d+)/10", result)
                score = int(match.group(1)) if match else 0
                ranked_results.append((jd_file.name, score, result))
        else:
            # Pasted JD(s)
            jd_blocks = jds.split("---") if isinstance(jds, str) else []
            for idx, jd_text in enumerate(jd_blocks):
                jd_text = jd_text.strip()
                prompt = f"""Compare this resume and job description. Rate the fit from 0 to 10. 
Start with: Score: X/10. Then explain briefly.

Resume:
{resume_text}

Job Description:
{jd_text}"""

                with st.spinner(f"Analyzing JD #{idx+1}..."):
                    result = get_gpt_response(prompt)

                match = re.search(r"Score:\s*(\d+)/10", result)
                score = int(match.group(1)) if match else 0
                ranked_results.append((f"Pasted JD #{idx+1}", score, result))

        # Sort & display
        ranked_results.sort(key=lambda x: x[1], reverse=True)
        st.subheader("📊 Ranked Matches")

        for i, (name, score, explanation) in enumerate(ranked_results, 1):
            st.markdown(f"### {i}. {name} — Score: {score}/10")
            st.write(explanation)

# ---- Summary Page ----
elif page == "Summary":
    st.header("📊 Results Summary")
    st.info("Summary view will include scorecards soon.")

# ---- Detail View ----
elif page == "Detail View":
    st.header("🧠 Job Detail Feedback")
    st.info("Detailed view coming soon.")

# ---- Footer ----
st.markdown("---")
st.caption("🚧 MVP in progress – built with ❤️ by Inna using Streamlit + OpenAI")
