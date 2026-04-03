import os
import shutil

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from parser import extract_text
from llm import analyze_resume
from ats import calculate_ats_score
from jd_matcher import match_resume_with_jd

app = FastAPI()

ALLOWED_EXTENSIONS = {"pdf", "docx"}


@app.get("/")
def home():
    return {"message": "Resume Analyser API is running"}


@app.post("/analyze/")
async def analyze(
    file: UploadFile = File(...),
    jd: str = Form(""),
):
    filename = file.filename or "upload"
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Please upload a PDF or DOCX."
        )

    file_path = f"temp_{filename}"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = extract_text(file_path)

        if not text.strip():
            raise HTTPException(status_code=422, detail="Could not extract text from the file.")

        # ATS scoring (returns score, details list, section_scores dict)
        ats_score, details, section_scores = calculate_ats_score(text)

        # JD matching
        match_score = None
        missing_skills: list[str] = []
        if jd.strip():
            match_score, missing_skills = match_resume_with_jd(text, jd)

        # LLM analysis (Ollama)
        try:
            ai_analysis = analyze_resume(text, jd)
        except Exception as llm_err:
            ai_analysis = {
                "summary": f"AI analysis unavailable: {llm_err}",
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "missing_skills": [],
                "section_feedback": {},
            }

        return {
            "ats_score": ats_score,
            "details": details,
            "section_scores": section_scores,
            "match_score": match_score,
            "missing_skills": missing_skills,
            "analysis": ai_analysis,
        }

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
