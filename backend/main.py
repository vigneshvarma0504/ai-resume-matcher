from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os, shutil, sys

sys.path.append(os.path.dirname(__file__))
from parser import parse_file
from matcher import match_resume_to_jd

app = FastAPI(title="AI Resume Matcher API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"message": "AI Resume Matcher API is running!", "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/match")
async def match_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not job_description.strip():
        raise HTTPException(400, "Job description cannot be empty.")
    
    ext = os.path.splitext(resume.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(resume.file, tmp)
        tmp_path = tmp.name
    
    try:
        resume_text = parse_file(tmp_path)
        if len(resume_text) < 50:
            raise HTTPException(400, "Could not extract enough text from resume.")
        results = match_resume_to_jd(resume_text, job_description)
        results["resume_filename"] = resume.filename
        return results
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
