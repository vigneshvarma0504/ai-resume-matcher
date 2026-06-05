import streamlit as st
import requests
import os

# ── MUST be first Streamlit call ────────────────────────────────
st.set_page_config(
    page_title="AI Resume Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f7f6f2; }
    .skill-chip {
        display: inline-block; padding: 4px 12px;
        border-radius: 20px; font-size: 0.82rem;
        margin: 3px; font-weight: 500;
    }
    .chip-green { background: #d4dfcc; color: #1e3f0a; }
    .chip-red   { background: #e0ced7; color: #561740; }
    .chip-blue  { background: #c6d8e4; color: #0b3751; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🎯 AI Resume Matcher")
    st.markdown("---")
    st.markdown("### How It Works")
    st.markdown("""
    1. 📄 Upload your resume (PDF/DOCX)
    2. 📋 Paste the job description
    3. 🚀 Click **Analyze**
    4. 📊 View your match score
    5. 💡 Follow improvement tips
    6. ⬇️ Download report
    """)
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    api_url = st.text_input("API URL", value="http://localhost:8001")
    st.markdown("---")
    st.caption("Built with Python · spaCy · FAISS · Sentence Transformers")

# ── Header ───────────────────────────────────────────────────────
st.markdown("## 🎯 AI Resume Matcher")
st.markdown("*Compare your resume against any job description using semantic AI*")
st.divider()

# ── Inputs ───────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("### 📄 Your Resume")
    resume_file = st.file_uploader(
        "Upload PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        help="Text-based PDFs work best."
    )
    if resume_file:
        size_kb = len(resume_file.getvalue()) // 1024
        st.success(f"✅ **{resume_file.name}** ({size_kb} KB) ready")

with col_right:
    st.markdown("### 📋 Job Description")
    jd_text = st.text_area(
        "Paste the full job description here",
        height=220,
        placeholder="Paste the complete job description..."
    )
    if jd_text:
        st.caption(f"📝 {len(jd_text.split())} words entered")

st.divider()

# ── Analyze Button ───────────────────────────────────────────────
_, col_btn, _ = st.columns([1, 2, 1])
with col_btn:
    analyze_clicked = st.button("🚀 Analyze Match", use_container_width=True, type="primary")

# ── Run Analysis ─────────────────────────────────────────────────
if analyze_clicked:
    if not resume_file:
        st.error("⚠️ Please upload your resume first.")
    elif not jd_text or len(jd_text.strip()) < 30:
        st.error("⚠️ Please paste a job description (at least 30 characters).")
    else:
        with st.spinner("🔍 Analyzing... (first run may take 20-30 seconds while model loads)"):
            try:
                response = requests.post(
                    f"{api_url}/match",
                    files={"resume": (
                        resume_file.name,
                        resume_file.getvalue(),
                        "application/octet-stream"
                    )},
                    data={"job_description": jd_text},
                    timeout=120
                )
                if response.status_code == 200:
                    st.session_state["results"] = response.json()
                    st.success("✅ Analysis complete!")
                else:
                    detail = response.json().get("detail", "Unknown error")
                    st.error(f"❌ API Error: {detail}")

            except requests.exceptions.ConnectionError:
                st.error("❌ FastAPI server not running! Open a new terminal and run:\n\n`cd backend && uvicorn main:app --reload --port 8001`")
            except requests.exceptions.Timeout:
                st.error("⏱️ Timed out. The model is loading — wait 30s and try again.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

# ── Results ──────────────────────────────────────────────────────
if "results" in st.session_state:
    r = st.session_state["results"]
    st.divider()
    st.markdown("## 📊 Match Results")

    # 4 score cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 Overall Match",      f"{r.get('final_score', 0)}%")
    m2.metric("🧠 Semantic Similarity", f"{r.get('semantic_similarity', 0)}%")
    m3.metric("🔧 Skills Coverage",    f"{r.get('skills_match_percentage', 0)}%")
    m4.metric("📌 Match Level",         r.get('match_level', 'N/A'))

    st.divider()

    # Skills breakdown
    st.markdown("### 🔬 Skills Breakdown")
    s1, s2, s3 = st.columns(3)

    with s1:
        matched = r.get("matched_skills", [])
        st.markdown(f"**✅ Matched** `{len(matched)}`")
        chips = " ".join([f'<span class="skill-chip chip-green">{s.title()}</span>' for s in matched])
        st.markdown(chips or "*None*", unsafe_allow_html=True)

    with s2:
        missing = r.get("missing_skills", [])
        st.markdown(f"**❌ Missing** `{len(missing)}`")
        chips = " ".join([f'<span class="skill-chip chip-red">{s.title()}</span>' for s in missing])
        st.markdown(chips or "🎉 None missing!", unsafe_allow_html=True)

    with s3:
        extra = r.get("extra_skills", [])
        st.markdown(f"**➕ Bonus** `{len(extra)}`")
        chips = " ".join([f'<span class="skill-chip chip-blue">{s.title()}</span>' for s in extra[:15]])
        st.markdown(chips or "*None*", unsafe_allow_html=True)

    st.divider()

    # Improvement tips
    st.markdown("### 💡 Improvement Tips")
    for tip in r.get("improvement_suggestions", []):
        st.info(tip)

    st.divider()

    # Download report as text
    st.markdown("### ⬇️ Download Report")
    report_text = f"""AI RESUME MATCH REPORT
{"="*50}
Resume:             {r.get('resume_filename', 'Resume')}
Overall Score:      {r.get('final_score', 0)}%
Match Level:        {r.get('match_level', '')}
Semantic Score:     {r.get('semantic_similarity', 0)}%
Skills Coverage:    {r.get('skills_match_percentage', 0)}%

MATCHED SKILLS:
{', '.join(r.get('matched_skills', [])) or 'None'}

MISSING SKILLS:
{', '.join(r.get('missing_skills', [])) or 'None'}

BONUS SKILLS:
{', '.join(r.get('extra_skills', [])) or 'None'}

IMPROVEMENT TIPS:
{chr(10).join(['- ' + t for t in r.get('improvement_suggestions', [])])}
"""
    st.download_button(
        label="⬇️ Download Text Report",
        data=report_text,
        file_name=f"resume_match_{r.get('final_score', 0)}pct.txt",
        mime="text/plain",
        use_container_width=True
    )