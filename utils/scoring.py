# utils/scoring.py

import openai
import re

def score_resume_to_jd(resume_text, jd_text):
    prompt = f"""
Compare this resume and job description. Rate the fit from 0 to 10.
Explain briefly why. Start your answer with: Score: X/10

Resume:
{resume_text}

Job Description:
{jd_text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that compares resumes and job descriptions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )
    content = response.choices[0].message.content
    score_match = re.search(r"Score:\s*(\d+)/10", content)
    score = int(score_match.group(1)) if score_match else 0
    return score, content
