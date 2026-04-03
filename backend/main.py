from fastapi import FastAPI, UploadFile, File, Form
from parser import extract_text
from llm import analyze_resume
from ats import calculate_ats_score
from jd_matcher import match_resume_with_jd
import shutil

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}


@app.post("/analyze/")
async def analyze(
    file: UploadFile = File(...),
    jd: str = Form("")
):
    file_path = f"temp_{file.filename}"

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    text = extract_text(file_path)

    # 🔥 ATS SCORE (your logic)
    ats_score, details = calculate_ats_score(text)

    # 🔥 JD MATCHING
    match_score = None
    missing_skills = []
    jd_analysis = None

    if jd:
        match_score, missing_skills, jd_analysis = match_resume_with_jd(text, jd)

    # 🤖 LLM ANALYSIS
    result = analyze_resume(text)

    return {
        "analysis": result["analysis"],
        "ats_score": ats_score,
        "details": details,
        "match_score": match_score,
        "missing_skills": missing_skills,
        "jd_analysis": jd_analysis
    }