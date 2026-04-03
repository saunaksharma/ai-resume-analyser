import requests

def match_resume_with_jd(resume_text, jd_text):
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()

    # Predefined skill list
    skills = [
        "python", "java", "c++", "sql",
        "machine learning", "deep learning",
        "aws", "docker", "kubernetes",
        "fastapi", "flask", "react", "node",
        "data structures", "algorithms",
        "system design"
    ]

    # Extract skills from JD
    jd_skills = [skill for skill in skills if skill in jd_lower]

    # Match skills
    matched = [skill for skill in jd_skills if skill in resume_lower]
    missing = [skill for skill in jd_skills if skill not in resume_lower]

    if len(jd_skills) == 0:
        match_score = 0
    else:
        match_score = int((len(matched) / len(jd_skills)) * 100)

    # LLM analysis using llama3
    llm_analysis = analyze_jd_match(resume_text, jd_text)

    return match_score, missing, llm_analysis


def analyze_jd_match(resume_text, jd_text):
    url = "http://localhost:11434/api/generate"

    prompt = f"""
You are a job application expert. Compare the resume with the job description below.

IMPORTANT:
- Do NOT use markdown like ** or *
- Follow the format EXACTLY

Format:

Match Summary:
- ...

Key Strengths for This Role:
- ...

Gaps to Address:
- ...

Recommendation:
- ...

Job Description:
{jd_text}

Resume:
{resume_text}
"""

    response = requests.post(
        url,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]
