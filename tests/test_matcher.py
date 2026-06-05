# tests/test_matcher.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.matcher import match_resume_to_jd

resume = """
    python developer with 3 years experience. built rest apis using fastapi
    and deployed on aws with docker. used machine learning with scikit-learn
    and pandas for data analysis. familiar with postgresql and git.
"""

jd = """
    we are looking for a python backend developer with fastapi experience,
    aws deployment, docker, postgresql, and machine learning knowledge.
    must know git and have strong api design skills.
"""

print("Running semantic match... (first run downloads ~80MB model, wait ~30 sec)")
result = match_resume_to_jd(resume, jd)

print(f"\n{'='*40}")
print(f"Final Score        : {result['final_score']}%")
print(f"Match Level        : {result['match_level']}")
print(f"Semantic Similarity: {result['semantic_similarity']}%")
print(f"Skills Match       : {result['skills_match_score']}%")
print(f"Matched Skills     : {result['matched_skills']}")
print(f"Missing Skills     : {result['missing_skills']}")
print(f"Suggestions        : {result['improvement_suggestions']}")
print(f"{'='*40}")

assert result["final_score"] > 0,        "final score should be > 0"
assert result["semantic_similarity"] > 0, "semantic score should be > 0"
assert len(result["matched_skills"]) > 0, "should find matched skills"
print("\n✅ Matcher test passed!")