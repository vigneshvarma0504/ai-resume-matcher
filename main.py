# main.py  (project root)
# PURPOSE: Entry point for the FastAPI application.
# Run with: uvicorn main:app --reload --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="AI Resume Matcher",
    description="Semantic resume-to-JD matching using BERT embeddings, FAISS, and spaCy",
    version="1.0.0"
)

# CORS middleware: allows the Streamlit frontend (port 8501)
# to call this API (port 8000) without browser blocking requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)