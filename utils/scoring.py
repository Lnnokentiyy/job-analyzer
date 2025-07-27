import openai

def score_resume_to_jd(resume_text, jd_text):
    prompt = f"""
You are a career coach and recruiter. Compare the following resume and job description. 
Rate the fit from 0 to 10. Start your response with: Score: X/10
Then explain why this resume is or isn't a good match.

Resume:
{resume_text}

Job Description:
{jd_text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=800
    )

    content = response["choices"][0]["message"]["content"]

    try:
        score_line, explanation = content.split("\n", 1)
        score = int(score_line.strip().split(":")[1].split("/")[0])
    except Exception:
        score = 0
        explanation = "⚠️ Couldn't parse score."

    return score, explanation
