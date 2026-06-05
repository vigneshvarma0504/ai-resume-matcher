# app/api/routes.py
# PURPOSE: Define all FastAPI endpoints.
# /health  → check API is alive
# /match   → main endpoint: upload resume + paste JD → get match results
# /report  → generate and return a downloadable PDF

import os
import tempfile
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from app.services.parser import parse_resume, parse_job_description
from app.services.matcher import match_resume_to_jd
from app.services.report import generate_report

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Simple ping endpoint.
    Recruiters and engineers use /health to confirm the server is running.
    Best practice in every production API.
    """
    return {"status": "healthy", "message": "AI Resume Matcher API is running"}


@router.post("/match")
async def match(
    resume: UploadFile = File(...),          # file upload from form
    job_description: str = Form(...)         # plain text from form
):
    """
    MAIN ENDPOINT — full pipeline in 4 steps:
    1. Read uploaded file bytes
    2. Parse text from PDF/DOCX/TXT
    3. Parse + clean the job description
    4. Run matching algorithm and return JSON results

    WHY async? File I/O is slow. async lets FastAPI handle
    other requests while waiting for the file to be read.
    """
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    # Read uploaded file into memory as bytes
    file_bytes = await resume.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        resume_text = parse_resume(resume.filename, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if len(resume_text.split()) < 20:
        raise HTTPException(status_code=400, detail="Could not extract enough text. Please upload a text-based PDF.")

    jd_text = parse_job_description(job_description)
    result  = match_resume_to_jd(resume_text, jd_text)
    result["resume_filename"] = resume.filename

    return result


@router.post("/report")
async def download_report(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Run the full match pipeline THEN generate a PDF.
    Returns the PDF file as a downloadable response.

    WHY a separate endpoint?
    Generating a PDF takes extra time. The /match endpoint
    returns JSON fast. /report only runs when user clicks download.
    """
    file_bytes  = await resume.read()
    resume_text = parse_resume(resume.filename, file_bytes)
    jd_text     = parse_job_description(job_description)
    result      = match_resume_to_jd(resume_text, jd_text)
    result["resume_filename"] = resume.filename

    # Write PDF to a temp file, serve it, then clean up
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    generate_report(result, tmp.name)

    return FileResponse(
        tmp.name,
        media_type="application/pdf",
        filename=f"resume_match_{result['final_score']}pct.pdf",
        background=None
    )