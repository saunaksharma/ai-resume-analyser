import requests
import re

def extract_ats_score(text):
    match = re.search(r'ATS Score[:\s]*\**(\d+)\**', text)
    if match:
        return int(match.group(1))
    return None


def analyze_resume(text):
    url = "http://localhost:11434/api/generate"

    prompt = f"""
Analyze this resume.

IMPORTANT:


- Do NOT use markdown like ** or *
- Follow the format EXACTLY

Format:



Strengths:
- ...

Weaknesses:
- ...

Missing Skills:
- ...

Suggestions:
- ...

Resume:
{text}
"""

    response = requests.post(
        url,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()["response"]

    score = extract_ats_score(result)

    return {
        "analysis": result,
        "ats_score": score
    }