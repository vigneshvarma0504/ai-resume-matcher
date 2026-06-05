# tests/test_parser.py
# Quick sanity check — run this to confirm the parser works.

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.parser import parse_resume, parse_job_description

# Test 1: TXT resume parsing
resume_bytes = b"John Doe | Python Developer | Skills: Python, FastAPI, Docker, SQL"
result = parse_resume("resume.txt", resume_bytes)
print("Resume parsed:", result)
assert "python" in result
assert "fastapi" in result
print("✅ Test 1 passed")

# Test 2: Job description parsing
jd = "We need a Python developer with FastAPI, Docker, and PostgreSQL experience."
result_jd = parse_job_description(jd)
print("JD parsed:", result_jd)
assert "python" in result_jd
assert "fastapi" in result_jd
print("✅ Test 2 passed")

print("\n🎉 All parser tests passed!")