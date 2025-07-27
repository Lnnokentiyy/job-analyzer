import openai

def score_resume_to_jd(resume_text, jd_text):
    client = openai.OpenAI()
    prompt = (
        f"Given the following resume and job description, score how well the resume matches the job description "
        f"on a scale of 1 to 10. Then explain your reasoning with 2-7 bullet points.\n\n"
        f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}\n\n"
        f"Respond in this format:\nScore: X/10\nReason: <your explanation>"
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who evaluates resume-job fit."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.5
    )

    result_text = response.choices[0].message.content.strip()
    
    if "Score:" in result_text:
        try:
            score_line, reason_line = result_text.split("\n", 1)
            score = int(score_line.replace("Score:", "").replace("/10", "").strip())
            return score, reason_line.strip()
        except:
            return 0, "Failed to parse score from model output."
    return 0, "No score returned."
