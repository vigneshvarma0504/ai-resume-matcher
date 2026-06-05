import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from extractor import extract_all_skills, get_skills_overlap

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> np.ndarray:
    return MODEL.encode([text], convert_to_numpy=True).astype(np.float32)

def compute_cosine_similarity(vec1, vec2) -> float:
    faiss.normalize_L2(vec1)
    faiss.normalize_L2(vec2)
    index = faiss.IndexFlatIP(vec1.shape[1])
    index.add(vec2)
    scores, _ = index.search(vec1, 1)
    return float(np.clip(scores[0][0], 0, 1))

def generate_suggestions(missing_skills: list, semantic_score: float) -> list:
    tips = []
    if missing_skills:
        tips.append(f"🎯 Add these key skills: {', '.join(missing_skills[:5])}")
    if semantic_score < 0.4:
        tips.append("📝 Mirror the JD's exact terminology and action verbs.")
        tips.append("🔄 Rewrite your summary to directly address what this role needs.")
    elif semantic_score < 0.65:
        tips.append("✍️ Align experience bullets more closely with JD responsibilities.")
    else:
        tips.append("✅ Great alignment! Quantify your achievements with numbers.")
    return tips

def match_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    r_vec = get_embedding(resume_text)
    j_vec = get_embedding(jd_text)
    semantic_sim = compute_cosine_similarity(r_vec.copy(), j_vec.copy())
    r_skills = extract_all_skills(resume_text)
    j_skills = extract_all_skills(jd_text)
    skills = get_skills_overlap(r_skills, j_skills)
    skills_score = skills["skills_match_percentage"] / 100
    final = round(((semantic_sim * 0.6) + (skills_score * 0.4)) * 100, 1)
    level = ("🟢 Strong Match" if final >= 75 else
             "🟡 Moderate Match" if final >= 50 else "🔴 Weak Match")
    return {
        "final_score": final,
        "match_level": level,
        "semantic_similarity": round(semantic_sim * 100, 1),
        "skills_match_percentage": skills["skills_match_percentage"],
        "resume_skills": r_skills,
        "jd_skills": j_skills,
        "matched_skills": skills["matched_skills"],
        "missing_skills": skills["missing_skills"],
        "extra_skills": skills["extra_skills"],
        "improvement_suggestions": generate_suggestions(skills["missing_skills"], semantic_sim)
    }
