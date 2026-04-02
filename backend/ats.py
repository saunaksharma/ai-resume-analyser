def calculate_ats_score(text):
    text = text.lower()

    score = 0
    details = []

    # Keywords
    keywords = [
        "python", "java", "sql", "c++",
        "machine learning", "deep learning",
        "docker", "aws", "fastapi", "flask",
        "react", "node", "kubernetes"
    ]

    found = sum(1 for k in keywords if k in text)
    keyword_score = min(found * 3, 30)
    score += keyword_score
    details.append(f"Keyword strength (+{keyword_score})")

    # Experience quality
    if "intern" in text or "experience" in text:
        if "month" in text or "year" in text:
            score += 20
            details.append("Detailed experience (+20)")
        else:
            score += 10
            details.append("Basic experience (+10)")

    # Project quality
    if "project" in text:
        if "built" in text or "developed" in text:
            score += 20
            details.append("Strong projects (+20)")
        else:
            score += 10
            details.append("Basic projects (+10)")

    # Advanced skills bonus
    advanced_skills = ["aws", "docker", "kubernetes", "microservices"]

    bonus = sum(1 for s in advanced_skills if s in text)
    bonus_score = min(bonus * 5, 20)

    score += bonus_score

    if bonus_score > 0:
        details.append(f"Advanced skills bonus (+{bonus_score})")

    # Education
    if "b.tech" in text or "bachelor" in text:
        score += 10
        details.append("Education (+10)")

    score = min(score, 100)

    return score, details