import requests
import json
import os

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")


def analyze_resume(resume_text: str, jd_text: str = "") -> dict:
    jd_section = ""
    if jd_text:
        jd_section = f"""
Job Description:
{jd_text}

"""

    prompt = f"""You are an expert resume reviewer and career coach. Analyze the resume below and return a JSON object with your analysis.

{jd_section}Resume:
{resume_text}

Return ONLY a valid JSON object with this exact structure:
{{
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
  "missing_skills": ["skill 1", "skill 2"],
  "summary": "2-3 sentence overall assessment of the resume",
  "section_feedback": {{
    "contact": "feedback on contact info",
    "summary": "feedback on professional summary/objective",
    "experience": "feedback on work experience section",
    "education": "feedback on education section",
    "skills": "feedback on skills section"
  }}
}}

Rules:
- Be specific and actionable, not generic
- Identify 3-5 items per list
- missing_skills should reflect skills relevant to the job description (if provided) or common industry gaps
- section_feedback should note if a section is missing or weak
- Return ONLY the JSON object, nothing else"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )
    response.raise_for_status()

    result_text = response.json().get("response", "").strip()

    # Strip markdown code fences if present
    if result_text.startswith("```"):
        result_text = result_text.split("```", 2)[-1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
        result_text = result_text.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(result_text)
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw text as the summary
        parsed = {
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "missing_skills": [],
            "summary": result_text[:500] if result_text else "Analysis could not be parsed.",
            "section_feedback": {},
        }

    # Ensure all expected keys exist
    for key in ("strengths", "weaknesses", "suggestions", "missing_skills"):
        if key not in parsed or not isinstance(parsed[key], list):
            parsed[key] = []
    if "summary" not in parsed or not isinstance(parsed["summary"], str):
        parsed["summary"] = ""
    if "section_feedback" not in parsed or not isinstance(parsed["section_feedback"], dict):
        parsed["section_feedback"] = {}

    return parsed
