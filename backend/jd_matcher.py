def match_resume_with_jd(resume_text, jd_text):
    resume_text = resume_text.lower()
    jd_text = jd_text.lower()

    # 🔥 Predefined skill list
    skills = [
        "python", "java", "c++", "sql",
        "machine learning", "deep learning",
        "aws", "docker", "kubernetes",
        "fastapi", "flask", "react", "node",
        "data structures", "algorithms",
        "system design"
    ]

    # Extract skills from JD
    jd_skills = [skill for skill in skills if skill in jd_text]

    # Match skills
    matched = [skill for skill in jd_skills if skill in resume_text]

    missing = [skill for skill in jd_skills if skill not in resume_text]

    if len(jd_skills) == 0:
        return 0, []

    match_score = int((len(matched) / len(jd_skills)) * 100)

    return match_score, missing

