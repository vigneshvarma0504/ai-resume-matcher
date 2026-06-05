# app/services/parser.py
# PURPOSE: Extract raw text from uploaded resume files.
# Supports PDF, DOCX, and TXT.
# This is Step 1 of the pipeline — before NLP, before scoring.

from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from app.utils.text_cleaner import clean_text


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    PDFs are structured as pages.
    We loop through every page, pull text, join them, and clean.
    PyPDF2 handles the binary PDF format for us.
    """
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            pages.append(extracted)
    return clean_text(" ".join(pages))


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    DOCX files are structured as paragraphs.
    python-docx reads each paragraph object — we join and clean.
    """
    doc = Document(BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return clean_text(" ".join(paragraphs))


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Plain .txt — just decode bytes to a string."""
    return clean_text(file_bytes.decode("utf-8", errors="ignore"))


def parse_resume(filename: str, file_bytes: bytes) -> str:
    """
    Main entry point.
    Detects file type by extension and calls the right extractor.
    Raises a clear error message if file format is unsupported.
    """
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif name.endswith(".txt"):
        return extract_text_from_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported format. Please upload PDF, DOCX, or TXT.")


def parse_job_description(text: str) -> str:
    """
    Job descriptions are pasted as plain text in the UI.
    We just clean and return.
    """
    return clean_text(text or "")