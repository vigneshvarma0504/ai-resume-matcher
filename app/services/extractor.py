# app/services/extractor.py
# PURPOSE: Extract skills from resume and JD text using two methods combined.
# Method 1 - Keyword matching: scan text for skills from our CSV database
# Method 2 - spaCy NLP: find noun phrases and match to skills database
# Using BOTH gives better coverage than either method alone.

import re
import pandas as pd
import spacy
from app.config import SKILLS_FILE, SPACY_MODEL

# Load the spaCy model ONCE when this file is imported.
# Loading takes ~1 second — doing it here means every function
# call after that is instant because it reuses the same loaded model.
nlp = spacy.load(SPACY_MODEL)


def load_skills_db() -> set:
    """
    Read skills_master.csv → return a Python set of skill strings.
    WHY a set? Checking 'skill in set' is O(1) — instant.
    Checking 'skill in list' is O(n) — gets slower as list grows.
    """
    df = pd.read_csv(SKILLS_FILE)
    return set(df["skill"].str.lower().str.strip())


# Load the skills DB once at module level so it's shared everywhere
SKILLS_DB = load_skills_db()


def extract_skills_by_keyword(text: str) -> list:
    """
    Method 1: Loop through every skill in the DB.
    Use regex \b (word boundary) to match whole words only.

    Example why \b matters:
    Searching for 'r' WITHOUT \b would match inside 'resume', 'programmer' etc.
    WITH \b it only matches the standalone letter 'r' (the R language).
    re.escape() handles skills with special chars like 'c++'.
    """
    found = []
    text_lower = text.lower()
    for skill in SKILLS_DB:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(found)


def extract_skills_by_spacy(text: str) -> list:
    """
    Method 2: Use spaCy grammar understanding.
    spaCy reads text and identifies 'noun chunks' — natural phrases
    like 'machine learning', 'rest api', 'data analysis'.
    We then check if those phrases exist in our skills database.

    WHY spaCy on top of keyword matching?
    Keywords miss multi-word skills when text is written differently.
    spaCy groups related words by grammar so we catch more combinations.
    """
    doc = nlp(text[:50000])   # cap at 50k chars to avoid memory issues
    found = set()
    for chunk in doc.noun_chunks:
        phrase = chunk.text.lower().strip()
        if phrase in SKILLS_DB:
            found.add(phrase)
    return sorted(list(found))


def extract_all_skills(text: str) -> list:
    """
    Final function: combine both methods using set union (|).
    If EITHER method finds a skill, it is included.
    This maximizes coverage — we miss as few skills as possible.
    """
    keyword_skills = set(extract_skills_by_keyword(text))
    spacy_skills   = set(extract_skills_by_spacy(text))
    return sorted(list(keyword_skills | spacy_skills))


def compare_skills(resume_skills: list, jd_skills: list) -> dict:
    """
    Compare resume skills vs job description skills.

    matched_skills = skills in BOTH lists      → candidate has what job needs
    missing_skills = in JD but NOT in resume   → candidate's skill gaps
    extra_skills   = in resume but NOT in JD   → bonus skills candidate has

    SCORE FORMULA:
    skills_match_score = (matched / total_jd_skills) × 100

    Example: JD needs 10 skills, resume has 7 of them → score = 70.0
    """
    r_set = set(resume_skills)
    j_set = set(jd_skills)

    matched = sorted(list(r_set & j_set))   # & = intersection
    missing = sorted(list(j_set - r_set))   # in JD, not in resume
    extra   = sorted(list(r_set - j_set))   # in resume, not in JD

    score = round(len(matched) / len(j_set) * 100, 1) if j_set else 0.0

    return {
        "matched_skills":      matched,
        "missing_skills":      missing,
        "extra_skills":        extra,
        "skills_match_score":  score,
        "total_resume_skills": len(r_set),
        "total_jd_skills":     len(j_set),
        "total_matched":       len(matched),
    }