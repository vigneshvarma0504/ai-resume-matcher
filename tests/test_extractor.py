# tests/test_extractor.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.extractor import extract_all_skills, compare_skills

resume_text = """
    senior python developer with 4 years experience in fastapi, docker,
    postgresql, aws, and machine learning using scikit-learn and pandas.
    strong knowledge of git, linux, and rest api design.
"""

jd_text = """
    looking for a python developer skilled in fastapi, docker, aws,
    kubernetes, machine learning, sql, and postgresql.
    experience with ci/cd and git required.
"""

# Test 1: Skills extraction works
resume_skills = extract_all_skills(resume_text)
jd_skills     = extract_all_skills(jd_text)
print("Resume skills:", resume_skills)
print("JD skills    :", jd_skills)
assert "python"           in resume_skills, "python not found in resume"
assert "fastapi"          in resume_skills, "fastapi not found in resume"
assert "machine learning" in resume_skills, "machine learning not found"
print("✅ Test 1 passed — skills extracted correctly")

# Test 2: Comparison logic works
result = compare_skills(resume_skills, jd_skills)
print("\nMatched :", result["matched_skills"])
print("Missing :", result["missing_skills"])
print("Score   :", result["skills_match_score"], "%")
assert result["skills_match_score"] > 0,        "score should be > 0"
assert len(result["matched_skills"]) > 0,        "should have matched skills"
assert len(result["missing_skills"]) >= 0,       "missing_skills should exist"
print("✅ Test 2 passed — comparison logic correct")

print("\n🎉 All extractor tests passed!")