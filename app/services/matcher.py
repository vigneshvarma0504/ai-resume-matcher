# app/services/matcher.py
# PURPOSE: Compute semantic similarity between resume and JD using:
# 1. Sentence Transformers — convert text to 384-number vectors (embeddings)
# 2. FAISS — measure cosine similarity between those vectors
#
# WHY NOT JUST KEYWORD MATCHING?
# "3+ years building scalable backend systems" and "senior software engineer"
# share ZERO keywords but are highly semantically related.
# Embeddings capture MEANING, not just words.

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL
from app.services.extractor import extract_all_skills, compare_skills

# Load the BERT model once at startup (~80MB download on first run, cached after)
# "all-MiniLM-L6-v2" is the best balance of speed and accuracy for this task
model = SentenceTransformer(EMBEDDING_MODEL)


def get_embedding(text: str) -> np.ndarray:
    """
    Convert a text string into a 384-dimensional vector.

    WHAT IS AN EMBEDDING?
    Think of it as the text's "fingerprint" — a list of 384 numbers
    that represents its meaning. Similar texts produce similar numbers.
    The model learned this from reading millions of sentences.
    """
    embedding = model.encode([text], convert_to_numpy=True)
    return embedding.astype(np.float32)


def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Measure how similar two embeddings are using FAISS cosine similarity.

    HOW COSINE SIMILARITY WORKS:
    Imagine two arrows pointing in 3D space.
    If they point in the same direction → score = 1.0 (identical meaning)
    If they point at 90 degrees         → score = 0.5 (somewhat related)
    If they point in opposite directions → score = 0.0 (unrelated)

    FAISS TRICK: Normalizing vectors first turns dot product into cosine.
    faiss.normalize_L2() scales each vector to length 1.
    Then IndexFlatIP (Inner Product) = cosine similarity.
    """
    faiss.normalize_L2(vec1)
    faiss.normalize_L2(vec2)

    # Create a FAISS index — think of it as a fast search container
    dimension = vec1.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(vec2)                          # add JD embedding to index

    scores, _ = index.search(vec1, 1)        # search for resume in index
    return float(np.clip(scores[0][0], 0, 1))


def generate_suggestions(missing_skills: list, semantic_score: float) -> list:
    """
    Generate human-readable improvement tips based on score and missing skills.
    These show up in the UI and the downloadable PDF report.
    """
    tips = []

    if missing_skills:
        top5 = ", ".join(missing_skills[:5])
        tips.append(f"🎯 Add these missing skills to your resume: {top5}")

    if semantic_score < 0.40:
        tips.append("📝 Your resume language is very different from the JD — mirror its exact wording and action verbs.")
        tips.append("🔄 Rewrite your summary paragraph to directly address what this specific role requires.")
    elif semantic_score < 0.65:
        tips.append("✍️ Good foundation — align your bullet points more closely with the JD's responsibilities.")
        tips.append("📊 Add quantified achievements (numbers, percentages, scale) to strengthen your impact.")
    else:
        tips.append("✅ Strong semantic alignment — your resume language matches the JD well.")
        tips.append("🚀 Polish with metrics: how many users, what scale, what % improvement?")

    return tips


def match_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    """
    MAIN FUNCTION — runs the full matching pipeline.

    SCORING FORMULA:
    final_score = (semantic_similarity × 0.6) + (skills_coverage × 0.4)

    WHY THIS WEIGHTING?
    60% semantic: captures overall language/context alignment
    40% skills:   captures specific technical keyword coverage
    Semantic is weighted higher because meaning matters more than keyword count.
    A resume can be a great fit without using the exact same words.
    """
    # Step 1: Get vector embeddings for both texts
    resume_vec = get_embedding(resume_text)
    jd_vec     = get_embedding(jd_text)

    # Step 2: Compute semantic similarity (0.0 to 1.0)
    semantic_sim = compute_cosine_similarity(resume_vec.copy(), jd_vec.copy())

    # Step 3: Extract and compare skills
    resume_skills = extract_all_skills(resume_text)
    jd_skills     = extract_all_skills(jd_text)
    skills_result = compare_skills(resume_skills, jd_skills)

    # Step 4: Calculate weighted final score
    skills_coverage = skills_result["skills_match_score"] / 100
    final_score     = round(((semantic_sim * 0.6) + (skills_coverage * 0.4)) * 100, 1)

    # Step 5: Determine match level label
    if final_score >= 75:
        match_level = "🟢 Strong Match"
    elif final_score >= 50:
        match_level = "🟡 Moderate Match"
    else:
        match_level = "🔴 Weak Match"

    # Step 6: Generate improvement suggestions
    suggestions = generate_suggestions(
        skills_result["missing_skills"],
        semantic_sim
    )

    return {
        "final_score":             final_score,
        "match_level":             match_level,
        "semantic_similarity":     round(semantic_sim * 100, 1),
        "skills_match_score":      skills_result["skills_match_score"],
        "matched_skills":          skills_result["matched_skills"],
        "missing_skills":          skills_result["missing_skills"],
        "extra_skills":            skills_result["extra_skills"],
        "resume_skills":           resume_skills,
        "jd_skills":               jd_skills,
        "improvement_suggestions": suggestions,
        "total_resume_skills":     skills_result["total_resume_skills"],
        "total_jd_skills":         skills_result["total_jd_skills"],
    }