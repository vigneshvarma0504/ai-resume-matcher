# 🎯 AI Resume Matcher

> AI-powered resume screening system using NLP, BERT embeddings, FAISS vector search, spaCy, FastAPI, and Streamlit.

## 🚀 What It Does
Upload any PDF/DOCX resume → paste a job description → instantly get:
- **Match score** (semantic similarity + skills coverage)
- **Skills breakdown** (matched, missing, bonus)
- **Improvement tips** powered by NLP
- **Downloadable PDF report**

## 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| NLP & Skills Extraction | spaCy (en_core_web_md) |
| Text Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector Similarity | FAISS (Facebook AI Similarity Search) |
| Backend API | FastAPI + Uvicorn |
| Frontend UI | Streamlit |
| File Parsing | pdfplumber, python-docx |
| PDF Reports | ReportLab |

## ⚙️ Setup & Installation
```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-matcher
cd ai-resume-matcher
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 -m spacy download en_core_web_md
```

## ▶️ Running the App
Open two terminals:

**Terminal 1 — Backend API:**
```bash
source venv/bin/activate
uvicorn main:app --reload --port 8001
```

**Terminal 2 — Frontend:**
```bash
source venv/bin/activate
cd frontend && streamlit run app.py
```

Open **http://localhost:8501** in your browser.

## 📡 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/match` | Match resume to job description |
| POST | `/report` | Generate downloadable PDF report |

Interactive API docs at: **http://localhost:8001/docs**

## 🧠 Scoring Formula
Semantic similarity uses BERT embeddings + FAISS cosine distance.
Skills coverage uses spaCy NER + regex keyword matching.
