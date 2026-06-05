import spacy
import re
from pathlib import Path

nlp = spacy.load("en_core_web_md")

def load_skills_database() -> set:
    skills_path = Path(__file__).parent.parent / "data" / "skills_db.txt"
    with open(skills_path, "r") as f:
        return {line.strip().lower() for line in f if line.strip()}

SKILLS_DATABASE = load_skills_database()

def extract_skills_keyword(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in SKILLS_DATABASE:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(found)

def extract_skills_spacy(text: str) -> list:
    doc = nlp(text[:100000])
    noun_phrases = set()
    for chunk in doc.noun_chunks:
        phrase = chunk.text.lower().strip()
        if phrase in SKILLS_DATABASE:
            noun_phrases.add(phrase)
    return sorted(list(noun_phrases))

def extract_all_skills(text: str) -> list:
    return sorted(list(set(extract_skills_keyword(text)) | set(extract_skills_spacy(text))))

def get_skills_overlap(resume_skills: list, jd_skills: list) -> dict:
    r, j = set(resume_skills), set(jd_skills)
    return {
        "matched_skills": sorted(list(r & j)),
        "missing_skills": sorted(list(j - r)),
        "extra_skills": sorted(list(r - j)),
        "skills_match_percentage": round(len(r & j) / len(j) * 100, 1) if j else 0
    }
