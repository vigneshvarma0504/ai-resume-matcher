# app/services/report.py
# PURPOSE: Generate a professional downloadable PDF report using ReportLab.
# The report summarizes the match score, skills analysis, and improvement tips.
# Recruiters and users can download this as proof of the analysis.

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


# ── Color palette ──────────────────────────────────────────────
DARK      = colors.HexColor("#1a1a2e")
TEAL      = colors.HexColor("#01696f")
LIGHT_BG  = colors.HexColor("#f0f7f7")
GREEN     = colors.HexColor("#437a22")
RED       = colors.HexColor("#a12c7b")
BLUE      = colors.HexColor("#006494")
MUTED     = colors.HexColor("#7a7974")
WHITE     = colors.white


def _make_styles():
    """Build all paragraph styles used in the PDF."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", fontSize=22, fontName="Helvetica-Bold",
            textColor=DARK, spaceAfter=6
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontSize=11, fontName="Helvetica",
            textColor=MUTED, spaceAfter=16
        ),
        "section": ParagraphStyle(
            "section", fontSize=13, fontName="Helvetica-Bold",
            textColor=TEAL, spaceBefore=14, spaceAfter=6
        ),
        "body": ParagraphStyle(
            "body", fontSize=10, fontName="Helvetica",
            textColor=DARK, spaceAfter=4, leading=15
        ),
        "chip_green": ParagraphStyle(
            "chip_green", fontSize=9, fontName="Helvetica",
            textColor=GREEN
        ),
        "chip_red": ParagraphStyle(
            "chip_red", fontSize=9, fontName="Helvetica",
            textColor=RED
        ),
        "chip_blue": ParagraphStyle(
            "chip_blue", fontSize=9, fontName="Helvetica",
            textColor=BLUE
        ),
        "tip": ParagraphStyle(
            "tip", fontSize=10, fontName="Helvetica",
            textColor=DARK, leftIndent=12, spaceAfter=5, leading=14
        ),
    }


def _score_color(score: float):
    if score >= 75: return GREEN
    if score >= 50: return colors.HexColor("#da7101")
    return RED


def _skills_table(skills: list, style_name: str, styles: dict) -> Table:
    """Render a list of skills as a compact wrapped table."""
    if not skills:
        return Paragraph("None found", styles["body"])
    # 4 skills per row
    rows, row = [], []
    for i, s in enumerate(skills):
        row.append(Paragraph(f"• {s.title()}", styles[style_name]))
        if (i + 1) % 4 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row + [""] * (4 - len(row)))  # pad last row
    t = Table(rows, colWidths=[4.2 * cm] * 4)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def generate_report(result: dict, output_path: str) -> str:
    """
    Build the PDF and save to output_path.
    Returns the output_path so the caller can open/send it.
    """
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = _make_styles()
    story  = []

    # ── Header ─────────────────────────────────────────────────
    story.append(Paragraph("AI Resume Match Report", styles["title"]))
    story.append(Paragraph(
        f"Resume: {result.get('resume_filename', 'Uploaded Resume')}",
        styles["subtitle"]
    ))
    story.append(HRFlowable(width="100%", color=TEAL, thickness=1.5))
    story.append(Spacer(1, 10))

    # ── Score summary table ─────────────────────────────────────
    score      = result.get("final_score", 0)
    sem_score  = result.get("semantic_similarity", 0)
    skill_score= result.get("skills_match_score", 0)
    level      = result.get("match_level", "—")

    score_data = [
        ["Metric", "Score"],
        ["🎯 Overall Match Score", f"{score}%"],
        ["🧠 Semantic Similarity",  f"{sem_score}%"],
        ["🔧 Skills Coverage",      f"{skill_score}%"],
        ["📊 Match Level",          level.replace("🟢","").replace("🟡","").replace("🔴","").strip()],
    ]
    score_table = Table(score_data, colWidths=[10*cm, 7.7*cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  TEAL),
        ("TEXTCOLOR",   (0,0), (-1,0),  WHITE),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 10),
        ("BACKGROUND",  (0,1), (-1,-1), LIGHT_BG),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#dcd9d5")),
        ("FONTNAME",    (0,1), (0,-1),  "Helvetica-Bold"),
        ("TEXTCOLOR",   (1,1), (1,1),   _score_color(score)),
        ("FONTNAME",    (1,1), (1,1),   "Helvetica-Bold"),
        ("FONTSIZE",    (1,1), (1,1),   13),
        ("TOPPADDING",  (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # ── Matched Skills ─────────────────────────────────────────
    story.append(Paragraph("✅ Matched Skills", styles["section"]))
    story.append(_skills_table(result.get("matched_skills", []), "chip_green", styles))
    story.append(Spacer(1, 10))

    # ── Missing Skills ─────────────────────────────────────────
    story.append(Paragraph("❌ Missing Skills (in JD, not in resume)", styles["section"]))
    story.append(_skills_table(result.get("missing_skills", []), "chip_red", styles))
    story.append(Spacer(1, 10))

    # ── Extra Skills ───────────────────────────────────────────
    story.append(Paragraph("➕ Extra Skills (in resume, not in JD)", styles["section"]))
    story.append(_skills_table(result.get("extra_skills", []), "chip_blue", styles))
    story.append(Spacer(1, 10))

    # ── Improvement Tips ───────────────────────────────────────
    story.append(HRFlowable(width="100%", color=TEAL, thickness=0.5))
    story.append(Paragraph("💡 Improvement Suggestions", styles["section"]))
    for tip in result.get("improvement_suggestions", []):
        story.append(Paragraph(tip, styles["tip"]))

    # ── Footer ─────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", color=MUTED, thickness=0.5))
    story.append(Paragraph(
        "Generated by AI Resume Matcher · Built with Python, spaCy, FAISS & Sentence Transformers",
        ParagraphStyle("footer", fontSize=8, textColor=MUTED, alignment=1)
    ))

    doc.build(story)
    return output_path